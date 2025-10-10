"""
Plotting interfaces and protocols.

This module defines clean interfaces for all plotting functionality,
making it easy to add new plot types and visualization styles.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.axes import Axes


class PlotStyle(Enum):
    """Available plot styles."""
    NORWEGIAN_METEOGRAM = "norwegian_meteogram"  # Norwegian meteogram diagram


class SymbolType(Enum):
    """Weather symbol types."""
    SVG = "svg"                # SVG icons from Met.no repository (only supported type)


@dataclass
class PlotConfig:
    """Configuration for plot appearance."""
    # Basic plotting settings
    figure_size: tuple = (12, 8)
    dpi: int = 300
    style: str = "whitegrid"
    color_palette: str = "husl"
    tight_layout: bool = True
    constrained_layout: bool = False
    
    # Font configuration
    fonts: Optional[Dict[str, Any]] = None
    
    # Color configuration
    colors: Optional[Dict[str, Any]] = None
    
    # Layout configuration
    layout: Optional[Dict[str, Any]] = None
    
    # Grid settings
    grid_enabled: bool = True
    grid_style: str = "dashed"
    grid_color: str = "grey"
    grid_alpha: float = 0.3
    
    # Symbol settings - Default to SVG icons from metno_weather_icons/
    symbol_type: SymbolType = SymbolType.SVG
    symbol_size: int = 20
    auto_download_icons: bool = True  # Automatically download Met.no icons if needed
    
    # Weather symbols
    include_weather_symbols: bool = True
    
    # Dynamic plotting settings
    variables_to_plot: Optional[List[str]] = None  # If None, auto-select based on data
    plot_layout: str = "auto"  # auto, grid, vertical, horizontal
    show_symbols: bool = True
    show_grid: bool = True
    
    # T-series specific
    tseries_height_ratios: List[float] = None
    tseries_grid_interval: int = 1
    tseries_time_interval: int = 1
    
    # Time axis padding configuration
    time_axis_padding: Optional[Dict[str, Any]] = None
    
    # Variable configuration - defines how each variable is plotted
    variable_config: Optional[Dict[str, Dict[str, Any]]] = None
    
    def get_effective_colors(self) -> Dict[str, str]:
        """Get effective color configuration from variable_config and colors sections."""
        colors = {}
        
        # Get UI colors from colors section
        if self.colors:
            colors.update({
                'background': self.colors.get('background', '#ffffff'),
                'text': self.colors.get('text', '#333333'),
                'grid': self.colors.get('grid', '#e0e0e0')
            })
        else:
            colors.update({
                'background': '#ffffff',
                'text': '#333333',
                'grid': self.grid_color
            })
        
        # Get variable colors from variable_config section
        if self.variable_config:
            # Temperature colors (special case with positive/negative)
            temp_config = self.variable_config.get('temperature', {})
            colors['temperature_above'] = temp_config.get('color_positive', '#d62728')
            colors['temperature_below'] = temp_config.get('color_negative', '#1f77b4')
            
            # Other variable colors
            dew_config = self.variable_config.get('dew_point', {})
            colors['dew_point'] = dew_config.get('color', '#17becf')
            
            pressure_config = self.variable_config.get('pressure', {})
            colors['pressure'] = pressure_config.get('color', '#2ca02c')
            
            precip_config = self.variable_config.get('precipitation', {})
            colors['precipitation'] = precip_config.get('color', '#1f77b4')
            
            wind_config = self.variable_config.get('wind_speed', {})
            colors['wind'] = wind_config.get('color', '#ff7f0e')
            
            humidity_config = self.variable_config.get('humidity', {})
            colors['humidity'] = humidity_config.get('color', '#9467bd')
            
            cloud_config = self.variable_config.get('cloud_cover', {})
            colors['cloud_cover'] = cloud_config.get('color', '#8c564b')
        else:
            # Fallback to default colors if no variable_config
            colors.update({
                'temperature_above': '#d62728',
                'temperature_below': '#1f77b4',
                'dew_point': '#17becf',
                'pressure': '#2ca02c',
                'precipitation': '#1f77b4',
                'wind': '#ff7f0e',
                'humidity': '#9467bd',
                'cloud_cover': '#8c564b'
            })
        
        return colors
    
    def get_effective_layout_config(self):
        """Get effective layout configuration including padding settings."""
        return self.layout
    
    def get_effective_panel_padding(self):
        """Get effective panel padding configuration."""
        return self.layout.get('panel_padding') if self.layout else None
    
    def get_effective_label_padding(self):
        """Get effective label padding configuration."""
        return self.layout.get('label_padding') if self.layout else None
    
    def get_effective_time_axis_padding(self):
        """Get effective time axis padding configuration."""
        if self.time_axis_padding:
            return {
                'start_padding': self.time_axis_padding.get('start_padding', 0.05),
                'end_padding': self.time_axis_padding.get('end_padding', 0.05),
                'start_padding_hours': self.time_axis_padding.get('start_padding_hours'),
                'end_padding_hours': self.time_axis_padding.get('end_padding_hours')
            }
        # Default padding configuration
        return {
            'start_padding': 0.05,
            'end_padding': 0.05,
            'start_padding_hours': None,
            'end_padding_hours': None
        }


class WeatherPlotter(ABC):
    """Abstract base class for all weather plotters."""
    
    def __init__(self, config: PlotConfig):
        """Initialize the plotter.
        
        Args:
            config: Plot configuration
        """
        self.config = config
    
    @abstractmethod
    def create_plot(
        self,
        data: pd.DataFrame,
        airport: Dict[str, Any],
        **kwargs
    ) -> Figure:
        """Create a weather plot.
        
        Args:
            data: Weather data DataFrame with standardized columns
            airport: Airport information dictionary
            **kwargs: Additional plot-specific parameters
            
        Returns:
            matplotlib Figure object
        """
        raise NotImplementedError("Subclasses must implement create_plot")
    
    @abstractmethod
    def get_supported_variables(self) -> List[str]:
        """Get list of variables this plotter can display.
        
        Returns:
            List of supported variable names
        """
        return []
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate that data contains required variables.
        
        Args:
            data: Weather data DataFrame
            
        Returns:
            True if data is valid for this plotter
        """
        required_vars = self.get_required_variables()
        return all(var in data.columns for var in required_vars)
    
    def get_required_variables(self) -> List[str]:
        """Get minimum required variables for this plotter.
        
        Returns:
            List of required variable names
        """
        return ['temperature']  # Default minimum requirement


