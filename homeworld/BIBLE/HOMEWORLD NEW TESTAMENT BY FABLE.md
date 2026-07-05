# THE NEW TESTAMENT — HOMEWORLD: A GOOD BASIS
## Module Design: forge, fleet, helm — v1.0 — Peak Together — July 4, 2026

---

> ## ⚖️ OWNER AMENDMENTS (add-only, maintained by DeepSeek — READ FIRST) ⚖️
>
> **These are Nir's (the owner's) binding decisions made after this document was written.
> They OVERRIDE anything below that conflicts. Fable's original text is preserved verbatim
> underneath. New amendments are appended to this list.**
>
> **Amendment A1 — SHIPS ARE SOLID, NOT WIREframe (July 5, 2026).** Ships are now **solid,
> opaque, lit triangle meshes** (per-pixel Blinn-Phong: key + fill + rim + specular, paneled
> hulls, emissive nozzles/windows feeding bloom), built by `shipwright.py`. **Only the MATH
> LAYER** (arrows, grids, ghosts, trails, labels) stays glowing holographic, drawn additively
> OVER the solids with depth testing. forge's render pipeline is now: **solid pass (depth
> write) → glow pass (depth test, no write) → bloom → overlay** (see `shaders.py` MESH shader,
> `solid.py`, updated `bloom.py`/`forge.py`). Wherever this document's "Homeworld-of-wireframes
> aesthetic" or wireframe-ship language appears, it is superseded — **ships are solid; the math
> layer glows.** (Full text: `notes/amendment_a1_art_direction.md` + Old Testament amendments.)

---
## Requires: BIBLE.md v2.1 (the Old Testament). If this document contradicts the
## Bible, the Bible wins. If code contradicts this document, this document wins
## until the owner approves an interface version bump.

NOTE TO ALL READERS (human, Opus parent/child, DeepSeek): All mathematics is
written in LaTeX. Inline math is delimited by $...$ and display math by $$...$$.
Subscripts use _, superscripts use ^. Never alter the LaTeX when copying.
All code blocks are Python 3.12+ unless marked GLSL.

---------------------------------------------------------------------------------
PART 0 — SCOPE AND SHARED CONVENTIONS
---------------------------------------------------------------------------------

This document specifies the three foundation modules to implementation depth:

  forge/  — the render engine (a real-time Manim: window, camera, glowing
            vector primitives, bloom, text, screenshots)
  helm/   — the input abstraction (logical actions; keyboard+mouse now,
            joystick+Xbox later without touching game logic)
  fleet/  — the simulation core (ships as matrix columns, the 10 Hz pulse,
            orders, events, and the Referee — the canonical NumPy verdict
            functions used by the whole game)

The remaining modules (campaign, bridge, intel, audio, content) are specified in
the APOCRYPHA. app.py wiring is specified here (Part 4) because it binds these
three.

SHARED CONVENTIONS (frozen):

- Coordinate system: right-handed, Y is up. The Homeworld "reference plane" is
  the XZ-plane through the origin. The Mothership sits at the origin $(0,0,0)$.
- Units: abstract "space units"; typical play volume is a sphere of radius ~100
  units. Angles in radians everywhere. Time in seconds.
- All simulation math in numpy float64. All GPU data converted to float32 only
  at upload time.
- Colors are RGBA tuples of floats in [0, 1].
- Naming: modules and files lowercase; classes CapWords; functions and
  variables snake_case; constants UPPER_SNAKE.
- Errors: fail loudly. app.py wraps everything in one try/except that writes
  crashlog.txt (full traceback + version + seed + mission id) and shows a
  friendly message. No module silently swallows exceptions.
- Dependencies (complete list): numpy, moderngl, pyglet, Pillow. Nothing else
  without owner approval.
- Tolerance doctrine (from the Bible, Part 1): structural verdicts never use
  equality. The single source of truth for tolerances is fleet/referee.py:
  TOL_RANK = 1e-6 (relative), TOL_RESIDUAL = 1e-4 (absolute, gameplay-tuned per
  mission file), TOL_IMAG = 1e-9.

TIME MODEL (frozen): the game runs a fixed-timestep logic PULSE at 10 Hz
(PULSE_DT = 0.1 s) and renders at display rate (target 60 fps) with linear
interpolation. The accumulator pattern lives in forge (it owns the pyglet
clock); fleet is called back exactly once per pulse; renderers receive the
interpolation fraction $\alpha \in [0, 1)$ and draw positions

$$p_{\text{draw}} = p_{\text{prev}} + \alpha \, (p_{\text{curr}} - p_{\text{prev}}).$$

DETERMINISM (frozen): fleet owns the only random generator,
numpy.random.default_rng(seed). Logic never reads the wall clock. Given the same
seed and the same order stream, every pulse is bit-identical. The seed is shown
in the F1 debug overlay so a bug report is "seed 1234, mission 5, pulse ~300,
here is what I saw."

---------------------------------------------------------------------------------
PART 1 — FORGE: THE REAL-TIME MANIM
---------------------------------------------------------------------------------

=== 1.1 FILES ===

