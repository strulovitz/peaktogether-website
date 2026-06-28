"""tools/map_viewer.py — QUAKE build-time 3D map-viewer utility (Parent 8, Part B).

Loads ANY floorplan.json and renders it as a navigable 3D wireframe so a human
can FLY around and inspect the whole level — rooms, corridors, and the
bridges/underpasses at their true heights. This is (1) Nir's eyes on a layout
before rooms are built, and (2) the seed of the future in-game "map mode".

DESIGN (confirmed with DeepSeek):
  * THIN WRAPPER over the real Mode-A render core:
      - gfx_context.make_window  -> window + ctx with the Mode-A GL invariant
        (depth test ON, LEQUAL, depth write ON, BLEND OFF) already applied.
      - render_wire.draw_graph(view, fp, state) -> the verified wire path
        (build_wire_mesh + line-quads + distance dimming + per-level GL cache).
      - draw_graph never reads `state`, so a minimal stub GameState is passed.
  * FREE-FLY CAMERA built on camera.py's PURE math (forward_from_angles +
    look_at) so it shares the EXACT compass (+X=east, +Z=north, Y=up) and the
    EXACT row-major / column-vector matrix convention draw_graph expects.
    We do NOT reuse the damped game `Camera` (heading-only, pitch-clamped) —
    a map tool needs free fly-anywhere/look-anywhere, the opposite of comfort
    damping. We reuse its math core, not its policy.
  * SELF-CONTAINED INPUT (Option 1): reads pyglet key/mouse directly. The
    graduation into in-game map mode is a clean one-function swap to
    input_actions later.
  * NO HARDCODED LEVEL SIZES anywhere. Any floorplan, any node/edge count.
  * HEADLESS-SAFE: guarded by glguard.HAVE_GL; importing this module never
    needs a GL context. The pure FlyCamera math is fully testable headless.

COORDINATES ARE LAW: floorplan is the XZ map-plane, Y up. Heading theta ->
forward (cos theta, 0, sin theta); +X=east, +Z=north.

Run:
    python -m tools.map_viewer quake/levels/principia_bk1_inverse_square/floorplan.json
    python -m tools.map_viewer quake/tests/golden_pack/floorplan.json
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from math import cos, pi, sin, tan
from pathlib import Path

import numpy as np

# Pure math reused from the game camera (compass + matrix convention).
from camera import forward_from_angles, look_at
from contracts import Floorplan
from glguard import HAVE_GL


# --------------------------------------------------------------------------- #
# PINNED VIEWER CONSTANTS (tool-local; not game constants).                   #
# All are *rates/ratios*, never level sizes — the viewer is scale-free.       #
# --------------------------------------------------------------------------- #
WINDOW_W = 1280
WINDOW_H = 800
WINDOW_TITLE = "QUAKE — Map Viewer (build tool)"

FLY_SPEED_MPS = 18.0          # base translate speed (m/s)
FLY_BOOST_MULT = 4.0          # hold Shift to fly fast
LOOK_SPEED_RADPS = 1.8        # arrow-key look rate (rad/s)
MOUSE_LOOK_GAIN = 0.0032      # rad per pixel of mouse motion
PITCH_LIMIT_RAD = (pi / 2.0) - 0.01   # avoid gimbal flip at straight up/down

FOV_Y_DEG = 60.0
NEAR_M = 0.1
FAR_M = 5000.0                # generous: the tool must see any-scale layouts


def _perspective_matrix(fov_y_deg: float, aspect: float, near: float, far: float) -> np.ndarray:
    """Right-handed perspective projection matrix (column-vector convention).

    Returns (4,4) float32 row-major.  fov_y in degrees.  aspect = width/height.
    """
    f = 1.0 / tan(fov_y_deg * pi / 360.0)
    m = np.zeros((4, 4), dtype=np.float64)
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = (2.0 * far * near) / (near - far)
    m[3, 2] = -1.0
    return np.ascontiguousarray(m, dtype=np.float32)


# --------------------------------------------------------------------------- #
# PURE CORE — FlyCamera. No GL, no window, no IO. Fully headless-testable.     #
# --------------------------------------------------------------------------- #
@dataclass
class FlyCamera:
    """Free-fly inspection camera.

    State: world position (x, y, z), yaw (heading), pitch. Unlike the game
    camera there is NO damping and NO pitch clamp beyond a gimbal guard — this
    is a tool for getting to any vantage point.

    Compass matches camera.forward_from_angles exactly:
      forward = (cos(pitch)cos(yaw), sin(pitch), cos(pitch)sin(yaw))
      +X=east, +Z=north, Y=up.
    """

    pos: np.ndarray = field(
        default_factory=lambda: np.zeros(3, dtype=np.float64)
    )
    yaw: float = 0.0
    pitch: float = 0.0

    # ---- pure math ----
    def forward(self) -> np.ndarray:
        """Unit forward vector (float64)."""
        return forward_from_angles(self.yaw, self.pitch).astype(np.float64)

    def right(self) -> np.ndarray:
        """Unit right vector on the XZ plane (ignores pitch), for strafing.

        right = forward_flat x up, normalized. Using the FLAT forward keeps
        WASD strafing horizontal regardless of look pitch (comfortable fly).
        """
        fwd_flat = np.array((cos(self.yaw), 0.0, sin(self.yaw)), dtype=np.float64)
        up = np.array((0.0, 1.0, 0.0), dtype=np.float64)
        r = np.cross(fwd_flat, up)
        norm = np.linalg.norm(r)
        if norm < 1e-12:
            return np.array((1.0, 0.0, 0.0), dtype=np.float64)
        return r / norm

    def add_look(self, d_yaw: float, d_pitch: float) -> None:
        """Apply a look delta, clamping pitch to the gimbal guard."""
        self.yaw = (self.yaw + d_yaw) % (2.0 * pi)
        self.pitch = _clamp(self.pitch + d_pitch, -PITCH_LIMIT_RAD, PITCH_LIMIT_RAD)

    def move(
        self,
        forward_amt: float,
        right_amt: float,
        up_amt: float,
    ) -> None:
        """Translate by amounts (meters) along forward(full), right(flat), worldY.

        forward uses the FULL pitched forward so W/S fly toward where you look;
        up_amt is pure world-Y (Q/E) so you can rise/fall independent of look.
        """
        self.pos = (
            self.pos
            + self.forward() * forward_amt
            + self.right() * right_amt
            + np.array((0.0, up_amt, 0.0), dtype=np.float64)
        )

    def view_matrix(self) -> np.ndarray:
        """Return the (4,4) float32 row-major view matrix draw_graph expects.

        Built via camera.look_at so the convention is byte-identical to the
        game camera — the transpose-on-upload in render_wire undoes the
        column-vector convention exactly as it does for the real camera.
        """
        eye = self.pos
        target = self.pos + self.forward()
        up = np.array((0.0, 1.0, 0.0), dtype=np.float64)
        return look_at(eye, target, up)


def _clamp(x: float, lo: float, hi: float) -> float:
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


# --------------------------------------------------------------------------- #
# PURE CORE — floorplan stats + a good initial vantage (scale-free).          #
# --------------------------------------------------------------------------- #
@dataclass
class FloorplanStats:
    n_rooms: int
    n_corridors: int
    n_crossings: int
    min_layer: int
    max_layer: int
    bbox_min: tuple[float, float, float]
    bbox_max: tuple[float, float, float]
    center: np.ndarray
    extent: float          # largest span across X/Y/Z


def compute_stats(fp: Floorplan) -> FloorplanStats:
    """Derive everything the HUD + initial camera need from the data alone.

    Scale-free: the start vantage is a function of the layout's own extent, so
    a 3-room fixture and a 200-room level both frame nicely.
    """
    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []

    for room in fp.rooms:
        xs.append(float(room.map_xz[0]))
        zs.append(float(room.map_xz[1]))
        ys.append(float(room.socket_y))

    for cor in fp.corridors:
        for (px, pz) in cor.path_xz:
            xs.append(float(px))
            zs.append(float(pz))
        ys.append(float(cor.cruise_y))

    for cr in fp.crossings:
        ys.append(float(cr.over_y))
        ys.append(float(cr.under_y))

    if not xs:
        xs = [0.0]
    if not ys:
        ys = [0.0]
    if not zs:
        zs = [0.0]

    bbox_min = (min(xs), min(ys), min(zs))
    bbox_max = (max(xs), max(ys), max(zs))
    center = np.array(
        [
            (bbox_min[0] + bbox_max[0]) * 0.5,
            (bbox_min[1] + bbox_max[1]) * 0.5,
            (bbox_min[2] + bbox_max[2]) * 0.5,
        ],
        dtype=np.float64,
    )
    extent = max(
        bbox_max[0] - bbox_min[0],
        bbox_max[1] - bbox_min[1],
        bbox_max[2] - bbox_min[2],
        1.0,  # floor so a single-point layout still gets a usable vantage
    )

    layers = [int(c.height_level) for c in fp.corridors]
    min_layer = min(layers) if layers else 0
    max_layer = max(layers) if layers else 0

    return FloorplanStats(
        n_rooms=len(fp.rooms),
        n_corridors=len(fp.corridors),
        n_crossings=len(fp.crossings),
        min_layer=min_layer,
        max_layer=max_layer,
        bbox_min=bbox_min,
        bbox_max=bbox_max,
        center=center,
        extent=extent,
    )


def initial_camera(stats: FloorplanStats) -> FlyCamera:
    """A pleasant starting vantage: pulled back and up, looking at the center.

    Position and look are derived from the layout extent — NO magic level size.
    """
    cam = FlyCamera()
    # Stand back ~1.6x the extent on -Z, up ~0.9x the extent, look at center.
    back = stats.extent * 1.6
    up = stats.extent * 0.9
    cam.pos = np.array(
        [stats.center[0], stats.center[1] + up, stats.center[2] - back],
        dtype=np.float64,
    )
    # Aim at center: yaw toward +Z-ish, pitch downward.
    to_center = stats.center - cam.pos
    horiz = float(np.hypot(to_center[0], to_center[2]))
    cam.yaw = float(np.arctan2(to_center[2], to_center[0]))  # atan2(z, x): +X east, +Z north
    cam.pitch = float(np.arctan2(to_center[1], horiz)) if horiz > 1e-9 else 0.0
    cam.pitch = _clamp(cam.pitch, -PITCH_LIMIT_RAD, PITCH_LIMIT_RAD)
    return cam


# --------------------------------------------------------------------------- #
# PURE CORE — a minimal GameState stub (draw_graph never reads it).           #
# --------------------------------------------------------------------------- #
def _stub_game_state(fp: Floorplan):
    """draw_graph accepts `state` but never reads it (confirmed by DeepSeek).

    We build the lightest possible object exposing the GameState field names,
    so even if a future draw_graph touches one it won't AttributeError. We do
    NOT import/construct SaveGame (would couple us to its schema); a duck-typed
    object is sufficient for a build tool and keeps coupling minimal.
    """

    @dataclass
    class _StubState:
        mode: str = "corridor"
        current_room_id: str | None = None
        pos: tuple[float, float, float] = (0.0, 0.0, 0.0)
        heading_rad: float = 0.0
        pitch_rad: float = 0.0
        lit: set = field(default_factory=set)
        cleared: set = field(default_factory=set)
        save: object = None

    return _StubState()


# --------------------------------------------------------------------------- #
# THIN SHELL — window, input, draw loop. Guarded by HAVE_GL.                   #
# --------------------------------------------------------------------------- #
def load_floorplan(path: Path) -> Floorplan:
    """Validate-load any floorplan.json against the frozen Floorplan model."""
    text = Path(path).read_text(encoding="utf-8")
    return Floorplan.model_validate_json(text)


def run(floorplan_path: Path) -> int:
    """Open the viewer on a floorplan. Returns an exit code.

    Requires GL; raises RuntimeError headless (the pure core is testable
    without this).
    """
    if not HAVE_GL:
        raise RuntimeError(
            "map_viewer.run requires a GL context (glguard.HAVE_GL is False). "
            "The pure FlyCamera/stats math is available headless."
        )

    import pyglet
    from pyglet.window import key as pyglet_key

    from gfx_context import make_window
    from render_wire import draw_graph

    fp = load_floorplan(floorplan_path)
    stats = compute_stats(fp)
    cam = initial_camera(stats)
    state = _stub_game_state(fp)

    window, _ctx = make_window(WINDOW_W, WINDOW_H, WINDOW_TITLE)

    # Manual key state tracking (pyglet 2.1.14 KeyStateHandler broken on Windows)
    _pressed: set[int] = set()

    # Mouse-look is opt-in (toggle with M) so the cursor isn't captured by
    # surprise. Tracks exclusive mouse + accumulates motion deltas.
    mouse_look = {"on": False}

    flat_note = "FLAT (no bridges)" if stats.n_crossings == 0 else ""

    hud = pyglet.text.Label(
        "", font_name="Consolas", font_size=12,
        x=10, y=WINDOW_H - 10, anchor_x="left", anchor_y="top",
        multiline=True, width=WINDOW_W - 20, color=(220, 220, 220, 255),
    )
    help_label = pyglet.text.Label(
        "WASD move  ·  arrows look  ·  Q/E down/up  ·  Shift boost  ·  "
        "M mouse-look  ·  R reset view  ·  Esc quit",
        font_name="Consolas", font_size=11,
        x=10, y=10, anchor_x="left", anchor_y="bottom",
        color=(160, 160, 160, 255),
    )

    @window.event
    def on_mouse_motion(x, y, dx, dy):  # noqa: ANN001
        if mouse_look["on"]:
            cam.add_look(dx * MOUSE_LOOK_GAIN, dy * MOUSE_LOOK_GAIN)

    @window.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):  # noqa: ANN001
        # Right/any drag also looks, even without mouse-look toggle.
        cam.add_look(dx * MOUSE_LOOK_GAIN, dy * MOUSE_LOOK_GAIN)

    @window.event
    def on_key_press(symbol, modifiers):  # noqa: ANN001
        _pressed.add(symbol)
        if symbol == pyglet_key.ESCAPE:
            window.close()
        elif symbol == pyglet_key.M:
            mouse_look["on"] = not mouse_look["on"]
            try:
                window.set_exclusive_mouse(mouse_look["on"])
            except Exception:
                pass
        elif symbol == pyglet_key.R:
            fresh = initial_camera(stats)
            cam.pos = fresh.pos
            cam.yaw = fresh.yaw
            cam.pitch = fresh.pitch

    @window.event
    def on_key_release(symbol, modifiers):  # noqa: ANN001
        _pressed.discard(symbol)

    def update(dt: float) -> None:  # noqa: ANN001
        boost = FLY_BOOST_MULT if (
            pyglet_key.LSHIFT in _pressed or pyglet_key.RSHIFT in _pressed
        ) else 1.0
        step = FLY_SPEED_MPS * boost * dt
        look = LOOK_SPEED_RADPS * dt

        fwd = (1.0 if pyglet_key.W in _pressed else 0.0) - (1.0 if pyglet_key.S in _pressed else 0.0)
        strafe = (1.0 if pyglet_key.D in _pressed else 0.0) - (1.0 if pyglet_key.A in _pressed else 0.0)
        rise = (1.0 if pyglet_key.E in _pressed else 0.0) - (1.0 if pyglet_key.Q in _pressed else 0.0)
        if fwd or strafe or rise:
            cam.move(fwd * step, strafe * step, rise * step)

        d_yaw = (1.0 if pyglet_key.RIGHT in _pressed else 0.0) - (1.0 if pyglet_key.LEFT in _pressed else 0.0)
        d_pitch = (1.0 if pyglet_key.UP in _pressed else 0.0) - (1.0 if pyglet_key.DOWN in _pressed else 0.0)
        if d_yaw or d_pitch:
            cam.add_look(d_yaw * look, d_pitch * look)

    @window.event
    def on_draw():  # noqa: ANN001
        window.clear()
        view = cam.view_matrix()
        proj = _perspective_matrix(FOV_Y_DEG, WINDOW_W / WINDOW_H, NEAR_M, FAR_M)
        # view * proj: column-vector convention → world-to-clip
        vp = np.ascontiguousarray(proj @ view, dtype=np.float32)
        # Reuse the verified Mode-A wire path. draw_graph honors per-corridor
        # cruise_y, so bridges/underpasses appear at their true heights.
        draw_graph(vp, fp, state)

        hud.text = (
            f"{floorplan_path.name}\n"
            f"rooms: {stats.n_rooms}   corridors: {stats.n_corridors}   "
            f"crossings: {stats.n_crossings}  {flat_note}\n"
            f"height layers: {stats.min_layer}..{stats.max_layer}\n"
            f"pos: ({cam.pos[0]:+.1f}, {cam.pos[1]:+.1f}, {cam.pos[2]:+.1f})   "
            f"yaw: {cam.yaw:+.2f}  pitch: {cam.pitch:+.2f}\n"
            f"bbox: {tuple(round(v, 1) for v in stats.bbox_min)} .. "
            f"{tuple(round(v, 1) for v in stats.bbox_max)}"
        )
        # HUD/help drawn after the 3D pass. (Mode-A leaves BLEND off; pyglet
        # labels manage their own GL state for text.)
        hud.draw()
        help_label.draw()

    pyglet.clock.schedule_interval(update, 1.0 / 60.0)
    pyglet.app.run()
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 1:
        sys.stderr.write(
            "usage: python -m tools.map_viewer <path/to/floorplan.json>\n"
        )
        return 2
    path = Path(argv[0])
    if not path.is_file():
        sys.stderr.write(f"map_viewer: file not found: {path}\n")
        return 2
    return run(path)


if __name__ == "__main__":
    raise SystemExit(main())
