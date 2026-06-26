"""render_wire.py — QUAKE M1 module #6: Mode A wireframe corridor renderer.

PURE CORE: build_wire_mesh / hex_to_rgb — plain numpy, zero GL.
THIN SHELL: draw_graph — guarded so it imports & runs headless without a GL
context (skips the draw, never crashes on import).

COORDINATES ARE LAW: floorplan is the XZ map-plane, Y is up. Room-local axes
are PARALLEL to map axes (no rotation). Math is ROW-MAJOR internally;
transpose only at the GL boundary.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from contracts import (Floorplan, FloorRoom, Corridor, Crossing,
                       Vec2, Vec3, Hex, NodeId, GameState, ViewMatrix)

# ---------------------------------------------------------------------------
# PINNED CONSTANTS
# ---------------------------------------------------------------------------
WIRE_BASE        = (1.0, 1.0, 1.0)
DIM_NEAR_M       = 6.0
DIM_FAR_M        = 90.0
DIM_FLOOR_GREY   = 0.12     # never-black horizon
WIRE_PX_WIDTH    = 2.5      # constant on-screen line width
DEPTH_BIAS       = 1e-4
RING_SEGMENTS    = 48
BLOOM_THRESHOLD  = 0.6
BLOOM_STRENGTH   = 0.5


# ---------------------------------------------------------------------------
# PURE CORE
# ---------------------------------------------------------------------------
@dataclass
class WireMesh:
    """Renderable wireframe geometry, pure data, zero GL."""
    line_segments: np.ndarray   # shape (N, 2, 3) float32 — N pairs of endpoints
    seg_colors: np.ndarray      # shape (N, 3) float32 — per-segment RGB 0..1
    ring_segments: np.ndarray   # shape (M, 2, 3) float32 — M pairs of ring chords
    ring_colors: np.ndarray     # shape (M, 3) float32 — per-ring-segment RGB 0..1


def hex_to_rgb(h: Hex) -> tuple[float, float, float]:
    """Convert "#rrggbb" hex string to (r, g, b) floats in 0..1."""
    s = h.lstrip("#")
    if len(s) != 6:
        raise ValueError(f"hex_to_rgb expects '#rrggbb', got {h!r}")
    r = int(s[0:2], 16) / 255.0
    g = int(s[2:4], 16) / 255.0
    b = int(s[4:6], 16) / 255.0
    return (r, g, b)


def build_wire_mesh(fp: Floorplan) -> WireMesh:
    """Build renderable wireframe geometry from Floorplan.

    Corridors: each consecutive pair of path_xz points becomes a line segment
    at y=cruise_y. Color = WIRE_BASE (white) for all corridor segments.

    Rooms: a ring (circle) of map_radius_m in the XZ plane at y=socket_y,
    tessellated with RING_SEGMENTS chords. Color = hex_to_rgb(map_color).

    Crossings render naturally — corridors carry their own cruise_y, so
    over_y > under_y separation is honored straight from the data.

    Pure: deterministic, no GL.
    """
    # --- Corridor line segments -------------------------------------------
    seg_list: list[np.ndarray] = []
    seg_col_list: list[tuple[float, float, float]] = []
    base = WIRE_BASE

    for cor in fp.corridors:
        y = float(cor.cruise_y)
        pts = cor.path_xz
        for n in range(len(pts) - 1):
            ax, az = float(pts[n][0]), float(pts[n][1])
            bx, bz = float(pts[n + 1][0]), float(pts[n + 1][1])
            seg_list.append(np.array(
                [[ax, y, az], [bx, y, bz]], dtype=np.float32))
            seg_col_list.append(base)

    if seg_list:
        line_segments = np.stack(seg_list, axis=0).astype(np.float32)
        seg_colors = np.array(seg_col_list, dtype=np.float32)
    else:
        line_segments = np.zeros((0, 2, 3), dtype=np.float32)
        seg_colors = np.zeros((0, 3), dtype=np.float32)

    # --- Room rings --------------------------------------------------------
    ring_list: list[np.ndarray] = []
    ring_col_list: list[tuple[float, float, float]] = []

    # Precompute deterministic angle table (closed loop of RING_SEGMENTS chords).
    angles = (2.0 * np.pi) * (np.arange(RING_SEGMENTS, dtype=np.float64)
                              / float(RING_SEGMENTS))
    next_angles = (2.0 * np.pi) * (
        (np.arange(RING_SEGMENTS, dtype=np.float64) + 1.0) / float(RING_SEGMENTS))

    for room in fp.rooms:
        cx, cz = float(room.map_xz[0]), float(room.map_xz[1])
        r = float(room.map_radius_m)
        y = float(room.socket_y)
        rgb = hex_to_rgb(room.map_color)
        # XZ ring: x = cx + r*cos(t), z = cz + r*sin(t), constant y=socket_y.
        for k in range(RING_SEGMENTS):
            t0 = angles[k]
            t1 = next_angles[k]
            x0 = cx + r * np.cos(t0)
            z0 = cz + r * np.sin(t0)
            x1 = cx + r * np.cos(t1)
            z1 = cz + r * np.sin(t1)
            ring_list.append(np.array(
                [[x0, y, z0], [x1, y, z1]], dtype=np.float32))
            ring_col_list.append(rgb)

    if ring_list:
        ring_segments = np.stack(ring_list, axis=0).astype(np.float32)
        ring_colors = np.array(ring_col_list, dtype=np.float32)
    else:
        ring_segments = np.zeros((0, 2, 3), dtype=np.float32)
        ring_colors = np.zeros((0, 3), dtype=np.float32)

    return WireMesh(
        line_segments=line_segments,
        seg_colors=seg_colors,
        ring_segments=ring_segments,
        ring_colors=ring_colors,
    )


# ---------------------------------------------------------------------------
# Pure helper for the shell: expand segments into camera-facing line-quads.
# ---------------------------------------------------------------------------
def expand_segments_to_quad_attribs(
        segments: np.ndarray,
        colors: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Expand (N,2,3) segments into per-vertex attribute arrays for line-quads.

    Each segment -> 2 triangles (6 vertices). For each emitted vertex we carry:
      - in_pos       : the segment endpoint world position (vec3)
      - in_other     : the *other* endpoint of the segment (vec3) — lets the
                       vertex shader compute the screen-space line direction
      - in_side      : -1.0 or +1.0 — which side to offset for the quad width
      - in_color     : per-vertex RGB

    PURE: no GL. The shell uploads these straight into a VBO. The actual
    screen-space expansion math lives in the shader.

    Triangle layout per segment (A=endpoint0, B=endpoint1):
        (A,-1) (B,-1) (B,+1)   and   (A,-1) (B,+1) (A,+1)
    """
    n = segments.shape[0]
    if n == 0:
        return (np.zeros((0, 3), np.float32),
                np.zeros((0, 3), np.float32),
                np.zeros((0,), np.float32),
                np.zeros((0, 3), np.float32))

    A = segments[:, 0, :]   # (N,3)
    B = segments[:, 1, :]   # (N,3)

    # Per-segment 6-vertex pattern.
    pos      = np.empty((n, 6, 3), np.float32)
    other    = np.empty((n, 6, 3), np.float32)
    side     = np.empty((n, 6), np.float32)
    colA     = colors  # (N,3)

    # Vertex roles: (pos_is_A?, side)
    #   v0=(A,-1) v1=(B,-1) v2=(B,+1) v3=(A,-1) v4=(B,+1) v5=(A,+1)
    pos[:, 0] = A; other[:, 0] = B; side[:, 0] = -1.0
    pos[:, 1] = B; other[:, 1] = A; side[:, 1] = -1.0
    pos[:, 2] = B; other[:, 2] = A; side[:, 2] = +1.0
    pos[:, 3] = A; other[:, 3] = B; side[:, 3] = -1.0
    pos[:, 4] = B; other[:, 4] = A; side[:, 4] = +1.0
    pos[:, 5] = A; other[:, 5] = B; side[:, 5] = +1.0

    col = np.repeat(colA[:, None, :], 6, axis=1)  # (N,6,3)

    return (pos.reshape(-1, 3).astype(np.float32),
            other.reshape(-1, 3).astype(np.float32),
            side.reshape(-1).astype(np.float32),
            col.reshape(-1, 3).astype(np.float32))


