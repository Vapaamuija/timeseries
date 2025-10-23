"""
SVG rendering functionality for weather symbols.

This module handles the SVG-specific rendering logic, including Cairo setup,
environment configuration, and SVG-to-PNG conversion for matplotlib.
"""

import logging
import os
import platform
import sys
import warnings
from pathlib import Path
from typing import Optional

import numpy as np
from matplotlib.axes import Axes
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

logger = logging.getLogger(__name__)


class SVGRenderer:
    """Handles SVG rendering for weather symbols."""

    def __init__(self, symbol_size: int = 20) -> None:
        """Initialize SVG renderer.

        Args:
            symbol_size: Size of symbols in pixels
        """
        self.symbol_size = symbol_size

    def has_high_quality_svg_support(self) -> bool:
        """Check if high-quality SVG rendering is available.

        Returns:
            True if cairosvg and PIL are available for true SVG rendering
        """
        try:
            # Set up environment variables for Cairo detection based on OS
            self._setup_cairo_environment()

            import cairosvg  # type: ignore
            from PIL import Image

            # Suppress verbose Cairo error messages
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                # Temporarily redirect stderr to suppress Cairo library errors
                original_stderr = sys.stderr
                try:
                    # Redirect stderr to devnull to suppress Cairo errors
                    sys.stderr = open(os.devnull, "w")

                    # Test if cairosvg actually works by trying a simple conversion
                    cairosvg.svg2png(
                        bytestring=b'<svg width="1" height="1"></svg>',
                        output_width=1,
                        output_height=1,
                    )
                    return True

                finally:
                    # Always restore stderr
                    sys.stderr.close()
                    sys.stderr = original_stderr

        except (ImportError, OSError, Exception):
            return False

    def _setup_cairo_environment(self) -> None:
        """Set up Cairo environment variables based on the operating system."""
        system = platform.system()

        if system == "Darwin":  # macOS
            # Try Apple Silicon Homebrew path first
            homebrew_paths = [
                "/opt/homebrew/opt/cairo/lib",
                "/usr/local/opt/cairo/lib",  # Intel Mac
            ]

            for cairo_path in homebrew_paths:
                if os.path.exists(cairo_path):
                    # Set environment variables for current process
                    current_dyld = os.environ.get("DYLD_LIBRARY_PATH", "")
                    if cairo_path not in current_dyld:
                        os.environ["DYLD_LIBRARY_PATH"] = f"{cairo_path}:{current_dyld}"

                    pkg_config_path = f"{cairo_path.replace('/lib', '/lib/pkgconfig')}"
                    current_pkg = os.environ.get("PKG_CONFIG_PATH", "")
                    if pkg_config_path not in current_pkg:
                        os.environ["PKG_CONFIG_PATH"] = (
                            f"{pkg_config_path}:{current_pkg}"
                        )
                    break

        elif system == "Linux":
            # Linux systems - ensure standard paths are in PKG_CONFIG_PATH
            standard_paths = [
                "/usr/lib/pkgconfig",
                "/usr/lib/x86_64-linux-gnu/pkgconfig",
                "/usr/lib64/pkgconfig",
                "/usr/share/pkgconfig",
            ]

            current_pkg = os.environ.get("PKG_CONFIG_PATH", "")
            for path in standard_paths:
                if os.path.exists(path) and path not in current_pkg:
                    os.environ["PKG_CONFIG_PATH"] = f"{path}:{current_pkg}"

    def get_svg_installation_instructions(self) -> str:
        """Get platform-specific instructions for installing SVG support.

        Returns:
            String with installation instructions
        """
        system = platform.system()

        if system == "Darwin":  # macOS
            return """To enable high-quality SVG weather symbols on macOS:

🍺 Using Homebrew (Recommended):
1. Install Cairo library: brew install cairo
2. Install Python packages: pip install cairosvg pillow
3. Run the setup script: ./bin/setup_svg_rendering.sh

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
Run the setup script: ./bin/setup_svg_rendering.sh

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
3. Run: ./bin/setup_svg_rendering.sh

💡 Note: The fallback transparent markers work excellently without Cairo."""

        else:
            return """To enable high-quality SVG weather symbols:

🔧 General Instructions:
1. Install Cairo development libraries for your system
2. Install Python packages: pip install cairosvg pillow
3. Run the setup script: ./bin/setup_svg_rendering.sh

📚 System-specific commands:
• macOS: brew install cairo
• Ubuntu/Debian: sudo apt-get install libcairo2-dev pkg-config python3-dev
• CentOS/RHEL: sudo yum install cairo-devel pkgconfig python3-devel
• Fedora: sudo dnf install cairo-devel pkgconfig python3-devel"""

    def render_svg_icon(
        self, ax: Axes, x_position: float, y_position: float, svg_path: Path
    ) -> None:
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
            import io

            import cairosvg
            from PIL import Image

            # Convert SVG to PNG with transparent background
            png_data = cairosvg.svg2png(
                url=str(svg_path),
                output_width=int(self.symbol_size * 4),  # High resolution
                output_height=int(self.symbol_size * 4),
                background_color="transparent",
            )

            # Load PNG data as image
            image = Image.open(io.BytesIO(png_data))

            # Convert PIL Image to numpy array for OffsetImage
            image_array = np.array(image)

            # Create OffsetImage and AnnotationBbox for proper positioning
            imagebox = OffsetImage(image_array, zoom=0.25)  # Scale down from high-res
            ab = AnnotationBbox(
                imagebox,
                (x_position, y_position),
                frameon=False,  # No frame
                pad=0,
                xycoords="data",
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
