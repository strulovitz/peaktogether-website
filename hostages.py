"""hostages.py -- DESCENT QED, MODULE: hostages.

THE PRIZE. Two glowing 3D HUMANOID figures -- a couple -- standing together
at the far end of every corridor's blue cavern, facing back up the corridor
toward the arriving ship, waiting to be rescued. NOT a sprite, NOT a
billboard, NOT a flat quad, NOT a blob. A REAL 3D body (head, torso, two
arms, two legs) assembled from GL primitives in code -- built and animated
the SAME WAY robots.py builds the Robot's hull: code-built triangle lists,
fake flat lighting, stored pre-shaded geometry, a glPushMatrix transform to
world position + facing, gentle idle animation, and a draw(cr,cu,texcache)
method split opaque/emissive exactly like Robot.

THE ENGINE IS MATHEMATICS-BLIND. Hostages carry NO mathematics and NO
meaning -- pure prize geometry. The warm figure color is DECORATION (chosen
here, like Robot's HULL_GREY), never a meaning-color. We never call
palette.eye()/tint()/blend_rgb() (those map ledger keys -> MEANING). We use
an OPAQUE decoration color only.

There is NO losing in this game: no damage, no death, no timer, no fail
state. The couple simply waits.

DRAW PHASE: hostages are SOLID 3D geometry, drawn in the draw_robots slot,
AFTER render.flush_walls -- exactly where Robot.draw() is called from
CorridorGeometry.draw_robots(). draw() is a back-to-back wrapper of the
opaque body and the additive glow, mirroring Robot.draw().

Confirmed dependencies (frozen, quoted from the pasted files):
    render.draw_billboard / ship_right / ship_up      (camera basis cr,cu)
    CorridorGeometry.hostage_positions() -> list[(x,y,z)]   (3 floor anchors)
    CorridorGeometry.entrance_pose() -> ((x,y,z),(nx,ny,nz))  (mouth + normal)
    palette opaque constants (HOSTAGE_BLUE etc.); optional palette.HOSTAGE_GLOW
"""

import math
import numpy as np
from OpenGL.GL import *

import palette


# ----------------------------------------------------------------------
# LIGHT + MATERIAL  (mirrors robots.py: fake flat lighting, world is
# fixed-function flat). Copied so the figures shade the SAME way the hull
# does -- a recognizable solid object, not a flat sprite.
# ----------------------------------------------------------------------
_LIGHT_DIR = np.array([0.35, 0.80, 0.45], dtype=float)
_LIGHT_DIR /= np.linalg.norm(_LIGHT_DIR)

_AMBIENT   = 0.42     # base brightness in shadow (a touch brighter than the
                      # robot's 0.32 so the friendly figures read warm, not grim)
_DIFFUSE   = 0.55
_SPEC_GAIN = 0.30     # softer than the robot's metallic 0.85 (people, not metal)
_SPEC_POW  = 12.0

# ---- WARM DECORATION COLORS (never meaning) --------------------------
# The couple GLOWS warm so they POP against palette.HOSTAGE_BLUE cavern
# walls. These are DECORATION, chosen here exactly like robots.py chooses
# HULL_GREY / VISOR_BLACK. If the parent adds an official opaque
# palette.HOSTAGE_GLOW key, build_hostages() will prefer it (see below).
_GLOW_WARM = np.array([1.0, 0.78, 0.45], dtype=float)   # warm amber default

# Two distinct people: per-variant skin + clothing tints (decoration only).
# variant 0 = slightly taller, cooler clothing; variant 1 = slightly
# shorter, warmer clothing. Tasteful + simple, per the brief.
_VARIANTS = [
    dict(skin=np.array([1.00, 0.80, 0.62]),   # warm light skin
         cloth=np.array([0.95, 0.62, 0.30]),  # warm amber suit
         height=1.00),
    dict(skin=np.array([0.86, 0.62, 0.46]),   # warm medium skin
         cloth=np.array([0.95, 0.45, 0.40]),  # warm coral suit
         height=0.92),
]


