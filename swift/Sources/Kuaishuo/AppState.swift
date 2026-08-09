import SwiftUI

@Observable
@MainActor
final class AppState {
    enum Status: Equatable {
        case downloading    // First launch: downloading models from HuggingFace
        case loadingModel   // Loading cached models into memory
        case ready          // Idle, waiting for fn key
        case recording      // fn held, mic active
        case transcribing   // fn released, processing audio
        case error(String)  // Something went wrong
    }

    var status: Status = .loadingModel
    var lastTranscription: String = ""
    /// True while recording in fn+Space hands-free mode (no need to hold fn).
    var isHandsFree = false

    var isRecording: Bool { status == .recording }
    var statusText: String {
        switch status {
        case .downloading:        return "Downloading model (~2.5GB)..."
        case .loadingModel:       return "Loading model..."
        case .ready:              return "Ready"
        case .recording:          return isHandsFree ? "Listening (hands-free)..." : "Recording..."
        case .transcribing:       return "Transcribing..."
        case .error(let message): return "Error: \(message)"
        }
    }

    var statusIcon: String {
        switch status {
        case .downloading:   return "arrow.down.circle"
        case .loadingModel:  return "gear"
        case .ready:         return "waveform"
        case .recording:     return "mic.fill"
        case .transcribing:  return "ellipsis.circle"
        case .error:         return "exclamationmark.triangle"
        }
    }

    var isDownloading: Bool { status == .downloading }
}
