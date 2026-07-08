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

<<<<<<<<<< AMENDMENT G3.1-A — added 2026-07-08 >>>>>>>>>>
ORDERED BY: Nir (iron rule: NO FLAT SHADING EVER — everything Gouraud).
REQUESTED BY: Fable "Parent D" (the graphics/terrain.py + graphics/totem.py chunk),
in his Gouraud totem redelivery.
CHANGE: REQUIRED_SHADERS grows from 8 stems to 9 — a NINTH stem "totem" is added:
    REQUIRED_SHADERS = ("terrain", "wire", "flat", "icon_billboard",
                        "glass", "bloom_extract", "bloom_blur", "composite",
                        "totem")
WHY: the shared 'flat' program is one flat color per draw call and cannot express
Gouraud shading, which the iron rule requires for the helix totem's surface. The
new "totem" program is owned by graphics/totem.py (Child D); its GLSL lives in
data/shaders/totem.vert + data/shaders/totem.frag.
INTERFACE (canon):
    totem.vert: uniform mat4 u_mvp; in vec3 in_pos; in float in_light;
    totem.frag: uniform vec4 u_color;   // f_color = vec4(u_color.rgb * v_light, u_color.a)
STATUS: applied in graphics/renderer.py (extracted code) 2026-07-08; both shader
files created. (The 'flat' program stays for LINES only — edge lines, rings,
hearing circle, arm — which have no surface to shade, so that is not flat shading.)
<<<<<<<<<< END AMENDMENT G3.1-A >>>>>>>>>>

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

<<<<<<<<<< AMENDMENT G3.2-A — added 2026-07-08 (locked 2026-07-07) >>>>>>>>>>
ORDERED BY: Nir. ESTABLISHED BY: Fable "Parent C" (the camera.py + renderer.py
chunk), as the first consumer of SceneSpec.camera_limits.
CHANGE (de-facto contract nailed down — no signature change): the camera_limits
dict (from SceneSpec.camera_limits, consumed by OrbitCamera.__init__) has these
canonical keys, which Parent G's scene.py validation AND every scene.json MUST
conform to:
    "target"    : 3-list world point, default [0, 0, 0]
    "zoom_min"  : float, default 0.5
    "zoom_max"  : float, default 2.5
    "distance"  : float, OPTIONAL, default 14.0
MATRIX CONVENTION (locked, matches helix_panel): column vectors, clip = VP @ p,
uploaded transposed via np.ascontiguousarray(vp.T).tobytes(). Zoom factor > 1 =
zoom IN (confirmed consistent with game_state). The helix panel uses a FIXED
distance (~16.1, bounding-sphere, elevation-proof); zoom applies to terrain only.
STATUS: implemented + behavior-tested in graphics/camera.py (Parent C).
DEEPSEEK OWES: propagate these keys to Parent G's scene.py + all scene JSON.
<<<<<<<<<< END AMENDMENT G3.2-A >>>>>>>>>>

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

<<<<<<<<<< AMENDMENT G3.3-A — added 2026-07-08 >>>>>>>>>>
ORDERED BY: Nir (decisions A2/A3/A4 + snow-bloom). REQUESTED/DELIVERED BY: Fable
"Parent D" (the terrain.py + totem.py chunk).
CLARIFICATIONS to the __init__ docstring above (which said "flat/Gouraud shaded"
and "Water plane at z=0"):
  A3 — SHADING IS GOURAUD, NOT FLAT (Nir's iron rule: no flat shading ever).
       Per-vertex Lambert light (from central differences of the true surface_fn,
       sun _LIGHT_DIR=(0.45,0.28,0.85), _AMBIENT=0.38), smoothly interpolated.
  A2 — HARD hypsometric bands: band color is chosen PER FRAGMENT from the
       interpolated world height, so band edges are pixel-sharp level curves.
       (Gouraud light × hard per-fragment bands = smooth shading AND crisp curves.)
       Band edges (absolute world z, identical every scene): (-1.5, -0.6, 0.0,
       1.1, 2.2); darkest abyss = COLOR_DEEP_WATER * 0.55.
  A4 — NO separate water plane / no water VBO. Below z=0 is the SAME mesh in hard
       blue bands darkening with depth. (A static second VBO would have been
       contract-legal, but Nir's design removes the need.)
  SNOW-BLOOM (Nir) — terrain colors stay <= 1.0 EXCEPT peak snow (~0.82-0.84),
       which Nir CHOSE to keep just above the 0.80 bloom bright-pass for a faint
       shimmer.
OWNED SHADERS (terrain.py owns these; interface canon):
  terrain.vert: uniform mat4 u_mvp; in vec3 in_pos; in float in_light;
  terrain.frag: uniform vec3 u_band_colors[6]; uniform float u_band_edges[5];
ADDITION (flagged): TerrainMesh.release() frees VBO/IBO/VAO on scene change (not
in the frozen contract; safe to never call; main should call old_mesh.release()).
height_at is a pure passthrough that also accepts numpy arrays (fast draping).
STATUS: implemented in graphics/terrain.py (Parent D, extracted code) 2026-07-08.
<<<<<<<<<< END AMENDMENT G3.3-A >>>>>>>>>>

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

<<<<<<<<<< AMENDMENT G3.4-A — added 2026-07-08 >>>>>>>>>>
ORDERED BY: Nir. REQUESTED BY: Fable "Parent D" (the terrain.py + totem.py chunk).
Two changes to TotemVisual.draw, both delivered in graphics/totem.py:

(1) DRAPED RINGS — signature change (Nir's decision A7).
    OLD:  def draw(self, view_proj, totem_state, ground_z: float,
                   measure_phase: float) -> None
    NEW:  def draw(self, view_proj, totem_state, height_fn,
                   measure_phase: float) -> None
    WHY: A7 requires the hearing circle + rhythm rings + arm to be DRAPED over
    the terrain (hugging every bump/dip), which needs terrain height sampled all
    around each ring — a single scalar ground_z is not enough. height_fn(x, y) -> z
    is a callable; main passes TerrainMesh.height_at (a pure surface-fn passthrough
    that accepts numpy arrays for fast draping). The totem computes its own ground
    height from height_fn.
    DEEPSEEK OWES: wire main's frame step 4 to pass terrain.height_at:
        totem_visual.draw(vp_left, snap_totem, terrain.height_at, phase)

(2) GOURAUD HELIX — no flat shading (Nir's iron rule).
    The helix surface is GOURAUD shaded (per-vertex Lambert from the ribbon's
    analytic radial normals, same sun _LIGHT_DIR=(0.45,0.28,0.85) and _AMBIENT=0.38
    as terrain.py), drawn with the NEW "totem" shader program (see AMENDMENT G3.1-A).
    The 'flat' program is used ONLY for LINES (edge lines, rings, hearing circle,
    arm) — lines have no surface to shade, so this obeys the iron rule.

(3) ARM DIRECTION — clarified (Nir's decision A1).
    The docstring says "angle = measure_phase*360"; the LOCKED value is
    angle = 90 - measure_phase*360 degrees (CLOCKWISE from above; phase 0 = 12
    o'clock = world +y), matching helix_panel.py line 253 verbatim.
STATUS: all three applied in graphics/totem.py (extracted code) 2026-07-08.
<<<<<<<<<< END AMENDMENT G3.4-A >>>>>>>>>>

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
