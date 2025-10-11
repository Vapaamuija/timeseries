"""
Parameter plotting implementation for meteogram.

This module provides parameter plotting functionality following the Single Responsibility Principle.
"""

import logging
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from matplotlib.axes import Axes

from .components import FormattingUtils
from .interfaces import PlotConfig
from .legend_interfaces import ParameterPlotter

logger = logging.getLogger(__name__)


class MeteogramParameterPlotter(ParameterPlotter):
    """Meteogram parameter plotter implementation."""

    def __init__(self, config: PlotConfig):
        """Initialize meteogram parameter plotter.

        Args:
            config: Plot configuration
        """
        super().__init__(config)
        self.time_interval = 1  # Time labels every 1 hour

        # Store axis references for grid calculations
        self._wind_axis: Optional[Axes] = None
        self._pressure_axis: Optional[Axes] = None
        self._precip_axis: Optional[Axes] = None

    def plot_main_parameters(self, ax: Axes, data: pd.DataFrame) -> None:
        """Plot main weather parameters (temperature, pressure, precipitation, dew point, wind speed)."""
        time_indices = np.arange(len(data))

        # Plot temperature and dew point (primary axis)
        self.plot_temperature_and_dew_point(ax, data, time_indices)

        # Plot wind speed (secondary axis)
        ax_wind = None
        if "wind_speed" in data.columns:
            ax_wind = self.plot_wind_speed(ax, data, time_indices)

        # Plot pressure (secondary axis)
        if "pressure" in data.columns:
            self.plot_pressure(ax, data, time_indices, ax_wind)

        # Plot precipitation (overlay bars)
        if "precipitation" in data.columns:
            self.plot_precipitation(ax, data, time_indices)

        # Format main axis
        self._format_main_axis(ax, data)

    def plot_temperature_and_dew_point(
        self, ax: Axes, data: pd.DataFrame, time_indices: np.ndarray
    ) -> Optional[Axes]:
        """Plot temperature and dew point on primary axis."""
        effective_colors = self.config.get_effective_colors()
        font_config: Dict[str, Any] = getattr(self.config, "fonts", {}) or {}
        label_fontsize = font_config.get("label_size", 10)
        text_color = effective_colors.get("text", "#333333")

        # Temperature (primary y-axis) with conditional coloring
        if "temperature" in data.columns:
            temp_data = data["temperature"]
            self._plot_temperature_segments(ax, time_indices, temp_data)

            # Configure temperature axis
            ax.set_ylabel("", color=text_color, fontsize=label_fontsize)
            ax.tick_params(axis="y", labelcolor=text_color, labelleft=False)

            # Calculate temperature range including dew point if available
            temp_min, temp_max = data["temperature"].min(), data["temperature"].max()
            if "dew_point" in data.columns:
                dew_min, dew_max = data["dew_point"].min(), data["dew_point"].max()
                temp_min = min(temp_min, dew_min)
                temp_max = max(temp_max, dew_max)

            margin = max(2, (temp_max - temp_min) * 0.1)
            ax.set_ylim(temp_min - margin, temp_max + margin)

            # Add horizontal reference line at zero
            grid_color = effective_colors.get("grid", "#e0e0e0")
            colors_config: Dict[str, Any] = getattr(self.config, "colors", {}) or {}
            grid_alpha = colors_config.get("grid_alpha", 0.5)
            ax.axhline(
                y=0, color=grid_color, linestyle="--", alpha=grid_alpha, linewidth=0.8
            )

        # Dew point (same y-axis as temperature)
        if "dew_point" in data.columns:
            dew_point_color = effective_colors.get("dew_point", "#17becf")
            ax.plot(
                time_indices,
                data["dew_point"],
                color=dew_point_color,
                linewidth=1.5,
                linestyle="--",
                label="Dew Point",
                alpha=0.8,
            )

        return None  # No secondary axis created

    def plot_wind_speed(
        self, ax: Axes, data: pd.DataFrame, time_indices: np.ndarray
    ) -> Axes:
        """Plot wind speed on secondary axis."""
        ax_wind = ax.twinx()
        wind_data = data["wind_speed"]
        effective_colors = self.config.get_effective_colors()
        wind_color = effective_colors.get("wind", "#ff7f0e")
        font_config: Dict[str, Any] = getattr(self.config, "fonts", {}) or {}
        label_fontsize = font_config.get("label_size", 10)

        ax_wind.plot(
            time_indices,
            wind_data,
            color=wind_color,
            linewidth=2,
            label="Wind Speed",
            alpha=0.8,
        )

        # Configure wind axis
        ax_wind.set_ylabel("", color=wind_color, fontsize=label_fontsize)
        ax_wind.tick_params(axis="y", labelcolor=wind_color, labelright=False)

        # Set wind speed range
        wind_min, wind_max = wind_data.min(), wind_data.max()
        margin = max(1, (wind_max - wind_min) * 0.1)
        ax_wind.set_ylim(max(0, wind_min - margin), wind_max + margin)

        # Position wind axis on the right side
        ax_wind.spines["right"].set_position(("outward", 0))
        ax_wind.spines["right"].set_visible(True)

        # Store wind axis for legend positioning
        self._wind_axis = ax_wind
        return ax_wind

    def plot_pressure(
        self,
        ax: Axes,
        data: pd.DataFrame,
        time_indices: np.ndarray,
        ax_wind: Optional[Axes],
    ) -> None:
        """Plot pressure on secondary axis."""
        ax_pressure = ax.twinx()

        # Position pressure axis further to the right if wind speed exists
        if ax_wind is not None:
            ax_pressure.spines["right"].set_position(("outward", 60))

        effective_colors = self.config.get_effective_colors()
        pressure_color = effective_colors.get("pressure", "#2ca02c")

        ax_pressure.plot(
            time_indices,
            data["pressure"],
            color=pressure_color,
            linewidth=1.5,
            label="Pressure",
        )

        # Configure pressure axis
        ax_pressure.set_ylabel("", color=pressure_color, fontsize=10)
        ax_pressure.tick_params(axis="y", labelcolor=pressure_color, labelright=False)

        # Set pressure range
        pressure_min, pressure_max = data["pressure"].min(), data["pressure"].max()
        margin = max(5, (pressure_max - pressure_min) * 0.1)
        ax_pressure.set_ylim(pressure_min - margin, pressure_max + margin)

        # Store pressure axis for legend positioning
        self._pressure_axis = ax_pressure

    def plot_precipitation(
        self, ax: Axes, data: pd.DataFrame, time_indices: np.ndarray
    ) -> None:
        """Plot precipitation as bars."""
        ax_precip = ax.twinx()
        precip_data = np.maximum(data["precipitation"], 0)

        # Get precipitation styling
        effective_colors = self.config.get_effective_colors()
        precip_color = effective_colors.get("precipitation", "#1f77b4")

        precip_config = {}
        if hasattr(self.config, "variable_config") and self.config.variable_config:
            precip_config = self.config.variable_config.get("precipitation", {})
        alpha = precip_config.get("alpha", 0.7)

        # Create edge color (darker version of main color)
        edge_color = self._create_darkened_color(precip_color)

        # Create precipitation bars
        bars = ax_precip.bar(
            time_indices,
            precip_data,
            width=0.6,
            color=precip_color,
            alpha=alpha,
            edgecolor=edge_color,
            linewidth=0.8,
        )

        # Add precipitation value labels
        self._add_precipitation_labels(ax_precip, bars, precip_data, edge_color)

        # Configure precipitation axis
        max_precip = max(5, precip_data.max() * 1.4) if precip_data.max() > 0 else 5
        ax_precip.set_ylim(0, max_precip)
        ax_precip.set_yticks([])
        ax_precip.spines["right"].set_visible(False)
        ax_precip.spines["left"].set_visible(False)
        ax_precip.spines["top"].set_visible(False)
        ax_precip.spines["bottom"].set_visible(False)

        # Store precipitation axis for legend positioning
        self._precip_axis = ax_precip

    def get_axis_references(self) -> Dict[str, Optional[Axes]]:
        """Get axis references for grid calculations.

        Returns:
            Dictionary containing axis references
        """
        return {
            "wind_axis": self._wind_axis,
            "pressure_axis": self._pressure_axis,
            "precip_axis": self._precip_axis,
        }

    def _plot_temperature_segments(
        self, ax: Axes, time_indices: np.ndarray, temp_data: pd.Series
    ) -> None:
        """Plot temperature as continuous segments with proper color transitions.

        This method ensures the temperature line is continuous even when crossing zero,
        by plotting overlapping segments at transition points.

        Args:
            ax: matplotlib Axes object
            time_indices: Array of time indices for x-axis
            temp_data: Temperature data series
        """
        if len(temp_data) == 0:
            return

        # Convert to numpy arrays for easier processing
        temps = temp_data.values
        indices = time_indices

        # Find segments of continuous color
        segments = []
        current_segment = {"start": 0, "end": 0, "above_zero": temps[0] >= 0}

        for i in range(1, len(temps)):
            is_above_zero = temps[i] >= 0

            if is_above_zero == current_segment["above_zero"]:
                # Continue current segment
                current_segment["end"] = i
            else:
                # Finish current segment and start new one
                segments.append(current_segment)
                current_segment = {
                    "start": i - 1,
                    "end": i,
                    "above_zero": is_above_zero,
                }

        # Add the final segment
        segments.append(current_segment)

        # Plot each segment with appropriate color
        has_above_zero = False
        has_below_zero = False

        for segment in segments:
            start_idx = segment["start"]
            end_idx = segment["end"]
            is_above_zero = segment["above_zero"]

            # Get the data for this segment
            segment_indices = indices[start_idx : end_idx + 1]
            segment_temps = temps[start_idx : end_idx + 1]

            # Choose color and label
            colors = self.config.get_effective_colors()
            if is_above_zero:
                color = colors["temperature_above"]
                label = "Temperature ≥0°C" if not has_above_zero else None
                has_above_zero = True
            else:
                color = colors["temperature_below"]
                label = "Temperature <0°C" if not has_below_zero else None
                has_below_zero = True

            # Plot the segment
            ax.plot(
                segment_indices,
                segment_temps.tolist(),
                color=color,
                linewidth=2,
                label=label,
            )

    def _create_darkened_color(self, color: str) -> str:
        """Create a darkened version of a hex color."""
        if color.startswith("#"):
            hex_color = color[1:]
            rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
            darkened_rgb = tuple(max(0, int(c * 0.7)) for c in rgb)
            return f"#{darkened_rgb[0]:02x}{darkened_rgb[1]:02x}{darkened_rgb[2]:02x}"
        return color

    def _add_precipitation_labels(
        self, ax_precip: Axes, bars: Any, precip_data: np.ndarray, edge_color: str
    ) -> None:
        """Add value labels to precipitation bars."""
        font_config: Dict[str, Any] = getattr(self.config, "fonts", {}) or {}
        label_fontsize = font_config.get("annotation_size", 8)
        label_fontweight = font_config.get("weights", {}).get("annotation", "bold")

        for bar, value in zip(bars, precip_data):
            if value > 0.1:  # Only label significant precipitation
                ax_precip.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(0.1, precip_data.max() * 0.02),
                    f"{value:.1f}",
                    ha="center",
                    va="bottom",
                    fontsize=label_fontsize,
                    color=edge_color,
                    fontweight=label_fontweight,
                )

    def _format_main_axis(self, ax: Axes, data: pd.DataFrame) -> None:
        """Format the main axis with padding and time labels."""
        padding_config = self.config.get_effective_time_axis_padding()
        if padding_config:
            start_limit, end_limit = FormattingUtils.calculate_padded_xlim(
                data, padding_config
            )
            ax.set_xlim(start_limit, end_limit)
        else:
            ax.set_xlim(0, len(data) - 1)

        # Add time labels with padding configuration
        FormattingUtils.add_time_labels(ax, data, self.time_interval, padding_config)
