"""
Grid management implementation for meteogram.

This module provides grid management functionality following the Single Responsibility Principle.
"""

import logging
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from matplotlib.axes import Axes

from .components import FormattingUtils
from .interfaces import PlotConfig
from .legend_interfaces import GridManager

logger = logging.getLogger(__name__)


class MeteogramGridManager(GridManager):
    """Meteogram grid manager implementation."""

    def __init__(self, config: PlotConfig):
        """Initialize meteogram grid manager.

        Args:
            config: Plot configuration
        """
        super().__init__(config)
        self.grid_interval = 1  # Grid every 1 hour
        self._shared_grid_values: Dict[str, Dict[str, Any]] = {}

        # Initialize axis references for grid calculations
        self._wind_axis: Optional[Axes] = None
        self._pressure_axis: Optional[Axes] = None
        self._precip_axis: Optional[Axes] = None

    def apply_unified_grid(self, axes: List[Axes], data: pd.DataFrame) -> None:
        """Apply unified grid lines to all panels for consistent alignment.

        This ensures that all panels (hour labels, weather symbols, cloud layers,
        main parameters, wind section, etc.) share the same vertical grid lines,
        making it easy to visually align data across different panels at the same hour.

        Args:
            axes: List of all axes in the meteogram
            data: Weather data DataFrame
        """
        if data.empty:
            return

        data_length = len(data)

        # Detect day boundaries for thicker grid lines
        day_boundaries = self.detect_day_boundaries(data)

        # Get padding configuration
        padding_config = self.config.get_effective_time_axis_padding()

        # Calculate x-limits with padding
        if padding_config:
            start_limit, end_limit = FormattingUtils.calculate_padded_xlim(
                data, padding_config
            )
        else:
            start_limit, end_limit = 0, data_length - 1

        # Apply the same grid to ALL panels
        for i, ax in enumerate(axes):
            # Only add grid to axes that are not turned off
            if ax.get_visible():
                # Set consistent x-limits for all panels with padding
                ax.set_xlim(start_limit, end_limit)

                # Add vertical grid lines at 1-hour intervals
                if i == 0:  # Hour labels panel - extend grid lines to almost the bottom
                    # For hour panel, make grid lines extend from y=0.1 to y=0.0 (just under the hours)
                    self._add_custom_vertical_grid(
                        ax,
                        data_length,
                        y_start=0.1,
                        y_end=0.0,
                        day_boundaries=day_boundaries,
                    )
                else:
                    # For all other panels, use full height grid lines
                    # Get grid colors from configuration
                    effective_colors = self.config.get_effective_colors()
                    grid_color = effective_colors.get("grid", "#e0e0e0")
                    colors_config = getattr(self.config, "colors", {}) or {}
                    grid_alpha = colors_config.get("grid_alpha", 0.3)

                    FormattingUtils.add_vertical_grid(
                        ax,
                        data_length,
                        grid_line_interval=self.grid_interval,
                        grid_line_color=grid_color,
                        grid_transparency=grid_alpha,
                        day_boundary_indices=day_boundaries,
                    )

                # Skip automatic horizontal grid lines for main parameters panel (index 7)
                # The horizontal grid lines will be drawn by the legend functions to ensure alignment
                if (
                    i > 0 and i != 7
                ):  # Skip hour labels panel (index 0) and main parameters panel (index 7)
                    FormattingUtils.add_horizontal_grid(
                        ax,
                        color=grid_color,
                        alpha=grid_alpha,
                        linestyle=":",
                        linewidth=0.5,
                    )

    def calculate_shared_grid_system(self, ax_main: Axes, data: pd.DataFrame) -> None:
        """Calculate shared grid lines for all variables and store them for legend alignment.

        Args:
            ax_main: Main parameters axis (temperature axis)
            data: Weather data DataFrame
        """
        # Temperature grid (primary axis)
        if "temperature" in data.columns:
            temp_min, temp_max = ax_main.get_ylim()
            # Use more grid lines for temperature to match reference density (approx 1 degree steps)
            temp_grid: List[float] = FormattingUtils.calculate_nice_grid_values(
                temp_min, temp_max, maximum_grid_lines=10
            )
            self._shared_grid_values["temperature"] = {
                "values": temp_grid,
                "axis_min": temp_min,
                "axis_max": temp_max,
                "axis": ax_main,
            }

        # Wind speed grid (if wind axis exists)
        if (
            "wind_speed" in data.columns
            and hasattr(self, "_wind_axis")
            and self._wind_axis is not None
        ):
            wind_min, wind_max = self._wind_axis.get_ylim()
            # Wind speed usually in steps of 2 m/s
            wind_grid: List[float] = FormattingUtils.calculate_nice_grid_values(
                wind_min, wind_max, maximum_grid_lines=10
            )
            self._shared_grid_values["wind_speed"] = {
                "values": wind_grid,
                "axis_min": wind_min,
                "axis_max": wind_max,
                "axis": self._wind_axis,
            }

        # Pressure grid (if pressure axis exists)
        if (
            "pressure" in data.columns
            and hasattr(self, "_pressure_axis")
            and self._pressure_axis is not None
        ):
            pressure_min, pressure_max = self._pressure_axis.get_ylim()
            # Pressure usually in steps of 5 or 10 hPa
            pressure_grid: List[float] = FormattingUtils.calculate_nice_grid_values(
                pressure_min, pressure_max, maximum_grid_lines=10
            )
            self._shared_grid_values["pressure"] = {
                "values": pressure_grid,
                "axis_min": pressure_min,
                "axis_max": pressure_max,
                "axis": self._pressure_axis,
            }

        # Precipitation grid (if precipitation axis exists)
        if (
            "precipitation" in data.columns
            and hasattr(self, "_precip_axis")
            and self._precip_axis is not None
        ):
            precip_min, precip_max = self._precip_axis.get_ylim()
            # Precipitation usually in steps of 1 or 2 mm
            precip_grid: List[float] = FormattingUtils.calculate_nice_grid_values(
                precip_min, precip_max, maximum_grid_lines=10
            )
            # Filter out negative values for precipitation
            precip_grid = [val for val in precip_grid if val >= 0]
            self._shared_grid_values["precipitation"] = {
                "values": precip_grid,
                "axis_min": precip_min,
                "axis_max": precip_max,
                "axis": self._precip_axis,
            }

        # Dew point uses the same axis as temperature
        if "dew_point" in data.columns:
            self._shared_grid_values["dew_point"] = self._shared_grid_values.get(
                "temperature", {}
            )

        # Humidity would use the same system if it exists
        if "humidity" in data.columns:
            # Humidity typically ranges 0-100%, so we can create a standard grid
            humidity_grid: List[float] = [0, 20, 40, 60, 80, 100]
            self._shared_grid_values["humidity"] = {
                "values": humidity_grid,
                "axis_min": 0,
                "axis_max": 100,
                "axis": None,  # Would need its own axis
            }

    def draw_shared_horizontal_grid_lines(self) -> None:
        """Draw shared horizontal grid lines across the main plot for all variables."""
        if not hasattr(self, "_shared_grid_values"):
            return

        # Get grid styling
        effective_colors = self.config.get_effective_colors()
        grid_color = effective_colors.get("grid", "#e0e0e0")

        # Draw grid lines for temperature (primary axis) - these are the main shared lines
        if "temperature" in self._shared_grid_values:
            temp_info = self._shared_grid_values["temperature"]
            if "values" in temp_info and "axis" in temp_info:
                temp_values: List[float] = temp_info["values"]
                temp_axis = temp_info["axis"]
                for temp_val in temp_values:
                    temp_axis.axhline(
                        y=temp_val,
                        color=grid_color,
                        linestyle="-",
                        alpha=0.3,
                        linewidth=0.5,
                        zorder=0,
                    )

        # Draw grid lines for other axes (lighter/dotted to distinguish)
        for var_name, var_info in self._shared_grid_values.items():
            if var_name != "temperature" and var_info.get("axis") is not None:
                if "values" in var_info:
                    var_values: List[float] = var_info["values"]
                    var_axis = var_info["axis"]
                    for val in var_values:
                        var_axis.axhline(
                            y=val,
                            color=grid_color,
                            linestyle=":",
                            alpha=0.2,
                            linewidth=0.5,
                            zorder=0,
                        )

    def detect_day_boundaries(self, data: pd.DataFrame) -> List[int]:
        """Detect indices where day boundaries occur in the data.

        Args:
            data: Weather data DataFrame with datetime index

        Returns:
            List of indices where day changes occur
        """
        day_boundaries: List[int] = []
        if data.empty:
            return day_boundaries

        current_date = None
        for i, timestamp in enumerate(data.index):
            date = timestamp.date()
            if date != current_date:
                current_date = date
                if i > 0:  # Don't mark the first data point as a boundary
                    day_boundaries.append(i)

        return day_boundaries

    def _add_custom_vertical_grid(
        self,
        ax: Axes,
        data_length: int,
        y_start: float = 1.0,
        y_end: float = 0.0,
        day_boundaries: Optional[List[int]] = None,
    ) -> None:
        """Add custom vertical grid lines with specific y-range.

        Args:
            ax: matplotlib Axes object
            data_length: Length of the data
            y_start: Starting y position (in axis coordinates)
            y_end: Ending y position (in axis coordinates)
            day_boundaries: List of indices where day boundaries occur (for thicker lines)
        """
        day_boundaries = day_boundaries or []

        if data_length > 0:
            # Position grid lines at the center of each hour (0.5, 1.5, 2.5, etc.)
            grid_positions = np.arange(0.5, data_length, self.grid_interval)
            for pos in grid_positions:
                if pos < data_length:
                    # Check if this position is near a day boundary (within 0.5 of any boundary)
                    is_day_boundary = any(
                        abs(pos - boundary) < 0.5 for boundary in day_boundaries
                    )
                    linewidth = 1.5 if is_day_boundary else 0.5

                    ax.plot(
                        [pos, pos],
                        [y_start, y_end],
                        color="gray",
                        linestyle="-",
                        alpha=0.3,
                        linewidth=linewidth,
                    )

    def get_shared_grid_values(self) -> Dict[str, Dict[str, Any]]:
        """Get shared grid values for legend positioning.

        Returns:
            Dictionary containing grid values for each variable
        """
        return self._shared_grid_values

    def set_axis_references(
        self,
        wind_axis: Optional[Axes] = None,
        pressure_axis: Optional[Axes] = None,
        precip_axis: Optional[Axes] = None,
    ) -> None:
        """Set axis references for grid calculations.

        Args:
            wind_axis: Wind speed axis
            pressure_axis: Pressure axis
            precip_axis: Precipitation axis
        """
        self._wind_axis = wind_axis
        self._pressure_axis = pressure_axis
        self._precip_axis = precip_axis