class WeatherSymbolRenderer(ABC):
    """Abstract base class for weather symbol renderers."""
    
    def __init__(self, config: PlotConfig):
        """Initialize the symbol renderer.
        
        Args:
            config: Plot configuration
        """
        self.config = config
    
    @abstractmethod
    def add_symbols_to_plot(
        self,
        ax: Axes,
        data: pd.DataFrame,
        y_position: Optional[float] = None,
        **kwargs
    ) -> int:
        """Add weather symbols to a plot.
        
        Args:
            ax: matplotlib Axes object
            data: DataFrame with 'weather_symbol' column
            y_position: Y position for symbols
            **kwargs: Additional renderer-specific parameters
            
        Returns:
            Number of symbols added
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_symbol_info(self, symbol_code: str) -> Optional[Dict[str, Any]]:
        """Get information about a weather symbol.
        
        Args:
            symbol_code: Weather symbol code
            
        Returns:
            Dictionary with symbol information
        """
        raise NotImplementedError
    
    def get_supported_symbols(self) -> List[str]:
        """Get list of supported weather symbol codes.
        
        Returns:
            List of supported symbol codes
        """
        return []


class PlotterRegistry:
    """Registry for managing multiple plotters."""
    
    def __init__(self):
        """Initialize the registry."""
        self.plotters = {}
        self.symbol_renderers = {}
    
    def register_plotter(self, name: str, plotter_class: type, is_default: bool = False):
        """Register a plotter class.
        
        Args:
            name: Plotter name
            plotter_class: Plotter class
            is_default: Whether this is the default plotter for its style
        """
        self.plotters[name] = {
            'class': plotter_class,
            'is_default': is_default
        }
    
    def register_symbol_renderer(self, name: str, renderer_class: type, is_default: bool = False):
        """Register a symbol renderer class.
        
        Args:
            name: Renderer name
            renderer_class: Renderer class
            is_default: Whether this is the default renderer
        """
        self.symbol_renderers[name] = {
            'class': renderer_class,
            'is_default': is_default
        }
    
    def get_plotter(self, name: str, config: PlotConfig) -> Optional[WeatherPlotter]:
        """Get a plotter instance by name.
        
        Args:
            name: Plotter name
            config: Plot configuration
            
        Returns:
            Plotter instance or None
        """
        plotter_info = self.plotters.get(name)
        if plotter_info:
            return plotter_info['class'](config)
        return None
    
    def get_symbol_renderer(self, name: str, config: PlotConfig) -> Optional[WeatherSymbolRenderer]:
        """Get a symbol renderer instance by name.
        
        Args:
            name: Renderer name
            config: Plot configuration
            
        Returns:
            Symbol renderer instance or None
        """
        renderer_info = self.symbol_renderers.get(name)
        if renderer_info:
            return renderer_info['class'](config)
        return None
    
    def get_default_plotter(self, style: PlotStyle, config: PlotConfig) -> Optional[WeatherPlotter]:
        """Get the default plotter for a style.
        
        Args:
            style: Plot style
            config: Plot configuration
            
        Returns:
            Default plotter instance or None
        """
        # Find default plotter for this style
        for name, info in self.plotters.items():
            if info['is_default'] and style.value in name.lower():
                return info['class'](config)
        
        # Fallback to first available plotter
        if self.plotters:
            first_plotter = next(iter(self.plotters.values()))
            return first_plotter['class'](config)
        
        return None
    
    def list_plotters(self) -> Dict[str, Dict[str, Any]]:
        """List all registered plotters.
        
        Returns:
            Dictionary of plotter information
        """
        return {name: {'is_default': info['is_default']} for name, info in self.plotters.items()}
    
    def list_symbol_renderers(self) -> Dict[str, Dict[str, Any]]:
        """List all registered symbol renderers.
        
        Returns:
            Dictionary of renderer information
        """
        return {name: {'is_default': info['is_default']} for name, info in self.symbol_renderers.items()}


# Global registry instance
plotting_registry = PlotterRegistry()
