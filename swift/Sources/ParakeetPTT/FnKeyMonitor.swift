import CoreGraphics
import Foundation

final class FnKeyMonitor: @unchecked Sendable {
    private let holdThreshold: TimeInterval = 0.3
    private var eventTap: CFMachPort?
    private var runLoopSource: CFRunLoopSource?
    private var fnPressTime: Date?
    private var holdTimerActive = false
    private var isHolding = false

    var onHoldStart: (() -> Void)?
    var onRelease: (() -> Void)?

    func start() -> Bool {
        let eventMask: CGEventMask = 1 << CGEventType.flagsChanged.rawValue

        guard let tap = CGEvent.tapCreate(
            tap: .cgSessionEventTap,
            place: .headInsertEventTap,
            options: .defaultTap,
            eventsOfInterest: eventMask,
            callback: { proxy, type, event, refcon in
                guard let refcon else { return Unmanaged.passUnretained(event) }
                let monitor = Unmanaged<FnKeyMonitor>.fromOpaque(refcon).takeUnretainedValue()
                return monitor.handleEvent(type: type, event: event)
            },
            userInfo: Unmanaged.passUnretained(self).toOpaque()
        ) else {
            return false
        }

        eventTap = tap
        runLoopSource = CFMachPortCreateRunLoopSource(kCFAllocatorDefault, tap, 0)
        CFRunLoopAddSource(CFRunLoopGetMain(), runLoopSource, .commonModes)
        CGEvent.tapEnable(tap: tap, enable: true)
        return true
    }

    func stop() {
        if let tap = eventTap {
            CGEvent.tapEnable(tap: tap, enable: false)
        }
        if let source = runLoopSource {
            CFRunLoopRemoveSource(CFRunLoopGetMain(), source, .commonModes)
        }
        eventTap = nil
        runLoopSource = nil
    }

    private func handleEvent(type: CGEventType, event: CGEvent) -> Unmanaged<CGEvent>? {
        // Re-enable if system disabled our tap
        if type == .tapDisabledByTimeout || type == .tapDisabledByUserInput {
            if let tap = eventTap {
                CGEvent.tapEnable(tap: tap, enable: true)
            }
            return Unmanaged.passUnretained(event)
        }

        guard type == .flagsChanged else {
            return Unmanaged.passUnretained(event)
        }

        let keycode = event.getIntegerValueField(.keyboardEventKeycode)
        guard keycode == 63 else { return Unmanaged.passUnretained(event) } // 63 = fn key

        let fnDown = event.flags.contains(.maskSecondaryFn)

        if fnDown && fnPressTime == nil {
            fnPressTime = Date()
            holdTimerActive = true
            DispatchQueue.main.asyncAfter(deadline: .now() + holdThreshold) { [weak self] in
                self?.checkThreshold()
            }
        } else if !fnDown && fnPressTime != nil {
            fnPressTime = nil
            holdTimerActive = false
            if isHolding {
                isHolding = false
                DispatchQueue.main.async { [weak self] in
                    self?.onRelease?()
                }
            }
        }

        return Unmanaged.passUnretained(event)
    }

    private func checkThreshold() {
        guard holdTimerActive, fnPressTime != nil else { return }
        isHolding = true
        DispatchQueue.main.async { [weak self] in
            self?.onHoldStart?()
        }
    }

    deinit { stop() }
}
