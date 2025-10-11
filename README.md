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

## Before You Start

### What You Need

1. **Python 3.8 or newer** - [Download here](https://www.python.org/downloads/)
2. **Git** - [Download here](https://git-scm.com/downloads/)
3. **Internet connection** - To download weather data
4. **5 minutes** - That's all it takes to get started!

### Check If You Have Python

Open a terminal/command prompt and type:

```bash
python --version
```

You should see something like `Python 3.9.0` or newer. If not, install Python first.

## Quick Start (5 Minutes)

### Step 1: Download the Code

```bash
# Download the project
git clone <repository-url>
cd weather-tool
```

### Step 2: Install Requirements

```bash
# Install the required packages
pip install -r requirements.txt
```

**For High-Quality Weather Symbols** (Optional but recommended):

🚀 **Easy Setup (All Platforms):**

```bash
# Run the automated setup script
./setup_svg_rendering.sh
```

🔧 **Manual Installation:**

```bash
# macOS (with Homebrew):
brew install cairo
pip install cairosvg pillow

# Ubuntu/Debian:
sudo apt-get install libcairo2-dev pkg-config python3-dev
pip install cairosvg pillow

# CentOS/RHEL:
sudo yum install cairo-devel pkgconfig python3-devel
pip install cairosvg pillow

# Fedora:
sudo dnf install cairo-devel pkgconfig python3-devel
pip install cairosvg pillow

# Arch Linux:
sudo pacman -S cairo pkgconf python
pip install cairosvg pillow
```

**Having trouble?** See our [Troubleshooting Guide](docs/TROUBLESHOOTING.md)

### Step 3: Create Your First Weather Plot

```bash
# Create a weather plot for Oslo Airport
python dev.py plot ENGM --output my_first_weather_plot.png
```

**Success!** You should now have a weather plot file called `my_first_weather_plot.png` 🎉

## Your First Weather Plots

### Try These Examples (Copy & Paste)

```bash
# Oslo, Norway
python dev.py plot ENGM --output oslo.png

# Copenhagen, Denmark
python dev.py plot EKCH --output copenhagen.png

# London Heathrow, UK
python dev.py plot EGLL --output london.png

# New York JFK, USA
python dev.py plot KJFK --output newyork.png
```

### Different Plot Styles

#### Modern Style (Clean and Simple)

```bash
python dev.py plot ENGM --style modern --output oslo_modern.png
```

#### Traditional Meteogram (Professional Weather Chart)

```bash
python dev.py plot ENGM --style tseries --output oslo_professional.png
```

## Finding Airport Codes

Don't know an airport code? Use the search feature:

```bash
# Search for airports
python dev.py search "paris"
python dev.py search "tokyo"
python dev.py search "sydney"
```

This shows you the airport codes (like LFPG, RJTT, YSSY) to use in your plots.

## Common Use Cases

### Daily Weather Check

```bash
# Today's weather for your local airport
python dev.py plot KJFK --output today_weather.png
```

### Travel Planning

```bash
# Check weather at your destination
python dev.py search "rome"  # Find airport code
python dev.py plot LIRF --output rome_weather.png
```

### Compare Multiple Cities

```bash
# Compare temperature across cities
python dev.py plot-multiple ENGM,EKCH,ESSA --style comparison --variable temperature --output nordic_comparison.png
```

### Weather for Next Week

```bash
# 7-day forecast
python dev.py plot ENGM --end-time "$(date -d '+7 days' '+%Y-%m-%d 00:00')" --output week_forecast.png
```

## Understanding Your Weather Plots

### What the Charts Show

**Modern Style Charts**:

-   **Top panel**: Temperature (red/blue line)
-   **Second panel**: Atmospheric pressure (black line)
-   **Third panel**: Wind speed (green line) and direction (arrows)
-   **Bottom panel**: Precipitation (blue bars)

**Traditional Meteogram**:

-   Professional meteorological format
-   Used by weather services and pilots
-   Shows detailed cloud layers and wind barbs

### Reading the Data

-   **X-axis**: Time (usually next 48 hours)
-   **Y-axis**: Weather values (temperature in °C, pressure in hPa, etc.)
-   **Colors**: Different variables use different colors
-   **Symbols**: Official Met.no weather symbols show current conditions with transparent backgrounds
    -   Clear sky: ○ (circle)
    -   Cloudy: □ (square)
    -   Rain: ▽ (triangle down)
    -   Snow: ★ (star)
    -   Fog: ⬡ (hexagon)

## Command Reference

### Basic Commands

```bash
# Create a weather plot
python dev.py plot <AIRPORT_CODE> --output <filename.png>

# Search for airports
python dev.py search "<city or airport name>"

# Test if everything is working
python dev.py test-connection

# Get help
python dev.py --help
```

### Useful Options

```bash
# Different styles
--style modern          # Clean, modern charts
--style tseries         # Professional meteogram
--style comparison      # Compare multiple airports

# Time ranges
--end-time "2024-01-03 00:00"     # Show until this date
--start-time "2024-01-01 12:00"   # Start from this date

# Specific weather data
--variables temperature,pressure   # Only show these variables
--data-source http                # Use API data
--data-source file                # Use weather model files
```

## Examples for Different Needs

### For Students Learning Python

```bash
# Simple examples to understand the tool
python dev.py plot ENGM --output example1.png
python dev.py search "oslo"
python dev.py test-connection
```

### For Weather Enthusiasts

```bash
# Professional weather charts
python dev.py plot ENGM --style tseries --output professional_chart.png

# Compare multiple locations
python dev.py plot-multiple ENGM,ENBR,ENTC --style comparison --variable temperature
```

### For Travelers

```bash
# Check weather at destination
python dev.py search "destination city"
python dev.py plot <AIRPORT_CODE> --output trip_weather.png
```

### For Developers

```bash
# Use the Python API
python -c "
from weather_tool import WeatherPlotter
plotter = WeatherPlotter()
fig = plotter.plot_airport('ENGM', output_path='oslo.png')
print('Plot created!')
"
```

## Project Structure (For Curious Developers)

```
weather-tool/
├── dev.py                    # Main command-line tool (start here!)
├── requirements.txt          # Required Python packages
├── config/settings.yaml      # Configuration file
├── src/weather_tool/         # Main Python package
├── docs/                     # Documentation
│   ├── GETTING_STARTED.md    # Detailed setup guide
│   ├── EXAMPLES.md           # More examples
│   └── TROUBLESHOOTING.md    # Fix common problems
├── examples/                 # Python code examples
└── output/                   # Your generated plots go here
```

## Documentation

### 📚 Complete Documentation Structure

This project maintains comprehensive documentation that is **always kept up to date** with the latest features and changes. All documentation lives in the `docs/` directory and is organized for different user needs.

#### Essential Documentation

-   **[README.md](README.md)** - This file! Essential commands, quick start, and overview
-   **[docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)** - Detailed setup guide for beginners

#### Additional Documentation (Coming Soon)

-   **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Fix common problems and errors
-   **[docs/EXAMPLES.md](docs/EXAMPLES.md)** - Advanced examples and use cases
-   **[docs/API_REFERENCE.md](docs/API_REFERENCE.md)** - Complete Python API documentation
-   **[docs/CONFIGURATION.md](docs/CONFIGURATION.md)** - Configuration options and customization
-   **[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)** - How to contribute to the project

### 🔄 Documentation Maintenance Policy

**Critical**: All documentation in `docs/` must be kept current with code changes. When you:

-   Add new features → Update relevant documentation
-   Change command syntax → Update README.md and examples
-   Modify configuration → Update configuration docs
-   Fix bugs → Update troubleshooting guide
-   Change API → Update API reference

### 📖 Documentation Standards

-   **Beginner-friendly**: Clear, step-by-step instructions
-   **Copy-paste ready**: All commands should work as written
-   **Up-to-date**: Always reflects current functionality
-   **Comprehensive**: Covers all features and edge cases
-   **Well-organized**: Logical structure for easy navigation

## Need Help?

### Quick Fixes

1. **Not working?** → Check [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
2. **Want more examples?** → See [Examples Guide](docs/EXAMPLES.md)
3. **First time setup?** → Read [Getting Started Guide](docs/GETTING_STARTED.md)

### Test Your Setup

```bash
# Run these to check if everything works
python dev.py --help           # Should show help text
python dev.py test-connection  # Should show "Connection OK"
python dev.py plot ENGM --output test.png  # Should create a plot

# Test weather symbol capabilities
python -c "
from src.weather_tool.plotting.symbols import UnifiedWeatherSymbols
from src.weather_tool.plotting.interfaces import PlotConfig, SymbolType
config = PlotConfig(symbol_type=SymbolType.SVG)
renderer = UnifiedWeatherSymbols(config)
print('High-quality SVG support:', renderer.has_high_quality_svg_support())
"
```

### Common Issues

-   **"python: command not found"** → Try `py` instead of `python` (Windows)
-   **"No module named 'requests'"** → Run `pip install -r requirements.txt`
-   **"Permission denied"** → Add `--user` to pip commands
-   **Empty plots** → Check internet connection, try different airport code
-   **Weather symbols not showing** → Install Cairo library and cairosvg for high-quality SVG symbols
-   **"cairo library not found"** → Install system Cairo library first (see installation instructions above)

## What Makes This Tool Special?

### ✅ Beginner-Friendly

-   Simple commands that just work
-   Clear error messages
-   Lots of examples
-   No complex setup required

### ✅ Professional Quality

-   Uses real meteorological data from Met.no
-   Creates publication-quality charts
-   Official Met.no weather symbols with transparent backgrounds
-   Supports international weather standards
-   Used by weather professionals

### ✅ Flexible and Powerful

-   Multiple data sources (APIs and weather models)
-   Different chart styles for different needs
-   Batch processing for multiple airports
-   Python API for custom applications

### ✅ Well-Documented

-   Step-by-step guides for beginners
-   Troubleshooting for common issues
-   Examples for every use case
-   Clean, readable code

## Weather Symbols

### Official Met.no Weather Symbols

This tool uses official weather symbols from the Norwegian Meteorological Institute (Met.no), ensuring accuracy and consistency with professional weather services.

### Symbol Rendering

-   **High-Quality SVG**: When Cairo library is installed, renders true SVG symbols with transparent backgrounds
-   **Fallback Markers**: Uses weather-appropriate matplotlib markers when SVG libraries aren't available
-   **Transparent Backgrounds**: All symbols blend seamlessly with any plot background

### Symbol Types

The tool automatically maps Met.no weather codes to appropriate symbols:

-   **Clear/Fair Weather**: ○ (circle) - for sunny conditions
-   **Cloudy Conditions**: □ (square) - for overcast skies
-   **Rain**: ▽ (triangle down) - for precipitation
-   **Snow**: ★ (star) - for snow conditions
-   **Fog**: ⬡ (hexagon) - for low visibility
-   **Thunder**: ◆ (diamond) - for thunderstorms
-   **Sleet**: + (plus) - for mixed precipitation

### Installation for Best Quality

For the highest quality weather symbols with true transparency:

```bash
# macOS
brew install cairo
pip install cairosvg pillow

# Ubuntu/Debian
sudo apt-get install libcairo2-dev
pip install cairosvg pillow

# Windows
# Download Cairo from https://cairographics.org/download/
pip install cairosvg pillow
```

Without these libraries, the tool automatically falls back to matplotlib markers that still provide clear, transparent weather symbols.

## Advanced Features (When You're Ready)

### Python API

```python
from weather_tool import WeatherPlotter

# Create a plotter
plotter = WeatherPlotter()

# Create a weather plot
fig = plotter.plot_airport(
    icao_code="ENGM",           # Oslo Airport
    plot_style="modern",        # Clean style
    output_path="oslo.png"      # Save location
)
```

### Custom Configuration

Edit `config/settings.yaml` to customize:

-   Default plot styles
-   Color schemes
-   Data sources
-   Time ranges

### Batch Processing

```bash
# Process multiple airports at once
python dev.py plot-multiple ENGM,EKCH,ESSA --output-dir scandinavian_weather/
```

## Contributing

Want to help make this tool better?

1. **Report bugs**: Create an issue if something doesn't work
2. **Suggest features**: Tell us what you'd like to see
3. **Improve documentation**: Help make guides even clearer
4. **Add examples**: Share your cool weather plots

## Requirements

### Core Requirements

-   Python 3.8 or newer
-   Internet connection for weather data
-   About 50MB of disk space

### Python Packages (Installed Automatically)

-   `numpy` - For numerical calculations
-   `pandas` - For data handling
-   `matplotlib` - For creating plots
-   `requests` - For downloading weather data
-   `xarray` - For weather file processing

### Optional Packages (For Enhanced Weather Symbols)

-   `cairosvg` - For high-quality SVG weather symbol rendering
-   `pillow` - For image processing and transparency support
-   System Cairo library - Required for SVG rendering

## License

MIT License - Feel free to use this for any purpose!

## Credits

-   **Weather Data**: Norwegian Meteorological Institute (Met.no)
-   **Original Concept**: Based on Norwegian T-series meteorological plotting
-   **Inspiration**: Making weather data accessible to everyone

---

## Ready to Start?

1. **Install Python** (if you haven't already)
2. **Clone this repository**
3. **Run `pip install -r requirements.txt`**
4. **Try `python dev.py plot ENGM --output test.png`**

**That's it!** You're now creating professional weather plots! 🌤️

For more detailed instructions, see our [Getting Started Guide](docs/GETTING_STARTED.md).

**Happy weather plotting!** ☀️🌧️❄️
