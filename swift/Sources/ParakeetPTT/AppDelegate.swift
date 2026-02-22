import AppKit
import AVFoundation
import SwiftUI

@MainActor
class AppDelegate: NSObject, NSApplicationDelegate {
    let appState = AppState()
    private let transcriptionService = TranscriptionService()
    private let audioRecorder = AudioRecorder()
    private let fnKeyMonitor = FnKeyMonitor()
    private var overlayPanel: OverlayPanel?

    func applicationDidFinishLaunching(_ notification: Notification) {
        requestMicPermission()
        setupOverlay()
        setupFnKeyMonitor()
        loadModel()
    }

    private func requestMicPermission() {
        switch AVCaptureDevice.authorizationStatus(for: .audio) {
        case .authorized:
            print("[PTT] Microphone permission: authorized")
        case .notDetermined:
            print("[PTT] Requesting microphone permission...")
            AVCaptureDevice.requestAccess(for: .audio) { granted in
                print("[PTT] Microphone permission \(granted ? "granted" : "denied")")
            }
        case .denied, .restricted:
            print("[PTT] Microphone permission denied — check System Settings > Privacy > Microphone")
            appState.status = .error("Grant Microphone permission in System Settings")
        @unknown default:
            break
        }
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
            let duration = Double(samples.count) / 16000.0
            print("[PTT] Captured \(samples.count) samples (\(String(format: "%.1f", duration))s of audio)")

            // Check audio levels
            if !samples.isEmpty {
                let maxAmp = samples.map { abs($0) }.max() ?? 0
                let rms = sqrt(samples.map { $0 * $0 }.reduce(0, +) / Float(samples.count))
                print("[PTT] Audio levels — max: \(maxAmp), RMS: \(rms)")
            }

            guard !samples.isEmpty else {
                print("[PTT] No samples captured, skipping transcription")
                appState.status = .ready
                hideOverlay()
                return
            }

            do {
                let text = try await transcriptionService.transcribe(samples)
                print("[PTT] Transcription result: '\(text)'")
                if !text.isEmpty {
                    PasteService.paste(text)
                    appState.lastTranscription = text
                } else {
                    print("[PTT] Transcription returned empty text")
                }
            } catch {
                print("[PTT] Transcription error: \(error)")
                appState.status = .error("Transcription failed: \(error.localizedDescription)")
            }

            appState.status = .ready
            hideOverlay()
        }
    }

    // MARK: - Overlay

    private func showOverlay() {
        overlayPanel?.showView(OverlayView(status: appState.status))
    }

    private func updateOverlay() {
        overlayPanel?.showView(OverlayView(status: appState.status))
    }

    private func hideOverlay() {
        overlayPanel?.orderOut(nil)
    }
}
