Onward to the eyes. 🎨
📜 THE BHAGAVAD GITA — PART 3
The Graphics Module Contracts

LOOM2 · v1.0 · July 7, 2026 · Bodies empty by design — contracts frozen.
G3.1 — graphics/renderer.py

"""
LOOM2 -- graphics/renderer.py
The moderngl foundation: context, shader loading, framebuffers, bloom.
Reuses the proven pipeline style of Quake: Principia / Homeworld: A Good Basis
(DeepSeek may paste the working bloom/composite shaders from those repos).
Allowed imports: moderngl, pyglet, numpy, os, config. NO game logic.
Child chat scope: implement all bodies. ~250 lines expected.
"""
import moderngl, config

class Renderer:
    def __init__(self, window):            # pyglet window, already created
        """Create moderngl context; load all shaders from config.SHADERS_DIR;
        create two offscreen framebuffers (left panel, right panel), each
        (WINDOW_W//2, int(WINDOW_H*config.PANELS_FRAC)) -- the 50/50 split
        (SUTRAS 2.1) is enforced HERE and nowhere else."""
        raise NotImplementedError

    def begin_panel(self, side: str) -> None:
        """'left' | 'right': bind that panel's framebuffer, clear, set viewport
        and depth test. All draw calls until end_panel() land in this panel."""
        raise NotImplementedError

    def end_panel(self) -> None:
        raise NotImplementedError

    def composite(self) -> None:
        """Blit both panels to screen with bloom pass; leave the top strip and
        quiz bar regions untouched black (hud draws there afterward)."""
        raise NotImplementedError

    def program(self, name: str):
        """Return the compiled shader program by filename stem, e.g.
        program('terrain') -> data/shaders/terrain.vert + terrain.frag."""
        raise NotImplementedError

REQUIRED_SHADERS = ("terrain", "wire", "flat", "icon_billboard",
                    "glass", "bloom_extract", "bloom_blur", "composite")
# DeepSeek creates these files; children write GLSL inside them as needed.

G3.2 — graphics/camera.py

"""
LOOM2 -- graphics/camera.py
ONE camera state shared by BOTH panels (SUTRAS 3.2). Pure math, no GL calls.
Allowed imports: math, numpy, config, core.types.
Child chat scope: implement all bodies. ~120 lines expected.
"""
import config
from core.types import CameraState

class OrbitCamera:
    def __init__(self, limits: dict):
        """limits from SceneSpec.camera_limits: zoom_min/max, target center.
        Start at config.CAM_DEFAULT."""
        raise NotImplementedError

    def orbit(self, d_azimuth_deg: float, d_elevation_deg: float) -> None:
        """Elevation clamped to [CAM_ELEV_MIN_DEG, CAM_ELEV_MAX_DEG] -- the
        'forbidden top' is rounded (SUTRAS 3.5); azimuth wraps 0..360 and
        ALWAYS persists (it is the audio pan reference)."""
        raise NotImplementedError

    def zoom(self, factor: float) -> None:
        """Visual only. NEVER touches audio (SUTRAS 3.1)."""
        raise NotImplementedError

    def reset(self) -> None: raise NotImplementedError

    def state(self) -> CameraState: raise NotImplementedError

    def view_proj_terrain(self) -> "np.ndarray":
        """4x4 view-projection for the LEFT panel (isometric-feel perspective,
        Ultima-style default angle)."""
        raise NotImplementedError

    def view_proj_helix(self) -> "np.ndarray":
        """4x4 for the RIGHT panel: same azimuth & elevation, fixed distance
        framing the full 6-octave helix. Rotating one rotates both."""
        raise NotImplementedError

G3.3 — graphics/terrain.py

"""
LOOM2 -- graphics/terrain.py
The raised-relief hypsometric map (LEFT panel).
Allowed imports: numpy, moderngl, config, core.types.
Child chat scope: implement all bodies. ~200 lines expected.
"""

class TerrainMesh:
    def __init__(self, renderer, surface_fn, domain: tuple, mesh_step: float):
        """Build a triangle mesh of z = f(x,y) over the finite domain
        (SUTRAS Part 8). Per-vertex colors by height: config.COLOR_* bands
        (deep water < shallow < lowland < upland < peak), flat/Gouraud shaded
        demoscene look. Water plane at z=0, slightly glossy. Static VBO --
        built once per scene."""
        raise NotImplementedError

    def draw(self, view_proj) -> None:
        raise NotImplementedError

    def height_at(self, x: float, y: float) -> float:
        """Exact f(x,y) passthrough -- used to plant the totem on the ground."""
        raise NotImplementedError

G3.4 — graphics/totem.py

"""
LOOM2 -- graphics/totem.py
The tiny cute polygonal helix totem + ground projections (SUTRAS Part 7).
Allowed imports: math, numpy, moderngl, config, core.types.
Child chat scope: implement all bodies. ~180 lines expected.
"""

class TotemVisual:
    def __init__(self, renderer):
        """Small low-poly helix model (~200 triangles), no staff. Emissive
        material fed to bloom with a slow sinusoidal pulse (period ~3 s,
        NOT synced to the measure -- it breathes, it does not tick)."""
        raise NotImplementedError

    def draw(self, view_proj, totem_state, ground_z: float,
             measure_phase: float) -> None:
        """Draw at (x, y, ground_z): the helix model; the hearing circle on
        the ground; rhythm rings at radii n*RING_WIDTH inside it; the
        conductor's arm sweeping once per measure (angle = measure_phase*360,
        12 o'clock at phase 0 -- the downbeat)."""
        raise NotImplementedError

