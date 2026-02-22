import FluidAudio
import Foundation

actor TranscriptionService {
    private var models: AsrModels?
    private nonisolated(unsafe) var manager: AsrManager?

    func loadModel() async throws {
        let models = try await AsrModels.downloadAndLoad(version: .v3)
        let manager = AsrManager(config: .default)
        try await manager.initialize(models: models)
        self.models = models
        self.manager = manager
    }

    func transcribe(_ audioSamples: [Float]) async throws -> String {
        guard let manager else {
            throw TranscriptionError.notInitialized
        }
        let result = try await manager.transcribe(audioSamples, source: .microphone)
        return result.text
    }
}

enum TranscriptionError: LocalizedError {
    case notInitialized

    var errorDescription: String? {
        switch self {
        case .notInitialized: return "Model not loaded"
        }
    }
}
