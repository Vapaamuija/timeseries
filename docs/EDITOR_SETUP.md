# Editor Configuration Guide

This guide helps you configure your editor to follow the same formatting rules as the weather-tool project.

## Supported Editors

### ✅ VS Code (Recommended)

-   **Configuration**: `.vscode/` directory with complete settings
-   **Features**:
    -   Automatic formatting on save
    -   Integrated linting and type checking
    -   Pre-configured tasks and launch configurations
    -   Recommended extensions list

### ✅ PyCharm/IntelliJ IDEA

-   **Configuration**: `.idea/README.md` with detailed setup instructions
-   **Features**:
    -   External tools integration
    -   Code style configuration
    -   File watchers for automatic formatting
    -   Run configurations

### ✅ Vim/Neovim

-   **Configuration**: `.vimrc` with Python-specific settings
-   **Features**:
    -   Key mappings for formatting tools
    -   Python-specific indentation and line length
    -   Integration with Black, isort, flake8, mypy

### ✅ Sublime Text

-   **Configuration**: `.sublime-settings.json`
-   **Features**:
    -   Python formatting with Black
    -   Import sorting with isort
    -   Linting with flake8
    -   File exclusions

### ✅ EditorConfig Support

-   **Configuration**: `.editorconfig`
-   **Features**:
    -   Universal editor configuration
    -   File-type specific settings
    -   Consistent indentation and line endings

## Quick Setup Instructions

### VS Code

1. Install recommended extensions (prompted when opening project)
2. Configuration is automatically loaded from `.vscode/` directory
3. Use `Ctrl+Shift+P` → "Format Document" or `Ctrl+S` (auto-format on save)

### PyCharm

1. Follow instructions in `.idea/README.md`
2. Configure external tools for Black, isort, flake8, mypy
3. Set up file watchers for automatic formatting

### Vim/Neovim

1. Copy `.vimrc` contents to your vim configuration
2. Use `<leader>f` for Black formatting
3. Use `<leader>i` for import sorting
4. Use `<leader>l` for linting

### Sublime Text

1. Install Python packages: Black, isort, flake8
2. Copy `.sublime-settings.json` to your project settings
3. Use `Ctrl+Shift+P` → "Format Document"

## Common Features Across All Editors

### Code Formatting

-   **Line length**: 88 characters
-   **Indentation**: 4 spaces
-   **String quotes**: Double quotes preferred
-   **Trailing whitespace**: Automatically removed
-   **Final newline**: Automatically added

### Import Organization

-   **Tool**: isort with Black profile
-   **Order**: Standard library → Third-party → Local imports
-   **Format**: Multi-line with trailing commas

### Linting and Type Checking

-   **flake8**: Style and error checking
-   **mypy**: Static type checking
-   **bandit**: Security vulnerability scanning
-   **pylint**: Additional code analysis

### File Exclusions

All editors exclude these patterns:

-   `__pycache__/` directories
-   `*.pyc` files
-   `.pytest_cache/`
-   `.coverage`
-   `htmlcov/`
-   `bandit-report.json`
-   `*.egg-info/`
-   `build/` and `dist/`

## Editor-Specific Commands

### VS Code

-   **Format**: `Shift+Alt+F` or `Ctrl+S` (auto-save)
-   **Organize Imports**: `Shift+Alt+O`
-   **Run Tasks**: `Ctrl+Shift+P` → "Tasks: Run Task"

### PyCharm

-   **Format**: `Ctrl+Alt+L`
-   **Optimize Imports**: `Ctrl+Alt+O`
-   **External Tools**: Tools menu → External Tools

### Vim/Neovim

-   **Format**: `<leader>f`
-   **Sort Imports**: `<leader>i`
-   **Lint**: `<leader>l`
-   **Type Check**: `<leader>m`

### Sublime Text

-   **Format**: `Ctrl+Shift+P` → "Format Document"
-   **Sort Imports**: `Ctrl+Shift+P` → "Sort Imports"

## Troubleshooting

### Common Issues

1. **Formatting not working**:

    - Ensure Black is installed: `pip install black`
    - Check editor extension/plugin installation
    - Verify configuration file placement

2. **Import sorting conflicts**:

    - Ensure isort is installed: `pip install isort`
    - Check isort profile setting: `--profile=black`

3. **Linting errors**:

    - Ensure flake8 is installed: `pip install flake8`
    - Check flake8 configuration in `.flake8`

4. **Type checking issues**:
    - Ensure mypy is installed: `pip install mypy`
    - Check mypy configuration in `pyproject.toml`

### Editor-Specific Troubleshooting

#### VS Code

-   Check Python interpreter selection
-   Verify extension installation
-   Check workspace settings

#### PyCharm

-   Verify external tool configurations
-   Check Python interpreter settings
-   Ensure plugins are enabled

#### Vim/Neovim

-   Check if Python tools are in PATH
-   Verify key mappings
-   Test external command execution

#### Sublime Text

-   Verify package installation
-   Check Python interpreter setting
-   Test formatting commands

## Advanced Configuration

### Custom Key Bindings

Most editors allow custom key bindings for formatting commands. See editor-specific documentation for details.

### Project-Specific Settings

Some editors support project-specific settings that override global configurations. This is useful for maintaining consistency across team members.

### Integration with Pre-commit

All editors can be configured to work with the pre-commit hooks. The hooks will run automatically on commit, ensuring code quality regardless of editor configuration.

## Team Collaboration

### Shared Configuration

-   All configuration files are committed to the repository
-   Team members get consistent formatting automatically
-   No need for manual configuration sharing

### CI/CD Integration

-   Pre-commit hooks ensure consistent code quality
-   Automated formatting checks in CI pipeline
-   Consistent code style across all contributors

## Best Practices

1. **Use the provided configurations** as starting points
2. **Customize only when necessary** to maintain team consistency
3. **Test formatting** before committing code
4. **Keep tools updated** for latest features and bug fixes
5. **Document custom changes** for team members

## Support

For editor-specific issues:

-   Check editor documentation
-   Verify tool installation and configuration
-   Test with minimal examples
-   Consult project maintainers for project-specific issues
