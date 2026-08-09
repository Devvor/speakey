import AppKit
import SwiftUI

class OverlayPanel: NSPanel {
    init() {
        super.init(
            contentRect: NSRect(x: 0, y: 0, width: 240, height: 48),
            styleMask: [.nonactivatingPanel, .fullSizeContentView],
            backing: .buffered,
            defer: false
        )

        level = .floating
        isFloatingPanel = true
        collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary, .stationary]

        titleVisibility = .hidden
        titlebarAppearsTransparent = true
        isMovableByWindowBackground = false
        backgroundColor = .clear
        isOpaque = false
        hasShadow = true
        hidesOnDeactivate = false
        animationBehavior = .utilityWindow

        standardWindowButton(.closeButton)?.isHidden = true
        standardWindowButton(.miniaturizeButton)?.isHidden = true
        standardWindowButton(.zoomButton)?.isHidden = true
    }

    override var canBecomeKey: Bool { false }
    override var canBecomeMain: Bool { false }

    func showView(_ view: some View) {
        let hostingView = NSHostingView(rootView: view)
        let fittingSize = hostingView.fittingSize
        contentView = hostingView
        setContentSize(fittingSize)
        positionAtBottomCenter()
        orderFrontRegardless()
    }

    func positionAtBottomCenter() {
        guard let screen = NSScreen.main else { return }
        let visibleFrame = screen.visibleFrame
        let x = visibleFrame.midX - (frame.width / 2)
        // Sit above the dock/menu-safe area, a bit higher than flush-bottom.
        let y = visibleFrame.minY + 56
        setFrameOrigin(NSPoint(x: x, y: y))
    }
}
