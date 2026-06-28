# QUAKE — Parent 8 Part B Deliverable (3D Map Viewer)

> Verbatim answer from Claude Opus 4.8 (Parent 8), June 28, 2026. Saved word-for-word by DeepSeek.

---

Excellent — Option 1 confirmed, both floorplans exist (including one with a real crossing to verify bridges render). Building now. 🗺️✈️

Here's the complete deliverable.

## tools/map_viewer.py

```python
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
from math import cos, pi, sin
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

    keys = pyglet_key.KeyStateHandler()
    window.push_handlers(keys)

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

    def update(dt: float) -> None:  # noqa: ANN001
        boost = FLY_BOOST_MULT if (
            keys[pyglet_key.LSHIFT] or keys[pyglet_key.RSHIFT]
        ) else 1.0
        step = FLY_SPEED_MPS * boost * dt
        look = LOOK_SPEED_RADPS * dt

        fwd = (1.0 if keys[pyglet_key.W] else 0.0) - (1.0 if keys[pyglet_key.S] else 0.0)
        strafe = (1.0 if keys[pyglet_key.D] else 0.0) - (1.0 if keys[pyglet_key.A] else 0.0)
        rise = (1.0 if keys[pyglet_key.E] else 0.0) - (1.0 if keys[pyglet_key.Q] else 0.0)
        if fwd or strafe or rise:
            cam.move(fwd * step, strafe * step, rise * step)

        d_yaw = (1.0 if keys[pyglet_key.RIGHT] else 0.0) - (1.0 if keys[pyglet_key.LEFT] else 0.0)
        d_pitch = (1.0 if keys[pyglet_key.UP] else 0.0) - (1.0 if keys[pyglet_key.DOWN] else 0.0)
        if d_yaw or d_pitch:
            cam.add_look(d_yaw * look, d_pitch * look)

    @window.event
    def on_draw():  # noqa: ANN001
        window.clear()
        view = cam.view_matrix()
        # Reuse the verified Mode-A wire path. draw_graph honors per-corridor
        # cruise_y, so bridges/underpasses appear at their true heights.
        draw_graph(view, fp, state)

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
```

## tests/test_map_viewer.py

