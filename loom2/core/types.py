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
