# Development Guide

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