```python
"""Parent 8 — headless-safe tests for the map viewer's PURE core.

We test FlyCamera math + floorplan stats + the scale-free initial vantage.
NO hardcoded level sizes: floorplans are generated at parametrized sizes, and
all assertions are graph-relative.

GL/window code (run/on_draw) is NOT tested here — it needs a context and is the
thin shell. We assert it correctly refuses to run headless instead.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from contracts import Floorplan, FloorRoom, Corridor, Crossing
from tools.map_viewer import (
    FlyCamera,
    compute_stats,
    initial_camera,
    load_floorplan,
    run,
    PITCH_LIMIT_RAD,
)
from glguard import HAVE_GL


# --------------------------------------------------------------------------- #
# Generated floorplans of arbitrary size — no magic counts.                   #
# --------------------------------------------------------------------------- #
def _make_floorplan(n_rooms: int, n_crossings: int = 0) -> Floorplan:
    rooms = []
    for i in range(n_rooms):
        rooms.append(
            FloorRoom(
                room_id=f"n{i}",
                map_xz=(float(i) * 10.0, float(-i) * 7.0),
                importance=1 + (i % 5),
                map_radius_m=2.0 + (i % 5),
                map_color="#4f6d7a",
                socket_y=0.0,
            )
        )
    corridors = []
    for i in range(max(0, n_rooms - 1)):
        layer = i % 3
        corridors.append(
            Corridor(
                corridor_id=f"edge.n{i}.to.n{i + 1}",
                source=f"n{i}",
                target=f"n{i + 1}",
                height_level=layer,
                cruise_y=float(layer) * 3.0,
                path_xz=[rooms[i].map_xz, rooms[i + 1].map_xz],
                width_m=3.0,
            )
        )
    crossings = []
    for j in range(n_crossings):
        crossings.append(
            Crossing(
                crossing_id=f"crossing_{j}",
                over_corridor=f"edge.n{j}.to.n{j + 1}",
                under_corridor=f"edge.n{j + 1}.to.n{j + 2}",
                at_xz=(float(j), float(-j)),
                over_y=6.0,
                under_y=3.0,
            )
        )
    return Floorplan(
        schema_version="1.0",
        level_id="gen_level",
        seed=1,
        rooms=rooms,
        corridors=corridors,
        crossings=crossings,
    )


SIZES = [1, 2, 3, 5, 8, 20, 55]


# --------------------------------------------------------------------------- #
# FlyCamera pure math                                                         #
# --------------------------------------------------------------------------- #
def test_view_matrix_shape_dtype_and_convention():
    """view_matrix must be the (4,4) float32 row-major matrix draw_graph wants,
    byte-identical in convention to camera.look_at."""
    from camera import look_at

    cam = FlyCamera()
    cam.pos = np.array([1.0, 2.0, 3.0])
    cam.yaw = 0.5
    cam.pitch = -0.2
    m = cam.view_matrix()

    assert m.shape == (4, 4)
    assert m.dtype == np.float32
    assert m.flags["C_CONTIGUOUS"]  # row-major memory

    # Same as look_at(eye, eye+forward, up) by construction.
    eye = cam.pos
    target = cam.pos + cam.forward()
    expected = look_at(eye, target, np.array([0.0, 1.0, 0.0]))
    assert np.allclose(m, expected)


def test_forward_uses_frozen_compass():
    """yaw=0, pitch=0 -> forward (1,0,0) = +X east. yaw=pi/2 -> +Z north."""
    cam = FlyCamera()
    cam.yaw = 0.0
    cam.pitch = 0.0
    assert np.allclose(cam.forward(), [1.0, 0.0, 0.0], atol=1e-6)

    cam.yaw = math.pi / 2.0
    assert np.allclose(cam.forward(), [0.0, 0.0, 1.0], atol=1e-6)


def test_move_forward_changes_position_along_look():
    cam = FlyCamera()
    cam.yaw = 0.0  # facing +X
    cam.pitch = 0.0
    start = cam.pos.copy()
    cam.move(forward_amt=5.0, right_amt=0.0, up_amt=0.0)
    delta = cam.pos - start
    assert np.allclose(delta, [5.0, 0.0, 0.0], atol=1e-6)


def test_strafe_is_horizontal_regardless_of_pitch():
    """right() ignores pitch -> strafing never changes Y even when looking up."""
    cam = FlyCamera()
    cam.yaw = 0.0
    cam.pitch = 1.0  # looking steeply up
    start = cam.pos.copy()
    cam.move(forward_amt=0.0, right_amt=3.0, up_amt=0.0)
    delta = cam.pos - start
    assert abs(delta[1]) < 1e-9  # no vertical drift from strafe


def test_up_is_pure_world_y():
    cam = FlyCamera()
    cam.yaw = 1.234
    cam.pitch = 0.7
    start = cam.pos.copy()
    cam.move(forward_amt=0.0, right_amt=0.0, up_amt=4.0)
    delta = cam.pos - start
    assert np.allclose(delta, [0.0, 4.0, 0.0], atol=1e-9)


def test_pitch_is_clamped_to_gimbal_guard():
    cam = FlyCamera()
    cam.add_look(0.0, 100.0)   # try to look way past straight up
    assert cam.pitch <= PITCH_LIMIT_RAD + 1e-12
    cam.add_look(0.0, -100.0)
    assert cam.pitch >= -PITCH_LIMIT_RAD - 1e-12


def test_yaw_wraps_and_stays_finite():
    cam = FlyCamera()
    for _ in range(1000):
        cam.add_look(0.1, 0.0)
    assert math.isfinite(cam.yaw)
    assert 0.0 <= cam.yaw < 2.0 * math.pi + 1e-9


# --------------------------------------------------------------------------- #
# Floorplan stats + scale-free initial vantage                                #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("n", SIZES)
def test_stats_counts_match_floorplan(n):
    fp = _make_floorplan(n)
    stats = compute_stats(fp)
    assert stats.n_rooms == len(fp.rooms)
    assert stats.n_corridors == len(fp.corridors)
    assert stats.n_crossings == len(fp.crossings)
    assert stats.extent >= 1.0
    assert np.all(np.isfinite(stats.center))


@pytest.mark.parametrize("n", SIZES)
def test_initial_camera_is_outside_bbox_and_finite(n):
    """The starting vantage scales with the layout (no magic size) and sits
    back from the content so the whole level is in frame."""
    fp = _make_floorplan(n)
    stats = compute_stats(fp)
    cam = initial_camera(stats)
    assert np.all(np.isfinite(cam.pos))
    assert math.isfinite(cam.yaw) and math.isfinite(cam.pitch)
    # Camera should be pulled back/up relative to extent (scale-relative check).
    assert cam.pos[1] >= stats.center[1]  # above center
    # Distance from center grows with extent (no fixed constant asserted).
    dist = float(np.linalg.norm(cam.pos - stats.center))
    assert dist >= stats.extent  # at least one extent away


def test_crossings_drive_flat_note_logic():
    """A 0-crossing layout is distinguishable from one with crossings via the
    same field the HUD reads — this is Nir's 'is it flat?' cue."""
    flat = compute_stats(_make_floorplan(5, n_crossings=0))
    bridged = compute_stats(_make_floorplan(5, n_crossings=2))
    assert flat.n_crossings == 0
    assert bridged.n_crossings == 2


def test_single_room_does_not_crash():
    fp = _make_floorplan(1)
    stats = compute_stats(fp)
    cam = initial_camera(stats)
    assert np.all(np.isfinite(cam.pos))


# --------------------------------------------------------------------------- #
# Shell guard                                                                 #
# --------------------------------------------------------------------------- #
@pytest.mark.skipif(HAVE_GL, reason="only meaningful when no GL is present")
def test_run_refuses_headless(tmp_path):
    """run() must raise (not segfault/hang) when there is no GL context."""
    fp = _make_floorplan(3)
    p = tmp_path / "floorplan.json"
    p.write_text(fp.model_dump_json(), encoding="utf-8")
    with pytest.raises(RuntimeError):
        run(p)


def test_load_floorplan_roundtrip(tmp_path):
    fp = _make_floorplan(8, n_crossings=1)
    p = tmp_path / "floorplan.json"
    p.write_text(fp.model_dump_json(), encoding="utf-8")
    loaded = load_floorplan(p)
    assert loaded.level_id == fp.level_id
    assert len(loaded.rooms) == len(fp.rooms)
    assert len(loaded.crossings) == len(fp.crossings)
```

