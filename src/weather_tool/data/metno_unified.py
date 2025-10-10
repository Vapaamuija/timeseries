"""
Met.no weather data clients.

This module provides implementations for fetching weather data from Met.no services:
- HTTP API client for real-time data via locationforecast API
- File server client for THREDDS archive data
- Unified client combining both sources
"""

import logging
import requests
import xarray as xr
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
import pyproj

from .interfaces import (
    WeatherDataClient, 
    HTTPWeatherClient, 
    FileWeatherClient,
    DataSourceInfo, 
    DataSourceType,
    DataQuality,
    WeatherDataProcessor
)

logger = logging.getLogger(__name__)


class MetNoHTTPClient(HTTPWeatherClient):
    """Met.no HTTP API client for real-time weather data."""
    
    def __init__(self, config: Any):
        """Initialize Met.no HTTP client."""
        super().__init__(config)
        self.base_url = getattr(config.api, 'base_url', 'https://api.met.no/weatherapi/locationforecast/2.0')
        self.user_agent = getattr(config.api, 'user_agent', 'weather-tool/1.0')
        
        # Update session headers for Met.no API requirements
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'application/json',
        })
    
    def get_weather_data(
        self,
        latitude: float,
        longitude: float,
        start_time: datetime,
        end_time: datetime,
        variables: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Fetch weather data from Met.no locationforecast API."""
        if not self.validate_coordinates(latitude, longitude):
            raise ValueError(f"Invalid coordinates: {latitude}, {longitude}")
        
        if not self.validate_time_range(start_time, end_time):
            raise ValueError(f"Invalid time range: {start_time} to {end_time}")
        
        try:
            # Met.no locationforecast API endpoint - use complete to get all cloud layers and dew point
            url = f"{self.base_url}/complete"
            params = {
                'lat': latitude,
                'lon': longitude,
            }
            
            logger.info(f"Fetching weather data from Met.no API for {latitude}, {longitude}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert Met.no JSON to DataFrame
            df = self._parse_metno_json(data, start_time, end_time)
            
            # Standardize the DataFrame
            source_info = self.get_source_info()
            standardized_df = WeatherDataProcessor.standardize_dataframe(df, source_info)
            
            logger.info("Successfully fetched %d data points from Met.no API", len(standardized_df))
            return standardized_df
            
        except requests.RequestException as e:
            logger.error("Failed to fetch data from Met.no API: %s", e)
            raise
        except Exception as e:
            logger.error("Error processing Met.no API data: %s", e)
            raise
    
    def _parse_metno_json(self, data: Dict[str, Any], start_time: datetime, end_time: datetime) -> pd.DataFrame:
        """Parse Met.no JSON response into DataFrame."""
        timeseries = data.get('properties', {}).get('timeseries', [])
        
        if not timeseries:
            raise ValueError("No timeseries data found in Met.no response")
        
        records = []
        for entry in timeseries:
            time_str = entry.get('time')
            if not time_str:
                continue
            
            # Parse timestamp and make timezone-naive for comparison
            timestamp = pd.to_datetime(time_str)
            if timestamp.tz is not None:
                timestamp = timestamp.tz_convert('UTC').tz_localize(None)
            
            # Ensure start_time and end_time are timezone-naive
            start_naive = start_time.replace(tzinfo=None) if start_time.tzinfo else start_time
            end_naive = end_time.replace(tzinfo=None) if end_time.tzinfo else end_time
            
            # Filter by time range
            if timestamp < start_naive or timestamp > end_naive:
                continue
            
            # Extract weather data
            instant_data = entry.get('data', {}).get('instant', {}).get('details', {})
            next_1h_data = entry.get('data', {}).get('next_1_hours', {})
            next_6h_data = entry.get('data', {}).get('next_6_hours', {})
            
            record = {
                'timestamp': timestamp,
                'air_temperature_2m': instant_data.get('air_temperature'),
                'air_pressure_at_sea_level': instant_data.get('air_pressure_at_sea_level'),
                'relative_humidity_2m': instant_data.get('relative_humidity'),
                'wind_speed_10m': instant_data.get('wind_speed'),
                'wind_from_direction_10m': instant_data.get('wind_from_direction'),
                'cloud_area_fraction': instant_data.get('cloud_area_fraction'),
                'high_type_cloud_area_fraction': instant_data.get('cloud_area_fraction_high'),
                'medium_type_cloud_area_fraction': instant_data.get('cloud_area_fraction_medium'),
                'low_type_cloud_area_fraction': instant_data.get('cloud_area_fraction_low'),
                'dew_point_temperature_2m': instant_data.get('dew_point_temperature'),
                'fog_area_fraction': instant_data.get('fog_area_fraction'),
            }
            
            # Add precipitation from next_1_hours or next_6_hours
            if next_1h_data:
                details = next_1h_data.get('details', {})
                record['precipitation_amount'] = details.get('precipitation_amount', 0)
                
                # Weather symbol
                summary = next_1h_data.get('summary', {})
                record['symbol_code'] = summary.get('symbol_code')
            elif next_6h_data:
                details = next_6h_data.get('details', {})
                record['precipitation_amount'] = details.get('precipitation_amount', 0)
                
                # Weather symbol
                summary = next_6h_data.get('summary', {})
                record['symbol_code'] = summary.get('symbol_code')
            else:
                record['precipitation_amount'] = 0
                record['symbol_code'] = None
            
            records.append(record)
        
        if not records:
            raise ValueError("No data points found in specified time range")
        
        df = pd.DataFrame(records)
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)
        
        return df
    
    def test_connection(self) -> bool:
        """Test connection to Met.no API."""
        try:
            # Test with Oslo coordinates
            url = f"{self.base_url}/compact"
            params = {'lat': 59.9139, 'lon': 10.7522}
            
            response = self.session.get(url, params=params, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_source_info(self) -> DataSourceInfo:
        """Get information about Met.no API source."""
        return DataSourceInfo(
            name="Met.no LocationForecast API",
            source_type=DataSourceType.HTTP_API,
            base_url=self.base_url,
            requires_auth=False,
            rate_limited=True,
            available_variables=[
                'air_temperature_2m', 'air_pressure_at_sea_level', 'relative_humidity_2m',
                'wind_speed_10m', 'wind_from_direction_10m', 'precipitation_amount',
                'cloud_area_fraction', 'symbol_code', 'dew_point_temperature_2m', 'fog_area_fraction'
            ],
            time_resolution="1H",
            spatial_resolution="1km",
            update_frequency="6H",
            max_forecast_hours=168,  # 7 days
            description="Met.no LocationForecast API provides weather forecasts for locations worldwide"
        )


class MetNoFileClient(FileWeatherClient):
    """Met.no THREDDS file server client for archive data."""
    
    def __init__(self, config: Any):
        """Initialize Met.no file client."""
        super().__init__(config)
        self.base_url = getattr(config.thredds, 'base_url', 'https://thredds.met.no/thredds/dodsC')
        self.data_path = getattr(config.thredds, 'data_path', 'meps25epsarchive')
    
    def get_weather_data(
        self,
        latitude: float,
        longitude: float,
        start_time: datetime,
        end_time: datetime,
        variables: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Fetch weather data from Met.no THREDDS server."""
        if not self.validate_coordinates(latitude, longitude):
            raise ValueError(f"Invalid coordinates: {latitude}, {longitude}")
        
        if not self.validate_time_range(start_time, end_time):
            raise ValueError(f"Invalid time range: {start_time} to {end_time}")
        
        try:
            # Find the appropriate file URL
            file_url = self._get_file_url(start_time)
            
            logger.info(f"Opening THREDDS file: {file_url}")
            
            # Open dataset
            ds = xr.open_dataset(file_url, decode_times=True)
            
            # Convert coordinates to projection
            x, y = self._convert_coordinates(latitude, longitude, ds)
            
            # Select nearest grid point
            ds_point = ds.sel(x=x, y=y, method='nearest', drop=True)
            
            # Filter by time range
            ds_filtered = ds_point.sel(time=slice(start_time, end_time))
            
            # Convert to DataFrame
            df = ds_filtered.to_dataframe()
            
            # Clean up multi-level columns
            df = self._clean_dataframe(df)
            
            # Standardize the DataFrame
            source_info = self.get_source_info()
            standardized_df = WeatherDataProcessor.standardize_dataframe(df, source_info)
            
            logger.info("Successfully fetched %d data points from THREDDS", len(standardized_df))
            return standardized_df
            
        except Exception as e:
            logger.error("Failed to fetch data from THREDDS: %s", e)
            raise
    
    def _get_file_url(self, target_time: datetime) -> str:
        """Get THREDDS file URL for the target time."""
        # Use a recent file for demonstration
        # In production, this would find the appropriate file based on target_time
        date_str = target_time.strftime("%Y/%m/%d")
        hour_str = "03"  # Use 03Z run as default
        
        # Correct URL structure for MEPS archive
        # The correct base URL should be the dodsC endpoint, not catalog.html
        base_url = "https://thredds.met.no/thredds/dodsC"
        url = f"{base_url}/meps25epsarchive/{date_str}/meps_det_sfc_{target_time.strftime('%Y%m%d')}T{hour_str}Z.ncml"
        
        return url
    
    def _convert_coordinates(self, latitude: float, longitude: float, ds: xr.Dataset) -> tuple:
        """Convert lat/lon to dataset projection coordinates."""
        try:
            # Get projection info from dataset
            crs_info = ds.attrs.get('grid_mapping', {})
            
            # Default Lambert Conformal Conic for MEPS
            crs = pyproj.CRS.from_cf({
                "grid_mapping_name": "lambert_conformal_conic",
                "standard_parallel": [63.3, 63.3],
                "longitude_of_central_meridian": 15.0,
                "latitude_of_projection_origin": 63.3,
                "earth_radius": 6371000.0,
            })
            
            # Transform coordinates
            proj = pyproj.Proj.from_crs(4326, crs, always_xy=True)
            x, y = proj.transform(longitude, latitude)
            
            return x, y
            
        except Exception as e:
            logger.warning(f"Coordinate conversion failed: {e}, using lat/lon directly")
            return longitude, latitude
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean up DataFrame from xarray conversion."""
        # Remove multi-level column names
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] if col[1] == '' else f"{col[0]}_{col[1]}" for col in df.columns]
        
        # Reset index to make time a column, then set it back
        df = df.reset_index()
        if 'time' in df.columns:
            df.set_index('time', inplace=True)
        
        return df
    
    def test_connection(self) -> bool:
        """Test connection to THREDDS server."""
        try:
            # Test with a recent file
            test_date = datetime.now() - timedelta(days=1)
            test_url = self._get_file_url(test_date)
            
            # Try to open the dataset
            ds = xr.open_dataset(test_url)
            ds.close()
            return True
        except Exception:
            return False
    
    def get_source_info(self) -> DataSourceInfo:
        """Get information about THREDDS source."""
        return DataSourceInfo(
            name="Met.no THREDDS Server",
            source_type=DataSourceType.FILE_SERVER,
            base_url=self.base_url,
            requires_auth=False,
            rate_limited=False,
            available_variables=[
                'air_temperature_2m', 'air_pressure_at_sea_level', 'relative_humidity_2m',
                'wind_speed', 'wind_direction', 'precipitation_amount_acc',
                'high_type_cloud_area_fraction', 'medium_type_cloud_area_fraction',
                'low_type_cloud_area_fraction', 'fog_area_fraction'
            ],
            time_resolution="1H",
            spatial_resolution="2.5km",
            update_frequency="6H",
            max_forecast_hours=66,
            description="Met.no THREDDS server provides access to MEPS model data"
        )


class MetNoUnifiedClient(WeatherDataClient):
    """Unified Met.no client combining HTTP API and THREDDS file access."""
    
    def __init__(self, config: Any):
        """Initialize unified Met.no client."""
        super().__init__(config)
        self.http_client = MetNoHTTPClient(config)
        self.file_client = MetNoFileClient(config)
        
        # Preference: try HTTP first, fallback to files
        self.prefer_http = True
    
    def get_weather_data(
        self,
        latitude: float,
        longitude: float,
        start_time: datetime,
        end_time: datetime,
        variables: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Fetch weather data using best available source."""
        
        # For recent/future data, prefer HTTP API
        now = datetime.now()
        if start_time > now - timedelta(days=2):
            try:
                logger.info("Trying Met.no HTTP API for recent/forecast data")
                return self.http_client.get_weather_data(
                    latitude, longitude, start_time, end_time, variables
                )
            except Exception as e:
                logger.warning(f"HTTP API failed: {e}, trying THREDDS")
        
        # For older data or if HTTP fails, try THREDDS
        try:
            logger.info("Trying Met.no THREDDS for archive data")
            return self.file_client.get_weather_data(
                latitude, longitude, start_time, end_time, variables
            )
        except Exception as e:
            logger.warning("THREDDS failed: %s", e)
            
            # If THREDDS fails and we haven't tried HTTP yet, try it
            if start_time <= now - timedelta(days=2):
                try:
                    logger.info("Fallback to HTTP API")
                    return self.http_client.get_weather_data(
                        latitude, longitude, start_time, end_time, variables
                    )
                except Exception as e2:
                    logger.error("Both HTTP and THREDDS failed: HTTP=%s, THREDDS=%s", e2, e)
                    raise
            else:
                raise
    
    
    def test_connection(self) -> bool:
        """Test connection to both HTTP and THREDDS."""
        http_ok = self.http_client.test_connection()
        file_ok = self.file_client.test_connection()
        
        logger.info("Connection test: HTTP=%s, THREDDS=%s", http_ok, file_ok)
        return http_ok or file_ok
    
    def get_source_info(self) -> DataSourceInfo:
        """Get information about unified source."""
        return DataSourceInfo(
            name="Met.no Unified Client",
            source_type=DataSourceType.HTTP_API,  # Primary type
            base_url="https://api.met.no + https://thredds.met.no",
            requires_auth=False,
            rate_limited=True,
            available_variables=[
                'temperature', 'pressure', 'humidity', 'wind_speed', 'wind_direction',
                'precipitation', 'cloud_cover', 'weather_symbol', 'visibility',
                'dew_point', 'cloud_high', 'cloud_medium', 'cloud_low', 'fog'
            ],
            time_resolution="1H",
            spatial_resolution="1-2.5km",
            update_frequency="6H",
            max_forecast_hours=168,
            description="Unified Met.no client combining HTTP API and THREDDS access"
        )
