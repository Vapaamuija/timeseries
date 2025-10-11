"""Command-line interface for weather tool."""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, List, Optional

import click
import matplotlib.pyplot as plt
import requests

from .core.config import Config
from .core.weather_plotter import WeatherPlotter
from .utils.helpers import parse_time_range, validate_icao_code
from .utils.logging import setup_logging


@click.group()
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Configuration file path"
)
@click.option("--log-level", default="INFO", help="Logging level")
@click.option("--log-file", help="Log file path")
def main(
    config: Optional[str] = None,
    log_level: str = "INFO",
    log_file: Optional[str] = None,
) -> None:
    """Weather Tool - Airport Time Series Plotting."""
    # Set up logging
    setup_logging(level=log_level, log_file=log_file)

    # Load configuration
    if config:
        config_obj = Config.from_file(config)
        click.echo(f"Loaded configuration from: {config}")
    else:
        # Try to load from default settings.yaml file
        default_config_path = Path("config/settings.yaml")
        if default_config_path.exists():
            config_obj = Config.from_file(str(default_config_path))
            click.echo(f"Loaded configuration from: {default_config_path}")
        else:
            # Fall back to default configuration if settings.yaml doesn't exist
            config_obj = Config()
            click.echo("Using default configuration (config/settings.yaml not found)")

    # Store config in context for subcommands
    click.get_current_context().obj = config_obj
    click.echo("Weather Tool initialized")


@main.command()
@click.argument("icao_code")
@click.option(
    "--start-time", help='Start time (YYYY-MM-DD HH:MM or relative like "24 hours ago")'
)
@click.option("--end-time", help='End time (YYYY-MM-DD HH:MM or relative like "now")')
@click.option(
    "--time-range",
    help='Time range (e.g., "next 6 hours", "last 24 hours", "next 3 days")',
)
@click.option("--variables", help="Comma-separated list of variables to plot")
@click.option(
    "--data-source",
    default="auto",
    type=click.Choice(["auto", "metno", "http", "file"]),
    help="Data source preference",
)
@click.option(
    "--symbols",
    type=click.Choice(["ascii", "unicode", "svg"]),
    help="Weather symbol type",
)
@click.option("--output", "-o", help="Output file path")
@click.option("--show/--no-show", default=False, help="Display plot after creation")
@click.pass_context
def plot(
    ctx: Any,
    icao_code: str,
    start_time: Optional[str],
    end_time: Optional[str],
    time_range: Optional[str],
    variables: Optional[str],
    data_source: Optional[str],
    symbols: Optional[str],
    output: Optional[str],
    show: bool,
) -> None:
    """Plot weather data for a single airport."""
    try:
        # Validate ICAO code
        if not validate_icao_code(icao_code):
            click.echo(f"Error: Invalid ICAO code '{icao_code}'", err=True)
            return

        # Parse time range
        if time_range:
            # Use the time-range argument
            start_dt, end_dt = parse_time_range(time_range)
            if start_dt is None or end_dt is None:
                click.echo(f"Error: Invalid time range '{time_range}'", err=True)
                click.echo(
                    "Examples: 'next 6 hours', 'last 24 hours', 'next 3 days'", err=True
                )
                return
        else:
            # Use individual start/end time arguments or defaults
            if start_time:
                start_dt = datetime.fromisoformat(start_time.replace("T", " "))
            else:
                start_dt = datetime.now() - timedelta(days=1)

            if end_time:
                end_dt = datetime.fromisoformat(end_time.replace("T", " "))
            else:
                end_dt = datetime.now() + timedelta(days=2)

        # Parse variables
        var_list = None
        if variables:
            var_list = [v.strip() for v in variables.split(",")]

        # Create plotter
        plotter = WeatherPlotter(ctx.obj)

        click.echo(f"Plotting weather data for {icao_code}...")

        # Create plot with new options (always meteogram style)
        plotter.plot_airport(
            icao_code=icao_code,
            start_time=start_dt,
            end_time=end_dt,
            variables=var_list,
            data_source=data_source or "auto",
            output_path=output,
            symbol_type=symbols,
        )

        if show:
            plt.show()

        click.echo("Plot created successfully!")

    except (ValueError, RuntimeError, OSError, IOError, FileNotFoundError) as e:
        click.echo(f"Error: {e}", err=True)
        logging.error("Plot command failed: %s", e)


