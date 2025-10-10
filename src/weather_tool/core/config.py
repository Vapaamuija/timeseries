"""Configuration management for weather tool."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class APIConfig:
    """Configuration for API access."""
    base_url: str = "https://api.met.no/weatherapi/locationforecast/2.0"
    user_agent: str = "weather-tool/0.1.0"
    timeout: int = 30
    rate_limit_delay: float = 1.0


@dataclass
class THREDDSConfig:
    """Configuration for THREDDS server access."""
    base_url: str = "https://thredds.met.no/thredds/catalog.html"
    data_path: str = "/lustre/storeB/immutable/archive/projects/metproduction"
    timeout: int = 60
    max_retries: int = 3


@dataclass
class PlottingConfig:
    """Configuration for plotting."""
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
    
    # Weather symbols
    include_weather_symbols: bool = True
    symbol_size: int = 20
    symbol_type: str = "svg"  # Default symbol type
    
    # Dynamic plotting settings
    variables_to_plot: Optional[List[str]] = None
    plot_layout: str = "auto"
    max_variables_per_plot: int = 6
    
    # Variable configuration - defines how each variable is plotted
    variable_config: Optional[Dict[str, Dict[str, Any]]] = None


@dataclass
class Config:
    """Main configuration class."""
    
    api: APIConfig = field(default_factory=APIConfig)
    thredds: THREDDSConfig = field(default_factory=THREDDSConfig)
    plotting: PlottingConfig = field(default_factory=PlottingConfig)
    
    # Data directories
    data_dir: Path = field(default_factory=lambda: Path("data"))
    cache_dir: Path = field(default_factory=lambda: Path("data/cache"))
    output_dir: Path = field(default_factory=lambda: Path("output"))
    
    # Logging
    log_level: str = "DEBUG"
    log_file: Optional[str] = None
    
    # Processing
    max_workers: int = 4
    chunk_size: int = 1000
    
    # T-series specific configuration
    tseries_grid_interval: int = 1
    tseries_time_interval: int = 1
    
    # Time axis padding configuration
    time_axis_padding: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_file(cls, config_path: str) -> "Config":
        """Load configuration from YAML file."""
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create configuration from dictionary."""
        config = cls()
        
        if "api" in data:
            config.api = APIConfig(**data["api"])
        
        if "thredds" in data:
            config.thredds = THREDDSConfig(**data["thredds"])
        
        if "plotting" in data:
            config.plotting = PlottingConfig(**data["plotting"])
        
        # Handle other fields
        for key, value in data.items():
            if key not in ["api", "thredds", "plotting"] and hasattr(config, key):
                if key.endswith("_dir"):
                    setattr(config, key, Path(value))
                else:
                    setattr(config, key, value)
        
        return config
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        config = cls()
        
        # API configuration
        if os.getenv("WEATHER_API_BASE_URL"):
            config.api.base_url = os.getenv("WEATHER_API_BASE_URL")
        if os.getenv("WEATHER_API_USER_AGENT"):
            config.api.user_agent = os.getenv("WEATHER_API_USER_AGENT")
        
        # THREDDS configuration
        if os.getenv("WEATHER_THREDDS_BASE_URL"):
            config.thredds.base_url = os.getenv("WEATHER_THREDDS_BASE_URL")
        if os.getenv("WEATHER_THREDDS_DATA_PATH"):
            config.thredds.data_path = os.getenv("WEATHER_THREDDS_DATA_PATH")
        
        # Directories
        if os.getenv("WEATHER_DATA_DIR"):
            config.data_dir = Path(os.getenv("WEATHER_DATA_DIR"))
        if os.getenv("WEATHER_OUTPUT_DIR"):
            config.output_dir = Path(os.getenv("WEATHER_OUTPUT_DIR"))
        
        return config
    
    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        for dir_path in [self.data_dir, self.cache_dir, self.output_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "api": {
                "base_url": self.api.base_url,
                "user_agent": self.api.user_agent,
                "timeout": self.api.timeout,
                "rate_limit_delay": self.api.rate_limit_delay,
            },
            "thredds": {
                "base_url": self.thredds.base_url,
                "data_path": self.thredds.data_path,
                "timeout": self.thredds.timeout,
                "max_retries": self.thredds.max_retries,
            },
            "plotting": {
                # Basic plotting settings
                "figure_size": self.plotting.figure_size,
                "dpi": self.plotting.dpi,
                "style": self.plotting.style,
                "color_palette": self.plotting.color_palette,
                "tight_layout": self.plotting.tight_layout,
                "constrained_layout": self.plotting.constrained_layout,
                
                # Font configuration
                "fonts": self.plotting.fonts,
                
                # Color configuration
                "colors": self.plotting.colors,
                
                # Layout configuration
                "layout": self.plotting.layout,
                
                # Weather symbols
                "include_weather_symbols": self.plotting.include_weather_symbols,
                "symbol_size": self.plotting.symbol_size,
                "symbol_type": self.plotting.symbol_type,
                
                # Dynamic plotting settings
                "variables_to_plot": self.plotting.variables_to_plot,
                "plot_layout": self.plotting.plot_layout,
                "max_variables_per_plot": self.plotting.max_variables_per_plot,
                
                # Variable configuration
                "variable_config": self.plotting.variable_config,
            },
            "data_dir": str(self.data_dir),
            "cache_dir": str(self.cache_dir),
            "output_dir": str(self.output_dir),
            "log_level": self.log_level,
            "log_file": self.log_file,
            "max_workers": self.max_workers,
            "chunk_size": self.chunk_size,
            "tseries_grid_interval": self.tseries_grid_interval,
            "tseries_time_interval": self.tseries_time_interval,
            "time_axis_padding": self.time_axis_padding,
        }
    
    def save_to_file(self, config_path: str) -> None:
        """Save configuration to YAML file."""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, indent=2)
