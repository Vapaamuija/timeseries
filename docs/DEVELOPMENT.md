# Development Guide

## Development Environment Setup

This guide will help you set up a complete development environment for the weather-tool project using pyenv and virtual environments.

### Prerequisites

- **Git** - For version control
- **Internet connection** - For downloading dependencies and weather data
- **Basic command line knowledge** - Terminal/command prompt usage

### Step 1: Install pyenv (Python Version Manager)

#### macOS

```bash
# Install using Homebrew (recommended)
brew install pyenv

# Add to your shell profile (~/.zshrc or ~/.bash_profile)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

# Reload your shell
source ~/.zshrc
```

#### Ubuntu/Debian

```bash
# Install dependencies
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git

# Install pyenv
curl https://pyenv.run | bash

# Add to your shell profile (~/.bashrc)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Reload your shell
source ~/.bashrc
```

### Step 2: Install direnv (Automatic Environment Management)

[direnv](https://direnv.net/) automatically loads and unloads environment variables when you enter or leave a directory. This eliminates the need to manually activate virtual environments.

#### macOS

```bash
# Install using Homebrew (recommended)
brew install direnv

# Add to your shell profile (~/.zshrc or ~/.bash_profile)
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc

# Reload your shell
source ~/.zshrc
```

#### Ubuntu/Debian

```bash
# Install direnv
sudo apt install direnv

# Add to your shell profile (~/.bashrc)
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc

# Reload your shell
source ~/.bashrc
```

#### Verify direnv Installation

```bash
# Check if direnv is working
direnv version

# Test basic functionality
mkdir /tmp/direnv-test
cd /tmp/direnv-test
echo 'export TEST_VAR=hello' > .envrc
direnv allow .
echo $TEST_VAR  # Should show "hello"
cd ..
echo $TEST_VAR  # Should be empty
rm -rf /tmp/direnv-test
```

### Step 3: Install Python 3.11

```bash
# Install Python 3.11 (recommended version)
pyenv install 3.11.7

# Set as global default (optional)
pyenv global 3.11.7

# Verify installation
python --version  # Should show Python 3.11.7
```

### Step 4: Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd weather-tool

# Verify you're in the right directory
ls -la  # Should show README.md, src/, docs/, etc.
```

### Step 5: Create Virtual Environment

```bash
# Create a virtual environment using the pyenv Python
python -m venv venv

# Verify the virtual environment was created
ls -la venv/  # Should show bin/, lib/, etc.

# Manually activate the virtual environment for initial setup
source venv/bin/activate

# Verify you're in the virtual environment
which python  # Should show path to venv/bin/python
python --version  # Should show Python 3.11.7
```

### Step 6: Create .envrc File for Automatic Environment Activation

Create a `.envrc` file in the project root to automatically activate the virtual environment:

```bash
# Create .envrc file
cat > .envrc << 'EOF'
# Automatically activate virtual environment
source venv/bin/activate

# Add project root to Python path
PATH_add src

# Set development environment variables
export WEATHER_TOOL_DEV=true
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

# Optional: Set default output directory
export WEATHER_TOOL_OUTPUT_DIR="${PWD}/output"
EOF

# Allow direnv to use this .envrc file
direnv allow .

# Test that it works - you should see direnv messages
cd .. && cd weather-tool
```

### Step 7: Install Dependencies

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Install development dependencies (optional but recommended)
pip install -e ".[dev]"
```

### Step 8: Install High-Quality Weather Symbols (Optional but Recommended)

#### macOS

```bash
# Install Cairo library
brew install cairo

# Install Python packages for SVG rendering
pip install cairosvg pillow
```

#### Ubuntu/Debian

```bash
# Install Cairo development libraries
sudo apt-get install libcairo2-dev pkg-config python3-dev

# Install Python packages for SVG rendering
pip install cairosvg pillow
```

### Step 9: Verify Installation

```bash
# Test basic functionality
python dev.py --help

# Test weather tool CLI
./bin/wt --help

# Test connection to weather data
./bin/wt test-connection

# Create a test plot
./bin/wt plot ENGM --output test_installation.png

# Check if the plot was created
ls -la test_installation.png
```

### Step 10: Set Up Development Tools (Optional)

```bash
# Install pre-commit hooks for code quality
pre-commit install

# Run formatting and linting
python dev.py format
python dev.py lint

# Run tests
python dev.py test
```

## Virtual Environment Management with direnv

### Daily Workflow (Automatic with direnv)

With direnv set up, your virtual environment is automatically managed:

```bash
# Simply navigate to the project directory
cd weather-tool

# direnv automatically:
# - Activates the virtual environment
# - Sets up environment variables
# - Adds project paths to PYTHONPATH
# You should see: direnv: loading .envrc

# Your prompt should now show (venv) at the beginning
# (venv) user@computer:~/weather-tool$

# Work on your code...
# When you leave the directory, direnv automatically:
# - Deactivates the virtual environment
# - Cleans up environment variables
cd ..
# You should see: direnv: unloading
```

### Manual Environment Commands (if needed)

```bash
# Manually activate virtual environment (if direnv is not working)
source venv/bin/activate

# Manually deactivate virtual environment
deactivate

# Check which Python you're using
which python

# Check installed packages
pip list

# Update a specific package
pip install --upgrade package_name

# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

### direnv Commands

```bash
# Allow direnv to use .envrc file (first time setup)
direnv allow .

# Deny direnv from using .envrc file
direnv deny .

# Check direnv status
direnv status

# Reload environment manually
direnv reload

# Edit .envrc file
direnv edit .
```

### Troubleshooting Environment Issues

#### Common Issues and Solutions

1. **"python: command not found"**
   ```bash
   # Make sure pyenv is properly installed
   pyenv versions
   
   # Reinstall Python if needed
   pyenv install 3.11.7
   pyenv global 3.11.7
   ```

2. **direnv not working**
   ```bash
   # Check if direnv is installed and hooked into shell
   direnv version
   
   # Check if .envrc file exists and is allowed
   ls -la .envrc
   direnv status
   
   # If not allowed, allow it
   direnv allow .
   
   # Test by leaving and re-entering directory
   cd .. && cd weather-tool
   ```

2a. **"venv/bin/activate: No such file or directory"**
   ```bash
   # This means the virtual environment doesn't exist yet
   # Create it first:
   python -m venv venv
   
   # Then allow direnv again
   direnv allow .
   
   # Test by leaving and re-entering directory
   cd .. && cd weather-tool
   ```

3. **Virtual environment not activating**
   ```bash
   # Check if .envrc file is correct
   cat .envrc
   
   # Recreate virtual environment
   rm -rf venv
   python -m venv venv
   
   # Reload direnv
   direnv reload
   ```

4. **Package installation fails**
   ```bash
   # Update pip and try again
   pip install --upgrade pip
   pip install -r requirements.txt
   
   # On Ubuntu, you might need additional system packages
   sudo apt-get install python3-dev build-essential
   ```

5. **Permission errors on macOS**
   ```bash
   # Use --user flag if needed
   pip install --user -r requirements.txt
   ```

6. **direnv hook not working**
   ```bash
   # Check if hook is in shell profile
   grep direnv ~/.zshrc  # or ~/.bashrc
   
   # Re-add hook if missing
   echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc  # or bash
   source ~/.zshrc  # or ~/.bashrc
   ```

## IDE Integration

### VS Code / Cursor

1. **Open the project folder** in VS Code/Cursor
2. **Select Python interpreter**:
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
   - Type "Python: Select Interpreter"
   - Choose the interpreter from your virtual environment: `./venv/bin/python`

3. **Install recommended extensions** (prompted when opening project)

### PyCharm

1. **Open the project** in PyCharm
2. **Configure Python interpreter**:
   - Go to File → Settings → Project → Python Interpreter
   - Click the gear icon → Add
   - Choose "Existing environment"
   - Select `./venv/bin/python`

## Running CLI During Development

You can run the weather-tool CLI during development without installing the package using several methods:

### **Method 1: Using bin/ Scripts (Recommended)**

#### **Full command name:**
```bash
./bin/weather-tool --help
./bin/weather-tool plot ENGM --style tseries --output test.png
./bin/weather-tool search "oslo"
```

#### **Short alias:**
```bash
./bin/wt --help
./bin/wt plot ENGM --style modern --output test.png
./bin/wt list-airports --country NO
```

#### **Python script:**
```bash
python bin/dev-cli.py --help
python bin/dev-cli.py plot ENGM --style tseries
```

### **Method 2: Direct Python Module**

```bash
# Run CLI module directly
python -m src.weather_tool.cli --help
python -m src.weather_tool.cli plot ENGM --style tseries

# Or with PYTHONPATH
PYTHONPATH=src python -m weather_tool.cli plot ENGM --style modern
```

### **Method 3: Python Script**

```bash
# Direct execution
python src/weather_tool/cli.py --help
python src/weather_tool/cli.py plot ENGM --output test.png
```

### **Method 4: Development Installation (Editable)**

```bash
# Install in development mode (changes reflect immediately)
pip install -e .

# Then use normally
weather-tool --help
weather-tool plot ENGM --style tseries
```

## Development Workflow

### **Quick Testing**
```bash
# Test CLI help
./bin/wt --help

# Test basic plotting
./bin/wt plot ENGM --output test.png

# Test different styles
./bin/wt plot ENGM --style modern --output modern_test.png
./bin/wt plot ENGM --style tseries --output tseries_test.png

# Test data sources
./bin/wt plot ENGM --data-source http --output http_test.png
./bin/wt plot ENGM --data-source file --output file_test.png
```

### **Development Commands**
```bash
# Test connections
./bin/wt test-connection

# Search functionality
./bin/wt search "oslo"
./bin/wt search "ENGM"

# List airports
./bin/wt list-airports --country NO --limit 5

# Export configuration
./bin/wt export-config --output dev_config.yaml
```

### **Debugging**
```bash
# Enable debug logging
./bin/wt --log-level DEBUG plot ENGM --output debug_test.png

# Test specific data source
./bin/wt plot ENGM --data-source metno --log-level INFO

# Verbose output
./bin/wt -v plot ENGM --style tseries
```

## Adding New CLI Commands

### **Step 1: Add Command to CLI**
```python
# In src/weather_tool/cli.py

@main.command()
@click.argument('icao_code')
@click.option('--style', default='modern', help='Plot style')
@click.pass_obj
def my_command(config, icao_code, style):
    """My custom CLI command."""
    # Implementation here
    pass
```

### **Step 2: Test During Development**
```bash
./bin/wt my-command ENGM --style tseries
```

### **Step 3: Add to Help Documentation**
```bash
./bin/wt --help  # Should show your new command
```

## Project Structure for Development

```
weather-tool/
├── bin/                       # Development CLI access
│   ├── weather-tool           # Full CLI script
│   ├── wt                     # Short alias
│   └── dev-cli.py             # Python development runner
├── src/weather_tool/          # Source code
│   ├── cli.py                 # CLI implementation
│   ├── core/                  # Core functionality
│   ├── data/                  # Clean data architecture
│   └── plotting/              # Clean plotting architecture
├── config/                    # Configuration files
├── output/                    # Generated plots (development)
└── tests/                     # Test suite
```

## Development Best Practices

### **Testing Changes**
```bash
# Test basic functionality
./bin/wt plot ENGM --output test.png

# Test different plot styles
./bin/wt plot ENGM --style modern --output modern.png
./bin/wt plot ENGM --style tseries --output tseries.png

# Test data sources
./bin/wt plot ENGM --data-source http --output http.png
./bin/wt plot ENGM --data-source file --output file.png
```

### **Code Changes**
1. **Edit source code** in `src/weather_tool/`
2. **Test immediately** with `./bin/wt` (no reinstallation needed)
3. **Check output** in `output/` directory
4. **Iterate quickly** with instant feedback

### **Configuration Testing**
```bash
# Test with custom config
./bin/wt --config config/settings.yaml plot ENGM

# Test configuration export
./bin/wt export-config --output test_config.yaml

# Test with different log levels
./bin/wt --log-level DEBUG plot ENGM
```

## Advantages of bin/ Scripts

### ✅ **No Installation Required**
- Run CLI immediately after cloning repository
- No need for `pip install -e .`
- Works in any Python environment

### ✅ **Fast Development Cycle**
- Edit code → Run `./bin/wt` → See results
- No reinstallation between changes
- Instant feedback loop

### ✅ **Multiple Access Methods**
- `./bin/weather-tool` - full name
- `./bin/wt` - short alias  
- `python bin/dev-cli.py` - explicit Python

### ✅ **Environment Independence**
- Works with any Python interpreter
- No package installation conflicts
- Clean development environment

## Common Development Tasks

### **Testing New Features**
```bash
# Test new plot style
./bin/wt plot ENGM --style my_new_style --output test.png

# Test new data source
./bin/wt plot ENGM --data-source my_source --output test.png

# Test new weather symbols
./bin/wt plot ENGM --symbols my_symbols --output test.png
```

### **Debugging Issues**
```bash
# Enable verbose logging
./bin/wt --log-level DEBUG plot ENGM 2>&1 | tee debug.log

# Test specific components
./bin/wt test-connection --http --file
./bin/wt search "test" --limit 1
```

### **Performance Testing**
```bash
# Time command execution
time ./bin/wt plot ENGM --output perf_test.png

# Test batch processing
time ./bin/wt plot-multiple ENGM,ENBR,ENVA --output-dir batch_test/
```

## Integration with IDEs

### **VS Code / Cursor**
Add to `.vscode/tasks.json`:
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Weather Tool - Plot ENGM",
            "type": "shell",
            "command": "./bin/wt",
            "args": ["plot", "ENGM", "--output", "ide_test.png"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always"
            }
        }
    ]
}
```

### **PyCharm**
Create run configuration:
- **Script path**: `bin/weather-tool`
- **Parameters**: `plot ENGM --output pycharm_test.png`
- **Working directory**: `/Users/jaakkosuutarla/Development/personal/weather-tool`

## Summary

**Development CLI Access Methods:**

1. **`./bin/weather-tool`** - Full command name
2. **`./bin/wt`** - Short alias (recommended for development)
3. **`python bin/dev-cli.py`** - Explicit Python execution
4. **`python -m src.weather_tool.cli`** - Direct module execution
5. **`pip install -e .`** - Editable installation (optional)

**Recommended for development:** Use `./bin/wt` for quick testing and iteration!
