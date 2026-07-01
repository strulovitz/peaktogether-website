"""QUAKE — minimap.py (FLAT pivot HUD).

A corner heads-up minimap for the flat, teleport-based game:
  * every room = a dot, colored by its importance (floorplan map_color);
  * every link (corridor) = a thin line between the two rooms;
  * cleared rooms (demon killed) get a red X;
  * the player = a real OS emoji marker sitting on the current room, whose mood
    changes: happy (demon killed) / frightened (demon out & alive) /
    thinking (panels colored, demon not out) / neutral (nothing done yet).

SPLIT:
  * PURE CORE  — compute_box / project_rooms / room_mood / hex_to_rgb: plain math,
                 zero GL, fully unit-testable headless.
  * THIN SHELL — draw_minimap: GL draw. Guarded by HAVE_GL; never crashes on
                 import and returns immediately when there is no GL context.
"""

from __future__ import annotations

import math
from typing import Dict, Optional, Tuple

try:
    from glguard import HAVE_GL
except Exception:  # pragma: no cover
    HAVE_GL = False


# ---------------------------------------------------------------------------
# PURE CORE
# ---------------------------------------------------------------------------

# Mood -> emoji glyph (real Segoe UI Emoji codepoints).
MOOD_EMOJI = {
    "happy": "\U0001F600",        # 😀 demon killed
    "frightened": "\U0001F631",   # 😱 demon out & alive
    "thinking": "\U0001F914",     # 🤔 panels colored, demon not out
    "neutral": "\U0001F642",      # 🙂 nothing done yet
}

# Importance -> dot radius scale (bigger = more important), matching the map idea.
_BASE_DOT_NDC_Y = 0.016


def hex_to_rgb(h: str) -> Tuple[float, float, float]:
    """'#RRGGBB' -> (r, g, b) floats in 0..1. Tolerant of missing '#'."""
    s = h.lstrip("#")
    if len(s) != 6:
        return (0.8, 0.8, 0.85)
    return (int(s[0:2], 16) / 255.0,
            int(s[2:4], 16) / 255.0,
            int(s[4:6], 16) / 255.0)


def compute_box(aspect: float, side_y: float = 0.56,
                margin: float = 0.04) -> Tuple[float, float, float, float]:
    """Top-right minimap box in NDC as (x0, y0, x1, y1).

    side_y is the box height in NDC-Y units; the width is chosen so the box is
    SQUARE on screen (NDC-X extent = side_y / aspect). Pure.
    """
    aspect = max(aspect, 1e-6)
    side_x = side_y / aspect
    x1 = 1.0 - margin
    x0 = x1 - side_x
    y1 = 1.0 - margin
    y0 = y1 - side_y
    return (x0, y0, x1, y1)


def project_rooms(rooms_xz: Dict[str, Tuple[float, float]],
                  box: Tuple[float, float, float, float],
                  aspect: float,
                  pad_frac: float = 0.14) -> Dict[str, Tuple[float, float]]:
    """Map world (x, z) room centers into NDC positions inside `box`.

    The world bounding box is fit UNIFORMLY (no distortion) and centered; world
    +Z maps to screen up. Returns {room_id: (ndc_x, ndc_y)}. Pure.
    """
    x0, y0, x1, y1 = box
    aspect = max(aspect, 1e-6)
    if not rooms_xz:
        return {}

    xs = [p[0] for p in rooms_xz.values()]
    zs = [p[1] for p in rooms_xz.values()]
    minx, maxx = min(xs), max(xs)
    minz, maxz = min(zs), max(zs)
    wcx = (minx + maxx) / 2.0
    wcz = (minz + maxz) / 2.0
    wspanx = max(maxx - minx, 1e-6)
    wspanz = max(maxz - minz, 1e-6)

    side_y = y1 - y0
    usable = side_y * (1.0 - 2.0 * pad_frac)        # in on-screen-square (NDC-Y) units
    scale = usable / max(wspanx, wspanz)

    bcx = (x0 + x1) / 2.0
    bcy = (y0 + y1) / 2.0

    out: Dict[str, Tuple[float, float]] = {}
    for nid, (wx, wz) in rooms_xz.items():
        ox = (wx - wcx) * scale        # NDC-Y units (square on screen)
        oy = (wz - wcz) * scale
        out[nid] = (bcx + ox / aspect, bcy + oy)
    return out


