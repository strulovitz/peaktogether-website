"""QUAKE runtime engine — M6, module #10: render_room.py

Mode B solid first-person room renderer.

SPLIT:
  - PURE core: geometry, numpy, zero GL. Fully unit-tested.
  - THIN shell: GL draw, guarded for headless. Never crashes on import.

COORDINATES ARE LAW:
  Room box axis-aligned. dimensions_m = (W, H, D).
  X in [-W/2, W/2], Y in [0, H], Z in [-D/2, D/2].
  N wall z=+D/2 (inward -Z), S z=-D/2 (inward +Z),
  E x=+W/2 (inward -X), W x=-W/2 (inward +X), floor y=0, ceiling y=H.
  Room-local axes parallel to map axes (NO rotation).

NOTE (Parent 11 integration): the PURE CORE below is unchanged. The THIN GL
SHELL at the bottom was rebuilt (moderngl.get_context, per-context program
cache, per-room VAO cache, synthesized flat normals, real uniforms, correct
manifest texture resolve, explicit per-frame GL-state assert).
"""

from __future__ import annotations

import math
import os
import time
from dataclasses import dataclass, field

import numpy as np

# ---- SHARED TYPES: import ONLY from contracts. Never redefine. ----
from contracts import (
    RoomRuntime,
    DoorRT,
    PanelPairRT,
    PanelPlacementRT,
    ViewMatrix,
    Pack,
    GameState,
    Vec3,
    PairId,
)

# ---- PINNED CONSTANTS (pure builders) ----
DOOR_JAMB_DEPTH_M = 0.3
ALCOVE_DEPTH_M = 0.4
PANEL_INSET_M = 0.02  # panel sits just off the wall to avoid z-fight
CEILING_DROP_M = 0.05  # ceiling-equation quad hangs just below the ceiling (no z-fight)

# Ceiling equation manual toggle (C key)
_show_ceilings: bool = False


def toggle_ceilings() -> bool:
    global _show_ceilings
    _show_ceilings = not _show_ceilings
    return _show_ceilings


# ======================================================================
# PURE CORE DATA STRUCTURES
# ======================================================================
@dataclass
class PanelQuad:
    """One panel (drawing or text) in the room."""
    pair_id: PairId
    is_drawing: bool
    off_asset_id: str
    on_asset_id: str
    corners: np.ndarray  # (4, 3) float32 — world-space quad corners
    uv: np.ndarray       # (4, 2) float32 — texture coordinates


@dataclass
class RoomMesh:
    """All geometry for one room. Pure data, zero GL."""
    wall_tris: np.ndarray         # (Nw, 3, 3) float32
    wall_uvs: np.ndarray          # (Nw, 3, 2) float32
    door_frame_tris: np.ndarray   # (Nd, 3, 3) float32
    panel_quads: list[PanelQuad] = field(default_factory=list)
    ceiling_quads: list[PanelQuad] = field(default_factory=list)
    alcove_tris: np.ndarray = field(
        default_factory=lambda: np.zeros((0, 3, 3), dtype=np.float32)
    )


# ======================================================================
# PURE GEOMETRY HELPERS
# ======================================================================
_EMPTY_TRIS = lambda: np.zeros((0, 3, 3), dtype=np.float32)
_EMPTY_UVS = lambda: np.zeros((0, 3, 2), dtype=np.float32)


def _quad_to_tris(p0, p1, p2, p3):
    """Two triangles for a quad with corners in order p0->p1->p2->p3.

    Returns (2, 3, 3) float32. Winding: (p0,p1,p2) and (p0,p2,p3).
    """
    p0 = np.asarray(p0, dtype=np.float32)
    p1 = np.asarray(p1, dtype=np.float32)
    p2 = np.asarray(p2, dtype=np.float32)
    p3 = np.asarray(p3, dtype=np.float32)
    return np.array(
        [[p0, p1, p2], [p0, p2, p3]], dtype=np.float32
    )


def _quad_uvs():
    """Standard UVs matching _quad_to_tris triangle ordering."""
    uv0 = (0.0, 0.0)
    uv1 = (1.0, 0.0)
    uv2 = (1.0, 1.0)
    uv3 = (0.0, 1.0)
    return np.array(
        [[uv0, uv1, uv2], [uv0, uv2, uv3]], dtype=np.float32
    )


def _wall_basis(wall: str):
    """Return (along_axis, inward_normal, plane_axis_index) for a wall.

    'along' is the unit vector along the wall horizontally.
    'inward' is the unit inward normal of the wall.
    """
    if wall == "N":   # z = +D/2, inward -Z, along +X
        return np.array([1.0, 0.0, 0.0], np.float32), np.array([0.0, 0.0, -1.0], np.float32)
    if wall == "S":   # z = -D/2, inward +Z, along -X (opposite of N — viewer faces opposite direction)
        return np.array([-1.0, 0.0, 0.0], np.float32), np.array([0.0, 0.0, 1.0], np.float32)
    if wall == "E":   # x = +W/2, inward -X, along -Z
        return np.array([0.0, 0.0, -1.0], np.float32), np.array([-1.0, 0.0, 0.0], np.float32)
    if wall == "W":   # x = -W/2, inward +X, along +Z
        return np.array([0.0, 0.0, 1.0], np.float32), np.array([1.0, 0.0, 0.0], np.float32)
    raise ValueError(f"unknown wall {wall!r}")


