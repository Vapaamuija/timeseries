"""
Unified weather symbols implementation.

This module consolidates all weather symbol functionality into a single,
clean implementation using official Met.no weather symbols from:
https://github.com/metno/weathericons/tree/main/weather
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import requests

from .interfaces import WeatherSymbolRenderer, PlotConfig, SymbolType


logger = logging.getLogger(__name__)


class UnifiedWeatherSymbols(WeatherSymbolRenderer):
    """Unified weather symbol renderer using ONLY official Met.no SVG symbols.
    
    This renderer exclusively uses SVG symbols from the official Met.no weather icons repository.
    No fallback markers are used - if SVG rendering fails, symbols are simply skipped.
    
    REQUIRED dependencies for SVG rendering:
        pip install cairosvg pillow
    
    Or run the setup script:
        ./setup_svg_rendering.sh
    
    If SVG rendering is not available, no weather symbols will be displayed.
    """
    
    def __init__(self, config: PlotConfig):
        """Initialize unified weather symbols.
        
        Args:
            config: Plot configuration
        """
        super().__init__(config)
        
        # Official Met.no weather icons repository
        self.icon_base_url = "https://raw.githubusercontent.com/metno/weathericons/main/weather/svg/"
        self.icon_cache_dir = Path("data/metno_weather_icons")
        
        # Create comprehensive symbol mapping
        self.symbol_mapping = self._create_metno_symbol_mapping()
        
        # Always use SVG symbols - this is the only supported type
        self.config.symbol_type = SymbolType.SVG
        logger.info("Using SVG icons from Met.no repository")
        
        # Auto-download icons if enabled
        if config.auto_download_icons:
            self._ensure_icons_available()
    
    def _create_metno_symbol_mapping(self) -> Dict[str, Dict[str, Any]]:
        """Create comprehensive Met.no symbol mapping.
        
        Returns:
            Dictionary mapping symbol codes to display properties
        """
        symbols = {
            # Clear sky
            'clearsky_day': {
                'svg': 'clearsky_day.svg',
                'color': '#FFD700', 'description': 'Clear sky'
            },
            'clearsky_night': {
                'svg': 'clearsky_night.svg',
                'color': '#4169E1', 'description': 'Clear sky'
            },
            'clearsky_polartwilight': {
                'svg': 'clearsky_polartwilight.svg',
                'color': '#FF8C00', 'description': 'Clear sky (polar twilight)'
            },
            
            # Fair weather
            'fair_day': {
                'svg': 'fair_day.svg',
                'color': '#FFD700', 'description': 'Fair'
            },
            'fair_night': {
                'svg': 'fair_night.svg',
                'color': '#4169E1', 'description': 'Fair'
            },
            'fair_polartwilight': {
                'svg': 'fair_polartwilight.svg',
                'color': '#FF8C00', 'description': 'Fair (polar twilight)'
            },
            
            # Partly cloudy
            'partlycloudy_day': {
                'svg': 'partlycloudy_day.svg',
                'color': '#87CEEB', 'description': 'Partly cloudy'
            },
            'partlycloudy_night': {
                'svg': 'partlycloudy_night.svg',
                'color': '#696969', 'description': 'Partly cloudy'
            },
            'partlycloudy_polartwilight': {
                'svg': 'partlycloudy_polartwilight.svg',
                'color': '#696969', 'description': 'Partly cloudy (polar twilight)'
            },
            
            # Cloudy
            'cloudy': {
                'svg': 'cloudy.svg',
                'color': '#696969', 'description': 'Cloudy'
            },
            
            # Rain showers
            'lightrainshowers_day': {
                'svg': 'lightrainshowers_day.svg',
                'color': '#4682B4', 'description': 'Light rain showers'
            },
            'lightrainshowers_night': {
                'svg': 'lightrainshowers_night.svg',
                'color': '#4682B4', 'description': 'Light rain showers'
            },
            'lightrainshowers_polartwilight': {
                'svg': 'lightrainshowers_polartwilight.svg',
                'color': '#4682B4', 'description': 'Light rain showers (polar twilight)'
            },
            
            'rainshowers_day': {
                'svg': 'rainshowers_day.svg',
                'color': '#1E90FF', 'description': 'Rain showers'
            },
            'rainshowers_night': {
                'svg': 'rainshowers_night.svg',
                'color': '#1E90FF', 'description': 'Rain showers'
            },
            'rainshowers_polartwilight': {
                'svg': 'rainshowers_polartwilight.svg',
                'color': '#1E90FF', 'description': 'Rain showers (polar twilight)'
            },
            
            'heavyrainshowers_day': {
                'svg': 'heavyrainshowers_day.svg',
                'color': '#0000CD', 'description': 'Heavy rain showers'
            },
            'heavyrainshowers_night': {
                'svg': 'heavyrainshowers_night.svg',
                'color': '#0000CD', 'description': 'Heavy rain showers'
            },
            'heavyrainshowers_polartwilight': {
                'svg': 'heavyrainshowers_polartwilight.svg',
                'color': '#0000CD', 'description': 'Heavy rain showers (polar twilight)'
            },
            
            # Rain
            'lightrain': {
                'svg': 'lightrain.svg',
                'color': '#4682B4', 'description': 'Light rain'
            },
            'rain': {
                'svg': 'rain.svg',
                'color': '#1E90FF', 'description': 'Rain'
            },
            'heavyrain': {
                'svg': 'heavyrain.svg',
                'color': '#0000CD', 'description': 'Heavy rain'
            },
            
            # Snow showers
            'lightsnowshowers_day': {
                'svg': 'lightsnowshowers_day.svg',
                'color': '#B0E0E6', 'description': 'Light snow showers'
            },
            'lightsnowshowers_night': {
                'svg': 'lightsnowshowers_night.svg',
                'color': '#B0E0E6', 'description': 'Light snow showers'
            },
            'lightsnowshowers_polartwilight': {
                'svg': 'lightsnowshowers_polartwilight.svg',
                'color': '#B0E0E6', 'description': 'Light snow showers (polar twilight)'
            },
            
            'snowshowers_day': {
                'svg': 'snowshowers_day.svg',
                'color': '#87CEEB', 'description': 'Snow showers'
            },
            'snowshowers_night': {
                'svg': 'snowshowers_night.svg',
                'color': '#87CEEB', 'description': 'Snow showers'
            },
            'snowshowers_polartwilight': {
                'svg': 'snowshowers_polartwilight.svg',
                'color': '#87CEEB', 'description': 'Snow showers (polar twilight)'
            },
            
            'heavysnowshowers_day': {
                'svg': 'heavysnowshowers_day.svg',
                'color': '#4169E1', 'description': 'Heavy snow showers'
            },
            'heavysnowshowers_night': {
                'svg': 'heavysnowshowers_night.svg',
                'color': '#4169E1', 'description': 'Heavy snow showers'
            },
            'heavysnowshowers_polartwilight': {
                'svg': 'heavysnowshowers_polartwilight.svg',
                'color': '#4169E1', 'description': 'Heavy snow showers (polar twilight)'
            },
            
            # Snow
            'lightsnow': {
                'svg': 'lightsnow.svg',
                'color': '#B0E0E6', 'description': 'Light snow'
            },
            'snow': {
                'svg': 'snow.svg',
                'color': '#87CEEB', 'description': 'Snow'
            },
            'heavysnow': {
                'svg': 'heavysnow.svg',
                'color': '#4169E1', 'description': 'Heavy snow'
            },
            
            # Sleet
            'lightsleet': {
                'svg': 'lightsleet.svg',
                'color': '#20B2AA', 'description': 'Light sleet'
            },
            'sleet': {
                'svg': 'sleet.svg',
                'color': '#008B8B', 'description': 'Sleet'
            },
            'heavysleet': {
                'svg': 'heavysleet.svg',
                'color': '#006400', 'description': 'Heavy sleet'
            },
            
            # Thunder
            'lightrainandthundershowers_day': {
                'svg': 'lightrainandthundershowers_day.svg',
                'color': '#8B008B', 'description': 'Light rain and thunder showers'
            },
            'rainandthunder': {
                'svg': 'rainandthunder.svg',
                'color': '#8B008B', 'description': 'Rain and thunder'
            },
            
            # Fog
            'fog': {
                'svg': 'fog.svg',
                'color': '#696969', 'description': 'Fog'
            },
        }
        
        return symbols
    
    def has_high_quality_svg_support(self) -> bool:
        """Check if high-quality SVG rendering is available.
        
        Returns:
            True if cairosvg and PIL are available for true SVG rendering
        """
        try:
            # Set up environment variables for Cairo detection based on OS
            self._setup_cairo_environment()
            
            import cairosvg
            from PIL import Image
            import warnings
            import sys
            import os
            
            # Suppress verbose Cairo error messages
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                # Temporarily redirect stderr to suppress Cairo library errors
                original_stderr = sys.stderr
                try:
                    # Redirect stderr to devnull to suppress Cairo errors
                    sys.stderr = open(os.devnull, 'w')
                    
                    # Test if cairosvg actually works by trying a simple conversion
                    cairosvg.svg2png(bytestring=b'<svg width="1" height="1"></svg>', output_width=1, output_height=1)
                    return True
                    
                finally:
                    # Always restore stderr
                    sys.stderr.close()
                    sys.stderr = original_stderr
                    
        except (ImportError, OSError, Exception):
            return False
    
    def _setup_cairo_environment(self):
        """Set up Cairo environment variables based on the operating system."""
        import platform
        import os
        
        system = platform.system()
        
        if system == "Darwin":  # macOS
            # Try Apple Silicon Homebrew path first
            homebrew_paths = [
                "/opt/homebrew/opt/cairo/lib",
                "/usr/local/opt/cairo/lib"  # Intel Mac
            ]
            
            for cairo_path in homebrew_paths:
                if os.path.exists(cairo_path):
                    # Set environment variables for current process
                    current_dyld = os.environ.get('DYLD_LIBRARY_PATH', '')
                    if cairo_path not in current_dyld:
                        os.environ['DYLD_LIBRARY_PATH'] = f"{cairo_path}:{current_dyld}"
                    
                    pkg_config_path = f"{cairo_path.replace('/lib', '/lib/pkgconfig')}"
                    current_pkg = os.environ.get('PKG_CONFIG_PATH', '')
                    if pkg_config_path not in current_pkg:
                        os.environ['PKG_CONFIG_PATH'] = f"{pkg_config_path}:{current_pkg}"
                    break
                    
        elif system == "Linux":
            # Linux systems - ensure standard paths are in PKG_CONFIG_PATH
            standard_paths = [
                "/usr/lib/pkgconfig",
                "/usr/lib/x86_64-linux-gnu/pkgconfig",
                "/usr/lib64/pkgconfig",
                "/usr/share/pkgconfig"
            ]
            
            current_pkg = os.environ.get('PKG_CONFIG_PATH', '')
            for path in standard_paths:
                if os.path.exists(path) and path not in current_pkg:
                    os.environ['PKG_CONFIG_PATH'] = f"{path}:{current_pkg}"
    
    def get_svg_installation_instructions(self) -> str:
        """Get platform-specific instructions for installing SVG support.
        
        Returns:
            String with installation instructions
        """
        import platform
        system = platform.system()
        
        if system == "Darwin":  # macOS
            return """To enable high-quality SVG weather symbols on macOS:

