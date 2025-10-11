# Visual Regression Tests for Meteogram

This directory contains comprehensive visual regression tests to ensure that the meteogram plotter generates consistent, high-quality output that matches the reference diagram.

## Overview

The visual tests compare generated meteogram plots against a reference image (`reference_images/diagram.png`) using multiple similarity metrics to detect any visual regressions in the plotting code.

## Test Structure

### Main Test Files

-   **`test_meteogram_visual.py`** - Main test suite with visual comparison logic
-   **`run_visual_tests.py`** - Helper script for running and debugging tests
-   **`reference_images/diagram.png`** - Reference image for comparison
-   **`output/`** - Generated test outputs (created during test runs)

### Test Cases

#### Core Visual Regression Tests

1. **`test_meteogram_matches_reference`** - Main visual regression test

    - Generates a meteogram with deterministic test data covering ALL supported variables
    - Compares against reference image using multi-metric similarity analysis
    - Threshold: >0.82 similarity score (allows for minor font/rendering differences)

2. **`test_plotter_detects_differences`** - Validates that the comparison can detect real differences

    - Uses intentionally different data to generate a visually different plot
    - Ensures similarity score is <0.81 (confirms the test can catch regressions)

3. **`test_plotter_data_validation`** - Tests error handling for invalid data

4. **`test_plotter_required_variables`** - Tests minimum viable data requirements

#### Comprehensive Component Tests

5. **`test_temperature_component_rendering`** - Temperature component with zero-crossing

    - Tests temperature color changes (red above 0°C, blue below 0°C)
    - Validates proper rendering of temperature transitions

6. **`test_precipitation_component_rendering`** - Precipitation bars with various intensities

    - Tests precipitation rendering from 0 to 15mm with proper scaling
    - Validates precipitation value labels and bar heights

7. **`test_wind_component_rendering`** - Wind barbs with various speeds and directions

    - Tests wind speeds from 0 to 45 m/s with proper barb symbols
    - Tests all wind directions (0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°)

8. **`test_cloud_layers_component_rendering`** - Cloud layers with coverage patterns

    - Tests all cloud layers (high, medium, low, fog) with 0-100% coverage
    - Validates continuous thick line rendering with variable thickness

9. **`test_weather_symbols_component_rendering`** - Weather symbols rendering

    - Tests various weather symbol codes (1-12)
    - Validates symbol positioning and rendering quality

10. **`test_dew_point_component_rendering`** - Dew point with temperature relationship
    - Tests dew point rendering as dashed line
    - Validates realistic temperature-dew point relationships

#### Grid and Layout Tests

11. **`test_grid_positioning_after_changes`** - Grid positioning validation
    -   Tests that vertical grid lines are centered at hour midpoints (0.5, 1.5, 2.5, etc.)
    -   Validates alignment across all panels

#### Edge Case and Robustness Tests

12. **`test_edge_case_empty_variables`** - Minimal data handling

    -   Tests with only required variables (temperature, pressure)
    -   Validates graceful handling of missing optional variables

13. **`test_edge_case_extreme_values`** - Extreme weather values
    -   Tests extreme temperatures (-40°C to 50°C)
    -   Tests extreme pressures (900-1100 hPa)
    -   Tests extreme precipitation (0-200mm)
    -   Tests extreme wind speeds (0-100 m/s)

## Similarity Metrics

The visual comparison uses a weighted combination of three metrics:

1. **Mean Squared Error (MSE)** - Pixel-level differences (50% weight)
2. **Structural Similarity (SSIM)** - Perceptual similarity (30% weight)
3. **Histogram Correlation** - Color distribution similarity (20% weight)

This multi-metric approach provides robust detection of visual changes while being tolerant of minor rendering differences across systems.

## Running the Tests

### Basic Usage

```bash
# Run all visual tests
python -m pytest tests/test_meteogram_visual.py -v

# Run specific test
python -m pytest tests/test_meteogram_visual.py::TestMeteogramVisual::test_meteogram_matches_reference -v

# Run with detailed output
python -m pytest tests/test_meteogram_visual.py -v -s
```

### Using the Helper Script

```bash
# Run all tests with helper script
python tests/run_visual_tests.py

# Run with verbose output and show results
python tests/run_visual_tests.py --verbose --show-images

# Run specific test
python tests/run_visual_tests.py --test TestMeteogramVisual::test_meteogram_matches_reference

# Create side-by-side comparison
python tests/run_visual_tests.py --compare

# Clean test outputs
python tests/run_visual_tests.py --clean
```

## Interpreting Results

### Successful Test

```
Similarity metrics - MSE: 0.954, SSIM: 0.575, Hist: 0.997, Combined: 0.849
✅ Visual test passed! Similarity score: 0.849
```

### Failed Test

```
AssertionError: Generated meteogram differs too much from reference.
Similarity score: 0.723 (expected > 0.84).
Check /path/to/difference.png for visual differences.
```

### Test Outputs

When tests run, they generate several files in `tests/output/`:

