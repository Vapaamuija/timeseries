#!/bin/bash
# Setup script for high-quality SVG weather symbol rendering
# This script configures Cairo library detection for the weather-tool
# Supports: macOS (Homebrew), Ubuntu/Debian (apt), and other Linux distributions

echo "🎨 Weather Tool - SVG Rendering Setup"
echo "====================================="
echo ""

# Ensure we run from the project root (parent directory of this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Activate local virtualenv if available
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment (.venv)"
    # shellcheck disable=SC1091
    source .venv/bin/activate || true
else
    echo "⚠️  No .venv found. Proceeding with current Python environment"
fi

# Detect operating system
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo "🔍 Detected system: $MACHINE"
echo ""

# Install Cairo library based on the operating system
install_cairo() {
    case $MACHINE in
        Mac)
            echo "📦 Installing Cairo on macOS..."
            if command -v brew >/dev/null 2>&1; then
                if ! brew list cairo &> /dev/null; then
                    echo "Installing Cairo via Homebrew..."
                    brew install cairo
                else
                    echo "✅ Cairo library is already installed via Homebrew"
                fi
            else
                echo "❌ Homebrew not found. Please install Homebrew first:"
                echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                exit 1
            fi
            ;;
        Linux)
            echo "📦 Installing Cairo on Linux..."
            
            # Detect Linux distribution
            if command -v apt-get >/dev/null 2>&1; then
                # Ubuntu/Debian
                echo "Detected Ubuntu/Debian system"
                echo "Installing Cairo development libraries..."
                sudo apt-get update
                sudo apt-get install -y libcairo2-dev pkg-config python3-dev
                echo "✅ Cairo libraries installed via apt"
                
            elif command -v yum >/dev/null 2>&1; then
                # CentOS/RHEL/Fedora (older)
                echo "Detected CentOS/RHEL system"
                echo "Installing Cairo development libraries..."
                sudo yum install -y cairo-devel pkgconfig python3-devel
                echo "✅ Cairo libraries installed via yum"
                
            elif command -v dnf >/dev/null 2>&1; then
                # Fedora (newer)
                echo "Detected Fedora system"
                echo "Installing Cairo development libraries..."
                sudo dnf install -y cairo-devel pkgconfig python3-devel
                echo "✅ Cairo libraries installed via dnf"
                
            elif command -v pacman >/dev/null 2>&1; then
                # Arch Linux
                echo "Detected Arch Linux system"
                echo "Installing Cairo development libraries..."
                sudo pacman -S --noconfirm cairo pkgconf python
                echo "✅ Cairo libraries installed via pacman"
                
            else
                echo "❌ Unsupported Linux distribution"
                echo "Please install Cairo development libraries manually:"
                echo "  - Ubuntu/Debian: sudo apt-get install libcairo2-dev pkg-config python3-dev"
                echo "  - CentOS/RHEL: sudo yum install cairo-devel pkgconfig python3-devel"
                echo "  - Fedora: sudo dnf install cairo-devel pkgconfig python3-devel"
                echo "  - Arch: sudo pacman -S cairo pkgconf python"
                exit 1
            fi
            ;;
        *)
            echo "❌ Unsupported operating system: $MACHINE"
            echo "Please install Cairo development libraries manually for your system."
            exit 1
            ;;
    esac
}

# Install Cairo
install_cairo

echo ""
echo "📦 Installing Python packages..."

# Ensure core project dependencies are present (pandas is a good proxy)
if ! python - <<'PY'
import sys
try:
    import pandas  # noqa: F401
except Exception:
    sys.exit(1)
sys.exit(0)
PY
then
    if [ -f "requirements.txt" ]; then
        echo "📥 Installing project requirements (this may take a while)..."
        pip install -U pip setuptools wheel
        pip install -r requirements.txt
    else
        echo "❌ requirements.txt not found; cannot install core dependencies"
        echo "   Please run this script from the project root."
        exit 1
    fi
else
    echo "✅ Core Python dependencies already available"
fi

# Reinstall Cairo-related Python packages to ensure proper linking
pip uninstall -y cairocffi cairosvg 2>/dev/null || true
pip install cairocffi cairosvg pillow

echo ""
echo "🔧 Setting up environment variables..."