🍺 Using Homebrew (Recommended):
1. Install Cairo library: brew install cairo
2. Install Python packages: pip install cairosvg pillow
3. Run the setup script: ./setup_svg_rendering.sh

If you don't have Homebrew, install it from: https://brew.sh/

🔧 Manual Setup:
Add to your ~/.zshrc or ~/.bashrc:
export DYLD_LIBRARY_PATH="/opt/homebrew/opt/cairo/lib:$DYLD_LIBRARY_PATH"
export PKG_CONFIG_PATH="/opt/homebrew/opt/cairo/lib/pkgconfig:$PKG_CONFIG_PATH"

(Use /usr/local/opt/cairo/lib for Intel Macs)"""
        
        elif system == "Linux":
            return """To enable high-quality SVG weather symbols on Linux:

📦 Install Cairo development libraries:
• Ubuntu/Debian: sudo apt-get install libcairo2-dev pkg-config python3-dev
• CentOS/RHEL: sudo yum install cairo-devel pkgconfig python3-devel  
• Fedora: sudo dnf install cairo-devel pkgconfig python3-devel
• Arch Linux: sudo pacman -S cairo pkgconf python

🐍 Install Python packages:
pip install cairosvg pillow

🚀 Quick Setup:
Run the setup script: ./setup_svg_rendering.sh

