"""
Norwegian meteogram plotter implementation.

This module provides the Norwegian meteogram plotter that matches the provided diagram style.
"""

import logging
from typing import List, Optional, Dict, Any
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np

from .interfaces import WeatherPlotter, PlotConfig
from .symbols import UnifiedWeatherSymbols
from .components import (
    LayoutManager, FormattingUtils,
    WindBarbPlotter, CloudLayerPlotter, BottomLegendPlotter
)

logger = logging.getLogger(__name__)


class MeteogramPlotter(WeatherPlotter):
    """Norwegian meteogram plotter matching the provided diagram style."""
    
    def __init__(self, config: PlotConfig):
        """Initialize Norwegian meteogram plotter."""
        super().__init__(config)
        self.symbol_renderer = UnifiedWeatherSymbols(config)
        self.layout_manager = LayoutManager(config)
        self.wind_barb_plotter = WindBarbPlotter(config)
        self.cloud_layer_plotter = CloudLayerPlotter(config)
        self.bottom_legend_plotter = BottomLegendPlotter(config)
        
        # Norwegian meteogram specific configuration
        # Define panel height ratios for meteogram layout
        self.panel_heights = {
            'hour_labels': 0.25,      # Top panel with hour labels and dates
            'cloud_high': 0.4,        # High altitude cloud coverage
            'cloud_medium': 0.4,      # Medium altitude cloud coverage  
            'cloud_low': 0.4,         # Low altitude cloud coverage
            'fog': 0.4,               # Fog layer
            'separator': 0.2,         # Visual separator between cloud and main sections
            'main_params': 4.0,       # Main weather parameters (temperature, pressure, precipitation)
            'time_axis': 0.6,         # Time axis with date labels
            'weather_symbols': 1.0,   # Weather symbols panel
            'wind_section': 1.2       # Wind barbs and wind information
        }
        
        # Convert to list for matplotlib gridspec (maintains order)
        # New order: 1) Cloud coverage (as is), 2) Weather symbols, 3) Main diagram, 4) Wind at bottom
        self.height_ratios = [
            self.panel_heights['hour_labels'],
            self.panel_heights['cloud_high'],
            self.panel_heights['cloud_medium'],
            self.panel_heights['cloud_low'],
            self.panel_heights['fog'],
            self.panel_heights['separator'],
            self.panel_heights['weather_symbols'],
            self.panel_heights['main_params'],
            self.panel_heights['time_axis'],
            self.panel_heights['wind_section']
        ]
        self.grid_interval = 1  # Grid every 1 hour
        self.time_interval = 1  # Time labels every 1 hour
    
    def create_plot(
        self,
        data: pd.DataFrame,
        airport: Dict[str, Any],
        title: Optional[str] = None,
        **kwargs
    ) -> Figure:
        """Create a Norwegian meteogram plot.
        
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
        
        # Create Norwegian meteogram layout using layout manager with configurable padding
        fig, axes = self.layout_manager.create_meteogram_layout(
            self.height_ratios, figsize=(16, 12), 
            panel_padding=panel_padding, layout_config=layout_config
        )
        
        (ax_hour_labels, ax_cloud_high, ax_cloud_medium, ax_cloud_low, 
         ax_fog, ax_separator, ax_weather_symbols, ax_main_params, 
         ax_time_axis, ax_wind_section) = axes
        
        # Apply Norwegian meteogram formatting first to set proper margins
        self._format_norwegian_plot_custom(fig)
        
        # Set title using font configuration
        plot_title = title or f"Meteogram - {airport.get('name', 'Airport')}"
        if 'icao' in airport:
            plot_title += f" ({airport['icao']})"
        
        # Get font configuration
        font_config = getattr(self.config, 'fonts', {}) or {}
        title_fontsize = font_config.get('title_size', 14)
        title_fontweight = font_config.get('weights', {}).get('title', 'bold')
        
        # Get text color from configuration
        effective_colors = self.config.get_effective_colors()
        text_color = effective_colors.get('text', '#333333')
        
        fig.suptitle(plot_title, fontsize=title_fontsize, fontweight=title_fontweight, color=text_color)
        
        # Plot each panel (after margins are set)
        self._plot_hour_labels(ax_hour_labels, data, label_padding)
        self._plot_cloud_layers_using_component(ax_cloud_high, ax_cloud_medium, ax_cloud_low, ax_fog, data, label_padding)
        self._plot_separator(ax_separator)
        self._plot_weather_symbols(ax_weather_symbols, data)  # Weather symbols after cloud coverage
        self._plot_main_parameters(ax_main_params, data)
        self._plot_time_axis(ax_time_axis, data)
        self._plot_wind_section_using_component(ax_wind_section, data)
        
        # Apply unified grid to ALL panels for consistent alignment
        self._apply_unified_grid_to_all_panels([
            ax_hour_labels, ax_cloud_high, ax_cloud_medium, ax_cloud_low, 
            ax_fog, ax_separator, ax_weather_symbols, ax_main_params, 
            ax_time_axis, ax_wind_section
        ], data)
        
        # Calculate shared grid system for all variables
        self._calculate_shared_grid_system(ax_main_params, data)
        
        # Draw shared horizontal grid lines
        self._draw_shared_horizontal_grid_lines()
        
        # Add all legends using shared grid system
        
        # Add left-side legends for temperature and wind speed
        self._add_left_side_legends(ax_main_params, data, label_padding)
        
        # Add right-side legends for pressure and precipitation
        self._add_right_side_legends(ax_main_params, data, label_padding)
        
        # Add bottom legend column with colors and definitions
        self.bottom_legend_plotter.add_bottom_legend(fig, data, label_padding)
        
        logger.info("Norwegian meteogram created successfully")
        return fig
    
    def get_supported_variables(self) -> List[str]:
        """Get supported variables for Norwegian meteogram."""
        return [
            'temperature', 'pressure', 'precipitation', 'wind_speed', 'wind_direction',
            'cloud_cover', 'cloud_high', 'cloud_medium', 'cloud_low', 'fog', 'weather_symbol',
            'dew_point'
        ]
    
    def get_required_variables(self) -> List[str]:
        """Get minimum required variables for Norwegian meteogram."""
        return ['temperature', 'pressure']
    
    def _plot_hour_labels(self, ax: Axes, data: pd.DataFrame, label_padding=None):
        """Plot hour labels at the top of the meteogram."""
        # Get padding configuration
        padding_config = self.config.get_effective_time_axis_padding()
        if padding_config:
            from .components import FormattingUtils
            start_limit, end_limit = FormattingUtils.calculate_padded_xlim(data, padding_config)
            ax.set_xlim(start_limit, end_limit)
        else:
            ax.set_xlim(0, len(data))
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        if data.empty:
            return
        
        # Use configurable positioning or defaults
        hour_label_y = 0.3  # Default
        date_label_y = 0.7  # Default
        
        if label_padding:
            # Handle both dictionary and object-style label padding
            if isinstance(label_padding, dict):
                hour_label_y = label_padding.get('hour_label_y', hour_label_y)
                date_label_y = label_padding.get('date_label_y', date_label_y)
            else:
                hour_label_y = getattr(label_padding, 'hour_label_y', hour_label_y)
                date_label_y = getattr(label_padding, 'date_label_y', date_label_y)
        
        # Add hour labels at 1 hour intervals
        # Get font and color configuration
        font_config = getattr(self.config, 'fonts', {}) or {}
        effective_colors = self.config.get_effective_colors()
        label_fontsize = font_config.get('tick_size', 9)
        label_fontweight = font_config.get('weights', {}).get('tick', 'normal')
        text_color = effective_colors.get('text', '#333333')
        
        for i in range(0, len(data), 1):  # Every hour
            if i < len(data):
                hour = data.index[i].strftime('%H')
                ax.text(i, hour_label_y, hour, ha='center', va='center',
                       fontsize=label_fontsize, fontweight=label_fontweight, color=text_color)
        
        # Add date labels at day boundaries
        current_date = None
        for i, timestamp in enumerate(data.index):
            date = timestamp.date()
            if date != current_date:
                current_date = date
                # Format date like "Tor 09. okt." (Norwegian style)
                day_name = timestamp.strftime('%a')  # Abbreviated day name
                date_str = timestamp.strftime('%d. %b.')  # Day and abbreviated month
                full_date = f"{day_name} {date_str}"
                # Use same font config but with label weight for dates
                date_fontweight = font_config.get('weights', {}).get('label', 'bold')
                ax.text(i, date_label_y, full_date, ha='left', va='center',
                       fontsize=label_fontsize, fontweight=date_fontweight, color=text_color)

    def _plot_weather_symbols(self, ax: Axes, data: pd.DataFrame):
        """Plot weather symbols after cloud coverage section."""
        # Get padding configuration and set x-limits
        padding_config = self.config.get_effective_time_axis_padding()
        if padding_config:
            from .components import FormattingUtils
            start_limit, end_limit = FormattingUtils.calculate_padded_xlim(data, padding_config)
            ax.set_xlim(start_limit, end_limit)
        else:
            ax.set_xlim(0, len(data))  # Match other panels' x-limits
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        if 'weather_symbol' in data.columns:
            # Position symbols in the center of the dedicated symbol panel
            # Use time indices to align with other panels
            symbols_added = self.symbol_renderer.add_symbols_to_plot(
                ax, 
                data, 
                y_position=0.5,  # Center of the symbol panel
                symbol_type=self.config.symbol_type
            )
            logger.debug("Added %d weather symbols to meteogram", symbols_added)
        else:
            logger.warning("No weather_symbol column found in data")
    
    def _plot_cloud_layers_using_component(self, ax1: Axes, ax2: Axes, ax3: Axes, ax4: Axes, data: pd.DataFrame, label_padding=None):
        """Plot cloud layers using cloud layer component."""
        cloud_axes = [ax1, ax2, ax3, ax4]
        cloud_vars = ['cloud_high', 'cloud_medium', 'cloud_low', 'fog']
        cloud_labels = ['Høy', 'Mellom', 'Lav', 'Tåke']
        
        self.cloud_layer_plotter.plot_cloud_layers(
            cloud_axes, data, cloud_vars, cloud_labels, self.grid_interval, label_padding
        )
    
    def _plot_wind_section_using_component(self, ax: Axes, data: pd.DataFrame):
        """Plot wind section using wind barb component."""
        self.wind_barb_plotter.plot_barbs(ax, data, max_barbs=15, ylabel=None, length=7)
    
    def _format_norwegian_plot_custom(self, fig: Figure):
        """Apply Norwegian meteogram specific formatting."""
        # Set font parameters
        plt.rcParams.update({'font.size': 9})
        
        # Manual subplot adjustment for proper spacing with room for scale legends on both sides
        plt.subplots_adjust(
            left=0.12,  # Increased space for left scale legends
            right=0.88,  # Increased space for right scale legends
            top=0.93,
            bottom=0.08,
            hspace=0.01,  # Even tighter spacing between panels
            wspace=0
        )
        
        # Add signature line at bottom using configuration
        font_config = getattr(self.config, 'fonts', {}) or {}
        effective_colors = self.config.get_effective_colors()
        signature_fontsize = font_config.get('annotation_size', 6)
        grid_color = effective_colors.get('grid', '#e0e0e0')
        colors_config = getattr(self.config, 'colors', {}) or {}
        grid_alpha = colors_config.get('grid_alpha', 0.4)
        
        fig.text(0.15, 0.02, '/' * 90, fontsize=signature_fontsize, alpha=grid_alpha, 
                family='monospace', color=grid_color)
    
    def _plot_separator(self, ax: Axes):
        """Plot separator panel."""
        ax.axis('off')
    
    def _plot_temperature_segments(self, ax: Axes, time_indices: np.ndarray, temp_data: pd.Series):
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
        current_segment = {'start': 0, 'end': 0, 'above_zero': temps[0] >= 0}
        
        for i in range(1, len(temps)):
            is_above_zero = temps[i] >= 0
            
            if is_above_zero == current_segment['above_zero']:
                # Continue current segment
                current_segment['end'] = i
            else:
                # Finish current segment and start new one
                segments.append(current_segment)
                current_segment = {'start': i-1, 'end': i, 'above_zero': is_above_zero}
        
        # Add the final segment
        segments.append(current_segment)
        
        # Plot each segment with appropriate color
        has_above_zero = False
        has_below_zero = False
        
        for segment in segments:
            start_idx = segment['start']
            end_idx = segment['end']
            is_above_zero = segment['above_zero']
            
            # Get the data for this segment
            segment_indices = indices[start_idx:end_idx+1]
            segment_temps = temps[start_idx:end_idx+1]
            
            # Choose color and label
            colors = self.config.get_effective_colors()
            if is_above_zero:
                color = colors['temperature_above']
                label = 'Temperature ≥0°C' if not has_above_zero else None
                has_above_zero = True
            else:
                color = colors['temperature_below']
                label = 'Temperature <0°C' if not has_below_zero else None
                has_below_zero = True
            
            # Plot the segment
            ax.plot(segment_indices, segment_temps, 
                   color=color, linewidth=2, label=label)
    
    def _plot_main_parameters(self, ax: Axes, data: pd.DataFrame):
        """Plot main weather parameters (temperature, pressure, precipitation, dew point, wind speed)."""
        time_indices = np.arange(len(data))
        
        # Temperature (primary y-axis) with conditional coloring
        if 'temperature' in data.columns:
            temp_data = data['temperature']
            
            # Plot temperature as continuous segments with color changes at zero crossings
            self._plot_temperature_segments(ax, time_indices, temp_data)
            
            # Remove axis labels since we're using custom scale legends
            # Get text color from configuration
            effective_colors = self.config.get_effective_colors()
            text_color = effective_colors.get('text', '#333333')
            font_config = getattr(self.config, 'fonts', {}) or {}
            label_fontsize = font_config.get('label_size', 10)
            
            ax.set_ylabel('', color=text_color, fontsize=label_fontsize)
            ax.tick_params(axis='y', labelcolor=text_color, labelleft=False)
            
            # Calculate temperature range including dew point if available
            temp_min, temp_max = data['temperature'].min(), data['temperature'].max()
            if 'dew_point' in data.columns:
                dew_min, dew_max = data['dew_point'].min(), data['dew_point'].max()
                temp_min = min(temp_min, dew_min)
                temp_max = max(temp_max, dew_max)
            
            margin = max(2, (temp_max - temp_min) * 0.1)
            ax.set_ylim(temp_min - margin, temp_max + margin)
            
            # Add horizontal reference lines
            # Get grid color from configuration
            grid_color = effective_colors.get('grid', '#e0e0e0')
            colors_config = getattr(self.config, 'colors', {}) or {}
            grid_alpha = colors_config.get('grid_alpha', 0.5)
            ax.axhline(y=0, color=grid_color, linestyle='--', alpha=grid_alpha, linewidth=0.8)
        
        # Dew point (same y-axis as temperature)
        if 'dew_point' in data.columns:
            # Use dedicated dew point color from configuration
            dew_point_color = effective_colors.get('dew_point', '#17becf')
            ax.plot(time_indices, data['dew_point'], 
                   color=dew_point_color, linewidth=1.5, linestyle='--', 
                   label='Dew Point', alpha=0.8)
        
        # Wind speed (secondary y-axis on the right)
        ax_wind = None
        if 'wind_speed' in data.columns:
            ax_wind = ax.twinx()
            wind_data = data['wind_speed']
            # Get wind color from configuration
            wind_color = effective_colors.get('wind', '#ff7f0e')
            ax_wind.plot(time_indices, wind_data, 
                        color=wind_color, linewidth=2, label='Wind Speed', alpha=0.8)
            # Remove axis labels since we're using custom scale legends
            ax_wind.set_ylabel('', color=wind_color, fontsize=label_fontsize)
            ax_wind.tick_params(axis='y', labelcolor=wind_color, labelright=False)
            
            # Set wind speed range
            wind_min, wind_max = wind_data.min(), wind_data.max()
            margin = max(1, (wind_max - wind_min) * 0.1)
            ax_wind.set_ylim(max(0, wind_min - margin), wind_max + margin)
            
            # Position wind axis on the right side
            ax_wind.spines['right'].set_position(('outward', 0))
            ax_wind.spines['right'].set_visible(True)
            
            # Store wind axis for legend positioning
            self._wind_axis = ax_wind
        
        # Pressure (secondary y-axis, positioned further right if wind speed exists)
        if 'pressure' in data.columns:
            ax_pressure = ax.twinx()
            if ax_wind is not None:
                # Position pressure axis further to the right
                ax_pressure.spines['right'].set_position(('outward', 60))
            
            # Get pressure colors from configuration
            effective_colors = self.config.get_effective_colors()
            pressure_color = effective_colors.get('pressure', '#2ca02c')
            
            ax_pressure.plot(time_indices, data['pressure'], 
                           color=pressure_color, linewidth=1.5, label='Pressure')
            # Remove axis labels since we're using custom scale legends
            ax_pressure.set_ylabel('', color=pressure_color, fontsize=10)
            ax_pressure.tick_params(axis='y', labelcolor=pressure_color, labelright=False)
            
            # Set pressure range
            pressure_min, pressure_max = data['pressure'].min(), data['pressure'].max()
            margin = max(5, (pressure_max - pressure_min) * 0.1)
            ax_pressure.set_ylim(pressure_min - margin, pressure_max + margin)
            
            # Store pressure axis for legend positioning
            self._pressure_axis = ax_pressure
        
        # Precipitation (bars, positioned as overlay)
        if 'precipitation' in data.columns:
            ax_precip = ax.twinx()
            
            precip_data = np.maximum(data['precipitation'], 0)
            
            # Get precipitation colors from configuration
            effective_colors = self.config.get_effective_colors()
            precip_color = effective_colors.get('precipitation', '#1f77b4')
            
            # Get precipitation variable configuration if available
            precip_config = {}
            if hasattr(self.config, 'variable_config') and self.config.variable_config:
                precip_config = self.config.variable_config.get('precipitation', {})
            
            # Get alpha from config or use default
            alpha = precip_config.get('alpha', 0.7)
            
            # Create edge color (darker version of main color)
            # Convert hex to RGB, darken, and convert back
            if precip_color.startswith('#'):
                hex_color = precip_color[1:]
                rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                # Darken by reducing each component by 30%
                darkened_rgb = tuple(max(0, int(c * 0.7)) for c in rgb)
                edge_color = f"#{darkened_rgb[0]:02x}{darkened_rgb[1]:02x}{darkened_rgb[2]:02x}"
            else:
                edge_color = precip_color  # Fallback if not hex
            
            # Create precipitation bars with configuration-based styling
            bars = ax_precip.bar(time_indices, precip_data, 
                               width=0.6, color=precip_color, alpha=alpha, 
                               edgecolor=edge_color, linewidth=0.8)
            
            # Add precipitation value labels for significant precipitation
            # Get font configuration
            font_config = getattr(self.config, 'fonts', {}) or {}
            label_fontsize = font_config.get('annotation_size', 8)
            label_fontweight = font_config.get('weights', {}).get('annotation', 'bold')
            
            for bar, value in zip(bars, precip_data):
                if value > 0.1:  # Only label significant precipitation
                    # Position label above the bar
                    ax_precip.text(bar.get_x() + bar.get_width()/2,
                                 bar.get_height() + max(0.1, precip_data.max() * 0.02),
                                 f'{value:.1f}',
                                 ha='center', va='bottom',
                                 fontsize=label_fontsize, color=edge_color, fontweight=label_fontweight)
            
            # Set precipitation axis limits and styling
            max_precip = max(5, precip_data.max() * 1.4) if precip_data.max() > 0 else 5
            ax_precip.set_ylim(0, max_precip)
            
            # Hide precipitation axis ticks and spines for cleaner look
            ax_precip.set_yticks([])
            ax_precip.spines['right'].set_visible(False)
            ax_precip.spines['left'].set_visible(False)
            ax_precip.spines['top'].set_visible(False)
            ax_precip.spines['bottom'].set_visible(False)
            
            # Store precipitation axis for legend positioning
            self._precip_axis = ax_precip
        
        # Format main axis with padding
        padding_config = self.config.get_effective_time_axis_padding()
        if padding_config:
            from .components import FormattingUtils
            start_limit, end_limit = FormattingUtils.calculate_padded_xlim(data, padding_config)
            ax.set_xlim(start_limit, end_limit)
        else:
            ax.set_xlim(0, len(data) - 1)
        # Grid lines are now handled centrally by _apply_unified_grid_to_all_panels
        
        # Add time labels with padding configuration
        padding_config = self.config.get_effective_time_axis_padding()
        FormattingUtils.add_time_labels(ax, data, self.time_interval, padding_config)
    
    def _plot_time_axis(self, ax: Axes, data: pd.DataFrame):
        """Plot time axis with date labels."""
        # Get padding configuration and set x-limits
        padding_config = self.config.get_effective_time_axis_padding()
        if padding_config:
            from .components import FormattingUtils
            start_limit, end_limit = FormattingUtils.calculate_padded_xlim(data, padding_config)
            ax.set_xlim(start_limit, end_limit)
        else:
            ax.set_xlim(0, len(data))
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        if data.empty:
            return
        
        # Add date labels at midnight positions
        current_date = None
        for i, timestamp in enumerate(data.index):
            date = timestamp.date()
            if date != current_date:
                current_date = date
                date_str = date.strftime('%Y-%m-%d')
                ax.text(i, 0.5, date_str, ha='left', va='center',
                       fontsize=9, fontweight='normal')
    
    def _apply_unified_grid_to_all_panels(self, axes: List[Axes], data: pd.DataFrame):
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
        day_boundaries = self._detect_day_boundaries(data)
        
        # Get padding configuration
        padding_config = self.config.get_effective_time_axis_padding()
        
        # Calculate x-limits with padding
        if padding_config:
            from .components import FormattingUtils
            start_limit, end_limit = FormattingUtils.calculate_padded_xlim(data, padding_config)
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
                    self._add_custom_vertical_grid(ax, data_length, y_start=0.1, y_end=0.0, day_boundaries=day_boundaries)
                else:
                    # For all other panels, use full height grid lines
                    # Get grid colors from configuration
                    effective_colors = self.config.get_effective_colors()
                    grid_color = effective_colors.get('grid', '#e0e0e0')
                    colors_config = getattr(self.config, 'colors', {}) or {}
                    grid_alpha = colors_config.get('grid_alpha', 0.3)
                    
                    FormattingUtils.add_vertical_grid(
                        ax, 
                        data_length, 
                        grid_line_interval=self.grid_interval,
                        grid_line_color=grid_color, 
                        grid_transparency=grid_alpha,
                        day_boundary_indices=day_boundaries
                    )
                
                # Skip automatic horizontal grid lines for main parameters panel (index 7)
                # The horizontal grid lines will be drawn by the legend functions to ensure alignment
                if i > 0 and i != 7:  # Skip hour labels panel (index 0) and main parameters panel (index 7)
                    FormattingUtils.add_horizontal_grid(
                        ax,
                        color=grid_color,
                        alpha=grid_alpha,
                        linestyle=':',
                        linewidth=0.5
                    )
    
    def _calculate_shared_grid_system(self, ax_main: Axes, data: pd.DataFrame):
        """Calculate shared grid lines for all variables and store them for legend alignment.
        
        Args:
            ax_main: Main parameters axis (temperature axis)
            data: Weather data DataFrame
        """
        from .components import FormattingUtils
        
        # Initialize storage for all grid values
        self._shared_grid_values = {}
        
        # Temperature grid (primary axis)
        if 'temperature' in data.columns:
            temp_min, temp_max = ax_main.get_ylim()
            temp_grid = FormattingUtils.calculate_nice_grid_values(temp_min, temp_max, maximum_grid_lines=6)
            self._shared_grid_values['temperature'] = {
                'values': temp_grid,
                'axis_min': temp_min,
                'axis_max': temp_max,
                'axis': ax_main
            }
        
        # Wind speed grid (if wind axis exists)
        if 'wind_speed' in data.columns and hasattr(self, '_wind_axis'):
            wind_min, wind_max = self._wind_axis.get_ylim()
            wind_grid = FormattingUtils.calculate_nice_grid_values(wind_min, wind_max, maximum_grid_lines=6)
            self._shared_grid_values['wind_speed'] = {
                'values': wind_grid,
                'axis_min': wind_min,
                'axis_max': wind_max,
                'axis': self._wind_axis
            }
        
        # Pressure grid (if pressure axis exists)
        if 'pressure' in data.columns and hasattr(self, '_pressure_axis'):
            pressure_min, pressure_max = self._pressure_axis.get_ylim()
            pressure_grid = FormattingUtils.calculate_nice_grid_values(pressure_min, pressure_max, maximum_grid_lines=6)
            self._shared_grid_values['pressure'] = {
                'values': pressure_grid,
                'axis_min': pressure_min,
                'axis_max': pressure_max,
                'axis': self._pressure_axis
            }
        
        # Precipitation grid (if precipitation axis exists)
        if 'precipitation' in data.columns and hasattr(self, '_precip_axis'):
            precip_min, precip_max = self._precip_axis.get_ylim()
            precip_grid = FormattingUtils.calculate_nice_grid_values(precip_min, precip_max, maximum_grid_lines=6)
            # Filter out negative values for precipitation
            precip_grid = [val for val in precip_grid if val >= 0]
            self._shared_grid_values['precipitation'] = {
                'values': precip_grid,
                'axis_min': precip_min,
                'axis_max': precip_max,
                'axis': self._precip_axis
            }
        
        # Dew point uses the same axis as temperature
        if 'dew_point' in data.columns:
            self._shared_grid_values['dew_point'] = self._shared_grid_values.get('temperature', {})
        
        # Humidity would use the same system if it exists
        if 'humidity' in data.columns:
            # Humidity typically ranges 0-100%, so we can create a standard grid
            humidity_grid = [0, 20, 40, 60, 80, 100]
            self._shared_grid_values['humidity'] = {
                'values': humidity_grid,
                'axis_min': 0,
                'axis_max': 100,
                'axis': None  # Would need its own axis
            }
    
    def _draw_shared_horizontal_grid_lines(self):
        """Draw shared horizontal grid lines across the main plot for all variables."""
        if not hasattr(self, '_shared_grid_values'):
            return
        
        # Get grid styling
        effective_colors = self.config.get_effective_colors()
        grid_color = effective_colors.get('grid', '#e0e0e0')
        
        # Draw grid lines for temperature (primary axis) - these are the main shared lines
        if 'temperature' in self._shared_grid_values:
            temp_info = self._shared_grid_values['temperature']
            for temp_val in temp_info['values']:
                temp_info['axis'].axhline(y=temp_val, color=grid_color, 
                                        linestyle='-', alpha=0.3, linewidth=0.5, zorder=0)
        
        # Draw grid lines for other axes (lighter/dotted to distinguish)
        for var_name, var_info in self._shared_grid_values.items():
            if var_name != 'temperature' and var_info.get('axis') is not None:
                for val in var_info['values']:
                    var_info['axis'].axhline(y=val, color=grid_color, 
                                           linestyle=':', alpha=0.2, linewidth=0.5, zorder=0)

    def _detect_day_boundaries(self, data: pd.DataFrame) -> List[int]:
        """Detect indices where day boundaries occur in the data.
        
        Args:
            data: Weather data DataFrame with datetime index
            
        Returns:
            List of indices where day changes occur
        """
        day_boundaries = []
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
    
    def _add_custom_vertical_grid(self, ax: Axes, data_length: int, y_start: float = 1.0, y_end: float = 0.0, day_boundaries: list = None):
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
                    is_day_boundary = any(abs(pos - boundary) < 0.5 for boundary in day_boundaries)
                    linewidth = 1.5 if is_day_boundary else 0.5
                    
                    ax.plot([pos, pos], [y_start, y_end], 
                           color='gray', linestyle='-', alpha=0.3, linewidth=linewidth)
    
    def _add_left_side_legends(self, ax: Axes, data: pd.DataFrame, label_padding=None):
        """Add legends on the left side for temperature and wind speed.
        
        Args:
            ax: Main parameters axis
            data: Weather data DataFrame
            label_padding: LabelPaddingConfig for custom positioning
        """
        fig = ax.get_figure()
        fig.canvas.draw()  # Force drawing to get final positions
        bbox = ax.get_position()
        
        # Use configurable positioning or defaults
        legend_x = 0.02  # Default left side position
        unit_offset = 0.05  # Default offset for unit labels
        
        if label_padding:
            # Handle both dictionary and object-style label padding
            if isinstance(label_padding, dict):
                legend_x = label_padding.get('left_legend_x', legend_x)
                unit_offset = label_padding.get('left_unit_offset', unit_offset)
            else:
                legend_x = getattr(label_padding, 'left_legend_x', legend_x)
                unit_offset = getattr(label_padding, 'left_unit_offset', unit_offset)
        
        # Temperature scale (if temperature data exists)
        if 'temperature' in data.columns and hasattr(self, '_shared_grid_values'):
            colors = self.config.get_effective_colors()
            
            # Use shared grid values for temperature
            temp_info = self._shared_grid_values.get('temperature', {})
            if temp_info:
                temp_values = temp_info['values']
                temp_min = temp_info['axis_min']
                temp_max = temp_info['axis_max']
                temp_range = temp_max - temp_min
                
                # Position temperature legend values at the shared grid line positions
                for temp_val in temp_values:
                    # Convert temperature value to y position in figure coordinates
                    y_pos_axis = (temp_val - temp_min) / temp_range  # Position in axis (0-1)
                    y_pos_fig = bbox.y0 + y_pos_axis * bbox.height  # Convert to figure coordinates
                    
                    fig.text(legend_x, y_pos_fig, f'{int(temp_val)}°', 
                            fontsize=9, va='center', ha='left',
                            color=colors['temperature_above'], fontweight='normal',
                            transform=fig.transFigure)
                
                # Add temperature unit label above the highest scale number
                if temp_values:
                    highest_temp = max(temp_values)
                    y_pos_axis = (highest_temp - temp_min) / temp_range
                    y_pos_fig = bbox.y0 + y_pos_axis * bbox.height
                    # Position unit label slightly above the highest number
                    temp_label_y = y_pos_fig + 0.02  # Small offset above
                    
                    fig.text(legend_x, temp_label_y, '°C', 
                            fontsize=10, va='center', ha='left',
                            color=colors['temperature_above'], fontweight='bold',
                            transform=fig.transFigure)
        
        # Wind speed scale (if wind speed data exists)
        if 'wind_speed' in data.columns and hasattr(self, '_shared_grid_values'):
            # Add wind speed unit label with horizontal offset to avoid overlap
            wind_legend_x = legend_x + unit_offset  # Offset horizontally from temperature
            
            # Use shared grid values for wind speed
            wind_info = self._shared_grid_values.get('wind_speed', {})
            if wind_info:
                wind_values = wind_info['values']
                wind_min = wind_info['axis_min']
                wind_max = wind_info['axis_max']
                wind_range = wind_max - wind_min
                
                # Get wind color from configuration
                effective_colors = self.config.get_effective_colors()
                wind_color = effective_colors.get('wind', '#ff7f0e')
                
                # Get font configuration
                font_config = getattr(self.config, 'fonts', {}) or {}
                legend_fontsize = font_config.get('tick_size', 9)
                legend_fontweight = font_config.get('weights', {}).get('tick', 'normal')
                
                # Position wind speed legend values at the shared grid positions
                for wind_val in wind_values:
                    # Convert wind speed value to y position in figure coordinates
                    y_pos_axis = (wind_val - wind_min) / wind_range
                    y_pos_fig = bbox.y0 + y_pos_axis * bbox.height
                    
                    fig.text(wind_legend_x, y_pos_fig, f'{int(wind_val)}', 
                            fontsize=legend_fontsize, va='center', ha='left',
                            color=wind_color, fontweight=legend_fontweight,
                            transform=fig.transFigure)
                
                # Add wind speed unit label above the highest scale number
                if wind_values:
                    highest_wind = max(wind_values)
                    y_pos_axis = (highest_wind - wind_min) / wind_range
                    y_pos_fig = bbox.y0 + y_pos_axis * bbox.height
                    # Position unit label slightly above the highest number
                    wind_label_y = y_pos_fig + 0.02  # Small offset above
                    
                    # Get unit from variable config or use default
                    wind_config = {}
                    if hasattr(self.config, 'variable_config') and self.config.variable_config:
                        wind_config = self.config.variable_config.get('wind_speed', {})
                    unit_label = wind_config.get('unit', 'm/s')
                    
                    fig.text(wind_legend_x, wind_label_y, unit_label, 
                            fontsize=10, va='center', ha='left',
                            color=wind_color, fontweight='bold',
                            transform=fig.transFigure)

    def _add_right_side_legends(self, ax: Axes, data: pd.DataFrame, label_padding=None):
        """Add legends on the right side for pressure and precipitation.
        
        Args:
            ax: Main parameters axis
            data: Weather data DataFrame
            label_padding: LabelPaddingConfig for custom positioning
        """
        fig = ax.get_figure()
        fig.canvas.draw()  # Force drawing to get final positions
        bbox = ax.get_position()
        
        # Use configurable positioning or defaults
        legend_x = 0.98  # Default right side position
        unit_offset = 0.05  # Default offset for unit labels
        
        if label_padding:
            # Handle both dictionary and object-style label padding
            if isinstance(label_padding, dict):
                legend_x = label_padding.get('right_legend_x', legend_x)
                unit_offset = label_padding.get('right_unit_offset', unit_offset)
            else:
                legend_x = getattr(label_padding, 'right_legend_x', legend_x)
                unit_offset = getattr(label_padding, 'right_unit_offset', unit_offset)
        
        # Precipitation scale (if precipitation data exists)
        if 'precipitation' in data.columns and hasattr(self, '_shared_grid_values'):
            # Use shared grid values for precipitation
            precip_info = self._shared_grid_values.get('precipitation', {})
            if precip_info:
                precip_values = precip_info['values']
                precip_min = precip_info['axis_min']
                precip_max = precip_info['axis_max']
                precip_range = precip_max - precip_min
                
                # Get precipitation colors from configuration
                effective_colors = self.config.get_effective_colors()
                precip_color = effective_colors.get('precipitation', '#1f77b4')
                
                # Get font configuration
                font_config = getattr(self.config, 'fonts', {}) or {}
                legend_fontsize = font_config.get('tick_size', 9)
                legend_fontweight = font_config.get('weights', {}).get('tick', 'normal')
                
                # Position precipitation legend values at the shared grid positions
                for precip_val in precip_values:
                    # Convert precipitation value to y position in figure coordinates
                    y_pos_axis = (precip_val - precip_min) / precip_range
                    y_pos_fig = bbox.y0 + y_pos_axis * bbox.height
                    
                    fig.text(legend_x, y_pos_fig, f'{int(precip_val)}', 
                            fontsize=legend_fontsize, va='center', ha='right',
                            color=precip_color, fontweight=legend_fontweight,
                            transform=fig.transFigure)
                
                # Add precipitation unit label above the highest scale number
                if precip_values:
                    highest_precip = max(precip_values)
                    y_pos_axis = (highest_precip - precip_min) / precip_range
                    y_pos_fig = bbox.y0 + y_pos_axis * bbox.height
                    # Position unit label slightly above the highest number
                    precip_label_y = y_pos_fig + 0.02  # Small offset above
                    
                    # Get unit from variable config or use default
                    precip_config = {}
                    if hasattr(self.config, 'variable_config') and self.config.variable_config:
                        precip_config = self.config.variable_config.get('precipitation', {})
                    unit_label = precip_config.get('unit', 'mm')
                    
                    fig.text(legend_x, precip_label_y, unit_label, 
                            fontsize=10, va='center', ha='right',
                            color=precip_color, fontweight='bold',
                            transform=fig.transFigure)
        
        # Pressure scale (if pressure data exists)
        if 'pressure' in data.columns and hasattr(self, '_shared_grid_values'):
            # Add pressure unit label with horizontal offset to avoid overlap
            pressure_legend_x = legend_x - unit_offset  # Offset horizontally from precipitation
            
            # Use shared grid values for pressure
            pressure_info = self._shared_grid_values.get('pressure', {})
            if pressure_info:
                pressure_values = pressure_info['values']
                pressure_min = pressure_info['axis_min']
                pressure_max = pressure_info['axis_max']
                pressure_range = pressure_max - pressure_min
                
                # Get pressure colors from configuration
                effective_colors = self.config.get_effective_colors()
                pressure_color = effective_colors.get('pressure', '#2ca02c')
                
                # Get font configuration
                font_config = getattr(self.config, 'fonts', {}) or {}
                legend_fontsize = font_config.get('tick_size', 9)
                legend_fontweight = font_config.get('weights', {}).get('tick', 'normal')
                
                # Position pressure legend values at the shared grid positions
                for pressure_val in pressure_values:
                    # Convert pressure value to y position in figure coordinates
                    y_pos_axis = (pressure_val - pressure_min) / pressure_range
                    y_pos_fig = bbox.y0 + y_pos_axis * bbox.height
                    
                    fig.text(pressure_legend_x, y_pos_fig, f'{int(pressure_val)}', 
                            fontsize=legend_fontsize, va='center', ha='right',
                            color=pressure_color, fontweight=legend_fontweight,
                            transform=fig.transFigure)
                
                # Add pressure unit label above the highest scale number
                if pressure_values:
                    highest_pressure = max(pressure_values)
                    y_pos_axis = (highest_pressure - pressure_min) / pressure_range
                    y_pos_fig = bbox.y0 + y_pos_axis * bbox.height
                    # Position unit label slightly above the highest number
                    pressure_label_y = y_pos_fig + 0.02  # Small offset above
                    
                    # Get unit from variable config or use default
                    pressure_config = {}
                    if hasattr(self.config, 'variable_config') and self.config.variable_config:
                        pressure_config = self.config.variable_config.get('pressure', {})
                    unit_label = pressure_config.get('unit', 'hPa')
                    
                    fig.text(pressure_legend_x, pressure_label_y, unit_label, 
                            fontsize=10, va='center', ha='right',
                            color=pressure_color, fontweight='bold',
                            transform=fig.transFigure)