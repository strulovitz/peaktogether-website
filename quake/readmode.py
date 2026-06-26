"""QUAKE M6 — readmode (module #11).

Renders a pin-sharp, full-screen, flat 2D, zoomable/pannable image of a
master-DPI panel PNG. No perspective, no blur.

SPLIT:
  - PURE core: read_uv_transform — pure math, zero GL, fully unit-tested.
  - THIN shell: draw_read — GL draw, guarded for headless, never crashes on import.

This module ONLY RENDERS. Target selection is owned by gameplay/nav.
draw_read receives the pre-chosen master PNG path.
"""

from contracts import Vec2

# HAVE_GL must never crash on import.
try:
    from glguard import HAVE_GL
except Exception:
    HAVE_GL = False


# ---------------------------------------------------------------------------
# PURE CORE — math only, zero GL, unit-testable.
# ---------------------------------------------------------------------------

MAX_ZOOM = 8.0


def read_uv_transform(zoom: float, pan: Vec2) -> tuple[float, Vec2]:
    """Validate and clamp zoom/pan.

    zoom: clamp to [1.0, MAX_ZOOM].
    pan:  (pan_x, pan_y) — clamp each axis to ±(1 - 1/zoom) * 0.5.
          At zoom == 1.0, pan is forced to (0.0, 0.0).

    Returns (clamped_zoom, clamped_pan) where clamped_pan is a Vec2.
    Pure math, zero GL.
    """
    # Clamp zoom into [1.0, MAX_ZOOM].
    if zoom < 1.0:
        clamped_zoom = 1.0
    elif zoom > MAX_ZOOM:
        clamped_zoom = MAX_ZOOM
    else:
        clamped_zoom = float(zoom)

    # At 1x there is nothing to pan.
    if clamped_zoom == 1.0:
        return clamped_zoom, (0.0, 0.0)

    # Symmetric per-axis pan limit.
    limit = (1.0 - 1.0 / clamped_zoom) * 0.5

    pan_x, pan_y = pan
    clamped_x = _clamp(float(pan_x), -limit, limit)
    clamped_y = _clamp(float(pan_y), -limit, limit)

    return clamped_zoom, (clamped_x, clamped_y)


def _clamp(value: float, lo: float, hi: float) -> float:
    if value < lo:
        return lo
    if value > hi:
        return hi
    return value


# ---------------------------------------------------------------------------
# THIN SHELL — GL draw. Guarded. Uncertain external APIs isolated behind
# tiny wrapper functions marked "INTEGRATION: confirm exact API".
# ---------------------------------------------------------------------------

# Module-level caches (shared across all reads).
_texture_cache: dict = {}   # path -> moderngl.Texture
_vao_cache: dict = {}       # id(ctx) -> fullscreen VAO

# Fullscreen quad geometry in NDC.
#   bl, br, tr, bl, tr, tl  (two triangles)
_QUAD_POSITIONS = [
    -1.0, -1.0,
     1.0, -1.0,
     1.0,  1.0,
    -1.0, -1.0,
     1.0,  1.0,
    -1.0,  1.0,
]
_QUAD_UVS = [
    0.0, 0.0,
    1.0, 0.0,
    1.0, 1.0,
    0.0, 0.0,
    1.0, 1.0,
    0.0, 1.0,
]


# --- isolated uncertain-API wrappers ---------------------------------------

def _get_context():
    # INTEGRATION: confirm exact API — moderngl.create_context() requires an
    # existing GL context bound (via pyglet window). Returns None if unavailable.
    import moderngl
    try:
        return moderngl.create_context()
    except Exception:
        return None


def _load_rgba(asset_master_path: str):
    # INTEGRATION: confirm exact API — Pillow Image.open / convert / size / tobytes.
    from PIL import Image
    img = Image.open(asset_master_path).convert("RGBA")
    return img.size, img.tobytes()


def _make_texture(ctx, size, data):
    # INTEGRATION: confirm exact API — ctx.texture(size, components, data).
    texture = ctx.texture(size, 4, data)
    # INTEGRATION: confirm exact API — texture.build_mipmaps() for minification.
    try:
        texture.build_mipmaps()
    except Exception:
        pass
    return texture


def _use_texture(texture, location: int) -> None:
    # INTEGRATION: confirm exact API — texture.use(location=...).
    texture.use(location=location)


def _set_uniform(program, name: str, value) -> None:
    # INTEGRATION: confirm exact API — program['name'].value = value.
    try:
        program[name].value = value
    except KeyError:
        # Uniform may be optimized out by the driver; ignore gracefully.
        pass


def _make_fullscreen_vao(ctx, program):
    # INTEGRATION: confirm exact API — ctx.buffer / ctx.vertex_array layout.
    import numpy as np
    pos_vbo = ctx.buffer(np.array(_QUAD_POSITIONS, dtype=np.float32).tobytes())
    uv_vbo = ctx.buffer(np.array(_QUAD_UVS, dtype=np.float32).tobytes())
    vao = ctx.vertex_array(
        program,
        [
            (pos_vbo, "2f", "in_pos"),
            (uv_vbo, "2f", "in_uv"),
        ],
    )
    return vao


def _render(vao) -> None:
    # INTEGRATION: confirm exact API — vao.render().
    vao.render()


# --- public shell ----------------------------------------------------------

def draw_read(asset_master_path: str, zoom: float, pan: Vec2) -> None:
    """Render the master-DPI panel PNG as a fullscreen flat 2D image.

    Headless-safe: returns immediately when no GL context is available.
    """
    if not HAVE_GL:
        return

    # 1. Pure clamp.
    clamp_zoom, clamped_pan = read_uv_transform(zoom, pan)

    # 2. Context.
    ctx = _get_context()
    if ctx is None:
        return

    # 3. Load + cache the master PNG as a GL texture, keyed by path.
    texture = _texture_cache.get(asset_master_path)
    if texture is None:
        size, data = _load_rgba(asset_master_path)
        texture = _make_texture(ctx, size, data)
        _texture_cache[asset_master_path] = texture

    # 4. Compile/fetch the blit program.
    from shaders import blit_program
    program = blit_program(ctx)

    # 5. Uniforms.
    _set_uniform(program, "u_tex", 0)
    _set_uniform(program, "u_zoom", clamp_zoom)
    _set_uniform(program, "u_pan", tuple(clamped_pan))
    _use_texture(texture, 0)

    # 6. Cached fullscreen VAO (shared across all reads, per context).
    cache_key = id(ctx)
    vao = _vao_cache.get(cache_key)
    if vao is None:
        vao = _make_fullscreen_vao(ctx, program)
        _vao_cache[cache_key] = vao

    _render(vao)

    # 7. Done. App owns pause/resume.
    return