# ----------------------------------------------------------------------
# TUNING CONSTANTS  (DeepSeek may adjust ONLY after Nir's flight)
# ----------------------------------------------------------------------
# TODO(DeepSeek): TUNE after Nir flies the demo. | ACCEPTANCE: the couple
#   reads as two distinct PEOPLE standing TOGETHER (not clones, not merged,
#   not too far apart); the idle bob/sway reads ALIVE (gentle, not seasick);
#   they GLOW warm and POP against the blue cavern.
HOSTAGE_SIZE     = 1.6     # overall figure scale (a person ~2.6 units tall)
COUPLE_SPACING   = 2.2     # world units between the two people (center-to-center)
BOB_AMPLITUDE    = 0.10    # gentle vertical breathing bob (people, not hover)
BOB_SPEED        = 1.1     # rad/sec of the bob
SWAY_AMPLITUDE   = 0.045   # rad of subtle side-to-side weight-shift sway
SWAY_SPEED       = 0.7     # rad/sec of the sway
NEAR_RADIUS      = 14.0    # default "the ship is near the couple" radius

GLOW_AURA_DIAM   = 5.5     # diameter (x size) of the warm ground-glow aura disk
GLOW_AURA_ALPHA  = 0.30    # additive strength of that aura
GLOW_AURA_SEG    = 22      # triangles in the aura fan (smooth disk)
GLOW_EDGE_ALPHA  = 0.55    # additive warm body-edge halo strength (the POP)


# ----------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------
def _unit(v):
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def _shade(tri, base_rgb):
    """Fake flat lighting -- COPIED from robots.py so a hostage body part
    shades identically to the robot hull (solid 3D read, not a sprite)."""
    a, b, c = (np.array(v, float) for v in tri)
    n = np.cross(b - a, c - a)
    ln = np.linalg.norm(n)
    if ln < 1e-9:
        return tuple(base_rgb * _AMBIENT)
    n = n / ln
    ndl = abs(float(n.dot(_LIGHT_DIR)))
    bright = _AMBIENT + _DIFFUSE * ndl
    spec = _SPEC_GAIN * (ndl ** _SPEC_POW)
    rgb = base_rgb * bright + spec
    return tuple(min(1.0, ch) for ch in rgb)


# ----------------------------------------------------------------------
# BODY PRIMITIVES  (low-poly, output as triangles (a,b,c) -- same format
# robots.py's _box/_prism/_wedge_snout emit). Local model space: +Y up,
# the figure faces +Z (we rotate by yaw about +Y in draw, exactly like
# the robot hull). Origin at the feet (y=0 = floor).
# ----------------------------------------------------------------------
def _box(cx, cy, cz, hx, hy, hz):
    """Axis-aligned box centered (cx,cy,cz), half-extents (hx,hy,hz).
    COPIED from robots.py _box -> 12 triangles."""
    x0, x1 = cx - hx, cx + hx
    y0, y1 = cy - hy, cy + hy
    z0, z1 = cz - hz, cz + hz
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 1, 2, 3), (5, 4, 7, 6), (4, 0, 3, 7),
         (1, 5, 6, 2), (3, 2, 6, 7), (4, 5, 1, 0)]
    tris = []
    for a, b, c, d in f:
        tris += [(v[a], v[b], v[c]), (v[a], v[c], v[d])]
    return tris


def _taper_box(cx, cy, cz, hx_bot, hz_bot, hx_top, hz_top, y0, y1):
    """A vertical box that tapers from (hx_bot,hz_bot) at y0 to
    (hx_top,hz_top) at y1 -> gives torso/limbs a body-like taper rather
    than a brick. 12 triangles, same (a,b,c) format."""
    b00 = (cx - hx_bot, y0, cz - hz_bot); b10 = (cx + hx_bot, y0, cz - hz_bot)
    b11 = (cx + hx_bot, y0, cz + hz_bot); b01 = (cx - hx_bot, y0, cz + hz_bot)
    t00 = (cx - hx_top, y1, cz - hz_top); t10 = (cx + hx_top, y1, cz - hz_top)
    t11 = (cx + hx_top, y1, cz + hz_top); t01 = (cx - hx_top, y1, cz + hz_top)
    tris = []
    tris += [(b00, b10, t10), (b00, t10, t00)]   # -Z face
    tris += [(b10, b11, t11), (b10, t11, t10)]   # +X face
    tris += [(b11, b01, t01), (b11, t01, t11)]   # +Z face
    tris += [(b01, b00, t00), (b01, t00, t01)]   # -X face
    tris += [(t00, t10, t11), (t00, t11, t01)]   # top cap
    tris += [(b00, b01, b11), (b00, b11, b10)]   # bottom cap
    return tris


