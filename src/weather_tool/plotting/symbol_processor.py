"""
Symbol processing and positioning logic.

This module handles the processing of weather symbols, including positioning,
sampling, and coordinate calculations for matplotlib integration.
"""

import logging
from typing import Any, Optional

import pandas as pd
from matplotlib.axes import Axes

from .icon_manager import IconManager
from .interfaces import PlotConfig
from .svg_renderer import SVGRenderer
from .symbol_mapping import WeatherSymbolMapping

logger = logging.getLogger(__name__)


class SymbolProcessor:
    """Processes weather symbols for plotting."""

    def __init__(
        self,
        config: PlotConfig,
        symbol_mapping: WeatherSymbolMapping,
        icon_manager: IconManager,
        svg_renderer: SVGRenderer,
    ) -> None:
        """Initialize symbol processor.

        Args:
            config: Plot configuration
            symbol_mapping: Weather symbol mapping instance
            icon_manager: Icon manager instance
            svg_renderer: SVG renderer instance
        """
        self.config = config
        self.symbol_mapping = symbol_mapping
        self.icon_manager = icon_manager
        self.svg_renderer = svg_renderer

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
        if "weather_symbol" not in data.columns:
            logger.warning("No weather symbol data available")
            return 0

        # Filter out NaN values
        symbol_data = data["weather_symbol"].dropna()

        if symbol_data.empty:
            logger.warning("No valid weather symbols found")
            return 0

        # Extract symbol_type from kwargs if provided
        symbol_type = kwargs.get("symbol_type", self.config.symbol_type)

        logger.debug("Using symbol type: %s", symbol_type)

        # Determine y position for symbols
        if y_position is None:
            y_min, y_max = ax.get_ylim()
            y_position = (
                y_max - (y_max - y_min) * 0.15
            )  # 15% from top for better visibility

        # Sample symbols to avoid overcrowding
        sampled_data = self._sample_symbols(symbol_data)

        # Add symbols with proper handling - SVG only
        symbols_added = self._render_svg_symbols(ax, sampled_data, y_position)

        logger.info("Added %d weather symbols to plot", symbols_added)
        return symbols_added

    def _sample_symbols(self, symbol_data: pd.Series) -> pd.Series:
        """Sample symbols to avoid overcrowding.

        Args:
            symbol_data: Series with weather symbol data

        Returns:
            Sampled symbol data
        """
        n_symbols = len(symbol_data)
        if (
            n_symbols > 50
        ):  # Increased threshold to avoid sampling for typical meteogram data
            step = max(1, n_symbols // 20)
            sampled_data = symbol_data.iloc[::step]
            logger.debug(
                "Sampled %d symbols from %d (step=%d)",
                len(sampled_data),
                n_symbols,
                step,
            )
            return sampled_data
        else:
            logger.debug("No sampling needed for %d symbols", n_symbols)
            return symbol_data

    def _render_svg_symbols(
        self, ax: Axes, symbol_data: pd.Series, y_position: float
    ) -> int:
        """Render SVG symbols to the plot.

        Args:
            ax: matplotlib Axes object
            symbol_data: Series with weather symbol data
            y_position: Y position for symbols

        Returns:
            Number of symbols added
        """
        symbols_added = 0

        # Check SVG rendering capability before processing any symbols
        if not self.svg_renderer.has_high_quality_svg_support():
            logger.error("SVG rendering not available - cannot display weather symbols")
            logger.error("Install SVG support with: pip install cairosvg pillow")
            logger.error("Or run the setup script: ./bin/setup_svg_rendering.sh")
            return 0

        # Use proper time-based positioning to align with grid
        for idx, symbol_code in symbol_data.items():
            if self._process_single_symbol(
                ax=ax,
                symbol_data=symbol_data,
                idx=idx,
                symbol_code=symbol_code,
                y_position=y_position,
            ):
                symbols_added += 1

        return symbols_added

    def _process_single_symbol(
        self,
        ax: Axes,
        symbol_data: pd.Series,
        idx: Any,
        symbol_code: Any,
        y_position: float,
    ) -> bool:
        """Process a single weather symbol.

        Args:
            ax: matplotlib Axes object
            symbol_data: Series with weather symbol data
            idx: Index of the symbol
            symbol_code: Weather symbol code
            y_position: Y position for symbols

        Returns:
            True if symbol was successfully added, False otherwise
        """
        symbol_info = self.symbol_mapping.get_symbol_info(symbol_code)

        if not symbol_info:
            logger.warning("No symbol info found for code: %s", symbol_code)
            return False

        # Get the actual position in the data array (time index)
        time_position = self._calculate_time_position(symbol_data, idx)
        logger.debug(
            "Rendering SVG symbol at time position %d: code=%s",
            time_position,
            symbol_code,
        )

        # Always use SVG icons - no fallbacks
        svg_path = self.icon_manager.get_icon_path(symbol_code)
        logger.debug("SVG mode: symbol_code=%s, svg_path=%s", symbol_code, svg_path)

        if svg_path and svg_path.exists():
            try:
                logger.debug("Using SVG icon: %s", svg_path)
                self.svg_renderer.render_svg_icon(
                    ax, time_position, y_position, svg_path
                )
                return True
            except (RuntimeError, OSError, ValueError) as e:
                logger.error("Failed to render SVG icon %s: %s", svg_path.name, e)
                return False
        else:
            # Try to download SVG if not available and auto-download is enabled
            if self.config.auto_download_icons and symbol_info.get("svg"):
                try:
                    downloaded_path = self.icon_manager.download_svg_icon(
                        symbol_info["svg"]
                    )
                    if downloaded_path and downloaded_path.exists():
                        logger.debug(
                            "Downloaded and using SVG icon: %s", downloaded_path
                        )
                        self.svg_renderer.render_svg_icon(
                            ax, time_position, y_position, downloaded_path
                        )
                        return True
                    else:
                        logger.warning(
                            "Failed to download SVG for %s - symbol skipped",
                            symbol_code,
                        )
                        return False
                except (
                    RuntimeError,
                    OSError,
                    ValueError,
                ) as e:
                    logger.error(
                        "Failed to download/render SVG for %s: %s", symbol_code, e
                    )
                    return False
            else:
                logger.warning(
                    "SVG not found for %s and auto-download disabled - symbol skipped",
                    symbol_code,
                )
                return False

    def _calculate_time_position(self, symbol_data: pd.Series, idx: Any) -> float:
        """Calculate time position for symbol placement.

        Args:
            symbol_data: Series with weather symbol data
            idx: Index of the symbol

        Returns:
            Time position for symbol placement
        """
        loc_result = symbol_data.index.get_loc(idx)
        if isinstance(loc_result, slice):
            time_position = (
                float(loc_result.start) if loc_result.start is not None else 0.0
            )
        elif isinstance(loc_result, (int, float)):
            time_position = float(loc_result)
        else:
            time_position = 0.0
        return time_position

    def get_symbol_statistics(self, data: pd.DataFrame) -> dict:
        """Get statistics about weather symbols in the data.

        Args:
            data: DataFrame with weather symbol data

        Returns:
            Dictionary with symbol statistics
        """
        if "weather_symbol" not in data.columns:
            return {"total_symbols": 0, "unique_symbols": 0, "symbol_counts": {}}

        symbol_data = data["weather_symbol"].dropna()

        if symbol_data.empty:
            return {"total_symbols": 0, "unique_symbols": 0, "symbol_counts": {}}

        return self.symbol_mapping.get_symbol_statistics(symbol_data)
