#!/usr/bin/env python3
"""
Download all Met.no weather icons from the official repository.

This script downloads all weather icons from:
https://github.com/metno/weathericons

The icons are cached locally in data/metno_weather_icons/ for use in plots.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from weather_tool.plotting.interfaces import PlotConfig, SymbolType
from weather_tool.plotting.symbols import UnifiedWeatherSymbols


def main():
    """Download all Met.no weather icons."""
    print("🌤️  Met.no Weather Icons Downloader")
    print("=" * 50)
    print()

    # Initialize symbol renderer
    config = PlotConfig(symbol_type=SymbolType.SVG)
    symbol_renderer = UnifiedWeatherSymbols(config)

    print(f"📁 Icons will be cached in: {symbol_renderer.icon_cache_dir}")
    print(f"🌐 Source repository: https://github.com/metno/weathericons")
    print()

    # Show available symbols
    supported_symbols = symbol_renderer.get_supported_symbols()
    print(f"📊 Total symbols available: {len(supported_symbols)}")
    print()

    # Download all icons
    print("⬇️  Downloading icons...")
    results = symbol_renderer.download_all_icons()

    # Show results
    successful = sum(results.values())
    total = len(results)
    failed = total - successful

    print()
    print("📈 Download Results:")
    print(f"  ✅ Successful: {successful}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📊 Total: {total}")

    if failed > 0:
        print()
        print("❌ Failed downloads:")
        for icon_name, success in results.items():
            if not success:
                print(f"  - {icon_name}")

    print()
    print("🎨 Icon Usage Examples:")
    print("  - ASCII symbols: config.symbol_type = SymbolType.ASCII")
    print("  - Unicode symbols: config.symbol_type = SymbolType.UNICODE")
    print("  - SVG icons: config.symbol_type = SymbolType.SVG")

    # Show some example symbols
    print()
    print("🌟 Example Weather Symbols:")
    example_codes = ["clearsky_day", "partlycloudy_day", "rain", "snow", "fog"]

    for code in example_codes:
        symbol_info = symbol_renderer.get_symbol_info(code)
        if symbol_info:
            icon_path = symbol_renderer.get_icon_path(code)
            status = "✅" if icon_path and icon_path.exists() else "❌"
            print(f"  {status} {code}: {symbol_info['description']}")
            print(
                f"     ASCII: {symbol_info['ascii']} | Unicode: {symbol_info['unicode']}"
            )
            if icon_path:
                print(f"     SVG: {icon_path}")
            print()

    if successful == total:
        print("🎉 All icons downloaded successfully!")
        return 0
    else:
        print("⚠️  Some icons failed to download. Check your internet connection.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
