🎵 LOOM2 -- Sonifiquation : Mac Setup Guide

Welcome, Justin! Here's how to get LOOM2 running on your Mac.

PREREQUISITES
-------------
- macOS 10.15 (Catalina) or later
- Python 3.10 or later  (download from https://python.org if needed)

QUICK START
-----------
1. Open Terminal
2. Navigate to the loom2 folder (the one containing this MAC/ folder)
3. Run the launcher:

      chmod +x MAC/run_loom2.sh
      ./MAC/run_loom2.sh

   The script will:
   - Check for Python 3
   - Offer to install dependencies (moderngl, pyglet, sounddevice, etc.)
   - Launch the game

   First launch will take a few seconds as the sampler decodes
   instrument sounds. Subsequent launches start instantly.

MANUAL SETUP (if you prefer)
----------------------------
   cd path/to/loom2
   python3 -m pip install -r requirements-runtime.txt
   python3 -u main.py

CONTROLS
--------
   Keyboard: arrow keys = orbit camera, WASD = move totem
   Mouse: drag to look around, scroll = zoom
   Gamepad: Xbox/PlayStation controllers supported
   Esc = quit

SOUND
-----
   Headphones strongly recommended for the full sonification experience!

TROUBLESHOOTING
---------------
   "no usable system TTF font found"
   → This should no longer happen (we added Helvetica fallback),
     but if it does, install the Liberation fonts:
         brew install font-liberation

   Audio glitches / crackling
   → Try increasing buffer size in your audio settings, or close
     other audio-heavy apps.

Questions? Just ask Nir! 🎵
