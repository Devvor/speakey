import AppKit
import ApplicationServices
import Foundation

/// Global fn-key push-to-talk with fn+Space hands-free, Esc cancel, and post-session cooldown.
final class FnKeyMonitor: @unchecked Sendable {
    private let holdThreshold: TimeInterval = 0.3
    private let cooldownDuration: TimeInterval = 0.5

    private enum Mode {
        case idle
        case pressPending
        case holding
        case handsFree
    }

    private var mode: Mode = .idle
    private var monitors: [Any] = []
    private var fnWasDown = false
    private var pressStartedAt: Date?
    private var holdTimerWorkItem: DispatchWorkItem?
    private var cooldownUntil: Date?
    /// Ignore the next fn-up (Esc cancel, or releasing fn after fn+Space chord).
    private var ignoreNextFnUp = false

    var onHoldStart: (() -> Void)?
    var onRelease: (() -> Void)?
    var onHandsFreeStart: (() -> Void)?
    var onHandsFreeStop: (() -> Void)?
    var onCancel: (() -> Void)?

    func start() -> Bool {
        guard AXIsProcessTrusted() else {
            KuaishuoLog.write("Event monitor failed: AXIsProcessTrusted=false")
            return false
        }

        // Global monitors cover other apps; local monitors cover when this app is focused
        // (global monitors do not receive events while the app is key).
        if let flagsMonitor = NSEvent.addGlobalMonitorForEvents(
            matching: .flagsChanged,
            handler: { [weak self] event in
                self?.handleFlagsChanged(event)
            }
        ) {
            monitors.append(flagsMonitor)
        }
        if let keyMonitor = NSEvent.addGlobalMonitorForEvents(
            matching: .keyDown,
            handler: { [weak self] event in
                self?.handleKeyDown(event)
            }
        ) {
            monitors.append(keyMonitor)
        }

        if let flagsMonitor = NSEvent.addLocalMonitorForEvents(
            matching: .flagsChanged,
            handler: { [weak self] event in
                self?.handleFlagsChanged(event)
                return event
            }
        ) {
            monitors.append(flagsMonitor)
        }
        if let keyMonitor = NSEvent.addLocalMonitorForEvents(
            matching: .keyDown,
            handler: { [weak self] event in
                let consume = self?.handleKeyDown(event) ?? false
                return consume ? nil : event
            }
        ) {
            monitors.append(keyMonitor)
        }

        let ok = !monitors.isEmpty
        if ok {
            KuaishuoLog.write("Fn key monitor started (NSEvent global + local monitors)")
        } else {
            KuaishuoLog.write("Event monitor failed: add*MonitorForEvents returned nil")
        }
        return ok
    }

    func stop() {
        for monitor in monitors {
            NSEvent.removeMonitor(monitor)
        }
        monitors.removeAll()
        cancelHoldTimer()
        mode = .idle
        fnWasDown = false
        pressStartedAt = nil
        ignoreNextFnUp = false
        cooldownUntil = nil
    }

    /// Force idle after a failed session start (e.g. mic error) without firing callbacks.
    func resetToIdle() {
        DispatchQueue.main.async { [weak self] in
            guard let self else { return }
            self.cancelHoldTimer()
            self.mode = .idle
            self.pressStartedAt = nil
            if self.fnWasDown {
                self.ignoreNextFnUp = true
            }
            self.beginCooldown()
        }
    }

    // MARK: - Events

    private func handleFlagsChanged(_ event: NSEvent) {
        // Globe/Fn key — keycode 63 on most Macs; 179 on some external keyboards.
        guard event.keyCode == 63 || event.keyCode == 179 else { return }

        let fnDown = event.modifierFlags.contains(.function)
        KuaishuoLog.write("fn flagsChanged keyCode=\(event.keyCode) down=\(fnDown) mode=\(mode)")

        if fnDown && !fnWasDown {
            fnWasDown = true
            DispatchQueue.main.async { [weak self] in
                self?.fnDownOnMain()
            }
        } else if !fnDown && fnWasDown {
            fnWasDown = false
            DispatchQueue.main.async { [weak self] in
                self?.fnUpOnMain()
            }
        }
    }

    /// Returns `true` when the local monitor should swallow the event (Esc / fn+Space).
    @discardableResult
    private func handleKeyDown(_ event: NSEvent) -> Bool {
        // 53 = Escape, 49 = Space
        if event.keyCode == 53 {
            let shouldConsume: Bool
            switch mode {
            case .holding, .handsFree, .pressPending:
                shouldConsume = true
            case .idle:
                shouldConsume = false
            }
            DispatchQueue.main.async { [weak self] in
                self?.handleEscape()
            }
            return shouldConsume
        }

        if event.keyCode == 49 {
            let fnHeld = event.modifierFlags.contains(.function) || fnWasDown
            guard fnHeld else { return false }
            DispatchQueue.main.async { [weak self] in
                self?.handleFnSpace()
            }
            return true
        }

        return false
    }

