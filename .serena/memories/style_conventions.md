# Code Style & Conventions

- Line length: 100 chars
- Formatter: Black
- Linter: Ruff
- Type hints encouraged
- Docstrings required for public functions/classes
- TDD workflow: failing test → implement → pass → commit
- Commit convention: feat:/fix:/test:/docs:/refactor:/chore:
- Coverage target: >80%
- Mock external calls in unit tests; mark integration tests with @pytest.mark.slow
