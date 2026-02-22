import SwiftUI

@Observable
@MainActor
final class AppState {
    enum Status: Equatable {
        case loading       // Model downloading/loading
        case ready         // Idle, waiting for fn key
        case recording     // fn held, mic active
        case transcribing  // fn released, processing audio
        case error(String) // Something went wrong
    }

    var status: Status = .loading
    var lastTranscription: String = ""

    var isRecording: Bool { status == .recording }
    var statusText: String {
        switch status {
        case .loading:            return "Loading model..."
        case .ready:              return "Ready"
        case .recording:          return "Recording..."
        case .transcribing:       return "Transcribing..."
        case .error(let message): return "Error: \(message)"
        }
    }

    var statusIcon: String {
        switch status {
        case .loading:       return "arrow.down.circle"
        case .ready:         return "waveform"
        case .recording:     return "mic.fill"
        case .transcribing:  return "ellipsis.circle"
        case .error:         return "exclamationmark.triangle"
        }
    }
}
