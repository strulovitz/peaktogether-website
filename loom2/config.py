"""
LOOM2 -- config.py
FROZEN CONSTANTS. Single source of truth. No module may redefine these.
Imports: none (pure data). Every child chat receives this file.
"""

# ---------- audio ----------
SAMPLE_RATE   = 44100
BLOCK_SIZE    = 1024         # reverted 4096->1024 (Fable Run 2, 2026-07-08): the
                             # screech was cured by pacing the main loop (vsync=False
                             # + 60fps cap + GIL yield in main.py), NOT by buffer size,
                             # so we keep the snappy ~23ms response. latency='high'
                             # stays in engine._open_stream for extra safety margin.
MEASURE_SEC   = 2.0            # fixed: 120 BPM, four beats (SUTRAS/VEDAS)
F0_HZ         = 440.0          # A4 at z = 0 (origin-centered helix)
Z_PER_OCTAVE  = 2.0            # world height units per octave (per-scene override allowed)
RING_WIDTH    = 0.8            # world units per rhythm ring
NMAX_RING     = 5              # fastest ring: 5 pulses / measure
HEARING_R     = 2.5            # default hearing radius (world units)
PENTA_CLASSES = ("A", "B", "Cs", "E", "Fs")   # A-major pentatonic
OUTPUT_MODES  = ("stereo", "surround_5_1", "surround_7_1")  # user-toggleable

# ---------- the orchestra (SUTRAS Part 1; DeepSeek library 2026-07-07) ----------
FAMILY_ANGLE_DEG = {"brass": 90.0, "woodwinds": 210.0, "strings": 330.0}

# family -> ordered low-to-high list of (instrument, tuple_of_owned_notes)
REGISTER_MAP = {
  "strings": (
    ("double_bass", ("E1","Fs1","A1","B1","Cs2","E2","Fs2")),
    ("cello",       ("A2","B2","Cs3","E3","Fs3")),
    ("viola",       ("A3","B3","Cs4","E4","Fs4")),
    ("violin",      ("A4","B4","Cs5","E5","Fs5","A5","B5","Cs6","E6","Fs6",
                     "A6","B6","Cs7","E7","Fs7","A7")),
  ),
  "woodwinds": (
    ("contrabassoon",("B0","Cs1","E1","Fs1","A1","B1","Cs2","E2","Fs2")),
    ("bassoon",      ("A2","B2","Cs3","E3","Fs3")),
    ("clarinet",     ("A3","B3","Cs4","E4","Fs4")),
    ("oboe",         ("A4","B4","Cs5","E5","Fs5")),
    ("flute",        ("A5","B5","Cs6","E6","Fs6","A6","B6")),
  ),
  "brass": (
    ("tuba",        ("E1","Fs1","A1","B1","Cs2","E2","Fs2")),
    ("trombone",    ("A2","B2","Cs3","E3","Fs3")),
    ("french_horn", ("A3","B3","Cs4","E4","Fs4")),
    ("trumpet",     ("A4","B4","Cs5","E5","Fs5","A5","B5","Cs6")),
  ),
}
# Full-range rule: notes outside a family's total span soft-clamp to its
# lowest/highest owned note (SUTRAS 1.3). Never resample across registers.

# ---------- screen (SUTRAS Part 2: equal respect 50/50) ----------
# LAYOUT OVERHAUL (Nir, 2026-07-08): TWO regions only -- NO dedicated text strip.
# Graphics 80% (the two 50/50 panels) + quiz bar 20%. Scenario text, the equation,
# and the panel titles are PAINTED ON TOP of the graphics by the HUD (see HUD block).
WINDOW_W, WINDOW_H = 1280, 720
TOP_STRIP_FRAC   = 0.0         # RETIRED (was 0.08): no strip; text is painted over graphics
PANELS_FRAC      = 0.80        # upper area = 80% (576 px): terrain left 50%, helix right 50%
QUIZ_BAR_FRAC    = 0.20        # bottom quiz bar (144 px)
PANEL_TITLE_LEFT  = "CARTESIAN COORDINATES"
PANEL_TITLE_RIGHT = "SONIFIQUATION COORDINATES"   # Nir's word. It stays.

# ---------- HUD (Nir's overhaul 2026-07-08; drawn Homeworld-style moderngl overlay, NOT pyglet) ----------
# Text is painted ON TOP of the graphics (no background box). Every glyph gets a thin
# BLACK stroke/outline hugging its shape so it stays readable over any landscape.
# Emojis are allowed inline (baked from the Windows "Segoe UI Emoji" font into the atlas).
HUD_MAX_TEXT_LINES = 3         # scenario text: up to 3 lines across the top of the graphics
HUD_TEXT_PX        = 20        # glyph size; ~24 px line pitch (2 px above + 2 px below)
HUD_LINE_PITCH_PX  = 24
HUD_TITLE_PX       = 14        # panel titles: smaller, at the bottom of each panel
# colors RGB 0-255 (Nir's palette; bright + outlined; tweak freely):
HUD_OUTLINE_RGB  = (0, 0, 0)          # the stroke around every glyph
HUD_TEXT_RGB     = (255, 255, 255)    # scenario lines: white
HUD_EQUATION_RGB = (255, 218, 40)     # equation: yellow (centered, bottom of graphics, over the seam)
HUD_TITLE_RGB    = (255, 255, 255)    # panel titles: white
HUD_WRONG_RGB    = (255, 45, 150)     # wrong-answer text: bright pink (never red)
HUD_HINT_RGB     = (60, 240, 90)      # hint text: bright green
HUD_WIN_RGB      = (120, 205, 255)    # "YOU WIN!!!" big, centered, blinking -- light blue
HUD_EQUATION_MAX_H_PX = 88           # max display height for equation PNG (pixels)

# ---------- camera ----------
CAM_ELEV_MIN_DEG = 5.0
CAM_ELEV_MAX_DEG = 85.0        # "forbidden top" rounded (SUTRAS 3.5)
CAM_DEFAULT      = {"azimuth_deg": 0.0, "elevation_deg": 35.0, "zoom": 1.0}

# ---------- hypsometric colors (RGB 0-255) ----------
COLOR_DEEP_WATER=(20,60,140); COLOR_SHALLOW=(50,140,230)
COLOR_LOWLAND=(70,160,80);    COLOR_UPLAND=(150,110,70)
COLOR_PEAK=(232,232,238)

# ---------- paths ----------
DATA_DIR="data"; SAMPLES_DIR="data/samples"; SCENES_DIR="data/scenes"
ICONS_DIR="data/icons"; SHADERS_DIR="data/shaders"
MANIFEST_PATH="data/samples/manifest.json"

# ---------- quiz ----------
OPTION_WAV_SECONDS = 4.0       # exactly 2 measures, loopable, stereo 16-bit
