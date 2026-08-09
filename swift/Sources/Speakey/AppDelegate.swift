import AppKit
import AVFoundation
import FluidAudio
import SwiftUI
import UserNotifications

@MainActor
class AppDelegate: NSObject, NSApplicationDelegate {
    let appState = AppState()
    private let transcriptionService = TranscriptionService()
    private let audioRecorder = AudioRecorder()
    private let fnKeyMonitor = FnKeyMonitor()
    private var overlayPanel: OverlayPanel?

    func applicationDidFinishLaunching(_ notification: Notification) {
        SpeakeyLog.write("App launched from \(Bundle.main.bundlePath)")
        promptForAccessibilityIfNeeded()
        SpeakeyLog.write("AX trusted: \(AXIsProcessTrusted())")
        requestMicPermission()
        requestNotificationPermission()
        setupOverlay()
        setupFnKeyMonitor()
        loadModel()
    }

    private func promptForAccessibilityIfNeeded() {
        guard !AXIsProcessTrusted() else { return }
        let options = ["AXTrustedCheckOptionPrompt": true] as CFDictionary
        AXIsProcessTrustedWithOptions(options)
    }

    private func requestMicPermission() {
        switch AVCaptureDevice.authorizationStatus(for: .audio) {
        case .authorized:
            print("[Speakey] Microphone permission: authorized")
        case .notDetermined:
            print("[Speakey] Requesting microphone permission...")
            AVCaptureDevice.requestAccess(for: .audio) { granted in
                print("[Speakey] Microphone permission \(granted ? "granted" : "denied")")
            }
        case .denied, .restricted:
            print("[Speakey] Microphone permission denied — check System Settings > Privacy > Microphone")
            appState.status = .error("Grant Microphone permission in System Settings")
        @unknown default:
            break
        }
    }