# ---------------------------------------------------------------------------
# HEADLESS GUARD — safe import
# ---------------------------------------------------------------------------
try:
    from glguard import HAVE_GL
except Exception:
    HAVE_GL = False


# ---------------------------------------------------------------------------
# THIN GL SHELL
# ---------------------------------------------------------------------------
# Per-floorplan cache of built mesh + GL buffers, keyed by level_id.
_GL_CACHE: dict[str, dict] = {}


def _row_major_to_gl(mvp: np.ndarray) -> np.ndarray:
    """Return the matrix in the layout the GL uniform setter wants.

    Our internal convention is ROW-MAJOR. moderngl's write() expects the raw
    bytes; whether GLSL reads them as the transpose depends on the upload path.
    We transpose here so a standard column-major GLSL `mat4 * vec4` consumes a
    correctly-oriented matrix.

    INTEGRATION: confirm exact orientation (transpose or not) once against the
    real shader; flip this single line if the picture comes out transposed.
    """
    return np.ascontiguousarray(mvp.T, dtype=np.float32)


def _gl_get_context():
    """Fetch the active moderngl context.

    INTEGRATION: confirm exact API — `moderngl.get_context()` returns the
    current context bound by gfx_context; some setups pass a ctx explicitly.
    """
    import moderngl  # local import: never required at module import time
    return moderngl.get_context()


