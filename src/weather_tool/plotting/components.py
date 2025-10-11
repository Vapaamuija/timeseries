"""
Reusable plotting components for meteogram visualization.

This module provides the essential components needed for the meteogram plotter.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .interfaces import PlotConfig

logger = logging.getLogger(__name__)


class WindBarbPlotter:
    """Specialized plotter for wind barbs."""

    def __init__(self, config: PlotConfig):
        """Initialize wind barb plotter."""
        self.config = config

    def plot_barbs(
        self,
        ax: Axes,
        data: pd.DataFrame,
        max_barbs: int = 15,
        ylabel: Optional[str] = None,
        length: int = 7,
    ) -> None:
        """Plot wind barbs on the given axis.

        Args:
            ax: matplotlib Axes object
            data: DataFrame with wind data
            max_barbs: Maximum number of barbs to plot
            ylabel: Y-axis label
            length: Length of wind barbs
        """
        # Ensure we have wind data
        if "wind_speed" not in data.columns or "wind_direction" not in data.columns:
            logger.warning("Missing wind data columns")
            return

        # Sample data to avoid overcrowding, but maintain time synchronization
        n_points = len(data)
        if n_points > max_barbs:
            step = max(1, n_points // max_barbs)
            # Get the indices of sampled data to maintain time alignment
            sampled_indices = list(range(0, n_points, step))
            sampled_data = data.iloc[sampled_indices]
        else:
            sampled_indices = list(range(n_points))
            sampled_data = data

        # Convert wind direction from degrees to u,v components
        wind_speed = sampled_data["wind_speed"].fillna(0)
        wind_direction = sampled_data["wind_direction"].fillna(0)

        # Convert to radians and calculate u,v components
        wind_dir_rad = np.deg2rad(wind_direction)
        u = -wind_speed * np.sin(wind_dir_rad)  # Negative for meteorological convention
        v = -wind_speed * np.cos(wind_dir_rad)  # Negative for meteorological convention

        # Create x positions for barbs - use original data indices to maintain time alignment
        x_positions = np.array(sampled_indices)
        y_positions = np.ones(len(sampled_data)) * 0.5  # Center vertically

        # Plot wind barbs
        ax.barbs(
            x_positions,
            y_positions,
            u,
            v,
            length=length,
            barbcolor="black",
            flagcolor="black",
            linewidth=1.2,
            fill_empty=True,
        )

        # Format axis - remove boxes and numeric labels
        ax.set_ylim(0, 1)
        ax.set_xlim(0, len(data) - 1)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=9, color="#ff7f0e")
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        ax.tick_params(axis="both", direction="in", length=3)

        # Remove all spines (boxes) around the wind barb area
        for spine in ax.spines.values():
            spine.set_visible(False)


class LayoutManager:
    """Manages layout and positioning for meteogram."""

    def __init__(self, config: PlotConfig):
        """Initialize layout manager."""
        self.config = config

    def create_meteogram_layout(
        self,
        panel_heights: Any,
        figsize: Tuple[int, int] = (16, 12),
        panel_padding: Optional[Any] = None,
        layout_config: Optional[Any] = None,
    ) -> Tuple[Figure, List[Axes]]:
        """Create the meteogram layout with proper panel organization.

        Args:
            panel_heights: Dictionary mapping panel names to height ratios, or list of height ratios
            figsize: Figure size as (width, height) tuple
            panel_padding: PanelPaddingConfig for custom panel spacing
            layout_config: LayoutConfig for margins and spacing

        Returns:
            Tuple of (Figure, List of Axes objects)
        """
        # Create figure
        fig = plt.figure(figsize=figsize, dpi=self.config.dpi)

        # Handle both dict and list inputs for panel_heights
        if isinstance(panel_heights, dict):
            height_ratios = list(panel_heights.values())
        else:
            height_ratios = panel_heights

        # Use configurable spacing and margins
        hspace = 0.05  # Default
        left = 0.15  # Default
        right = 0.95  # Default
        top = 0.95  # Default
        bottom = 0.1  # Default

        # Apply layout config if provided
        if layout_config:
            # Handle both dictionary and object-style layout config
            if isinstance(layout_config, dict):
                left = layout_config.get("left_margin", left)
                right = layout_config.get("right_margin", right)
                top = layout_config.get("top_margin", top)
                bottom = layout_config.get("bottom_margin", bottom)
            else:
                # Object-style access
                left = getattr(layout_config, "left_margin", left)
                right = getattr(layout_config, "right_margin", right)
                top = getattr(layout_config, "top_margin", top)
                bottom = getattr(layout_config, "bottom_margin", bottom)

        # Use panel padding hspace if available
        if panel_padding:
            # Handle both dictionary and object-style panel padding
            if isinstance(panel_padding, dict):
                hspace = panel_padding.get("hspace", hspace)
            else:
                hspace = getattr(panel_padding, "hspace", hspace)

        # Create gridspec with configurable height ratios and spacing
        gs = fig.add_gridspec(
            len(height_ratios),
            1,
            height_ratios=height_ratios,
            hspace=hspace,
            left=left,
            right=right,
            top=top,
            bottom=bottom,
        )

        # Create axes for each panel
        axes = []
        for i in range(len(height_ratios)):
            axes.append(fig.add_subplot(gs[i]))

        return fig, axes


class CloudLayerPlotter:
    """Specialized plotter for cloud layers with proper meteogram styling."""

    def __init__(self, config: PlotConfig):
        """Initialize cloud layer plotter."""
        self.config = config
        self.axis_positions: Dict[str, Axes] = (
            {}
        )  # Store axis positions for legend placement

    def plot_cloud_layers(
        self,
        axes: List[Axes],
        data: pd.DataFrame,
        variables: List[str],
        labels: List[str],
        grid_interval: int = 1,
        label_padding: Optional[Any] = None,
    ) -> None:
        """Plot cloud layers on multiple axes.

        Args:
            axes: List of matplotlib Axes objects
            data: DataFrame with cloud data
            variables: List of cloud variable names
            labels: List of labels for each cloud layer
            grid_interval: Grid interval for time axis
            label_padding: LabelPaddingConfig for custom label positioning
        """
        # Store axis positions for legend placement
        for ax, label in zip(axes, labels):
            self.axis_positions[label] = ax

        # Plot each cloud layer without individual legends
        for ax, variable, label in zip(axes, variables, labels):
            # Get padding configuration from config
            padding_config = self.config.get_effective_time_axis_padding()
            self._plot_single_layer_no_legend(
                ax, data, variable, grid_interval, padding_config
            )

        # Then add all legends after plotting is complete
        self._add_all_legends(labels, label_padding)

    def _plot_single_layer_no_legend(
        self,
        ax: Axes,
        data: pd.DataFrame,
        variable: str,
        grid_interval: int,
        padding_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Plot a single cloud layer with line thickness representing coverage (0-100%).

        Note: grid_interval parameter is kept for API compatibility but grid lines
        are now handled centrally by the plotter's unified grid system.
        """
        # Suppress unused parameter warning - kept for API compatibility
        _ = grid_interval
        # Get colors from configuration (always needed for legend)
        colors = self._get_cloud_colors(variable)

        if variable in data.columns:
            # Ensure numeric data and handle NaN values
            cloud_data_numeric = pd.to_numeric(data[variable], errors="coerce").fillna(
                0
            )

            # Support both 0-1 and 0-100 ranges for cloud coverage
            if cloud_data_numeric.max() <= 1.0:
                # Data is in 0-1 range, convert to 0-100
                cloud_data_percent = cloud_data_numeric * 100
            else:
                # Data is already in 0-100 range
                cloud_data_percent = cloud_data_numeric

            # Clip to valid percentage range
            cloud_data_percent = pd.Series(
                np.clip(cloud_data_percent, 0, 100), index=cloud_data_percent.index
            )

            # Convert back to 0-1 for thickness calculation
            cloud_data_normalized = cloud_data_percent / 100.0

            time_indices = np.arange(len(cloud_data_normalized))

            # Create continuous thick line where thickness represents cloud coverage
            # Use fill_between to create variable thickness horizontal band

            # Create the upper and lower bounds for the filled area
            # Center the band vertically and vary thickness based on coverage
            center_y = 0.5  # Center of the panel

            # Calculate thickness - scale coverage to reasonable thickness
            max_thickness = 0.4  # Maximum thickness (40% of panel height)
            thickness = cloud_data_normalized * max_thickness

            # Create upper and lower bounds
            upper_bound = center_y + thickness / 2
            lower_bound = center_y - thickness / 2

            # Fill the area between bounds to create thick line effect
            ax.fill_between(
                time_indices,
                lower_bound,
                upper_bound,
                color=colors["color"],
                alpha=colors["alpha"],
                edgecolor=colors["edge_color"],
                linewidth=colors["edge_width"],
                step="mid",
            )

            # Add outline for better definition
            ax.plot(
                time_indices,
                upper_bound,
                color=colors["edge_color"],
                linewidth=colors["edge_width"],
                alpha=0.8,
            )
            ax.plot(
                time_indices,
                lower_bound,
                color=colors["edge_color"],
                linewidth=colors["edge_width"],
                alpha=0.8,
            )

        # Format axis to match meteogram style
        ax.set_ylim(0, 1)
        if padding_config:
            start_limit, end_limit = FormattingUtils.calculate_padded_xlim(
                data, padding_config
            )
            ax.set_xlim(start_limit, end_limit)
        else:
            ax.set_xlim(0, len(data) - 1)
        ax.set_yticklabels([])
        ax.set_xticklabels([])

        # Grid lines are now handled centrally by the plotter
        # Individual panels no longer draw their own grids

        ax.tick_params(axis="both", direction="in", length=3)

    def _get_cloud_colors(self, variable: str) -> dict:
        """Get color configuration for a cloud variable from settings."""
        # Default colors if configuration is not available (using settings.yaml colors)
        default_colors = {
            "cloud_high": {
                "color": "#87CEEB",
                "alpha": 1.0,
                "edge_color": "#5F9EA0",
                "edge_width": 0.5,
            },
            "cloud_medium": {
                "color": "#4682B4",
                "alpha": 1.0,
                "edge_color": "#2F4F4F",
                "edge_width": 0.5,
            },
            "cloud_low": {
                "color": "#2F4F4F",
                "alpha": 1.0,
                "edge_color": "#1C1C1C",
                "edge_width": 0.5,
            },
            "fog": {
                "color": "#48CAE4",
                "alpha": 1.0,
                "edge_color": "#0077BE",
                "edge_width": 0.5,
            },
        }

        # Try to get colors from configuration
        try:
            if hasattr(self.config, "variable_config") and self.config.variable_config:
                var_config = self.config.variable_config.get(variable, {})
                if var_config:  # Only use config if it exists and is not empty
                    logger.debug(
                        "Using configuration colors for %s: %s", variable, var_config
                    )
                    return {
                        "color": var_config.get(
                            "color",
                            default_colors.get(variable, default_colors["cloud_low"])[
                                "color"
                            ],
                        ),
                        "alpha": var_config.get(
                            "alpha",
                            default_colors.get(variable, default_colors["cloud_low"])[
                                "alpha"
                            ],
                        ),
                        "edge_color": var_config.get(
                            "edge_color",
                            default_colors.get(variable, default_colors["cloud_low"])[
                                "edge_color"
                            ],
                        ),
                        "edge_width": var_config.get(
                            "edge_width",
                            default_colors.get(variable, default_colors["cloud_low"])[
                                "edge_width"
                            ],
                        ),
                    }
                else:
                    logger.debug(
                        "No configuration found for %s, using defaults", variable
                    )
            else:
                logger.debug(
                    "No variable_config available, using defaults for %s", variable
                )
        except (AttributeError, KeyError) as e:
            logger.debug("Error accessing configuration for %s: %s", variable, e)

        # Return default colors for the variable (now using settings.yaml values)
        colors = default_colors.get(variable, default_colors["cloud_low"])
        logger.debug("Using default colors for %s: %s", variable, colors)
        return colors

    def _add_all_legends(
        self, labels: List[str], label_padding: Optional[Any] = None
    ) -> None:
        """Add all legends after plotting is complete, using stored axis positions."""
        # Map labels to variables for color lookup
        label_to_var = {
            "Høy": "cloud_high",
            "Mellom": "cloud_medium",
            "Lav": "cloud_low",
            "Tåke": "fog",
        }

        # Use configurable padding or defaults
        cloud_label_x = 0.12  # Default
        cloud_label_offset = 0.01  # Default

        if label_padding:
            # Handle both dictionary and object-style label padding
            if isinstance(label_padding, dict):
                cloud_label_x = label_padding.get("cloud_label_x", cloud_label_x)
                cloud_label_offset = label_padding.get(
                    "cloud_label_offset", cloud_label_offset
                )
            else:
                cloud_label_x = getattr(label_padding, "cloud_label_x", cloud_label_x)
                cloud_label_offset = getattr(
                    label_padding, "cloud_label_offset", cloud_label_offset
                )

        for label in labels:
            if label in self.axis_positions:
                ax = self.axis_positions[label]
                variable = label_to_var.get(label, "cloud_low")
                colors = self._get_cloud_colors(variable)

                # Get the current axis position after all formatting is applied
                fig = ax.get_figure()
                if fig is not None:
                    fig.canvas.draw()  # Force drawing to get final positions
                bbox = ax.get_position()

                # Position legend at exact center of axis
                legend_y = bbox.y0 + bbox.height * 0.5

                # Add legend text with configurable positioning
                if fig is not None:
                    fig.text(
                        cloud_label_x,
                        legend_y,
                        label,
                        fontsize=9,
                        va="center",
                        ha="right",
                        color="#808080",
                        fontweight="normal",
                        transform=fig.transFigure,
                    )

                # Add colored square with configurable offset
                if fig is not None:
                    square_x = cloud_label_x + cloud_label_offset
                    colored_rect = plt.Rectangle(
                        (square_x, legend_y - 0.003),
                        0.008,
                        0.006,
                        facecolor=colors["color"],
                        alpha=colors["alpha"],
                        edgecolor=colors["edge_color"],
                        linewidth=colors["edge_width"],
                        transform=fig.transFigure,
                        clip_on=False,
                    )
                    fig.patches.append(colored_rect)

    def _add_colored_legend(self, ax: Axes, label: str, colors: dict) -> None:
        """Add text label and colored square inline with the related cloud layer."""
        # Get the axis position in figure coordinates
        bbox = ax.get_position()

        # Position legend at the center of the axis
        legend_y = bbox.y0 + bbox.height * 0.5

        # Add legend text
        fig = ax.get_figure()
        if fig is not None:
            fig.text(
                0.12,
                legend_y,
                label,
                fontsize=9,
                va="center",
                ha="right",
                color="#808080",
                fontweight="normal",
                transform=fig.transFigure,
            )

        # Add colored square next to text
        if fig is not None:
            colored_rect = plt.Rectangle(
                (0.13, legend_y - 0.003),
                0.008,
                0.006,
                facecolor=colors["color"],
                alpha=colors["alpha"],
                edgecolor=colors["edge_color"],
                linewidth=colors["edge_width"],
                transform=fig.transFigure,
                clip_on=False,
            )
            fig.patches.append(colored_rect)


