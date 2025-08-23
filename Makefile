# Development commands for DVGE

.PHONY: install test lint format type-check clean dev-install setup-hooks

# Install dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
dev-install:
	pip install -r requirements.txt
	pip install pre-commit isort
	pre-commit install

# Setup pre-commit hooks
setup-hooks:
	pre-commit install
	pre-commit autoupdate

# Run tests
test:
	python -m pytest tests/ -v

# Run tests with coverage
test-cov:
	python -m pytest tests/ -v --cov=dvge --cov-report=html --cov-report=term

# Lint code
lint:
	flake8 dvge/ tests/
	mypy dvge/

# Format code
format:
	black dvge/ tests/
	isort dvge/ tests/

# Type checking
type-check:
	mypy dvge/

# Run all quality checks
quality: format lint test

# Clean build artifacts
clean:
	find . -type f -name "*.pyc" -delete || true
	find . -type d -name "__pycache__" -delete || true
	rm -rf .pytest_cache htmlcov .mypy_cache .coverage || true

# Run the application
run:
	python main.py

# Build package
build:
	python -m build

# Help
help:
	@echo "Available commands:"
	@echo "  install      - Install runtime dependencies"
	@echo "  dev-install  - Install development dependencies"
	@echo "  setup-hooks  - Setup pre-commit hooks"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linters"
	@echo "  format       - Format code with black and isort"
	@echo "  type-check   - Run type checking"
	@echo "  quality      - Run all quality checks"
	@echo "  clean        - Clean build artifacts"
	@echo "  run          - Run the application"
	@echo "  build        - Build package"