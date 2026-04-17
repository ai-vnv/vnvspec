# Contributing to vnvspec

Thank you for considering contributing to vnvspec!

## Development setup

```bash
git clone https://github.com/ai-vnv-lab/vnvspec.git
cd vnvspec
just install
just check
```

## Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run `just check` to ensure all checks pass
5. Commit and push your changes
6. Open a pull request

## Code quality

All code must pass:

- `ruff format --check .` — formatting
- `ruff check .` — linting
- `mypy --strict src/vnvspec` — type checking
- `pytest --cov-fail-under=85` — tests with coverage

## License

By contributing, you agree that your contributions will be licensed under the Apache-2.0 License.