def _octa_sphere(cx, cy, cz, r):
    """A faceted low-poly sphere (subdivided octahedron) for the head.
    Faceted on purpose -> matches the robot's low-poly faceted look and
    catches the fake light per-facet. Returns triangle list (a,b,c)."""
    # 6 octahedron vertices
    top = (cx, cy + r, cz); bot = (cx, cy - r, cz)
    xp = (cx + r, cy, cz); xn = (cx - r, cy, cz)
    zp = (cx, cy, cz + r); zn = (cx, cy, cz - r)
    base = [
        (top, zp, xp), (top, xp, zn), (top, zn, xn), (top, xn, zp),
        (bot, xp, zp), (bot, zn, xp), (bot, xn, zn), (bot, zp, xn),
    ]

    def _mid(p, q):
        m = ((p[0] + q[0]) * 0.5, (p[1] + q[1]) * 0.5, (p[2] + q[2]) * 0.5)
        d = (m[0] - cx, m[1] - cy, m[2] - cz)
        n = math.sqrt(d[0] * d[0] + d[1] * d[1] + d[2] * d[2]) or 1.0
        s = r / n
        return (cx + d[0] * s, cy + d[1] * s, cz + d[2] * s)

    tris = []
    for a, b, c in base:                      # one subdivision -> 32 facets
        ab, bc, ca = _mid(a, b), _mid(b, c), _mid(c, a)
        tris += [(a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca)]
    return tris


def _build_body(variant):
    """Assemble ONE recognizable standing PERSON from the primitives above,
    pre-shaded per-triangle (skin tone for head/hands, cloth tone for the
    rest). Returns (verts_flat Nx3, colors list). Mirrors robots.py's
    _build_hull()+_shade() pattern: geometry built once, colors baked.

    Proportions (local space, feet at y=0), scaled by variant height:
        legs  0.00 -> 1.10
        torso 1.05 -> 1.95   (tapers in at the waist, out at shoulders)
        arms  1.05 -> 1.90   (alongside the torso)
        neck  1.90 -> 2.02
        head  ~2.25 (sphere r 0.27)
    """
    v = _VARIANTS[variant % len(_VARIANTS)]
    skin = v["skin"]
    cloth = v["cloth"]
    H = v["height"]

    skin_tris, cloth_tris = [], []

    # --- legs (two tapered boxes), feet at floor ---
    leg_y0, leg_y1 = 0.00 * H, 1.10 * H
    for sx in (-1, 1):
        cloth_tris += _taper_box(0.16 * sx, 0, 0,
                                 hx_bot=0.13, hz_bot=0.15,
                                 hx_top=0.16, hz_top=0.17,
                                 y0=leg_y0, y1=leg_y1)
        # foot
        cloth_tris += _box(0.16 * sx, 0.04 * H, 0.06,
                           0.15, 0.05 * H, 0.24)

    # --- torso (taper: narrow waist -> broad shoulders) ---
    torso_y0, torso_y1 = 1.05 * H, 1.95 * H
    cloth_tris += _taper_box(0, 0, 0,
                             hx_bot=0.28, hz_bot=0.17,
                             hx_top=0.42, hz_top=0.20,
                             y0=torso_y0, y1=torso_y1)

    # --- arms (two tapered boxes alongside the torso) ---
    arm_y0, arm_y1 = 1.05 * H, 1.90 * H
    for sx in (-1, 1):
        ax = 0.52 * sx
        cloth_tris += _taper_box(ax, 0, 0.0,
                                 hx_bot=0.11, hz_bot=0.13,
                                 hx_top=0.13, hz_top=0.15,
                                 y0=arm_y0, y1=arm_y1)
        # hand (skin) at the wrist
        skin_tris += _box(ax, arm_y0 - 0.02, 0.0, 0.12, 0.10, 0.13)

    # --- neck (skin) ---
    skin_tris += _box(0, 1.98 * H, 0.0, 0.10, 0.08 * H, 0.10)

    # --- head (skin sphere) ---
    head_cy = 2.28 * H
    head_r = 0.27
    skin_tris += _octa_sphere(0, head_cy, 0.02, head_r)

    # --- bake geometry + shaded colors (robots.py pattern) ---
    verts = []
    colors = []
    for t in skin_tris:
        verts += list(t)
        colors.append(_shade(t, skin))
    for t in cloth_tris:
        verts += list(t)
        colors.append(_shade(t, cloth))

    verts_flat = np.array(verts, dtype=float)
    total_height = 2.55 * H
    return verts_flat, colors, total_height