@main.command()
@click.argument("icao_codes")
@click.option("--start-time", help="Start time (YYYY-MM-DD HH:MM)")
@click.option("--end-time", help="End time (YYYY-MM-DD HH:MM)")
@click.option(
    "--time-range",
    help='Time range (e.g., "next 6 hours", "last 24 hours", "next 3 days")',
)
@click.option("--variables", help="Comma-separated list of variables to plot")
@click.option(
    "--data-source",
    default="auto",
    type=click.Choice(["auto", "api", "files"]),
    help="Data source preference",
)
@click.option("--output-dir", "-o", help="Output directory for plots")
@click.option("--show-symbols/--no-symbols", default=None, help="Show weather symbols")
@click.pass_context
def plot_multiple(
    ctx: Any,
    icao_codes: str,
    start_time: Optional[str],
    end_time: Optional[str],
    time_range: Optional[str],
    variables: Optional[str],
    data_source: Optional[str],
    output_dir: Optional[str],
    show_symbols: Optional[bool],
) -> None:
    """Plot weather data for multiple airports."""
    try:
        # Parse ICAO codes
        codes = [code.strip().upper() for code in icao_codes.split(",")]

        # Validate ICAO codes
        invalid_codes = [code for code in codes if not validate_icao_code(code)]
        if invalid_codes:
            click.echo(
                f"Error: Invalid ICAO codes: {', '.join(invalid_codes)}", err=True
            )
            return

        # Parse time range
        if time_range:
            # Use the time-range argument
            start_dt, end_dt = parse_time_range(time_range)
            if start_dt is None or end_dt is None:
                click.echo(f"Error: Invalid time range '{time_range}'", err=True)
                click.echo(
                    "Examples: 'next 6 hours', 'last 24 hours', 'next 3 days'", err=True
                )
                return
        else:
            # Use individual start/end time arguments or defaults
            if start_time:
                start_dt = datetime.fromisoformat(start_time.replace("T", " "))
            else:
                start_dt = datetime.now() - timedelta(days=1)

            if end_time:
                end_dt = datetime.fromisoformat(end_time.replace("T", " "))
            else:
                end_dt = datetime.now() + timedelta(days=2)

        # Parse variables
        var_list = None
        if variables:
            var_list = [v.strip() for v in variables.split(",")]

        # Create plotter
        plotter = WeatherPlotter(ctx.obj)

        click.echo(f"Plotting weather data for {len(codes)} airports...")

        # Create plots
        figures = plotter.plot_multiple_airports(
            icao_codes=codes,
            start_time=start_dt,
            end_time=end_dt,
            variables=var_list,
            data_source=data_source or "auto",
            output_dir=output_dir,
        )

        click.echo(f"Created {len(figures)} plots successfully!")

    except (ValueError, RuntimeError, OSError, IOError) as e:
        click.echo(f"Error: {e}", err=True)
        logging.error("Plot multiple command failed: %s", e)