def _gl_viewport_size(ctx) -> tuple[int, int]:
    """Current framebuffer pixel size (w, h).

    INTEGRATION: confirm exact API — typically `ctx.fbo.size` or
    `ctx.screen.size`.
    """
    try:
        return tuple(int(v) for v in ctx.fbo.size)
    except Exception:
        return tuple(int(v) for v in ctx.screen.size)


def _gl_make_vbo(ctx, data: np.ndarray):
    """Create a vertex buffer.

    INTEGRATION: confirm exact API — `ctx.buffer(data.tobytes())`.
    """
    return ctx.buffer(data.astype(np.float32, copy=False).tobytes())


def _gl_make_vao(ctx, program, pos_vbo, other_vbo, side_vbo, col_vbo):
    """Build a vertex array binding the four attribute streams.

    INTEGRATION: confirm exact API and attribute names match shaders.py —
    `ctx.vertex_array(program, [(vbo, fmt, *names)])`.
    """
    return ctx.vertex_array(
        program,
        [
            (pos_vbo,   "3f", "in_pos"),
            (other_vbo, "3f", "in_other"),
            (side_vbo,  "1f", "in_side"),
            (col_vbo,   "3f", "in_color"),
        ],
    )


def _gl_set_uniform(program, name: str, value) -> None:
    """Set a program uniform if it exists.

    INTEGRATION: confirm exact API — moderngl programs are dict-like:
    `program[name].value = value`. Uniform may be optimized out; ignore misses.
    """
    try:
        program[name].value = value
    except KeyError:
        pass
    except Exception:
        # Matrices want bytes via .write(); handle that path.
        try:
            program[name].write(np.ascontiguousarray(value, np.float32).tobytes())
        except Exception:
            pass


def _gl_set_matrix(program, name: str, mat_row_major: np.ndarray) -> None:
    """Upload a (4,4) row-major matrix uniform.

    INTEGRATION: confirm exact API — `program[name].write(bytes)`.
    """
    data = _row_major_to_gl(mat_row_major)
    try:
        program[name].write(data.tobytes())
    except Exception:
        pass


def _gl_draw_vao(vao, vertex_count: int) -> None:
    """Issue the draw call as triangles.

    INTEGRATION: confirm exact API — `vao.render(mode=moderngl.TRIANGLES)`
    or `vao.render()` (defaults to triangles).
    """
    try:
        vao.render()
    except Exception:
        pass