G3.5 — graphics/helix_panel.py

"""
LOOM2 -- graphics/helix_panel.py
THE SONIFIQUATION COORDINATES panel (RIGHT half). The soul on screen.
Allowed imports: math, numpy, moderngl, pyglet(image loading), os, config,
core.types.
Child chat scope: implement all bodies. ~300 lines expected. Hard module.
"""

class HelixPanel:
    def __init__(self, renderer):
        """Load 13 instrument icons from config.ICONS_DIR (transparent PNGs)
        into a texture atlas. Build the wireframe helix: coils spanning the
        full orchestra range (~B0..C7), A4=440 line marked at z=0, floor with
        rhythm-ring circles, family register stacks drawn at their clock
        angles (tuba low ... trumpet high) as dim resident icons."""
        raise NotImplementedError

    def draw(self, view_proj, voices: list, flashes: list,
             measure_phase: float) -> None:
        """For every Voice: draw its instrument icon as a camera-facing
        billboard at cylindrical position (r=ring*RING_WIDTH,
        theta=stage_angle_deg, z=note_z scaled to helix height), SCALED BY
        PERSPECTIVE distance from the camera (SUTRAS Part 4 -- far icons
        small). Blend voices (0<blend<1) show BOTH family icons overlapped
        with proportional alpha. flashes: matching icons glow-scale up ~1.3x
        with a 150 ms decay, feeding bloom. Conductor's arm sweeps the floor.
        Panel title text 'SONIFIQUATION COORDINATES' rendered by hud, not here."""
        raise NotImplementedError

    def icon_for(self, sample_id: str) -> int:
        """'viola_E4' -> atlas index of viola. Pure lookup."""
        raise NotImplementedError

G3.6 — graphics/slice_mode.py

"""
LOOM2 -- graphics/slice_mode.py
THE GLASS BLADE (SUTRAS Part 6). Visual + path math; NO audio calls.
Allowed imports: math, numpy, moderngl, config, core.types.
Child chat scope: implement all bodies. ~250 lines expected. Hard module.
"""
from core.types import SlicePlane

class GlassBlade:
    def __init__(self, renderer):
        raise NotImplementedError

    def update_plane(self, plane: SlicePlane) -> None:
        """Store current plane pose (moved/rotated by input while in SLICE mode)."""
        raise NotImplementedError

    def intersection_path(self, surface_fn, domain: tuple,
                          step: float = 0.25) -> list:
        """THE CONTRACT THE WHOLE FEATURE HANGS ON:
        returns ordered [(x, y), ...] where the vertical plane crosses the
        domain -- the transect. Straight line in (x,y): sample along it.
        Used BOTH to draw the glowing cross-section curve AND as the totem's
        auto-walk itinerary (one stop per measure, executed by game_state --
        a procession of neighborhoods, NEVER a siren)."""
        raise NotImplementedError

    def draw(self, view_proj, surface_fn) -> None:
        """Semi-transparent glass quad; the cross-section curve z=f(path(t))
        drawn GLOWING ON THE GLASS like a graph on a screen; current auto-walk
        stop marked with a bright bead."""
        raise NotImplementedError

G3.7 — graphics/hud.py

"""
LOOM2 -- graphics/hud.py
Top strip + quiz bar + panel titles. 2D overlay, pyglet text/sprites.
Allowed imports: pyglet, os, config, core.types.
Child chat scope: implement all bodies. ~220 lines expected.
"""

class Hud:
    def __init__(self, window):
        raise NotImplementedError

    def set_scene(self, spec) -> None:      # SceneSpec
        """Load title_lines, equation.png (LaTeX-rendered, top strip right side),
        question text, option labels, hint_lines."""
        raise NotImplementedError

    def draw(self, mode, quiz_ui_state: dict) -> None:
        """Top strip: 2-3 scenario lines + equation image. Panel titles:
        config.PANEL_TITLE_LEFT / PANEL_TITLE_RIGHT. Quiz bar: buttons
        A B C D (playing state shows a small speaker glyph), OK, and HINT
        beside OK (SUTRAS 5.1); hint text overlays when open; wrong-answer
        explanation text shown gently (soft color, no red); success text on
        correct. quiz_ui_state comes from game_state, hud only DRAWS."""
        raise NotImplementedError

    def hit_test(self, mx: int, my: int) -> str:
        """Mouse -> 'A'|'B'|'C'|'D'|'OK'|'HINT'|'' -- consumed by input_map."""
        raise NotImplementedError

Seam summary for DeepSeek: every draw() receives ready-made state; graphics never computes game logic and never touches audio. The only cross-panel guarantee is OrbitCamera — one instance, two view_proj_* calls. GlassBlade.intersection_path is consumed by game_state (Part 4) to march the totem measure-by-measure.

End of Part 3. Say "continue" for Part 4 — the core & main contracts (surfaces.py, scene.py, game_state.py, input_map.py, main.py) — and then the Gita is complete and ready for DeepSeek to bind. 📜🧵