# ======================================================================
class Hostage:
    """A single rescued PERSON -- a real 3D humanoid figure.

    PUBLIC INTERFACE (final, mirrors Robot's shape):
        Hostage(world_pos, facing, color_id, variant=0, size=HOSTAGE_SIZE)
        update(dt)                          # gentle idle life; NO tracking
        draw(camera_right, camera_up, texcache)            # wrapper
        draw_opaque(camera_right, camera_up, texcache)     # body, depth on
        draw_emissive(camera_right, camera_up, texcache)   # warm glow, additive
        position   (property) -> bobbed world-center (feet anchor + bob)
        base_pos              -> un-bobbed floor anchor (public)

    world_pos : (x,y,z) FLOOR anchor (feet) in world space.
    facing    : (dx,dy,dz) direction the person looks (toward the ship).
    color_id  : opaque warm GLOW rgb (decoration, never meaning).
    variant   : 0 or 1 -> the two distinct people of the couple.
    """

    def __init__(self, world_pos, facing, color_id, variant=0,
                 size=HOSTAGE_SIZE):
        # --- placement (mirrors Robot.base_pos + a yaw) ---
        self.base_pos = np.asarray(world_pos, dtype=float)
        self.size = float(size)
        self.variant = int(variant)

        # yaw from facing, SAME convention as the robots / hub.spawn_pose:
        #   yaw = atan2(dx, -dz)
        f = _unit(facing)
        if abs(f[0]) < 1e-9 and abs(f[2]) < 1e-9:
            f = np.array([0.0, 0.0, 1.0])
        self._yaw = math.atan2(f[0], -f[2])

        # --- warm glow color (DECORATION, never meaning) ---
        self._glow = (np.asarray(color_id, dtype=float)
                      if color_id is not None else _GLOW_WARM.copy())

        # --- geometry built once, colors baked (Robot pattern) ---
        self._verts, self._colors, self._fig_h = _build_body(self.variant)

        # --- animation state (mirrors Robot._t / _bob_y) ---
        self._t = 0.0
        self._bob_y = 0.0
        self._sway = 0.0
        # phase offset so the two people don't breathe in lock-step (alive)
        self._phase = self.variant * 1.3

    # ------------------------------------------------------------------
    def update(self, dt):
        """Gentle idle life: a slow breathing bob + a subtle weight-shift
        sway. MIRRORS Robot.update's _t advance + sinusoidal bob. NO player
        tracking, NO combat, NO timer -- they just wait to be rescued."""
        self._t += dt
        ph = self._t + self._phase
        self._bob_y = BOB_AMPLITUDE * math.sin(ph * BOB_SPEED)
        self._sway = SWAY_AMPLITUDE * math.sin(ph * SWAY_SPEED)

    # ------------------------------------------------------------------
    def _world_center(self):
        return self.base_pos + np.array([0.0, self._bob_y, 0.0])

    @property
    def position(self):
        """Public, read-only: the figure's CURRENT bobbed floor-anchor this
        frame (same point draw/update use). base_pos is the un-bobbed
        anchor. Mirrors Robot.position."""
        return self._world_center()

    # ------------------------------------------------------------------
    # DRAW -- split opaque / emissive exactly like Robot. The corridor's
    # draw_robots slot calls draw() AFTER render.flush_walls (same place
    # Robot.draw() is called). The opaque body writes depth normally; the
    # warm glow is additive with depth-write off. We NEVER call flush.
    # ------------------------------------------------------------------
    def draw(self, camera_right, camera_up, texcache):
        """Convenience wrapper: opaque body then additive glow, back to
        back -- mirrors Robot.draw()."""
        self.draw_opaque(camera_right, camera_up, texcache)
        self.draw_emissive(camera_right, camera_up, texcache)

    def draw_opaque(self, camera_right, camera_up, texcache):
        """OPAQUE phase: the solid 3D body (head/torso/arms/legs), fake-lit,
        normal depth test + depth-write on. Same transform recipe as
        Robot.draw_opaque: translate -> rotate(yaw) -> scale -> emit tris."""
        cx, cy, cz = self._world_center()

        glPushMatrix()
        glTranslatef(cx, cy, cz)
        glRotatef(math.degrees(self._yaw), 0.0, 1.0, 0.0)
        glRotatef(math.degrees(self._sway), 0.0, 0.0, 1.0)   # subtle weight shift
        glScalef(self.size, self.size, self.size)

        glDisable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)

        self._draw_body()

        glPopMatrix()

    def draw_emissive(self, camera_right, camera_up, texcache):
        """EMISSIVE phase: a warm additive halo so the couple GLOWS and POPS
        against the blue cavern -- (1) a soft camera-facing ground-glow aura
        disk under the figure (uses cr,cu like Robot._disk), and (2) a warm
        additive re-draw of the body that brightens its silhouette. Additive
        blend, depth-write off; state restored exactly like Robot."""
        cx, cy, cz = self._world_center()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)   # additive -> glow, dark vanishes
        glDepthMask(GL_FALSE)

        # (1) warm ground-glow aura disk at the feet, camera-facing.
        aura_center = (cx, cy + 0.05 * self.size, cz)
        self._glow_disk(aura_center, GLOW_AURA_DIAM * self.size,
                        camera_right, camera_up, self._glow, GLOW_AURA_ALPHA)

        # (2) warm additive body halo -> emissive silhouette that POPS.
        glPushMatrix()
        glTranslatef(cx, cy, cz)
        glRotatef(math.degrees(self._yaw), 0.0, 1.0, 0.0)
        glRotatef(math.degrees(self._sway), 0.0, 0.0, 1.0)
        glScalef(self.size, self.size, self.size)
        gr, gg, gb = (float(self._glow[0]), float(self._glow[1]),
                      float(self._glow[2]))
        v = self._verts
        glBegin(GL_TRIANGLES)
        glColor4f(gr, gg, gb, GLOW_EDGE_ALPHA)
        for vert in v:
            glVertex3f(*vert)
        glEnd()
        glPopMatrix()

        # restore state exactly like Robot does after its emissive pass
        glDepthMask(GL_TRUE)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_BLEND)

    # ------------------------------------------------------------------
    def _draw_body(self):
        """Immediate-mode body emit -- mirrors Robot._draw_hull exactly:
        one glColor3f per pre-shaded triangle, three vertices each."""
        v = self._verts
        glBegin(GL_TRIANGLES)
        for i, col in enumerate(self._colors):
            glColor3f(*col)
            for vert in v[3 * i:3 * i + 3]:
                glVertex3f(*vert)
        glEnd()

    def _glow_disk(self, center, diameter, cright, cup, rgb, alpha):
        """A soft warm CIRCLE (triangle fan) facing the camera: bright core
        fading to transparent at the rim. COPIED structure from
        robots.py Robot._disk (the explosion fireball disk)."""
        c = np.asarray(center, float)
        rad = diameter * 0.5
        r = np.asarray(cright, float)
        u = np.asarray(cup, float)
        n = GLOW_AURA_SEG
        glBegin(GL_TRIANGLE_FAN)
        glColor4f(rgb[0], rgb[1], rgb[2], min(1.0, alpha))   # warm core
        glVertex3f(*c)
        for i in range(n + 1):
            a = 2.0 * math.pi * i / n
            edge = c + (r * math.cos(a) + u * math.sin(a)) * rad
            glColor4f(rgb[0], rgb[1], rgb[2], 0.0)           # transparent rim
            glVertex3f(*edge)
        glEnd()


