"""
Meteogram plotting architecture.

This module provides the meteogram plotter that matches the provided diagram style,
with theme and configuration support.
"""

# Global registry
# Core interfaces and protocols
from .interfaces import (
    PlotConfig,
    PlotStyle,
    PlotterRegistry,
    SymbolType,
    WeatherPlotter,
    WeatherSymbolRenderer,
    plotting_registry,
)

# Meteogram implementation
from .plotters import MeteogramPlotter
from .symbols import UnifiedWeatherSymbols  # Official Met.no weather symbols

# Register meteogram plotter as the default and only plotter
plotting_registry.register_plotter("meteogram", MeteogramPlotter, is_default=True)

# Register symbol renderer
plotting_registry.register_symbol_renderer(
    "metno", UnifiedWeatherSymbols, is_default=True
)

__all__ = [
    # Core interfaces
    "WeatherPlotter",
    "PlotConfig",
    "PlotStyle",
    "SymbolType",
    # Meteogram implementation
    "MeteogramPlotter",
    "UnifiedWeatherSymbols",
    # Global registry
    "plotting_registry",
]