@main.command()
@click.argument("query")
@click.option("--limit", default=10, help="Maximum number of results")
@click.pass_context
def search(ctx: Any, query: str, limit: int) -> None:
    """Search for airports by name or code."""
    try:
        plotter = WeatherPlotter(ctx.obj)
        results = plotter.search_airports(query)

        if not results:
            click.echo("No airports found.")
            return

        click.echo(f"Found {len(results)} airports:")
        click.echo()

        for i, airport in enumerate(results[:limit], 1):
            name = airport.get("name", "Unknown")
            icao = airport.get("icao", "N/A")
            iata = airport.get("iata", "N/A")
            country = airport.get("country", "N/A")

            click.echo(f"{i:2d}. {name}")
            click.echo(f"    ICAO: {icao}  IATA: {iata}  Country: {country}")

            if "distance_km" in airport:
                click.echo(f"    Distance: {airport['distance_km']:.1f} km")

            click.echo()

        if len(results) > limit:
            click.echo(f"... and {len(results) - limit} more results")

    except (ValueError, RuntimeError, OSError, IOError) as e:
        click.echo(f"Error: {e}", err=True)
        logging.error("Search command failed: %s", e)


@main.command()
@click.option("--country", help="Filter by country code")
@click.option("--type", "airport_type", help="Filter by airport type")
@click.option("--limit", default=20, help="Maximum number of results")
@click.pass_context
def list_airports(
    ctx: Any, country: Optional[str], airport_type: Optional[str], limit: int
) -> None:
    """List available airports."""
    try:
        plotter = WeatherPlotter(ctx.obj)
        airports = plotter.list_available_airports()

        # Apply filters
        if country:
            airports = [
                a for a in airports if a.get("country", "").upper() == country.upper()
            ]

        if airport_type:
            airports = [
                a for a in airports if a.get("type", "").lower() == airport_type.lower()
            ]

        if not airports:
            click.echo("No airports found.")
            return

        click.echo(f"Found {len(airports)} airports:")
        click.echo()

        for i, airport in enumerate(airports[:limit], 1):
            name = airport.get("name", "Unknown")
            icao = airport.get("icao", "N/A")
            country_code = airport.get("country", "N/A")
            airport_type_str = airport.get("type", "N/A")

            click.echo(f"{i:2d}. {name} ({icao}) - {country_code} - {airport_type_str}")

        if len(airports) > limit:
            click.echo(f"... and {len(airports) - limit} more airports")

    except (ValueError, RuntimeError, OSError, IOError) as e:
        click.echo(f"Error: {e}", err=True)
        logging.error("List airports command failed: %s", e)


def _test_api_connection(plotter: WeatherPlotter) -> None:
    """Test API connection."""
    click.echo("Testing API connection...")
    try:
        if plotter.http_client.test_connection():
            click.echo("✓ API connection successful")
        else:
            click.echo("✗ API connection failed")
    except (requests.RequestException, ValueError, TypeError) as e:
        click.echo(f"✗ API connection error: {e}")


def _test_file_connection(plotter: WeatherPlotter) -> None:
    """Test file server connection."""
    click.echo("Testing file server connection...")
    try:
        if plotter.file_client.test_connection():
            click.echo("✓ File server connection successful")
        else:
            click.echo("✗ File server connection failed")
    except (OSError, IOError, ValueError, TypeError, RuntimeError) as e:
        click.echo(f"✗ File server connection error: {e}")


@main.command()
@click.option("--api/--no-api", default=True, help="Test API connection")
@click.option("--files/--no-files", default=True, help="Test file server connection")
@click.pass_context
def test_connection(ctx: Any, api: bool, files: bool) -> None:
    """Test connections to data sources."""
    try:
        plotter = WeatherPlotter(ctx.obj)

        if api:
            _test_api_connection(plotter)

        if files:
            _test_file_connection(plotter)

    except (ValueError, RuntimeError, OSError, IOError) as e:
        click.echo(f"Error: {e}", err=True)
        logging.error("Test connection command failed: %s", e)


@main.command()
@click.option("--output", "-o", default="config.yaml", help="Output configuration file")
@click.pass_context
def export_config(ctx: Any, output: str) -> None:
    """Export current configuration to file."""
    try:
        ctx.obj.save_to_file(output)
        click.echo(f"Configuration exported to {output}")

    except (OSError, IOError, ValueError, TypeError) as e:
        click.echo(f"Error: {e}", err=True)
        logging.error("Export config command failed: %s", e)


if __name__ == "__main__":
    main()
