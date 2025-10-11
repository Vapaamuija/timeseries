# Makefile for weather-tool development
# Provides convenient commands for code formatting, linting, and testing

.PHONY: help install install-dev format lint test clean pre-commit-install pre-commit-run

# Default target
help:
	@echo "Available commands:"
	@echo "  install          Install the package"
	@echo "  install-dev      Install development dependencies"
	@echo "  format           Format code with black and isort"
	@echo "  lint             Run all linting tools"
	@echo "  lint-black       Check code formatting with black"
	@echo "  lint-isort       Check import sorting with isort"
	@echo "  lint-flake8      Run flake8 linting"
	@echo "  lint-mypy        Run type checking with mypy"
	@echo "  lint-bandit      Run security checks with bandit"
	@echo "  lint-pylint      Run pylint"
	@echo "  test             Run tests with pytest"
	@echo "  test-cov         Run tests with coverage"
	@echo "  clean            Clean build artifacts"
	@echo "  pre-commit-install Install pre-commit hooks"
	@echo "  pre-commit-run   Run pre-commit on all files"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# Code formatting
format:
	@echo "Formatting code with black..."
	black src/ tests/ scripts/ bin/ dev.py
	@echo "Sorting imports with isort..."
	isort src/ tests/ scripts/ bin/ dev.py
	@echo "Formatting complete!"

# Linting
lint: lint-black lint-isort lint-flake8 lint-mypy lint-bandit

lint-black:
	@echo "Checking code formatting with black..."
	black --check src/ tests/ scripts/ bin/ dev.py

lint-isort:
	@echo "Checking import sorting with isort..."
	isort --check-only src/ tests/ scripts/ bin/ dev.py

lint-flake8:
	@echo "Running flake8 linting..."
	flake8 src/ tests/ scripts/ bin/ dev.py

lint-mypy:
	@echo "Running type checking with mypy..."
	mypy src/weather_tool/

lint-bandit:
	@echo "Running security checks with bandit..."
	bandit -r src/ -f json -o bandit-report.json || true
	@echo "Bandit report saved to bandit-report.json"

lint-pylint:
	@echo "Running pylint..."
	pylint src/weather_tool/

# Testing
test:
	@echo "Running tests..."
	pytest tests/

test-cov:
	@echo "Running tests with coverage..."
	pytest tests/ --cov=weather_tool --cov-report=html --cov-report=term-missing

# Pre-commit
pre-commit-install:
	@echo "Installing pre-commit hooks..."
	pre-commit install
	@echo "Pre-commit hooks installed!"

pre-commit-run:
	@echo "Running pre-commit on all files..."
	pre-commit run --all-files

# Cleanup
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf bandit-report.json
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Cleanup complete!"

# Development workflow
dev-setup: install-dev pre-commit-install
	@echo "Development environment setup complete!"
	@echo "Run 'make format' to format your code"
	@echo "Run 'make lint' to check code quality"
	@echo "Run 'make test' to run tests"