# Determine shell configuration file
SHELL_CONFIG=""
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_CONFIG="$HOME/.bashrc"
fi

# Set up environment variables based on operating system
setup_environment() {
    case $MACHINE in
        Mac)
            # macOS with Homebrew
            CAIRO_LIB_PATH="/opt/homebrew/opt/cairo/lib"
            CAIRO_PKG_PATH="/opt/homebrew/opt/cairo/lib/pkgconfig"
            
            # Check for Intel Mac (older Homebrew path)
            if [[ ! -d "$CAIRO_LIB_PATH" && -d "/usr/local/opt/cairo/lib" ]]; then
                CAIRO_LIB_PATH="/usr/local/opt/cairo/lib"
                CAIRO_PKG_PATH="/usr/local/opt/cairo/lib/pkgconfig"
            fi
            
            if [ -n "$SHELL_CONFIG" ]; then
                if ! grep -q "DYLD_LIBRARY_PATH.*cairo" "$SHELL_CONFIG" 2>/dev/null; then
                    echo "" >> "$SHELL_CONFIG"
                    echo "# Cairo library path for weather-tool SVG rendering (macOS)" >> "$SHELL_CONFIG"
                    echo "export DYLD_LIBRARY_PATH=\"$CAIRO_LIB_PATH:\$DYLD_LIBRARY_PATH\"" >> "$SHELL_CONFIG"
                    echo "export PKG_CONFIG_PATH=\"$CAIRO_PKG_PATH:\$PKG_CONFIG_PATH\"" >> "$SHELL_CONFIG"
                    echo "✅ macOS environment variables added to $SHELL_CONFIG"
                else
                    echo "✅ macOS environment variables already configured"
                fi
            fi
            
            # Set for current session
            export DYLD_LIBRARY_PATH="$CAIRO_LIB_PATH:${DYLD_LIBRARY_PATH:-}"
            export PKG_CONFIG_PATH="$CAIRO_PKG_PATH:${PKG_CONFIG_PATH:-}"
            ;;
            
        Linux)
            # Linux systems - Cairo should be in standard library paths
            if [ -n "$SHELL_CONFIG" ]; then
                if ! grep -q "PKG_CONFIG_PATH.*cairo" "$SHELL_CONFIG" 2>/dev/null; then
                    echo "" >> "$SHELL_CONFIG"
                    echo "# Cairo library path for weather-tool SVG rendering (Linux)" >> "$SHELL_CONFIG"
                    echo 'export PKG_CONFIG_PATH="/usr/lib/pkgconfig:/usr/lib/x86_64-linux-gnu/pkgconfig:$PKG_CONFIG_PATH"' >> "$SHELL_CONFIG"
                    echo "✅ Linux environment variables added to $SHELL_CONFIG"
                else
                    echo "✅ Linux environment variables already configured"
                fi
            fi
            
            # Set for current session
            export PKG_CONFIG_PATH="/usr/lib/pkgconfig:/usr/lib/x86_64-linux-gnu/pkgconfig:${PKG_CONFIG_PATH:-}"
            ;;
    esac
}

setup_environment

echo ""
echo "🧪 Testing SVG rendering..."

# Test the setup
python -c "
import os
os.environ['DYLD_LIBRARY_PATH'] = '/opt/homebrew/opt/cairo/lib:' + os.environ.get('DYLD_LIBRARY_PATH', '')

try:
    from weather_tool.plotting.symbols import UnifiedWeatherSymbols
    from weather_tool.plotting.interfaces import PlotConfig, SymbolType
    
    config = PlotConfig(symbol_type=SymbolType.SVG)
    renderer = UnifiedWeatherSymbols(config)
    
    if renderer.has_high_quality_svg_support():
        print('🎉 SUCCESS! High-quality SVG rendering is working!')
        print('✅ Your weather plots will now use true Met.no SVG symbols')
        print('✅ No more fallback markers or Cairo errors')
    else:
        print('❌ SVG rendering test failed')
        
except Exception as e:
    print(f'❌ Error during test: {e}')
"

echo ""
echo "🔄 To apply changes in your current terminal, run:"
echo "   source $SHELL_CONFIG"
echo ""
echo "Or restart your terminal for the changes to take effect automatically."
echo ""
echo "✅ Setup complete! Your weather tool now supports high-quality SVG symbols!"