    // MARK: - State machine (main queue)

    private func fnDownOnMain() {
        if isCoolingDown {
            KuaishuoLog.write("fn down ignored — cooldown")
            return
        }

        switch mode {
        case .idle:
            mode = .pressPending
            pressStartedAt = Date()
            scheduleHoldTimer()

        case .handsFree:
            // Any press while hands-free arms a stop on release (tap or hold).
            pressStartedAt = Date()

        case .pressPending, .holding:
            break
        }
    }

    private func fnUpOnMain() {
        if ignoreNextFnUp {
            ignoreNextFnUp = false
            KuaishuoLog.write("fn up ignored — chord/cancel release")
            return
        }

        cancelHoldTimer()

        switch mode {
        case .pressPending:
            // Short tap with no Space — ignore (no longer used for hands-free).
            mode = .idle
            pressStartedAt = nil
            KuaishuoLog.write("fn short tap ignored")

        case .holding:
            mode = .idle
            beginCooldown()
            KuaishuoLog.write("fn hold released — finalize")
            onRelease?()

        case .handsFree:
            // Tap/release ends hands-free and finalizes.
            mode = .idle
            pressStartedAt = nil
            beginCooldown()
            KuaishuoLog.write("fn tap in hands-free — finalize")
            onHandsFreeStop?()

        case .idle:
            break
        }
    }

    private func handleFnSpace() {
        if isCoolingDown {
            KuaishuoLog.write("fn+Space ignored — cooldown")
            return
        }

        switch mode {
        case .idle, .pressPending:
            cancelHoldTimer()
            beginHandsFree()

        case .holding:
            // Already recording via hold — switch to hands-free so fn can be released.
            mode = .handsFree
            pressStartedAt = nil
            if fnWasDown {
                ignoreNextFnUp = true
            }
            KuaishuoLog.write("fn+Space — convert hold to hands-free")
            onHandsFreeStart?()

        case .handsFree:
            break
        }
    }

    private func scheduleHoldTimer() {
        cancelHoldTimer()
        let work = DispatchWorkItem { [weak self] in
            self?.holdThresholdReached()
        }
        holdTimerWorkItem = work
        DispatchQueue.main.asyncAfter(deadline: .now() + holdThreshold, execute: work)
    }

    private func cancelHoldTimer() {
        holdTimerWorkItem?.cancel()
        holdTimerWorkItem = nil
    }

    private func holdThresholdReached() {
        holdTimerWorkItem = nil
        guard mode == .pressPending, fnWasDown else { return }

        mode = .holding
        KuaishuoLog.write("fn hold threshold reached — starting recording")
        onHoldStart?()
    }

    private func beginHandsFree() {
        mode = .handsFree
        pressStartedAt = nil
        // Releasing the fn+Space chord must not immediately stop the session.
        if fnWasDown {
            ignoreNextFnUp = true
        }
        KuaishuoLog.write("fn+Space — hands-free start")
        onHandsFreeStart?()
    }

    private func handleEscape() {
        switch mode {
        case .holding:
            KuaishuoLog.write("Esc — cancel hold recording")
            cancelHoldTimer()
            mode = .idle
            if fnWasDown {
                ignoreNextFnUp = true
            }
            beginCooldown()
            onCancel?()

        case .handsFree:
            KuaishuoLog.write("Esc — cancel hands-free recording")
            mode = .idle
            pressStartedAt = nil
            if fnWasDown {
                ignoreNextFnUp = true
            }
            beginCooldown()
            onCancel?()

        case .pressPending:
            KuaishuoLog.write("Esc — abort pending press")
            cancelHoldTimer()
            mode = .idle
            pressStartedAt = nil
            if fnWasDown {
                ignoreNextFnUp = true
            }

        case .idle:
            break
        }
    }

    private func beginCooldown() {
        cooldownUntil = Date().addingTimeInterval(cooldownDuration)
    }

    private var isCoolingDown: Bool {
        guard let cooldownUntil else { return false }
        return Date() < cooldownUntil
    }

    deinit { stop() }
}

enum KuaishuoLog {
    private static let url = FileManager.default.homeDirectoryForCurrentUser
        .appendingPathComponent("Library/Logs/Kuaishuo.log")

    static func write(_ message: String) {
        let line = "[\(ISO8601DateFormatter().string(from: Date()))] \(message)\n"
        guard let data = line.data(using: .utf8) else { return }

        if FileManager.default.fileExists(atPath: url.path) {
            if let handle = try? FileHandle(forWritingTo: url) {
                handle.seekToEndOfFile()
                handle.write(data)
                try? handle.close()
            }
        } else {
            try? data.write(to: url)
        }

        fputs(line, stderr)
    }
}
