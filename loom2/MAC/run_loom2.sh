#!/usr/bin/env bash
# ============================================================
#  LOOM2 -- Sonifiquation : Mac / Linux launcher
#  Double-click, or run from Terminal:
#      chmod +x run_loom2.sh
#      ./run_loom2.sh
# ============================================================
set -euo pipefail

# cd to the loom2/ directory (one level up from MAC/)
cd "$(dirname "$0")/.."

echo "🎵 Launching LOOM2 -- Sonifiquation ..."
echo "(Close the game window, or press Esc, to quit.)"
echo ""

# Find Python: try python3 first (Mac standard), then python
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON="$cmd"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "❌ ERROR: Python 3 not found. Please install Python 3.10+ from https://python.org"
    echo "   Then install dependencies with: pip3 install -r requirements-runtime.txt"
    exit 1
fi

echo "🐍 Using: $($PYTHON --version)"

# Check if dependencies are installed; if not, guide the user
$PYTHON -c "import moderngl, pyglet, numpy, PIL, sounddevice, miniaudio" 2>/dev/null || {
    echo ""
    echo "⚠️  Some dependencies are missing. Install them with:"
    echo "   $PYTHON -m pip install -r requirements-runtime.txt"
    echo ""
    read -r -p "Install now? [Y/n] " answer
    if [ "$answer" != "n" ] && [ "$answer" != "N" ]; then
        $PYTHON -m pip install -r requirements-runtime.txt
    else
        echo "Install manually and re-run. Exiting."
        exit 1
    fi
}

# Launch the game (unbuffered so you see prints LIVE)
$PYTHON -u main.py

echo ""
echo "============================================================"
echo "🎵 LOOM2 has exited. Read any message above."
echo "============================================================"
