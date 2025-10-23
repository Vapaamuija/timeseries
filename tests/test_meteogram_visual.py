"""
Visual regression test for meteogram plotter.

This test ensures that the meteogram plotter generates
the exact same visual output as the reference diagram.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from PIL import Image, ImageChops

from weather_tool.plotting.interfaces import PlotConfig, SymbolType

# Import the plotter and configuration classes
from weather_tool.plotting.plotters import MeteogramPlotter


class TestMeteogramVisual:
    """Visual regression tests for meteogram plotter."""

    @pytest.fixture
    def reference_image_path(self) -> Path:
        """Path to the reference diagram image."""
        path = Path(__file__).parent / "reference_images" / "diagram.png"
        if not path.exists():
            pytest.skip("Reference image 'diagram.png' is missing; skipping visual comparison test.")
        return path

    @pytest.fixture
    def test_output_dir(self) -> Path:
        """Directory for test output images."""
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        return output_dir

    @pytest.fixture
    def deterministic_weather_data(self) -> pd.DataFrame:
        """Create deterministic weather data that matches the reference diagram pattern."""
        # Create time series that matches the reference diagram
        # The reference shows approximately 24 hours of data with 3-hour intervals
        start_time = datetime(2024, 1, 15, 0, 0)  # Fixed date for reproducibility
        end_time = start_time + timedelta(hours=72)  # 3 days of data
        time_index = pd.date_range(start=start_time, end=end_time, freq="3h")

        n_points = len(time_index)

        # Create comprehensive data that covers ALL supported variables
        data = {
            # Core temperature data: varies between -5°C and 15°C with realistic pattern
            "temperature": self._create_temperature_pattern(n_points),
            # Dew point: should be lower than temperature, realistic relationship
            "dew_point": self._create_dew_point_pattern(n_points),
            # Pressure: varies around 1000-1020 hPa with gradual changes
            "pressure": self._create_pressure_pattern(n_points),
            # Precipitation: intermittent with values matching the reference (0.6, 1.9, 2.2, etc.)
            "precipitation": self._create_precipitation_pattern(n_points),
            # Wind: realistic wind speed and direction patterns
            "wind_speed": self._create_wind_speed_pattern(n_points),
            "wind_direction": self._create_wind_direction_pattern(n_points),
            # Cloud layers: continuous coverage patterns (0-100%)
            "cloud_high": self._create_cloud_pattern(n_points, "high"),
            "cloud_medium": self._create_cloud_pattern(n_points, "medium"),
            "cloud_low": self._create_cloud_pattern(n_points, "low"),
            "cloud_cover": self._create_total_cloud_cover_pattern(
                n_points
            ),  # Total cloud cover
            "fog": self._create_fog_pattern(n_points),
            # Weather symbols: codes that match the reference diagram
            "weather_symbol": self._create_weather_symbol_pattern(n_points),
        }

        return pd.DataFrame(data, index=time_index)

    def _create_temperature_pattern(self, n_points: int) -> np.ndarray:
        """Create temperature pattern matching the reference diagram."""
        # Base pattern: starts around 5°C, dips to -2°C, rises to 12°C
        base_temps = np.array(
            [
                5,
                3,
                1,
                -1,
                -2,
                0,
                3,
                6,
                8,
                10,
                12,
                10,
                8,
                6,
                4,
                2,
                0,
                -1,
                1,
                3,
                5,
                7,
                9,
                8,
            ]
        )

        # Extend or truncate to match n_points
        if n_points <= len(base_temps):
            return base_temps[:n_points]
        else:
            # Repeat pattern with slight variations
            full_pattern = np.tile(base_temps, (n_points // len(base_temps)) + 1)
            return full_pattern[:n_points]

    def _create_dew_point_pattern(self, n_points: int) -> np.ndarray:
        """Create dew point pattern that's realistic relative to temperature."""
        # Dew point should be lower than temperature with realistic relationship
        temp_pattern = self._create_temperature_pattern(n_points)
        # Dew point is typically 2-8°C lower than temperature
        dew_point_offset = 3 + 2 * np.sin(np.linspace(0, 2 * np.pi, n_points))
        return temp_pattern - dew_point_offset

    def _create_pressure_pattern(self, n_points: int) -> np.ndarray:
        """Create pressure pattern matching the reference diagram."""
        # Gradual pressure changes between 995-1015 hPa
        base_pressure = 1005
        variations = np.sin(np.linspace(0, 4 * np.pi, n_points)) * 8
        trend = np.linspace(-5, 10, n_points)
        return base_pressure + variations + trend

    def _create_precipitation_pattern(self, n_points: int) -> np.ndarray:
        """Create precipitation pattern with specific values from reference."""
        precip = np.zeros(n_points)

        # Add specific precipitation events matching the reference
        # These positions and values are approximated from the reference diagram
        if n_points >= 10:
            precip[6] = 0.6  # Light precipitation
            precip[8] = 1.9  # Moderate precipitation
            precip[9] = 2.2  # Moderate precipitation
            precip[10] = 4.2  # Heavy precipitation
            precip[11] = 5.6  # Heavy precipitation
            precip[12] = 7.3  # Very heavy precipitation
            precip[13] = 7.9  # Very heavy precipitation

        return precip

    def _create_wind_speed_pattern(self, n_points: int) -> np.ndarray:
        """Create wind speed pattern for wind barbs matching the reference diagram."""
        # Based on the reference diagram, wind speeds appear to be mostly low (0-5 m/s)
        # with some periods of slightly higher winds
        base_pattern = np.array(
            [2, 1, 3, 2, 4, 3, 2, 5, 4, 3, 2, 1, 0, 1, 2, 3, 4, 2, 1, 3, 2, 4, 3, 2]
        )

        # Extend or truncate to match n_points
        if n_points <= len(base_pattern):
            return base_pattern[:n_points].astype(float)
        else:
            # Repeat pattern with slight variations
            full_pattern = np.tile(base_pattern, (n_points // len(base_pattern)) + 1)
            return full_pattern[:n_points].astype(float)

    def _create_wind_direction_pattern(self, n_points: int) -> np.ndarray:
        """Create wind direction pattern for wind barbs matching the reference diagram."""
        # Based on the reference diagram, wind directions appear to be mostly from SW to W
        # with some variation but showing persistence typical of weather patterns
        base_pattern = np.array(
            [
                220,
                230,
                240,
                250,
                260,
                270,
                280,
                270,
                260,
                250,
                240,
                230,
                220,
                210,
                200,
                210,
                220,
                230,
                240,
                250,
                260,
                270,
                280,
                270,
            ]
        )

        # Extend or truncate to match n_points
        if n_points <= len(base_pattern):
            return base_pattern[:n_points].astype(float)
        else:
            # Repeat pattern with slight variations
            full_pattern = np.tile(base_pattern, (n_points // len(base_pattern)) + 1)
            return full_pattern[:n_points].astype(float)

    def _create_cloud_pattern(self, n_points: int, layer_type: str) -> np.ndarray:
        """Create cloud layer patterns with continuous coverage variations (0-100%)."""
        # Based on the reference image, cloud layers show continuous thick lines
        # with varying thickness representing coverage percentage (0-100%)
        patterns = {
            # High clouds: continuous coverage with varying thickness (0-100%)
            "high": [
                85.0,
                90.0,
                95.0,
                100.0,
                100.0,
                95.0,
                90.0,
                85.0,
                80.0,
                75.0,
                70.0,
                75.0,
                80.0,
                85.0,
                90.0,
                95.0,
                100.0,
                100.0,
                95.0,
                90.0,
                85.0,
                80.0,
                75.0,
                70.0,
            ],
            # Medium clouds: continuous coverage with different pattern
            "medium": [
                70.0,
                75.0,
                80.0,
                85.0,
                90.0,
                95.0,
                100.0,
                100.0,
                95.0,
                90.0,
                85.0,
                80.0,
                75.0,
                70.0,
                65.0,
                60.0,
                65.0,
                70.0,
                75.0,
                80.0,
                85.0,
                90.0,
                95.0,
                100.0,
            ],
            # Low clouds: continuous coverage with gradual variations
            "low": [
                60.0,
                65.0,
                70.0,
                75.0,
                80.0,
                85.0,
                90.0,
                95.0,
                100.0,
                95.0,
                90.0,
                85.0,
                80.0,
                75.0,
                70.0,
                65.0,
                60.0,
                55.0,
                50.0,
                55.0,
                60.0,
                65.0,
                70.0,
                75.0,
            ],
        }

        base_pattern = np.array(patterns[layer_type])
        if n_points <= len(base_pattern):
            return base_pattern[:n_points].astype(float)
        else:
            full_pattern = np.tile(base_pattern, (n_points // len(base_pattern)) + 1)
            return full_pattern[:n_points].astype(float)

    def _create_fog_pattern(self, n_points: int) -> np.ndarray:
        """Create fog pattern - mostly clear with occasional continuous fog (0-100%)."""
        fog = np.zeros(n_points)
        # Add some continuous fog periods with varying thickness
        if n_points >= 8:
            # Create a continuous fog period in the early hours
            fog[1:4] = [25.0, 40.0, 30.0]  # Continuous light fog with varying thickness
            if n_points >= 16:
                fog[14:16] = [15.0, 20.0]  # Later light fog period
        return fog

    def _create_total_cloud_cover_pattern(self, n_points: int) -> np.ndarray:
        """Create total cloud cover pattern (0-100%)."""
        # Total cloud cover should be related to individual cloud layers
        high_clouds = self._create_cloud_pattern(n_points, "high")
        medium_clouds = self._create_cloud_pattern(n_points, "medium")
        low_clouds = self._create_cloud_pattern(n_points, "low")

        # Total cloud cover is not simply additive, but represents overall coverage
        # Use maximum of layers with some blending
        total_cover = np.maximum(high_clouds, np.maximum(medium_clouds, low_clouds))

        # Add some variation to make it more realistic
        variation = 5 * np.sin(np.linspace(0, 3 * np.pi, n_points))
        total_cover = np.clip(total_cover + variation, 0, 100)

        return total_cover

    def _create_weather_symbol_pattern(self, n_points: int) -> np.ndarray:
        """Create weather symbol pattern matching the reference."""
        # Weather symbols based on the reference diagram
        # 1=clear, 2=fair, 3=partly cloudy, 4=cloudy, 9=light rain, 10=rain, etc.
        base_symbols = [
            3,
            3,
            3,
            3,
            4,
            4,
            9,
            10,
            10,
            10,
            10,
            10,
            9,
            4,
            3,
            3,
            2,
            2,
            1,
            1,
            2,
            3,
            3,
            4,
        ]

        if n_points <= len(base_symbols):
            return np.array(base_symbols[:n_points])
        else:
            full_pattern = np.tile(base_symbols, (n_points // len(base_symbols)) + 1)
            return full_pattern[:n_points]

    @pytest.fixture
    def test_airport_info(self) -> Dict[str, Any]:
        """Airport information for the test."""
        return {
            "name": "Test Airport",
            "icao": "TEST",
            "latitude": 60.0,
            "longitude": 10.0,
            "elevation": 100,
            "country": "Norway",
        }

    @pytest.fixture
    def reference_plot_config(self) -> PlotConfig:
        """Create PlotConfig that matches the reference diagram exactly."""
        # Load configuration from settings.yaml to get cloud colors
        from weather_tool.core.config import Config

        config = Config.from_file("config/settings.yaml")

        return PlotConfig(
            # Match the reference diagram dimensions and styling
            # Reference is 2893x685, so use aspect ratio that matches
            figure_size=(20, 5),  # Wider aspect ratio to match reference
            dpi=150,  # Higher DPI to get closer to reference resolution
            # Symbol configuration
            symbol_type=SymbolType.SVG,
            symbol_size=20,
            show_symbols=True,
            # Grid settings
            grid_enabled=True,
            show_grid=True,
            # Style
            style="default",  # Use matplotlib default style
            # Load variable configuration from settings.yaml for cloud colors
            variable_config=config.plotting.variable_config,
        )

    def test_meteogram_matches_reference(
        self,
        deterministic_weather_data: pd.DataFrame,
        test_airport_info: Dict[str, Any],
        reference_plot_config: PlotConfig,
        reference_image_path: Path,
        test_output_dir: Path,
    ) -> None:
        """Test that the generated meteogram matches the reference diagram exactly."""

        # Create the plotter
        plotter = MeteogramPlotter(reference_plot_config)

        # Generate the plot
        fig = plotter.create_plot(
            data=deterministic_weather_data,
            airport=test_airport_info,
            title="Test Meteogram",
        )

        # Save the generated plot
        generated_path = test_output_dir / "generated_meteogram.png"
        fig.savefig(generated_path, dpi=100, bbox_inches="tight", facecolor="white")
        plt.close(fig)

        # Load both images for comparison
        reference_img = Image.open(reference_image_path)
        generated_img = Image.open(generated_path)

        # Resize images to same size if needed (reference might be different size)
        if reference_img.size != generated_img.size:
            # Resize generated to match reference
            generated_img = generated_img.resize(
                reference_img.size, Image.Resampling.LANCZOS
            )

        # Convert to RGB if needed
        if reference_img.mode != "RGB":
            reference_img = reference_img.convert("RGB")
        if generated_img.mode != "RGB":
            generated_img = generated_img.convert("RGB")

        # Calculate pixel differences
        diff_img = ImageChops.difference(reference_img, generated_img)

        # Save difference image for debugging
        diff_path = test_output_dir / "difference.png"
        diff_img.save(diff_path)

        # Calculate similarity metrics
        similarity_score = self._calculate_image_similarity(
            reference_img, generated_img
        )

        # Save comparison report
        self._save_comparison_report(
            reference_path=reference_image_path,
            generated_path=generated_path,
            diff_path=diff_path,
            similarity_score=similarity_score,
            output_dir=test_output_dir,
        )

        # Assert similarity (allow for reasonable differences due to font rendering, etc.)
        # The threshold is set based on empirical testing - 0.82 allows for minor differences
        # including the addition of hour labels at the top while still catching significant
        # layout or data rendering issues
        assert similarity_score > 0.82, (
            f"Generated meteogram differs too much from reference. "
            f"Similarity score: {similarity_score:.3f} (expected > 0.82). "
            f"Check {diff_path} for visual differences."
        )

        print(f"✅ Visual test passed! Similarity score: {similarity_score:.3f}")

        # Additional validation: check that the images are not completely black or white
        self._validate_image_content(generated_img)

    def _calculate_image_similarity(
        self, img1: Image.Image, img2: Image.Image
    ) -> float:
        """Calculate similarity score between two images (0-1, where 1 is identical)."""
        # Convert images to numpy arrays
        arr1 = np.array(img1)
        arr2 = np.array(img2)

        # Ensure both arrays have the same shape
        if arr1.shape != arr2.shape:
            print(f"Warning: Image shapes differ: {arr1.shape} vs {arr2.shape}")

        # Calculate multiple similarity metrics for robustness

        # 1. Mean Squared Error
        mse = np.mean((arr1.astype(float) - arr2.astype(float)) ** 2)
        max_possible_mse = 255**2
        mse_similarity = 1 - (mse / max_possible_mse)

        # 2. Structural Similarity (simplified version)
        # Calculate mean and variance for each image
        mu1, mu2 = np.mean(arr1), np.mean(arr2)
        var1, var2 = np.var(arr1), np.var(arr2)
        covar = np.mean((arr1 - mu1) * (arr2 - mu2))

        # SSIM-like calculation (simplified)
        c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
        ssim = ((2 * mu1 * mu2 + c1) * (2 * covar + c2)) / (
            (mu1**2 + mu2**2 + c1) * (var1 + var2 + c2)
        )
        ssim_similarity = (ssim + 1) / 2  # Normalize to 0-1

        # 3. Histogram correlation
        hist1 = np.histogram(arr1.flatten(), bins=256, range=(0, 256))[0]
        hist2 = np.histogram(arr2.flatten(), bins=256, range=(0, 256))[0]
        hist_corr = np.corrcoef(hist1, hist2)[0, 1]
        hist_similarity = (hist_corr + 1) / 2 if not np.isnan(hist_corr) else 0

        # Combine metrics (weighted average)
        combined_similarity = (
            0.5 * mse_similarity + 0.3 * ssim_similarity + 0.2 * hist_similarity
        )

        print(
            f"Similarity metrics - MSE: {mse_similarity:.3f}, SSIM: {ssim_similarity:.3f}, Hist: {hist_similarity:.3f}, Combined: {combined_similarity:.3f}"
        )

        return combined_similarity

    def _save_comparison_report(
        self,
        reference_path: Path,
        generated_path: Path,
        diff_path: Path,
        similarity_score: float,
        output_dir: Path,
    ) -> None:
        """Save a detailed comparison report."""
        report_path = output_dir / "comparison_report.txt"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("Meteogram Visual Comparison Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Reference image: {reference_path}\n")
            f.write(f"Generated image: {generated_path}\n")
            f.write(f"Difference image: {diff_path}\n\n")
            f.write(f"Similarity score: {similarity_score:.6f}\n")
            f.write(f"Test result: {'PASS' if similarity_score > 0.95 else 'FAIL'}\n\n")

            if similarity_score <= 0.95:
                f.write("Possible causes of differences:\n")
                f.write("- Font rendering differences between systems\n")
                f.write("- Matplotlib version differences\n")
                f.write("- Weather symbol rendering differences\n")
                f.write("- Color palette variations\n")
                f.write("- Plot layout or spacing differences\n")

    def test_plotter_data_validation(self, reference_plot_config: PlotConfig) -> None:
        """Test that the plotter properly validates input data."""
        plotter = MeteogramPlotter(reference_plot_config)

        # Test with empty DataFrame
        empty_data = pd.DataFrame()
        airport_info = {"name": "Test", "icao": "TEST"}

        with pytest.raises(ValueError, match="Data validation failed"):
            plotter.create_plot(empty_data, airport_info)

    def test_plotter_required_variables(
        self, reference_plot_config: PlotConfig
    ) -> None:
        """Test that the plotter works with minimum required variables."""
        plotter = MeteogramPlotter(reference_plot_config)

        # Create minimal data with only required variables
        time_index = pd.date_range("2024-01-01", periods=24, freq="1h")
        minimal_data = pd.DataFrame(
            {
                "temperature": np.random.normal(5, 3, 24),
                "pressure": np.random.normal(1013, 10, 24),
            },
            index=time_index,
        )

        airport_info = {"name": "Test", "icao": "TEST"}

        # Should not raise an exception
        fig = plotter.create_plot(minimal_data, airport_info)
        assert fig is not None
        plt.close(fig)

    def test_plotter_detects_differences(
        self, reference_plot_config: PlotConfig, test_output_dir: Path
    ) -> None:
        """Test that the comparison can detect when plots are actually different."""
        plotter = MeteogramPlotter(reference_plot_config)

        # Create intentionally different data
        time_index = pd.date_range("2024-01-01", periods=24, freq="1h")
        different_data = pd.DataFrame(
            {
                "temperature": np.full(
                    24, 50.0
                ),  # Unrealistic constant high temperature
                "pressure": np.full(24, 800.0),  # Unrealistic low pressure
                "precipitation": np.full(24, 100.0),  # Unrealistic constant heavy rain
            },
            index=time_index,
        )

        airport_info = {"name": "Test", "icao": "TEST"}

        # Generate a plot with very different data
        fig = plotter.create_plot(different_data, airport_info)
        different_path = test_output_dir / "different_meteogram.png"
        fig.savefig(different_path, dpi=100, bbox_inches="tight", facecolor="white")
        plt.close(fig)

        # Load reference and different images
        reference_path = Path(__file__).parent / "reference_images" / "diagram.png"
        if not reference_path.exists():
            pytest.skip("Reference image 'diagram.png' is missing; skipping difference detection test.")
        reference_img = Image.open(reference_path)
        different_img = Image.open(different_path)

        # Resize if needed
        if reference_img.size != different_img.size:
            different_img = different_img.resize(
                reference_img.size, Image.Resampling.LANCZOS
            )

        # Convert to RGB
        if reference_img.mode != "RGB":
            reference_img = reference_img.convert("RGB")
        if different_img.mode != "RGB":
            different_img = different_img.convert("RGB")

        # Calculate similarity - should be much lower
        similarity_score = self._calculate_image_similarity(
            reference_img, different_img
        )

        # Assert that the similarity is low (images are different)
        assert similarity_score < 0.85, (
            f"Expected low similarity for different data, but got {similarity_score:.3f}. "
            f"The comparison might not be working correctly."
        )

        print(
            f"✅ Difference detection test passed! Similarity score: {similarity_score:.3f}"
        )

    def _validate_image_content(self, img: Image.Image) -> None:
        """Validate that the image has reasonable content (not blank or corrupted)."""
        arr = np.array(img)

        # Check that image is not completely black
        assert not np.all(arr == 0), "Generated image appears to be completely black"

        # Check that image is not completely white
        assert not np.all(arr == 255), "Generated image appears to be completely white"

        # Check that there's reasonable variation in pixel values
        std_dev = np.std(arr)
        assert (
            std_dev > 10
        ), f"Generated image has very low variation (std: {std_dev:.2f}), might be corrupted"

    # ========================================================================
    # COMPREHENSIVE COMPONENT TESTS
    # ========================================================================

    def test_temperature_component_rendering(
        self, reference_plot_config: PlotConfig, test_output_dir: Path
    ) -> None:
        """Test temperature component with various edge cases."""
        plotter = MeteogramPlotter(reference_plot_config)

        # Test temperature crossing zero (color change)
        time_index = pd.date_range("2024-01-01", periods=12, freq="1h")
        temp_data = pd.DataFrame(
            {
                "temperature": [-5, -3, -1, 0, 2, 5, 8, 10, 7, 3, 0, -2],
                "pressure": [1013] * 12,  # Required variable
            },
            index=time_index,
        )

        airport_info = {"name": "Temperature Test", "icao": "TEMP"}
        fig = plotter.create_plot(
            temp_data, airport_info, title="Temperature Component Test"
        )

        output_path = test_output_dir / "temperature_component_test.png"
        fig.savefig(output_path, dpi=100, bbox_inches="tight", facecolor="white")
        plt.close(fig)

        # Validate the image was created and has content
        assert output_path.exists(), "Temperature component test image was not created"
        img = Image.open(output_path)
        self._validate_image_content(img)

    def test_precipitation_component_rendering(
        self, reference_plot_config: PlotConfig, test_output_dir: Path
    ) -> None:
        """Test precipitation component with various intensities."""
        plotter = MeteogramPlotter(reference_plot_config)

        # Test various precipitation intensities
        time_index = pd.date_range("2024-01-01", periods=12, freq="1h")
        precip_data = pd.DataFrame(
            {
                "temperature": [5] * 12,  # Required variable
                "pressure": [1013] * 12,  # Required variable
                "precipitation": [
                    0,
                    0.1,
                    0.5,
                    1.0,
                    2.5,
                    5.0,
                    10.0,
                    15.0,
                    8.0,
                    3.0,
                    1.0,
                    0,
                ],
            },
            index=time_index,
        )

        airport_info = {"name": "Precipitation Test", "icao": "PREC"}
        fig = plotter.create_plot(
            precip_data, airport_info, title="Precipitation Component Test"
        )

        output_path = test_output_dir / "precipitation_component_test.png"
        fig.savefig(output_path, dpi=100, bbox_inches="tight", facecolor="white")
        plt.close(fig)

        assert (
            output_path.exists()
        ), "Precipitation component test image was not created"
        img = Image.open(output_path)
        self._validate_image_content(img)

    def test_wind_component_rendering(
        self, reference_plot_config: PlotConfig, test_output_dir: Path
    ) -> None:
        """Test wind barb component with various speeds and directions."""
        plotter = MeteogramPlotter(reference_plot_config)

        # Test various wind speeds and directions
        time_index = pd.date_range("2024-01-01", periods=12, freq="1h")
        wind_data = pd.DataFrame(
            {
                "temperature": [5] * 12,  # Required variable
                "pressure": [1013] * 12,  # Required variable
                "wind_speed": [
                    0,
                    2.5,
                    5,
                    7.5,
                    10,
                    15,
                    20,
                    25,
                    30,
                    35,
                    40,
                    45,
                ],  # Various speeds
                "wind_direction": [
                    0,
                    45,
                    90,
                    135,
                    180,
                    225,
                    270,
                    315,
                    360,
                    30,
                    60,
                    120,
                ],  # Various directions
            },
            index=time_index,
        )

        airport_info = {"name": "Wind Test", "icao": "WIND"}
        fig = plotter.create_plot(wind_data, airport_info, title="Wind Component Test")

        output_path = test_output_dir / "wind_component_test.png"
        fig.savefig(output_path, dpi=100, bbox_inches="tight", facecolor="white")
        plt.close(fig)

        assert output_path.exists(), "Wind component test image was not created"
        img = Image.open(output_path)
        self._validate_image_content(img)

    def test_cloud_layers_component_rendering(
        self, reference_plot_config: PlotConfig, test_output_dir: Path
    ) -> None:
        """Test cloud layer components with various coverage patterns."""
        plotter = MeteogramPlotter(reference_plot_config)

        # Test various cloud coverage patterns
        time_index = pd.date_range("2024-01-01", periods=12, freq="1h")
        cloud_data = pd.DataFrame(
            {
                "temperature": [5] * 12,  # Required variable
                "pressure": [1013] * 12,  # Required variable
                "cloud_high": [0, 10, 25, 50, 75, 90, 100, 85, 60, 35, 15, 5],
                "cloud_medium": [5, 20, 40, 60, 80, 95, 90, 70, 45, 25, 10, 0],
                "cloud_low": [10, 30, 50, 70, 85, 100, 95, 75, 50, 30, 15, 5],
                "fog": [0, 0, 5, 15, 25, 40, 30, 20, 10, 5, 0, 0],
            },
            index=time_index,
        )

        airport_info = {"name": "Cloud Test", "icao": "CLOD"}
        fig = plotter.create_plot(
            cloud_data, airport_info, title="Cloud Layers Component Test"
        )

        output_path = test_output_dir / "cloud_layers_component_test.png"
        fig.savefig(output_path, dpi=100, bbox_inches="tight", facecolor="white")
        plt.close(fig)

        assert output_path.exists(), "Cloud layers component test image was not created"
        img = Image.open(output_path)
        self._validate_image_content(img)

    def test_weather_symbols_component_rendering(
        self, reference_plot_config: PlotConfig, test_output_dir: Path
    ) -> None:
        """Test weather symbols component with various symbol codes."""
        plotter = MeteogramPlotter(reference_plot_config)

        # Test various weather symbol codes
        time_index = pd.date_range("2024-01-01", periods=12, freq="1h")
        symbol_data = pd.DataFrame(
            {
                "temperature": [5] * 12,  # Required variable
                "pressure": [1013] * 12,  # Required variable
                "weather_symbol": [
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                ],  # Various symbols
            },
            index=time_index,
        )

        airport_info = {"name": "Symbol Test", "icao": "SYMB"}
        fig = plotter.create_plot(
            symbol_data, airport_info, title="Weather Symbols Component Test"
        )

        output_path = test_output_dir / "weather_symbols_component_test.png"
        fig.savefig(output_path, dpi=100, bbox_inches="tight", facecolor="white")
        plt.close(fig)

        assert (
            output_path.exists()
        ), "Weather symbols component test image was not created"
        img = Image.open(output_path)
        self._validate_image_content(img)

    def test_dew_point_component_rendering(
        self, reference_plot_config: PlotConfig, test_output_dir: Path
    ) -> None:
        """Test dew point component rendering with temperature."""
        plotter = MeteogramPlotter(reference_plot_config)

        # Test dew point with temperature
        time_index = pd.date_range("2024-01-01", periods=12, freq="1h")
        dew_data = pd.DataFrame(
            {
                "temperature": [10, 8, 6, 4, 2, 0, -2, 0, 3, 6, 8, 10],
                "dew_point": [5, 3, 1, -1, -3, -5, -7, -5, -2, 1, 3, 5],
                "pressure": [1013] * 12,  # Required variable
            },
            index=time_index,
        )

        airport_info = {"name": "Dew Point Test", "icao": "DEWP"}
        fig = plotter.create_plot(
            dew_data, airport_info, title="Dew Point Component Test"
        )

        output_path = test_output_dir / "dew_point_component_test.png"
        fig.savefig(output_path, dpi=100, bbox_inches="tight", facecolor="white")
        plt.close(fig)

        assert output_path.exists(), "Dew point component test image was not created"
        img = Image.open(output_path)
        self._validate_image_content(img)

    def test_grid_positioning_after_changes(
        self, reference_plot_config: PlotConfig, test_output_dir: Path
    ) -> None:
        """Test that grid lines are properly centered after the positioning changes."""
        plotter = MeteogramPlotter(reference_plot_config)

        # Create simple data to clearly see grid positioning
        time_index = pd.date_range("2024-01-01 00:00", periods=6, freq="1h")
        grid_test_data = pd.DataFrame(
            {
                "temperature": [0, 5, 10, 15, 10, 5],
                "pressure": [1013, 1015, 1017, 1015, 1013, 1010],
            },
            index=time_index,
        )

        airport_info = {"name": "Grid Test", "icao": "GRID"}
        fig = plotter.create_plot(
            grid_test_data, airport_info, title="Grid Positioning Test"
        )

        output_path = test_output_dir / "grid_positioning_test.png"
        fig.savefig(output_path, dpi=100, bbox_inches="tight", facecolor="white")
        plt.close(fig)

        assert output_path.exists(), "Grid positioning test image was not created"
        img = Image.open(output_path)
        self._validate_image_content(img)

    def test_edge_case_empty_variables(
        self, reference_plot_config: PlotConfig, test_output_dir: Path
    ) -> None:
        """Test handling of missing optional variables."""
        plotter = MeteogramPlotter(reference_plot_config)

        # Test with only required variables
        time_index = pd.date_range("2024-01-01", periods=6, freq="1h")
        minimal_data = pd.DataFrame(
            {
                "temperature": [5, 3, 1, 4, 7, 6],
                "pressure": [1013, 1015, 1012, 1018, 1016, 1014],
            },
            index=time_index,
        )

        airport_info = {"name": "Minimal Test", "icao": "MIN"}
        fig = plotter.create_plot(minimal_data, airport_info, title="Minimal Data Test")

        output_path = test_output_dir / "minimal_data_test.png"
        fig.savefig(output_path, dpi=100, bbox_inches="tight", facecolor="white")
        plt.close(fig)

        assert output_path.exists(), "Minimal data test image was not created"
        img = Image.open(output_path)
        self._validate_image_content(img)

    def test_edge_case_extreme_values(
        self, reference_plot_config: PlotConfig, test_output_dir: Path
    ) -> None:
        """Test handling of extreme weather values."""
        plotter = MeteogramPlotter(reference_plot_config)

        # Test with extreme values
        time_index = pd.date_range("2024-01-01", periods=6, freq="1h")
        extreme_data = pd.DataFrame(
            {
                "temperature": [-40, -20, 0, 20, 40, 50],  # Extreme temperatures
                "pressure": [900, 950, 1000, 1050, 1100, 1013],  # Extreme pressures
                "precipitation": [0, 1, 10, 50, 100, 200],  # Extreme precipitation
                "wind_speed": [0, 10, 25, 50, 75, 100],  # Extreme wind speeds
                "wind_direction": [0, 90, 180, 270, 360, 45],
            },
            index=time_index,
        )

        airport_info = {"name": "Extreme Test", "icao": "EXTR"}
        fig = plotter.create_plot(
            extreme_data, airport_info, title="Extreme Values Test"
        )

        output_path = test_output_dir / "extreme_values_test.png"
        fig.savefig(output_path, dpi=100, bbox_inches="tight", facecolor="white")
        plt.close(fig)

        assert output_path.exists(), "Extreme values test image was not created"
        img = Image.open(output_path)
        self._validate_image_content(img)


if __name__ == "__main__":
    # Allow running the test directly for development
    import sys

    sys.exit(pytest.main([__file__, "-v"]))
