# Task Completion Checklist

1. Run tests: `pytest -v`
2. Check coverage: `pytest --cov=src --cov-report=term-missing`
3. Format: `black src/ tests/`
4. Lint: `ruff check src/ tests/`
5. Verify no regressions in existing tests
6. Commit with conventional message