def _wall_corners(wall: str, W: float, H: float, D: float):
    """Return the 4 corners (CCW seen from inside) of a full wall quad.

    Order chosen so corners go around the rectangle:
    bottom-left, bottom-right, top-right, top-left in the wall's
    (along, up) frame.
    """
    if wall == "N":
        z = D / 2.0
        return (
            (-W / 2, 0.0, z), (W / 2, 0.0, z),
            (W / 2, H, z), (-W / 2, H, z),
        )
    if wall == "S":
        z = -D / 2.0
        return (
            (-W / 2, 0.0, z), (W / 2, 0.0, z),
            (W / 2, H, z), (-W / 2, H, z),
        )
    if wall == "E":
        x = W / 2.0
        return (
            (x, 0.0, -D / 2), (x, 0.0, D / 2),
            (x, H, D / 2), (x, H, -D / 2),
        )
    if wall == "W":
        x = -W / 2.0
        return (
            (x, 0.0, -D / 2), (x, 0.0, D / 2),
            (x, H, D / 2), (x, H, -D / 2),
        )
    raise ValueError(f"unknown wall {wall!r}")


def _wall_along_coord(wall: str, xyz):
    """The scalar coordinate of a point along the wall's horizontal axis."""
    x, y, z = xyz
    if wall in ("N", "S"):
        return x
    return z  # E / W -> z


def _wall_along_extent(wall: str, W: float, D: float):
    """Half-extent of the wall along its horizontal axis."""
    if wall in ("N", "S"):
        return W / 2.0
    return D / 2.0


def _wall_fixed_value(wall: str, W: float, D: float):
    """The fixed plane coordinate of the wall (z for N/S, x for E/W)."""
    if wall == "N":
        return D / 2.0
    if wall == "S":
        return -D / 2.0
    if wall == "E":
        return W / 2.0
    if wall == "W":
        return -W / 2.0
    raise ValueError(wall)


def _point_on_wall(wall: str, along: float, y: float, W: float, D: float):
    """Build a 3D point on the wall plane from (along, y)."""
    fixed = _wall_fixed_value(wall, W, D)
    if wall in ("N", "S"):
        return (along, y, fixed)
    # E / W: fixed is x, along is z
    return (fixed, y, along)


def _build_wall_with_holes(wall: str, room: RoomRuntime):
    """Build wall quad(s) subtracting door holes on this wall.

    Returns (tris (N,3,3), uvs (N,3,2)).
    """
    W, H, D = room.dimensions_m
    half = _wall_along_extent(wall, W, D)
    a_min, a_max = -half, half

    # collect doors on this wall as (along_lo, along_hi, height)
    holes = []
    for d in room.doors:
        if d.wall != wall:
            continue
        c = _wall_along_coord(wall, d.center_xyz)
        lo = c - d.width_m / 2.0
        hi = c + d.width_m / 2.0
        holes.append((lo, hi, d.height_m))

    tris_list = []
    uvs_list = []

    if not holes:
        c = _wall_corners(wall, W, H, D)
        tris_list.append(_quad_to_tris(*c))
        uvs_list.append(_quad_uvs())
        return (
            np.concatenate(tris_list, axis=0),
            np.concatenate(uvs_list, axis=0),
        )

    # Sort holes left->right along wall.
    holes.sort(key=lambda h: h[0])

    def add_region(lo, hi, y0, y1):
        if hi - lo <= 1e-9 or y1 - y0 <= 1e-9:
            return
        p0 = _point_on_wall(wall, lo, y0, W, D)
        p1 = _point_on_wall(wall, hi, y0, W, D)
        p2 = _point_on_wall(wall, hi, y1, W, D)
        p3 = _point_on_wall(wall, lo, y1, W, D)
        tris_list.append(_quad_to_tris(p0, p1, p2, p3))
        uvs_list.append(_quad_uvs())

    cursor = a_min
    for lo, hi, dh in holes:
        # left solid region between cursor and the hole, full height
        add_region(cursor, lo, 0.0, H)
        # region above the hole
        add_region(lo, hi, dh, H)
        # (below the hole is the doorway floor -> no region)
        cursor = hi
    # remaining region to the right of last hole, full height
    add_region(cursor, a_max, 0.0, H)

    if not tris_list:
        return _EMPTY_TRIS(), _EMPTY_UVS()
    return (
        np.concatenate(tris_list, axis=0),
        np.concatenate(uvs_list, axis=0),
    )


def _build_floor_ceiling(room: RoomRuntime):
    W, H, D = room.dimensions_m
    # floor y=0
    floor = _quad_to_tris(
        (-W / 2, 0.0, -D / 2), (W / 2, 0.0, -D / 2),
        (W / 2, 0.0, D / 2), (-W / 2, 0.0, D / 2),
    )
    # ceiling y=H
    ceil = _quad_to_tris(
        (-W / 2, H, -D / 2), (W / 2, H, -D / 2),
        (W / 2, H, D / 2), (-W / 2, H, D / 2),
    )
    tris = np.concatenate([floor, ceil], axis=0)
    uvs = np.concatenate([_quad_uvs(), _quad_uvs()], axis=0)
    return tris, uvs


