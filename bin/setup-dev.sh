#!/bin/bash
"""
Development setup script for weather-tool.

This script sets up the development environment without installing the package.
"""

echo "Setting up weather-tool development environment..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: Please run this script from the weather-tool project root"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p output
mkdir -p data/cache
mkdir -p logs

# Test CLI access
echo "Testing CLI access..."
if ./bin/wt --help > /dev/null 2>&1; then
    echo "✓ CLI access working!"
else
    echo "✗ CLI access failed"
    exit 1
fi

echo ""
echo "✅ Development environment ready!"
echo ""
echo "Usage:"
echo "  ./bin/wt --help                    # Show help"
echo "  ./bin/wt plot ENGM --output test.png  # Test plot"
echo "  ./bin/wt search oslo               # Search airports"
echo ""
echo "Short alias:"
echo "  ./bin/wt plot ENGM --style tseries # T-series meteogram"
echo ""
echo "Happy developing! 🌤️"
