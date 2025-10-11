"""
Layout formatting implementation for meteogram.

This module provides layout formatting functionality following the Single Responsibility Principle.
"""

import logging
from typing import Any, Dict, Optional

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .components import FormattingUtils
from .interfaces import PlotConfig

# LayoutFormatter interface not needed for this implementation

logger = logging.getLogger(__name__)


class MeteogramLayoutFormatter:
    """Meteogram layout formatter implementation."""

    def __init__(self, config: PlotConfig):
        """Initialize meteogram layout formatter.

        Args:
            config: Plot configuration
        """
        self.config = config

    def format_meteogram_plot(self, fig: Figure) -> None:
        """Apply meteogram specific formatting."""
        # Set font parameters
        plt.rcParams.update({"font.size": 9})

        # Manual subplot adjustment for proper spacing with room for scale legends on both sides
        plt.subplots_adjust(
            left=0.12,  # Increased space for left scale legends
            right=0.88,  # Increased space for right scale legends
            top=0.93,
            bottom=0.08,
            hspace=0.01,  # Even tighter spacing between panels
            wspace=0,
        )

        # Add signature line at bottom using configuration
        font_config = getattr(self.config, "fonts", {}) or {}
        effective_colors = self.config.get_effective_colors()
        signature_fontsize = font_config.get("annotation_size", 6)
        grid_color = effective_colors.get("grid", "#e0e0e0")
        colors_config = getattr(self.config, "colors", {}) or {}
        grid_alpha = colors_config.get("grid_alpha", 0.4)

        fig.text(
            0.15,
            0.02,
            "/" * 90,
            fontsize=signature_fontsize,
            alpha=grid_alpha,
            family="monospace",
            color=grid_color,
        )

    def plot_hour_labels(
        self, ax: Axes, data: pd.DataFrame, label_padding: Optional[Any] = None
    ) -> None:
        """Plot hour labels at the top of the meteogram."""
        # Get padding configuration
        padding_config = self.config.get_effective_time_axis_padding()
        if padding_config:
            start_limit, end_limit = FormattingUtils.calculate_padded_xlim(
                data, padding_config
            )
            ax.set_xlim(start_limit, end_limit)
        else:
            ax.set_xlim(0, len(data))
        ax.set_ylim(0, 1)
        ax.axis("off")

        if data.empty:
            return

        # Use configurable positioning or defaults
        hour_label_y = 0.3  # Default
        date_label_y = 0.7  # Default

        if label_padding:
            # Handle both dictionary and object-style label padding
            if isinstance(label_padding, dict):
                hour_label_y = label_padding.get("hour_label_y", hour_label_y)
                date_label_y = label_padding.get("date_label_y", date_label_y)
            else:
                hour_label_y = getattr(label_padding, "hour_label_y", hour_label_y)
                date_label_y = getattr(label_padding, "date_label_y", date_label_y)

        # Add hour labels at 1 hour intervals
        # Get font and color configuration
        font_config: Dict[str, Any] = getattr(self.config, "fonts", {}) or {}
        effective_colors = self.config.get_effective_colors()
        label_fontsize = font_config.get("tick_size", 9)
        label_fontweight = font_config.get("weights", {}).get("tick", "normal")
        text_color = effective_colors.get("text", "#333333")

        for i in range(0, len(data), 1):  # Every hour
            if i < len(data):
                hour = data.index[i].strftime("%H")
                ax.text(
                    i,
                    hour_label_y,
                    hour,
                    ha="center",
                    va="center",
                    fontsize=label_fontsize,
                    fontweight=label_fontweight,
                    color=text_color,
                )

        # Add date labels at day boundaries
        current_date = None
        for i, timestamp in enumerate(data.index):
            date = timestamp.date()
            if date != current_date:
                current_date = date
                # Format date like "Tor 09. okt." (Norwegian style)
                day_name = timestamp.strftime("%a")  # Abbreviated day name
                date_str = timestamp.strftime("%d. %b.")  # Day and abbreviated month
                full_date = f"{day_name} {date_str}"
                # Use same font config but with label weight for dates
                date_fontweight = font_config.get("weights", {}).get("label", "bold")
                ax.text(
                    i,
                    date_label_y,
                    full_date,
                    ha="left",
                    va="center",
                    fontsize=label_fontsize,
                    fontweight=date_fontweight,
                    color=text_color,
                )

    def plot_time_axis(self, ax: Axes, data: pd.DataFrame) -> None:
        """Plot time axis with date labels."""
        # Get padding configuration and set x-limits
        padding_config = self.config.get_effective_time_axis_padding()
        if padding_config:
            start_limit, end_limit = FormattingUtils.calculate_padded_xlim(
                data, padding_config
            )
            ax.set_xlim(start_limit, end_limit)
        else:
            ax.set_xlim(0, len(data))
        ax.set_ylim(0, 1)
        ax.axis("off")

        if data.empty:
            return

        # Add date labels at midnight positions
        current_date = None
        for i, timestamp in enumerate(data.index):
            date = timestamp.date()
            if date != current_date:
                current_date = date
                date_str = date.strftime("%Y-%m-%d")
                ax.text(
                    i,
                    0.5,
                    date_str,
                    ha="left",
                    va="center",
                    fontsize=9,
                    fontweight="normal",
                )

    def plot_separator(self, ax: Axes) -> None:
        """Plot separator panel."""
        ax.axis("off")

    def plot_weather_symbols(
        self, ax: Axes, data: pd.DataFrame, symbol_renderer: Any
    ) -> None:
        """Plot weather symbols after cloud coverage section."""
        # Get padding configuration and set x-limits
        padding_config = self.config.get_effective_time_axis_padding()
        if padding_config:
            start_limit, end_limit = FormattingUtils.calculate_padded_xlim(
                data, padding_config
            )
            ax.set_xlim(start_limit, end_limit)
        else:
            ax.set_xlim(0, len(data))  # Match other panels' x-limits
        ax.set_ylim(0, 1)
        ax.axis("off")

        if "weather_symbol" in data.columns:
            # Position symbols in the center of the dedicated symbol panel
            # Use time indices to align with other panels
            symbols_added = symbol_renderer.add_symbols_to_plot(
                ax,
                data,
                y_position=0.5,  # Center of the symbol panel
                symbol_type=self.config.symbol_type,
            )
            logger.debug("Added %d weather symbols to meteogram", symbols_added)
        else:
            logger.warning("No weather_symbol column found in data")
