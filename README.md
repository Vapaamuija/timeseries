# Weather Tool - Create Beautiful Weather Plots

A simple Python tool that creates professional weather charts for airports around the world. Perfect for learning Python, meteorology, or just getting cool weather visualizations!

## What Does This Tool Do?

This tool downloads real weather data and creates beautiful charts showing:

-   🌡️ Temperature over time
-   🌧️ Precipitation (rain/snow)
-   💨 Wind speed and direction
-   ☁️ Cloud coverage
-   📊 Atmospheric pressure
-   🎨 Official Met.no weather symbols with transparent backgrounds

**Example**: Create a weather chart for Oslo Airport with just one command!

```bash
./bin/weather-tool plot ENGM --output oslo_weather.png
```

## Quick Start

### What You Need

1. **Python 3.8 or newer** - [Download here](https://www.python.org/downloads/)
2. **Git** - [Download here](https://git-scm.com/downloads/)
3. **Internet connection** - To download weather data

### Installation

```bash
# Download the project
git clone <repository-url>
cd weather-tool

# Install the required packages
pip install -r requirements.txt

# For high-quality weather symbols (optional but recommended)
./bin/setup_svg_rendering.sh
```

### Your First Weather Plot

```bash
# Create a weather plot for Oslo Airport
./bin/weather-tool plot ENGM --output my_first_weather_plot.png
```

**Success!** You should now have a weather plot file called `my_first_weather_plot.png` 🎉

## Basic Examples

```bash
# Try different airports
./bin/weather-tool plot ENGM --output oslo.png        # Oslo, Norway
./bin/weather-tool plot EKCH --output copenhagen.png  # Copenhagen, Denmark
./bin/weather-tool plot EGLL --output london.png      # London Heathrow, UK

# Plot weather for any location using GPS coordinates
./bin/weather-tool plot-coords 59.9139 10.7522 --location-name "Oslo City Center" --output oslo_city.png
./bin/weather-tool plot-coords 40.7128 -74.0060 --location-name "New York City" --output nyc.png
./bin/weather-tool plot-coords 35.6762 139.6503 --location-name "Tokyo" --output tokyo.png

# Search for airports
./bin/weather-tool search "paris"
./bin/weather-tool search "tokyo"

# Different plot styles
./bin/weather-tool plot ENGM --style modern --output modern.png
./bin/weather-tool plot ENGM --style tseries --output professional.png
```

## GPS Coordinate Support

You can plot weather data for any location worldwide using GPS coordinates:

```bash
# Basic coordinate plotting
./bin/weather-tool plot-coords 59.9139 10.7522 --output oslo.png

# With custom location name
./bin/weather-tool plot-coords 59.9139 10.7522 --location-name "Oslo City Center"

# With time range
./bin/weather-tool plot-coords 59.9139 10.7522 --time-range "next 24 hours"

# With specific variables
./bin/weather-tool plot-coords 59.9139 10.7522 --variables "temperature,precipitation,wind"
```

### Coordinate Format
- **Latitude**: -90 to 90 (negative for Southern Hemisphere)
- **Longitude**: -180 to 180 (negative for Western Hemisphere)
- **Examples**: 
  - Oslo: `59.9139 10.7522`
  - New York: `40.7128 -74.0060`
  - Sydney: `-33.8688 151.2093` (Note: Use quotes for negative coordinates)

**Note**: For negative coordinates, you may need to use quotes or the `--` separator to prevent them from being interpreted as command options.

## Project Structure

```
weather-tool/
├── bin/                      # Command-line tools
│   ├── weather-tool          # Main weather tool CLI
│   ├── dev                   # Development utilities (format, lint, test)
│   ├── setup-dev.sh          # Development environment setup
│   └── setup_svg_rendering.sh # SVG rendering setup
├── requirements.txt          # Required Python packages
├── config/settings.yaml      # Configuration file
├── src/weather_tool/         # Main Python package
├── docs/                     # Complete documentation
└── output/                   # Your generated plots go here
```

**Important**: Use `./bin/weather-tool` for weather plotting, and `./bin/dev` for development tasks like formatting and testing.

### Quick Command Reference

```bash
# Weather plotting commands
./bin/weather-tool plot ENGM --output plot.png    # Plot by airport code
./bin/weather-tool plot-coords 59.9139 10.7522 --output plot.png  # Plot by GPS coordinates
./bin/weather-tool search "oslo"                  # Search airports
./bin/weather-tool --help                         # Get help

# Development commands  
./bin/dev format                                  # Format code
./bin/dev lint                                    # Check code quality
./bin/dev test                                    # Run tests
./bin/dev --help                                  # Development help
```

## Documentation

Complete documentation is available in the `docs/` folder:

-   **[docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)** - Detailed setup guide for beginners
-   **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Complete development environment setup with pyenv/venv
-   **[docs/EDITOR_SETUP.md](docs/EDITOR_SETUP.md)** - Editor configuration guide
-   **[docs/FORMATTING.md](docs/FORMATTING.md)** - Code formatting and quality tools
-   **[docs/BIN_SCRIPTS.md](docs/BIN_SCRIPTS.md)** - Development scripts usage guide

### Additional Documentation (Coming Soon)

-   **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Fix common problems and errors
-   **[docs/EXAMPLES.md](docs/EXAMPLES.md)** - Advanced examples and use cases
-   **[docs/API_REFERENCE.md](docs/API_REFERENCE.md)** - Complete Python API documentation
-   **[docs/CONFIGURATION.md](docs/CONFIGURATION.md)** - Configuration options and customization
-   **[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)** - How to contribute to the project

## Need Help?

1. **First time setup?** → Read [Getting Started Guide](docs/GETTING_STARTED.md)
2. **Setting up development environment?** → See [Development Guide](docs/DEVELOPMENT.md) with pyenv/venv setup
3. **Not working?** → Check [Troubleshooting Guide](docs/TROUBLESHOOTING.md) (coming soon)
4. **Want more examples?** → See [Examples Guide](docs/EXAMPLES.md) (coming soon)

### Test Your Setup

```bash
# Run these to check if everything works
./bin/weather-tool --help           # Should show help text
./bin/weather-tool test-connection  # Should show "Connection OK"
./bin/weather-tool plot ENGM --output test.png  # Should create a plot
```

## What Makes This Tool Special?

-   ✅ **Beginner-Friendly**: Simple commands that just work
-   ✅ **Professional Quality**: Uses real meteorological data from Met.no
-   ✅ **Official Weather Symbols**: High-quality SVG symbols with transparent backgrounds
-   ✅ **Well-Documented**: Complete guides for all skill levels

## Requirements

-   Python 3.8 or newer
-   Internet connection for weather data
-   About 50MB of disk space

## License

MIT License - Feel free to use this for any purpose!

## Credits

-   **Weather Data**: Norwegian Meteorological Institute (Met.no)
-   **Original Concept**: Based on Norwegian T-series meteorological plotting

---

**Ready to start?** See the [Getting Started Guide](docs/GETTING_STARTED.md) for detailed instructions.

**Happy weather plotting!** ☀️🌧️❄️