def _build_door_jambs(room: RoomRuntime):
    """Recessed inward-facing jamb strips around each door opening.

    For each door: top jamb, left jamb, right jamb — short strips
    going from the wall plane inward by DOOR_JAMB_DEPTH_M.
    """
    W, H, D = room.dimensions_m
    tris_list = []
    for d in room.doors:
        wall = d.wall
        _, inward = _wall_basis(wall)
        c_along = _wall_along_coord(wall, d.center_xyz)
        lo = c_along - d.width_m / 2.0
        hi = c_along + d.width_m / 2.0
        dh = d.height_m
        depth = DOOR_JAMB_DEPTH_M

        def wp(along, y, off):
            """point on wall offset inward by `off`."""
            base = np.asarray(_point_on_wall(wall, along, y, W, D), np.float32)
            return base + inward * off

        # Top jamb: horizontal strip at y=dh, from wall plane inward.
        tris_list.append(_quad_to_tris(
            wp(lo, dh, 0.0), wp(hi, dh, 0.0),
            wp(hi, dh, depth), wp(lo, dh, depth),
        ))
        # Left jamb: vertical strip at along=lo, from floor to dh.
        tris_list.append(_quad_to_tris(
            wp(lo, 0.0, 0.0), wp(lo, 0.0, depth),
            wp(lo, dh, depth), wp(lo, dh, 0.0),
        ))
        # Right jamb: vertical strip at along=hi, floor to dh.
        tris_list.append(_quad_to_tris(
            wp(hi, 0.0, 0.0), wp(hi, 0.0, depth),
            wp(hi, dh, depth), wp(hi, dh, 0.0),
        ))

    if not tris_list:
        return _EMPTY_TRIS()
    return np.concatenate(tris_list, axis=0)


def _placement_corners(center: Vec3, width: float, height: float,
                       yaw_rad: float, inset: float):
    """Build the 4 world-space corners of a flat panel quad.

    The panel normal is given by yaw_rad: normal = (sin yaw, 0, cos yaw)
    (so yaw=0 -> +Z, yaw=pi -> -Z, yaw=pi/2 -> +X). The panel's local
    'right' (horizontal) axis is perpendicular to the normal in the XZ
    plane; the local 'up' axis is +Y.

    The center is offset by `inset` along the normal (off the wall).
    Returns (4,3) float32 corners in order BL, BR, TR, TL.
    """
    cx, cy, cz = center
    normal = np.array(
        [math.sin(yaw_rad), 0.0, math.cos(yaw_rad)], dtype=np.float32
    )
    # right axis: rotate normal -90deg about Y so panel spans horizontally
    right = np.array(
        [math.cos(yaw_rad), 0.0, -math.sin(yaw_rad)], dtype=np.float32
    )
    up = np.array([0.0, 1.0, 0.0], dtype=np.float32)

    c = np.array([cx, cy, cz], dtype=np.float32) + normal * inset
    hw = width / 2.0
    hh = height / 2.0

    bl = c - right * hw - up * hh
    br = c + right * hw - up * hh
    tr = c + right * hw + up * hh
    tl = c - right * hw + up * hh
    return np.array([bl, br, tr, tl], dtype=np.float32)


def _panel_corners_on_wall(wall, center, width, height, inset):
    """Flat panel corners lying ON the given wall, facing INTO the room.

    Robust orientation: derived from the `wall` field (unambiguous) rather than
    `yaw_rad` — the room data's yaw convention (normal=(cos,sin)) differs from the
    old renderer's (normal=(sin,cos)), which made panels render perpendicular to
    the wall. Using the wall basis makes panels always parallel to their wall.
    Returns (4,3) float32 corners in order BL, BR, TR, TL.
    """
    along, inward = _wall_basis(wall)
    up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    c = np.asarray(center, dtype=np.float32) + inward * inset
    hw, hh = width / 2.0, height / 2.0
    bl = c - along * hw - up * hh
    br = c + along * hw - up * hh
    tr = c + along * hw + up * hh
    tl = c - along * hw + up * hh
    return np.array([bl, br, tr, tl], dtype=np.float32)


def _flip_u(uv: np.ndarray) -> np.ndarray:
    out = uv.copy()
    out[:, 0] = 1.0 - out[:, 0]
    return out


def _expand_quad(corners: np.ndarray, factor: float) -> np.ndarray:
    """Scale a (4,3) quad about its own center by `factor` (for the glow halo)."""
    c = corners.mean(axis=0)
    return (c + (corners - c) * factor).astype(np.float32)


def _build_panel_quads(room: RoomRuntime):
    quads: list[PanelQuad] = []
    uv = np.array(
        [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]], dtype=np.float32
    )
    for pair in room.panel_pairs:
        dp = pair.drawing_placement
        tp = pair.text_placement
        d_corners = _panel_corners_on_wall(
            dp.wall, dp.center_xyz, dp.width_m, dp.height_m, PANEL_INSET_M
        )
        quads.append(PanelQuad(
            pair_id=pair.pair_id,
            is_drawing=True,
            off_asset_id=pair.drawing_off_asset,
            on_asset_id=pair.drawing_on_asset,
            corners=d_corners,
            uv=uv.copy(),
        ))
        t_corners = _panel_corners_on_wall(
            tp.wall, tp.center_xyz, tp.width_m, tp.height_m, PANEL_INSET_M
        )
        quads.append(PanelQuad(
            pair_id=pair.pair_id,
            is_drawing=False,
            off_asset_id=pair.text_off_asset,
            on_asset_id=pair.text_on_asset,
            corners=t_corners,
            uv=uv.copy(),
        ))
    return quads


