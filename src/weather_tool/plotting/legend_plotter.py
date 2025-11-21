"""
Legend plotting implementation for meteogram.

This module provides legend plotting functionality following the Single Responsibility Principle.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .interfaces import PlotConfig
from .legend_interfaces import SideLegendPlotter

logger = logging.getLogger(__name__)


class MeteogramLegendPlotter(SideLegendPlotter):
    """Meteogram legend plotter implementation."""

    def __init__(self, config: PlotConfig):
        """Initialize meteogram legend plotter.

        Args:
            config: Plot configuration
        """
        super().__init__(config)
        self._shared_grid_values: Dict[str, Dict[str, Any]] = {}

    def add_legends(
        self,
        fig: Figure,
        ax: Axes,
        data: pd.DataFrame,
        label_padding: Optional[Any] = None,
    ) -> None:
        """Add legends to the plot.

        Args:
            fig: matplotlib Figure object
            ax: Main parameters axis
            data: Weather data DataFrame
            label_padding: Label padding configuration
        """
        # Add left-side legends for temperature and wind speed
        self._add_left_side_legends(ax, data, label_padding)

        # Add right-side legends for pressure and precipitation
        self._add_right_side_legends(ax, data, label_padding)

    def get_positioning(
        self, label_padding: Optional[Any] = None
    ) -> Tuple[float, float]:
        """Get positioning configuration for side legends.

        Args:
            label_padding: Label padding configuration

        Returns:
            Tuple of (legend_x, unit_offset)
        """
        legend_x = 0.02  # Default left side position
        unit_offset = 0.05  # Default offset for unit labels

        if label_padding:
            # Handle both dictionary and object-style label padding
            if isinstance(label_padding, dict):
                legend_x = label_padding.get("left_legend_x", legend_x)
                unit_offset = label_padding.get("left_unit_offset", unit_offset)
            else:
                legend_x = getattr(label_padding, "left_legend_x", legend_x)
                unit_offset = getattr(label_padding, "left_unit_offset", unit_offset)

        return legend_x, unit_offset

    def add_variable_legend(
        self, fig: Figure, bbox: Any, legend_x: float, variable_name: str
    ) -> None:
        """Add legend for a specific variable.

        Args:
            fig: matplotlib Figure object
            bbox: Axis bounding box
            legend_x: X position for legend
            variable_name: Name of the variable to add legend for
        """
        if variable_name == "temperature":
            self._add_temperature_legend(fig, bbox, legend_x)
        elif variable_name == "wind_speed":
            self._add_wind_speed_legend(fig, bbox, legend_x)
        elif variable_name == "pressure":
            self._add_pressure_legend(fig, bbox, legend_x)
        elif variable_name == "precipitation":
            self._add_precipitation_legend(fig, bbox, legend_x)

    def set_shared_grid_values(
        self, shared_grid_values: Dict[str, Dict[str, Any]]
    ) -> None:
        """Set shared grid values for legend positioning.

        Args:
            shared_grid_values: Dictionary containing grid values for each variable
        """
        self._shared_grid_values = shared_grid_values

    def _add_left_side_legends(
        self, ax: Axes, data: pd.DataFrame, label_padding: Optional[Any] = None
    ) -> None:
        """Add legends on the left side for temperature and wind speed.

        Args:
            ax: Main parameters axis
            data: Weather data DataFrame
            label_padding: LabelPaddingConfig for custom positioning
        """
        fig = ax.get_figure()
        if fig is not None:
            fig.canvas.draw()  # Force drawing to get final positions
        bbox = ax.get_position()

        # Get positioning configuration
        legend_x, unit_offset = self._get_left_legend_positioning(label_padding)
        
        # Calculate exact positions
        # Standard Meteogram: Wind (outer) -> Temperature (inner)
        wind_x = legend_x
        temp_x = legend_x + unit_offset

        # Add wind speed legend if data exists (Outer column)
        if "wind_speed" in data.columns and self._shared_grid_values:
            self._add_wind_speed_legend(fig, bbox, wind_x)

        # Add temperature legend if data exists (Inner column)
        if "temperature" in data.columns and self._shared_grid_values:
            self._add_temperature_legend(fig, bbox, temp_x)

    def _get_left_legend_positioning(
        self, label_padding: Optional[Any]
    ) -> Tuple[float, float]:
        """Get positioning configuration for left side legends."""
        legend_x = 0.04  # Default left side position
        unit_offset = 0.05  # Default offset for unit labels

        if label_padding:
            # Handle both dictionary and object-style label padding
            if isinstance(label_padding, dict):
                legend_x = label_padding.get("left_legend_x", legend_x)
                unit_offset = label_padding.get("left_unit_offset", unit_offset)
            else:
                legend_x = getattr(label_padding, "left_legend_x", legend_x)
                unit_offset = getattr(label_padding, "left_unit_offset", unit_offset)

        return legend_x, unit_offset

    def _add_temperature_legend(self, fig: Any, bbox: Any, legend_x: float) -> None:
        """Add temperature legend to the left side."""
        colors = self.config.get_effective_colors()
        temp_info = self._shared_grid_values.get("temperature", {})

        if not (temp_info and "values" in temp_info):
            return

        temp_values: List[float] = temp_info["values"]
        temp_min: float = temp_info["axis_min"]
        temp_max: float = temp_info["axis_max"]
        temp_range = temp_max - temp_min

        # Add temperature scale values
        for temp_val in temp_values:
            y_pos_axis = (temp_val - temp_min) / temp_range
            y_pos_fig = bbox.y0 + y_pos_axis * bbox.height

            if fig is not None:
                fig.text(
                    legend_x,
                    y_pos_fig,
                    f"{int(temp_val)}°",
                    fontsize=9,
                    va="center",
                    ha="left",
                    color=colors["temperature_above"],
                    fontweight="normal",
                    transform=fig.transFigure,
                )

        # Add temperature unit label
        if temp_values:
            highest_temp = max(temp_values)
            y_pos_axis = (highest_temp - temp_min) / temp_range
            y_pos_fig = bbox.y0 + y_pos_axis * bbox.height
            temp_label_y = y_pos_fig + 0.02

            if fig is not None:
                fig.text(
                    legend_x,
                    temp_label_y,
                    "°C",
                    fontsize=10,
                    va="center",
                    ha="left",
                    color=colors["temperature_above"],
                    fontweight="bold",
                    transform=fig.transFigure,
                )
                
                # Add thermometer symbol
                fig.text(
                    legend_x,
                    temp_label_y + 0.015,
                    "🌡",  # Thermometer
                    fontsize=14,
                    va="center",
                    ha="left",
                    color=colors["temperature_above"],
                    transform=fig.transFigure,
                )

    def _add_wind_speed_legend(
        self, fig: Any, bbox: Any, legend_x: float
    ) -> None:
        """Add wind speed legend to the left side."""
        wind_legend_x = legend_x
        wind_info = self._shared_grid_values.get("wind_speed", {})

        if not (wind_info and "values" in wind_info):
            return

        wind_values: List[float] = wind_info["values"]
        wind_min: float = wind_info["axis_min"]
        wind_max: float = wind_info["axis_max"]
        wind_range = wind_max - wind_min

        # Get styling configuration
        effective_colors = self.config.get_effective_colors()
        wind_color = effective_colors.get("wind", "#ff7f0e")
        font_config: Dict[str, Any] = getattr(self.config, "fonts", {}) or {}
        legend_fontsize = font_config.get("tick_size", 9)
        legend_fontweight = font_config.get("weights", {}).get("tick", "normal")

        # Add wind speed scale values
        for wind_val in wind_values:
            y_pos_axis = (wind_val - wind_min) / wind_range
            y_pos_fig = bbox.y0 + y_pos_axis * bbox.height

            if fig is not None:
                fig.text(
                    wind_legend_x,
                    y_pos_fig,
                    f"{int(wind_val)}",
                    fontsize=legend_fontsize,
                    va="center",
                    ha="left",
                    color=wind_color,
                    fontweight=legend_fontweight,
                    transform=fig.transFigure,
                )

        # Add wind speed unit label
        if wind_values:
            highest_wind = max(wind_values)
            y_pos_axis = (highest_wind - wind_min) / wind_range
            y_pos_fig = bbox.y0 + y_pos_axis * bbox.height
            wind_label_y = y_pos_fig + 0.02

            # Get unit from variable config or use default
            wind_config = {}
            if hasattr(self.config, "variable_config") and self.config.variable_config:
                wind_config = self.config.variable_config.get("wind_speed", {})
            unit_label = wind_config.get("unit", "m/s")

            if fig is not None:
                fig.text(
                    wind_legend_x,
                    wind_label_y,
                    unit_label,
                    fontsize=10,
                    va="center",
                    ha="left",
                    color=wind_color,
                    fontweight="bold",
                    transform=fig.transFigure,
                )
                
                # Add wind symbol
                fig.text(
                    wind_legend_x,
                    wind_label_y + 0.015,
                    "💨",  # Wind
                    fontsize=14,
                    va="center",
                    ha="left",
                    color=wind_color,
                    transform=fig.transFigure,
                )

    def _add_right_side_legends(
        self, ax: Axes, data: pd.DataFrame, label_padding: Optional[Any] = None
    ) -> None:
        """Add legends on the right side for pressure and precipitation.

        Args:
            ax: Main parameters axis
            data: Weather data DataFrame
            label_padding: LabelPaddingConfig for custom positioning
        """
        fig = ax.get_figure()
        if fig is not None:
            fig.canvas.draw()  # Force drawing to get final positions
        bbox = ax.get_position()

        # Get positioning configuration
        legend_x, unit_offset = self._get_right_legend_positioning(label_padding)

        # Calculate exact positions
        # Standard Meteogram: Pressure (inner) -> Precipitation (outer)
        precip_x = legend_x
        pressure_x = legend_x - unit_offset

        # Add precipitation legend if data exists (Outer column)
        if "precipitation" in data.columns and self._shared_grid_values:
            self._add_precipitation_legend(fig, bbox, precip_x)

        # Add pressure legend if data exists (Inner column)
        if "pressure" in data.columns and self._shared_grid_values:
            self._add_pressure_legend(fig, bbox, pressure_x)

    def _get_right_legend_positioning(
        self, label_padding: Optional[Any]
    ) -> Tuple[float, float]:
        """Get positioning configuration for right side legends."""
        legend_x = 0.96  # Default right side position
        unit_offset = 0.05  # Default offset for unit labels

        if label_padding:
            # Handle both dictionary and object-style label padding
            if isinstance(label_padding, dict):
                legend_x = label_padding.get("right_legend_x", legend_x)
                unit_offset = label_padding.get("right_unit_offset", unit_offset)
            else:
                legend_x = getattr(label_padding, "right_legend_x", legend_x)
                unit_offset = getattr(label_padding, "right_unit_offset", unit_offset)

        return legend_x, unit_offset

    def _add_precipitation_legend(self, fig: Any, bbox: Any, legend_x: float) -> None:
        """Add precipitation legend to the right side."""
        precip_info = self._shared_grid_values.get("precipitation", {})

        if not (precip_info and "values" in precip_info):
            return

        precip_values: List[float] = precip_info["values"]
        precip_min: float = precip_info["axis_min"]
        precip_max: float = precip_info["axis_max"]
        precip_range = precip_max - precip_min

        # Get styling configuration
        effective_colors = self.config.get_effective_colors()
        precip_color = effective_colors.get("precipitation", "#1f77b4")
        font_config: Dict[str, Any] = getattr(self.config, "fonts", {}) or {}
        legend_fontsize = font_config.get("tick_size", 9)
        legend_fontweight = font_config.get("weights", {}).get("tick", "normal")

        # Add precipitation scale values
        for precip_val in precip_values:
            y_pos_axis = (precip_val - precip_min) / precip_range
            y_pos_fig = bbox.y0 + y_pos_axis * bbox.height

            if fig is not None:
                fig.text(
                    legend_x,
                    y_pos_fig,
                    f"{int(precip_val)}",
                    fontsize=legend_fontsize,
                    va="center",
                    ha="right",
                    color=precip_color,
                    fontweight=legend_fontweight,
                    transform=fig.transFigure,
                )

        # Add precipitation unit label
        if precip_values:
            highest_precip = max(precip_values)
            y_pos_axis = (highest_precip - precip_min) / precip_range
            y_pos_fig = bbox.y0 + y_pos_axis * bbox.height
            precip_label_y = y_pos_fig + 0.02

            # Get unit from variable config or use default
            precip_config = {}
            if hasattr(self.config, "variable_config") and self.config.variable_config:
                precip_config = self.config.variable_config.get("precipitation", {})
            unit_label = precip_config.get("unit", "mm")

            if fig is not None:
                fig.text(
                    legend_x,
                    precip_label_y,
                    unit_label,
                    fontsize=10,
                    va="center",
                    ha="right",
                    color=precip_color,
                    fontweight="bold",
                    transform=fig.transFigure,
                )
                
                # Add rain symbol
                fig.text(
                    legend_x,
                    precip_label_y + 0.015,
                    "☂",  # Umbrella/Rain
                    fontsize=14,
                    va="center",
                    ha="right",
                    color=precip_color,
                    transform=fig.transFigure,
                )

    def _add_pressure_legend(
        self, fig: Any, bbox: Any, legend_x: float
    ) -> None:
        """Add pressure legend to the right side."""
        pressure_legend_x = legend_x
        pressure_info = self._shared_grid_values.get("pressure", {})

        if not (pressure_info and "values" in pressure_info):
            return

        pressure_values: List[float] = pressure_info["values"]
        pressure_min: float = pressure_info["axis_min"]
        pressure_max: float = pressure_info["axis_max"]
        pressure_range = pressure_max - pressure_min

        # Get styling configuration
        effective_colors = self.config.get_effective_colors()
        pressure_color = effective_colors.get("pressure", "#2ca02c")
        font_config: Dict[str, Any] = getattr(self.config, "fonts", {}) or {}
        legend_fontsize = font_config.get("tick_size", 9)
        legend_fontweight = font_config.get("weights", {}).get("tick", "normal")

        # Add pressure scale values
        for pressure_val in pressure_values:
            y_pos_axis = (pressure_val - pressure_min) / pressure_range
            y_pos_fig = bbox.y0 + y_pos_axis * bbox.height

            if fig is not None:
                fig.text(
                    pressure_legend_x,
                    y_pos_fig,
                    f"{int(pressure_val)}",
                    fontsize=legend_fontsize,
                    va="center",
                    ha="right",
                    color=pressure_color,
                    fontweight=legend_fontweight,
                    transform=fig.transFigure,
                )

        # Add pressure unit label
        if pressure_values:
            highest_pressure = max(pressure_values)
            y_pos_axis = (highest_pressure - pressure_min) / pressure_range
            y_pos_fig = bbox.y0 + y_pos_axis * bbox.height
            pressure_label_y = y_pos_fig + 0.02

            # Get unit from variable config or use default
            pressure_config = {}
            if hasattr(self.config, "variable_config") and self.config.variable_config:
                pressure_config = self.config.variable_config.get("pressure", {})
            unit_label = pressure_config.get("unit", "hPa")

            if fig is not None:
                fig.text(
                    pressure_legend_x,
                    pressure_label_y,
                    unit_label,
                    fontsize=10,
                    va="center",
                    ha="right",
                    color=pressure_color,
                    fontweight="bold",
                    transform=fig.transFigure,
                )
                
                # Add pressure symbol
                fig.text(
                    pressure_legend_x,
                    pressure_label_y + 0.015,
                    "⏱",  # Stopwatch/Gauge approximation
                    fontsize=14,
                    va="center",
                    ha="right",
                    color=pressure_color,
                    transform=fig.transFigure,
                )
