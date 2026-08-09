@preconcurrency import AVFoundation

final class AudioRecorder {
    private var engine: AVAudioEngine?
    private var samples: [Float] = []
    private let lock = NSLock()
    private var isRecording = false
    private var converter: AVAudioConverter?

    private let targetFormat = AVAudioFormat(
        commonFormat: .pcmFormatFloat32,
        sampleRate: 16000,
        channels: 1,
        interleaved: false
    )!

    func startRecording() throws {
        guard !isRecording else { return }

        let engine = AVAudioEngine()
        self.engine = engine

        let inputNode = engine.inputNode
        let nativeFormat = inputNode.outputFormat(forBus: 0)
        print("[Speakey] Mic native format: \(nativeFormat)")

        // Create converter from native mic format to 16kHz mono Float32
        guard let converter = AVAudioConverter(from: nativeFormat, to: targetFormat) else {
            throw RecorderError.converterFailed
        }
        self.converter = converter

        lock.lock()
        samples = []
        lock.unlock()

        inputNode.installTap(onBus: 0, bufferSize: 4096, format: nativeFormat) { [weak self] buffer, _ in
            self?.processBuffer(buffer)
        }

        engine.prepare()
        try engine.start()
        isRecording = true
        print("[Speakey] Recording started")
    }

    func stopRecording() -> [Float] {
        guard isRecording, let engine else { return [] }

        engine.inputNode.removeTap(onBus: 0)
        engine.stop()
        isRecording = false
        self.engine = nil
        self.converter = nil

        lock.lock()
        let captured = samples
        samples = []
        lock.unlock()

        return captured
    }

    private func processBuffer(_ buffer: AVAudioPCMBuffer) {
        guard let converter else { return }

        // Calculate output frame capacity based on sample rate ratio
        let ratio = targetFormat.sampleRate / buffer.format.sampleRate
        let outputFrameCount = AVAudioFrameCount(Double(buffer.frameLength) * ratio)
        guard let outputBuffer = AVAudioPCMBuffer(
            pcmFormat: targetFormat,
            frameCapacity: outputFrameCount
        ) else { return }

        var error: NSError?
        nonisolated(unsafe) var consumed = false
        converter.convert(to: outputBuffer, error: &error) { _, outStatus in
            if consumed {
                outStatus.pointee = .noDataNow
                return nil
            }
            consumed = true
            outStatus.pointee = .haveData
            return buffer
        }

        if let error {
            print("[Speakey] Conversion error: \(error)")
            return
        }

        guard let channelData = outputBuffer.floatChannelData else { return }
        let frameCount = Int(outputBuffer.frameLength)
        guard frameCount > 0 else { return }

        let newSamples = Array(UnsafeBufferPointer(
            start: channelData[0],
            count: frameCount
        ))

        lock.lock()
        samples.append(contentsOf: newSamples)
        lock.unlock()
    }
}

enum RecorderError: LocalizedError {
    case converterFailed

    var errorDescription: String? {
        switch self {
        case .converterFailed: return "Failed to create audio format converter"
        }
    }
}