🔧 Manual Setup (if needed):
Add to your ~/.bashrc:
export PKG_CONFIG_PATH="/usr/lib/pkgconfig:/usr/lib/x86_64-linux-gnu/pkgconfig:$PKG_CONFIG_PATH" """
        
        elif system == "Windows":
            return """To enable high-quality SVG weather symbols on Windows:

⚠️  Windows installation is complex. Consider using WSL2 with Ubuntu instead.

🪟 Native Windows:
1. Install Cairo from: https://cairographics.org/download/
2. Install Python packages: pip install cairosvg pillow
3. May require additional Visual C++ build tools

🐧 WSL2 Alternative (Recommended):
1. Install WSL2 with Ubuntu
2. Follow Ubuntu installation instructions
3. Run: ./setup_svg_rendering.sh

💡 Note: The fallback transparent markers work excellently without Cairo."""
        
        else:
            return """To enable high-quality SVG weather symbols:

🔧 General Instructions:
1. Install Cairo development libraries for your system
2. Install Python packages: pip install cairosvg pillow
3. Run the setup script: ./setup_svg_rendering.sh

📚 System-specific commands:
• macOS: brew install cairo
• Ubuntu/Debian: sudo apt-get install libcairo2-dev pkg-config python3-dev
• CentOS/RHEL: sudo yum install cairo-devel pkgconfig python3-devel
• Fedora: sudo dnf install cairo-devel pkgconfig python3-devel"""
    
    def _get_svg_icon_path(self, symbol_code) -> Optional[Path]:
        """Get the path to an SVG icon file.
        
        Args:
            symbol_code: Weather symbol code (int or str)
            
        Returns:
            Path to SVG file or None if not found
        """
        if not symbol_code:
            return None
        
        # Convert to string if it's an integer
        symbol_code = str(symbol_code)
        
        # Clean symbol code (remove any _d or _n suffixes for day/night variants)
        base_symbol = symbol_code.replace('_d', '').replace('_n', '')
        
        # Try exact match first
        svg_path = self.icon_cache_dir / f"{symbol_code}.svg"
        if svg_path.exists():
            return svg_path
        
        # Try base symbol without day/night suffix
        svg_path = self.icon_cache_dir / f"{base_symbol}.svg"
        if svg_path.exists():
            return svg_path
        
        # Try common variations
        variations = [
            f"{symbol_code}_day.svg",
            f"{symbol_code}_night.svg",
            f"{base_symbol}_day.svg",
            f"{base_symbol}_night.svg"
        ]
        
        for variation in variations:
            svg_path = self.icon_cache_dir / variation
            if svg_path.exists():
                return svg_path
        
        return None
    
    
    def _add_svg_icon(self, ax: Axes, x_position, y_position: float, svg_path: Path) -> None:
        """Add an SVG icon to the plot with transparent background.
        
        This method ONLY renders SVG icons - no fallback markers.
        If SVG rendering fails, the symbol is simply skipped.
        
        Args:
            ax: matplotlib Axes object
            x_position: X position (index)
            y_position: Y position
            svg_path: Path to SVG file
        """
        try:
            from matplotlib.offsetbox import OffsetImage, AnnotationBbox
            import cairosvg
            import io
            from PIL import Image
            
            # Convert SVG to PNG with transparent background
            png_data = cairosvg.svg2png(
                url=str(svg_path),
                output_width=int(self.config.symbol_size * 4),  # High resolution
                output_height=int(self.config.symbol_size * 4),
                background_color='transparent'
            )
            
            # Load PNG data as image
            image = Image.open(io.BytesIO(png_data))
            
            # Create OffsetImage and AnnotationBbox for proper positioning
            imagebox = OffsetImage(image, zoom=0.25)  # Scale down from high-res
            ab = AnnotationBbox(
                imagebox, 
                (x_position, y_position),
                frameon=False,  # No frame
                pad=0,
                xycoords='data'
            )
            ax.add_artist(ab)
            
            logger.debug("Rendered SVG icon with transparency: %s", svg_path.name)
            
        except ImportError as e:
            logger.error("SVG rendering dependencies not available: %s", e)
            logger.error("Install with: pip install cairosvg pillow")
            raise RuntimeError("SVG rendering requires cairosvg and pillow packages")
            
        except Exception as e:
            logger.error("Failed to render SVG icon %s: %s", svg_path.name, e)
            raise RuntimeError(f"SVG rendering failed for {svg_path.name}: {e}")
    
    def _ensure_icons_available(self) -> None:
        """Ensure essential weather icons are available locally."""
        essential_icons = [
            'clearsky_day.svg', 'clearsky_night.svg', 'fair_day.svg', 'fair_night.svg',
            'partlycloudy_day.svg', 'partlycloudy_night.svg', 'cloudy.svg',
            'lightrain.svg', 'rain.svg', 'heavyrain.svg',
            'lightsnow.svg', 'snow.svg', 'heavysnow.svg',
            'fog.svg', 'rainshowers_day.svg', 'snowshowers_day.svg'
        ]
        
        missing_icons = []
        for icon in essential_icons:
            icon_path = self.icon_cache_dir / icon
            if not icon_path.exists():
                missing_icons.append(icon)
        
        if missing_icons:
            logger.info(f"Downloading {len(missing_icons)} essential Met.no weather icons...")
            for icon in missing_icons:
                self.download_svg_icon(icon)
    
    def add_symbols_to_plot(
        self,
        ax: Axes,
        data: pd.DataFrame,
        y_position: Optional[float] = None,
        symbol_type: Optional[SymbolType] = None,
    ) -> int:
        """Add weather symbols to a plot.
        
        Args:
            ax: matplotlib Axes object
            data: DataFrame with 'weather_symbol' column
            y_position: Y position for symbols
            symbol_type: Type of symbols to use
            
        Returns:
            Number of symbols added
        """
        if 'weather_symbol' not in data.columns:
            logger.warning("No weather symbol data available")
            return 0
        
        # Filter out NaN values
        symbol_data = data['weather_symbol'].dropna()
        
        if symbol_data.empty:
            logger.warning("No valid weather symbols found")
            return 0
        
        # Use configured symbol type or default (now auto-detected)
        if symbol_type is None:
            symbol_type = self.config.symbol_type
        
        logger.debug("Using symbol type: %s", symbol_type)
        
        # Determine y position for symbols
        if y_position is None:
            y_min, y_max = ax.get_ylim()
            y_position = y_max - (y_max - y_min) * 0.15  # 15% from top for better visibility
        
        # Sample symbols to avoid overcrowding
        n_symbols = len(symbol_data)
        if n_symbols > 50:  # Increased threshold to avoid sampling for typical meteogram data
            step = max(1, n_symbols // 20)
            symbol_data = symbol_data.iloc[::step]
            logger.debug("Sampled %d symbols from %d (step=%d)", len(symbol_data), n_symbols, step)
        else:
            logger.debug("No sampling needed for %d symbols", n_symbols)
        
        # Add symbols with proper handling - SVG only
        symbols_added = 0
        
        # Check SVG rendering capability before processing any symbols
        if not self.has_high_quality_svg_support():
            logger.error("SVG rendering not available - cannot display weather symbols")
            logger.error("Install SVG support with: pip install cairosvg pillow")
            logger.error("Or run the setup script: ./setup_svg_rendering.sh")
            return 0
        
        # Use proper time-based positioning to align with grid
        for idx, symbol_code in symbol_data.items():
            symbol_info = self.get_symbol_info(symbol_code)
            
            if not symbol_info:
                logger.warning("No symbol info found for code: %s", symbol_code)
                continue
            
            # Get the actual position in the data array (time index)
            time_position = symbol_data.index.get_loc(idx)
            logger.debug("Rendering SVG symbol at time position %d: code=%s", time_position, symbol_code)
            
            # Always use SVG icons - no fallbacks
            svg_path = self._get_svg_icon_path(symbol_code)
            logger.debug("SVG mode: symbol_code=%s, svg_path=%s", symbol_code, svg_path)
            
            if svg_path and svg_path.exists():
                try:
                    logger.debug("Using SVG icon: %s", svg_path)
                    self._add_svg_icon(ax, time_position, y_position, svg_path)
                    symbols_added += 1
                except Exception as e:
                    logger.error("Failed to render SVG icon %s: %s", svg_path.name, e)
                    # Skip this symbol - no fallback markers
                    continue
            else:
                # Try to download SVG if not available and auto-download is enabled
                if self.config.auto_download_icons and symbol_info.get('svg'):
                    try:
                        downloaded_path = self.download_svg_icon(symbol_info['svg'])
                        if downloaded_path and downloaded_path.exists():
                            logger.debug("Downloaded and using SVG icon: %s", downloaded_path)
                            self._add_svg_icon(ax, time_position, y_position, downloaded_path)
                            symbols_added += 1
                        else:
                            logger.warning("Failed to download SVG for %s - symbol skipped", symbol_code)
                    except Exception as e:
                        logger.error("Failed to download/render SVG for %s: %s", symbol_code, e)
                        continue
                else:
                    logger.warning("SVG not found for %s and auto-download disabled - symbol skipped", symbol_code)
        
        logger.info(f"Added {symbols_added} weather symbols to plot")
        return symbols_added
    
    def get_symbol_info(self, symbol_code) -> Optional[Dict[str, Any]]:
        """Get symbol information for a weather code.
        
        Args:
            symbol_code: Weather symbol code from Met.no (int or str)
            
        Returns:
            Dictionary with symbol information or None if not found
        """
        # Handle both integer and string codes
        if isinstance(symbol_code, (int, float)):
            # Map integer codes to descriptive keys (simplified WMO codes)
            int_code = int(symbol_code)
            code_mapping = {
                1: 'clearsky_day',
                2: 'fair_day', 
                3: 'partlycloudy_day',
                4: 'cloudy',
                9: 'lightrain',
                10: 'rain',
                12: 'lightsnow',
                13: 'snow'
            }
            clean_code = code_mapping.get(int_code, 'clearsky_day')  # Default to clear sky
        else:
            clean_code = str(symbol_code).lower().strip()
        
        # Try exact match first
        if clean_code in self.symbol_mapping:
            return self.symbol_mapping[clean_code]
        
        # Try partial matches for codes with variants
        for code, info in self.symbol_mapping.items():
            if clean_code.startswith(code.split('_')[0]):
                return info
        
        # Default fallback
        logger.debug(f"Unknown Met.no weather symbol code: {symbol_code}")
        return {
            'svg': None,
            'color': '#000000', 'description': f'Unknown ({symbol_code})'
        }
    
    def get_supported_symbols(self) -> List[str]:
        """Get list of supported weather symbol codes.
        
        Returns:
            List of supported Met.no symbol codes
        """
        return list(self.symbol_mapping.keys())
    
    def download_svg_icon(self, svg_filename: str) -> Optional[Path]:
        """Download SVG icon from Met.no repository.
        
        Args:
            svg_filename: Name of the SVG icon file
            
        Returns:
            Path to downloaded icon or None if failed
        """
        if not svg_filename:
            return None
        
        # Set up cache directory
        self.icon_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if already cached
        icon_path = self.icon_cache_dir / svg_filename
        if icon_path.exists():
            return icon_path
        
        # Download from official Met.no repository
        try:
            url = self.icon_base_url + svg_filename
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            with open(icon_path, 'wb') as f:
                f.write(response.content)
            
            logger.debug(f"Downloaded Met.no weather icon: {svg_filename}")
            return icon_path
            
        except Exception as e:
            logger.warning(f"Failed to download Met.no weather icon {svg_filename}: {e}")
            return None
    
    def download_all_icons(self) -> Dict[str, bool]:
        """Download all SVG icons from the Met.no repository.
        
        Returns:
            Dictionary mapping icon names to download success status
        """
        results = {}
        
        logger.info("Downloading all Met.no weather icons...")
        
        for symbol_code, symbol_info in self.symbol_mapping.items():
            svg_filename = symbol_info.get('svg')
            if svg_filename:
                icon_path = self.download_svg_icon(svg_filename)
                results[svg_filename] = icon_path is not None
        
        successful = sum(results.values())
        total = len(results)
        
        logger.info(f"Downloaded {successful}/{total} Met.no weather icons")
        
        return results
    
    def get_icon_path(self, symbol_code: str) -> Optional[Path]:
        """Get local path to SVG icon for a symbol code.
        
        Args:
            symbol_code: Weather symbol code
            
        Returns:
            Path to local SVG icon or None if not available
        """
        symbol_info = self.get_symbol_info(symbol_code)
        if not symbol_info or not symbol_info.get('svg'):
            return None
        
        svg_filename = symbol_info['svg']
        icon_path = self.icon_cache_dir / svg_filename
        
        if not icon_path.exists():
            # Try to download it
            return self.download_svg_icon(svg_filename)
        
        return icon_path
    
    def get_symbol_statistics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Get statistics about weather symbols in the data.
        
        Args:
            data: DataFrame with weather symbol data
            
        Returns:
            Dictionary with symbol statistics
        """
        if 'weather_symbol' not in data.columns:
            return {'total_symbols': 0, 'unique_symbols': 0, 'symbol_counts': {}}
        
        symbol_data = data['weather_symbol'].dropna()
        
        if symbol_data.empty:
            return {'total_symbols': 0, 'unique_symbols': 0, 'symbol_counts': {}}
        
        # Count occurrences
        symbol_counts = symbol_data.value_counts().to_dict()
        
        # Get descriptions
        symbol_descriptions = {}
        for code, count in symbol_counts.items():
            symbol_info = self.get_symbol_info(code)
            description = symbol_info['description'] if symbol_info else f'Unknown ({code})'
            symbol_descriptions[description] = count
        
        return {
            'total_symbols': len(symbol_data),
            'unique_symbols': len(symbol_counts),
            'symbol_counts': symbol_descriptions,
            'most_common': max(symbol_descriptions.items(), key=lambda x: x[1]) if symbol_descriptions else None,
            'metno_codes': symbol_counts,
        }
