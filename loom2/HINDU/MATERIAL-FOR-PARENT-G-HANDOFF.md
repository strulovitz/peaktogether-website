# MATERIAL FOR THE HAND-OFF TO PARENT G

> Assembled by DeepSeek at Nir's request. This file is raw MATERIAL only — no
> instructions, no method. It contains three things Parent F may draw on when
> writing the hand-off to Parent G:
>   1. Parent G's mission, VERBATIM from the Bhagavad Gita (his three files).
>   2. The list of WHOLE Gita files Parent G needs (Nir pastes those separately).
>   3. VERBATIM public-API excerpts from the PURANAS (signatures + docstrings
>      only, bodies omitted) — the seams main.py touches. NOT whole Puranas files.

---

## 1. PARENT G'S MISSION — VERBATIM FROM THE BHAGAVAD GITA

### Assignment (Gita Part 4, G4.6 — Child-Chat Assignment Plan)

    Child G: core/surfaces.py + core/scene.py + main.py

### G4.1 — core/surfaces.py (verbatim)

```
"""
LOOM2 -- core/surfaces.py
The Surface Catalog as code. PURE MATH, vectorization-friendly (floats or
numpy arrays in, same shape out). Allowed imports: numpy, math, config.
Child chat scope: implement all bodies. ~120 lines expected.
"""

def ramp(x, y):          raise NotImplementedError   # z = 0.55x + 0.30y
def bowl(x, y):          raise NotImplementedError   # z = 0.16(x^2+y^2) - 1.0 (lake!)
def hill(x, y):          raise NotImplementedError   # z = 3.4*exp(-(x^2+y^2)/7) - 0.6
def ridge(x, y):         raise NotImplementedError   # z = 1.8 - 0.22x^2  (no y!)
def saddle(x, y):        raise NotImplementedError   # z = 0.16(x^2 - y^2)
def field(x, y):         raise NotImplementedError   # z = 0.16*x*y  (Babylon; rotated saddle)
def egg_carton(x, y):    raise NotImplementedError   # z = 1.6*sin(1.5x)*sin(1.5y)
def monkey_saddle(x, y): raise NotImplementedError   # z = 0.08(x^3 - 3x*y^2)
def cannon_range(x, y):  raise NotImplementedError   # x=v (speed), y=theta (deg);
                                                     # z = k*v^2*sin(2y_rad), scaled
                                                     # to musical range at design time

REGISTRY = {  # scene.json refers to surfaces ONLY by these names
    "ramp": ramp, "bowl": bowl, "hill": hill, "ridge": ridge,
    "saddle": saddle, "field": field, "egg_carton": egg_carton,
    "monkey_saddle": monkey_saddle, "cannon_range": cannon_range,
}

def get(name: str):
    """REGISTRY lookup with a clear error message listing valid names."""
    raise NotImplementedError
```

### G4.2 — core/scene.py (verbatim)

```
"""
LOOM2 -- core/scene.py
Scene loading & validation. Allowed imports: json, os, config, core.types,
core.surfaces. Child chat scope: implement all bodies. ~130 lines expected.
"""
from core.types import SceneSpec, QuizOption

def load_scene(scene_id: str) -> SceneSpec:
    """Read data/scenes/<scene_id>/scene.json -> SceneSpec.
    VALIDATE HARD, fail loud at load (never mid-game):
      - surface_name in surfaces.REGISTRY
      - exactly 4 options, exactly one correct
      - every option wav exists, equation.png exists
      - hint_lines: 1-3 lines; title_lines: 1-3 lines
      - totem_start inside domain; camera_limits keys present."""
    raise NotImplementedError

def campaign_order() -> list:
    """The 12 scene_ids in UPANISHADS Act order, read from
    data/scenes/campaign.json (a simple ordered list -- content, not code)."""
    raise NotImplementedError
```

### G4.5 — main.py (verbatim)

