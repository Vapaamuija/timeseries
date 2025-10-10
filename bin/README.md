# Development CLI Access

This directory contains scripts for running the weather-tool CLI during development without installing the package.

## Quick Start

### **1. Setup Development Environment**
```bash
# Run once to install dependencies and setup directories
./bin/setup-dev.sh
```

### **2. Use CLI During Development**
```bash
# Full command name
./bin/weather-tool --help
./bin/weather-tool plot ENGM --output test.png

# Short alias (recommended)
./bin/wt --help
./bin/wt plot ENGM --style tseries --output test.png

# Python script
python bin/dev-cli.py plot ENGM --style modern
```

## Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `weather-tool` | Full CLI access | `./bin/weather-tool <command>` |
| `wt` | Short alias | `./bin/wt <command>` |
| `dev-cli.py` | Python runner | `python bin/dev-cli.py <command>` |
| `setup-dev.sh` | Development setup | `./bin/setup-dev.sh` |

## Development Examples

### **Testing Plot Styles**
```bash
# Modern style
./bin/wt plot ENGM --style modern --output modern.png

# T-series meteogram
./bin/wt plot ENGM --style tseries --output tseries.png

# Comparison plot
./bin/wt plot-multiple ENGM,ENBR --style comparison --variable temperature --output comparison.png
```

### **Testing Data Sources**
```bash
# Unified Met.no client (recommended)
./bin/wt plot ENGM --data-source metno --output metno.png

# HTTP API only
./bin/wt plot ENGM --data-source http --output http.png

# THREDDS files only
./bin/wt plot ENGM --data-source file --output file.png
```

### **Testing Weather Symbols**
```bash
# ASCII symbols (no font warnings)
./bin/wt plot ENGM --symbols ascii --output ascii.png

# Unicode symbols
./bin/wt plot ENGM --symbols unicode --output unicode.png
```

### **Utility Commands**
```bash
# Search airports
./bin/wt search "oslo"
./bin/wt search "bergen"

# List Norwegian airports
./bin/wt list-airports --country NO --limit 10

# Test connections
./bin/wt test-connection --http --file

# Export configuration
./bin/wt export-config --output my_config.yaml
```

## Advantages

### ✅ **No Installation Required**
- Clone repository and run immediately
- No `pip install` needed for development
- Works in any Python environment

### ✅ **Fast Development Cycle**
- Edit code → Run `./bin/wt` → See results
- No reinstallation between changes
- Instant feedback

### ✅ **Multiple Access Methods**
- Choose the method that works best for your workflow
- All methods work identically
- Easy to switch between approaches

### ✅ **IDE Integration**
- Easy to configure in VS Code, PyCharm, etc.
- Can be used in build tasks and run configurations
- Supports debugging and profiling

## Troubleshooting

### **"ModuleNotFoundError"**
```bash
# Install dependencies first
pip install -r requirements.txt

# Or run setup script
./bin/setup-dev.sh
```

### **"Permission denied"**
```bash
# Make scripts executable
chmod +x bin/weather-tool
chmod +x bin/wt
chmod +x bin/dev-cli.py
chmod +x bin/setup-dev.sh
```

### **"Command not found"**
```bash
# Make sure you're in the project root
cd /Users/jaakkosuutarla/Development/personal/weather-tool

# Use relative path
./bin/wt --help
```

## Integration Examples

### **Makefile Integration**
```makefile
# Add to Makefile
test-cli:
	./bin/wt plot ENGM --output test.png

test-tseries:
	./bin/wt plot ENGM --style tseries --output tseries_test.png

clean:
	rm -f output/test*.png
```

### **Shell Aliases**
```bash
# Add to ~/.bashrc or ~/.zshrc
alias wt-dev='cd /Users/jaakkosuutarla/Development/personal/weather-tool && ./bin/wt'

# Usage from anywhere
wt-dev plot ENGM --output test.png
```

### **Docker Development**
```dockerfile
# In Dockerfile
COPY bin/ /app/bin/
COPY src/ /app/src/
WORKDIR /app

# Run CLI in container
RUN ./bin/wt --help
```

Happy developing! 🚀
