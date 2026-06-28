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
    if wall == "S":   # z = -D/2, inward +Z, along +X
        return np.array([1.0, 0.0, 0.0], np.float32), np.array([0.0, 0.0, 1.0], np.float32)
    if wall == "E":   # x = +W/2, inward -X, along +Z
        return np.array([0.0, 0.0, 1.0], np.float32), np.array([-1.0, 0.0, 0.0], np.float32)
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


def _build_panel_quads(room: RoomRuntime):
    quads: list[PanelQuad] = []
    uv = np.array(
        [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]], dtype=np.float32
    )
    for pair in room.panel_pairs:
        dp = pair.drawing_placement
        tp = pair.text_placement
        d_corners = _placement_corners(
            dp.center_xyz, dp.width_m, dp.height_m, dp.yaw_rad, PANEL_INSET_M
        )
        quads.append(PanelQuad(
            pair_id=pair.pair_id,
            is_drawing=True,
            off_asset_id=pair.drawing_off_asset,
            on_asset_id=pair.drawing_on_asset,
            corners=d_corners,
            uv=uv.copy(),
        ))
        t_corners = _placement_corners(
            tp.center_xyz, tp.width_m, tp.height_m, tp.yaw_rad, PANEL_INSET_M
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
    uv = np.array(
        [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]], dtype=np.float32
    )
    for eq in room.ceiling_equations:
        cx, cy, cz = eq.pos_xyz
        w, d = eq.size_m  # width (X), depth (Z)
        hw = w / 2.0
        hd = d / 2.0
        # Facing downward (-Y). Corners in XZ plane at y = cy.
        bl = (cx - hw, cy, cz - hd)
        br = (cx + hw, cy, cz - hd)
        tr = (cx + hw, cy, cz + hd)
        tl = (cx - hw, cy, cz + hd)
        corners = np.array([bl, br, tr, tl], dtype=np.float32)
        quads.append(PanelQuad(
            pair_id=eq.asset_id,  # not a true pair_id; ceilings don't toggle
            is_drawing=True,
            off_asset_id=eq.asset_id,
            on_asset_id=eq.asset_id,
            corners=corners,
            uv=uv.copy(),
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

    # Back corners (pushed inward)
    push = inward * depth
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
    """A pair is "on" iff any of its asset IDs are in the `lit` set."""
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
AMBIENT    = 0.38

_prog_cache: dict = {}            # ctx-id -> solid program
_mesh_cache: dict = {}            # room_id -> RoomMesh
_vao_cache:  dict = {}            # room_id -> dict of VAOs
_texture_cache: dict = {}         # asset_id -> texture|None

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
    return getattr(entry,"wall_path",None)       # wall mip (not the read-mode master)

def _upload_texture(ctx, asset_id, pack):
    if asset_id in _texture_cache: return _texture_cache[asset_id]
    tex=None
    try:
        from PIL import Image
        path=_resolve_asset_path(asset_id,pack)
        if path is not None:
            img=Image.open(path).convert("RGBA")
            tex=ctx.texture(img.size,4,img.tobytes())
            try: tex.build_mipmaps()
            except Exception: pass
    except Exception:
        tex=None
    _texture_cache[asset_id]=tex
    return tex

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
    # ---- assert OUR full GL state every frame ----
    ctx.enable(moderngl.DEPTH_TEST); ctx.depth_func="<="; ctx.depth_mask=True
    ctx.disable(moderngl.BLEND)

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
    # 4) alcove
    if vaos["alcove"] is not None:
        _set(prog,"u_tint",ALCOVE_RGB); vaos["alcove"].render()

    # 2+5) panels (textured, blend ON for transparent PNGs)
    ctx.enable(moderngl.BLEND)
    ctx.blend_func=(moderngl.SRC_ALPHA,moderngl.ONE_MINUS_SRC_ALPHA)
    _set(prog,"u_use_tint",0)
    for q,vao in vaos["panels"]:
        on = panel_is_on(q.pair_id, state.lit, room)   # pure helper (same module)
        asset = q.on_asset_id if on else q.off_asset_id
        tex=_upload_texture(ctx,asset,pack)
        if tex is not None: tex.use(0); _set(prog,"u_tex",0)
        vao.render()
    ctx.disable(moderngl.BLEND)

    # 6) ceiling equations — blood-red tint only when cleared
    if room.room_id in state.cleared and vaos["ceiling"]:
        ctx.enable(moderngl.BLEND); ctx.blend_func=(moderngl.SRC_ALPHA,moderngl.ONE_MINUS_SRC_ALPHA)
        _set(prog,"u_use_tint",1); _set(prog,"u_tint",(1.0,0.0,0.0))
        for q,vao in vaos["ceiling"]:
            tex=_upload_texture(ctx,q.off_asset_id,pack)
            if tex is not None: tex.use(0); _set(prog,"u_tex",0)
            vao.render()
        ctx.disable(moderngl.BLEND)
        _set(prog,"u_use_tint",0)
