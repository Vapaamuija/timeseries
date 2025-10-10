"""
Clean data fetching and processing architecture.

This module provides a unified interface for weather data access with:
- HTTP API client for real-time data
- File server client for archive data  
- Unified Met.no client combining both
- Clean interfaces for adding new sources
"""

# Core interfaces and protocols
from .interfaces import (
    WeatherDataClient, 
    HTTPWeatherClient, 
    FileWeatherClient,
    DataSourceInfo, 
    DataClientRegistry, 
    WeatherDataProcessor,
    DataSourceType,
    DataQuality
)

# Met.no client implementations
from .metno_unified import (
    MetNoUnifiedClient,    # Primary client - combines HTTP + File
    MetNoHTTPClient,       # HTTP API access only
    MetNoFileClient        # THREDDS file access only
)

__all__ = [
    # Core interfaces
    "WeatherDataClient", "HTTPWeatherClient", "FileWeatherClient",
    "DataSourceInfo", "DataClientRegistry", "WeatherDataProcessor",
    "DataSourceType", "DataQuality",
    
    # Met.no clients
    "MetNoUnifiedClient", "MetNoHTTPClient", "MetNoFileClient",
]