## CHANGELOG (Part B)

New file tools/map_viewer.py — standalone 3D wireframe map-viewer.

    Thin wrapper over the verified Mode-A render core: gfx_context.make_window (inherits the depth-on / blend-off Mode-A invariant), then render_wire.draw_graph(view, fp, state) per frame. Because draw_graph honors each corridor's cruise_y, bridges/underpasses render at their true heights for free — no new geometry code.
    FlyCamera (pure) built on camera.forward_from_angles + camera.look_at, so it shares the frozen compass (+X=east, +Z=north, Y=up) and the exact row-major / column-vector matrix convention draw_graph expects (the transpose-on-upload in render_wire undoes it identically to the game camera). I deliberately did not reuse the damped game Camera — its heading-only, pitch-clamped policy is the opposite of what a free-fly inspection tool needs — but I reused its math core, so the future in-game map mode can adopt either camera behind one swap.
    Controls (Option 1, self-contained pyglet input): WASD move (forward follows full look; strafe stays horizontal), arrows look, Q/E down/up in world-Y, Shift boost, M toggle mouse-look, R reset to the framed start view, Esc quit.
    Scale-free everywhere: the initial vantage is derived from the layout's own bounding-box extent (compute_stats → initial_camera), so a 3-room fixture and a 200-room level both frame correctly. No node/edge/room count is hardcoded in the viewer or its tests; FAR_M is generous (5000 m) so even an unexpectedly large layout is visible.
    HUD shows rooms / corridors / crossings, height-layer span, camera pose, and bbox — and prints "FLAT (no bridges)" whenever crossings == 0, so the G5 design question (is the 0-crossing Principia layout acceptable?) is visible to Nir's eye the moment he loads it.
    Minimal GameState stub: since draw_graph never reads state (DeepSeek-confirmed), I pass a light duck-typed object exposing the GameState field names — avoiding coupling to SaveGame's schema while staying safe if a future draw_graph ever touches a field.
    Headless-safe: the module imports with no GL; run() raises a clear RuntimeError headless rather than crashing. All pure math is testable without a context.
    Any floorplan: path is a CLI arg, validated through the frozen Floorplan pydantic model.

