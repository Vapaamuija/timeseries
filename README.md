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
python dev.py plot ENGM --output oslo_weather.png
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
./setup_svg_rendering.sh
```

### Your First Weather Plot

```bash
# Create a weather plot for Oslo Airport
python dev.py plot ENGM --output my_first_weather_plot.png
```

**Success!** You should now have a weather plot file called `my_first_weather_plot.png` 🎉

## Basic Examples

```bash
# Try different airports
python dev.py plot ENGM --output oslo.png        # Oslo, Norway
python dev.py plot EKCH --output copenhagen.png  # Copenhagen, Denmark
python dev.py plot EGLL --output london.png      # London Heathrow, UK

# Search for airports
python dev.py search "paris"
python dev.py search "tokyo"

# Different plot styles
python dev.py plot ENGM --style modern --output modern.png
python dev.py plot ENGM --style tseries --output professional.png
```

## Project Structure

```
weather-tool/
├── dev.py                    # Main command-line tool
├── requirements.txt          # Required Python packages
├── config/settings.yaml      # Configuration file
├── src/weather_tool/         # Main Python package
├── docs/                     # Complete documentation
└── output/                   # Your generated plots go here
```

## Documentation

Complete documentation is available in the `docs/` folder:

-   **[docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)** - Detailed setup guide for beginners
-   **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Complete development environment setup with pyenv/venv
-   **[docs/EDITOR_SETUP.md](docs/EDITOR_SETUP.md)** - Editor configuration guide
-   **[docs/FORMATTING.md](docs/FORMATTING.md)** - Code formatting and quality tools

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
python dev.py --help           # Should show help text
python dev.py test-connection  # Should show "Connection OK"
python dev.py plot ENGM --output test.png  # Should create a plot
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
