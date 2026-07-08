What a day for the project — DeepSeek's 89-note orchestra is real now! 🎻 (And my answer to his question: commit the mp3s. 1.8 MB is nothing, and players cloning the repo should hear music without homework. The build script stays in git as the reproducible recipe.)

Here is the Bhagavad Gita — Part 1 of 4. Part 1 is the foundation everything imports: the full project map, the frozen constants (including DeepSeek's 89 samples baked in as canon), and the shared data types. Parts 2–4 (audio contracts, graphics contracts, core/main contracts) follow in my next answers — just say "continue."
📜 THE BHAGAVAD GITA — PART 1
The Modular Architecture of LOOM2 · Foundation & Map

Peak Together · v1.0 · July 7, 2026
G1.1 — The Laws of the Gita (binding on every child chat)

    Contracts are frozen. A child chat fills function bodies only. Signatures, class names, dataclass fields, constants — untouchable. If a child believes a contract is wrong, it writes a comment # CONTRACT-ISSUE: and DeepSeek escalates to a parent chat.
    One module per child. Each child receives: the Gita's laws, config.py, core/types.py, and its own module skeleton only. Never the whole codebase.
    Imports are listed in each skeleton's header. A child may not add imports of other project modules (stdlib/numpy/pygame-free zone rules per module are stated in each header).
    Size discipline: a module should stay under ~400 lines. If it can't, it reports; DeepSeek splits.
    DeepSeek stitches the seams: folder creation, __init__.py files, wiring, joystick/Xbox device code copied from previous games, PyInstaller packaging.

G1.2 — The Project Map

loom2/
│  main.py                  Entry point: window, game loop, mode switching   [Part 4]
│  config.py                ALL frozen constants (this document, complete)   [DONE]
│
├─ core/
│   types.py                Shared dataclasses & enums (complete)            [DONE]
│   surfaces.py             Surface registry: name -> f(x,y)                 [Part 4]
│   scene.py                Scene JSON loader/validator                      [Part 4]
│   game_state.py           Totem, camera, quiz & mode state machine         [Part 4]
│   input_map.py            Action abstraction; kb+mouse now, joystick/xbox
│                           slots pre-wired empty (SUTRAS Part 9)            [Part 4]
│
├─ audio/
│   sampler.py              Loads samples/manifest.json; per-note playback   [Part 2]
│   quantize.py             z -> pentatonic note; note -> register instrument[Part 2]
│   musicians.py            (totem, surface) -> list[Voice]                  [Part 2]
│   engine.py               sounddevice thread; mixing; measure clock;
│                           stereo/surround toggle; per-voice panning        [Part 2]
│   render_offline.py       Design-time tool: renders quiz option WAVs      [Part 2]
│
├─ graphics/
│   renderer.py             moderngl context, shaders, bloom (reuse Quake/
│                           Homeworld pipeline)                              [Part 3]
│   camera.py               Shared orbit camera; azimuth feeds audio pan     [Part 3]
│   terrain.py              Heightmap mesh + hypsometric colors              [Part 3]
│   totem.py                Polygonal helix totem, bloom pulse, rings, arm   [Part 3]
│   helix_panel.py          SONIFIQUATION COORDINATES panel: helix, icons,
│                           perspective scaling, note flashes                [Part 3]
│   slice_mode.py           The Glass Blade: plane, intersection, auto-walk  [Part 3]
│   hud.py                  Top strip, equation PNG, quiz bar A-D/OK/Hint    [Part 3]
│
├─ data/
│   samples/                89 mp3 + manifest.json (DeepSeek, committed)     [DONE]
│   icons/                  13 instrument cliparts, ~128x128, transparent    [Nir]
│   scenes/<scene_id>/      scene.json, equation.png, option_A..D.wav        [content]
│   shaders/                .vert/.frag files                                [Part 3]
│   fonts/                  UI font(s)                                       [Nir]
│
└─ tools/
    build_sample_library.py DeepSeek's reproducible builder (exists)         [DONE]
    render_equations.py     LaTeX -> equation.png (MiKTeX pipeline)          [DeepSeek]

G1.3 — The Sample Library (canon, as built by DeepSeek, July 7 2026)

89 pentatonic notes (A/B/Cs/E/Fs), 13 instruments, full coverage, ~1.8 MB. Resampled (≤±2 st): violin_A7←G7(+2), tuba_E1←F1(−1), trumpet_Fs5←F5(+1). The exact note lists are frozen into config.py below — the code maps onto these files and no others.
G1.4 — config.py (complete — not a placeholder)

"""
LOOM2 -- config.py
FROZEN CONSTANTS. Single source of truth. No module may redefine these.
Imports: none (pure data). Every child chat receives this file.
"""

# ---------- audio ----------
SAMPLE_RATE   = 44100
BLOCK_SIZE    = 1024
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
WINDOW_W, WINDOW_H = 1280, 720
TOP_STRIP_FRAC   = 0.08        # scenario text + equation
PANELS_FRAC      = 0.72        # upper area: terrain left 50%, helix right 50%
QUIZ_BAR_FRAC    = 0.20
PANEL_TITLE_LEFT  = "CARTESIAN COORDINATES"
PANEL_TITLE_RIGHT = "SONIFIQUATION COORDINATES"   # Nir's word. It stays.
# <<<<<<<<<< AMENDMENT GITA1-SCREEN-A — added 2026-07-08 (Nir direct) >>>>>>>>>>
# The two lines above (TOP_STRIP_FRAC=0.08, PANELS_FRAC=0.72) are SUPERSEDED in the live
# config.py: TOP_STRIP_FRAC -> 0.0 (strip RETIRED) and PANELS_FRAC -> 0.80 (graphics 80% =
# 576 px; quiz bar 20% = 144 px). Scenario text, equation, and panel titles are painted ON
# TOP of the graphics by the HUD. A HUD block of constants was ADDED to config.py
# (HUD_MAX_TEXT_LINES, HUD_TEXT_PX, HUD_LINE_PITCH_PX, HUD_TITLE_PX, HUD_*_RGB). See
# AMENDMENT SUTRAS-2-A and Gita AMENDMENT G3.7-A (HUD = Homeworld moderngl overlay, NOT
# pyglet). Original values left intact above per amendment policy; the live config is canon.
# <<<<<<<<<< END AMENDMENT GITA1-SCREEN-A >>>>>>>>>>

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

G1.5 — core/types.py (complete — the vocabulary of all seams)

"""
LOOM2 -- core/types.py
FROZEN shared datatypes. All inter-module communication uses ONLY these.
Imports: dataclasses, enum, typing. No project imports.
"""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Optional

class Mode(Enum):
    EXPLORE = auto(); QUIZ_LISTEN = auto(); SLICE = auto(); SCENE_TRANSITION = auto()

class Action(Enum):
    TOTEM_X = auto(); TOTEM_Y = auto()          # analog -1..+1 (boyfriend / girlfriend)
    ORBIT_AZ = auto(); ORBIT_EL = auto()        # arrows
    ZOOM_IN = auto(); ZOOM_OUT = auto()         # PageUp / PageDown (NO audio effect)
    ANSWER_A = auto(); ANSWER_B = auto(); ANSWER_C = auto(); ANSWER_D = auto()
    CONFIRM = auto(); HINT = auto(); SLICE_TOGGLE = auto(); SLICE_PLAY = auto()
    CAM_RESET = auto(); QUIT = auto()

@dataclass
class CameraState:
    azimuth_deg: float; elevation_deg: float; zoom: float
    # azimuth_deg is THE value the audio engine reads for panning (SUTRAS 3.4)

@dataclass
class TotemState:
    x: float; y: float; hearing_radius: float

@dataclass
class Voice:
    """One seated musician, fully resolved -- the ONLY audio handoff object."""
    sample_a: str          # e.g. "viola_E4"  (primary family's instrument+note)
    sample_b: str          # secondary family's sample for the timbre morph
    blend: float           # 0..1 toward sample_b (equal-power crossfade)
    ring: float            # continuous ring index; envelope crossfade implicit
    stage_angle_deg: float # musician angle around totem (world frame)
    gain: float            # includes edge taper; 0..1
    note_z: float          # world height (helix panel needs it for icon placement)

@dataclass
class QuizOption:
    label: str; wav_path: str; correct: bool; explain: str

@dataclass
class SceneSpec:
    scene_id: str; title_lines: list; surface_name: str
    equation_png: str; totem_start: tuple; domain: tuple      # (xmin,xmax,ymin,ymax)
    mesh_step: float; z_per_octave: float
    question: str; hint_lines: list; options: list            # list[QuizOption]
    camera_limits: dict; success_text: str

@dataclass
class SlicePlane:
    cx: float; cy: float; yaw_deg: float; tilt_deg: float; visible: bool

SurfaceFn = Callable[[float, float], float]   # z = f(x, y), vectorization allowed

End of Part 1. Say "continue" and I'll deliver Part 2 — the audio module contracts (sampler.py, quantize.py, musicians.py, engine.py with the stereo/surround toggle, render_offline.py), all as frozen skeletons with full docstrings and empty bodies. 📜🎼