def room_mood(state, level_id: str, room_id: Optional[str]) -> str:
    """Determine the mood of the player's marker for `room_id`. Pure.

    happy: demon killed (room cleared) · frightened: hidden door open (demon out
    & alive) · thinking: some panels lit · neutral: nothing done yet.
    """
    if room_id is None:
        return "neutral"
    if room_id in getattr(state, "cleared", set()):
        return "happy"
    save = getattr(state, "save", None)
    lvl = None
    if save is not None and getattr(save, "levels", None):
        lvl = save.levels.get(level_id)
    rp = lvl.rooms.get(room_id) if (lvl is not None and getattr(lvl, "rooms", None)) else None
    if rp is not None:
        if getattr(rp, "hidden_door_open", False):
            return "frightened"
        if getattr(rp, "pairs_on", None):
            return "thinking"
    return "neutral"


def _disc_verts(segments: int = 20):
    """Unit disc (radius 1) as a flat triangle list around the origin. Pure."""
    v = []
    for i in range(segments):
        a0 = 2.0 * math.pi * i / segments
        a1 = 2.0 * math.pi * (i + 1) / segments
        v += [0.0, 0.0,
              math.cos(a0), math.sin(a0),
              math.cos(a1), math.sin(a1)]
    return v


# ---------------------------------------------------------------------------
# THIN SHELL — GL. Guarded. Never crashes headless.
# ---------------------------------------------------------------------------

# GLSL: flat-colored 2D primitive with a per-draw offset+scale (NDC space).
_MINI_VS = """#version 330 core
in vec2 in_pos;
uniform vec2 u_offset;
uniform vec2 u_scale;
void main() {
    gl_Position = vec4(in_pos * u_scale + u_offset, 0.0, 1.0);
}
"""
_MINI_FS = """#version 330 core
uniform vec4 u_color;
out vec4 frag_color;
void main() { frag_color = u_color; }
"""

# Per-context caches.
_mini_cache: dict = {}       # id(ctx) -> {"prog":..., "disc_vao":..., "disc_vbo":...}
_emoji_tex: dict = {}        # (id(ctx), mood) -> moderngl.Texture
_blit_cache: dict = {}       # id(ctx) -> blit program


def _setu(prog, name, value) -> None:
    try:
        prog[name].value = value
    except Exception:
        pass


def _get_ctx():
    import moderngl
    try:
        return moderngl.get_context()
    except Exception:
        return None


def _emoji_texture(ctx, mood: str):
    key = (id(ctx), mood)
    tex = _emoji_tex.get(key)
    if tex is not None:
        return tex
    try:
        from PIL import Image, ImageDraw, ImageFont
        glyph = MOOD_EMOJI.get(mood, MOOD_EMOJI["neutral"])
        px = 128
        font = ImageFont.truetype(r"C:\Windows\Fonts\seguiemj.ttf", 109)
        img = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        # center the glyph
        try:
            bbox = d.textbbox((0, 0), glyph, font=font, embedded_color=True)
            gw, gh = bbox[2] - bbox[0], bbox[3] - bbox[1]
            ox = (px - gw) // 2 - bbox[0]
            oy = (px - gh) // 2 - bbox[1]
        except Exception:
            ox, oy = 8, 8
        d.text((ox, oy), glyph, font=font, embedded_color=True)
        tex = ctx.texture(img.size, 4, img.tobytes())
        try:
            tex.build_mipmaps()
        except Exception:
            pass
        _emoji_tex[key] = tex
        return tex
    except Exception:
        return None


def _mini(ctx):
    c = _mini_cache.get(id(ctx))
    if c is not None:
        return c
    import numpy as np
    prog = ctx.program(vertex_shader=_MINI_VS, fragment_shader=_MINI_FS)
    disc_vbo = ctx.buffer(np.array(_disc_verts(), dtype="f4").tobytes())
    disc_vao = ctx.vertex_array(prog, [(disc_vbo, "2f", "in_pos")])
    c = {"prog": prog, "disc_vao": disc_vao, "disc_vbo": disc_vbo}
    _mini_cache[id(ctx)] = c
    return c


def _draw_lines(ctx, prog, verts, color, mode):
    import numpy as np
    if not verts:
        return
    vbo = ctx.buffer(np.array(verts, dtype="f4").tobytes())
    vao = ctx.vertex_array(prog, [(vbo, "2f", "in_pos")])
    _setu(prog, "u_color", color)
    _setu(prog, "u_offset", (0.0, 0.0))
    _setu(prog, "u_scale", (1.0, 1.0))
    vao.render(mode=mode)
    vao.release()
    vbo.release()


