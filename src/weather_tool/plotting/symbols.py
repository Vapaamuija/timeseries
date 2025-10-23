"""
Unified weather symbols implementation.

This module consolidates all weather symbol functionality into a single,
clean implementation using official Met.no weather symbols from:
https://github.com/metno/weathericons/tree/main/weather

The implementation follows SOLID principles with clear separation of concerns:
- SymbolMapping: Manages symbol definitions and metadata
- IconManager: Handles downloading and caching of SVG icons
- SVGRenderer: Manages SVG rendering and Cairo setup
- SymbolProcessor: Processes symbols and handles positioning logic
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from matplotlib.axes import Axes

from .icon_manager import IconManager
from .interfaces import PlotConfig, SymbolType, WeatherSymbolRenderer
from .svg_renderer import SVGRenderer
from .symbol_mapping import WeatherSymbolMapping
from .symbol_processor import SymbolProcessor

logger = logging.getLogger(__name__)


class UnifiedWeatherSymbols(WeatherSymbolRenderer):
    """Unified weather symbol renderer using ONLY official Met.no SVG symbols.

    This renderer exclusively uses SVG symbols from the official Met.no weather icons repository.
    No fallback markers are used - if SVG rendering fails, symbols are simply skipped.

    REQUIRED dependencies for SVG rendering:
        pip install cairosvg pillow

    Or run the setup script:
        ./bin/setup_svg_rendering.sh

    If SVG rendering is not available, no weather symbols will be displayed.
    """

    def __init__(self, config: PlotConfig):
        """Initialize unified weather symbols.

        Args:
            config: Plot configuration
        """
        super().__init__(config)

        # Official Met.no weather icons repository
        self.icon_base_url = (
            "https://raw.githubusercontent.com/metno/weathericons/main/weather/svg/"
        )
        self.icon_cache_dir = Path("data/metno_weather_icons")

        # Initialize components following dependency injection pattern
        self.symbol_mapping = WeatherSymbolMapping()
        self.icon_manager = IconManager(self.icon_cache_dir, self.icon_base_url)
        self.svg_renderer = SVGRenderer(config.symbol_size)
        self.symbol_processor = SymbolProcessor(
            config, self.symbol_mapping, self.icon_manager, self.svg_renderer
        )

        # Always use SVG symbols - this is the only supported type
        self.config.symbol_type = SymbolType.SVG
        logger.info("Using SVG icons from Met.no repository")

        # Auto-download icons if enabled
        if config.auto_download_icons:
            self.icon_manager.ensure_essential_icons(self.symbol_mapping.symbol_mapping)

    def has_high_quality_svg_support(self) -> bool:
        """Check if high-quality SVG rendering is available.

        Returns:
            True if cairosvg and PIL are available for true SVG rendering
        """
        return self.svg_renderer.has_high_quality_svg_support()

    def get_svg_installation_instructions(self) -> str:
        """Get platform-specific instructions for installing SVG support.

        Returns:
            String with installation instructions
        """
        return self.svg_renderer.get_svg_installation_instructions()

    def add_symbols_to_plot(
        self,
        ax: Axes,
        data: pd.DataFrame,
        y_position: Optional[float] = None,
        **kwargs: Any,
    ) -> int:
        """Add weather symbols to a plot.

        Args:
            ax: matplotlib Axes object
            data: DataFrame with 'weather_symbol' column
            y_position: Y position for symbols
            **kwargs: Additional parameters

        Returns:
            Number of symbols added
        """
        return self.symbol_processor.add_symbols_to_plot(ax, data, y_position, **kwargs)

    def get_symbol_info(self, symbol_code: Any) -> Optional[Dict[str, Any]]:
        """Get symbol information for a weather code.

        Args:
            symbol_code: Weather symbol code from Met.no (int or str)

        Returns:
            Dictionary with symbol information or None if not found
        """
        return self.symbol_mapping.get_symbol_info(symbol_code)

    def get_supported_symbols(self) -> List[str]:
        """Get list of supported weather symbol codes.

        Returns:
            List of supported Met.no symbol codes
        """
        return self.symbol_mapping.get_supported_symbols()

    def download_svg_icon(self, svg_filename: str) -> Optional[Path]:
        """Download SVG icon from Met.no repository.

        Args:
            svg_filename: Name of the SVG icon file

        Returns:
            Path to downloaded icon or None if failed
        """
        return self.icon_manager.download_svg_icon(svg_filename)

    def download_all_icons(self) -> Dict[str, bool]:
        """Download all SVG icons from the Met.no repository.

        Returns:
            Dictionary mapping icon names to download success status
        """
        return self.icon_manager.download_all_icons(self.symbol_mapping.symbol_mapping)

    def get_icon_path(self, symbol_code: str) -> Optional[Path]:
        """Get local path to SVG icon for a symbol code.

        Args:
            symbol_code: Weather symbol code

        Returns:
            Path to local SVG icon or None if not available
        """
        symbol_info = self.get_symbol_info(symbol_code)
        if not symbol_info or not symbol_info.get("svg"):
            return None

        svg_filename = symbol_info["svg"]
        if not isinstance(svg_filename, str):
            return None
        icon_path = self.icon_cache_dir / svg_filename

        if not icon_path.exists():
            # Try to download it
            return self.download_svg_icon(svg_filename)

        return icon_path

    def get_symbol_statistics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Get statistics about weather symbols in the data.

        Args:
            data: DataFrame with weather symbol data

        Returns:
            Dictionary with symbol statistics
        """
        return self.symbol_processor.get_symbol_statistics(data)

    def get_icon_statistics(self) -> Dict[str, Any]:
        """Get statistics about cached icons.

        Returns:
            Dictionary with icon statistics
        """
        return self.icon_manager.get_icon_statistics()
