"""render_wire.py — QUAKE Mode A wireframe corridor renderer.

PURE CORE: build_wire_mesh / hex_to_rgb — plain numpy, zero GL.
THIN SHELL: draw_graph — simple LINES rendering, depth-tested.

COORDINATES: floorplan is XZ map-plane, Y is up.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from contracts import (Floorplan, Hex, GameState, ViewMatrix)

# ---------------------------------------------------------------------------
# PINNED CONSTANTS
# ---------------------------------------------------------------------------
WIRE_BASE = (1.0, 1.0, 1.0)
RING_SEGMENTS = 48

# ---------------------------------------------------------------------------
# PURE CORE
# ---------------------------------------------------------------------------
@dataclass
class WireMesh:
    line_segments: np.ndarray   # (N, 2, 3) float32
    seg_colors: np.ndarray      # (N, 3) float32
    ring_segments: np.ndarray   # (M, 2, 3) float32
    ring_colors: np.ndarray     # (M, 3) float32


def hex_to_rgb(h: Hex) -> tuple[float, float, float]:
    s = h.lstrip("#")
    if len(s) != 6:
        raise ValueError(f"hex_to_rgb expects '#rrggbb', got {h!r}")
    return (int(s[0:2], 16) / 255.0, int(s[2:4], 16) / 255.0, int(s[4:6], 16) / 255.0)


def build_wire_mesh(fp: Floorplan) -> WireMesh:
    """Build wireframe line segments from a Floorplan.  Pure, no GL."""
    seg_list: list[np.ndarray] = []
    seg_col_list: list[tuple[float, float, float]] = []
    base = (1.0, 1.0, 1.0)

    for cor in fp.corridors:
        y = float(cor.cruise_y)
        pts = cor.path_xz
        for n in range(len(pts) - 1):
            ax, az = float(pts[n][0]), float(pts[n][1])
            bx, bz = float(pts[n + 1][0]), float(pts[n + 1][1])
            seg_list.append(np.array([[ax, y, az], [bx, y, bz]], dtype=np.float32))
            seg_col_list.append(base)

    line_segments = (np.stack(seg_list, axis=0).astype(np.float32) if seg_list
                     else np.zeros((0, 2, 3), dtype=np.float32))
    seg_colors = np.array(seg_col_list, dtype=np.float32) if seg_col_list else np.zeros((0, 3), dtype=np.float32)

    ring_list: list[np.ndarray] = []
    ring_col_list: list[tuple[float, float, float]] = []
    angles = (2.0 * np.pi) * (np.arange(RING_SEGMENTS, dtype=np.float64) / float(RING_SEGMENTS))
    next_angles = (2.0 * np.pi) * ((np.arange(RING_SEGMENTS, dtype=np.float64) + 1.0) / float(RING_SEGMENTS))

    for room in fp.rooms:
        cx, cz = float(room.map_xz[0]), float(room.map_xz[1])
        r = float(room.map_radius_m)
        y = float(room.socket_y)
        rgb = hex_to_rgb(room.map_color)
        for k in range(RING_SEGMENTS):
            t0, t1 = angles[k], next_angles[k]
            ring_list.append(np.array(
                [[cx + r * np.cos(t0), y, cz + r * np.sin(t0)],
                 [cx + r * np.cos(t1), y, cz + r * np.sin(t1)]], dtype=np.float32))
            ring_col_list.append(rgb)

    ring_segments = (np.stack(ring_list, axis=0).astype(np.float32) if ring_list
                     else np.zeros((0, 2, 3), dtype=np.float32))
    ring_colors = np.array(ring_col_list, dtype=np.float32) if ring_col_list else np.zeros((0, 3), dtype=np.float32)

    return WireMesh(line_segments=line_segments, seg_colors=seg_colors,
                    ring_segments=ring_segments, ring_colors=ring_colors)


# ---------------------------------------------------------------------------
# HEADLESS GUARD
# ---------------------------------------------------------------------------
try:
    from glguard import HAVE_GL
except Exception:
    HAVE_GL = False

_GL_CACHE: dict[str, dict] = {}


def _flatten_segments(segments: np.ndarray, colors: np.ndarray):
    """Flatten (N,2,3) segments -> (N*2,3) endpoints with per-vertex colors."""
    n = segments.shape[0]
    if n == 0:
        return np.zeros((0, 3), np.float32), np.zeros((0, 3), np.float32)
    pos = segments.reshape(-1, 3).astype(np.float32)
    col = np.repeat(colors, 2, axis=0).astype(np.float32)
    return pos, col


def draw_graph(view: ViewMatrix, fp: Floorplan, state: GameState) -> None:
    """Mode A wireframe: simple LINES, depth-tested."""
    if not HAVE_GL:
        return
    try:
        import moderngl
        ctx = moderngl.get_context()
    except Exception:
        return

    key = getattr(fp, "level_id", None) or id(fp)
    res = _GL_CACHE.get(key)
    if res is None:
        try:
            from shaders import wire_program as _wire_compile
            prog = _wire_compile(ctx)
            if prog is None:
                return

            mesh = build_wire_mesh(fp)
            seg_pos, seg_col = _flatten_segments(mesh.line_segments, mesh.seg_colors)
            ring_pos, ring_col = _flatten_segments(mesh.ring_segments, mesh.ring_colors)

            res = {"prog": prog, "seg_vao": None, "ring_vao": None}
            if seg_pos.shape[0] > 0:
                vbo_p = ctx.buffer(seg_pos.tobytes())
                vbo_c = ctx.buffer(seg_col.tobytes())
                res["seg_vao"] = ctx.vertex_array(
                    prog, [(vbo_p, '3f', 'in_pos'), (vbo_c, '3f', 'in_color')],
                    mode=moderngl.LINES)
            if ring_pos.shape[0] > 0:
                vbo_p = ctx.buffer(ring_pos.tobytes())
                vbo_c = ctx.buffer(ring_col.tobytes())
                res["ring_vao"] = ctx.vertex_array(
                    prog, [(vbo_p, '3f', 'in_pos'), (vbo_c, '3f', 'in_color')],
                    mode=moderngl.LINES)
        except Exception:
            return
        _GL_CACHE[key] = res

    prog = res.get("prog")
    if prog is None:
        return

    try:
        mvp_gl = np.ascontiguousarray(np.asarray(view, dtype=np.float32).T, dtype=np.float32)
        prog['u_mvp'].write(mvp_gl.tobytes())
    except Exception:
        pass

    try:
        if res.get("seg_vao") is not None:
            res["seg_vao"].render()
        if res.get("ring_vao") is not None:
            res["ring_vao"].render()
    except Exception:
        pass