class FormattingUtils:
    """Utility functions for plot formatting."""

    @staticmethod
    def calculate_padded_xlim(data: pd.DataFrame, padding_config: dict) -> tuple:
        """Calculate x-axis limits with configurable padding.

        Args:
            data: DataFrame with time index
            padding_config: Dictionary with padding configuration

        Returns:
            Tuple of (start_limit, end_limit) for x-axis
        """
        data_length = len(data)
        if data_length == 0:
            return (0, 1)

        # Get padding configuration
        start_padding = padding_config.get("start_padding", 0.05)
        end_padding = padding_config.get("end_padding", 0.05)
        start_padding_hours = padding_config.get("start_padding_hours")
        end_padding_hours = padding_config.get("end_padding_hours")

        # Calculate padding in data points
        if start_padding_hours is not None and len(data) > 1:
            # Convert hours to data points based on time resolution
            time_diff = (data.index[1] - data.index[0]).total_seconds() / 3600  # hours
            start_padding_points = start_padding_hours / time_diff
        else:
            # Use fractional padding
            start_padding_points = start_padding * (data_length - 1)

        if end_padding_hours is not None and len(data) > 1:
            # Convert hours to data points based on time resolution
            time_diff = (data.index[1] - data.index[0]).total_seconds() / 3600  # hours
            end_padding_points = end_padding_hours / time_diff
        else:
            # Use fractional padding
            end_padding_points = end_padding * (data_length - 1)

        # Calculate limits
        start_limit = -start_padding_points
        end_limit = (data_length - 1) + end_padding_points

        return (start_limit, end_limit)

    @staticmethod
    def format_time_axis(
        ax: Axes,
        data: pd.DataFrame,
        grid_interval: int = 1,
        padding_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Format time axis with proper meteogram styling.

        Args:
            ax: matplotlib Axes object
            data: DataFrame with time index
            grid_interval: Interval for grid lines (in hours)
            padding_config: Optional padding configuration
        """
        # Set x-axis limits with padding
        if padding_config:
            start_limit, end_limit = FormattingUtils.calculate_padded_xlim(
                data, padding_config
            )
            ax.set_xlim(start_limit, end_limit)
        else:
            ax.set_xlim(0, len(data) - 1)

        # Create time labels
        time_labels = []
        for i in range(0, len(data), grid_interval):
            if i < len(data):
                timestamp = data.index[i]
                time_labels.append(timestamp.strftime("%H"))
            else:
                time_labels.append("")

        # Set x-axis ticks and labels
        tick_positions = list(range(0, len(data), grid_interval))
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(time_labels, fontsize=8)

        # Add vertical grid lines
        for pos in tick_positions:
            ax.axvline(x=pos, color="grey", linestyle="-", alpha=0.3, linewidth=0.5)

    @staticmethod
    def add_time_labels(
        ax: Axes,
        data: pd.DataFrame,
        time_interval: int = 1,
        padding_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add time labels to the axis.

        Args:
            ax: matplotlib Axes object
            data: DataFrame with time index
            time_interval: Interval for time labels (in hours)
            padding_config: Optional padding configuration
        """
        # Set x-axis limits with padding
        if padding_config:
            start_limit, end_limit = FormattingUtils.calculate_padded_xlim(
                data, padding_config
            )
            ax.set_xlim(start_limit, end_limit)
        else:
            ax.set_xlim(0, len(data) - 1)

        # Create time labels
        time_labels = []
        tick_positions = []

        for i in range(0, len(data), time_interval):
            if i < len(data):
                timestamp = data.index[i]
                time_labels.append(timestamp.strftime("%H"))
                tick_positions.append(i)

        # Set x-axis ticks and labels
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(time_labels, fontsize=8)

        # Style the axis
        ax.tick_params(axis="both", direction="in", length=3)

    @staticmethod
    def add_vertical_grid(
        target_axis: Axes,
        total_time_points: int,
        grid_line_interval: int = 1,
        grid_line_color: str = "grey",
        grid_transparency: float = 0.3,
        day_boundary_indices: Optional[List[int]] = None,
    ) -> None:
        """Add vertical grid lines to the axis.

        Args:
            target_axis: matplotlib Axes object
            total_time_points: Length of the data (number of time points)
            grid_line_interval: Interval for grid lines (in hours)
            grid_line_color: Color of grid lines
            grid_transparency: Alpha transparency of grid lines
            day_boundary_indices: List of indices where day boundaries occur (for thicker lines)
        """
        day_boundary_indices = day_boundary_indices or []

        # Add vertical grid lines
        for time_point_index in range(0, total_time_points, grid_line_interval):
            # Make day boundary lines thicker
            if time_point_index in day_boundary_indices:
                grid_line_width = 1.5  # Thicker line for day boundaries
            else:
                grid_line_width = 0.5  # Normal line thickness

            target_axis.axvline(
                x=time_point_index,
                color=grid_line_color,
                linestyle="-",
                alpha=grid_transparency,
                linewidth=grid_line_width,
            )

    @staticmethod
    def add_horizontal_grid(
        ax: Axes,
        color: str = "lightgray",
        alpha: float = 0.4,
        linestyle: str = ":",
        linewidth: float = 0.5,
        grid_values: Optional[List[float]] = None,
    ) -> None:
        """Add horizontal grid lines to the axis.

        Args:
            ax: matplotlib Axes object
            color: Color of grid lines
            alpha: Alpha transparency of grid lines
            linestyle: Line style for grid lines
            linewidth: Width of grid lines
            grid_values: Optional list of specific y-values where to draw grid lines
        """
        if grid_values:
            # Use specific grid values
            for y_val in grid_values:
                ax.axhline(
                    y=y_val,
                    color=color,
                    linestyle=linestyle,
                    alpha=alpha,
                    linewidth=linewidth,
                )
        else:
            # Get current y-limits and add horizontal grid lines
            y_min, y_max = ax.get_ylim()

            # Add a few horizontal grid lines across the y-range
            num_lines = 3
            for i in range(1, num_lines):
                y_val = y_min + (y_max - y_min) * i / num_lines
                ax.axhline(
                    y=y_val,
                    color=color,
                    linestyle=linestyle,
                    alpha=alpha,
                    linewidth=linewidth,
                )

    @staticmethod
    def calculate_nice_grid_values(
        y_axis_minimum: float, y_axis_maximum: float, maximum_grid_lines: int = 6
    ) -> list:
        """Calculate nice round values for grid lines within the given range.

        Args:
            y_axis_minimum: Minimum y value
            y_axis_maximum: Maximum y value
            maximum_grid_lines: Maximum number of grid lines to generate

        Returns:
            List of nice round values for grid lines
        """
        import math

        # Calculate the range
        y_axis_value_range = y_axis_maximum - y_axis_minimum
        if y_axis_value_range == 0:
            return []

        # Calculate a nice step size
        approximate_step_size = y_axis_value_range / maximum_grid_lines

        # Find the order of magnitude
        step_magnitude = math.floor(math.log10(approximate_step_size))

        # Normalize the rough step to between 1 and 10
        normalized_step_size = approximate_step_size / (10**step_magnitude)

        # Choose a nice step size
        if normalized_step_size <= 1:
            rounded_step_size = 1
        elif normalized_step_size <= 2:
            rounded_step_size = 2
        elif normalized_step_size <= 5:
            rounded_step_size = 5
        else:
            rounded_step_size = 10

        # Scale back up
        final_step_size = rounded_step_size * (10**step_magnitude)

        # Find the starting point (round down to nearest step)
        grid_start_value = (
            math.floor(y_axis_minimum / final_step_size) * final_step_size
        )

        # Generate grid values
        calculated_grid_values = []
        current_grid_value = grid_start_value
        while current_grid_value <= y_axis_maximum:
            if current_grid_value >= y_axis_minimum:  # Only include values within range
                calculated_grid_values.append(current_grid_value)
            current_grid_value += final_step_size

        return calculated_grid_values

    @staticmethod
    def add_date_labels(ax: Axes, data: pd.DataFrame) -> None:
        """Add date labels below the time axis.

        Args:
            ax: matplotlib Axes object
            data: DataFrame with time index
        """
        # Get unique dates in the data
        dates = pd.to_datetime(data.index).date
        unique_dates = []
        date_positions = []

        current_date: Optional[Any] = None
        for i, date in enumerate(dates):
            if date != current_date:
                unique_dates.append(date)
                date_positions.append(i)
                current_date = date

        # Add date labels
        for pos, date in zip(date_positions, unique_dates):
            ax.text(
                pos,
                -0.15,
                date.strftime("%Y-%m-%d"),
                ha="left",
                va="top",
                fontsize=8,
                transform=ax.get_xaxis_transform(),
            )

    @staticmethod
    def apply_norwegian_styling(ax: Axes, ylabel: Optional[str] = None) -> None:
        """Apply meteogram styling to an axis.

        Args:
            ax: matplotlib Axes object
            ylabel: Y-axis label
        """
        # Set basic styling
        ax.tick_params(axis="both", direction="in", length=3)
        ax.grid(True, alpha=0.3, linestyle="-", linewidth=0.5)

        # Set ylabel if provided
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=9, color="#808080")

        # Remove top and right spines
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # Style remaining spines
        ax.spines["left"].set_color("#808080")
        ax.spines["bottom"].set_color("#808080")


