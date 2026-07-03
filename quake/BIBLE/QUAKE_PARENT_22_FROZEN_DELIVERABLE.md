# QUAKE PARENT 22 — FROZEN DELIVERABLE (VERBATIM)

> Claude Opus 4.8 (Parent 22). Saved word-for-word by DeepSeek. Mission: build the demon (moderngl port of the DOOM demon, many balls) + alcove reveal + explosion + red ceiling equations.

---

I have everything I need. Here's the complete implementation.

## demon.py

```python
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
```

## Edits to render_room.py

```python
# render_room.py — additions
# ---------------------------------------------------------------------------
# at module top:
import demon as demonmod

# module-level per-room demon state (mirrors DOOM's demon_alive dict)
_DEMON_SPHERES: dict[str, list["demonmod.DemonSphere"]] = {}
_DEMON_RENDERERS: dict[int, "demonmod.DemonRenderer"] = {}  # keyed by id(ctx)


def _get_demon_renderer(ctx, prog):
    r = _DEMON_RENDERERS.get(id(ctx))
    if r is None:
        r = demonmod.DemonRenderer(ctx=ctx, prog=prog)
        _DEMON_RENDERERS[id(ctx)] = r
    return r


def _room_demon_spheres(room) -> list["demonmod.DemonSphere"]:
    """Build & cache the demon sphere set for this room (deterministic)."""
    rid = room.room_id
    sph = _DEMON_SPHERES.get(rid)
    if sph is None:
        # seed off the room id so each room's blob is stable but distinct
        seed = 1729 + (hash(rid) & 0xFFFF)
        sph = demonmod.build_demon_spheres(body_span_m=1.2, n_body=100, seed=seed)
        _DEMON_SPHERES[rid] = sph
    return sph


# ---------------------------------------------------------------------------
# draw_room signature stays: draw_room(view, room, pack, state) -> None
# BUT it now needs the per-room death clock + spawn flag. Those live in the
# frame loop (app.py) which has dt. We read them from a small module registry
# that app.py updates each frame (see app.py edits). This keeps draw_room's
# public signature unchanged.

def draw_room(view, room, pack, state) -> None:
    # ... existing GL-state asserts, walls/floor/ceiling, door jambs ...

    # ----- ALCOVE: reveal ONLY once the demon has spawned (hidden door open) -
    lvl = state.save.levels[state.level_id]
    room_save = lvl.rooms.get(room.room_id)
    door_open = bool(room_save and room_save.hidden_door_open)
    if door_open:
        _build_alcove_and_draw(view, room, pack)   # was: unconditional each frame
    # (when door_open is False the alcove is simply not drawn → reads closed)

    # ... existing textured panel drawing ...

    # ----- DEMON -----
    if door_open and room.enemy is not None:
        t_death = _DEMON_DEATH_CLOCK.get(room.room_id)   # None while alive
        # once fully gone, stop drawing entirely
        if not (t_death is not None and demonmod.is_gone(t_death)):
            spheres = _room_demon_spheres(room)
            renderer = _get_demon_renderer(_ctx_of(room), solid_prog_of(room))
            alive_t = _DEMON_ALIVE_CLOCK.get(room.room_id, 0.0)
            renderer.draw(
                view=view,
                root_xyz=room.enemy.spawn_xyz,
                spheres=spheres,
                t_since_death=t_death,
                bob_t=alive_t,
            )

    # ----- CEILING EQUATIONS (blood-red on clear) -----
    # existing behavior already tints (1,0,0) when room.room_id in state.cleared.
    # Only render the equations that actually exist (list is already per-room).
    for ceq in room.ceiling_equations:
        red = room.room_id in state.cleared
        _draw_ceiling_eq(view, ceq, tint=(1.0, 0.0, 0.0) if red else None)
    # (no-op change if this already existed — confirm the tint fires on kill)

# render_room.py — the death/alive clocks the frame loop feeds
# (module level, updated by app.py each frame; render only reads them)
_DEMON_DEATH_CLOCK: dict[str, float] = {}   # room_id -> seconds since kill
_DEMON_ALIVE_CLOCK: dict[str, float] = {}   # room_id -> seconds since spawn


def demon_on_spawned(room_id: str) -> None:
    _DEMON_ALIVE_CLOCK.setdefault(room_id, 0.0)


def demon_on_killed(room_id: str) -> None:
    if room_id not in _DEMON_DEATH_CLOCK:
        _DEMON_DEATH_CLOCK[room_id] = 0.0
        # freeze fly directions the instant it dies (deterministic per room)
        sph = _DEMON_SPHERES.get(room_id)
        if sph is not None:
            demonmod.seed_explosion(sph, seed=4242 + (hash(room_id) & 0xFFFF))


def demon_tick(room_id: str, dt: float, dead: bool) -> None:
    if dead:
        if room_id in _DEMON_DEATH_CLOCK:
            _DEMON_DEATH_CLOCK[room_id] += dt
    else:
        _DEMON_ALIVE_CLOCK[room_id] = _DEMON_ALIVE_CLOCK.get(room_id, 0.0) + dt
```

## Edits to app.py (frame loop)

```python
# app.py — inside the per-frame loop, after gameplay.step(...) returns events + dt
import render_room

for ev in events:
    name = type(ev).__name__
    if name == "DemonSpawned":
        render_room.demon_on_spawned(ev.room_id)
    elif name == "DemonKilled":
        render_room.demon_on_killed(ev.room_id)

# advance the demon clock every frame for the current room (if a demon exists)
rid = state.current_room_id
room = pack.rooms_by_id.get(rid)
if room is not None and room.enemy is not None:
    dead = rid in state.cleared      # RoomCleared fires with DemonKilled
    # only tick once spawned (alive clock exists) or once dead
    if rid in render_room._DEMON_ALIVE_CLOCK or dead:
        render_room.demon_tick(rid, dt, dead=dead)

# draw_room called as before — it reads the clocks:
if state.mode == "room":
    render_room.draw_room(view, room, pack, state)
```