def _build_ceiling_quads(room: RoomRuntime):
    quads: list[PanelQuad] = []
    # UV maps per wall — each viewer looks AT the wall then UP, so text must read left-to-right
    uv_n = np.array([[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]], dtype=np.float32)  # V-flipped
    uv_s = np.array([[1.0,0.0],[0.0,0.0],[0.0,1.0],[1.0,1.0]], dtype=np.float32)  # 180° from N
    uv_e = np.array([[1.0,1.0],[1.0,0.0],[0.0,0.0],[0.0,1.0]], dtype=np.float32)  # 90° cw
    uv_w = np.array([[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0]], dtype=np.float32)  # 90° ccw
    for eq in room.ceiling_equations:
        cx, cy, cz = eq.pos_xyz
        cy = cy - CEILING_DROP_M
        w, d = eq.size_m
        # Determine which wall the equation is near
        dominant_z = abs(cz) >= abs(cx)
        if dominant_z:
            if cz > 0:   # N wall: text along X, V-flipped
                eq_uv = uv_n.copy()
                is_ns = True
            else:         # S wall: text along X, 180° rotated
                eq_uv = uv_s.copy()
                is_ns = True
        else:
            if cx > 0:   # E wall: text along Z, 90° cw
                eq_uv = uv_e.copy()
                is_ns = False
            else:         # W wall: text along Z, 90° ccw
                eq_uv = uv_w.copy()
                is_ns = False
        if not is_ns:
            hw_e = d / 2.0
            hd_e = w / 2.0
        else:
            hw_e = w / 2.0
            hd_e = d / 2.0
        # Facing downward (-Y). Corners in XZ plane at y = cy.
        bl = (cx - hw_e, cy, cz - hd_e)
        br = (cx + hw_e, cy, cz - hd_e)
        tr = (cx + hw_e, cy, cz + hd_e)
        tl = (cx - hw_e, cy, cz + hd_e)
        corners = np.array([bl, br, tr, tl], dtype=np.float32)
        quads.append(PanelQuad(
            pair_id=eq.asset_id,  # not a true pair_id; ceilings don't toggle
            is_drawing=True,
            off_asset_id=eq.asset_id,
            on_asset_id=eq.asset_id,
            corners=corners,
            uv=eq_uv,
        ))
    return quads


def _build_alcove(room: RoomRuntime):
    """Build a shallow recessed box at the final pair's drawing position.

    NOT a through-hole: it's a 5-sided box pushed inward by ALCOVE_DEPTH_M
    (back face + 4 side faces). The front (wall plane) stays open visually
    but the wall remains solid (we do NOT cut a hole there).
    """
    final_pair = None
    for pair in room.panel_pairs:
        if pair.pair_id == room.final_pair_id:
            final_pair = pair
            break
    if final_pair is None:
        return _EMPTY_TRIS()

    placement = final_pair.drawing_placement
    wall = placement.wall
    W, H, D = room.dimensions_m
    _, inward = _wall_basis(wall)

    cx, cy, cz = placement.center_xyz
    w = placement.width_m
    h = placement.height_m
    depth = ALCOVE_DEPTH_M

    # local right axis along the wall (horizontal)
    if wall in ("N", "S"):
        right = np.array([1.0, 0.0, 0.0], np.float32)
    else:
        right = np.array([0.0, 0.0, 1.0], np.float32)
    up = np.array([0.0, 1.0, 0.0], np.float32)
    center = np.array([cx, cy, cz], np.float32)

    hw, hh = w / 2.0, h / 2.0

    # Front rim corners (on the wall plane)
    f_bl = center - right * hw - up * hh
    f_br = center + right * hw - up * hh
    f_tr = center + right * hw + up * hh
    f_tl = center - right * hw + up * hh

    # Back corners (pushed into the wall = opposite of inward normal)
    push = -inward * depth
    b_bl = f_bl + push
    b_br = f_br + push
    b_tr = f_tr + push
    b_tl = f_tl + push

    tris_list = []
    # Back face (facing back toward room, i.e. inward normal)
    tris_list.append(_quad_to_tris(b_bl, b_br, b_tr, b_tl))
    # Top face
    tris_list.append(_quad_to_tris(f_tl, f_tr, b_tr, b_tl))
    # Bottom face
    tris_list.append(_quad_to_tris(f_bl, f_br, b_br, b_bl))
    # Left face
    tris_list.append(_quad_to_tris(f_bl, b_bl, b_tl, f_tl))
    # Right face
    tris_list.append(_quad_to_tris(f_br, b_br, b_tr, f_tr))

    return np.concatenate(tris_list, axis=0)


# ======================================================================
# PURE CORE — FROZEN SIGNATURES
# ======================================================================
def build_room_mesh(room: RoomRuntime) -> RoomMesh:
    """Build all geometry for a room. PURE, deterministic, no GL."""
    wall_tris_list = []
    wall_uvs_list = []

    for wall in ("N", "S", "E", "W"):
        t, u = _build_wall_with_holes(wall, room)
        if t.shape[0]:
            wall_tris_list.append(t)
            wall_uvs_list.append(u)

    fc_t, fc_u = _build_floor_ceiling(room)
    wall_tris_list.append(fc_t)
    wall_uvs_list.append(fc_u)

    if wall_tris_list:
        wall_tris = np.concatenate(wall_tris_list, axis=0).astype(np.float32)
        wall_uvs = np.concatenate(wall_uvs_list, axis=0).astype(np.float32)
    else:
        wall_tris = _EMPTY_TRIS()
        wall_uvs = _EMPTY_UVS()

    door_frame_tris = _build_door_jambs(room)
    panel_quads = _build_panel_quads(room)
    ceiling_quads = _build_ceiling_quads(room)
    alcove_tris = _build_alcove(room)

    return RoomMesh(
        wall_tris=wall_tris,
        wall_uvs=wall_uvs,
        door_frame_tris=door_frame_tris,
        panel_quads=panel_quads,
        ceiling_quads=ceiling_quads,
        alcove_tris=alcove_tris,
    )


