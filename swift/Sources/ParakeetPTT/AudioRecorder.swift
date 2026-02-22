import AVFoundation

final class AudioRecorder {
    private let engine = AVAudioEngine()
    private let mixer = AVAudioMixerNode()
    private var samples: [Float] = []
    private let lock = NSLock()
    private var isRecording = false

    private let targetFormat = AVAudioFormat(
        commonFormat: .pcmFormatFloat32,
        sampleRate: 16000,
        channels: 1,
        interleaved: false
    )!

    init() {
        engine.attach(mixer)
    }

    func startRecording() throws {
        guard !isRecording else { return }

        let inputNode = engine.inputNode
        let hardwareFormat = inputNode.inputFormat(forBus: 0)

        engine.connect(inputNode, to: mixer, format: hardwareFormat)
        engine.connect(mixer, to: engine.mainMixerNode, format: targetFormat)

        // Silence output to prevent feedback
        engine.mainMixerNode.outputVolume = 0

        lock.lock()
        samples = []
        lock.unlock()

        mixer.installTap(onBus: 0, bufferSize: 4096, format: targetFormat) { [weak self] buffer, _ in
            self?.processBuffer(buffer)
        }

        engine.prepare()
        try engine.start()
        isRecording = true
    }

    func stopRecording() -> [Float] {
        guard isRecording else { return [] }

        mixer.removeTap(onBus: 0)
        engine.stop()
        isRecording = false

        lock.lock()
        let captured = samples
        samples = []
        lock.unlock()

        return captured
    }

    private func processBuffer(_ buffer: AVAudioPCMBuffer) {
        guard let channelData = buffer.floatChannelData else { return }
        let frameCount = Int(buffer.frameLength)
        let newSamples = Array(UnsafeBufferPointer(
            start: channelData[0],
            count: frameCount
        ))

        lock.lock()
        samples.append(contentsOf: newSamples)
        lock.unlock()
    }
}