# ======================================================================
# MODULE-LEVEL HELPERS  (consumed by the corridor / hub / game-state)
# ======================================================================
def _resolve_glow():
    """Prefer an OFFICIAL opaque palette.HOSTAGE_GLOW key if the parent
    adds one (single-source of colors); else use the local warm decoration
    default. Never a meaning-color -- pure decoration."""
    glow = getattr(palette, "HOSTAGE_GLOW", None)
    if glow is not None:
        return np.asarray(glow, dtype=float)
    return _GLOW_WARM.copy()


def build_hostages(corridor_geom, color_id=None,
                   size=HOSTAGE_SIZE, spacing=COUPLE_SPACING):
    """Return EXACTLY TWO Hostage objects for `corridor_geom`, positioned as
    a couple standing TOGETHER on the cavern floor at the corridor's far end,
    facing back up the corridor toward the arriving ship.

    Uses ONLY the corridor's PUBLIC interface (no private access):
        corridor_geom.hostage_positions() -> [a_left, a_center, a_right]
            three floor anchors at offsets (-3.5, 0.0, +3.5) along the
            cavern's local 'right' axis (quoted from corridor_builder
            _build_cavern_anchors). We IGNORE the count of three and derive
            our OWN tight couple:
              midpoint = center anchor (index 1)
              right    = unit(a_right - a_left)   (the cavern lateral axis)
              two people at midpoint +/- right * (spacing/2)
        corridor_geom.entrance_pose() -> ((mouth_xyz),(normal)) -> the couple
            faces from their midpoint toward the mouth (up the corridor).

    EXACTLY TWO. A couple. Not three. Not one. TWO.
    """
    anchors = corridor_geom.hostage_positions()
    if not anchors:
        return []

    pts = [np.asarray(p, dtype=float) for p in anchors]
    if len(pts) >= 3:
        midpoint = pts[1]
        right = _unit(pts[2] - pts[0])
    elif len(pts) == 2:
        midpoint = (pts[0] + pts[1]) * 0.5
        right = _unit(pts[1] - pts[0])
    else:  # single anchor: synthesize a lateral axis from the mouth dir
        midpoint = pts[0]
        right = np.array([1.0, 0.0, 0.0])

    # facing: from the couple toward the corridor mouth (toward the ship).
    mouth_pos, _normal = corridor_geom.entrance_pose()
    facing = _unit(np.asarray(mouth_pos, dtype=float) - midpoint)
    # keep them upright -- face horizontally up the corridor (no head-tilt).
    facing = _unit(np.array([facing[0], 0.0, facing[2]])) \
        if (abs(facing[0]) > 1e-6 or abs(facing[2]) > 1e-6) \
        else np.array([0.0, 0.0, 1.0])

    glow = _resolve_glow() if color_id is None else np.asarray(color_id, float)

    half = 0.5 * float(spacing)
    left_pos = midpoint - right * half
    right_pos = midpoint + right * half

    return [
        Hostage(tuple(left_pos),  facing, glow, variant=0, size=size),
        Hostage(tuple(right_pos), facing, glow, variant=1, size=size),
    ]


def near_hostages(hostage_list, ship_pos, radius=NEAR_RADIUS):
    """True if `ship_pos` is within `radius` of the couple. PURE GEOMETRY,
    no side effects -- the ONLY query Brief #13 (GAME STATE) consumes.

    Distance is measured to the couple's CENTROID (the midpoint of the two
    figures' current positions), so it reads as 'near the couple' rather
    than near either individual."""
    if not hostage_list:
        return False
    centroid = np.mean([h.position for h in hostage_list], axis=0)
    d = np.asarray(ship_pos, dtype=float) - centroid
    return float(np.dot(d, d)) <= float(radius) * float(radius)