def draw_minimap(floorplan, state, level_id: str,
                 win_w: int, win_h: int) -> None:
    """Draw the corner minimap HUD over the current frame. Headless-safe."""
    if not HAVE_GL:
        return
    ctx = _get_ctx()
    if ctx is None:
        return

    rooms = getattr(floorplan, "rooms", None)
    if not rooms:
        return

    import moderngl

    aspect = float(win_w) / float(max(win_h, 1))
    rooms_xz = {r.room_id: (r.map_xz[0], r.map_xz[1]) for r in rooms}
    color_by_room = {r.room_id: r.map_color for r in rooms}
    imp_by_room = {r.room_id: r.importance for r in rooms}

    box = compute_box(aspect)
    x0, y0, x1, y1 = box
    pos = project_rooms(rooms_xz, box, aspect)

    c = _mini(ctx)
    prog = c["prog"]
    disc_vao = c["disc_vao"]

    # HUD render state: no depth test, alpha blend on.
    ctx.disable(moderngl.DEPTH_TEST)
    ctx.enable(moderngl.BLEND)
    ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)

    # --- 1) panel background quad ---
    panel = [x0, y0, x1, y0, x1, y1, x0, y0, x1, y1, x0, y1]
    _draw_lines(ctx, prog, panel, (0.04, 0.05, 0.07, 0.62), moderngl.TRIANGLES)
    # border
    border = [x0, y0, x1, y0, x1, y1, x0, y1]
    _draw_lines(ctx, prog, border, (0.55, 0.58, 0.66, 0.9), moderngl.LINE_LOOP)

    # --- 2) edges (links between rooms) ---
    edge_verts = []
    for cor in getattr(floorplan, "corridors", []):
        a = pos.get(cor.source)
        b = pos.get(cor.target)
        if a and b:
            edge_verts += [a[0], a[1], b[0], b[1]]
    _draw_lines(ctx, prog, edge_verts, (0.80, 0.82, 0.88, 0.75), moderngl.LINES)

    # --- 3) room dots (colored by importance) ---
    for rid, (mx, my) in pos.items():
        r_ndc = _BASE_DOT_NDC_Y * (0.65 + 0.14 * imp_by_room.get(rid, 3))
        rgb = hex_to_rgb(color_by_room.get(rid, "#9aa0a6"))
        _setu(prog, "u_color", (rgb[0], rgb[1], rgb[2], 1.0))
        _setu(prog, "u_offset", (mx, my))
        _setu(prog, "u_scale", (r_ndc / aspect, r_ndc))
        disc_vao.render(mode=moderngl.TRIANGLES)

    # --- 4) X over cleared rooms ---
    cleared = getattr(state, "cleared", set()) or set()
    x_verts = []
    xr = _BASE_DOT_NDC_Y * 1.15
    for rid in cleared:
        p = pos.get(rid)
        if not p:
            continue
        mx, my = p
        hx = xr / aspect
        hy = xr
        x_verts += [mx - hx, my - hy, mx + hx, my + hy,
                    mx - hx, my + hy, mx + hx, my - hy]
    _draw_lines(ctx, prog, x_verts, (0.93, 0.14, 0.14, 1.0), moderngl.LINES)

    # --- 5) player emoji marker on the current room ---
    cur = getattr(state, "current_room_id", None)
    marker = pos.get(cur) if cur is not None else None
    if marker is not None:
        mood = room_mood(state, level_id, cur)
        tex = _emoji_texture(ctx, mood)
        if tex is not None:
            blit = _blit_cache.get(id(ctx))
            if blit is None:
                from shaders import blit_program
                blit = blit_program(ctx)
                _blit_cache[id(ctx)] = blit
            if blit is not None:
                import numpy as np
                half = 0.052
                hx = half / aspect
                hy = half
                mx, my = marker
                quad = [
                    mx - hx, my - hy, 0.0, 0.0,
                    mx + hx, my - hy, 1.0, 0.0,
                    mx + hx, my + hy, 1.0, 1.0,
                    mx - hx, my - hy, 0.0, 0.0,
                    mx + hx, my + hy, 1.0, 1.0,
                    mx - hx, my + hy, 0.0, 1.0,
                ]
                vbo = ctx.buffer(np.array(quad, dtype="f4").tobytes())
                vao = ctx.vertex_array(
                    blit, [(vbo, "2f 2f", "in_pos", "in_uv")])
                _setu(blit, "u_tex", 0)
                _setu(blit, "u_zoom", 1.0)
                _setu(blit, "u_pan", (0.0, 0.0))
                tex.use(location=0)
                vao.render(mode=moderngl.TRIANGLES)
                vao.release()
                vbo.release()

    # restore depth test for the next frame's 3D pass
    ctx.enable(moderngl.DEPTH_TEST)
    ctx.disable(moderngl.BLEND)
