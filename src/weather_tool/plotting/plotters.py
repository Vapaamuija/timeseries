"""
Meteogram plotter implementation - Refactored using SOLID principles.

This module provides the meteogram plotter that matches the provided diagram style,
now using composition and delegation to follow SOLID principles.
"""

import logging
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from .components import (
    BottomLegendPlotter,
    CloudLayerPlotter,
    LayoutManager,
    WindBarbPlotter,
)
from .grid_manager import MeteogramGridManager
from .interfaces import PlotConfig, WeatherPlotter
from .layout_formatter import MeteogramLayoutFormatter
from .legend_plotter import MeteogramLegendPlotter
from .parameter_plotter import MeteogramParameterPlotter
from .symbols import UnifiedWeatherSymbols

logger = logging.getLogger(__name__)


class MeteogramPlotter(WeatherPlotter):
    """Meteogram plotter matching the provided diagram style."""

    def __init__(self, config: PlotConfig):
        """Initialize meteogram plotter with composed components."""
        super().__init__(config)

        # Initialize specialized components following Single Responsibility Principle
        self.symbol_renderer = UnifiedWeatherSymbols(config)
        self.layout_manager = LayoutManager(config)
        self.wind_barb_plotter = WindBarbPlotter(config)
        self.cloud_layer_plotter = CloudLayerPlotter(config)
        self.bottom_legend_plotter = BottomLegendPlotter(config)

        # Initialize new specialized components
        self.legend_plotter = MeteogramLegendPlotter(config)
        self.grid_manager = MeteogramGridManager(config)
        self.parameter_plotter = MeteogramParameterPlotter(config)
        self.layout_formatter = MeteogramLayoutFormatter(config)

        # Meteogram specific configuration
        # Define panel height ratios for meteogram layout
        self.panel_heights = {
            "hour_labels": 0.25,  # Top panel with hour labels and dates
            "cloud_high": 0.4,  # High altitude cloud coverage
            "cloud_medium": 0.4,  # Medium altitude cloud coverage
            "cloud_low": 0.4,  # Low altitude cloud coverage
            "fog": 0.4,  # Fog layer
            "separator": 0.2,  # Visual separator between cloud and main sections
            "main_params": (
                4.0
            ),  # Main weather parameters (temperature, pressure, precipitation)
            "time_axis": 0.6,  # Time axis with date labels
            "weather_symbols": 1.0,  # Weather symbols panel
            "wind_section": 1.2,  # Wind barbs and wind information
        }

        # Convert to list for matplotlib gridspec (maintains order)
        # New order: 1) Cloud coverage (as is), 2) Weather symbols, 3) Main diagram, 4) Wind at bottom
        self.height_ratios = [
            self.panel_heights["hour_labels"],
            self.panel_heights["cloud_high"],
            self.panel_heights["cloud_medium"],
            self.panel_heights["cloud_low"],
            self.panel_heights["fog"],
            self.panel_heights["separator"],
            self.panel_heights["weather_symbols"],
            self.panel_heights["main_params"],
            self.panel_heights["time_axis"],
            self.panel_heights["wind_section"],
        ]

    def create_plot(
        self,
        data: pd.DataFrame,
        airport: Dict[str, Any],
        title: Optional[str] = None,
        **kwargs: Any,
    ) -> Figure:
        """Create a meteogram plot using composed components.

        Args:
            data: Weather data DataFrame
            airport: Airport information dictionary
            title: Custom title
            **kwargs: Additional parameters

        Returns:
            matplotlib Figure object
        """
        if not self.validate_data(data):
            raise ValueError("Data validation failed")

        # Get padding configurations from theme system
        layout_config = self.config.get_effective_layout_config()
        panel_padding = self.config.get_effective_panel_padding()
        label_padding = self.config.get_effective_label_padding()

        # Create meteogram layout using layout manager with configurable padding
        # Use figure size from configuration if available
        figsize = (16, 12)
        if hasattr(self.config, "figure_size") and self.config.figure_size:
             figsize = self.config.figure_size
        
        fig, axes = self.layout_manager.create_meteogram_layout(
            self.height_ratios,
            figsize=figsize,
            panel_padding=panel_padding,
            layout_config=layout_config,
        )

        (
            ax_hour_labels,
            ax_cloud_high,
            ax_cloud_medium,
            ax_cloud_low,
            ax_fog,
            ax_separator,
            ax_weather_symbols,
            ax_main_params,
            ax_time_axis,
            ax_wind_section,
        ) = axes

        # Apply meteogram formatting using layout formatter
        self.layout_formatter.format_meteogram_plot(fig)

        # Set title using font configuration
        plot_title = title or f"Meteogram - {airport.get('name', 'Airport')}"
        if "icao" in airport:
            plot_title += f" ({airport['icao']})"

        # Get font configuration
        font_config: Dict[str, Any] = getattr(self.config, "fonts", {}) or {}
        title_fontsize = font_config.get("title_size", 14)
        title_fontweight = font_config.get("weights", {}).get("title", "bold")

        # Get text color from configuration
        effective_colors = self.config.get_effective_colors()
        text_color = effective_colors.get("text", "#333333")

        fig.suptitle(
            plot_title,
            fontsize=title_fontsize,
            fontweight=title_fontweight,
            color=text_color,
        )

        # Plot each panel using specialized components
        self.layout_formatter.plot_hour_labels(ax_hour_labels, data, label_padding)
        self._plot_cloud_layers_using_component(
            ax_cloud_high, ax_cloud_medium, ax_cloud_low, ax_fog, data, label_padding
        )
        self.layout_formatter.plot_separator(ax_separator)
        self.layout_formatter.plot_weather_symbols(
            ax_weather_symbols, data, self.symbol_renderer
        )
        self.parameter_plotter.plot_main_parameters(ax_main_params, data)
        self.layout_formatter.plot_time_axis(ax_time_axis, data)
        self._plot_wind_section_using_component(ax_wind_section, data)

        # Apply unified grid to ALL panels for consistent alignment using grid manager
        all_axes = [
            ax_hour_labels,
            ax_cloud_high,
            ax_cloud_medium,
            ax_cloud_low,
            ax_fog,
            ax_separator,
            ax_weather_symbols,
            ax_main_params,
            ax_time_axis,
            ax_wind_section,
        ]

        self.grid_manager.apply_unified_grid(all_axes, data)

        # Pass axis references to grid manager for correct grid calculation
        # Parameter plotter stores the secondary axes created
        axis_refs = self.parameter_plotter.get_axis_references()
        self.grid_manager.set_axis_references(
            wind_axis=axis_refs.get("wind_axis"),
            pressure_axis=axis_refs.get("pressure_axis"),
            precip_axis=axis_refs.get("precip_axis"),
        )

        # Calculate shared grid system for all variables using grid manager
        self.grid_manager.calculate_shared_grid_system(ax_main_params, data)

        # Draw shared horizontal grid lines using grid manager
        self.grid_manager.draw_shared_horizontal_grid_lines()

        # Configure legend plotter with shared grid values
        self.legend_plotter.set_shared_grid_values(
            self.grid_manager.get_shared_grid_values()
        )

        # Add all legends using legend plotter
        self.legend_plotter.add_legends(fig, ax_main_params, data, label_padding)

        # Add bottom legend column with colors and definitions
        self.bottom_legend_plotter.add_bottom_legend(fig, data, label_padding)

        # Apply visual debug helpers if enabled
        if self.config.debug_mode:
            self._apply_debug_visuals(fig, all_axes)

        logger.info("Meteogram created successfully using SOLID principles")
        return fig

    def _apply_debug_visuals(self, fig: Figure, axes: List[Any]) -> None:
        """Apply visual debug helpers to the plot."""
        import random
        
        # Define a list of very light pastel colors for debugging
        debug_colors = [
            "#fff0f0", "#f0fff0", "#f0f0ff", "#fff8f0", "#f0fff8", 
            "#f8f0ff", "#fffff0", "#f0ffff", "#fff0ff", "#f5f5f5"
        ]
        
        # Axis labels to identify panels
        labels = [
            "Hour Labels", "Cloud High", "Cloud Med", "Cloud Low", 
            "Fog", "Separator", "Weather Symbols", "Main Params", 
            "Time Axis", "Wind Section"
        ]
        
        # Add figure bounding box
        rect = plt.Rectangle(
            (0, 0), 1, 1, 
            transform=fig.transFigure, 
            facecolor="none", 
            edgecolor="red", 
            linewidth=2, 
            linestyle="--",
            zorder=1000
        )
        fig.patches.append(rect)
        fig.text(0.01, 0.99, "DEBUG MODE", color="red", weight="bold", transform=fig.transFigure)
        
        for i, ax in enumerate(axes):
            # Use modulo to cycle through colors
            bg_color = debug_colors[i % len(debug_colors)]
            
            # Set background color
            ax.set_facecolor(bg_color)
            
            # Add bounding box
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_color("red")
                spine.set_linestyle(":")
                spine.set_linewidth(1)
                
            # Add label in center
            label = labels[i] if i < len(labels) else f"Panel {i}"
            ax.text(
                0.5, 0.5, label,
                transform=ax.transAxes,
                ha="center", va="center",
                color="red", alpha=0.3,
                fontsize=12, weight="bold",
                zorder=1000
            )

    def get_supported_variables(self) -> List[str]:
        """Get supported variables for meteogram."""
        return [
            "temperature",
            "pressure",
            "precipitation",
            "wind_speed",
            "wind_direction",
            "cloud_cover",
            "cloud_high",
            "cloud_medium",
            "cloud_low",
            "fog",
            "weather_symbol",
            "dew_point",
        ]

    def get_required_variables(self) -> List[str]:
        """Get minimum required variables for meteogram."""
        return ["temperature", "pressure"]

    def _plot_cloud_layers_using_component(
        self,
        ax1: Any,
        ax2: Any,
        ax3: Any,
        ax4: Any,
        data: pd.DataFrame,
        label_padding: Optional[Any] = None,
    ) -> None:
        """Plot cloud layers using cloud layer component."""
        cloud_axes = [ax1, ax2, ax3, ax4]
        cloud_vars = ["cloud_high", "cloud_medium", "cloud_low", "fog"]
        cloud_labels = ["Høy", "Mellom", "Lav", "Tåke"]

        self.cloud_layer_plotter.plot_cloud_layers(
            cloud_axes,
            data,
            cloud_vars,
            cloud_labels,
            self.grid_manager.grid_interval,
            label_padding,
        )

    def _plot_wind_section_using_component(self, ax: Any, data: pd.DataFrame) -> None:
        """Plot wind section using wind barb component."""
        self.wind_barb_plotter.plot_barbs(ax, data, max_barbs=15, ylabel=None, length=7)