def panel_is_on(pair_id: PairId, lit: set[str], room: RoomRuntime) -> bool:
    """A pair is "on" iff its pair_id is in `lit` (how gameplay.resolve_shot
    records it) OR any of its asset IDs are in `lit` (legacy asset-keyed form)."""
    if pair_id in lit:
        return True
    for pair in room.panel_pairs:
        if pair.pair_id != pair_id:
            continue
        return (
            pair.drawing_on_asset in lit
            or pair.text_on_asset in lit
            or pair.drawing_off_asset in lit
            or pair.text_off_asset in lit
        )
    return False


# ======================================================================
# THIN GL SHELL (Parent 11 rebuild — lit, fixed, cached)
# ======================================================================
try:
    from glguard import HAVE_GL
except Exception:
    HAVE_GL = False

WALL_RGB   = (0.62, 0.60, 0.66)
JAMB_RGB   = (0.40, 0.38, 0.44)
ALCOVE_RGB = (0.30, 0.28, 0.34)
LIGHT_DIR  = (0.40, 0.85, 0.35)   # normalized below
AMBIENT    = 0.5

_prog_cache: dict = {}            # ctx-id -> solid program
_mesh_cache: dict = {}            # room_id -> RoomMesh
_vao_cache:  dict = {}            # room_id -> dict of VAOs
_texture_cache: dict = {}         # asset_id -> texture|None

# ---- DEMON (Parent 22): per-room sphere sets + clocks fed by app.py -------
import demon as demonmod

_DEMON_SPHERES: dict = {}         # room_id -> list[DemonSphere]
_DEMON_RENDERERS: dict = {}       # id(ctx) -> DemonRenderer
_DEMON_DEATH_CLOCK: dict = {}     # room_id -> seconds since kill
_DEMON_ALIVE_CLOCK: dict = {}     # room_id -> seconds since spawn
_DEMON_POS: dict = {}             # room_id -> (x, z) current position
_DEMON_YAW: dict = {}             # room_id -> facing yaw (rad)
_DEMON_SPAWN_Y: dict = {}         # room_id -> floor y for the demon root


def _room_demon_spheres(room):
    """Build & cache the demon sphere set for this room (deterministic)."""
    rid = room.room_id
    sph = _DEMON_SPHERES.get(rid)
    if sph is None:
        seed = 1729 + (abs(hash(rid)) & 0xFFFF)
        sph = demonmod.build_demon_spheres(body_span_m=1.2, n_body=100, seed=seed)
        _DEMON_SPHERES[rid] = sph
    return sph


def _get_demon_renderer(ctx, prog):
    r = _DEMON_RENDERERS.get(id(ctx))
    if r is None:
        r = demonmod.DemonRenderer(ctx=ctx, prog=prog)
        _DEMON_RENDERERS[id(ctx)] = r
    return r


def demon_on_spawned(room_id: str, spawn_xyz=None) -> None:
    _DEMON_ALIVE_CLOCK.setdefault(room_id, 0.0)
    if spawn_xyz is not None and room_id not in _DEMON_POS:
        _DEMON_POS[room_id] = (spawn_xyz[0], spawn_xyz[2])
        _DEMON_YAW[room_id] = 0.0
        _DEMON_SPAWN_Y[room_id] = spawn_xyz[1]


def demon_update(room_id: str, dt: float, player_xz) -> None:
    """Alive-only: creep toward the player, and aim (+ slow scan) at them."""
    if room_id not in _DEMON_POS:
        return
    t = _DEMON_ALIVE_CLOCK.get(room_id, 0.0)
    pos = demonmod.approach(_DEMON_POS[room_id], player_xz, dt)
    _DEMON_POS[room_id] = pos
    _DEMON_YAW[room_id] = demonmod.face_yaw(pos, player_xz) + demonmod.scan_yaw(t)


def demon_on_killed(room_id: str) -> None:
    if room_id not in _DEMON_DEATH_CLOCK:
        _DEMON_DEATH_CLOCK[room_id] = 0.0
        # freeze fly directions the instant it dies (deterministic per room)
        sph = _DEMON_SPHERES.get(room_id)
        if sph is not None:
            demonmod.seed_explosion(sph, seed=4242 + (abs(hash(room_id)) & 0xFFFF))


def demon_tick(room_id: str, dt: float, dead: bool) -> None:
    if dead:
        if room_id in _DEMON_DEATH_CLOCK:
            _DEMON_DEATH_CLOCK[room_id] += dt
    else:
        _DEMON_ALIVE_CLOCK[room_id] = _DEMON_ALIVE_CLOCK.get(room_id, 0.0) + dt

def _get_ctx():
    import moderngl
    return moderngl.get_context()          # FIX: reuse the real context

def _program(ctx):
    key=id(ctx)
    p=_prog_cache.get(key)
    if p is None:
        from shaders import solid_program
        p=solid_program(ctx)
        _prog_cache[key]=p
    return p

def _norm(v):
    v=np.asarray(v,np.float32); n=np.linalg.norm(v)
    return (v/n).astype(np.float32) if n>1e-9 else v

def _tri_normals(tris):
    """tris: (N,3,3) -> per-vertex flat normals (N*3,3)."""
    if tris.shape[0]==0: return np.zeros((0,3),np.float32)
    p0=tris[:,0,:]; p1=tris[:,1,:]; p2=tris[:,2,:]
    n=np.cross(p1-p0,p2-p0)
    ln=np.linalg.norm(n,axis=1,keepdims=True); ln[ln<1e-9]=1.0
    n=(n/ln).astype(np.float32)
    return np.repeat(n,3,axis=0)