def _build_gl_resources(ctx, program, fp: Floorplan) -> dict:
    """Build (or rebuild) GL buffers/VAOs for a floorplan. Pure-data prepped
    by the core, only the buffer creation touches GL."""
    mesh = build_wire_mesh(fp)

    s_pos, s_other, s_side, s_col = expand_segments_to_quad_attribs(
        mesh.line_segments, mesh.seg_colors)
    r_pos, r_other, r_side, r_col = expand_segments_to_quad_attribs(
        mesh.ring_segments, mesh.ring_colors)

    res: dict = {"mesh": mesh, "seg_count": 0, "ring_count": 0,
                 "seg_vao": None, "ring_vao": None}

    if s_pos.shape[0] > 0:
        seg_vbos = (
            _gl_make_vbo(ctx, s_pos),
            _gl_make_vbo(ctx, s_other),
            _gl_make_vbo(ctx, s_side),
            _gl_make_vbo(ctx, s_col),
        )
        res["seg_vao"] = _gl_make_vao(ctx, program, *seg_vbos)
        res["seg_count"] = s_pos.shape[0]

    if r_pos.shape[0] > 0:
        ring_vbos = (
            _gl_make_vbo(ctx, r_pos),
            _gl_make_vbo(ctx, r_other),
            _gl_make_vbo(ctx, r_side),
            _gl_make_vbo(ctx, r_col),
        )
        res["ring_vao"] = _gl_make_vao(ctx, program, *ring_vbos)
        res["ring_count"] = r_pos.shape[0]

    return res


def _run_bloom_post(ctx) -> None:
    """Screen-space bloom POST pass (NOT alpha blending of wires).

    Bright-extract (threshold BLOOM_THRESHOLD) -> separable blur ->
    additive composite (BLOOM_STRENGTH).

    INTEGRATION: FBO ping-pong with moderngl framebuffers + blit_program.
    The full-screen triangle draw, framebuffer allocation, and texture binding
    are all isolated here so DeepSeek's compile loop fixes them in one place.
    """
    try:
        from shaders import blit_program
    except Exception:
        return
    # INTEGRATION: implement ping-pong here once the real shaders.py / FBO
    # helpers are confirmed. Intentionally a no-op-safe stub: bloom is a visual
    # enhancement and must never crash the frame if the post-pass isn't wired.
    _ = blit_program
    return


def draw_graph(view: ViewMatrix, fp: Floorplan, state: GameState) -> None:
    """Mode A wireframe corridor renderer.

    Lines + node rings, depth-tested, BLEND OFF, distance-dimming white->dark
    grey (never black), crossings as TRUE 3D over/under (honored from data),
    camera-facing line-quads + depth bias, screen-space bloom (post effect).

    DEPTH/BLEND STATE: depth test on, LEQUAL, write on, BLEND OFF — owned by
    gfx_context; this function does NOT change it.
    """
    if not HAVE_GL:
        return

    try:
        from shaders import wire_program
    except Exception:
        return

    try:
        ctx = _gl_get_context()
    except Exception:
        return

    key = getattr(fp, "level_id", None) or id(fp)
    res = _GL_CACHE.get(key)
    if res is None:
        try:
            res = _build_gl_resources(ctx, wire_program, fp)
        except Exception:
            return
        _GL_CACHE[key] = res

    w, h = _gl_viewport_size(ctx)

    # Uniforms (row-major view -> oriented at the boundary).
    _gl_set_matrix(wire_program, "u_mvp", np.asarray(view, dtype=np.float32))
    _gl_set_uniform(wire_program, "u_dim_near", float(DIM_NEAR_M))
    _gl_set_uniform(wire_program, "u_dim_far", float(DIM_FAR_M))
    _gl_set_uniform(wire_program, "u_dim_floor", float(DIM_FLOOR_GREY))
    _gl_set_uniform(wire_program, "u_depth_bias", float(DEPTH_BIAS))
    _gl_set_uniform(wire_program, "u_px_width", float(WIRE_PX_WIDTH))
    _gl_set_uniform(wire_program, "u_viewport", (float(w), float(h)))
    _gl_set_uniform(wire_program, "u_color", tuple(float(c) for c in WIRE_BASE))

    # Draw corridor segments, then room rings.
    if res.get("seg_vao") is not None:
        _gl_draw_vao(res["seg_vao"], res["seg_count"])
    if res.get("ring_vao") is not None:
        _gl_draw_vao(res["ring_vao"], res["ring_count"])

    # Screen-space bloom post pass.
    _run_bloom_post(ctx)