```
forge/
├── __init__.py      # exports Forge, Camera, and all VObject classes
├── app.py           # Forge class: window, GL context, main loop, accumulator
├── camera.py        # Camera class: ORBIT / FOLLOW / POV, view & projection
├── vobjects.py      # all primitives (VObject base + 11 primitives)
├── batches.py       # CPU geometry expansion (numpy) + VBO management
├── shaders.py       # GLSL sources as Python strings
├── bloom.py         # offscreen FBOs, separable Gaussian blur, composite
├── text.py          # Pillow-built glyph atlas + Label rendering
└── demo.py          # python -m forge.demo  (acceptance test, see Part 6)
```

=== 1.2 THE FORGE CLASS (owner of window and loop) ===

```python
class Forge:
    def __init__(self, settings: dict) -> None:
        """Creates pyglet window + moderngl context. settings keys used:
        width, height, fullscreen, vsync, bloom_strength, title, version."""
    window: "pyglet.window.Window"     # exposed so helm can attach handlers
    camera: "Camera"
    def add(self, vob: "VObject") -> None: ...
    def remove(self, vob: "VObject") -> None: ...
    def set_debug_lines(self, lines: list[str]) -> None:
        """F1 overlay content; app refreshes each frame."""
    def screenshot(self, path: str | None = None) -> str:
        """Saves screenshots/YYYYMMDD_HHMMSS.png, returns path."""
    def run(self,
            tick_cb,      # tick_cb(dt: float) -> None, called at exactly 10 Hz
            frame_cb      # frame_cb(alpha: float) -> None, called每 frame
            ) -> None:
        """Starts the loop. Never returns until window closes.
        Loop body per display frame:
          accumulator += real_dt (clamped to 0.25 s to survive hitches)
          while accumulator >= PULSE_DT: tick_cb(PULSE_DT); accumulator -= PULSE_DT
          frame_cb(accumulator / PULSE_DT)   # update vobjects from snapshot
          render()                            # scene pass -> bloom -> composite
        """
```

The render() pipeline (fixed order): (1) clear scene FBO to pure black;
(2) draw all visible VObjects grouped into batches (Part 1.5); (3) bloom
(Part 1.6); (4) composite to screen; (5) draw debug overlay text last, no bloom.

=== 1.3 THE CAMERA ===

```python
class Camera:
    mode: str                 # "ORBIT" | "FOLLOW" | "POV"
    fov_y: float = 1.05       # ~60 degrees, radians
    near: float = 0.1
    far: float  = 2000.0
    # ORBIT state:
    target: "np.ndarray"      # (3,) point orbited
    yaw: float; pitch: float; distance: float
    def set_orbit(self, target: "np.ndarray") -> None: ...
    def orbit_input(self, d_yaw: float, d_pitch: float, d_zoom: float) -> None:
        """pitch clamped to (-1.55, 1.55) rad; distance clamped to (2, 500)."""
    def set_follow(self, get_pos) -> None:
        """get_pos() -> (3,) each frame; keeps yaw/pitch/distance around it."""
    def set_pov(self, get_pos, get_forward) -> None: ...
    def view(self) -> "np.ndarray":   # (4,4) float64 view matrix
    def proj(self, aspect: float) -> "np.ndarray": ...
    def eye(self) -> "np.ndarray":    # (3,) camera position, needed by batches
```

ORBIT math (frozen): with yaw $\theta$, pitch $\phi$, distance $d$, target $t$:

$$\text{eye} = t + d \,(\cos\phi \sin\theta, \; \sin\phi, \; \cos\phi \cos\theta)$$

view matrix = look_at(eye, t, up=$(0,1,0)$). look_at and perspective are
implemented in camera.py with numpy (do not import a math library for this;
the formulas are standard and ~15 lines).