def _set_mvp(prog, view, proj=None):
    # caller passes proj@view already (in `view` param), matching app.py
    try: prog["u_mvp"].write(np.ascontiguousarray(np.asarray(view,np.float32).T,np.float32).tobytes())
    except Exception: pass

def _set(prog,name,value):
    try: prog[name].value=value
    except Exception: pass

def _resolve_asset_path(asset_id, pack):
    manifest=getattr(pack,"manifest",None)
    if manifest is None: return None
    entry=manifest.assets.get(asset_id)          # FIX: real access
    if entry is None: return None
    rel=getattr(entry,"wall_path",None)          # wall mip (not the read-mode master)
    if not rel: return None
    base=getattr(pack,"asset_dir","") or ""      # FIX: wall_path is relative to the pack dir
    return os.path.join(base, rel) if base else rel

def _upload_texture(ctx, asset_id, pack):
    if asset_id in _texture_cache: return _texture_cache[asset_id]
    tex=None
    try:
        from PIL import Image
        path=_resolve_asset_path(asset_id,pack)
        if path is not None:
            img=Image.open(path).convert("RGBA")
            img=img.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.FLIP_LEFT_RIGHT)
            tex=ctx.texture(img.size,4,img.tobytes())
    except Exception:
        tex=None
    _texture_cache[asset_id]=tex
    return tex

_GOLD_TEX_CACHE: dict = {}  # key -> texture | None


def _bake_gold_texture(ctx, text: str, font_size: int):
    """Bake golden text to a GL texture using Pillow. Cached. Returns Texture or None."""
    key = f"gold_{text}_{font_size}"
    if key in _GOLD_TEX_CACHE:
        return _GOLD_TEX_CACHE[key]
    tex = None
    try:
        from PIL import Image, ImageDraw, ImageFont
        font = None
        for fp in ("C:/Windows/Fonts/segoeuib.ttf",
                   "segoeuib.ttf",
                   "C:/Windows/Fonts/segoeui.ttf",
                   "C:/Windows/Fonts/arialbd.ttf",
                   "arialbd.ttf"):
            try:
                font = ImageFont.truetype(fp, font_size)
                break
            except Exception:
                continue
        if font is None:
            font = ImageFont.load_default()
        tmp = Image.new("RGBA", (1, 1))
        tmpd = ImageDraw.Draw(tmp)
        bb = tmpd.textbbox((0, 0), text, font=font)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        pad = 10
        img = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.text((pad - bb[0], pad - bb[1]), text, fill=(255, 215, 0, 255), font=font)
        img = img.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.FLIP_LEFT_RIGHT)
        tex = ctx.texture(img.size, 4, img.tobytes())
    except Exception:
        tex = None
    _GOLD_TEX_CACHE[key] = tex
    return tex


_GOLD_VAOS: dict = {}  # room_id -> {"doors": [(PanelQuad, VAO), ...], "floor": (PanelQuad, VAO) | None}


def _build_door_label_quads(room, pack):
    """Build PanelQuads for golden door titles showing neighbor room names."""
    quads = []
    W, H, D = room.dimensions_m
    uv = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]], dtype=np.float32)
    names = getattr(pack, "room_names", {}) or {}
    up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    for door in room.doors:
        neighbor_name = names.get(door.neighbor_id, door.neighbor_id)
        wall = door.wall
        along, inward = _wall_basis(wall)
        along_coord = _wall_along_coord(wall, door.center_xyz)
        label_y = door.height_m + 0.18
        label_center_xyz = _point_on_wall(wall, along_coord, label_y, W, D)
        label_w = door.width_m
        label_h = 0.25
        c = np.asarray(label_center_xyz, dtype=np.float32) + inward * 0.012
        hw, hh = label_w / 2.0, label_h / 2.0
        bl = c - along * hw - up * hh
        br = c + along * hw - up * hh
        tr = c + along * hw + up * hh
        tl = c - along * hw + up * hh
        corners = np.array([bl, br, tr, tl], dtype=np.float32)
        quads.append(PanelQuad(
            pair_id=f"door_label_{door.edge_id}",
            is_drawing=True,
            off_asset_id=f"GOLD:{neighbor_name}",
            on_asset_id=f"GOLD:{neighbor_name}",
            corners=corners,
            uv=uv.copy(),
        ))
    return quads


def _build_floor_label_quad(room, pack):
    """Build a PanelQuad for the room name on the floor centre. Returns PanelQuad or None."""
    names = getattr(pack, "room_names", {}) or {}
    room_name = names.get(room.room_id, room.room_id)
    if not room_name:
        return None
    W, H, D = room.dimensions_m
    uv = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]], dtype=np.float32)
    label_w = min(W * 0.6, 5.0)
    label_h = 0.55
    label_y = 0.015
    cx, cz = 0.0, 0.0
    hw, hh = label_w / 2.0, label_h / 2.0
    bl = np.array([cx - hw, label_y, cz - hh], dtype=np.float32)
    br = np.array([cx + hw, label_y, cz - hh], dtype=np.float32)
    tr = np.array([cx + hw, label_y, cz + hh], dtype=np.float32)
    tl = np.array([cx - hw, label_y, cz + hh], dtype=np.float32)
    corners = np.array([bl, br, tr, tl], dtype=np.float32)
    return PanelQuad(
        pair_id="floor_label",
        is_drawing=True,
        off_asset_id=f"GOLD:{room_name}",
        on_asset_id=f"GOLD:{room_name}",
        corners=corners,
        uv=uv.copy(),
    )


