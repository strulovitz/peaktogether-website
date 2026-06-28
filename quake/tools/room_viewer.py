"""tools/room_viewer.py — fly INSIDE one Mode B room (lit walls, panels, ceiling).

The Mode-B counterpart of tools/map_viewer.py: loads ONE room from a pack and
lets a human fly around inside it, calling render_room.draw_room every frame.
This is Nir's eyes on Mode B (there is no other interactive way to see a room
yet — the full game app.py runs only a 60-frame smoke and starts in corridor).

Run (from the quake/ directory):
    python -m tools.room_viewer                          # first room of golden pack
    python -m tools.room_viewer r_b                      # a specific room id
    python -m tools.room_viewer r_a tests/golden_pack/   # room id + pack dir

Controls: WASD move · arrows look · Q/E down/up · Shift boost · M mouse-look ·
          C toggle ceiling-red (room cleared) · L toggle panels lit · R reset · Esc quit
"""
from __future__ import annotations

import sys
from math import pi

import numpy as np

from glguard import HAVE_GL
from camera import perspective, FOV_Y_DEG, NEAR_M, FAR_M
from assets import load_pack
import render_room
from tools.map_viewer import (
    FlyCamera, FLY_SPEED_MPS, FLY_BOOST_MULT, LOOK_SPEED_RADPS, MOUSE_LOOK_GAIN,
)

WINDOW_W = 1280
WINDOW_H = 800
WINDOW_TITLE = "QUAKE — Room Viewer (Mode B)"


class _ViewState:
    """Minimal GameState-ish: draw_room only reads .lit and .cleared."""
    def __init__(self):
        self.lit: set = set()
        self.cleared: set = set()


def run(room_id=None, pack_dir="tests/golden_pack/") -> int:
    if not HAVE_GL:
        raise RuntimeError(
            "room_viewer.run requires a GL context (glguard.HAVE_GL is False)."
        )
    import pyglet
    from pyglet.window import key as pyglet_key
    from gfx_context import make_window

    pack = load_pack(pack_dir)
    if room_id is None:
        room_id = next(iter(pack.rooms.keys()))
    if room_id not in pack.rooms:
        sys.stderr.write(
            f"room_viewer: room {room_id!r} not found. Have: {list(pack.rooms.keys())}\n"
        )
        return 2
    room = pack.rooms[room_id]
    Wm, Hm, Dm = room.dimensions_m
    state = _ViewState()

    window, _ctx = make_window(WINDOW_W, WINDOW_H, WINDOW_TITLE)

    def _reset():
        cam.pos = np.array([0.0, min(1.6, Hm * 0.5), 0.0], dtype=np.float64)
        cam.yaw = pi / 2.0    # look toward +Z (the N wall)
        cam.pitch = 0.0

    cam = FlyCamera()
    _reset()

    _pressed: set[int] = set()
    mouse_look = {"on": False}

    hud = pyglet.text.Label(
        "", font_name="Consolas", font_size=12, x=10, y=WINDOW_H - 10,
        anchor_x="left", anchor_y="top", multiline=True, width=WINDOW_W - 20,
        color=(220, 220, 220, 255),
    )
    help_label = pyglet.text.Label(
        "WASD move  ·  arrows look  ·  Q/E down/up  ·  Shift boost  ·  "
        "M mouse-look  ·  C ceiling-red  ·  L panels-lit  ·  R reset  ·  Esc quit",
        font_name="Consolas", font_size=11, x=10, y=10,
        anchor_x="left", anchor_y="bottom", color=(160, 160, 160, 255),
    )

    @window.event
    def on_mouse_motion(x, y, dx, dy):  # noqa: ANN001
        if mouse_look["on"]:
            cam.add_look(dx * MOUSE_LOOK_GAIN, dy * MOUSE_LOOK_GAIN)

    @window.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):  # noqa: ANN001
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
            _reset()
        elif symbol == pyglet_key.C:
            if room.room_id in state.cleared:
                state.cleared.discard(room.room_id)
            else:
                state.cleared.add(room.room_id)
        elif symbol == pyglet_key.L:
            if state.lit:
                state.lit = set()
            else:
                s: set = set()
                for pair in room.panel_pairs:
                    s.add(pair.drawing_on_asset)
                    s.add(pair.text_on_asset)
                state.lit = s

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
        aspect = WINDOW_W / WINDOW_H
        proj = perspective(FOV_Y_DEG, aspect, NEAR_M, FAR_M)
        mvp = np.ascontiguousarray(proj @ view, dtype=np.float32)
        render_room.draw_room(mvp, room, pack, state)
        hud.text = (
            f"room: {room.room_id}   dims(W,H,D): {tuple(round(v, 1) for v in room.dimensions_m)}\n"
            f"panels: {len(room.panel_pairs)}   cleared(ceiling-red): "
            f"{room.room_id in state.cleared}   panels_lit: {bool(state.lit)}\n"
            f"pos: ({cam.pos[0]:+.1f}, {cam.pos[1]:+.1f}, {cam.pos[2]:+.1f})   "
            f"yaw: {cam.yaw:+.2f}  pitch: {cam.pitch:+.2f}"
        )
        hud.draw()
        help_label.draw()

    pyglet.clock.schedule_interval(update, 1.0 / 60.0)
    pyglet.app.run()
    return 0


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    room_id = argv[0] if len(argv) >= 1 else None
    pack_dir = argv[1] if len(argv) >= 2 else "tests/golden_pack/"
    return run(room_id, pack_dir)


if __name__ == "__main__":
    raise SystemExit(main())
