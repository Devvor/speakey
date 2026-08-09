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
            PTTLog.write("Event monitor failed: AXIsProcessTrusted=false")
            return false
        }

        let flagsMonitor = NSEvent.addGlobalMonitorForEvents(matching: .flagsChanged) { [weak self] event in
            self?.handleFlagsChanged(event)
        }
        let keyMonitor = NSEvent.addGlobalMonitorForEvents(matching: .keyDown) { [weak self] event in
            self?.handleKeyDown(event)
        }

        if let flagsMonitor {
            monitors.append(flagsMonitor)
        }
        if let keyMonitor {
            monitors.append(keyMonitor)
        }

        let ok = !monitors.isEmpty
        if ok {
            PTTLog.write("Fn key monitor started (NSEvent global monitor)")
        } else {
            PTTLog.write("Event monitor failed: addGlobalMonitorForEvents returned nil")
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
        PTTLog.write("fn flagsChanged keyCode=\(event.keyCode) down=\(fnDown) mode=\(mode)")

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

    private func handleKeyDown(_ event: NSEvent) {
        // 53 = Escape, 49 = Space
        if event.keyCode == 53 {
            DispatchQueue.main.async { [weak self] in
                self?.handleEscape()
            }
            return
        }

        if event.keyCode == 49 {
            let fnHeld = event.modifierFlags.contains(.function) || fnWasDown
            guard fnHeld else { return }
            DispatchQueue.main.async { [weak self] in
                self?.handleFnSpace()
            }
        }
    }

    // MARK: - State machine (main queue)

    private func fnDownOnMain() {
        if isCoolingDown {
            PTTLog.write("fn down ignored — cooldown")
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
            PTTLog.write("fn up ignored — chord/cancel release")
            return
        }

        cancelHoldTimer()

        switch mode {
        case .pressPending:
            // Short tap with no Space — ignore (no longer used for hands-free).
            mode = .idle
            pressStartedAt = nil
            PTTLog.write("fn short tap ignored")

        case .holding:
            mode = .idle
            beginCooldown()
            PTTLog.write("fn hold released — finalize")
            onRelease?()

        case .handsFree:
            // Tap/release ends hands-free and finalizes.
            mode = .idle
            pressStartedAt = nil
            beginCooldown()
            PTTLog.write("fn tap in hands-free — finalize")
            onHandsFreeStop?()

        case .idle:
            break
        }
    }

    private func handleFnSpace() {
        if isCoolingDown {
            PTTLog.write("fn+Space ignored — cooldown")
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
            PTTLog.write("fn+Space — convert hold to hands-free")
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
        PTTLog.write("fn hold threshold reached — starting recording")
        onHoldStart?()
    }

    private func beginHandsFree() {
        mode = .handsFree
        pressStartedAt = nil
        // Releasing the fn+Space chord must not immediately stop the session.
        if fnWasDown {
            ignoreNextFnUp = true
        }
        PTTLog.write("fn+Space — hands-free start")
        onHandsFreeStart?()
    }

    private func handleEscape() {
        switch mode {
        case .holding:
            PTTLog.write("Esc — cancel hold recording")
            cancelHoldTimer()
            mode = .idle
            if fnWasDown {
                ignoreNextFnUp = true
            }
            beginCooldown()
            onCancel?()

        case .handsFree:
            PTTLog.write("Esc — cancel hands-free recording")
            mode = .idle
            pressStartedAt = nil
            if fnWasDown {
                ignoreNextFnUp = true
            }
            beginCooldown()
            onCancel?()

        case .pressPending:
            PTTLog.write("Esc — abort pending press")
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

enum PTTLog {
    private static let url = FileManager.default.homeDirectoryForCurrentUser
        .appendingPathComponent("Library/Logs/ParakeetPTT.log")

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