def _ensure_gold_vaos(ctx, prog, room, pack):
    """Build/cache golden-text VAOs for this room (door labels + floor name)."""
    rid = room.room_id
    if rid in _GOLD_VAOS:
        return _GOLD_VAOS[rid]
    door_quads = _build_door_label_quads(room, pack)
    floor_quad = _build_floor_label_quad(room, pack)
    door_vaos = []
    for dq in door_quads:
        pos, uvs = _quad_arrays(dq)
        door_vaos.append((dq, _tris_vao(ctx, prog, pos, uvs)))
    floor_vao = None
    if floor_quad is not None:
        pos, uvs = _quad_arrays(floor_quad)
        floor_vao = (_tris_vao(ctx, prog, pos, uvs), floor_quad)
    result = {"doors": door_vaos, "floor": floor_vao}
    _GOLD_VAOS[rid] = result
    return result


def _tris_vao(ctx, prog, tris, uvs):
    pos=tris.reshape(-1,3).astype(np.float32)
    uv =uvs.reshape(-1,2).astype(np.float32)
    nor=_tri_normals(tris)
    vp=ctx.buffer(np.ascontiguousarray(pos).tobytes())
    vu=ctx.buffer(np.ascontiguousarray(uv).tobytes())
    vn=ctx.buffer(np.ascontiguousarray(nor).tobytes())
    return ctx.vertex_array(prog,[(vp,'3f','in_pos'),(vu,'2f','in_uv'),(vn,'3f','in_normal')])

def _quad_arrays(quad):
    c=quad.corners; uv=quad.uv
    pos=np.array([c[0],c[1],c[2], c[0],c[2],c[3]],dtype=np.float32).reshape(-1,3,3)
    uvs=np.array([uv[0],uv[1],uv[2], uv[0],uv[2],uv[3]],dtype=np.float32).reshape(-1,3,2)
    return pos,uvs

def _get_room_vaos(ctx, prog, room):
    rid=room.room_id
    cached=_vao_cache.get(rid)
    if cached is not None: return cached
    if rid not in _mesh_cache:
        _mesh_cache[rid]=build_room_mesh(room)   # pure builder (same module)
    mesh=_mesh_cache[rid]
    d={}
    d["mesh"]=mesh
    d["wall"]=_tris_vao(ctx,prog,mesh.wall_tris,mesh.wall_uvs) if mesh.wall_tris.shape[0] else None
    if mesh.door_frame_tris.shape[0]:
        ju=np.zeros((mesh.door_frame_tris.shape[0],3,2),np.float32)
        d["jamb"]=_tris_vao(ctx,prog,mesh.door_frame_tris,ju)
    else: d["jamb"]=None
    if mesh.alcove_tris.shape[0]:
        au=np.zeros((mesh.alcove_tris.shape[0],3,2),np.float32)
        d["alcove"]=_tris_vao(ctx,prog,mesh.alcove_tris,au)
    else: d["alcove"]=None
    # panel + ceiling quad VAOs (textured)
    d["panels"]=[]
    for q in mesh.panel_quads:
        pos,uvs=_quad_arrays(q)
        d["panels"].append((q,_tris_vao(ctx,prog,pos,uvs)))
    d["ceiling"]=[]
    for q in mesh.ceiling_quads:
        pos,uvs=_quad_arrays(q)
        d["ceiling"].append((q,_tris_vao(ctx,prog,pos,uvs)))
    # final-proof-panel glow: a larger quad sitting just BEHIND the final
    # drawing panel (the hidden door). Rendered pulsing-gold once that panel is
    # lit, so the player knows which panel opens the door.
    d["final_pair"]=room.final_pair_id
    d["final_glow"]=None
    _fwall=None
    for pr in room.panel_pairs:
        if pr.pair_id==room.final_pair_id:
            _fwall=pr.drawing_placement.wall; break
    if _fwall is not None:
        _,_inward=_wall_basis(_fwall)
        for q in mesh.panel_quads:
            if q.pair_id==room.final_pair_id and q.is_drawing:
                gc=_expand_quad(q.corners,1.20) - _inward*0.012  # slightly behind panel
                gpos=np.array([gc[0],gc[1],gc[2], gc[0],gc[2],gc[3]],dtype=np.float32).reshape(-1,3,3)
                guv=np.zeros((2,3,2),np.float32)
                d["final_glow"]=_tris_vao(ctx,prog,gpos,guv)
                break
    _vao_cache[rid]=d
    return d