New file tests/test_map_viewer.py — headless-safe pure-core tests (no magic level sizes).

    FlyCamera: view-matrix shape/dtype/row-major + convention equality with camera.look_at; frozen-compass forward; forward-move along look; horizontal strafe regardless of pitch; pure-Y up; pitch gimbal clamp; yaw wrap/finiteness.
    Stats/vantage: counts match the floorplan across parametrized sizes [1,2,3,5,8,20,55]; the initial camera is finite, above center, and at least one extent away (scale-relative, no constant); single-room doesn't crash; the crossings-count field that drives the "FLAT" HUD note behaves.
    Shell guard: run() raises headless (skipped when GL is present); floorplan load round-trips.

Files NOT touched: every engine module and every contract. The viewer is pure-presentation and never mutates a floorplan.

## Run instructions (for Nir)

Two things to fly through:

python -m tools.map_viewer quake/tests/golden_pack/floorplan.json

→ the 3-room golden fixture with 1 real crossing — your bridge sanity check. Fly underneath/over the crossing; you should clearly see one corridor pass over another at a different height. If that reads correctly, the viewer's height rendering is trustworthy.

python -m tools.map_viewer quake/levels/principia_bk1_inverse_square/floorplan.json

→ the real 20-node Principia layout. The HUD will say crossings: 0  FLAT (no bridges). Fly around it and judge with your eyes: does this read as a beautiful walkable concept-graph, or does it feel too flat for the Quake fantasy?

Controls: WASD fly · arrows look · Q/E down/up · Shift boost · M mouse-look · R reset view · Esc quit.

## The honest design moment this hands back to you, Nir

Part B's whole purpose is to put this decision in your eyes, not in code:

    The engine is now correct (Part A: 358/358 green, in-bounds, scale-free).
    On Newton's real graph it produces 0 crossings — valid, but flat, which is in mild tension with the OT invariant that "crossings are a feature" and the reason this is true-3D Quake at all.

This is exactly the §12 boundary: not an engine bug — a graph-shape / aesthetic call. Once you've flown both maps, you (and DeepSeek) can decide among levers that don't touch the engine's correctness: tune LayoutConfig.k_factor, try other seeds, or let a future parent revisit Parent 7's dependency edges. None of that is my mandate now — my job was to make the machine robust and give you 3D eyes, and both are delivered.

## Hand-off note for DeepSeek

    Drop tools/map_viewer.py + tests/test_map_viewer.py in; run the suite. I expect the new pure-core tests green and zero regressions (the viewer touches no engine/contract).
    Then please confirm G6 by eye with Nir: load the golden fixture first (verify the single crossing reads as a true over/under bridge), then the Principia layout (verify free-fly works and the "FLAT" note shows).
    If pyglet 2.1.x flags any exact-API slips (KeyStateHandler, set_exclusive_mouse, pyglet.text.Label kwargs, schedule_interval), they're isolated in the shell — the compile/run loop fixes them in one place without touching the pure core. I avoided asserting their signatures from memory per the rules; flag me anything that doesn't match and I'll correct it.

That completes the Parent 8 mission: Part A (robust, scale-free engine + general tests) and Part B (free-fly 3D map viewer, the seed of in-game map mode). 🗝️✈️
