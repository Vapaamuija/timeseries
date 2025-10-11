# Code Formatting and Quality Tools

This document describes the code formatting and quality tools configured for the weather-tool project.

## Overview

The project uses a comprehensive set of tools to ensure code quality, consistency, and security:

- **Black**: Code formatter for consistent Python code style
- **isort**: Import sorting and organization
- **flake8**: Linting for style and programming errors
- **mypy**: Static type checking
- **bandit**: Security vulnerability scanner
- **pylint**: Additional code analysis
- **pre-commit**: Git hooks for automated quality checks

## Quick Start

### 1. Install Development Dependencies

```bash
# Install all development tools
pip install -e ".[dev]"

# Or install manually
pip install black isort flake8 mypy bandit pylint pre-commit
```

### 2. Install Pre-commit Hooks

```bash
# Install pre-commit hooks (recommended)
pre-commit install

# Or use the development script
python dev.py pre-commit-install
```

### 3. Format Your Code

```bash
# Format all code
python dev.py format

# Or use individual tools
black src/ tests/ scripts/ bin/ dev.py
isort src/ tests/ scripts/ bin/ dev.py
```

## Available Commands

### Using the Development Script (`dev.py`)

```bash
# Format code
python dev.py format

# Run all linting checks
python dev.py lint

# Run tests
python dev.py test

# Run tests with coverage
python dev.py test-cov

# Install pre-commit hooks
python dev.py pre-commit-install

# Run pre-commit on all files
python dev.py pre-commit-run

# Clean build artifacts
python dev.py clean

# Run everything (format, lint, test)
python dev.py all
```

### Using Make

```bash
# Format code
make format

# Run linting
make lint

# Run tests
make test

# Run tests with coverage
make test-cov

# Install pre-commit hooks
make pre-commit-install

# Clean build artifacts
make clean

# Show all available commands
make help
```

### Using Individual Tools

```bash
# Black formatting
black src/ tests/ scripts/ bin/ dev.py
black --check src/ tests/ scripts/ bin/ dev.py  # Check only

# Import sorting
isort src/ tests/ scripts/ bin/ dev.py
isort --check-only src/ tests/ scripts/ bin/ dev.py  # Check only

# Linting
flake8 src/ tests/ scripts/ bin/ dev.py

# Type checking
mypy src/weather_tool/

# Security scanning
bandit -r src/ -f json -o bandit-report.json

# Additional linting
pylint src/weather_tool/
```

## Configuration Files

### `pyproject.toml`
Main configuration file containing settings for:
- Black formatting rules
- isort import sorting
- mypy type checking
- flake8 linting
- bandit security scanning
- pylint analysis
- pytest testing

### `.pre-commit-config.yaml`
Pre-commit hooks configuration that runs:
- General file checks (trailing whitespace, YAML validation, etc.)
- Black formatting
- isort import sorting
- flake8 linting
- mypy type checking
- bandit security scanning
- pylint analysis
- Jupyter notebook formatting

### `.flake8`
Additional flake8 configuration with:
- Line length: 88 characters (compatible with Black)
- Ignored error codes that conflict with Black
- File-specific ignore rules
- Complexity limits

### `.bandit`
Bandit security scanner configuration:
- Excluded directories (tests, etc.)
- Skipped security checks
- Severity and confidence levels

## Code Style Guidelines

### Formatting Rules

1. **Line Length**: 88 characters maximum
2. **String Quotes**: Use double quotes by default
3. **Import Organization**: 
   - Standard library imports first
   - Third-party imports second
   - Local imports last
   - Each group separated by blank lines

### Type Hints

- Use comprehensive type hints for all function signatures
- Use `typing` module for complex types
- Use `Optional` for nullable values
- Use `Union` for multiple possible types

### Documentation

- Use docstrings following NumPy/SciPy standards
- Include type information in docstrings
- Document complex weather calculations with inline comments
- Include units in variable names and documentation

### Error Handling

- Use early returns for invalid conditions
- Place the happy path last in functions
- Implement proper logging using configured logger
- Use custom exceptions for weather-specific errors

## Pre-commit Workflow

Pre-commit hooks automatically run when you commit code:

1. **Trailing whitespace removal**
2. **End-of-file fixing**
3. **YAML/JSON/TOML validation**
4. **Large file detection**
5. **Merge conflict detection**
6. **Code formatting with Black**
7. **Import sorting with isort**
8. **Linting with flake8**
9. **Type checking with mypy**
10. **Security scanning with bandit**
11. **Additional analysis with pylint**

## Continuous Integration

The pre-commit configuration includes CI settings for:
- Automatic fixes via pre-commit.ci
- Weekly dependency updates
- Pull request automation

## Troubleshooting

### Common Issues

1. **Black conflicts with flake8**: The configuration handles this automatically
2. **Import sorting conflicts**: isort is configured to be compatible with Black
3. **Type checking errors**: Use `# type: ignore` comments sparingly
4. **Security warnings**: Review bandit reports and address legitimate concerns

### Skipping Hooks

To skip pre-commit hooks for a specific commit:
```bash
git commit --no-verify -m "Your commit message"
```

### Updating Hooks

To update pre-commit hooks to latest versions:
```bash
pre-commit autoupdate
```

## Integration with IDEs

### VS Code
Install the Python extension and configure:
```json
{
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true
}
```

### PyCharm
Configure external tools:
- Black: `black $FilePath$`
- isort: `isort $FilePath$`
- flake8: `flake8 $FilePath$`

## Best Practices

1. **Run formatting before committing**: Use `python dev.py format`
2. **Fix linting issues**: Address all flake8 and mypy warnings
3. **Review security reports**: Check bandit output for vulnerabilities
4. **Keep dependencies updated**: Run `pre-commit autoupdate` regularly
5. **Use type hints**: Add comprehensive type annotations
6. **Write tests**: Ensure good test coverage
7. **Document complex code**: Add clear docstrings and comments

## Contributing

When contributing to the project:

1. Install development dependencies
2. Install pre-commit hooks
3. Format your code before committing
4. Ensure all tests pass
5. Address any linting warnings
6. Review security scan results

The automated tools will help maintain code quality and consistency across the project.
