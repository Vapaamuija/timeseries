"""Airport data management."""

import logging
import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import requests
import pandas as pd


logger = logging.getLogger(__name__)


class AirportManager:
    """Manager for airport data and operations."""
    
    def __init__(self, config):
        """Initialize the airport manager.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.airports_data = {}
        self.airports_file = self.config.data_dir / "airports.json"
        
        # Load airport data
        self._load_airports()
    
    def _load_airports(self) -> None:
        """Load airport data from file or download if not available."""
        if self.airports_file.exists():
            try:
                with open(self.airports_file, 'r', encoding='utf-8') as f:
                    self.airports_data = json.load(f)
                logger.info(f"Loaded {len(self.airports_data)} airports from file")
                return
            except Exception as e:
                logger.warning(f"Failed to load airports from file: {e}")
        
        # Try to download airport data
        try:
            self._download_airport_data()
        except Exception as e:
            logger.warning(f"Failed to download airport data: {e}")
            # Load default airports as fallback
            self._load_default_airports()
    
    def _download_airport_data(self) -> None:
        """Download airport data from online sources."""
        logger.info("Downloading airport data...")
        
        # Try multiple sources for airport data
        sources = [
            {
                'url': 'https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airports.csv',
                'format': 'csv',
                'name': 'OurAirports'
            },
            # Add more sources as needed
        ]
        
        for source in sources:
            try:
                airports = self._download_from_source(source)
                if airports:
                    self.airports_data = airports
                    self._save_airports()
                    logger.info(f"Successfully downloaded {len(airports)} airports from {source['name']}")
                    return
            except Exception as e:
                logger.warning(f"Failed to download from {source['name']}: {e}")
                continue
        
        raise Exception("Failed to download airport data from any source")
    
    def _download_from_source(self, source: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """Download airport data from a specific source.
        
        Args:
            source: Source configuration dictionary
            
        Returns:
            Dictionary of airport data
        """
        response = requests.get(source['url'], timeout=30)
        response.raise_for_status()
        
        airports = {}
        
        if source['format'] == 'csv':
            # Parse CSV data
            lines = response.text.strip().split('\n')
            reader = csv.DictReader(lines)
            
            for row in reader:
                # Filter for airports with ICAO codes
                icao = row.get('ident', '').strip().upper()
                if not icao or len(icao) != 4:
                    continue
                
                # Skip non-airport types
                airport_type = row.get('type', '').lower()
                if airport_type not in ['large_airport', 'medium_airport', 'small_airport']:
                    continue
                
                # Extract relevant data
                try:
                    airport_data = {
                        'icao': icao,
                        'name': row.get('name', '').strip(),
                        'latitude': float(row.get('latitude_deg', 0)),
                        'longitude': float(row.get('longitude_deg', 0)),
                        'elevation': float(row.get('elevation_ft', 0)) if row.get('elevation_ft') else None,
                        'country': row.get('iso_country', '').strip(),
                        'region': row.get('iso_region', '').strip(),
                        'municipality': row.get('municipality', '').strip(),
                        'iata': row.get('iata_code', '').strip().upper() if row.get('iata_code') else None,
                        'type': airport_type,
                    }
                    
                    # Validate coordinates
                    if (-90 <= airport_data['latitude'] <= 90 and 
                        -180 <= airport_data['longitude'] <= 180):
                        airports[icao] = airport_data
                
                except (ValueError, TypeError) as e:
                    logger.debug(f"Skipping invalid airport data for {icao}: {e}")
                    continue
        
        return airports
    
    def _load_default_airports(self) -> None:
        """Load a default set of airports as fallback."""
        logger.info("Loading default airport data")
        
        # Default airports (major international airports)
        default_airports = {
            'ENGM': {
                'icao': 'ENGM',
                'name': 'Oslo Airport, Gardermoen',
                'latitude': 60.1939,
                'longitude': 11.1004,
                'elevation': 681,
                'country': 'NO',
                'region': 'NO-02',
                'municipality': 'Ullensaker',
                'iata': 'OSL',
                'type': 'large_airport',
            },
            'ESSA': {
                'icao': 'ESSA',
                'name': 'Stockholm Arlanda Airport',
                'latitude': 59.6519,
                'longitude': 17.9186,
                'elevation': 137,
                'country': 'SE',
                'region': 'SE-AB',
                'municipality': 'Sigtuna',
                'iata': 'ARN',
                'type': 'large_airport',
            },
            'EKCH': {
                'icao': 'EKCH',
                'name': 'Copenhagen Airport',
                'latitude': 55.6181,
                'longitude': 12.6561,
                'elevation': 17,
                'country': 'DK',
                'region': 'DK-84',
                'municipality': 'Kastrup',
                'iata': 'CPH',
                'type': 'large_airport',
            },
            'EFHK': {
                'icao': 'EFHK',
                'name': 'Helsinki Airport',
                'latitude': 60.3172,
                'longitude': 24.9633,
                'elevation': 179,
                'country': 'FI',
                'region': 'FI-01',
                'municipality': 'Vantaa',
                'iata': 'HEL',
                'type': 'large_airport',
            },
            'EHAM': {
                'icao': 'EHAM',
                'name': 'Amsterdam Airport Schiphol',
                'latitude': 52.3086,
                'longitude': 4.7639,
                'elevation': -11,
                'country': 'NL',
                'region': 'NL-NH',
                'municipality': 'Haarlemmermeer',
                'iata': 'AMS',
                'type': 'large_airport',
            },
        }
        
        self.airports_data = default_airports
        self._save_airports()
    
    def _save_airports(self) -> None:
        """Save airport data to file."""
        try:
            self.config.ensure_directories()
            with open(self.airports_file, 'w', encoding='utf-8') as f:
                json.dump(self.airports_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.airports_data)} airports to file")
        except Exception as e:
            logger.error(f"Failed to save airports to file: {e}")
    
    def get_airport(self, icao_code: str) -> Optional[Dict[str, Any]]:
        """Get airport information by ICAO code.
        
        Args:
            icao_code: ICAO airport code
            
        Returns:
            Airport information dictionary or None if not found
        """
        icao_code = icao_code.upper().strip()
        return self.airports_data.get(icao_code)
    
    def list_airports(
        self,
        country: Optional[str] = None,
        region: Optional[str] = None,
        airport_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get list of airports with optional filtering.
        
        Args:
            country: Filter by country code
            region: Filter by region code
            airport_type: Filter by airport type
            
        Returns:
            List of airport dictionaries
        """
        airports = list(self.airports_data.values())
        
        # Apply filters
        if country:
            airports = [a for a in airports if a.get('country', '').upper() == country.upper()]
        
        if region:
            airports = [a for a in airports if a.get('region', '').upper() == region.upper()]
        
        if airport_type:
            airports = [a for a in airports if a.get('type', '').lower() == airport_type.lower()]
        
        # Sort by name
        airports.sort(key=lambda x: x.get('name', ''))
        
        return airports
    
    def search_airports(self, query: str) -> List[Dict[str, Any]]:
        """Search for airports by name, ICAO code, or IATA code.
        
        Args:
            query: Search query
            
        Returns:
            List of matching airport dictionaries
        """
        query = query.lower().strip()
        matches = []
        
        for airport in self.airports_data.values():
            # Check ICAO code
            if airport.get('icao', '').lower().startswith(query):
                matches.append(airport)
                continue
            
            # Check IATA code
            if airport.get('iata') and airport['iata'].lower().startswith(query):
                matches.append(airport)
                continue
            
            # Check name
            if query in airport.get('name', '').lower():
                matches.append(airport)
                continue
            
            # Check municipality
            if query in airport.get('municipality', '').lower():
                matches.append(airport)
                continue
        
        # Sort by relevance (exact matches first, then by name)
        def sort_key(airport):
            icao_match = airport.get('icao', '').lower() == query
            iata_match = airport.get('iata', '').lower() == query if airport.get('iata') else False
            name_start = airport.get('name', '').lower().startswith(query)
            
            # Priority: exact ICAO > exact IATA > name starts with > other matches
            if icao_match:
                return (0, airport.get('name', ''))
            elif iata_match:
                return (1, airport.get('name', ''))
            elif name_start:
                return (2, airport.get('name', ''))
            else:
                return (3, airport.get('name', ''))
        
        matches.sort(key=sort_key)
        
        return matches
    
    def get_airports_by_country(self, country_code: str) -> List[Dict[str, Any]]:
        """Get all airports in a specific country.
        
        Args:
            country_code: ISO country code (e.g., 'NO', 'SE', 'DK')
            
        Returns:
            List of airport dictionaries
        """
        return self.list_airports(country=country_code)
    
    def get_nearby_airports(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 100,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Find airports near a given location.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            radius_km: Search radius in kilometers
            max_results: Maximum number of results to return
            
        Returns:
            List of nearby airport dictionaries with distances
        """
        import math
        
        def haversine_distance(lat1, lon1, lat2, lon2):
            """Calculate the great circle distance between two points."""
            R = 6371  # Earth's radius in kilometers
            
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = (math.sin(dlat/2)**2 + 
                 math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2)
            c = 2 * math.asin(math.sqrt(a))
            
            return R * c
        
        nearby_airports = []
        
        for airport in self.airports_data.values():
            try:
                airport_lat = float(airport.get('latitude', 0))
                airport_lon = float(airport.get('longitude', 0))
                
                distance = haversine_distance(latitude, longitude, airport_lat, airport_lon)
                
                if distance <= radius_km:
                    airport_with_distance = airport.copy()
                    airport_with_distance['distance_km'] = round(distance, 2)
                    nearby_airports.append(airport_with_distance)
            
            except (ValueError, TypeError):
                continue
        
        # Sort by distance
        nearby_airports.sort(key=lambda x: x['distance_km'])
        
        return nearby_airports[:max_results]
    
    def add_airport(self, airport_data: Dict[str, Any]) -> bool:
        """Add a new airport to the database.
        
        Args:
            airport_data: Airport information dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate required fields
            required_fields = ['icao', 'name', 'latitude', 'longitude']
            for field in required_fields:
                if field not in airport_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate ICAO code
            icao = airport_data['icao'].upper().strip()
            if len(icao) != 4:
                raise ValueError("ICAO code must be 4 characters")
            
            # Validate coordinates
            lat = float(airport_data['latitude'])
            lon = float(airport_data['longitude'])
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                raise ValueError("Invalid coordinates")
            
            # Add to database
            self.airports_data[icao] = airport_data.copy()
            self.airports_data[icao]['icao'] = icao
            
            # Save to file
            self._save_airports()
            
            logger.info(f"Added airport {icao}: {airport_data.get('name')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add airport: {e}")
            return False
    
    def remove_airport(self, icao_code: str) -> bool:
        """Remove an airport from the database.
        
        Args:
            icao_code: ICAO airport code
            
        Returns:
            True if successful, False otherwise
        """
        try:
            icao_code = icao_code.upper().strip()
            
            if icao_code in self.airports_data:
                del self.airports_data[icao_code]
                self._save_airports()
                logger.info(f"Removed airport {icao_code}")
                return True
            else:
                logger.warning(f"Airport {icao_code} not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove airport {icao_code}: {e}")
            return False
    
    def update_airport_data(self) -> bool:
        """Update airport data from online sources.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Updating airport data...")
            old_count = len(self.airports_data)
            
            self._download_airport_data()
            
            new_count = len(self.airports_data)
            logger.info(f"Airport data updated: {old_count} -> {new_count} airports")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update airport data: {e}")
            return False
    
    def export_airports(
        self,
        output_path: str,
        format: str = 'csv',
        filter_params: Optional[Dict[str, str]] = None
    ) -> bool:
        """Export airport data to file.
        
        Args:
            output_path: Output file path
            format: Export format ('csv', 'json')
            filter_params: Optional filter parameters
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get airports to export
            airports = self.list_airports(**(filter_params or {}))
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == 'csv':
                # Export as CSV
                if airports:
                    df = pd.DataFrame(airports)
                    df.to_csv(output_path, index=False)
                else:
                    # Create empty CSV with headers
                    headers = ['icao', 'name', 'latitude', 'longitude', 'elevation', 
                              'country', 'region', 'municipality', 'iata', 'type']
                    pd.DataFrame(columns=headers).to_csv(output_path, index=False)
            
            elif format.lower() == 'json':
                # Export as JSON
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(airports, f, indent=2, ensure_ascii=False)
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Exported {len(airports)} airports to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export airports: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the airport database.
        
        Returns:
            Dictionary with statistics
        """
        if not self.airports_data:
            return {'total_airports': 0}
        
        airports = list(self.airports_data.values())
        
        # Count by country
        countries = {}
        for airport in airports:
            country = airport.get('country', 'Unknown')
            countries[country] = countries.get(country, 0) + 1
        
        # Count by type
        types = {}
        for airport in airports:
            airport_type = airport.get('type', 'Unknown')
            types[airport_type] = types.get(airport_type, 0) + 1
        
        return {
            'total_airports': len(airports),
            'countries': len(countries),
            'by_country': dict(sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10]),
            'by_type': types,
            'has_iata': len([a for a in airports if a.get('iata')]),
            'has_elevation': len([a for a in airports if a.get('elevation') is not None]),
        }
