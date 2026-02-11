# Parakeet TDT 0.6B V3 Model Overview

## Model Information

**Model:** nvidia/parakeet-tdt-0.6b-v3
**Type:** Speech-to-Text (Automatic Speech Recognition)
**Architecture:** FastConformer-TDT with full attention
**Parameters:** 600 million
**License:** CC-BY-4.0
**Runtime:** NeMo 2.2+
**Languages:** 25 European languages with automatic detection

### Supported Languages

Bulgarian (bg), Croatian (hr), Czech (cs), Danish (da), Dutch (nl), English (en), Estonian (et), Finnish (fi), French (fr), German (de), Greek (el), Hungarian (hu), Italian (it), Latvian (lv), Lithuanian (lt), Maltese (mt), Polish (pl), Portuguese (pt), Romanian (ro), Slovak (sk), Slovenian (sl), Spanish (es), Swedish (sv), Russian (ru), Ukrainian (uk)

## Installation

```bash
pip install -U nemo_toolkit["asr"]
```

## Model Loading

```python
import nemo.collections.asr as nemo_asr

asr_model = nemo_asr.models.ASRModel.from_pretrained(
    model_name="nvidia/parakeet-tdt-0.6b-v3"
)
```

## Basic Usage

### Simple Transcription

```python
# Transcribe audio file
output = asr_model.transcribe(['audio_file.wav'])
print(output[0].text)
```

### Transcription with Timestamps

```python
output = asr_model.transcribe(
    ['audio_file.wav'],
    timestamps=True
)

# Access different timestamp levels
word_timestamps = output[0].timestamp['word']      # Word-level
segment_timestamps = output[0].timestamp['segment'] # Segment-level
char_timestamps = output[0].timestamp['char']       # Character-level

# Display segments with timestamps
for stamp in segment_timestamps:
    print(f"{stamp['start']}s - {stamp['end']}s : {stamp['segment']}")
```

## Technical Specifications

### Audio Requirements

- **Sample Rate:** 16kHz monochannel
- **Supported Formats:** .wav and .flac
- **Output:** Includes punctuation and capitalization

### Hardware Requirements

- **Minimum RAM:** 2GB (larger RAM supports longer audio inputs)
- **Supported GPUs:** NVIDIA Ampere, Blackwell, Hopper, Volta architectures
- **Operating System:** Linux (preferred)

### Performance Metrics

- **Average WER:** 6.05% across benchmark datasets
- **RTFx:** 3380 on HF-Open-ASR leaderboard (batch size 128)
- **Real-time Performance:** Very fast inference speed
- **Noise Robustness:** Tested on SNR 10, 5, 0, -5 dB levels
- **Telephony Support:** Compatible with μ-law 8kHz audio

## Key Features

- Word, segment, and character-level timestamps
- Punctuation and capitalization included in output
- Noise robust transcription
- Telephony audio support
- High accuracy with low word error rate
- Extremely fast real-time performance

## Resources

- **HuggingFace Page:** https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3
- **Documentation:** [NeMo ASR Models](https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/en/main/asr/models.html)
- **Demo:** [HuggingFace Spaces](https://huggingface.co/spaces/nvidia/parakeet-tdt-0.6b-v3)

## Notes for Mac ANE Implementation

For Apple Neural Engine (ANE) acceleration on Mac:
- NeMo natively uses PyTorch
- May require ONNX export and CoreML conversion
- Need to investigate CoreML compatibility for ANE acceleration
- Alternative: Use Metal Performance Shaders (MPS) backend in PyTorch for GPU acceleration on Mac

## Notes for Windows Implementation

- CUDA GPU support available through NVIDIA GPU drivers
- CPU fallback supported
- Ensure proper CUDA toolkit installation for GPU acceleration
