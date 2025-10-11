"""
Icon management for weather symbols.

This module handles downloading, caching, and managing SVG icons from the Met.no repository.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)


class IconManager:
    """Manages SVG icon downloading and caching."""

    def __init__(self, cache_dir: Path, base_url: str) -> None:
        """Initialize icon manager.

        Args:
            cache_dir: Directory to cache downloaded icons
            base_url: Base URL for Met.no weather icons repository
        """
        self.cache_dir = cache_dir
        self.base_url = base_url

    def get_icon_path(self, symbol_code: Any) -> Optional[Path]:
        """Get the path to an SVG icon file.

        Args:
            symbol_code: Weather symbol code (int or str)

        Returns:
            Path to SVG file or None if not found
        """
        if not symbol_code:
            return None

        # Convert to string if it's an integer
        symbol_code = str(symbol_code)

        # Clean symbol code (remove any _d or _n suffixes for day/night variants)
        base_symbol = symbol_code.replace("_d", "").replace("_n", "")

        # Try exact match first
        svg_path = self.cache_dir / f"{symbol_code}.svg"
        if svg_path.exists():
            return svg_path

        # Try base symbol without day/night suffix
        svg_path = self.cache_dir / f"{base_symbol}.svg"
        if svg_path.exists():
            return svg_path

        # Try common variations
        variations = [
            f"{symbol_code}_day.svg",
            f"{symbol_code}_night.svg",
            f"{base_symbol}_day.svg",
            f"{base_symbol}_night.svg",
        ]

        for variation in variations:
            svg_path = self.cache_dir / variation
            if svg_path.exists():
                return svg_path

        return None

    def download_svg_icon(self, svg_filename: str) -> Optional[Path]:
        """Download SVG icon from Met.no repository.

        Args:
            svg_filename: Name of the SVG icon file

        Returns:
            Path to downloaded icon or None if failed
        """
        if not svg_filename:
            return None

        # Set up cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Check if already cached
        icon_path = self.cache_dir / svg_filename
        if icon_path.exists():
            return icon_path

        # Download from official Met.no repository
        try:
            url = self.base_url + svg_filename
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            with open(icon_path, "wb") as f:
                f.write(response.content)

            logger.debug("Downloaded Met.no weather icon: %s", svg_filename)
            return icon_path

        except (requests.RequestException, OSError, IOError) as e:
            logger.warning(
                "Failed to download Met.no weather icon %s: %s", svg_filename, e
            )
            return None

    def download_all_icons(
        self, symbol_mapping: Dict[str, Dict[str, Any]]
    ) -> Dict[str, bool]:
        """Download all SVG icons from the Met.no repository.

        Args:
            symbol_mapping: Dictionary mapping symbol codes to their properties

        Returns:
            Dictionary mapping icon names to download success status
        """
        results = {}

        logger.info("Downloading all Met.no weather icons...")

        for symbol_info in symbol_mapping.values():
            svg_filename = symbol_info.get("svg")
            if svg_filename:
                icon_path = self.download_svg_icon(svg_filename)
                results[svg_filename] = icon_path is not None

        successful = sum(results.values())
        total = len(results)

        logger.info("Downloaded %d/%d Met.no weather icons", successful, total)

        return results

    def ensure_essential_icons(self, symbol_mapping: Dict[str, Dict[str, Any]]) -> None:
        """Ensure essential weather icons are available locally.

        Args:
            symbol_mapping: Dictionary mapping symbol codes to their properties
        """
        essential_icons = [
            "clearsky_day.svg",
            "clearsky_night.svg",
            "fair_day.svg",
            "fair_night.svg",
            "partlycloudy_day.svg",
            "partlycloudy_night.svg",
            "cloudy.svg",
            "lightrain.svg",
            "rain.svg",
            "heavyrain.svg",
            "lightsnow.svg",
            "snow.svg",
            "heavysnow.svg",
            "fog.svg",
            "rainshowers_day.svg",
            "snowshowers_day.svg",
        ]

        missing_icons = []
        for icon in essential_icons:
            icon_path = self.cache_dir / icon
            if not icon_path.exists():
                missing_icons.append(icon)

        if missing_icons:
            logger.info(
                "Downloading %d essential Met.no weather icons...", len(missing_icons)
            )
            for icon in missing_icons:
                self.download_svg_icon(icon)

    def get_icon_statistics(self) -> Dict[str, Any]:
        """Get statistics about cached icons.

        Returns:
            Dictionary with icon statistics
        """
        if not self.cache_dir.exists():
            return {"total_icons": 0, "cache_size_mb": 0}

        svg_files = list(self.cache_dir.glob("*.svg"))
        total_size = sum(f.stat().st_size for f in svg_files)

        return {
            "total_icons": len(svg_files),
            "cache_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_directory": str(self.cache_dir),
        }
