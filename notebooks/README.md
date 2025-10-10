# Weather Plotter Testing Environment

This directory contains a comprehensive Jupyter notebook for interactive testing and development of weather plotters. Perfect for developers at all levels to experiment with the codebase and see immediate visual results.

## 🎯 Purpose

- **Learn the complete plotting system** without needing API keys or real data
- **Experiment with all configurations** and see results immediately
- **Test modifications** to plotters in a safe environment
- **Understand the codebase** through interactive examples
- **Analyze weather patterns** with statistical tools
- **Handle errors gracefully** with built-in diagnostics

## 📁 Contents

### Main Notebook

- **`Weather_Plotter_Complete.ipynb`** - **🌟 THE COMPLETE SOLUTION** - Everything you need in one notebook:
  - 🎨 All plot types (Modern, T-Series, Norwegian Meteogram, Multi-Airport Comparison)
  - 🎮 Interactive configuration with real-time updates
  - 📊 Statistical analysis and correlation tools
  - 🛡️ Error handling and diagnostic tools
  - 📚 Comprehensive documentation and examples

### Legacy Notebooks (Optional)

- **`Weather_Plotter_Testing.ipynb`** - Original interactive testing environment
- **`Configuration_Playground.ipynb`** - Configuration experimentation
- **`Norwegian_Meteogram_Demo.ipynb`** - Norwegian meteogram examples
- **`Comparison_Analysis.ipynb`** - Multi-airport comparison analysis
- **`Quick_Test.ipynb`** - Simple setup verification

> **💡 Recommendation:** Start with `Weather_Plotter_Complete.ipynb` - it contains everything from all other notebooks in a well-organized, comprehensive format.

### Test Data

- **`test_data/`** - Pre-generated realistic weather data
  - `sample_24h_hourly.pkl` - 24-hour hourly data
  - `sample_7d_3hourly.pkl` - 7-day 3-hourly data  
  - `sample_30d_6hourly.pkl` - 30-day 6-hourly data
  - `sample_multi_airport_*.pkl` - Multi-airport comparison data
  - `test_airports.json` - Airport information
  - `sample_data_generator.py` - Data generation script

## 🚀 Quick Start (5 minutes)

### 1. One-Command Setup

```bash
cd notebooks
python setup_jupyter_env.py
```

This will:
- ✅ Install all required dependencies
- ✅ Generate realistic test data
- ✅ Verify everything is working

### 2. Start Jupyter

```bash
jupyter lab
```

### 3. Open the Main Notebook

**🌟 Recommended approach:**
1. **Open `Weather_Plotter_Complete.ipynb`** - The complete solution with everything you need
2. **Run all cells in order** from top to bottom
3. **Experiment with the interactive sections** to learn the system
4. **Use the diagnostic tools** if you encounter any issues

**Alternative (Legacy notebooks):**
- Start with `Quick_Test.ipynb` to verify setup
- Then explore individual specialized notebooks as needed

## 🎨 Features

### Interactive Widgets

- **Dataset Selection** - Choose from different time periods and data frequencies
- **Plot Style** - Switch between Modern and T-Series styles
- **Configuration** - Adjust colors, sizes, fonts, and variables
- **Real-time Updates** - See changes immediately

### Static Test Data

- **No API required** - All data is pre-generated
- **Realistic patterns** - Includes seasonal, diurnal, and weather variations
- **Multiple airports** - Test with different locations
- **Various time scales** - From hours to months

### Plot Types

- **Modern Style** - Clean, flexible multi-variable plots
- **T-Series Style** - Traditional Norwegian meteorological format  
- **Norwegian Meteogram** - Norwegian meteogram with cloud layers and wind barbs
- **Comparison Plots** - Multi-airport analysis with statistical insights
- **Interactive Widgets** - Real-time parameter adjustment and visualization

## 🔧 For Developers

### Understanding the Code Structure

```
src/weather_tool/plotting/
├── plotters.py          # Main plotter classes
├── interfaces.py        # Configuration and base classes
└── symbols.py          # Weather symbol rendering
```

### Key Classes

- **`ModernWeatherPlotter`** - Flexible multi-variable plotting
- **`TSeriesWeatherPlotter`** - Norwegian T-series meteograms
- **`MeteogramPlotter`** - Norwegian meteogram with cloud layers
- **`ComparisonWeatherPlotter`** - Multi-location comparisons
- **`PlotConfig`** - Configuration management

### Customization Points

