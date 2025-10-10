#!/usr/bin/env python3
"""
Simple development CLI runner.

Usage: python dev.py <command> [options]
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import and run CLI
from weather_tool.cli import main

if __name__ == "__main__":
    main()
