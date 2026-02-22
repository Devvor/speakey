# Suggested Commands

## Environment
```bash
source venv/bin/activate
```

## Testing
```bash
pytest                              # all tests
pytest -v                           # verbose
pytest tests/test_config.py -v      # specific file
pytest --cov=src --cov-report=term-missing  # with coverage
pytest -m "not slow"                # skip integration tests
```

## Formatting & Linting
```bash
black src/ tests/
ruff check src/ tests/
```

## Running
```bash
parakeet-stt transcribe audio.wav   # CLI transcription
parakeet-stt fn-ptt start           # start push-to-talk
parakeet-stt fn-ptt stop            # stop push-to-talk
parakeet-stt fn-ptt status          # check PTT status
```

## Git
```bash
git status
git add <files>
git commit -m "feat: description"
```
