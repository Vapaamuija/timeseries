"""
Weather symbol mapping and definitions.

This module contains the comprehensive mapping of Met.no weather symbols
to their display properties, colors, and descriptions.
"""

from typing import Any, Dict, List, Optional


class WeatherSymbolMapping:
    """Manages weather symbol mappings and metadata."""

    def __init__(self) -> None:
        """Initialize the symbol mapping."""
        self.symbol_mapping = self._create_metno_symbol_mapping()

    def _create_metno_symbol_mapping(self) -> Dict[str, Dict[str, Any]]:
        """Create comprehensive Met.no symbol mapping.

        Returns:
            Dictionary mapping symbol codes to display properties
        """
        symbols = {
            # Clear sky
            "clearsky_day": {
                "svg": "clearsky_day.svg",
                "color": "#FFD700",
                "description": "Clear sky",
            },
            "clearsky_night": {
                "svg": "clearsky_night.svg",
                "color": "#4169E1",
                "description": "Clear sky",
            },
            "clearsky_polartwilight": {
                "svg": "clearsky_polartwilight.svg",
                "color": "#FF8C00",
                "description": "Clear sky (polar twilight)",
            },
            # Fair weather
            "fair_day": {
                "svg": "fair_day.svg",
                "color": "#FFD700",
                "description": "Fair",
            },
            "fair_night": {
                "svg": "fair_night.svg",
                "color": "#4169E1",
                "description": "Fair",
            },
            "fair_polartwilight": {
                "svg": "fair_polartwilight.svg",
                "color": "#FF8C00",
                "description": "Fair (polar twilight)",
            },
            # Partly cloudy
            "partlycloudy_day": {
                "svg": "partlycloudy_day.svg",
                "color": "#87CEEB",
                "description": "Partly cloudy",
            },
            "partlycloudy_night": {
                "svg": "partlycloudy_night.svg",
                "color": "#696969",
                "description": "Partly cloudy",
            },
            "partlycloudy_polartwilight": {
                "svg": "partlycloudy_polartwilight.svg",
                "color": "#696969",
                "description": "Partly cloudy (polar twilight)",
            },
            # Cloudy
            "cloudy": {
                "svg": "cloudy.svg",
                "color": "#696969",
                "description": "Cloudy",
            },
            # Rain showers
            "lightrainshowers_day": {
                "svg": "lightrainshowers_day.svg",
                "color": "#4682B4",
                "description": "Light rain showers",
            },
            "lightrainshowers_night": {
                "svg": "lightrainshowers_night.svg",
                "color": "#4682B4",
                "description": "Light rain showers",
            },
            "lightrainshowers_polartwilight": {
                "svg": "lightrainshowers_polartwilight.svg",
                "color": "#4682B4",
                "description": "Light rain showers (polar twilight)",
            },
            "rainshowers_day": {
                "svg": "rainshowers_day.svg",
                "color": "#1E90FF",
                "description": "Rain showers",
            },
            "rainshowers_night": {
                "svg": "rainshowers_night.svg",
                "color": "#1E90FF",
                "description": "Rain showers",
            },
            "rainshowers_polartwilight": {
                "svg": "rainshowers_polartwilight.svg",
                "color": "#1E90FF",
                "description": "Rain showers (polar twilight)",
            },
            "heavyrainshowers_day": {
                "svg": "heavyrainshowers_day.svg",
                "color": "#0000CD",
                "description": "Heavy rain showers",
            },
            "heavyrainshowers_night": {
                "svg": "heavyrainshowers_night.svg",
                "color": "#0000CD",
                "description": "Heavy rain showers",
            },
            "heavyrainshowers_polartwilight": {
                "svg": "heavyrainshowers_polartwilight.svg",
                "color": "#0000CD",
                "description": "Heavy rain showers (polar twilight)",
            },
            # Rain
            "lightrain": {
                "svg": "lightrain.svg",
                "color": "#4682B4",
                "description": "Light rain",
            },
            "rain": {"svg": "rain.svg", "color": "#1E90FF", "description": "Rain"},
            "heavyrain": {
                "svg": "heavyrain.svg",
                "color": "#0000CD",
                "description": "Heavy rain",
            },
            # Snow showers
            "lightsnowshowers_day": {
                "svg": "lightsnowshowers_day.svg",
                "color": "#B0E0E6",
                "description": "Light snow showers",
            },
            "lightsnowshowers_night": {
                "svg": "lightsnowshowers_night.svg",
                "color": "#B0E0E6",
                "description": "Light snow showers",
            },
            "lightsnowshowers_polartwilight": {
                "svg": "lightsnowshowers_polartwilight.svg",
                "color": "#B0E0E6",
                "description": "Light snow showers (polar twilight)",
            },
            "snowshowers_day": {
                "svg": "snowshowers_day.svg",
                "color": "#87CEEB",
                "description": "Snow showers",
            },
            "snowshowers_night": {
                "svg": "snowshowers_night.svg",
                "color": "#87CEEB",
                "description": "Snow showers",
            },
            "snowshowers_polartwilight": {
                "svg": "snowshowers_polartwilight.svg",
                "color": "#87CEEB",
                "description": "Snow showers (polar twilight)",
            },
            "heavysnowshowers_day": {
                "svg": "heavysnowshowers_day.svg",
                "color": "#4169E1",
                "description": "Heavy snow showers",
            },
            "heavysnowshowers_night": {
                "svg": "heavysnowshowers_night.svg",
                "color": "#4169E1",
                "description": "Heavy snow showers",
            },
            "heavysnowshowers_polartwilight": {
                "svg": "heavysnowshowers_polartwilight.svg",
                "color": "#4169E1",
                "description": "Heavy snow showers (polar twilight)",
            },
            # Snow
            "lightsnow": {
                "svg": "lightsnow.svg",
                "color": "#B0E0E6",
                "description": "Light snow",
            },
            "snow": {"svg": "snow.svg", "color": "#87CEEB", "description": "Snow"},
            "heavysnow": {
                "svg": "heavysnow.svg",
                "color": "#4169E1",
                "description": "Heavy snow",
            },
            # Sleet
            "lightsleet": {
                "svg": "lightsleet.svg",
                "color": "#20B2AA",
                "description": "Light sleet",
            },
            "sleet": {"svg": "sleet.svg", "color": "#008B8B", "description": "Sleet"},
            "heavysleet": {
                "svg": "heavysleet.svg",
                "color": "#006400",
                "description": "Heavy sleet",
            },
            # Thunder
            "lightrainandthundershowers_day": {
                "svg": "lightrainandthundershowers_day.svg",
                "color": "#8B008B",
                "description": "Light rain and thunder showers",
            },
            "rainandthunder": {
                "svg": "rainandthunder.svg",
                "color": "#8B008B",
                "description": "Rain and thunder",
            },
            # Fog
            "fog": {"svg": "fog.svg", "color": "#696969", "description": "Fog"},
        }

        return symbols

    def get_symbol_info(self, symbol_code: Any) -> Optional[Dict[str, Any]]:
        """Get symbol information for a weather code.

        Args:
            symbol_code: Weather symbol code from Met.no (int or str)

        Returns:
            Dictionary with symbol information or None if not found
        """
        # Handle both integer and string codes
        if isinstance(symbol_code, (int, float)):
            # Map integer codes to descriptive keys (simplified WMO codes)
            int_code = int(symbol_code)
            code_mapping = {
                1: "clearsky_day",
                2: "fair_day",
                3: "partlycloudy_day",
                4: "cloudy",
                9: "lightrain",
                10: "rain",
                12: "lightsnow",
                13: "snow",
            }
            clean_code = code_mapping.get(
                int_code, "clearsky_day"
            )  # Default to clear sky
        else:
            clean_code = str(symbol_code).lower().strip()

        # Try exact match first
        if clean_code in self.symbol_mapping:
            return self.symbol_mapping[clean_code]

        # Try partial matches for codes with variants
        for code, info in self.symbol_mapping.items():
            if clean_code.startswith(code.split("_")[0]):
                return info

        # Default fallback
        return {
            "svg": None,
            "color": "#000000",
            "description": f"Unknown ({symbol_code})",
        }

    def get_supported_symbols(self) -> List[str]:
        """Get list of supported weather symbol codes.

        Returns:
            List of supported Met.no symbol codes
        """
        return list(self.symbol_mapping.keys())

    def get_symbol_statistics(self, symbol_data) -> Dict[str, Any]:
        """Get statistics about weather symbols in the data.

        Args:
            symbol_data: Series with weather symbol data

        Returns:
            Dictionary with symbol statistics
        """
        if symbol_data.empty:
            return {"total_symbols": 0, "unique_symbols": 0, "symbol_counts": {}}

        # Count occurrences
        symbol_counts = symbol_data.value_counts().to_dict()

        # Get descriptions
        symbol_descriptions = {}
        for code, count in symbol_counts.items():
            symbol_info = self.get_symbol_info(code)
            description = (
                symbol_info["description"] if symbol_info else f"Unknown ({code})"
            )
            symbol_descriptions[description] = count

        return {
            "total_symbols": len(symbol_data),
            "unique_symbols": len(symbol_counts),
            "symbol_counts": symbol_descriptions,
            "most_common": (
                max(symbol_descriptions.items(), key=lambda x: x[1])
                if symbol_descriptions
                else None
            ),
            "metno_codes": symbol_counts,
        }
