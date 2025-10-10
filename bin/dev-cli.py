#!/usr/bin/env python3
"""
Development CLI runner for weather-tool.

Alternative way to run CLI during development using Python directly.
Usage: python bin/dev-cli.py <command> [options]
"""

import sys
from pathlib import Path

# Add src to Python path for development
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import and run CLI
from weather_tool.cli import main

if __name__ == "__main__":
    print("Weather Tool - Development CLI")
    print("=" * 40)
    main()
