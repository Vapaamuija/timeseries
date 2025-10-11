"""
Legend plotting interfaces following Interface Segregation Principle.

This module defines clean interfaces for legend functionality,
separating concerns for different types of legends.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple

import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .interfaces import PlotConfig


class LegendPlotter(ABC):
    """Abstract base class for legend plotters."""

    def __init__(self, config: PlotConfig):
        """Initialize legend plotter.

        Args:
            config: Plot configuration
        """
        self.config = config

    @abstractmethod
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
        raise NotImplementedError("Subclasses must implement add_legends")


class SideLegendPlotter(LegendPlotter):
    """Abstract base class for side legend plotters (left/right)."""

    @abstractmethod
    def get_positioning(
        self, label_padding: Optional[Any] = None
    ) -> Tuple[float, float]:
        """Get positioning configuration for side legends.

        Args:
            label_padding: Label padding configuration

        Returns:
            Tuple of (legend_x, unit_offset)
        """
        raise NotImplementedError("Subclasses must implement get_positioning")

    @abstractmethod
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
        raise NotImplementedError("Subclasses must implement add_variable_legend")


class GridManager(ABC):
    """Abstract base class for grid management."""

    def __init__(self, config: PlotConfig):
        """Initialize grid manager.

        Args:
            config: Plot configuration
        """
        self.config = config

    @abstractmethod
    def apply_unified_grid(self, axes: List[Axes], data: pd.DataFrame) -> None:
        """Apply unified grid lines to all panels.

        Args:
            axes: List of all axes in the meteogram
            data: Weather data DataFrame
        """
        raise NotImplementedError("Subclasses must implement apply_unified_grid")

    @abstractmethod
    def calculate_shared_grid_system(self, ax_main: Axes, data: pd.DataFrame) -> None:
        """Calculate shared grid lines for all variables.

        Args:
            ax_main: Main parameters axis
            data: Weather data DataFrame
        """
        raise NotImplementedError(
            "Subclasses must implement calculate_shared_grid_system"
        )

    @abstractmethod
    def draw_shared_horizontal_grid_lines(self) -> None:
        """Draw shared horizontal grid lines across the main plot."""
        raise NotImplementedError(
            "Subclasses must implement draw_shared_horizontal_grid_lines"
        )

    @abstractmethod
    def detect_day_boundaries(self, data: pd.DataFrame) -> List[int]:
        """Detect indices where day boundaries occur.

        Args:
            data: Weather data DataFrame with datetime index

        Returns:
            List of indices where day changes occur
        """
        raise NotImplementedError("Subclasses must implement detect_day_boundaries")


class ParameterPlotter(ABC):
    """Abstract base class for parameter plotting."""

    def __init__(self, config: PlotConfig):
        """Initialize parameter plotter.

        Args:
            config: Plot configuration
        """
        self.config = config

    @abstractmethod
    def plot_main_parameters(self, ax: Axes, data: pd.DataFrame) -> None:
        """Plot main weather parameters.

        Args:
            ax: matplotlib Axes object
            data: Weather data DataFrame
        """
        raise NotImplementedError("Subclasses must implement plot_main_parameters")

    @abstractmethod
    def plot_temperature_and_dew_point(
        self, ax: Axes, data: pd.DataFrame, time_indices: Any
    ) -> Optional[Axes]:
        """Plot temperature and dew point.

        Args:
            ax: matplotlib Axes object
            data: Weather data DataFrame
            time_indices: Time indices for x-axis

        Returns:
            Secondary axis if created, None otherwise
        """
        raise NotImplementedError(
            "Subclasses must implement plot_temperature_and_dew_point"
        )

    @abstractmethod
    def plot_wind_speed(self, ax: Axes, data: pd.DataFrame, time_indices: Any) -> Axes:
        """Plot wind speed on secondary axis.

        Args:
            ax: matplotlib Axes object
            data: Weather data DataFrame
            time_indices: Time indices for x-axis

        Returns:
            Wind speed axis
        """
        raise NotImplementedError("Subclasses must implement plot_wind_speed")

    @abstractmethod
    def plot_pressure(
        self, ax: Axes, data: pd.DataFrame, time_indices: Any, ax_wind: Optional[Axes]
    ) -> None:
        """Plot pressure on secondary axis.

        Args:
            ax: matplotlib Axes object
            data: Weather data DataFrame
            time_indices: Time indices for x-axis
            ax_wind: Wind axis for positioning
        """
        raise NotImplementedError("Subclasses must implement plot_pressure")

    @abstractmethod
    def plot_precipitation(
        self, ax: Axes, data: pd.DataFrame, time_indices: Any
    ) -> None:
        """Plot precipitation as bars.

        Args:
            ax: matplotlib Axes object
            data: Weather data DataFrame
            time_indices: Time indices for x-axis
        """
        raise NotImplementedError("Subclasses must implement plot_precipitation")


class LayoutFormatter(ABC):
    """Abstract base class for layout formatting."""

    def __init__(self, config: PlotConfig):
        """Initialize layout formatter.

        Args:
            config: Plot configuration
        """
        self.config = config

    @abstractmethod
    def format_meteogram_plot(self, fig: Figure) -> None:
        """Apply meteogram specific formatting.

        Args:
            fig: matplotlib Figure object
        """
        raise NotImplementedError("Subclasses must implement format_meteogram_plot")

    @abstractmethod
    def plot_hour_labels(
        self, ax: Axes, data: pd.DataFrame, label_padding: Optional[Any] = None
    ) -> None:
        """Plot hour labels at the top of the meteogram.

        Args:
            ax: matplotlib Axes object
            data: Weather data DataFrame
            label_padding: Label padding configuration
        """
        raise NotImplementedError("Subclasses must implement plot_hour_labels")

    @abstractmethod
    def plot_time_axis(self, ax: Axes, data: pd.DataFrame) -> None:
        """Plot time axis with date labels.

        Args:
            ax: matplotlib Axes object
            data: Weather data DataFrame
        """
        raise NotImplementedError("Subclasses must implement plot_time_axis")

    @abstractmethod
    def plot_separator(self, ax: Axes) -> None:
        """Plot separator panel.

        Args:
            ax: matplotlib Axes object
        """
        raise NotImplementedError("Subclasses must implement plot_separator")