```
"""
LOOM2 -- main.py
Entry point. THIN: builds everything, runs the loop, owns NO logic.
Allowed imports: pyglet, config, all project modules.
Child chat scope: implement all bodies. ~120 lines expected.
"""

def build() -> dict:
    """Boot order (FROZEN):
      1. pyglet window (config.WINDOW_W/H)      2. Renderer(window)
      3. SampleLibrary()                        4. AudioEngine(library).start()
      5. OrbitCamera(scene limits)              6. Hud(window)
      7. GameState(engine, camera, first scene) 8. InputMap(window, hud)
      9. TerrainMesh / TotemVisual / HelixPanel / GlassBlade per scene
    Returns dict of all objects. On scene change GameState raises a
    'scene_changed' flag in snapshot(); main rebuilds TerrainMesh + hud.set_scene."""
    raise NotImplementedError

def frame(objs: dict, dt: float) -> None:
    """FROZEN FRAME ORDER:
      1. for (a, v) in input.poll(): state.handle_action(a, v)
      2. state.update(dt)
      3. snap = state.snapshot(); phase = engine.get_measure_phase()
      4. renderer.begin_panel('left'):  terrain.draw; totem_visual.draw;
         (SLICE mode: blade.draw)       renderer.end_panel()
      5. renderer.begin_panel('right'): helix_panel.draw(voices,
         engine.get_active_flashes(), phase); renderer.end_panel()
      6. renderer.composite()
      7. hud.draw(snap mode, state.quiz_ui_state())"""
    raise NotImplementedError

def main() -> None:
    """build(); pyglet clock schedules frame at 60 fps; clean engine.stop()
    on exit."""
    raise NotImplementedError

if __name__ == "__main__":
    main()
```

---

## 2. WHOLE GITA FILES PARENT G NEEDS (Nir pastes these separately)

- **Bhagavad Gita Part 1** — Laws of the Gita (G1.1), the full project tree, the
  complete frozen `config.py`, and `core/types.py`.
- **Bhagavad Gita Part 2** — audio contracts: `quantize.py`, `sampler.py`,
  `musicians.py`, `engine.py`, `render_offline.py` (incl. the `SampleLibrary`
  contract main.py builds at boot step 3), with amendments.
- **Bhagavad Gita Part 3 (amended)** — graphics contracts: `renderer.py`,
  `camera.py`, `terrain.py`, `totem.py`, `helix_panel.py`, `slice_mode.py`,
  `hud.py`, with amendments G3.1-A, G3.2-A, G3.3-A, G3.4-A, G3.6-A, G3.7-A.
- **Bhagavad Gita Part 4 (amended)** — core & main contracts: `surfaces.py`,
  `scene.py`, `game_state.py`, `input_map.py`, `main.py`, with amendments
  G4.3-A (and the G4.6 assignment plan). Parent G's own three files live here.

---

## 3. PURANAS — VERBATIM PUBLIC-API EXCERPTS (signatures + docstrings; bodies omitted)

> These three heavy modules were delivered whole in the PURANAS and are live code
> today. Below are ONLY the public seams main.py builds/calls (and the two dicts
> game_state returns). Bodies are omitted; every line shown is verbatim.

### 3a. audio/engine.py — class AudioEngine (the audio↔world seam)

```
CONTRACT AMENDMENT (approved by Nir, July 7 2026):
    AudioEngine.set_quiz_wav(path_or_None) -- quiz option WAVs play through
    this same engine and output path (required by GITA G4.3 _quiz_select).
    path=None stops playback (30 ms fade). Nothing else changed.

class AudioEngine:
    """Thread-safety contract: set_* methods are called from the game thread;
    the sounddevice callback reads a single atomically-swapped snapshot
    (build new dict/list, then one reference assignment -- no locks in the
    callback)."""

    def __init__(self, library):                       # library: SampleLibrary
        ...

    def start(self) -> None:
        """Open sounddevice.OutputStream with channels per current output
        mode; begin the callback."""

    def stop(self) -> None:
        ...

    def set_voices(self, voices: list) -> None:
        """Swap in a new list[Voice]. ... Vanished voices get a 30 ms
        fade-out, new ones a 30 ms fade-in (no clicks)."""

    def set_camera_azimuth(self, azimuth_deg: float) -> None:
        """THE surround input (SUTRAS 3.3/3.4). Zoom & elevation NEVER call this."""

    def set_output_mode(self, mode: str) -> None:
        """'stereo' | 'surround_5_1' | 'surround_7_1' (config.OUTPUT_MODES).
        Runtime toggle: close & reopen the stream with the new channel count;
        if the device refuses, fall back to stereo and report via get_status."""

    def set_quiz_wav(self, path) -> None:
        """AMENDMENT (approved): loop a pre-rendered option WAV through the
        same output path. path=None stops (30 ms fade). Mutual exclusion with
        live voices is game_state's discipline (G4.3); the mixer just mixes."""

    def get_measure_phase(self) -> float:
        """0..1 position inside the current 2.0 s measure. Drives the
        conductor's arm, ring pulses, icon flashes. Monotonic per measure."""

    def get_active_flashes(self) -> list:
        """List of (voice_index, strike_strength 0..1) for notes struck in the
        last ~50 ms -- consumed by helix_panel for icon glow."""

    def get_status(self) -> dict:
        # returns keys: mode, requested_mode, device_channels, running,
        # live_voices, dying_voices, quiz_playing, underruns,
        # fallback_voices, error

    def render_block_offline(self, seconds: float) -> np.ndarray:
        """Same mix path WITHOUT a device: (N, 2) float32 stereo, starting on
        a downbeat (t=0), voices at full gain (deterministic, no entry swell).
        ONE mixer, two callers -- byte-identical to live play."""
```