def draw_room(view: ViewMatrix, room: RoomRuntime, pack: Pack, state: GameState) -> None:
    """Mode B solid lit room. `view` carries proj@view (set by app.py)."""
    if not HAVE_GL: return
    try:
        import moderngl
        ctx=_get_ctx()
    except Exception:
        return
    prog=_program(ctx)
    if prog is None: return

    # Has this room's hidden door opened (demon revealed)? Gates the alcove + demon.
    try:
        level_id = pack.floorplan.level_id
        lvl = state.save.levels.get(level_id)
        room_save = lvl.rooms.get(room.room_id) if lvl is not None else None
        door_open = bool(room_save and room_save.hidden_door_open)
    except Exception:
        door_open = False

    # ---- assert OUR full GL state every frame ----
    ctx.enable(moderngl.DEPTH_TEST); ctx.depth_func="<="; ctx.depth_mask=True
    ctx.disable(moderngl.BLEND)
    ctx.disable(moderngl.CULL_FACE)   # FIX: interior room — show all faces (winding is inconsistent; pyglet enables culling by default)

    _set_mvp(prog,view)
    _set(prog,"u_light_dir",tuple(_norm(LIGHT_DIR)))
    _set(prog,"u_ambient",float(AMBIENT))

    vaos=_get_room_vaos(ctx,prog,room)

    # 1) walls / floor / ceiling structure (untextured lit solid: u_use_tint==2)
    _set(prog,"u_use_tint",2)
    _set(prog,"u_tint",WALL_RGB)
    if vaos["wall"] is not None: vaos["wall"].render()
    # 3) door jambs
    if vaos["jamb"] is not None:
        _set(prog,"u_tint",JAMB_RGB); vaos["jamb"].render()

    # final-proof-panel glow: once the final panel is lit (and before the door
    # opens), it pulses gold so the player knows THIS panel opens the door.
    if (not door_open) and vaos.get("final_glow") is not None \
            and panel_is_on(vaos.get("final_pair"), state.lit, room):
        pulse = 0.55 + 0.45 * math.sin(time.perf_counter() * 3.0)
        _set(prog,"u_use_tint",2)
        _set(prog,"u_tint",(1.0*pulse, 0.8*pulse, 0.12*pulse))
        vaos["final_glow"].render()
        _set(prog,"u_use_tint",0)

    # 2+5) panels (textured, blend ON for transparent PNGs)
    ctx.enable(moderngl.BLEND)
    ctx.blend_func=(moderngl.SRC_ALPHA,moderngl.ONE_MINUS_SRC_ALPHA)
    for q,vao in vaos["panels"]:
        on = panel_is_on(q.pair_id, state.lit, room)   # pure helper (same module)
        asset = q.on_asset_id if on else q.off_asset_id
        tex=_upload_texture(ctx,asset,pack)
        if tex is not None:
            tex.use(0); _set(prog,"u_tex",0); _set(prog,"u_use_tint",0)
        else:
            # FIX: missing texture -> lit grey placeholder, never an unbound-sampler white
            _set(prog,"u_use_tint",2); _set(prog,"u_tint",(0.78,0.78,0.82))
        vao.render()
    _set(prog,"u_use_tint",0)
    ctx.disable(moderngl.BLEND)

    # 4) alcove — drawn after panels with depth disabled, so it shows
    #     through the wall when the hidden door has opened
    if door_open and vaos["alcove"] is not None:
        ctx.disable(moderngl.DEPTH_TEST)
        _set(prog,"u_use_tint",2); _set(prog,"u_tint",ALCOVE_RGB)
        vaos["alcove"].render()
        ctx.enable(moderngl.DEPTH_TEST); ctx.depth_func="<="
        _set(prog,"u_use_tint",0)

    # 6) ceiling equations — blood-red tint when cleared, or toggled with C key
    if (room.room_id in state.cleared or _show_ceilings) and vaos["ceiling"]:
        ctx.enable(moderngl.BLEND); ctx.blend_func=(moderngl.SRC_ALPHA,moderngl.ONE_MINUS_SRC_ALPHA)
        _set(prog,"u_use_tint",1); _set(prog,"u_tint",(1.0,0.0,0.0))
        for q,vao in vaos["ceiling"]:
            tex=_upload_texture(ctx,q.off_asset_id,pack)
            if tex is not None: tex.use(0); _set(prog,"u_tex",0)
            vao.render()
        ctx.disable(moderngl.BLEND)
        _set(prog,"u_use_tint",0)

    # 7) golden text — door titles + floor room name (blended, textured)
    gold = _ensure_gold_vaos(ctx, prog, room, pack)
    ctx.enable(moderngl.BLEND); ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)
    _set(prog, "u_use_tint", 0)
    _set_mvp(prog, view)
    for q, vao in gold["doors"]:
        neighbor_name = q.off_asset_id.replace("GOLD:", "")
        tex = _bake_gold_texture(ctx, neighbor_name, 36)
        if tex is not None:
            tex.use(0); _set(prog, "u_tex", 0)
        vao.render()
    if gold["floor"] is not None:
        fvao, fq = gold["floor"]
        room_name = fq.off_asset_id.replace("GOLD:", "")
        tex = _bake_gold_texture(ctx, room_name, 72)
        if tex is not None:
            tex.use(0); _set(prog, "u_tex", 0)
        fvao.render()
    ctx.disable(moderngl.BLEND)

    # 8) DEMON — revealed with the alcove; bobs while alive; explodes on kill.
    #    Drawn last: it overwrites u_mvp per-sphere (view @ model), so nothing
    #    after it depends on the shared view mvp. Opaque -> blend off, depth on.
    if door_open and getattr(room, "enemy", None) is not None:
        if room.room_id not in _DEMON_POS:      # resumed game (spawn event missed)
            demon_on_spawned(room.room_id, room.enemy.spawn_xyz)
        t_death = _DEMON_DEATH_CLOCK.get(room.room_id)   # None while alive
        cleared_and_gone = room.room_id in state.cleared and (t_death is None or demonmod.is_gone(t_death))
        if not (t_death is not None and demonmod.is_gone(t_death)) and not cleared_and_gone:
            spheres = _room_demon_spheres(room)
            renderer = _get_demon_renderer(ctx, prog)
            alive_t = _DEMON_ALIVE_CLOCK.get(room.room_id, 0.0)
            sp = room.enemy.spawn_xyz
            pos_xz = _DEMON_POS.get(room.room_id, (sp[0], sp[2]))
            yaw = _DEMON_YAW.get(room.room_id, 0.0)
            root = (pos_xz[0], _DEMON_SPAWN_Y.get(room.room_id, sp[1]), pos_xz[1])
            ctx.disable(moderngl.BLEND)
            renderer.draw(view=view, root_xyz=root, spheres=spheres, yaw=yaw,
                          t_since_death=t_death, bob_t=alive_t)
        _set(prog,"u_use_tint",0)
