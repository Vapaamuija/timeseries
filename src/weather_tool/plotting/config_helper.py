"""
Configuration helper for optimal weather plotting setup.

This module provides utilities to automatically configure the best
plotting settings based on the user's system capabilities.
"""

import logging
from typing import Optional

from .interfaces import PlotConfig, SymbolType
from .symbols import UnifiedWeatherSymbols

logger = logging.getLogger(__name__)


def create_optimal_config(
    symbol_size: int = 20,
    figure_size: tuple = (12, 8),
    prefer_unicode: bool = True,  # Kept for backward compatibility but ignored
) -> PlotConfig:
    """Create an optimal PlotConfig for the current system.

    Args:
        symbol_size: Size of weather symbols
        figure_size: Figure size tuple
        prefer_unicode: Ignored - kept for backward compatibility

    Returns:
        Optimized PlotConfig instance with SVG symbols
    """
    # Always use SVG symbols - this is the only supported type
    logger.info("Using SVG symbols from Met.no repository")

    return PlotConfig(
        symbol_type=SymbolType.SVG,
        symbol_size=symbol_size,
        figure_size=figure_size,
        auto_download_icons=True,
    )


def get_recommended_symbol_type() -> SymbolType:
    """Get the recommended symbol type for the current system.

    Returns:
        Always returns SVG as it's the only supported type
    """
    # Always return SVG - it's the only supported type
    return SymbolType.SVG


def show_system_capabilities() -> None:
    """Show system capabilities for weather symbol rendering."""
    print("🔍 System Capabilities for Weather Symbols")
    print("=" * 45)

    # Test SVG support
    svg_config = PlotConfig(symbol_type=SymbolType.SVG)
    svg_renderer = UnifiedWeatherSymbols(svg_config)

    print("🎨 SVG icons: Always used (only supported type)")
    print(f"📁 SVG icon directory: {svg_renderer.icon_cache_dir}")
    print(f"🎯 Symbol type: {get_recommended_symbol_type().value}")

    # Check SVG rendering quality
    has_high_quality = svg_renderer.has_high_quality_svg_support()
    if has_high_quality:
        print("✅ High-quality SVG rendering: Available")
        print("🎨 Using true SVG icons with transparent backgrounds")
    else:
        print("⚠️  High-quality SVG rendering: Not available")
        print("🎨 Using fallback transparent markers (still looks great!)")
        print("\n💡 To enable high-quality SVG rendering:")
        print(svg_renderer.get_svg_installation_instructions())

    print("\n✅ Using official Met.no weather symbols for accuracy")

    # Show examples of weather conditions
    print("\n📊 Weather Symbol Examples:")
    weather_examples = [
        ("clearsky_day", "Clear sky (day)"),
        ("partlycloudy_day", "Partly cloudy (day)"),
        ("rain", "Rain"),
        ("snow", "Snow"),
        ("fog", "Fog"),
    ]

    print("Met.no weather symbols:")
    for symbol_code, desc in weather_examples:
        symbol_info = svg_renderer.get_symbol_info(symbol_code)
        if symbol_info:
            print(f"  {symbol_code}.svg → {symbol_info['description']} - {desc}")
        else:
            print(f"  {symbol_code}.svg → Unknown - {desc}")


def create_config_for_compatibility() -> PlotConfig:
    """Create a configuration optimized for maximum compatibility.

    Returns:
        PlotConfig with SVG symbols (only supported type)
    """
    return PlotConfig(
        symbol_type=SymbolType.SVG,
        symbol_size=18,
        figure_size=(12, 8),
        auto_download_icons=True,
    )


def create_config_for_quality() -> PlotConfig:
    """Create a configuration optimized for visual quality.

    Returns:
        PlotConfig with SVG symbols for best quality
    """
    return PlotConfig(
        symbol_type=SymbolType.SVG,
        symbol_size=22,
        figure_size=(14, 8),
        auto_download_icons=True,
    )
