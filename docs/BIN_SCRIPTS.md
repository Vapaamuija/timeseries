# Development Scripts Guide

This guide explains how to use the development scripts in the `bin/` directory for running the weather-tool CLI and development utilities during development without installing the package.

## Quick Start

### **1. Setup Development Environment**
```bash
# Run once to install dependencies and setup directories
./bin/setup-dev.sh
```

### **2. Use CLI During Development**
```bash
# Main weather tool CLI
./bin/weather-tool --help
./bin/weather-tool plot ENGM --output test.png
./bin/weather-tool plot ENGM --style tseries --output test.png
```

### **3. Development Utilities**
```bash
# Code formatting and quality
./bin/dev format                              # Format code
./bin/dev lint                                # Check code quality
./bin/dev test                                # Run tests
./bin/dev --help                              # Show all dev commands
```

### **4. SVG Rendering Setup**
```bash
# Setup high-quality SVG weather symbols
./bin/setup_svg_rendering.sh                 # Configure Cairo + SVG rendering
```

## Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `weather-tool` | Main CLI access | `./bin/weather-tool <command>` |
| `dev` | Development utilities | `./bin/dev <command>` |
| `setup-dev.sh` | Development setup | `./bin/setup-dev.sh` |
| `setup_svg_rendering.sh` | SVG rendering setup | `./bin/setup_svg_rendering.sh` |

## Development Examples

### **Testing Plot Styles**
```bash
# Modern style
./bin/weather-tool plot ENGM --style modern --output modern.png

# T-series meteogram
./bin/weather-tool plot ENGM --style tseries --output tseries.png

# Comparison plot
./bin/weather-tool plot-multiple ENGM,ENBR --style comparison --variable temperature --output comparison.png
```

### **Testing Data Sources**
```bash
# Unified Met.no client (recommended)
./bin/weather-tool plot ENGM --data-source metno --output metno.png

# HTTP API only
./bin/weather-tool plot ENGM --data-source http --output http.png

# THREDDS files only
./bin/weather-tool plot ENGM --data-source file --output file.png
```

### **Testing Weather Symbols**
```bash
# ASCII symbols (no font warnings)
./bin/weather-tool plot ENGM --symbols ascii --output ascii.png

# Unicode symbols
./bin/weather-tool plot ENGM --symbols unicode --output unicode.png
```

### **Utility Commands**
```bash
# Search airports
./bin/weather-tool search "oslo"
./bin/weather-tool search "bergen"

# List Norwegian airports
./bin/weather-tool list-airports --country NO --limit 10

# Test connections
./bin/weather-tool test-connection --http --file

# Export configuration
./bin/weather-tool export-config --output my_config.yaml
```

## Advantages

### ✅ **No Installation Required**
- Clone repository and run immediately
- No `pip install` needed for development
- Works in any Python environment

### ✅ **Fast Development Cycle**
- Edit code → Run `./bin/weather-tool` → See results
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
chmod +x bin/dev
chmod +x bin/setup-dev.sh
```

### **"Command not found"**
```bash
# Make sure you're in the project root
cd /Users/jaakkosuutarla/Development/personal/weather-tool

# Use relative path
./bin/weather-tool --help
```

## Integration Examples

### **Development Script Integration**
```bash
# Add to your development workflow
test-cli:
	./bin/weather-tool plot ENGM --output test.png

test-tseries:
	./bin/weather-tool plot ENGM --style tseries --output tseries_test.png

clean:
	./bin/dev clean
```

### **Shell Aliases**
```bash
# Add to ~/.bashrc or ~/.zshrc
alias wt-dev='cd /Users/jaakkosuutarla/Development/personal/weather-tool && ./bin/weather-tool'

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
RUN ./bin/weather-tool --help
```

Happy developing! 🚀