    private func requestNotificationPermission() {
        guard Bundle.main.bundleIdentifier != nil else {
            print("[Speakey] Skipping notification permission — no app bundle")
            return
        }
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound]) { granted, error in
            if let error {
                print("[Speakey] Notification permission error: \(error.localizedDescription)")
            } else {
                print("[Speakey] Notification permission \(granted ? "granted" : "denied")")
            }
        }
    }

    // MARK: - Setup

    private func setupOverlay() {
        overlayPanel = OverlayPanel()
    }

    private func setupFnKeyMonitor() {
        fnKeyMonitor.onHoldStart = { [weak self] in
            self?.startRecording(handsFree: false)
        }
        fnKeyMonitor.onRelease = { [weak self] in
            self?.stopRecordingAndTranscribe()
        }
        fnKeyMonitor.onHandsFreeStart = { [weak self] in
            self?.enterHandsFree()
        }
        fnKeyMonitor.onHandsFreeStop = { [weak self] in
            self?.stopRecordingAndTranscribe()
        }
        fnKeyMonitor.onCancel = { [weak self] in
            self?.cancelRecording()
        }

        if !fnKeyMonitor.start() {
            let path = Bundle.main.bundlePath
            appState.status = .error("Quit & reopen after granting permissions")
            SpeakeyLog.write("Event tap failed — path: \(path)")
        }
    }

    private func loadModel() {
        Task {
            do {
                let cacheDir = AsrModels.defaultCacheDirectory(for: .v3)
                let needsDownload = !AsrModels.modelsExist(at: cacheDir, version: .v3)

                if needsDownload {
                    appState.status = .downloading
                    print("[Speakey] Models not cached, downloading...")
                    try await AsrModels.download(version: .v3)
                    print("[Speakey] Download complete")
                }

                appState.status = .loadingModel
                print("[Speakey] Loading model into memory...")
                try await transcriptionService.loadFromCache()
                print("[Speakey] Model loaded successfully")

                appState.status = .ready
                SpeakeyLog.write("Model ready")

                if needsDownload {
                    sendReadyNotification()
                }
            } catch {
                appState.status = .error("Model load failed: \(error.localizedDescription)")
            }
        }
    }

    private func sendReadyNotification() {
        guard Bundle.main.bundleIdentifier != nil else { return }
        let content = UNMutableNotificationContent()
        content.title = "Speakey"
        content.body = "Model ready — hold fn to dictate, or fn+Space for hands-free"
        content.sound = .default

        let request = UNNotificationRequest(
            identifier: "model-ready",
            content: content,
            trigger: nil
        )
        UNUserNotificationCenter.current().add(request) { error in
            if let error {
                print("[Speakey] Failed to send notification: \(error.localizedDescription)")
            }
        }
    }

    // MARK: - Recording pipeline

    private func startRecording(handsFree: Bool) {
        guard appState.status == .ready else { return }
        appState.isHandsFree = handsFree
        appState.status = .recording
        showOverlay()

        do {
            try audioRecorder.startRecording()
        } catch {
            appState.isHandsFree = false
            appState.status = .error("Mic error: \(error.localizedDescription)")
            hideOverlay()
            fnKeyMonitor.resetToIdle()
        }
    }

    /// fn+Space: start hands-free, or convert an in-progress hold session.
    private func enterHandsFree() {
        if appState.status == .recording {
            appState.isHandsFree = true
            updateOverlay()
            return
        }
        startRecording(handsFree: true)
    }

    private func stopRecordingAndTranscribe() {
        Task {
            guard appState.status == .recording else { return }
            appState.isHandsFree = false
            appState.status = .transcribing
            updateOverlay()

            let samples = audioRecorder.stopRecording()
            let duration = Double(samples.count) / 16000.0
            print("[Speakey] Captured \(samples.count) samples (\(String(format: "%.1f", duration))s of audio)")

            let rms: Float
            if samples.isEmpty {
                rms = 0
            } else {
                let maxAmp = samples.map { abs($0) }.max() ?? 0
                rms = sqrt(samples.map { $0 * $0 }.reduce(0, +) / Float(samples.count))
                print("[Speakey] Audio levels — max: \(maxAmp), RMS: \(rms)")
            }

            // Too short or near-silent — skip inference and explain briefly.
            let minDuration = 0.25
            let minRMS: Float = 0.004
            if samples.isEmpty || duration < minDuration || rms < minRMS {
                print("[Speakey] Skipping transcription — empty/short/silent audio")
                await showTransientNotice("No speech detected")
                return
            }

            do {
                let text = try await transcriptionService.transcribe(samples)
                print("[Speakey] Transcription complete (\(text.count) chars)")
                if !text.isEmpty {
                    PasteService.paste(text)
                    appState.lastTranscription = text
                    appState.status = .ready
                    hideOverlay()
                } else {
                    print("[Speakey] Transcription returned empty text")
                    await showTransientNotice("No speech detected")
                }
            } catch {
                print("[Speakey] Transcription error: \(error)")
                await showTransientNotice("Transcription failed", recoverToReady: true)
            }
        }
    }

    /// Brief overlay/status message, then return to ready (avoids stuck error state).
    private func showTransientNotice(_ message: String, recoverToReady: Bool = true) async {
        appState.status = .error(message)
        updateOverlay()
        try? await Task.sleep(nanoseconds: 1_800_000_000)
        if recoverToReady {
            appState.status = .ready
        }
        hideOverlay()
    }

    private func cancelRecording() {
        guard appState.status == .recording else { return }
        _ = audioRecorder.stopRecording()
        appState.isHandsFree = false
        appState.status = .ready
        hideOverlay()
        SpeakeyLog.write("Recording cancelled — discarded")
    }

    // MARK: - Overlay

    private func showOverlay() {
        overlayPanel?.showView(
            OverlayView(status: appState.status, isHandsFree: appState.isHandsFree)
        )
    }

    private func updateOverlay() {
        overlayPanel?.showView(
            OverlayView(status: appState.status, isHandsFree: appState.isHandsFree)
        )
    }

    private func hideOverlay() {
        overlayPanel?.orderOut(nil)
    }
}