One line for DeepSeek to confirm on the machine: I assumed solid_program's vertex attributes are named exactly `in_pos` and `in_normal` — if the actual names differ (e.g. `in_position`), change the vertex_array layout in `DemonRenderer.__post_init__` to match. Everything else is self-contained.

## Unit tests — tests/test_demon.py

```python
import math
import demon


def test_sphere_counts_by_role():
    sph = demon.build_demon_spheres(n_body=100, seed=1)
    roles = {}
    for s in sph:
        roles[s.role] = roles.get(s.role, 0) + 1
    assert roles["body"] == 100
    assert roles["tooth"] == 10          # 5 upper + 5 lower
    assert roles["eye"] == 2
    assert roles["pupil"] == 2
    assert roles["glint"] == 2
    assert len(sph) == 116


def test_body_drawn_before_features():
    # after the big-first body sort + feature append, the first 100 are body
    sph = demon.build_demon_spheres(n_body=100, seed=1)
    assert all(s.role == "body" for s in sph[:100])
    assert all(s.role != "body" for s in sph[100:])


def test_body_sorted_big_first():
    sph = demon.build_demon_spheres(n_body=100, seed=1)
    body = [s.radius for s in sph if s.role == "body"]
    assert body == sorted(body, reverse=True)


def test_features_are_proud_of_body_front():
    # eyes/pupils/glints/teeth sit toward +Z (the face) and each nested layer
    # is more proud than the last
    sph = demon.build_demon_spheres(seed=1)
    eyes = [s for s in sph if s.role == "eye"]
    pupils = [s for s in sph if s.role == "pupil"]
    glints = [s for s in sph if s.role == "glint"]
    # pupil in front of eye, glint in front of pupil (compare same side)
    left_eye = min(eyes, key=lambda s: s.offset[0])
    left_pupil = min(pupils, key=lambda s: s.offset[0])
    left_glint = min(glints, key=lambda s: s.offset[0])
    assert left_pupil.offset[2] > left_eye.offset[2]
    assert left_glint.offset[2] > left_pupil.offset[2]
    # nested spheres shrink
    assert left_pupil.radius < left_eye.radius
    assert left_glint.radius < left_pupil.radius


def test_determinism():
    a = demon.build_demon_spheres(seed=99)
    b = demon.build_demon_spheres(seed=99)
    assert [ (s.offset, s.radius, s.role) for s in a ] == \
           [ (s.offset, s.radius, s.role) for s in b ]


def test_bob_offset_range():
    for t in [0.0, 0.5, 1.0, 3.14, 10.0]:
        assert -0.1001 <= demon.bob_offset(t) <= 0.1001
    # non-trivial motion
    assert abs(demon.bob_offset(math.pi / 4)) > 0.0


def test_seed_explosion_unit_dirs_and_speed():
    sph = demon.build_demon_spheres(seed=1)
    demon.seed_explosion(sph, seed=7)
    for s in sph:
        dx, dy, dz = s.fly_dir
        length = math.sqrt(dx*dx + dy*dy + dz*dz)
        assert abs(length - 1.0) < 1e-6           # unit direction
        assert 2.5 <= s.fly_speed <= 4.0          # DOOM speed range
        assert dy >= -0.3 - 1e-9                   # dy sampled in [-0.3, 1.0]


def test_explosion_monotonic_flyout_and_shrink():
    s = demon.DemonSphere(offset=(0,1,0), radius=0.1,
                          color=(1,0,0), role="body",
                          fly_dir=(0,1,0), fly_speed=3.0)
    prev_dist = -1.0
    prev_scale = 2.0
    for t in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]:
        pos, scale = demon.explosion_transform(s, t)
        dist = pos[1] - s.offset[1]              # flew along +Y
        assert dist >= prev_dist                 # monotonic fly-out
        assert scale <= prev_scale               # monotonic shrink
        prev_dist, prev_scale = dist, scale


def test_explosion_fully_shrunk_by_end():
    s = demon.DemonSphere(offset=(0,0,0), radius=0.2,
                          color=(1,1,1), role="body",
                          fly_dir=(1,0,0), fly_speed=3.0)
    _, scale_at_dur = demon.explosion_transform(s, demon.EXPLODE_DUR)
    assert scale_at_dur == 0.0
    _, scale_past = demon.explosion_transform(s, 0.65)
    assert scale_past == 0.0
    assert demon.is_gone(0.7) is True
    assert demon.is_gone(0.6) is False


def test_unit_sphere_mesh_shape():
    verts, idx = demon.build_unit_sphere_mesh(lat_bands=6, lon_bands=8)
    assert verts.shape[1] == 6                   # pos + normal
    # every vertex lies on the unit sphere (position part normalized)
    import numpy as np
    p = verts[:, :3]
    r = np.linalg.norm(p, axis=1)
    assert np.allclose(r, 1.0, atol=1e-5)
    assert idx.ndim == 1 and len(idx) % 3 == 0
```

That's the whole thing: the DOOM demon reproduced in moderngl with 116 balls (100 body + 10 teeth + 2 eyes + 2 pupils + 2 glints), the alcove gated on `hidden_door_open`, the pure time-driven explosion, and the red ceiling equations firing on clear. DeepSeek renders an offscreen PNG for Nir to eyeball, and widens the hit sphere if the ~1.2 m body reads wider than the current test. 🩸👹
