# Getting Started Guide for Junior Developers

Welcome! This guide will help you get the weather tool up and running, even if you're new to Python development.

## What You'll Need Before Starting

### Required Software

1. **Python 3.8 or newer** - [Download from python.org](https://www.python.org/downloads/)
2. **Git** - [Download from git-scm.com](https://git-scm.com/downloads/)
3. **A code editor** - We recommend [VS Code](https://code.visualstudio.com/)

### Check Your Setup

Open a terminal/command prompt and run these commands to verify:

```bash
python --version    # Should show Python 3.8+
git --version      # Should show git version
pip --version      # Should show pip version
```

If any command fails, install the missing software first.

## Step-by-Step Installation

### Step 1: Get the Code

```bash
# Navigate to where you want the project
cd ~/Desktop  # or wherever you keep projects

# Download the code
git clone <repository-url>
cd weather-tool
```

### Step 2: Install Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt
```

**If you get permission errors**, try:

```bash
pip install --user -r requirements.txt
```

### Step 3: Test the Installation

```bash
# Test that everything works
./bin/weather-tool --help
```

You should see a help message with available commands. If you see an error, check the [Troubleshooting](#troubleshooting) section below.

## Your First Weather Plot

Let's create your first weather plot! Copy and paste this command:

```bash
./bin/weather-tool plot ENGM --output my_first_plot.png
```


This will:

-   Get weather data for Oslo Airport (ENGM)
-   Create a weather plot
-   Save it as `my_first_plot.png` in the current folder

**Success!** You should now have a weather plot file you can open and view.

## Understanding the Command

Let's break down what you just ran:

```bash
./bin/weather-tool plot ENGM --output my_first_plot.png
```

-   `./bin/weather-tool` - Runs the weather tool
-   `plot` - Tells it to create a weather plot
-   `ENGM` - The airport code for Oslo Airport
-   `--output my_first_plot.png` - Where to save the plot

## Try More Examples

### Different Airports

```bash
# Copenhagen Airport
./bin/weather-tool plot EKCH --output copenhagen.png

# Stockholm Airport
./bin/weather-tool plot ESSA --output stockholm.png

# Bergen Airport
./bin/weather-tool plot ENBR --output bergen.png
```

### Different Plot Styles

```bash
# Modern style (default)
./bin/weather-tool plot ENGM --style modern --output modern_plot.png

# Traditional meteogram
./bin/weather-tool plot ENGM --style tseries --output traditional_plot.png
```

### Custom Time Ranges

```bash
# Next 3 days
./bin/weather-tool plot ENGM --end-time "2024-01-03 00:00" --output 3day_forecast.png

# Specific date range
./bin/weather-tool plot ENGM --start-time "2024-01-01 12:00" --end-time "2024-01-02 12:00" --output custom_range.png
```

## Finding Airport Codes

Don't know an airport code? Use the search feature:

```bash
# Search for airports
./bin/weather-tool search "oslo"
./bin/weather-tool search "london"
./bin/weather-tool search "new york"
```

This will show you the airport codes (like ENGM, EGLL, KJFK) that you can use in your plots.

## What's Next?

Now that you have the basics working, you can:

1. **Explore more commands**: Run `./bin/weather-tool --help` to see all options
2. **Try the Python API**: Look at `examples/basic_plotting.py`
3. **Customize settings**: Edit `config/settings.yaml`
4. **Read the main README**: For more advanced features

## Troubleshooting

### "python: command not found"

-   **On Windows**: Try `py` instead of `python`
-   **On Mac/Linux**: Make sure Python is installed and in your PATH

### "No module named 'requests'" (or similar)

-   Run: `pip install -r requirements.txt`
-   If that fails: `pip install --user -r requirements.txt`

### "Permission denied" errors

-   **On Windows**: Run command prompt as Administrator
-   **On Mac/Linux**: Add `--user` to pip commands: `pip install --user -r requirements.txt`

### "Cannot connect to weather service"

-   Check your internet connection
-   Try again in a few minutes (the service might be busy)
-   Use `./bin/weather-tool test-connection` to check what's working

### Plot looks wrong or empty

-   Make sure you used a valid airport code (try `./bin/weather-tool search "airport name"`)
-   Check that the time range isn't too far in the past
-   Try a different airport code to see if it's a data issue

### Still having problems?

1. Make sure you followed each step exactly
2. Check that all prerequisites are installed
3. Try the examples in this guide first
4. Look for error messages and search for them online

## Getting Help

-   **Command help**: Add `--help` to any command
-   **Examples**: Look in the `examples/` folder
-   **Configuration**: Check `config/settings.yaml`
-   **Issues**: Create an issue on the project repository

Remember: Everyone starts somewhere! Don't hesitate to ask questions and experiment with the tool.
