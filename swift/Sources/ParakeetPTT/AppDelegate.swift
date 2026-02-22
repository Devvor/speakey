import AppKit
import SwiftUI

@MainActor
class AppDelegate: NSObject, NSApplicationDelegate {
    let appState = AppState()
    private let transcriptionService = TranscriptionService()
    private let audioRecorder = AudioRecorder()
    private let fnKeyMonitor = FnKeyMonitor()
    private var overlayPanel: OverlayPanel?

    func applicationDidFinishLaunching(_ notification: Notification) {
        setupOverlay()
        setupFnKeyMonitor()
        loadModel()
    }

    // MARK: - Setup

    private func setupOverlay() {
        overlayPanel = OverlayPanel()
    }

    private func setupFnKeyMonitor() {
        fnKeyMonitor.onHoldStart = { [weak self] in
            self?.startRecording()
        }
        fnKeyMonitor.onRelease = { [weak self] in
            self?.stopRecordingAndTranscribe()
        }

        if !fnKeyMonitor.start() {
            appState.status = .error("Grant Accessibility permission in System Settings")
        }
    }

    private func loadModel() {
        Task {
            do {
                try await transcriptionService.loadModel()
                appState.status = .ready
            } catch {
                appState.status = .error("Model load failed: \(error.localizedDescription)")
            }
        }
    }

    // MARK: - Recording pipeline

    private func startRecording() {
        Task {
            guard appState.status == .ready else { return }
            appState.status = .recording
            showOverlay()

            do {
                try audioRecorder.startRecording()
            } catch {
                appState.status = .error("Mic error: \(error.localizedDescription)")
                hideOverlay()
            }
        }
    }

    private func stopRecordingAndTranscribe() {
        Task {
            guard appState.status == .recording else { return }
            appState.status = .transcribing
            updateOverlay()

            let samples = audioRecorder.stopRecording()

            guard !samples.isEmpty else {
                appState.status = .ready
                hideOverlay()
                return
            }

            do {
                let text = try await transcriptionService.transcribe(samples)
                if !text.isEmpty {
                    PasteService.paste(text)
                    appState.lastTranscription = text
                }
            } catch {
                appState.status = .error("Transcription failed: \(error.localizedDescription)")
            }

            appState.status = .ready
            hideOverlay()
        }
    }

    // MARK: - Overlay

    private func showOverlay() {
        let view = OverlayView(status: appState.status)
        overlayPanel?.contentView = NSHostingView(rootView: view)
        overlayPanel?.positionAtTopCenter()
        overlayPanel?.orderFrontRegardless()
    }

    private func updateOverlay() {
        let view = OverlayView(status: appState.status)
        overlayPanel?.contentView = NSHostingView(rootView: view)
    }

    private func hideOverlay() {
        overlayPanel?.orderOut(nil)
    }
}
