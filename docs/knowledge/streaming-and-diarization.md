# Streaming Transcription and Multi-Speaker Diarization

> **Last Updated:** 2026-02-12
> **Current Implementation:** Batch processing with Parakeet-TDT 0.6B v3

---

## Table of Contents

1. [Current Implementation: Batch Processing](#current-implementation-batch-processing)
2. [Buffer Architecture](#buffer-architecture)
3. [Streaming Model Options](#streaming-model-options)
4. [Multi-Speaker Diarization](#multi-speaker-diarization)
5. [Accuracy Comparison](#accuracy-comparison)
6. [Audio Quality Requirements](#audio-quality-requirements)
7. [Implementation Recommendations](#implementation-recommendations)

---

## Current Implementation: Batch Processing

### How It Works

The daemon mode uses **batch processing** - transcription occurs **after** recording is complete:

```
┌─────────────────────────────────────────────────┐
│  1. User starts recording                       │
│     └─> Audio buffered in memory               │
├─────────────────────────────────────────────────┤
│  2. User stops recording                        │
│     └─> recorder.stop() returns complete audio │
├─────────────────────────────────────────────────┤
│  3. Audio saved to temp file                    │
│     └─> Entire recording written to .wav       │
├─────────────────────────────────────────────────┤
│  4. Model transcribes complete file             │
│     └─> model.transcribe(tmp_path)             │
├─────────────────────────────────────────────────┤
│  5. Result returned to user                     │
│     └─> Text copied to clipboard               │
└─────────────────────────────────────────────────┘
```

### Key Code Flow

```python
# src/daemon/controller.py
def stop_recording(self) -> dict:
    # Stop recording - gets ALL recorded audio
    audio_data = self.recorder.stop()

    # Save complete audio to temp file
    self.recorder.save_audio(tmp_path)

    # Transcribe the ENTIRE file
    result = self.model.transcribe(tmp_path, timestamps=False)

    return {"status": "ok", "text": transcription}
```

### Why Batch Processing?

**Advantages:**
- ✅ **Highest accuracy** - Full context for punctuation and capitalization
- ✅ **Best model performance** - 6.05% WER (best in class)
- ✅ **Simpler implementation** - No chunking or stream management
- ✅ **Multilingual support** - 25 European languages
- ✅ **Still feels fast** - <2 seconds for typical dictation

**Use case:** Perfect for push-to-talk dictation where users speak a sentence/paragraph then release to transcribe.

---

## Buffer Architecture

### Implementation Details

```python
# src/ptt/recorder.py
class AudioRecorder:
    def __init__(self, config: Config):
        self.audio_buffer = []  # Python list (dynamic size)
        self.is_recording = False

    def _audio_callback(self, indata, frames, time, status):
        """Called every 64ms with new audio chunk."""
        if self.is_recording:
            self.audio_buffer.append(indata.copy())  # Grows indefinitely
```

### How the Buffer Works

```
Microphone → sounddevice → _audio_callback() → audio_buffer
                                                      ↓
                                          [chunk1, chunk2, ..., chunkN]
                                                      ↓
                                          Grows dynamically in RAM
```

**Key characteristics:**
- **Dynamic size** - Python list with no fixed limit
- **No data loss** - Earlier audio is never overwritten
- **Memory efficient** - ~64 KB/second or ~3.8 MB/minute
- **Concatenated on stop** - All chunks merged into single array

### Memory Usage

| Duration | Memory Used | Status |
|----------|-------------|--------|
| 1 minute | ~1.9 MB | ✅ Trivial |
| 5 minutes | ~9.5 MB | ✅ Recommended max |
| 10 minutes | ~19 MB | ✅ No problem |
| 1 hour | ~114 MB | ✅ Still fine |
| 10 hours | ~1.1 GB | ⚠️ Works but not recommended |

**Practical limit:** Only constrained by system RAM. Modern systems (8-32GB) can handle hours of recording before memory becomes an issue.

### Can Audio Get Cut Off?

**No.** The buffer will never discard earlier audio. Possible failure modes:

1. **System runs out of RAM** (extremely rare)
   - Would raise `MemoryError` exception
   - Not silent data loss

2. **Audio driver buffer overflow** (very rare)
   - sounddevice would print warning
   - Callback prints status if issues occur

3. **Process killed** (external)
   - User force-quits daemon
   - System crashes
   - OOM killer

**Best practice:** Keep recordings under 5-10 minutes for optimal transcription quality and user experience.

---

## Streaming Model Options

### Overview

NVIDIA offers three streaming ASR models for real-time transcription:

| Model | Size | Languages | Speakers | Latency | Punctuation |
|-------|------|-----------|----------|---------|-------------|
| Nemotron Speech Streaming | 0.6B | English | Single | 80ms - 1.12s | ✅ Yes |
| Parakeet RNNT | 1.1B | English | Single | Moderate | ❌ No |
| Multitalker Parakeet Streaming | 0.6B | English | Multiple | 80ms - 1.12s | ✅ Yes |

### 1. Nemotron Speech Streaming (0.6B)

**Model:** `nvidia/nemotron-speech-streaming-en-0.6b`

**Use case:** Ultra-low latency voice assistants and conversational AI

**Architecture:** Cache-aware streaming with RNN-T decoder

**Performance:**
- Average WER: 7.16% (1.12s chunks)
- Latency range: 80ms - 1120ms (configurable)
- Native punctuation and capitalization

**Strengths:**
- ✅ Lowest latency option
- ✅ Runtime flexibility (adjust chunk size without retraining)
- ✅ Superior throughput and GPU memory efficiency
- ✅ Cache-aware architecture (non-overlapping frames)

**Limitations:**
- ❌ English only
- ❌ Single speaker (no diarization)
- ❌ Latency-accuracy tradeoff (80ms chunks = 8.5% WER)

**Best for:** Live captions, voice assistants, real-time feedback where immediate response matters more than perfect accuracy.

---

### 2. Parakeet RNNT (1.1B)

**Model:** `nvidia/parakeet-rnnt-1.1b`

**Use case:** High-accuracy general-purpose streaming transcription

**Architecture:** FastConformer Transducer with RNN-T

**Performance:**
- Best WER: 1.46% (LibriSpeech clean)
- Average WER: ~9.96% (across datasets)
- Largest model (1.1B parameters)

**Strengths:**
- ✅ Highest accuracy among streaming models
- ✅ Large model capacity (1.1B params)
- ✅ 64K hours of training data

**Limitations:**
- ❌ No punctuation or capitalization (lowercase only)
- ❌ English only
- ❌ Single speaker (no diarization)
- ❌ Heavier resource requirements

**Best for:** Scenarios where accuracy is paramount and punctuation can be added post-processing.

---

### 3. Multitalker Parakeet Streaming (0.6B) ⭐

**Model:** `nvidia/multitalker-parakeet-streaming-0.6b-v1`

**Use case:** Multi-speaker meetings and conversations with overlapping speech

**Architecture:** Self-speaker adaptation with speaker kernel injection

**Performance:**
- Single-speaker WER: 7.44%
- Multi-speaker cpWER: 15-37% (depends on overlap severity)
- Latency: 80ms - 1120ms (configurable)

**Strengths:**
- ✅ **Multi-speaker support** (identifies who spoke when)
- ✅ **Handles overlapping speech** (simultaneous speakers)
- ✅ No speaker enrollment required
- ✅ Native punctuation and capitalization
- ✅ Real-time streaming capability

**Limitations:**
- ❌ Requires external diarization model first
- ❌ Computational cost scales with speakers (N speakers = N×compute)
- ❌ English only
- ❌ Higher WER in overlapping scenarios (15-37%)
- ❌ Quality depends on diarization accuracy

**Best for:** Meeting transcriptions, multi-party conversations, scenarios with brief speaker overlaps.

#### How Multitalker Works

```
┌─────────────────────────────────────────────────┐
│  Audio Input (Multi-speaker + Overlaps)         │
└─────────────────┬───────────────────────────────┘
                  │
        ┌─────────▼──────────┐
        │  Diarization Model │  ← Identifies speakers
        │  (Sortformer)      │     and their timing
        └─────────┬──────────┘
                  │
        ┌─────────▼──────────┐
        │  ASR Model × N     │  ← One instance per speaker
        │  (Multitalker)     │     Transcribes each stream
        └─────────┬──────────┘
                  │
        ┌─────────▼──────────┐
        │  Merged Output     │  ← Combined transcript
        │  [Speaker A]: text │     with speaker labels
        │  [Speaker B]: text │
        └────────────────────┘
```

**Required components:**
1. Diarization model: `nvidia/diar_streaming_sortformer_4spk-v2.1`
2. ASR model: One instance per detected speaker
3. Synchronization logic: Merge outputs with timestamps

**Example usage:**
```python
from nemo.collections.asr.models import SortformerEncLabelModel, ASRModel

# Load diarization model
diar_model = SortformerEncLabelModel.from_pretrained(
    "nvidia/diar_streaming_sortformer_4spk-v2.1"
).eval().to("cuda")

# Load ASR model
asr_model = ASRModel.from_pretrained(
    "nvidia/multitalker-parakeet-streaming-0.6b-v1"
).eval().to("cuda")

# Configure and run streaming transcription
# (See model card for full implementation)
```

---

## Multi-Speaker Diarization

### What is Diarization?

**Speaker diarization** answers the question: "Who spoke when?"

Output format:
```
[00:00 - 00:05] Speaker A: "Hello, how are you today?"
[00:05 - 00:08] Speaker B: "I'm doing great, thanks for asking."
[00:08 - 00:12] Speaker A: "That's wonderful to hear."
```

### Diarization Approaches

#### 1. **Post-Processing Diarization** (Compatible with Current Setup)

Use separate diarization model after transcription:

```python
# Step 1: Record and transcribe with Parakeet-TDT (high accuracy)
transcription = model.transcribe(audio_file)

# Step 2: Run diarization separately
from pyannote.audio import Pipeline
diarization = Pipeline.from_pretrained("pyannote/speaker-diarization")
speakers = diarization(audio_file)

# Step 3: Merge results (align text with speaker segments)
result = align_text_with_speakers(transcription, speakers)
```

**Pros:**
- ✅ Keep current high accuracy (6.05% WER)
- ✅ Simpler implementation
- ✅ Already working system

**Cons:**
- ❌ Not real-time (post-hoc processing)
- ❌ Two separate models
- ❌ Alignment can be imperfect

**Popular diarization tools:**
- [pyannote.audio](https://github.com/pyannote/pyannote-audio) - State-of-the-art Python library
- [NeMo Sortformer](https://huggingface.co/nvidia/diar_streaming_sortformer_4spk-v2.1) - NVIDIA's streaming diarization

---

#### 2. **Integrated Streaming Diarization** (Multitalker Model)

Use Multitalker Parakeet Streaming for real-time speaker identification:

**Architecture:**
```
Real-time Audio Stream
        ↓
Streaming Diarization (who's speaking now?)
        ↓
Speaker-specific ASR instances (what are they saying?)
        ↓
Merged transcript with speaker labels
```

**Pros:**
- ✅ True real-time streaming
- ✅ See speaker labels as they speak
- ✅ Handles overlapping speech

**Cons:**
- ❌ Lower accuracy (7-37% WER vs 6.05%)
- ❌ Complex setup (2 models + synchronization)
- ❌ Computational cost scales with speakers
- ❌ English only

---

### Speaker Overlap Handling

**Multitalker Parakeet Streaming** uniquely handles overlapping speech:

| Scenario | Capability | Performance |
|----------|------------|-------------|
| Turn-taking (no overlap) | ✅ Excellent | 7.44% WER |
| Brief overlaps (<500ms) | ✅ Good | ~15% cpWER |
| Moderate overlaps | ✅ Acceptable | ~23% cpWER |
| Severe overlaps (>50% overlap time) | ⚠️ Degraded | ~37% cpWER |

**Current Parakeet-TDT:** Does not handle overlapping speech - would transcribe as garbled text.

---

## Accuracy Comparison

### Word Error Rate (WER) Benchmarks

| Model | Avg WER | Best Case | Worst Case | Punctuation | Languages |
|-------|---------|-----------|------------|-------------|-----------|
| **Parakeet-TDT 0.6B v3** (current) | **6.05%** | 1.92% (clean) | 12.21% (-5dB SNR) | ✅ Excellent | 25 |
| Nemotron Streaming | 7.16% | 2.31% (clean) | 8.5% (80ms chunks) | ✅ Good | 1 |
| Parakeet RNNT | 9.96% | 1.46% (clean) | 17.1% (meetings) | ❌ None | 1 |
| Multitalker (single) | 7.44% | ~2% (clean) | ~15% (overlaps) | ✅ Good | 1 |
| Multitalker (multi) | 15-37% | 15% (brief overlaps) | 37% (severe overlaps) | ✅ Good | 1 |

### Error Rate Increase

Compared to current Parakeet-TDT:

```
Nemotron Streaming:     +18% more errors (single speaker)
Parakeet RNNT:          +65% more errors
Multitalker (single):   +23% more errors (single speaker)
Multitalker (multi):    +150-500% more errors (overlapping speech)
```

### What This Means Practically

**6.05% WER (Parakeet-TDT - Current):**
> "This is a test of the speech to text system with high accuracy."
>
> ✓ Perfect transcription (0 errors in 11 words)

**15% WER (Multitalker with overlaps):**
> "This is test the speech text system high accuracy."
>
> ✗ 2-3 errors per sentence (missing "a", "of", "to", "with")

**37% WER (Multitalker with severe overlaps):**
> "This test speech text high accuracy."
>
> ✗✗ 4+ errors per sentence (unusable for production)

### Context and Punctuation Quality

| Feature | Parakeet-TDT | Streaming Models |
|---------|--------------|------------------|
| **Sentence boundaries** | ✅ Excellent (full context) | ⚠️ Good (limited lookahead) |
| **Capitalization** | ✅ Proper nouns, sentences | ⚠️ May miss proper nouns |
| **Punctuation placement** | ✅ Accurate (sees full utterance) | ⚠️ May break mid-sentence |
| **Context understanding** | ✅ Full utterance | ⚠️ Sliding window only |

**Why:** Batch models see the entire utterance before deciding on punctuation. Streaming models must make decisions with partial context.

---

## Audio Quality Requirements

### Signal-to-Noise Ratio (SNR) Performance

**Parakeet-TDT 0.6B v3** noise robustness:

| SNR Level | WER | Audio Quality | Use Case |
|-----------|-----|---------------|----------|
| **100-25 dB** | 1.92-1.96% | Studio quality | Professional recording |
| **10 dB** | ~6% | Normal speaking | Typical office/home |
| **5 dB** | ~8.39% | Noisy environment | Coffee shop, street |
| **0 dB** | ~10-12% | Very noisy | Loud background |
| **-5 dB** | 12.21% | Severe noise | Voice = noise level |

### Microphone Distance Guidelines

**Optimal Range** (1-2 feet / 30-60 cm):
- Clean audio, minimal background noise
- SNR ~40+ dB
- Best transcription accuracy

**Acceptable Range** (3-5 feet / 1-1.5 m):
- Normal room environment
- SNR ~20-30 dB
- Some background noise tolerable

**Degraded Range** (6+ feet / 2+ m):
- SNR <10 dB
- Expect 10-15% WER
- Not recommended for production use

### Recording Duration Limits

**Technical limits:**
- No hard limit (buffer grows dynamically)
- Only limited by system RAM

**Practical recommendations:**

| Duration | Memory | Transcription Time | Recommendation |
|----------|--------|-------------------|----------------|
| 10-60s | <4 MB | <2s | ✅ Ideal for dictation |
| 1-5 min | <20 MB | 2-10s | ✅ Recommended max |
| 5-10 min | <40 MB | 10-20s | ⚠️ Acceptable |
| >10 min | >40 MB | >20s | ❌ Use file transcription |

**Why limit duration:**
- Model context window optimized for shorter utterances
- User experience (long waits feel bad)
- Accuracy may degrade on very long recordings

---

## Implementation Recommendations

### Scenario 1: Current Use Case (Single Speaker Dictation)

**Recommendation:** **Keep current Parakeet-TDT batch processing**

**Rationale:**
- ✅ Best accuracy (6.05% WER)
- ✅ Excellent punctuation/capitalization
- ✅ Simplest implementation (already working)
- ✅ Fast enough (<2s transcription feels instant)
- ✅ Multilingual support (25 languages)

**When to use:**
- Push-to-talk dictation
- Voice commands
- Short-form transcription
- Single speaker scenarios

---

### Scenario 2: Multi-Speaker Meetings (Post-Processing)

**Recommendation:** **Parakeet-TDT + Post-hoc Diarization**

**Implementation:**
```python
# Step 1: Record with daemon (high quality)
audio_file = record_audio()

# Step 2: Transcribe with Parakeet-TDT (6.05% WER)
transcription = model.transcribe(audio_file)

# Step 3: Run diarization separately
from pyannote.audio import Pipeline
diarization = Pipeline.from_pretrained("pyannote/speaker-diarization")
speakers = diarization(audio_file)

# Step 4: Align text with speakers
result = align_text_with_speakers(transcription, speakers)
```

**Pros:**
- ✅ Best accuracy for transcription (6.05%)
- ✅ Separate concern (ASR vs diarization)
- ✅ Proven, mature libraries (pyannote)
- ✅ No streaming complexity

**Cons:**
- ❌ Not real-time (batch processing)
- ❌ Two-step process
- ❌ Alignment may have imperfections

**When to use:**
- Meeting recordings (post-meeting review)
- Interviews
- Multi-speaker scenarios without real-time requirement

---

### Scenario 3: Real-Time Multi-Speaker Streaming

**Recommendation:** **Multitalker Parakeet Streaming**

**Implementation:**
```python
# Load models
diar_model = SortformerEncLabelModel.from_pretrained(
    "nvidia/diar_streaming_sortformer_4spk-v2.1"
)

asr_model = ASRModel.from_pretrained(
    "nvidia/multitalker-parakeet-streaming-0.6b-v1"
)

# Stream audio in chunks
for audio_chunk in audio_stream:
    # Diarize chunk (who's speaking?)
    speaker_labels = diar_model.process(audio_chunk)

    # Transcribe per speaker
    for speaker in active_speakers:
        text = asr_model.transcribe(audio_chunk, speaker_id)
        display(f"[{speaker}]: {text}")
```

**Pros:**
- ✅ True real-time streaming
- ✅ Speaker identification as they speak
- ✅ Handles overlapping speech
- ✅ Live captions with speaker labels

**Cons:**
- ❌ Much lower accuracy (7-37% WER)
- ❌ Complex implementation (2 models + sync)
- ❌ Computational cost scales with speakers
- ❌ English only

**When to use:**
- Live meeting captions
- Real-time conversation transcription
- Scenarios where immediate feedback > accuracy
- Multi-speaker voice assistants

---

### Scenario 4: Pseudo-Streaming (Hybrid Approach)

**Recommendation:** **Parakeet-TDT with VAD-based sentence segmentation**

**Concept:** Split long recordings into sentences using Voice Activity Detection (VAD), transcribe each separately, display progressively.

**Implementation:**
```python
import torch
from pyannote.audio import Model

# Load VAD model
vad_model = Model.from_pretrained("pyannote/segmentation")

# During recording, detect sentence boundaries
for audio_chunk in recording_stream:
    # Detect if sentence ended (silence detection)
    if vad_detects_sentence_end(audio_chunk):
        # Transcribe completed sentence
        text = model.transcribe(sentence_buffer)
        display(text)  # Show progressively

        # Reset buffer for next sentence
        sentence_buffer.clear()
```

**Pros:**
- ✅ High accuracy (6.05% WER - keeps Parakeet-TDT)
- ✅ Feels like streaming (progressive display)
- ✅ Maintains excellent punctuation
- ✅ No new ASR model needed

**Cons:**
- ❌ Not true real-time (sentence-level latency)
- ❌ VAD accuracy affects UX
- ❌ No mid-sentence updates

**When to use:**
- Long-form dictation (articles, documents)
- Want streaming feel with batch accuracy
- Single speaker scenarios

---

## Decision Matrix

| Requirement | Recommended Approach | Model |
|-------------|---------------------|-------|
| **Single speaker, highest accuracy** | Current setup | Parakeet-TDT 0.6B v3 |
| **Multi-speaker, post-processing OK** | Batch + diarization | Parakeet-TDT + pyannote |
| **Multi-speaker, real-time required** | Streaming | Multitalker Parakeet Streaming |
| **Live captions, single speaker** | Streaming | Nemotron Speech Streaming |
| **Long-form, progressive display** | Pseudo-streaming | Parakeet-TDT + VAD |
| **Brief overlaps, accuracy priority** | Post-processing | Parakeet-TDT + pyannote |
| **Severe overlaps, real-time needed** | Streaming (accept lower accuracy) | Multitalker Parakeet Streaming |

---

## References

### Model Documentation

- [NVIDIA Parakeet-TDT 0.6B v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) - Current model
- [NVIDIA Nemotron Speech Streaming](https://huggingface.co/nvidia/nemotron-speech-streaming-en-0.6b)
- [NVIDIA Parakeet RNNT 1.1B](https://huggingface.co/nvidia/parakeet-rnnt-1.1b)
- [NVIDIA Multitalker Parakeet Streaming](https://huggingface.co/nvidia/multitalker-parakeet-streaming-0.6b-v1)

### Research Papers

- [Canary-1B-v2 & Parakeet-TDT-0.6B-v3 Paper](https://arxiv.org/pdf/2509.14128) - Training details and benchmarks
- [NVIDIA Speech AI Performance Analysis](https://developer.nvidia.com/blog/nvidia-speech-ai-models-deliver-industry-leading-accuracy-and-performance/)

### Diarization Tools

- [pyannote.audio](https://github.com/pyannote/pyannote-audio) - Python speaker diarization
- [NeMo Sortformer Diarizer](https://huggingface.co/nvidia/diar_streaming_sortformer_4spk-v2.1) - Streaming diarization

### Technical Blogs

- [Modal: Streaming Audio Transcription](https://modal.com/docs/examples/streaming_parakeet)
- [NVIDIA: Pushing Boundaries with Parakeet ASR](https://developer.nvidia.com/blog/pushing-the-boundaries-of-speech-recognition-with-nemo-parakeet-asr-models/)
- [NeMo ASR Models Guide](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/models.html)

---

## Conclusion

**For current use case (single-speaker dictation):** The existing Parakeet-TDT batch processing provides optimal accuracy and user experience.

**For future multi-speaker requirements:** Consider post-processing diarization first (keeps high accuracy), only move to streaming models if real-time speaker identification is critical to the workflow.

**Key takeaway:** Streaming models trade 20-500% more errors for real-time feedback. This tradeoff is only worth it when immediate response is essential to the user experience.