class BottomLegendPlotter:
    """Specialized plotter for bottom legend column showing colors and definitions."""

    def __init__(self, config: PlotConfig):
        """Initialize bottom legend plotter."""
        self.config = config

    def _get_legend_positioning(
        self, legend_positioning_config: Optional[Any] = None
    ) -> tuple:
        """Get legend positioning configuration."""
        legend_vertical_position = 0.02
        legend_horizontal_start_position = 0.15
        legend_item_horizontal_spacing = 0.12

        if legend_positioning_config:
            if isinstance(legend_positioning_config, dict):
                legend_vertical_position = legend_positioning_config.get(
                    "bottom_legend_y", legend_vertical_position
                )
                legend_horizontal_start_position = legend_positioning_config.get(
                    "bottom_legend_x_start", legend_horizontal_start_position
                )
                legend_item_horizontal_spacing = legend_positioning_config.get(
                    "bottom_legend_spacing", legend_item_horizontal_spacing
                )
            else:
                legend_vertical_position = getattr(
                    legend_positioning_config,
                    "bottom_legend_y",
                    legend_vertical_position,
                )
                legend_horizontal_start_position = getattr(
                    legend_positioning_config,
                    "bottom_legend_x_start",
                    legend_horizontal_start_position,
                )
                legend_item_horizontal_spacing = getattr(
                    legend_positioning_config,
                    "bottom_legend_spacing",
                    legend_item_horizontal_spacing,
                )

        return (
            legend_vertical_position,
            legend_horizontal_start_position,
            legend_item_horizontal_spacing,
        )

    def add_bottom_legend(
        self,
        meteogram_figure: Figure,
        weather_data: pd.DataFrame,
        legend_positioning_config: Optional[Any] = None,
    ) -> None:
        """Add bottom legend column with colors and definitions.

        Args:
            meteogram_figure: matplotlib Figure object
            weather_data: Weather data DataFrame to determine which variables to show
            legend_positioning_config: LabelPaddingConfig for custom positioning
        """
        (
            legend_vertical_position,
            legend_horizontal_start_position,
            legend_item_horizontal_spacing,
        ) = self._get_legend_positioning(legend_positioning_config)

        # Get effective colors from configuration
        configured_color_scheme = self.config.get_effective_colors()

        # Get font configuration
        font_configuration = getattr(self.config, "fonts", {}) or {}
        legend_text_font_size = font_configuration.get("annotation_size", 8)
        legend_text_font_weight = font_configuration.get("weights", {}).get(
            "annotation", "normal"
        )
        legend_text_color = configured_color_scheme.get("text", "#333333")

        # Define legend items based on available data and configuration
        weather_legend_items = []

        # Temperature legend items (always show if temperature data exists)
        if "temperature" in weather_data.columns:
            weather_legend_items.extend(
                [
                    {
                        "color": configured_color_scheme.get(
                            "temperature_above", "#d62728"
                        ),
                        "label": "Temperature ≥0°C",
                        "type": "line",
                    },
                    {
                        "color": configured_color_scheme.get(
                            "temperature_below", "#1f77b4"
                        ),
                        "label": "Temperature <0°C",
                        "type": "line",
                    },
                ]
            )

        # Dew point legend item
        if "dew_point" in weather_data.columns:
            weather_legend_items.append(
                {
                    "color": configured_color_scheme.get("dew_point", "#17becf"),
                    "label": "Dew Point",
                    "type": "dashed_line",
                }
            )

        # Wind speed legend item
        if "wind_speed" in weather_data.columns:
            weather_legend_items.append(
                {
                    "color": configured_color_scheme.get("wind", "#ff7f0e"),
                    "label": "Wind Speed",
                    "type": "line",
                }
            )

        # Pressure legend item
        if "pressure" in weather_data.columns:
            weather_legend_items.append(
                {
                    "color": configured_color_scheme.get("pressure", "#2ca02c"),
                    "label": "Pressure",
                    "type": "line",
                }
            )

        # Precipitation legend item
        if "precipitation" in weather_data.columns:
            weather_legend_items.append(
                {
                    "color": configured_color_scheme.get("precipitation", "#1f77b4"),
                    "label": "Precipitation",
                    "type": "bar",
                }
            )

        # Cloud layer legend items
        available_cloud_variables = ["cloud_high", "cloud_medium", "cloud_low", "fog"]
        cloud_layer_display_labels = [
            "High Clouds",
            "Medium Clouds",
            "Low Clouds",
            "Fog",
        ]

        for cloud_variable, display_label in zip(
            available_cloud_variables, cloud_layer_display_labels
        ):
            if cloud_variable in weather_data.columns:
                # Get cloud colors from variable config
                cloud_layer_color_config = self._get_cloud_colors_for_legend(
                    cloud_variable
                )
                weather_legend_items.append(
                    {
                        "color": cloud_layer_color_config["color"],
                        "label": display_label,
                        "type": "filled_area",
                    }
                )

        # Draw legend items
        current_legend_x_position = legend_horizontal_start_position
        for legend_item in weather_legend_items:
            # Break to new row if we exceed figure width
            if current_legend_x_position > 0.85:  # Leave some margin on the right
                legend_vertical_position -= 0.03  # Move to next row
                current_legend_x_position = legend_horizontal_start_position

            self._draw_legend_item(
                meteogram_figure,
                current_legend_x_position,
                legend_vertical_position,
                legend_item,
                legend_text_font_size,
                legend_text_font_weight,
                legend_text_color,
            )
            current_legend_x_position += legend_item_horizontal_spacing

    def _get_cloud_colors_for_legend(self, variable: str) -> dict:
        """Get cloud colors for legend display."""
        # Default colors matching CloudLayerPlotter
        default_colors = {
            "cloud_high": {"color": "#87CEEB"},
            "cloud_medium": {"color": "#4682B4"},
            "cloud_low": {"color": "#2F4F4F"},
            "fog": {"color": "#48CAE4"},
        }

        # Try to get colors from configuration
        try:
            if hasattr(self.config, "variable_config") and self.config.variable_config:
                var_config = self.config.variable_config.get(variable, {})
                if var_config:
                    return {
                        "color": var_config.get(
                            "color",
                            default_colors.get(variable, default_colors["cloud_low"])[
                                "color"
                            ],
                        )
                    }
        except (AttributeError, KeyError):
            pass

        return default_colors.get(variable, default_colors["cloud_low"])

    def _draw_legend_item(
        self,
        meteogram_figure: Figure,
        legend_item_x_position: float,
        legend_item_y_position: float,
        legend_item_config: dict,
        text_font_size: int,
        text_font_weight: str,
        text_display_color: str,
    ) -> None:
        """Draw a single legend item with appropriate symbol and label.

        Args:
            meteogram_figure: matplotlib Figure object
            legend_item_x_position: X position in figure coordinates
            legend_item_y_position: Y position in figure coordinates
            legend_item_config: Dictionary with 'color', 'label', and 'type' keys
            text_font_size: Font size for text
            text_font_weight: Font weight for text
            text_display_color: Color for text
        """
        legend_symbol_width = 0.03  # Width of the symbol
        legend_symbol_height = 0.008  # Height of the symbol
        symbol_text_spacing = 0.005  # Offset between symbol and text

        # Draw symbol based on type
        if legend_item_config["type"] == "line":
            # Draw a solid line
            symbol_center_y = legend_item_y_position + legend_symbol_height / 2
            meteogram_figure.add_artist(
                plt.Line2D(
                    [
                        legend_item_x_position,
                        legend_item_x_position + legend_symbol_width,
                    ],
                    [symbol_center_y, symbol_center_y],
                    color=legend_item_config["color"],
                    linewidth=2,
                    transform=meteogram_figure.transFigure,
                    clip_on=False,
                )
            )

        elif legend_item_config["type"] == "dashed_line":
            # Draw a dashed line
            symbol_center_y = legend_item_y_position + legend_symbol_height / 2
            meteogram_figure.add_artist(
                plt.Line2D(
                    [
                        legend_item_x_position,
                        legend_item_x_position + legend_symbol_width,
                    ],
                    [symbol_center_y, symbol_center_y],
                    color=legend_item_config["color"],
                    linewidth=2,
                    linestyle="--",
                    transform=meteogram_figure.transFigure,
                    clip_on=False,
                )
            )

        elif legend_item_config["type"] == "bar":
            # Draw a small rectangle representing a bar
            bar_symbol_rectangle = plt.Rectangle(
                (legend_item_x_position, legend_item_y_position),
                legend_symbol_width,
                legend_symbol_height,
                facecolor=legend_item_config["color"],
                alpha=0.7,
                transform=meteogram_figure.transFigure,
                clip_on=False,
            )
            meteogram_figure.patches.append(bar_symbol_rectangle)

        elif legend_item_config["type"] == "filled_area":
            # Draw a filled rectangle representing cloud coverage
            filled_area_symbol_rectangle = plt.Rectangle(
                (legend_item_x_position, legend_item_y_position),
                legend_symbol_width,
                legend_symbol_height,
                facecolor=legend_item_config["color"],
                alpha=1.0,
                transform=meteogram_figure.transFigure,
                clip_on=False,
            )
            meteogram_figure.patches.append(filled_area_symbol_rectangle)

        # Add text label
        legend_text_x_position = (
            legend_item_x_position + legend_symbol_width + symbol_text_spacing
        )
        meteogram_figure.text(
            legend_text_x_position,
            legend_item_y_position + legend_symbol_height / 2,
            legend_item_config["label"],
            fontsize=text_font_size,
            fontweight=text_font_weight,
            color=text_display_color,
            va="center",
            ha="left",
            transform=meteogram_figure.transFigure,
        )