-   **`generated_meteogram.png`** - The newly generated plot
-   **`difference.png`** - Pixel-by-pixel difference visualization
-   **`side_by_side_comparison.png`** - Reference and generated images side by side
-   **`comparison_report.txt`** - Detailed comparison metrics and results

## Debugging Visual Differences

### 1. Examine the Difference Image

The difference image highlights areas where the generated plot differs from the reference:

-   Black areas = identical pixels
-   Colored areas = differences (brighter = more different)

### 2. Check the Side-by-Side Comparison

```bash
python tests/run_visual_tests.py --compare
```

This creates a visual comparison showing reference (left) and generated (right) images.

### 3. Review Similarity Metrics

-   **Low MSE similarity** = Significant pixel differences
-   **Low SSIM similarity** = Structural/layout differences
-   **Low Histogram similarity** = Color distribution changes

### 4. Common Causes of Differences

-   Font rendering variations across systems
-   Matplotlib version differences
-   Weather symbol rendering changes
-   Plot layout or spacing modifications
-   Data processing changes affecting the visual output

## Updating the Reference Image

If legitimate changes are made to the plotter that should become the new baseline:

1. **Verify the changes are intentional and correct**
2. **Run the test to generate a new image**:

    ```bash
    python tests/run_visual_tests.py --verbose
    ```

3. **Examine the generated image** in `tests/output/generated_meteogram.png`
4. **If the new image is correct, replace the reference**:

    ```bash
    cp tests/output/generated_meteogram.png tests/reference_images/diagram.png
    ```

5. **Re-run tests to confirm they pass**

## Configuration

### Test Data

The test uses deterministic weather data designed to exercise ALL supported plot components:

#### Core Weather Parameters

-   **Temperature**: Realistic variations from -5°C to 15°C with zero-crossing for color testing
-   **Dew Point**: Realistic relationship with temperature (typically 2-8°C lower)
-   **Pressure**: Gradual changes between 995-1015 hPa with realistic trends

#### Precipitation and Wind

-   **Precipitation**: Intermittent events with specific values (0.6, 1.9, 2.2, 4.2, 5.6, 7.3, 7.9 mm)
-   **Wind Speed**: Realistic patterns from 2-15 m/s with variations
-   **Wind Direction**: Persistent patterns with realistic directional changes

#### Cloud Layers (All with 0-100% coverage)

-   **High Clouds**: Continuous coverage with varying thickness (85-100% patterns)
-   **Medium Clouds**: Different coverage patterns (60-100% patterns)
-   **Low Clouds**: Gradual variations (50-100% patterns)
-   **Total Cloud Cover**: Derived from individual layers with realistic blending
-   **Fog**: Occasional periods with varying thickness (0-40% coverage)

#### Weather Symbols

-   **Symbol Codes**: 1-12 representing various weather conditions
-   **Pattern**: Clear → Fair → Partly Cloudy → Cloudy → Light Rain → Rain → Heavy Rain

#### Test Data Characteristics

-   **Deterministic**: Uses fixed random seeds for reproducible results
-   **Comprehensive**: Covers all 12 supported variables from `get_supported_variables()`
-   **Realistic**: Maintains physical relationships between variables
-   **Edge Cases**: Includes zero-crossings, extreme values, and boundary conditions

### Plot Configuration

The test uses a `PlotConfig` optimized for visual comparison:

-   Figure size: (20, 5) - Wide aspect ratio matching reference
-   DPI: 150 - High resolution for detailed comparison
-   Theme system: Disabled - Uses explicit colors for consistency
-   Symbols: SVG type for crisp rendering

## Troubleshooting

### Test Fails on CI/CD

Visual tests can be sensitive to system differences. Consider:

-   Using Docker containers for consistent environments
-   Adjusting similarity thresholds for CI environments
-   Generating reference images on the same system type as CI

### Fonts Look Different

Font rendering can vary across systems:

-   Ensure consistent font installations
-   Consider using matplotlib's built-in fonts
-   Adjust font-related plot settings if needed

### Performance Issues

Visual tests can be slower than unit tests:

-   Use lower DPI for faster testing during development
-   Run visual tests separately from unit tests
-   Consider parallel test execution

## Best Practices

1. **Run visual tests before major releases**
2. **Update reference images when making intentional visual changes**
3. **Use the helper script for debugging during development**
4. **Keep test data deterministic for reproducible results**
5. **Document any intentional visual changes in commit messages**

## Integration with Development Workflow

### Pre-commit Checks

```bash
# Quick visual test before committing
python tests/run_visual_tests.py --test TestMeteogramVisual::test_meteogram_matches_reference
```

### Development Iteration

```bash
# Make changes to plotter code
# Run visual test with comparison
python tests/run_visual_tests.py --compare
# Examine differences and iterate
```

### Release Validation

```bash
# Full visual test suite
python -m pytest tests/test_meteogram_visual.py -v
# Review all outputs
python tests/run_visual_tests.py --show-images
```

This visual testing framework ensures that the meteogram plotter maintains consistent, high-quality output across code changes and system environments.
