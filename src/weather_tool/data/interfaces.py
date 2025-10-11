"""
Data client interfaces and protocols.

This module defines the interfaces that all weather data clients must implement,
making it easy to add new data sources while maintaining consistency.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import requests


class DataSourceType(Enum):
    """Types of data sources."""

    HTTP_API = "http_api"
    FILE_SERVER = "file_server"
    LOCAL_FILE = "local_file"
    DATABASE = "database"


class DataQuality(Enum):
    """Data quality indicators."""

    REAL_TIME = "real_time"  # Live/current data
    FORECAST = "forecast"  # Forecast data
    HISTORICAL = "historical"  # Historical/archive data
    SYNTHETIC = "synthetic"  # Generated/test data


@dataclass
class WeatherDataPoint:
    """Standardized weather data point."""

    timestamp: datetime
    temperature: Optional[float] = None  # °C
    pressure: Optional[float] = None  # hPa
    humidity: Optional[float] = None  # %
    wind_speed: Optional[float] = None  # m/s
    wind_direction: Optional[float] = None  # degrees
    precipitation: Optional[float] = None  # mm
    cloud_cover: Optional[float] = None  # fraction (0-1)
    weather_symbol: Optional[str] = None  # Met.no symbol code

    # Additional variables
    visibility: Optional[float] = None  # km
    dew_point: Optional[float] = None  # °C
    uv_index: Optional[float] = None  # index

    # Cloud layers
    cloud_high: Optional[float] = None  # fraction (0-1)
    cloud_medium: Optional[float] = None  # fraction (0-1)
    cloud_low: Optional[float] = None  # fraction (0-1)
    fog: Optional[float] = None  # fraction (0-1)

    # Quality metadata
    data_quality: DataQuality = DataQuality.REAL_TIME
    source: Optional[str] = None
    model: Optional[str] = None


@dataclass
class DataSourceInfo:
    """Information about a data source."""

    name: str
    source_type: DataSourceType
    base_url: Optional[str] = None
    requires_auth: bool = False
    rate_limited: bool = False
    available_variables: Optional[List[str]] = None
    time_resolution: Optional[str] = None  # e.g., "1H", "15min"
    spatial_resolution: Optional[str] = None  # e.g., "2.5km", "1km"
    update_frequency: Optional[str] = None  # e.g., "6H", "1H"
    max_forecast_hours: Optional[int] = None
    description: Optional[str] = None


class WeatherDataClient(ABC):
    """Abstract base class for all weather data clients."""

    def __init__(self, config: Any):
        """Initialize the client.

        Args:
            config: Configuration object
        """
        self.config = config

    @abstractmethod
    def get_weather_data(
        self,
        latitude: float,
        longitude: float,
        start_time: datetime,
        end_time: datetime,
        variables: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Fetch weather data for given coordinates and time range.

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            start_time: Start time for data retrieval
            end_time: End time for data retrieval
            variables: List of weather variables to fetch

        Returns:
            DataFrame with standardized weather data
        """
        raise NotImplementedError

    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the data source is available.

        Returns:
            True if connection is successful, False otherwise
        """
        raise NotImplementedError

    @abstractmethod
    def get_source_info(self) -> DataSourceInfo:
        """Get information about this data source.

        Returns:
            DataSourceInfo object
        """
        raise NotImplementedError

    def get_available_variables(self) -> List[str]:
        """Get list of available weather variables.

        Returns:
            List of standardized variable names
        """
        return [
            "temperature",
            "pressure",
            "humidity",
            "wind_speed",
            "wind_direction",
            "precipitation",
            "cloud_cover",
            "weather_symbol",
            "visibility",
            "dew_point",
            "uv_index",
            "cloud_high",
            "cloud_medium",
            "cloud_low",
            "fog",
        ]

    def validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """Validate coordinate values.

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees

        Returns:
            True if coordinates are valid
        """
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)

    def validate_time_range(self, start_time: datetime, end_time: datetime) -> bool:
        """Validate time range.

        Args:
            start_time: Start time
            end_time: End time

        Returns:
            True if time range is valid
        """
        return start_time < end_time


class HTTPWeatherClient(WeatherDataClient):
    """Base class for HTTP-based weather data clients."""

    def __init__(self, config: Any):
        """Initialize HTTP client."""
        super().__init__(config)
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self) -> None:
        """Set up HTTP session with headers and timeouts."""
        self.session.headers.update(
            {
                "User-Agent": getattr(self.config, "user_agent", "weather-tool/1.0"),
                "Accept": "application/json",
            }
        )
        self.timeout = getattr(self.config, "timeout", 30)

    def __del__(self) -> None:
        """Clean up session."""
        if hasattr(self, "session"):
            self.session.close()


class FileWeatherClient(WeatherDataClient):
    """Base class for file-based weather data clients."""

    def __init__(self, config: Any):
        """Initialize file client."""
        super().__init__(config)
        self._file_cache: Dict[str, Any] = {}

    def clear_cache(self) -> None:
        """Clear file cache."""
        for ds in self._file_cache.values():
            if hasattr(ds, "close"):
                ds.close()
        self._file_cache.clear()

    def __del__(self) -> None:
        """Clean up cache."""
        if hasattr(self, "_file_cache"):
            self.clear_cache()


class WeatherDataProcessor:
    """Standardized weather data processor."""

    @staticmethod
    def standardize_dataframe(
        df: pd.DataFrame, source_info: DataSourceInfo
    ) -> pd.DataFrame:
        """Convert any weather DataFrame to standardized format.

        Args:
            df: Input DataFrame with weather data
            source_info: Information about the data source

        Returns:
            DataFrame with standardized column names and units
        """
        # Create standardized DataFrame
        standardized = pd.DataFrame(index=df.index)

        # Variable name mappings for different sources
        variable_mappings = {
            # Temperature
            "temperature": [
                "air_temperature_2m",
                "temperature_2m",
                "temp",
                "t2m",
                "temperature",
            ],
            "pressure": [
                "air_pressure_at_sea_level",
                "surface_air_pressure",
                "msl",
                "slp",
                "pressure",
            ],
            "humidity": [
                "relative_humidity_2m",
                "relative_humidity",
                "rh2m",
                "humidity",
            ],
            "wind_speed": ["wind_speed_10m", "wind_speed", "ws10m"],
            "wind_direction": ["wind_from_direction_10m", "wind_direction", "wd10m"],
            "precipitation": ["precipitation_amount", "precip", "tp", "precipitation"],
            "cloud_cover": ["cloud_area_fraction", "cloudiness", "cc", "cloud_cover"],
            "weather_symbol": ["symbol_code", "weather_symbol", "weather_code"],
            "visibility": ["visibility", "vis"],
            "dew_point": ["dew_point_temperature_2m", "dew_point", "td2m"],
            "uv_index": ["ultraviolet_index", "uv_index", "uvi"],
            "cloud_high": ["high_type_cloud_area_fraction", "cloud_high"],
            "cloud_medium": ["medium_type_cloud_area_fraction", "cloud_medium"],
            "cloud_low": ["low_type_cloud_area_fraction", "cloud_low"],
            "fog": ["fog_area_fraction", "fog"],
        }

        # Map variables
        for std_name, possible_names in variable_mappings.items():
            for name in possible_names:
                if name in df.columns:
                    standardized[std_name] = df[name]
                    break

        # Convert units to standard
        standardized = WeatherDataProcessor._convert_units(standardized)

        # Add derived variables
        standardized = WeatherDataProcessor._add_derived_variables(standardized)

        return standardized

    @staticmethod
    def _convert_units(df: pd.DataFrame) -> pd.DataFrame:
        """Convert units to standard format."""
        df_converted = df.copy()

        # Temperature: Kelvin to Celsius
        if "temperature" in df_converted.columns:
            temp_col = df_converted["temperature"]
            if temp_col.min() > 200:  # Likely in Kelvin
                df_converted["temperature"] = temp_col - 273.15

        # Pressure: Pa to hPa
        if "pressure" in df_converted.columns:
            pressure_col = df_converted["pressure"]
            if pressure_col.min() > 50000:  # Likely in Pa
                df_converted["pressure"] = pressure_col / 100

        # Ensure precipitation is non-negative
        if "precipitation" in df_converted.columns:
            df_converted["precipitation"] = df_converted["precipitation"].clip(lower=0)

        # Convert cloud coverage from percentage to fraction (0-1) if needed
        cloud_vars = ["cloud_cover", "cloud_high", "cloud_medium", "cloud_low", "fog"]
        for var in cloud_vars:
            if var in df_converted.columns:
                cloud_col = df_converted[var]
                # If values are > 1, assume they're percentages and convert to fractions
                if cloud_col.max() > 1:
                    df_converted[var] = cloud_col / 100.0
                # Ensure cloud fractions are between 0 and 1
                df_converted[var] = df_converted[var].clip(0, 1)

        return df_converted

    @staticmethod
    def _add_derived_variables(df: pd.DataFrame) -> pd.DataFrame:
        """Add derived weather variables."""
        df_derived = df.copy()

        # Wind chill
        if "temperature" in df_derived.columns and "wind_speed" in df_derived.columns:
            temp = df_derived["temperature"]
            wind_kmh = df_derived["wind_speed"] * 3.6  # Convert m/s to km/h

            # Wind chill formula (valid for T <= 10°C and wind >= 4.8 km/h)
            mask = (temp <= 10) & (wind_kmh >= 4.8)
            if mask.any():
                wind_chill = (
                    13.12
                    + 0.6215 * temp
                    - 11.37 * (wind_kmh**0.16)
                    + 0.3965 * temp * (wind_kmh**0.16)
                )
                df_derived.loc[mask, "wind_chill"] = wind_chill[mask]

        # Heat index
        if "temperature" in df_derived.columns and "humidity" in df_derived.columns:
            temp_f = df_derived["temperature"] * 9 / 5 + 32  # Convert to Fahrenheit
            rh = df_derived["humidity"]

            # Heat index formula (valid for T >= 80°F and RH >= 40%)
            mask = (temp_f >= 80) & (rh >= 40)
            if mask.any():
                hi = (
                    -42.379
                    + 2.04901523 * temp_f
                    + 10.14333127 * rh
                    - 0.22475541 * temp_f * rh
                    - 6.83783e-3 * temp_f**2
                    - 5.481717e-2 * rh**2
                    + 1.22874e-3 * temp_f**2 * rh
                    + 8.5282e-4 * temp_f * rh**2
                    - 1.99e-6 * temp_f**2 * rh**2
                )

                # Convert back to Celsius
                heat_index_c = (hi - 32) * 5 / 9
                df_derived.loc[mask, "heat_index"] = heat_index_c[mask]

        # Dew point calculation (if not already provided)
        if (
            (
                "dew_point" not in df_derived.columns
                or df_derived["dew_point"].isna().all()
            )
            and "temperature" in df_derived.columns
            and "humidity" in df_derived.columns
        ):
            temp = df_derived["temperature"]
            rh = df_derived["humidity"]

            # Magnus formula for dew point calculation
            # Constants for Magnus formula
            a = 17.27
            b = 237.7

            # Calculate alpha
            alpha = ((a * temp) / (b + temp)) + np.log(rh / 100.0)

            # Calculate dew point
            dew_point = (b * alpha) / (a - alpha)

            df_derived["dew_point"] = dew_point

        return df_derived


class DataClientRegistry:
    """Registry for managing multiple data clients."""

    def __init__(self) -> None:
        """Initialize the registry."""
        self.clients: Dict[str, Dict[str, Any]] = {}
        self.default_priority: List[str] = []

    def register_client(
        self, name: str, client: WeatherDataClient, priority: int = 0
    ) -> None:
        """Register a data client.

        Args:
            name: Client name
            client: Client instance
            priority: Priority (higher = preferred)
        """
        self.clients[name] = {
            "client": client,
            "priority": priority,
            "info": client.get_source_info(),
        }

        # Update priority list
        self.default_priority = sorted(
            self.clients.keys(), key=lambda x: self.clients[x]["priority"], reverse=True
        )

    def get_client(self, name: str) -> Optional[WeatherDataClient]:
        """Get a specific client by name.

        Args:
            name: Client name

        Returns:
            Client instance or None
        """
        return self.clients.get(name, {}).get("client")

    def get_best_client(
        self, requirements: Optional[Dict[str, Any]] = None
    ) -> Optional[WeatherDataClient]:
        """Get the best available client based on requirements.

        Args:
            requirements: Optional requirements dict

        Returns:
            Best available client or None
        """
        for client_name in self.default_priority:
            client: WeatherDataClient = self.clients[client_name]["client"]

            # Test if client is available
            try:
                if client.test_connection():
                    return client
            except (OSError, IOError, RuntimeError, ValueError):
                continue

        return None

    def list_clients(self) -> Dict[str, DataSourceInfo]:
        """List all registered clients.

        Returns:
            Dictionary mapping client names to their info
        """
        return {name: info["info"] for name, info in self.clients.items()}