There is NO mouse control of the camera and NO 3D mouse picking anywhere in the
game (the mouse belongs to the Navigator's 2D console — Bible Part 4). This
removes an entire class of complexity: forge needs no ray casting.

=== 1.4 VOBJECTS — THE PRIMITIVE VOCABULARY (frozen) ===

Base contract:

```python
class VObject:
    visible: bool = True
    color: tuple = (0.5, 0.9, 1.0, 1.0)   # default cyan glow
    glow: float = 1.0                       # brightness multiplier into bloom
    def set_color(self, rgba) -> None: ...
    # each subclass defines set_data(...) taking numpy arrays; calling set_data
    # marks the object dirty; batches re-upload only dirty objects.
```

The eleven primitives (constructor signatures frozen):

```python
Line(points: "np.ndarray")            # (N,3) polyline through N points
Arrow(start, end, head_size=0.5)      # shaft + 4-line pyramid head; THE vector
DashedLine(start, end, dash=0.5)      # equal dash/gap lengths
Grid(center, u, v, n=10, spacing=1.0) # plane grid spanned by vectors u and v:
                                      # lines center + i*spacing*u + j*spacing*v;
                                      # THIS is how "span of two vectors" is drawn
WireSphere(center, radius, seg=24)    # 3 orthogonal great circles + 2 parallels
WireMesh(vertices, edges)             # (N,3) float and (M,2) int index pairs;
                                      # ships are WireMeshes loaded from content/
SpannedBox(origin, v1, v2, v3=None)   # parallelogram (v3 None) or parallelepiped;
                                      # 12 edges; serves Ch.1 (span) and Ch.5 (det)
Ellipsoid(center, M)                  # unit wire-sphere transformed by 3x3 M;
                                      # for shields draw with M = Q @ diag(lambda)**-0.5
Trail(max_points=64)                  # ring buffer; .push(point) once per pulse;
                                      # alpha fades linearly from head to tail
Label(text, pos, size=1.0)            # billboarded text; set_text(str) allowed
ImagePanel(image, pos, w, h)          # image: (H,W) float64 in [0,1] grayscale;
                                      # set_image() re-uploads texture (Guidestone!)
```

Rules: every set_data accepts numpy float64 and copies it (no aliasing of fleet
memory). Nothing in forge knows what a "ship" is. A parent composing a scene
holds references to its VObjects and updates them in frame_cb from the fleet
snapshot.

=== 1.5 GEOMETRY: HOW LINES BECOME TRIANGLES (batches.py) ===

OpenGL native line width is unreliable above 1 px, so all lines are expanded to
camera-facing ribbons on the CPU with vectorized numpy, then drawn as triangles
in a small number of draw calls.

For a segment from $p_0$ to $p_1$ with half-width $w$, and camera eye $e$:

$$\text{dir} = \frac{p_1 - p_0}{\|p_1 - p_0\|}, \qquad
\text{side} = \frac{\text{dir} \times (e - p_0)}{\|\text{dir} \times (e - p_0)\|},$$

emit the quad $(p_0 - w s,\; p_0 + w s,\; p_1 + w s,\; p_1 - w s)$ as two
triangles, with a "ribbon coordinate" $u \in [-1, 1]$ across the width. The
fragment shader shades $\text{intensity} = (1 - u^2)^2$ so each line has a hot
core and soft edges BEFORE bloom even runs. Default half-width 0.06 units.

Batching: one dynamic VBO for all line-based primitives that changed this frame,
one for all static ones (rebuilt only when dirty), one textured-quad batch for
Labels + ImagePanels. Target: the whole game renders in < 10 draw calls. All
expansion code operates on arrays of segments at once — never a Python loop per
segment. With <= 20 ships and tiny wire meshes, total segments per frame is a
few thousand: trivial for numpy at 60 fps.

Blending (frozen): scene pass uses ADDITIVE blending, glBlendFunc(GL_ONE,
GL_ONE), depth test ON, depth write OFF for all line ribbons (ImagePanel: normal
alpha blending, depth write ON, drawn first). Additive blending is
order-independent, so NO sorting is ever needed — overlapping glow simply gets
brighter, which is exactly the Homeworld-of-wireframes aesthetic.

=== 1.6 BLOOM (bloom.py) ===

Classic three-FBO bloom, adequate and cheap:

1. Scene renders into FBO_A (RGBA16F, full resolution). Since the world is
   emissive-on-black, no bright-pass filter is needed — the scene IS the bright
   pass.
2. Downsample FBO_A into FBO_B at 1/4 resolution (hardware linear filter).
3. Separable Gaussian blur: horizontal pass FBO_B -> FBO_C, vertical pass
   FBO_C -> FBO_B, kernel of 9 taps with weights
   $w_i \propto e^{-i^2 / (2\sigma^2)}$, $\sigma = 2.0$, normalized to sum 1.
4. Composite to screen: final = scene + bloom_strength * blurred, where
   bloom_strength comes from settings.json (default 0.8), then a soft tone map
   $c \mapsto c / (1 + c)$ to keep hot cores white, not clipped ugly.

GLSL sketches (shaders.py; complete versions written by the implementing child):

```glsl
// line.vert
#version 330
uniform mat4 u_mvp;
in vec3 in_pos; in vec4 in_color; in float in_u;   // u: ribbon coord in [-1,1]
out vec4 v_color; out float v_u;
void main(){ gl_Position = u_mvp * vec4(in_pos,1.0); v_color=in_color; v_u=in_u; }

// line.frag
#version 330
in vec4 v_color; in float v_u; out vec4 f;
void main(){ float k = 1.0 - v_u*v_u; f = vec4(v_color.rgb * k * k * v_color.a, 1.0); }
```

=== 1.7 TEXT (text.py) ===

At startup, Pillow renders a monospace font (bundled .ttf in content/fonts/) at
48 px into a single glyph atlas texture covering ASCII 32..126 plus the exact
extra glyphs the game needs (frozen list): × · ⟂ Σ Λ σ λ θ ρ ε ≈ ≤ ≥ − → ‖.
Labels are quads sampling the atlas, billboarded: the quad is built in camera
space (using camera right/up axes) so text always faces the viewer. The debug
overlay reuses the same atlas drawn in screen space, bypassing bloom.

---------------------------------------------------------------------------------
PART 2 — HELM: THE INPUT ABSTRACTION
---------------------------------------------------------------------------------

=== 2.1 FILES ===

```
helm/
├── __init__.py       # exports Helm, ActionEvent, PointerState, ACTIONS
├── actions.py        # THE FROZEN ACTION LIST + dataclasses
├── keyboard_map.py   # KeyboardMapper (Pilot baseline)
├── mouse_map.py      # MouseMapper (Navigator baseline)
├── joystick_map.py   # STUB with instructions for DeepSeek (T16000M)
├── gamepad_map.py    # STUB with instructions for DeepSeek (Xbox controller)
└── demo.py           # python -m helm.demo (acceptance test, Part 6)
```

=== 2.2 THE FROZEN ACTION LIST (actions.py, version 1) ===

Adding a new action later = allowed with a minor version bump. Renaming or
removing an action = forbidden without owner approval. Game logic imports these
names and NEVER imports pyglet key codes.

```python
ACTIONS_VERSION = 1

# ---- Pilot: continuous axes (value in [-1.0, +1.0] each pulse) ----
PILOT_AXES = [
    "CAM_YAW", "CAM_PITCH", "CAM_ZOOM",      # camera orbit control
    "TRIM_X", "TRIM_Y", "TRIM_Z",            # thruster trim (Bible 2.1)
]
# ---- Pilot: buttons (events with value 1.0 press / 0.0 release) ----
PILOT_BUTTONS = [
    "SELECT_NEXT", "SELECT_PREV",            # cycle ships
    "SQUAD_NEXT", "SQUAD_PREV",              # cycle squads
    "ORDER_CONFIRM", "ORDER_CANCEL",
    "ACTION_PRIMARY",                        # fire / execute (context action)
    "ACTION_SECONDARY",                      # context action 2 (e.g., dock)
    "FLIGHT_MODE_TOGGLE",                    # component vs diagonal (Bible 2.1)
    "CAM_MODE_CYCLE",                        # ORBIT -> FOLLOW -> POV -> ORBIT
    "PAUSE",
]
# ---- System buttons (either player, always active) ----
SYSTEM_BUTTONS = [ "DEBUG_OVERLAY",          # F1
                   "SCREENSHOT" ]            # F12
# ---- Navigator: the pointer is the entire interface ----
# PointerState: x, y in window pixels (origin bottom-left), primary/secondary
# button booleans, wheel delta since last poll. The bridge module consumes
# PointerState directly; there are no named Navigator buttons.
```

```python
@dataclass(frozen=True)
class ActionEvent:
    action: str      # one of the names above
    value: float     # 1.0 press / 0.0 release; axes are polled, not evented

@dataclass(frozen=True)
class PointerState:
    x: float; y: float
    primary: bool; secondary: bool
    wheel: float
```

=== 2.3 THE HELM CLASS AND MAPPER PROTOCOL ===

```python
class Helm:
    def __init__(self, settings: dict) -> None:
        """settings['input'] = {
             'pilot_device': 'keyboard',      # or 'joystick' | 'gamepad'
             'navigator_device': 'mouse',     # or 'gamepad' | 'joystick'
             'keyboard_overrides': { ... }    # optional remaps, see 2.4
           }
        Any device may drive either role (Bible, Iron Rule 2). Unavailable
        device -> loud warning + fallback to keyboard/mouse, never a crash."""
    def attach(self, window) -> None:
        """Registers pyglet event handlers. Must be called once before run."""
    def poll(self) -> tuple[list[ActionEvent], dict[str, float], PointerState]:
        """Called once per PULSE by app.tick. Returns (button events since last
        poll, current axis values dict for all PILOT_AXES, pointer state).
        Also called once per FRAME with events discarded, for camera smoothness:
        poll_axes_only() -> dict[str, float]."""
    def poll_axes_only(self) -> dict[str, float]: ...
```

Mapper protocol (each device file implements this; helm composes two of them):

```python
class Mapper(Protocol):
    def attach(self, window) -> None: ...
    def poll_events(self) -> list[ActionEvent]: ...
    def poll_axes(self) -> dict[str, float]: ...
    def poll_pointer(self) -> PointerState | None: ...   # None if not a pointer
```

=== 2.4 DEFAULT KEYBOARD MAP (KeyboardMapper) ===

Frozen defaults (overridable in settings.json under keyboard_overrides, keys
are pyglet key names as strings):

```
Camera:    LEFT/RIGHT arrows -> CAM_YAW -1/+1 ; UP/DOWN -> CAM_PITCH +1/-1
           PAGEUP/PAGEDOWN   -> CAM_ZOOM -1/+1 ; C -> CAM_MODE_CYCLE
Trim:      W/S -> TRIM_Z +1/-1 ; A/D -> TRIM_X -1/+1 ; R/F -> TRIM_Y +1/-1
Selection: TAB -> SELECT_NEXT ; LSHIFT+TAB -> SELECT_PREV
           E -> SQUAD_NEXT ; Q -> SQUAD_PREV
Orders:    ENTER -> ORDER_CONFIRM ; BACKSPACE -> ORDER_CANCEL
           SPACE -> ACTION_PRIMARY ; LCTRL -> ACTION_SECONDARY
           X -> FLIGHT_MODE_TOGGLE ; P -> PAUSE
System:    F1 -> DEBUG_OVERLAY ; F12 -> SCREENSHOT
```

Held keys produce axis value +1/-1 while held (digital axes). This is the
baseline that must always work (Iron Rule 2).

=== 2.5 INSTRUCTIONS FOR DEEPSEEK: FUTURE JOYSTICK / GAMEPAD MAPPERS ===

Written here so the future work needs no context beyond this file:

1. Enumerate devices with pyglet.input.get_joysticks() and get_controllers();
   call device.open(). Xbox controllers appear via get_controllers() with named
   attributes (leftx, lefty, rightx, righty, lefttrigger, righttrigger, buttons
   a/b/x/y); the Thrustmaster T16000M appears via get_joysticks() with .x, .y,
   .rz (twist), .z (throttle slider) and .buttons list.
2. Apply the dead-zone formula to every analog axis with dead zone $d = 0.15$:
   $$v' = \operatorname{sign}(v) \cdot \max\!\left(0, \frac{|v| - d}{1 - d}\right)$$
3. Suggested T16000M pilot mapping: x -> CAM_YAW, y -> CAM_PITCH, twist rz ->
   TRIM_X, throttle z -> CAM_ZOOM, trigger -> ACTION_PRIMARY, thumb button ->
   ORDER_CONFIRM, hat switch -> TRIM_Y/TRIM_Z.
4. Suggested Xbox pilot mapping: leftx/lefty -> CAM_YAW/CAM_PITCH, rightx/righty
   -> TRIM_X/TRIM_Z, triggers -> CAM_ZOOM (RT-LT), A -> ORDER_CONFIRM, B ->
   ORDER_CANCEL, X -> ACTION_PRIMARY, Y -> FLIGHT_MODE_TOGGLE, bumpers ->
   SELECT_PREV/NEXT, start -> PAUSE.
5. Xbox as NAVIGATOR device: left stick moves a virtual pointer (PointerState
   synthesized: x += stick_x * speed * dt), A = primary click, B = secondary,
   right stick vertical = wheel. This gives couch-Navigator play.
6. Implement only poll_events / poll_axes / poll_pointer. DO NOT touch any file
   outside helm/. DO NOT rename any action. Test with: python -m helm.demo.

---------------------------------------------------------------------------------
PART 3 — FLEET: THE SIMULATION CORE AND THE REFEREE
---------------------------------------------------------------------------------

=== 3.1 FILES ===

```
fleet/
├── __init__.py      # exports FleetSim, Ship, orders, events, referee
├── ships.py         # Ship dataclass + ship class definitions loader
├── orders.py        # THE FROZEN ORDER TYPES (dataclasses)
├── events.py        # THE FROZEN EVENT TYPES
├── sim.py           # FleetSim: pulse loop, systems, state
├── referee.py       # THE CANONICAL NUMPY VERDICT FUNCTIONS (heart of Rule 4)
├── snapshot.py      # read-only FleetSnapshot for forge/bridge
└── demo.py          # python -m fleet.demo (headless self-test, Part 6)
```

=== 3.2 DATA MODEL ===

```python
@dataclass
class Ship:
    ship_id: int
    klass: str                  # "fighter", "beam_corvette", ... from content/
    signature: "np.ndarray"     # (6,) float64, channel order K,B,M,S,J,U
    pos: "np.ndarray"           # (3,) float64
    prev_pos: "np.ndarray"      # (3,) for render interpolation
    facing: "np.ndarray"        # (3,) unit vector (intake/nose direction)
    hp: float
    fuel: float
    squad: int                  # squad id, 0 = unassigned
    alive: bool = True
```

FleetSim state: dict ship_id -> Ship; resources: float; unlocked engine vectors
E (list of (3,) arrays); research flags; the mission-context objects (active
sensor grid matrix A_grid, active shield vectors, active gate frigate ids, the
current augmented matrix for row-op missions) — installed by campaign via the
mission API (Apocrypha) but STORED here so that one snapshot carries everything.

The two Bible matrices are assembled on demand (never stored stale):

```python
def formation_matrix(self, ids: list[int]) -> "np.ndarray":
    """P: columns are positions of the given ships, shape (3, len(ids))."""
def fleet_matrix(self, ids: list[int] | None = None) -> "np.ndarray":
    """A: columns are signatures (all living ships if ids is None), (6, n)."""
```

=== 3.3 ORDERS (orders.py — frozen dataclasses; both players feed one queue) ===

```python
@dataclass(frozen=True)                     # Bible 2.1
class MoveCombination:
    squad: int; coeffs: tuple[float, ...]; diagonal: bool
@dataclass(frozen=True)                     # continuous, built from TRIM axes
class Trim:
    ship_id: int; direction: tuple[float, float, float]
@dataclass(frozen=True)                     # Bible 2.2
class SetIntake:
    ship_id: int; facing: tuple[float, float, float]
@dataclass(frozen=True)                     # Bible 2.3 regimes 1 and 3
class FireSolution:
    group: tuple[int, ...]; target_id: int; throttles: tuple[float, ...]
@dataclass(frozen=True)                     # Bible 2.3 regime 2
class LeastSquaresFire:
    group: tuple[int, ...]; target_id: int
@dataclass(frozen=True)                     # Bible 2.8
class GramSchmidtDrill:
    squad: int
@dataclass(frozen=True)                     # Bible 2.5 / 2.6 row-op missions
class RowOperation:
    kind: str          # "subtract" | "swap" | "scale"
    i: int; j: int; multiplier: float       # row_i <- row_i - m * row_j, etc.
@dataclass(frozen=True)
class BackSubstitute:
    values: tuple[float, ...]               # the Navigator's x, checked by referee
@dataclass(frozen=True)
class BuildShip:
    klass: str
@dataclass(frozen=True)                     # Bible 2.7: deletes a row of A_grid
class JamStation:
    station_id: int
@dataclass(frozen=True)
class AssignSquad:
    ship_ids: tuple[int, ...]; squad: int
```

=== 3.4 EVENTS (events.py — frozen kinds; consumed by campaign/intel/audio) ===

```python
@dataclass(frozen=True)
class Event:
    kind: str
    data: dict      # payload documented per kind below
```

Frozen kind list, version 1 (add = minor bump; rename/remove = forbidden):
RANK_CHANGED {old, new} · SHIP_BUILT {ship_id, klass, rank_increased: bool} ·
SHIP_CAPTURED {ship_id, rank_increased} · SHIELD_DOWN {target_id} ·
SHIELD_PARTIAL {target_id, residual_norm, error_vector} · ORDER_REJECTED
{order, reason, residual} · ALARM_LEVEL {level: float, per_station: list} ·
GATE_VOLUME {volume: float, ok: bool} · DRILL_STEP {squad, step_index,
subtracted_component} · ROWOP_APPLIED {matrix_after} · PIVOT_ZERO {row} ·
SOLVED {context_id} · RESOURCE_TICK {amount, cos_theta} · DOCK_PROGRESS
{deviation_angle} · SHIP_LOST {ship_id, cause} · MISSION_FLAG {name, value}.

=== 3.5 THE PULSE (sim.py) — fixed system order, frozen ===

```python
class FleetSim:
    def __init__(self, seed: int, content: "ContentDB") -> None: ...
    def submit(self, order) -> None: ...          # queue; validated at tick
    def tick(self, dt: float) -> list[Event]:
        """Exactly one pulse. System order (FROZEN — determinism depends on it):
        1. store prev_pos for all ships
        2. ingest & validate queued orders (invalid -> ORDER_REJECTED, Rule 3:
           rejection explains, never punishes)
        3. movement: Trim integration + MoveCombination path following
        4. drills: advance Gram-Schmidt animations one step per pulse
        5. harvest: for each collector, rate = rho * max(0, f @ u)
        6. combat: resolve FireSolution / LeastSquaresFire via referee
        7. sensors: alarm level = k * ||A_grid @ p|| per cloaked ship
        8. structure: recompute fleet rank if columns changed; gate volume if
           gate active; Gram matrix penalty if formation bonus active
        9. emit events; return them"""
    def snapshot(self) -> "FleetSnapshot": ...
    def save(self, path: str) -> None: ...        # JSON; between missions only
    @staticmethod
    def load(path: str, content) -> "FleetSim": ...
```

FleetSnapshot (snapshot.py): a frozen dataclass with COPIED numpy arrays —
ship ids, klasses, pos, prev_pos, facing, hp, fuel, squads; fleet matrix A;
resources; rank; active mission-context readouts (grid matrix, alarm, gate
volume, augmented matrix, shield vectors). forge and bridge read ONLY this.
fleet never imports forge, helm, or bridge (enforced by review).

=== 3.6 THE REFEREE (referee.py) — canonical verdict functions ===

This file is the mathematical conscience of the game (Bible Iron Rule 4). Every
module that needs a verdict imports THESE functions; nobody reimplements them.
Signatures and cores are frozen:

```python
import numpy as np
TOL_RANK = 1e-6      # relative, on singular values
TOL_IMAG = 1e-9

def rank(A: np.ndarray) -> int:
    s = np.linalg.svd(A, compute_uv=False)
    if s.size == 0 or s[0] <= 0.0: return 0
    return int(np.sum(s > TOL_RANK * s[0]))

def is_solvable(A: np.ndarray, b: np.ndarray) -> bool:
    return rank(A) == rank(np.column_stack([A, b]))     # Strang Ch. 2/3

def residual(A: np.ndarray, x: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(A @ x - b))

def least_squares(A: np.ndarray, b: np.ndarray):
    x_hat, *_ = np.linalg.lstsq(A, b, rcond=None)
    e = b - A @ x_hat
    return x_hat, e, float(np.linalg.norm(e))           # Strang 4.2-4.3

def nullspace_basis(A: np.ndarray) -> np.ndarray:
    """Columns span N(A). Empty (n,0) array if nullspace is {0}."""
    U, s, Vt = np.linalg.svd(A)
    r = rank(A)
    return Vt[r:].T                                     # Strang 3.2

def in_nullspace(A: np.ndarray, x: np.ndarray, eps: float) -> tuple[bool, float]:
    level = float(np.linalg.norm(A @ x))
    return level < eps, level                           # level feeds the alarm

def spanned_volume(V: np.ndarray) -> float:
    """V is 3x3 (three column vectors) -> |det|; 3x2 -> parallelogram area."""
    if V.shape[1] == 3: return float(abs(np.linalg.det(V)))
    return float(np.linalg.norm(np.cross(V[:, 0], V[:, 1])))   # Strang Ch. 5

def real_eigen_axis(T: np.ndarray) -> np.ndarray:
    """The real eigenvector of a 3D rotation-like T (docking, Bible 2.11)."""
    w, V = np.linalg.eig(T)
    i = int(np.argmin(np.abs(w.imag) + np.abs(w.real - 1.0)))
    v = V[:, i].real
    return v / np.linalg.norm(v)

def weak_axis(S: np.ndarray) -> tuple[np.ndarray, float]:
    """Symmetric S -> (unit eigenvector of smallest eigenvalue, that value)."""
    w, Q = np.linalg.eigh(S)                            # Strang 6.3-6.4
    return Q[:, 0], float(w[0])

def gram_penalty(Q: np.ndarray) -> float:
    G = Q.T @ Q
    return float(np.sum((G - np.eye(G.shape[1])) ** 2)) # Strang 4.4

def cr_factor(A: np.ndarray) -> tuple[np.ndarray, np.ndarray, list[int]]:
    """Greedy independent-column selection using rank(); returns (C, R, kept):
    for each column j in order: keep it iff rank of kept-so-far increases.
    R solved per column by least squares on C. Exact for book-sized fleets."""

def svd_partial(G: np.ndarray, k: int) -> tuple[np.ndarray, float]:
    """Rank-k image and captured energy fraction (Guidestone, Bible 2.14):
    G_k = U[:, :k] @ diag(s[:k]) @ Vt[:k];  energy = sum(s[:k]^2)/sum(s^2)."""
```

Mathematical notes for readers: is_solvable implements "b is reachable iff
adding b as a column does not raise the rank", i.e., $b \in C(A)$. The
nullspace basis comes from the SVD $A = U \Sigma V^T$: the right singular
vectors $v_{r+1}, \ldots, v_n$ (rows $r$ and beyond of $V^T$) satisfy
$A v_i = 0$. The alarm level in in_nullspace is exactly the Bible's
$\|A p\|$ meter.

---------------------------------------------------------------------------------
PART 4 — APP.PY: WIRING AND THE FRAME LIFECYCLE
---------------------------------------------------------------------------------

app.py stays under ~150 lines forever. Its only jobs: load settings.json, build
the four objects, install the crash handler, define tick and frame, run.

```python
def main():
    settings = load_settings("settings.json")
    forge = Forge(settings)
    helm = Helm(settings); helm.attach(forge.window)
    content = ContentDB("content/")            # Apocrypha module (stub for now)
    fleet = FleetSim(settings.get("seed", 1234), content)
    pilot = PilotController(fleet, forge.camera)    # thin translators; will
    nav   = NavigatorStub()                          # move into bridge later

    def tick(dt):
        events, axes, pointer = helm.poll()
        pilot.apply(events, axes, dt)          # axes -> camera + Trim orders;
                                               # buttons -> selection + orders
        nav.apply(pointer)                     # bridge consumes this (Apocrypha)
        for ev in fleet.tick(dt):
            route_event(ev)                    # -> campaign/intel/audio later

    def frame(alpha):
        axes = helm.poll_axes_only()           # smooth camera between pulses
        pilot.smooth_camera(axes)
        scene_sync(fleet.snapshot(), alpha)    # update VObjects (see below)
        forge.set_debug_lines(debug_lines(fleet))

    forge.run(tick, frame)

if __name__ == "__main__":
    run_with_crashlog(main)                    # writes crashlog.txt on failure
```

scene_sync contract: a dict ship_id -> {WireMesh, Trail, Label} is kept; ships
appearing in the snapshot get VObjects created; dead ships get theirs removed;
positions set to $p_{\text{prev}} + \alpha (p - p_{\text{prev}})$. Mission
visuals (grids, nullspace lines, spanned boxes, ellipsoids) are owned by
campaign (Apocrypha) via the same pattern. Nothing else may mutate the scene.

---------------------------------------------------------------------------------
PART 5 — INTERFACES.md v1.0 (COMMIT THIS TEXT AS THE FROZEN CONTRACT)
---------------------------------------------------------------------------------

```
INTERFACES v1.0 — changes require owner approval + version bump.

forge: Forge(settings); .window; .camera; .add(vob); .remove(vob);
  .set_debug_lines(list[str]); .screenshot(path?) -> str;
  .run(tick_cb(dt), frame_cb(alpha))
  Camera: .mode; .set_orbit(t); .orbit_input(dyaw,dpitch,dzoom);
  .set_follow(get_pos); .set_pov(get_pos, get_forward); .view(); .proj(aspect);
  .eye()
  VObjects: Line, Arrow, DashedLine, Grid, WireSphere, WireMesh, SpannedBox,
  Ellipsoid, Trail, Label, ImagePanel — constructors as in NEW_TESTAMENT 1.4;
  all have .visible, .color, .glow, .set_color(); each set_data copies input.

helm: ACTIONS_VERSION=1; PILOT_AXES, PILOT_BUTTONS, SYSTEM_BUTTONS as listed in
  NEW_TESTAMENT 2.2; ActionEvent(action, value); PointerState(x, y, primary,
  secondary, wheel); Helm(settings); .attach(window);
  .poll() -> (list[ActionEvent], dict[str,float], PointerState);
  .poll_axes_only() -> dict[str,float]
  Mapper protocol: .attach(window); .poll_events(); .poll_axes();
  .poll_pointer()

fleet: FleetSim(seed, content); .submit(order); .tick(dt) -> list[Event];
  .snapshot() -> FleetSnapshot; .formation_matrix(ids); .fleet_matrix(ids?);
  .save(path); FleetSim.load(path, content)
  Orders and Event kinds exactly as in NEW_TESTAMENT 3.3 / 3.4 (version 1).
  referee: rank, is_solvable, residual, least_squares, nullspace_basis,
  in_nullspace, spanned_volume, real_eigen_axis, weak_axis, gram_penalty,
  cr_factor, svd_partial — signatures as in NEW_TESTAMENT 3.6.

Import law: forge imports nothing from the project. helm imports nothing from
the project. fleet imports nothing from forge/helm/bridge. app.py imports all.
```

---------------------------------------------------------------------------------
PART 6 — ACCEPTANCE DEMOS: TESTING WITH HUMAN EYES ONLY
---------------------------------------------------------------------------------

The project owner cannot read code, so every module ships a runnable demo whose
EXPECTED RESULT is described here in plain words. A module is "done" when its
demo matches this text on the owner's Windows 11 machine.

python -m forge.demo — EXPECTED: a black window titled "FORGE demo v1.0". A
glowing cyan grid plane. A white arrow from the center pointing up-right, slowly
rotating camera around it. A red dashed line. A wireframe sphere. A green
translucent box (SpannedBox) slowly flattening and un-flattening (its volume
label counting down to 0.00 and back — when it reads 0.00 the box is completely
flat). A small grayscale image panel in a corner that sharpens step by step,
looping (this is the Guidestone code path: it shows rank 1, 2, 4, 8, 16 of a
test image). Text label "The origin (0,0,0)" always facing you. Steady 60 fps in
the corner. F12 saves a screenshot; F1 toggles the debug text. Everything glows
softly; overlapping lines get brighter.

python -m helm.demo — EXPECTED: a small window. Every key from the default map
prints one line, e.g. "ACTION ORDER_CONFIRM 1.0" on press and "... 0.0" on
release; holding W prints "AXIS TRIM_Z +1.00" at 10 Hz; moving the mouse prints
"POINTER x=... y=..."; clicking prints primary/secondary; the wheel prints
deltas. Pressing an unmapped key prints nothing and does not crash.

python -m fleet.demo — EXPECTED: no window; a console self-test that recomputes
the Bible's worked examples through the real referee and prints PASS/FAIL:
  1. rank of the 2x3 matrix with columns (2,0),(1,3),(3,3) == 2 ....... PASS
  2. cr_factor keeps columns [0,1] and R's third column == (1,1) ...... PASS
  3. shield solve: A_g columns (2,0),(1,3), b=(7,6) -> x=(2.5,2.0) .... PASS
  4. nullspace of rows (1,1,0),(0,1,1) is spanned by +-(1,-1,1)/sqrt3 . PASS
  5. jamming row 2 grows nullspace dimension 1 -> 2 ................... PASS
  6. least squares pings (0,6),(1,0),(2,0) -> (C,D)=(5,-3) ............ PASS
  7. det of columns (2,0,0),(0,3,0),(1,1,1) == 6 ...................... PASS
  8. swarm matrix [[0.8,0.3],[0.2,0.7]] dominant eigenvector ~ (3,2) .. PASS
  9. weak axis of [[5,4],[4,5]] is +-(1,-1)/sqrt2, eigenvalue 1 ....... PASS
 10. svd_partial: energy fraction increases with k, reaches 1.0 ....... PASS
 11. determinism: two sims, same seed+orders, identical after 100 ticks PASS
 12. 100 pulses with 20 ships in < 0.5 s (performance floor) .......... PASS
FLEET SELF-TEST PASSED (12/12)

These twelve lines are the project's regression suite: after ANY change to
fleet or referee, the demo must still print 12/12. The demos are the owner's
window into correctness — they must never be deleted, only extended.

---------------------------------------------------------------------------------
BUILD SEQUENCE FOR THESE THREE MODULES (each step is one child-sized package)
---------------------------------------------------------------------------------

1. forge/app.py + camera.py + shaders.py: black window, camera math, one
   hardcoded triangle. 2. batches.py + Line/Arrow/Grid: the glowing grid and
   the first arrow from the origin (celebrate this). 3. bloom.py. 4. remaining
   VObjects + text.py + demo.py to full acceptance. 5. helm complete + demo
   (small). 6. fleet ships/orders/events/sim skeleton with movement + trim.
   7. referee.py + the 12-line self-test. 8. harvest/combat/sensors/structure
   systems. 9. app.py wiring: three ships flying combination orders live on
   screen. That is the moment the Bible's Mission 1 becomes buildable.

END OF THE NEW TESTAMENT. Next: the APOCRYPHA — campaign + content pipeline
(missions as data, the book-excerpt format), bridge (Navigator console + Big
Picture), intel (narrator), audio, and the Guidestone subsystem.