### 3b. core/game_state.py — class GameState (the conductor)

```
class GameState:
    def __init__(self, engine, camera, first_scene_id: str):
        """engine: AudioEngine. camera: OrbitCamera. Loads the scene, seats
        the grid (musicians.seat_grid), plants totem at totem_start, mode
        EXPLORE, pushes initial voices to engine."""

    def handle_action(self, action: Action, value: float) -> None:
        """THE ONLY INPUT ENTRY POINT. Routing by mode (G4.3). Discrete
        actions arrive once per press; held axes arrive every frame."""

    def update(self, dt: float) -> None:
        """Per frame: smooth analog totem motion; during slice auto-walk,
        advance one path stop per measure (downbeat edge of the engine's
        measure phase); scene transition timer; then clear intents."""

    def quiz_ui_state(self) -> dict:
        """Everything hud.draw needs: selected label, playing label,
        hint_open, explanation text, success state."""
        return {
            "selected": self._selected,
            "playing": self._playing,
            "hint_open": self._hint_open,
            "explain": self._explain,
            "success": self._success,
            "campaign_complete": self._campaign_complete,
        }

    def snapshot(self) -> dict:
        """Read-only bundle for main's draw calls: mode, totem, voices,
        slice plane, current SceneSpec. scene_changed is read-and-clear:
        main calls snapshot() exactly once per frame (G4.5).
        walk_stop/walking expose the current auto-walk stop for the bead
        (additive amendment, Q4; Parent E's GlassBlade.set_walk_stop)."""
        return {
            "mode": self._mode,
            "totem": self._totem,
            "voices": self._voices,
            "slice_plane": self._plane,
            "scene": self._spec,
            "scene_changed": changed,
            "quit": self._quit,
            "campaign_complete": self._campaign_complete,
            "walk_stop": idx,                # add. amend. Q4: bead marker
            "walking": self._walking,
            "walk_stop_x": wx,               # ground (x,y) of the current stop
            "walk_stop_y": wy,               # (slice_mode lifts to z=f(x,y)+LIFT)
        }
```

### 3c. graphics/helix_panel.py — class HelixPanel (RIGHT panel)

```
* Voice.note_z is WORLD height; the world-to-octave scale is the scene's
  z_per_octave. The draw contract doesn't carry it, so the panel exposes a
  plain public attribute `z_per_octave` (defaults to config.Z_PER_OCTAVE);
  main MAY set it on scene change. Optional -- everything works either way.

class HelixPanel:
    def __init__(self, renderer):
        """Load 13 instrument icons from config.ICONS_DIR (transparent PNGs)
        into a texture atlas. Build the wireframe helix: coils spanning the
        full orchestra range (~B0..C7), A4=440 line marked at z=0, floor with
        rhythm-ring circles, family register stacks drawn at their clock
        angles (tuba low ... trumpet high) as dim resident icons."""
        ...
        self.z_per_octave = config.Z_PER_OCTAVE   # main MAY set per scene

    def icon_for(self, sample_id: str) -> int:
        """'viola_E4' -> atlas index of viola. Pure lookup."""

    def draw(self, view_proj, voices: list, flashes: list,
             measure_phase: float) -> None:
        """For every Voice: draw its instrument icon as a camera-facing
        billboard at cylindrical position (r=ring*RING_WIDTH,
        theta=stage_angle_deg, z=note_z scaled to helix height), SCALED BY
        PERSPECTIVE distance from the camera (SUTRAS Part 4 -- far icons
        small). Blend voices (0<blend<1) show BOTH family icons overlapped
        with proportional alpha. flashes: matching icons glow-scale up ~1.3x
        with a 150 ms decay, feeding bloom. Conductor's arm sweeps the floor.
        Panel title text 'SONIFIQUATION COORDINATES' rendered by hud."""
```

---

END OF MATERIAL.
