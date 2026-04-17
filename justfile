# vnvspec task runner

default: check

# Install all dependencies (dev)
install:
    uv sync --all-extras

# Run ruff linter
lint:
    uv run ruff format --check .
    uv run ruff check .

# Run mypy type checker
typecheck:
    uv run mypy --strict src/vnvspec

# Run tests with coverage
test:
    uv run pytest --cov=vnvspec --cov-report=term-missing

# Run tests and enforce coverage threshold
cov:
    uv run pytest --cov=vnvspec --cov-report=term-missing --cov-report=xml --cov-fail-under=85

# Build docs
docs:
    uv run mkdocs build --strict

# Run all checks (master gate)
check: lint typecheck cov

# Clean build artifacts
clean:
    rm -rf dist/ build/ .mypy_cache/ .pytest_cache/ .coverage htmlcov/ site/
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Build package
build:
    uv build
