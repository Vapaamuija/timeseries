"""Weather Tool - Airport Time Series Plotting Package.

A comprehensive Python tool for plotting weather time series data for airports,
supporting both API-based and direct file access methods.
"""

__version__ = "0.1.0"
__author__ = "Weather Tool Team"
__email__ = "your.email@example.com"

from .core.config import Config
from .core.weather_plotter import WeatherPlotter
from .data.interfaces import DataClientRegistry
from .airports.manager import AirportManager

# Plotting components (direct imports)
from .plotting.plotters import MeteogramPlotter
from .plotting.interfaces import PlotConfig

__all__ = [
    "Config",
    "WeatherPlotter",
    "DataClientRegistry",
    "AirportManager",
    "MeteogramPlotter",
    "PlotConfig",
]
