"""
Norwegian meteogram plotting architecture.

This module provides the Norwegian meteogram plotter that matches the provided diagram style,
with theme and configuration support.
"""

# Core interfaces and protocols
from .interfaces import (
    WeatherPlotter,
    WeatherSymbolRenderer, 
    PlotterRegistry,
    PlotConfig,
    PlotStyle,
    SymbolType
)

# Norwegian meteogram implementation
from .plotters import MeteogramPlotter

from .symbols import UnifiedWeatherSymbols  # Official Met.no weather symbols

# Global registry
from .interfaces import plotting_registry

# Register Norwegian meteogram plotter as the default and only plotter
plotting_registry.register_plotter("norwegian_meteogram", MeteogramPlotter, is_default=True)

# Register symbol renderer
plotting_registry.register_symbol_renderer("metno", UnifiedWeatherSymbols, is_default=True)

__all__ = [
    # Core interfaces
    "WeatherPlotter",
    "PlotConfig", "PlotStyle", "SymbolType",
    
    # Norwegian meteogram implementation
    "MeteogramPlotter", "UnifiedWeatherSymbols",
    
    # Global registry
    "plotting_registry",
]