class GridManager:
    """Manages grid lines across all panels in the meteogram."""

    def __init__(self, config: PlotConfig):
        """Initialize grid manager."""
        self.config = config

    def add_unified_grid(
        self,
        meteogram_axes_dict: Dict[str, Axes],
        time_series_data: pd.DataFrame,
        hourly_grid_interval: int = 1,
        axis_padding_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add unified vertical grid lines across all panels.

        Args:
            meteogram_axes_dict: Dictionary of axes objects
            time_series_data: DataFrame with time data
            hourly_grid_interval: Interval for grid lines (in hours)
            axis_padding_config: Optional padding configuration
        """
        # Calculate grid positions
        vertical_grid_line_positions = list(
            range(0, len(time_series_data), hourly_grid_interval)
        )

        # Calculate x-limits with padding
        if axis_padding_config:
            x_axis_start_limit, x_axis_end_limit = (
                FormattingUtils.calculate_padded_xlim(
                    time_series_data, axis_padding_config
                )
            )
        else:
            x_axis_start_limit, x_axis_end_limit = 0, len(time_series_data) - 1

        # Add vertical grid lines to all axes
        for axis_identifier, panel_axis in meteogram_axes_dict.items():
            if axis_identifier not in [
                "time_axis"
            ]:  # Skip time axis as it handles its own grid
                for grid_line_position in vertical_grid_line_positions:
                    panel_axis.axvline(
                        x=grid_line_position,
                        color="grey",
                        linestyle="-",
                        alpha=0.3,
                        linewidth=0.5,
                    )

                # Set consistent x-limits with padding
                panel_axis.set_xlim(x_axis_start_limit, x_axis_end_limit)
