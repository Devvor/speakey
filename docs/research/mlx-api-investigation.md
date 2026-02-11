# MLX API Investigation

**Date:** 2026-02-12
**Repository:** https://github.com/EliFuzz/parakeet-mlx
**Status:** Production-ready implementation available

## Package Structure

```
parakeet_mlx/
├── __init__.py                 # Main package exports
├── core/
│   ├── config.py              # Configuration classes
│   ├── transcriber.py         # Transcription interface
│   ├── audio_sources.py       # Audio input sources
│   └── performance.py         # Performance monitoring
├── models/
│   ├── parakeet.py            # Parakeet TDT model
│   ├── attention.py           # Attention mechanisms
│   ├── conformer.py           # Conformer blocks
│   └── tokenizer.py           # Text tokenizer
├── audio/
│   └── alignment.py           # Timestamp alignment
└── utils/
    ├── model_loading.py       # Model loading utilities
    └── device_manager.py      # Audio device management
```

## Model Loading

The package provides two APIs:

### Simple API (Recommended for our use case)
```python
from parakeet_mlx import transcribe_file

result = transcribe_file("audio.wav")
print(result.text)
```

### Advanced API
```python
from parakeet_mlx import UnifiedTranscriber, TranscriptionConfig

config = TranscriptionConfig.for_file_transcription(
    file_path="audio.wav",
    chunk_duration=30.0,
    include_timestamps=True
)

transcriber = UnifiedTranscriber(config)
result = transcriber.transcribe()
```

## Transcription API

### Function Signature
```python
def transcribe_file(
    file_path: Union[str, Path],
    chunk_duration: Optional[float] = None,
    **kwargs
) -> AlignedResult
```

### Parameters
- `file_path`: Path to audio file (str or Path)
- `chunk_duration`: Optional chunk size for long audio (seconds)
- `**kwargs`: Additional configuration options

### Return Type: `AlignedResult`
```python
@dataclass
class AlignedResult:
    text: str                           # Full transcription text
    sentences: list[AlignedSentence]    # Sentence-level segments

    @property
    def tokens(self) -> list[AlignedToken]:  # Word-level tokens
        return [token for sentence in self.sentences
                for token in sentence.tokens]
```

## Output Format

### Token Structure (Word-level)
```python
@dataclass
class AlignedToken:
    id: int           # Token ID
    text: str         # Word text
    start: float      # Start time (seconds)
    duration: float   # Duration (seconds)
    end: float        # End time (auto-calculated)
```

### Sentence Structure (Segment-level)
```python
@dataclass
class AlignedSentence:
    text: str                    # Sentence text
    tokens: list[AlignedToken]   # Word tokens
    start: float                 # Start time
    end: float                   # End time
    duration: float              # Duration
```

## Integration Plan

### Backend Implementation Strategy

1. **Import the simple API:**
   ```python
   from parakeet_mlx import transcribe_file
   ```

2. **Convert MLX output to NeMo-compatible format:**
   ```python
   result = transcribe_file(audio_path)

   # Convert to our standard format
   output = {
       "text": result.text,
       "timestamps": {
           "word": [
               {
                   "start": token.start,
                   "end": token.end,
                   "word": token.text
               }
               for token in result.tokens
           ],
           "segment": [
               {
                   "start": sentence.start,
                   "end": sentence.end,
                   "segment": sentence.text
               }
               for sentence in result.sentences
           ]
       }
   }
   ```

3. **Handle errors gracefully:**
   ```python
   try:
       from parakeet_mlx import transcribe_file
       MLX_AVAILABLE = True
   except ImportError:
       MLX_AVAILABLE = False
   ```

## Dependencies

The parakeet-mlx package requires:
- `mlx >= 0.20.0` - Apple's ML framework
- `librosa` - Audio processing
- `soundfile` - Audio I/O
- `numpy` - Numerical operations

Already defined in our `pyproject.toml`:
```toml
[project.optional-dependencies]
mlx = [
    "mlx>=0.20.0",
    "librosa>=0.10.0",
    "soundfile>=0.12.0",
]
```

## Installation

### From PyPI (if available)
```bash
pip install parakeet-mlx
```

### From GitHub
```bash
pip install git+https://github.com/EliFuzz/parakeet-mlx.git
```

### With our project
```bash
pip install -e .[mlx]
# Then separately install parakeet-mlx
pip install git+https://github.com/EliFuzz/parakeet-mlx.git
```

## Key Advantages

1. **Simple API**: Single function call for file transcription
2. **Native Timestamps**: Built-in word and sentence-level timestamps
3. **Compatible Output**: Easy to convert to our standard format
4. **Production Ready**: Active development, comprehensive features
5. **Performance**: Native MLX implementation for Apple Neural Engine

## Implementation Notes

- The `transcribe_file` function handles all complexity internally
- Returns structured data with timestamps built-in
- No need for manual audio preprocessing
- Automatic chunking for long audio files
- Compatible with our existing backend interface

## Next Steps

1. Install parakeet-mlx package
2. Update `src/backends/mlx_backend.py` with actual implementation
3. Test with real audio file
4. Verify output format matches NeMo backend
5. Run integration tests