1. **Colors** - Modify color palettes and specific variable colors
2. **Layout** - Adjust subplot arrangements and sizing
3. **Variables** - Add new weather variables or modify existing ones
4. **Symbols** - Customize weather symbol rendering
5. **Formatting** - Change axis labels, grids, and styling

## 📊 Test Data Details

### Data Generation

The test data is generated using realistic patterns:

- **Temperature**: Seasonal + diurnal cycles + weather variability
- **Pressure**: Synoptic weather systems + short-term variations
- **Humidity**: Correlated with temperature + random variations
- **Wind**: Weibull distribution with persistence
- **Precipitation**: Intermittent with exponential distribution
- **Clouds**: Beta distribution with persistence for each layer

### Airports Included

- **ENGM** - Oslo Airport, Gardermoen (Norway)
- **EFHK** - Helsinki-Vantaa Airport (Finland)
- **ESSA** - Stockholm Arlanda Airport (Sweden)
- **EKCH** - Copenhagen Airport (Denmark)

## 💡 Pro Tips

### For Beginners
1. **Start with the examples** - run the first few cells to see basic plots
2. **Use the interactive widgets** - they provide immediate feedback
3. **Try different datasets** - see how time scales affect the plots
4. **Experiment with colors** - find combinations that work well

### For Developers
1. **Look at the source code** - understand how plotters work (`src/weather_tool/plotting/`)
2. **Modify configurations** - see how parameters affect output
3. **Create custom data** - use the data generator for new scenarios
4. **Add new features** - extend the plotting system

## 🔧 Customization Examples

### Change Colors
```python
config = PlotConfig(
    color_palette='viridis',
    temperature_color='#ff6b6b'
)
```

### Adjust Layout
```python
config = PlotConfig(
    figure_size=(16, 10),
    font_size=12
)
```

### Select Variables
```python
plotter.create_plot(
    data, airport,
    variables=['temperature', 'pressure', 'wind_speed']
)
```

## 🎓 Learning Path for All Developers

### 🌟 Unified Approach (Recommended)

**Use `Weather_Plotter_Complete.ipynb` for everything:**

1. **📚 Start with the Introduction** - Understand what's available
2. **🔧 Run Setup and Data Loading** - Get everything working
3. **🎨 Explore Quick Examples** - See all plot types in action
4. **🎮 Use Interactive Configuration** - Experiment with real-time changes
5. **📊 Try Statistical Analysis** - Understand data patterns and correlations
6. **🛡️ Learn Error Handling** - Use diagnostic tools for troubleshooting
7. **📖 Read the Complete Guide** - Master advanced techniques

### 🔄 Alternative (Legacy Notebooks)

If you prefer separate notebooks:

1. **Start Simple** - `Quick_Test.ipynb` to verify setup
2. **Understand Configuration** - `Configuration_Playground.ipynb` for parameters
3. **Explore Specialized Plots** - Individual notebooks for specific plot types
4. **Advanced Analysis** - `Comparison_Analysis.ipynb` for multi-airport work

### 🚀 Next Steps

- **Explore the Code** - Look at `src/weather_tool/plotting/plotters.py`
- **Create Custom Configurations** - Design your own themes and layouts
- **Extend the System** - Add new plot types or variables
- **Integrate Real Data** - Connect to live weather APIs

## 🛠️ Troubleshooting

### Common Issues

**Import Errors**
```python
# Make sure the project root is in the Python path
import sys
from pathlib import Path
sys.path.insert(0, str(Path().absolute().parent / 'src'))
```

**Widget Display Issues**
```bash
# Enable Jupyter widgets
jupyter nbextension enable --py widgetsnbextension
```

**Matplotlib Backend Issues**
```python
# Use the widget backend for interactive plots
%matplotlib widget
```

### Getting Help

1. Check the main project documentation
2. Look at the source code comments
3. Experiment with the interactive examples
4. Try different configurations to understand behavior

## 🎯 Best Practices

### For Testing
- Always start with the interactive widgets
- Save interesting configurations for later reference
- Test with different datasets to see various patterns
- Compare Modern vs T-Series styles for the same data

### For Development
- Make small changes and test immediately
- Use the configuration system rather than hardcoding values
- Follow the existing code patterns and style
- Document any new features or modifications

## 🚀 Next Steps

Once you're comfortable with the testing environment:

1. **Modify existing plotters** - Add new features or styling options
2. **Create new plot types** - Extend the system with your own ideas
3. **Improve the data generator** - Add more realistic patterns or new variables
4. **Contribute back** - Share your improvements with the project

Happy plotting! 🎨📊
