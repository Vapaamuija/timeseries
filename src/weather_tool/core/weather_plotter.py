"""Main weather plotting class."""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import pandas as pd

# import matplotlib.dates as mdates  # Unused for now
from matplotlib.figure import Figure

from ..airports.manager import AirportManager
from ..data.interfaces import DataClientRegistry, WeatherDataClient
from ..data.metno_unified import MetNoFileClient, MetNoHTTPClient, MetNoUnifiedClient
from ..plotting.interfaces import PlotConfig, SymbolType as PlotSymbolType
from ..plotting.plotters import MeteogramPlotter
from ..plotting.symbols import UnifiedWeatherSymbols
from .config import Config

logger = logging.getLogger(__name__)


class WeatherPlotter:
    """Main class for weather data plotting."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize weather plotter.

        Args:
            config: Configuration object. If None, uses default configuration.
        """
        self.config = config or Config()
        self.config.ensure_directories()

        # Initialize components
        self.airport_manager = AirportManager(self.config)

        # Clean unified data architecture
        self.data_registry = DataClientRegistry()

        # Met.no clients (unified, HTTP, file)
        self.metno_client = MetNoUnifiedClient(
            self.config
        )  # Primary: HTTP + File combined
        self.http_client = MetNoHTTPClient(self.config)  # HTTP API only
        self.file_client = MetNoFileClient(self.config)  # THREDDS files only

        # Register clients with priority
        self.data_registry.register_client("metno", self.metno_client, priority=100)
        self.data_registry.register_client("http", self.http_client, priority=80)
        self.data_registry.register_client("file", self.file_client, priority=60)

        # Convert symbol_type string to enum
        symbol_type = PlotSymbolType.SVG  # Default (only supported type)
        if hasattr(self.config.plotting, "symbol_type"):
            symbol_type_str = self.config.plotting.symbol_type.lower()
            if symbol_type_str == "svg":
                symbol_type = PlotSymbolType.SVG

        # Plotting components - unified architecture
        plot_config = PlotConfig(
            # Basic plotting settings
            figure_size=self.config.plotting.figure_size,
            dpi=self.config.plotting.dpi,
            style=self.config.plotting.style,
            color_palette=self.config.plotting.color_palette,
            tight_layout=self.config.plotting.tight_layout,
            constrained_layout=self.config.plotting.constrained_layout,
            # Font configuration
            fonts=self.config.plotting.fonts,
            # Color configuration
            colors=self.config.plotting.colors,
            # Layout configuration
            layout=self.config.plotting.layout,
            # Symbol settings
            symbol_type=symbol_type,
            symbol_size=self.config.plotting.symbol_size,
            include_weather_symbols=self.config.plotting.include_weather_symbols,
            # Dynamic plotting settings
            variables_to_plot=self.config.plotting.variables_to_plot,
            plot_layout=self.config.plotting.plot_layout,
            # T-series specific
            tseries_grid_interval=self.config.tseries_grid_interval,
            tseries_time_interval=self.config.tseries_time_interval,
            # Time axis padding configuration
            time_axis_padding=getattr(self.config, "time_axis_padding", None),
            # Variable configuration
            variable_config=self.config.plotting.variable_config,
        )

        self.plot_config = plot_config
        # Only meteogram plotter is supported
        self.meteogram_plotter = MeteogramPlotter(plot_config)
        self.symbol_renderer = UnifiedWeatherSymbols(plot_config)

        # Set up matplotlib
        self._setup_matplotlib()

        logger.info("WeatherPlotter initialized")

    def _setup_matplotlib(self) -> None:
        """Configure matplotlib settings."""
        self._setup_matplotlib_style()
        self._setup_matplotlib_basic_params()
        self._setup_matplotlib_fonts()
        self._setup_matplotlib_colors()

    def _setup_matplotlib_style(self) -> None:
        """Set matplotlib style."""
        try:
            plt.style.use(self.config.plotting.style)
        except OSError:
            # Fallback to default style if seaborn style not available
            plt.style.use("default")

    def _setup_matplotlib_basic_params(self) -> None:
        """Set basic matplotlib parameters."""
        # Get font size from configuration
        font_size = 10  # default
        if self.config.plotting.fonts and "base_size" in self.config.plotting.fonts:
            font_size = self.config.plotting.fonts["base_size"]

        plt.rcParams.update(
            {
                "font.size": font_size,
                "figure.dpi": self.config.plotting.dpi,
                "savefig.dpi": self.config.plotting.dpi,
                "figure.figsize": self.config.plotting.figure_size,
                "figure.autolayout": (
                    False
                ),  # Disable automatic layout to prevent warnings
                "figure.constrained_layout.use": (
                    False
                ),  # Also disable constrained layout
            }
        )

    def _setup_matplotlib_fonts(self) -> None:
        """Apply font settings if available."""
        if self.config.plotting.fonts:
            fonts_config = self.config.plotting.fonts
            if "family" in fonts_config:
                plt.rcParams["font.family"] = fonts_config["family"]
            if "title_size" in fonts_config:
                plt.rcParams["figure.titlesize"] = fonts_config["title_size"]

    def _setup_matplotlib_colors(self) -> None:
        """Apply color settings if available."""
        if self.config.plotting.colors:
            colors_config = self.config.plotting.colors
            if "background" in colors_config:
                plt.rcParams["figure.facecolor"] = colors_config["background"]
                plt.rcParams["axes.facecolor"] = colors_config["background"]
            if "text" in colors_config:
                plt.rcParams["text.color"] = colors_config["text"]
                plt.rcParams["axes.labelcolor"] = colors_config["text"]
                plt.rcParams["xtick.color"] = colors_config["text"]
                plt.rcParams["ytick.color"] = colors_config["text"]
            if "grid" in colors_config:
                plt.rcParams["grid.color"] = colors_config["grid"]
            if "grid_alpha" in colors_config:
                plt.rcParams["grid.alpha"] = colors_config["grid_alpha"]

    def plot_airport(
        self,
        icao_code: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        variables: Optional[List[str]] = None,
        data_source: str = "auto",
        output_path: Optional[str] = None,
        symbol_type: Optional[str] = None,
    ) -> Figure:
        """Plot weather data for a single airport.

        Args:
            icao_code: ICAO code of the airport
            start_time: Start time for data retrieval
            end_time: End time for data retrieval
            variables: List of weather variables to plot
            data_source: Data source ("api", "files", or "auto")
            output_path: Path to save the plot
            symbol_type: Weather symbol type ("ascii", "unicode", or "svg")

        Returns:
            matplotlib Figure object
        """
        logger.info("Plotting weather data for airport %s", icao_code)

        # Get airport information
        airport = self.airport_manager.get_airport(icao_code)
        if not airport:
            raise ValueError(f"Airport {icao_code} not found")

        # Set default time range if not provided
        if not start_time:
            start_time = datetime.now() - timedelta(days=1)
        if not end_time:
            end_time = datetime.now() + timedelta(days=2)

        # Get weather data
        weather_data = self._fetch_weather_data(
            airport, start_time, end_time, variables, data_source
        )

        # Create meteogram plot
        # Create custom plotter if symbol type is specified
        if symbol_type:
            # Convert string to SymbolType enum
            symbol_type_enum = PlotSymbolType(symbol_type.lower())

            # Create custom plot config with specified symbol type
            custom_plot_config = PlotConfig(
                # Basic plotting settings
                figure_size=self.plot_config.figure_size,
                dpi=self.plot_config.dpi,
                style=self.plot_config.style,
                color_palette=self.plot_config.color_palette,
                tight_layout=self.plot_config.tight_layout,
                constrained_layout=self.plot_config.constrained_layout,
                # Font configuration
                fonts=self.plot_config.fonts,
                # Color configuration
                colors=self.plot_config.colors,
                # Layout configuration
                layout=self.plot_config.layout,
                # Symbol settings
                symbol_type=symbol_type_enum,
                symbol_size=self.plot_config.symbol_size,
                auto_download_icons=self.plot_config.auto_download_icons,
                include_weather_symbols=self.plot_config.include_weather_symbols,
                # T-series specific
                tseries_grid_interval=self.plot_config.tseries_grid_interval,
                tseries_time_interval=self.plot_config.tseries_time_interval,
                # Time axis padding configuration
                time_axis_padding=self.plot_config.time_axis_padding,
                # Variable configuration
                variable_config=self.plot_config.variable_config,
            )

            custom_plotter = MeteogramPlotter(custom_plot_config)
            fig = custom_plotter.create_plot(weather_data, airport)
        else:
            # Use default meteogram plotter
            fig = self.meteogram_plotter.create_plot(weather_data, airport)

        # Save plot if output path provided
        if output_path:
            self._save_plot(fig, output_path)

        logger.info("Successfully plotted weather data for %s", icao_code)
        return fig

    def plot_coordinates(
        self,
        latitude: float,
        longitude: float,
        location_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        variables: Optional[List[str]] = None,
        data_source: str = "auto",
        output_path: Optional[str] = None,
        symbol_type: Optional[str] = None,
    ) -> Figure:
        """Plot weather data for given GPS coordinates.

        Args:
            latitude: Latitude in decimal degrees (-90 to 90)
            longitude: Longitude in decimal degrees (-180 to 180)
            location_name: Optional name for the location (used in plot title)
            start_time: Start time for data retrieval
            end_time: End time for data retrieval
            variables: List of weather variables to plot
            data_source: Data source ("api", "files", or "auto")
            output_path: Path to save the plot
            symbol_type: Weather symbol type ("ascii", "unicode", or "svg")

        Returns:
            matplotlib Figure object
        """
        logger.info("Plotting weather data for coordinates %.4f, %.4f", latitude, longitude)

        # Validate coordinates
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Invalid latitude: {latitude}. Must be between -90 and 90")
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Invalid longitude: {longitude}. Must be between -180 and 180")

        # Set default time range if not provided
        if not start_time:
            start_time = datetime.now() - timedelta(days=1)
        if not end_time:
            end_time = datetime.now() + timedelta(days=2)

        # Create location info dictionary (similar to airport structure)
        location_info = {
            "latitude": latitude,
            "longitude": longitude,
            "name": location_name or f"Location ({latitude:.4f}, {longitude:.4f})",
            "icao": None,  # No ICAO code for coordinates
            "country": None,
            "municipality": None,
        }

        # Get weather data
        weather_data = self._fetch_weather_data(
            location_info, start_time, end_time, variables, data_source
        )

        # Create meteogram plot
        # Create custom plotter if symbol type is specified
        if symbol_type:
            # Convert string to SymbolType enum
            symbol_type_enum = PlotSymbolType(symbol_type.lower())

            # Create custom plot config with specified symbol type
            custom_plot_config = PlotConfig(
                # Basic plotting settings
                figure_size=self.plot_config.figure_size,
                dpi=self.plot_config.dpi,
                style=self.plot_config.style,
                color_palette=self.plot_config.color_palette,
                tight_layout=self.plot_config.tight_layout,
                constrained_layout=self.plot_config.constrained_layout,
                # Font configuration
                fonts=self.plot_config.fonts,
                # Color configuration
                colors=self.plot_config.colors,
                # Layout configuration
                layout=self.plot_config.layout,
                # Symbol settings
                symbol_type=symbol_type_enum,
                symbol_size=self.plot_config.symbol_size,
                auto_download_icons=self.plot_config.auto_download_icons,
                include_weather_symbols=self.plot_config.include_weather_symbols,
                # T-series specific
                tseries_grid_interval=self.plot_config.tseries_grid_interval,
                tseries_time_interval=self.plot_config.tseries_time_interval,
                # Time axis padding configuration
                time_axis_padding=self.plot_config.time_axis_padding,
                # Variable configuration
                variable_config=self.plot_config.variable_config,
            )

            custom_plotter = MeteogramPlotter(custom_plot_config)
            fig = custom_plotter.create_plot(weather_data, location_info)
        else:
            # Use default meteogram plotter
            fig = self.meteogram_plotter.create_plot(weather_data, location_info)

        # Save plot if output path provided
        if output_path:
            self._save_plot(fig, output_path)

        return fig

    def plot_multiple_airports(
        self,
        icao_codes: List[str],
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        variables: Optional[List[str]] = None,
        data_source: str = "auto",
        output_dir: Optional[str] = None,
    ) -> Dict[str, Figure]:
        """Plot weather data for multiple airports.

        Args:
            icao_codes: List of ICAO codes
            start_time: Start time for data retrieval
            end_time: End time for data retrieval
            variables: List of weather variables to plot
            data_source: Data source ("api", "files", or "auto")
            output_dir: Directory to save plots

        Returns:
            Dictionary mapping ICAO codes to Figure objects
        """
        logger.info("Plotting weather data for %d airports", len(icao_codes))

        figures = {}

        for icao_code in icao_codes:
            try:
                output_path = None
                if output_dir:
                    output_path = Path(output_dir) / f"{icao_code}_weather.png"

                fig = self.plot_airport(
                    icao_code=icao_code,
                    start_time=start_time,
                    end_time=end_time,
                    variables=variables,
                    data_source=data_source,
                    output_path=str(output_path) if output_path else None,
                )

                figures[icao_code] = fig

            except (ValueError, RuntimeError, OSError, IOError) as e:
                logger.error("Failed to plot data for %s: %s", icao_code, e)
                continue

        logger.info("Successfully plotted data for %d airports", len(figures))
        return figures

    def _fetch_weather_data(
        self,
        airport: Dict[str, Any],
        start_time: datetime,
        end_time: datetime,
        variables: Optional[List[str]],
        data_source: str,
    ) -> pd.DataFrame:
        """Fetch weather data from the appropriate source.

        Args:
            airport: Airport information dictionary
            start_time: Start time for data retrieval
            end_time: End time for data retrieval
            variables: List of weather variables to fetch
            data_source: Data source preference

        Returns:
            DataFrame with weather data
        """
        client = self._get_data_client(data_source)

        return client.get_weather_data(
            latitude=airport["latitude"],
            longitude=airport["longitude"],
            start_time=start_time,
            end_time=end_time,
            variables=variables,
        )

    def _get_data_client(self, data_source: str) -> WeatherDataClient:
        """Get the appropriate data client based on source preference.

        Args:
            data_source: Data source preference ("auto", "metno", "http", "file")

        Returns:
            Weather data client instance
        """
        if data_source == "auto" or data_source == "metno":
            # Use unified Met.no client (primary) - combines HTTP + File
            return self.metno_client
        elif data_source == "http" or data_source == "api":
            # HTTP API client only
            return self.http_client
        elif data_source == "file" or data_source == "files":
            # File server client only
            return self.file_client
        else:
            # Try to get from registry (for extensibility)
            client = self.data_registry.get_client(data_source)
            if client:
                return client
            else:
                raise ValueError(
                    f"Invalid data source: {data_source}. Available: auto, metno, http, file"
                )

    def _save_plot(self, fig: Figure, output_path: str) -> None:
        """Save plot to file.

        Args:
            fig: matplotlib Figure object
            output_path: Path to save the plot
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Save with safe parameters to prevent huge images
        try:
            # Disable tight_layout to prevent warnings with complex layouts
            with plt.rc_context({"figure.autolayout": False}):
                fig.savefig(
                    output_file,
                    dpi=100,  # Fixed safe DPI
                    bbox_inches=None,  # Don't use tight bbox to avoid size issues
                    facecolor="white",
                    edgecolor="none",
                )
        except (OSError, IOError, ValueError, RuntimeError) as e:
            # Fallback with minimal options
            logger.warning("Standard save failed, using fallback: %s", e)
            fig.savefig(output_file, dpi=72, facecolor="white")

        logger.info("Plot saved to %s", output_file)

    def list_available_airports(self) -> List[Dict[str, Any]]:
        """Get list of available airports.

        Returns:
            List of airport dictionaries
        """
        return self.airport_manager.list_airports()

    def search_airports(self, query: str) -> List[Dict[str, Any]]:
        """Search for airports by name or ICAO code.

        Args:
            query: Search query

        Returns:
            List of matching airport dictionaries
        """
        return self.airport_manager.search_airports(query)
