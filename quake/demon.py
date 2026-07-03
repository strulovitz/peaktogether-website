"""
demon.py — QUAKE demon (moderngl port of the proven DOOM demon).

Pure builders (headless-testable) + a thin GL shell (glguard-gated).
Design copied verbatim from doom/principia/enemy/demon.py, made of MANY balls:
  ~100 pink body spheres (procedural jittered rounded-blob fill)
  10 white teeth (5 upper + 5 lower)
  2 blue eyes, each: blue eyeball -> black pupil -> white glint (nested, proud)
Death = per-sphere fly-out + shrink to nothing over ~0.6s, gone by ~0.7s.
Alive = gentle vertical bob (y += sin(t*2)*0.1) — applied by caller on the root.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

try:
    import glguard
    HAVE_GL = glguard.HAVE_GL
except Exception:  # pragma: no cover - headless import safety
    HAVE_GL = False

if HAVE_GL:
    import moderngl


# ----------------------------------------------------------------------------
# Colors (hex, matching the DOOM demon roles)
# ----------------------------------------------------------------------------
_PINK = "#e0607a"   # body
_WHITE = "#f4f4f0"  # teeth + glint
_BLUE = "#3a6ff0"   # eyeball
_BLACK = "#0a0a0a"  # pupil


def _hex_to_rgb(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    return (int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0)


# ----------------------------------------------------------------------------
# Sphere data model (moderngl analogue of DemonCircle, in 3D)
# ----------------------------------------------------------------------------
@dataclass
class DemonSphere:
    """One ball. offset is relative to the demon root (spawn_xyz)."""
    offset: tuple[float, float, float]
    radius: float
    color: tuple[float, float, float]
    role: str  # "body" | "tooth" | "eye" | "pupil" | "glint"
    # death kinematics (filled at kill time by seed_explosion)
    fly_dir: tuple[float, float, float] = (0.0, 0.0, 0.0)
    fly_speed: float = 0.0


# ----------------------------------------------------------------------------
# PURE BUILDERS
# ----------------------------------------------------------------------------
def build_demon_spheres(
    body_span_m: float = 1.2,
    n_body: int = 100,
    seed: int = 1729,
) -> list[DemonSphere]:
    """
    Build the full demon sphere set, centered at the root origin (0,0,0).
    Caller places the root at spawn_xyz. The cluster is ~body_span_m across
    and rests so its bottom is near y=0 relative to the root (spawn on floor).

    Ordering guarantee: BIG BODY spheres first, features after — so the draw
    order + proud offsets keep features visible over the opaque body.
    """
    rng = random.Random(seed)
    spheres: list[DemonSphere] = []

    body_radius = body_span_m * 0.5

    # ------- BODY: ~100 pink spheres, jittered to fill a rounded blob -------
    # Blob is slightly taller than wide (demon torso). Center of blob raised so
    # the whole cluster sits on the floor: root at spawn_xyz(y=0.1), blob center
    # at +body_radius so the bottom of the body is near the floor.
    cx, cy, cz = 0.0, body_radius, 0.0
    # radii of the blob ellipsoid
    rx, ry, rz = body_radius, body_radius * 1.05, body_radius * 0.85

    small = body_span_m * 0.16  # radius of each little body ball (overlap → dense)
    for _ in range(n_body):
        # sample a point inside a unit sphere, biased toward center for density
        while True:
            u = (rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))
            d2 = u[0] * u[0] + u[1] * u[1] + u[2] * u[2]
            if d2 <= 1.0:
                break
        # bias inward a touch so the surface stays lumpy but the core is solid
        bias = 0.5 + 0.5 * math.sqrt(d2)
        px = cx + u[0] * rx * bias
        py = cy + u[1] * ry * bias
        pz = cz + u[2] * rz * bias
        r = small * rng.uniform(0.75, 1.15)
        spheres.append(DemonSphere((px, py, pz), r, _hex_to_rgb(_PINK), "body"))

    # sort body big-first (matches DOOM: draw large body spheres first)
    spheres.sort(key=lambda s: s.radius, reverse=True)

    # ------- FEATURES (added AFTER body, nudged proud toward the player) -------
    # Player faces the demon from +Z (spawn is ~2.6m in front of the wall,
    # player stands further out on +Z), so the "face" is on the +Z side.
    face_z = cz + rz  # front surface of the blob

    eye_r = body_span_m * 0.12
    eye_dx = body_span_m * 0.22
    eye_y = cy + body_radius * 0.35
    eye_z = face_z + eye_r * 0.4  # sit proud of the body surface

    def nested_eye(sign: float) -> None:
        ex = sign * eye_dx
        # eyeball (blue)
        spheres.append(DemonSphere((ex, eye_y, eye_z), eye_r, _hex_to_rgb(_BLUE), "eye"))
        # pupil (black), smaller, pushed proud toward player (+Z)
        pupil_r = eye_r * 0.55
        pupil_z = eye_z + eye_r * 0.55
        spheres.append(DemonSphere((ex, eye_y, pupil_z), pupil_r, _hex_to_rgb(_BLACK), "pupil"))
        # glint (white), tiny, proud of pupil, offset up-left for a highlight
        glint_r = pupil_r * 0.45
        glint_z = pupil_z + pupil_r * 0.55
        gx = ex - sign * pupil_r * 0.3
        gy = eye_y + pupil_r * 0.3
        spheres.append(DemonSphere((gx, gy, glint_z), glint_r, _hex_to_rgb(_WHITE), "glint"))

    nested_eye(-1.0)  # left eye
    nested_eye(+1.0)  # right eye

    # ------- MOUTH: 5 upper + 5 lower white teeth, in an arc across the face -
    tooth_r = body_span_m * 0.055
    mouth_y = cy - body_radius * 0.25
    mouth_half_w = body_span_m * 0.28
    tooth_z = face_z + tooth_r * 0.6  # proud of the body
    gap = body_span_m * 0.05  # vertical gap between upper and lower rows

    for i in range(5):
        # -1 .. +1 across the mouth width
        t = (i / 4.0) * 2.0 - 1.0
        tx = t * mouth_half_w
        # slight downward arc at the corners
        arc = -(1.0 - t * t) * body_span_m * 0.03
        # upper tooth (points down): sits above the mouth line
        spheres.append(
            DemonSphere((tx, mouth_y + gap - arc, tooth_z), tooth_r, _hex_to_rgb(_WHITE), "tooth")
        )
        # lower tooth (points up): sits below the mouth line
        spheres.append(
            DemonSphere((tx, mouth_y - gap + arc, tooth_z), tooth_r, _hex_to_rgb(_WHITE), "tooth")
        )

    return spheres


def bob_offset(t: float) -> float:
    """Gentle vertical bob while alive: y += sin(t*2)*0.1 (matches DOOM)."""
    return math.sin(t * 2.0) * 0.1


def seed_explosion(spheres: list[DemonSphere], seed: int = 1729) -> None:
    """
    Assign each sphere a random fly-out direction (unit) × speed 2.5..4.0.
    Called once at kill time. Deterministic given seed. Mutates in place.
    Mirrors DOOM: direction = Vec3(uniform(-1,1), uniform(-0.3,1.0), uniform(-1,1))
    then normalized * uniform(2.5, 4.0).
    """
    rng = random.Random(seed)
    for s in spheres:
        dx = rng.uniform(-1.0, 1.0)
        dy = rng.uniform(-0.3, 1.0)
        dz = rng.uniform(-1.0, 1.0)
        length = math.sqrt(dx * dx + dy * dy + dz * dz) or 1.0
        dx, dy, dz = dx / length, dy / length, dz / length
        s.fly_dir = (dx, dy, dz)
        s.fly_speed = rng.uniform(2.5, 4.0)


# duration constants (match DOOM's 0.6s animate + 0.7s destroy)
EXPLODE_DUR = 0.6
GONE_AT = 0.7


def explosion_transform(
    sphere: DemonSphere, t: float
) -> tuple[tuple[float, float, float], float]:
    """
    PURE function of elapsed time since death.
    Returns (offset, scale_multiplier) for this sphere at time t.
      pos   = start_offset + fly_dir * fly_speed * t
      scale = radius * max(0, 1 - t/0.6)   (shrinks to nothing at t=0.6)
    scale_multiplier is the 0..1 factor (multiply sphere.radius by it).
    Fully gone (scale 0) for t >= EXPLODE_DUR.
    """
    ox, oy, oz = sphere.offset
    vx, vy, vz = sphere.fly_dir
    dist = sphere.fly_speed * t
    pos = (ox + vx * dist, oy + vy * dist, oz + vz * dist)
    scale_mult = max(0.0, 1.0 - t / EXPLODE_DUR)
    return pos, scale_mult


def is_gone(t: float) -> bool:
    """True once the whole demon has finished disintegrating."""
    return t >= GONE_AT


# ----------------------------------------------------------------------------
# UNIT-SPHERE MESH (pure CPU build; reused for every ball)
# ----------------------------------------------------------------------------
def build_unit_sphere_mesh(
    lat_bands: int = 10, lon_bands: int = 14
) -> tuple[np.ndarray, np.ndarray]:
    """
    Build a unit (radius 1) UV-sphere centered at origin.
    Returns (vertices, indices):
      vertices: float32 (N, 6) = position(3) + normal(3); for a unit sphere the
                position and normal are identical, but we pack both so the
                solid_program (which expects a normal) works unchanged.
      indices:  uint32 flat triangle list.
    Low-poly on purpose: ~100+ balls × small mesh stays cheap.
    """
    verts: list[float] = []
    for i in range(lat_bands + 1):
        theta = i * math.pi / lat_bands
        st, ct = math.sin(theta), math.cos(theta)
        for j in range(lon_bands + 1):
            phi = j * 2.0 * math.pi / lon_bands
            sp, cp = math.sin(phi), math.cos(phi)
            x = cp * st
            y = ct
            z = sp * st
            verts.extend([x, y, z, x, y, z])  # pos + normal (unit → same)

    idx: list[int] = []
    stride = lon_bands + 1
    for i in range(lat_bands):
        for j in range(lon_bands):
            a = i * stride + j
            b = a + stride
            idx.extend([a, b, a + 1, b, b + 1, a + 1])

    return (
        np.array(verts, dtype="f4").reshape(-1, 6),
        np.array(idx, dtype="u4"),
    )


# ----------------------------------------------------------------------------
# THIN GL SHELL (only touched when HAVE_GL)
# ----------------------------------------------------------------------------
def _mat_translate_scale(
    off: tuple[float, float, float], radius: float
) -> np.ndarray:
    """Column-major model matrix: uniform scale then translate. (row-major here;
    render_room's u_mvp path transposes in the shader, and we pre-multiply by
    the caller's view = proj@view, so we build in the same row-major convention
    render_room uses.)"""
    m = np.identity(4, dtype="f4")
    m[0, 0] = radius
    m[1, 1] = radius
    m[2, 2] = radius
    m[0, 3] = off[0]
    m[1, 3] = off[1]
    m[2, 3] = off[2]
    return m


@dataclass
class DemonRenderer:
    """
    Thin moderngl shell. One per (context) — caches the unit-sphere VAO.
    Draws the demon each frame using the shared solid_program with
    u_use_tint=2 (flat-lit solid base color).
    """
    ctx: "moderngl.Context"
    prog: "moderngl.Program"
    _vao: "moderngl.VertexArray" = field(default=None, init=False)
    _vbo: "moderngl.Buffer" = field(default=None, init=False)
    _ibo: "moderngl.Buffer" = field(default=None, init=False)
    _index_count: int = field(default=0, init=False)

    def __post_init__(self):
        if not HAVE_GL:
            return
        verts, idx = build_unit_sphere_mesh()
        self._vbo = self.ctx.buffer(verts.tobytes())
        self._ibo = self.ctx.buffer(idx.tobytes())
        self._index_count = len(idx)
        # solid_program vertex layout: in_pos (3f) + in_normal (3f)
        self._vao = self.ctx.vertex_array(
            self.prog,
            [(self._vbo, "3f 3f", "in_pos", "in_normal")],
            self._ibo,
        )

    def draw(
        self,
        view: np.ndarray,
        root_xyz: tuple[float, float, float],
        spheres: list[DemonSphere],
        t_since_death: Optional[float] = None,
        bob_t: float = 0.0,
    ) -> None:
        """
        view       : proj @ view (world→clip), row-major float32 (as render_room).
        root_xyz   : spawn_xyz (demon center on the floor).
        spheres    : the built demon spheres.
        t_since_death: None while alive; float seconds once dead.
        bob_t      : elapsed alive-time for the bob (ignored when dead).
        """
        if not HAVE_GL:
            return
        if t_since_death is not None and is_gone(t_since_death):
            return  # fully disintegrated → draw nothing

        self.prog["u_use_tint"].value = 2  # flat-lit solid base color

        rx, ry, rz = root_xyz
        # bob only while alive
        by = bob_offset(bob_t) if t_since_death is None else 0.0

        for s in spheres:
            if t_since_death is None:
                off = s.offset
                r = s.radius
            else:
                off, mult = explosion_transform(s, t_since_death)
                r = s.radius * mult
                if r <= 1e-5:
                    continue
            world_off = (rx + off[0], ry + off[1] + by, rz + off[2])
            model = _mat_translate_scale(world_off, r)
            mvp = view @ model  # row-major: clip = view * model * pos
            self.prog["u_mvp"].write(mvp.astype("f4").tobytes())
            self.prog["u_tint"].value = s.color
            self._vao.render(moderngl.TRIANGLES, vertices=self._index_count)
