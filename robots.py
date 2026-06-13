"""robots.py -- DESCENT QED, MODULE: robots.

A Robot is a HOVERING MACHINE. NOT humanoid. No head/face/arms/legs.
One faceted grey-metal hull + a recessed black "visor" slot on the front
face, across which a single bright LARSON SCANNER dot sweeps left<->right
with a comet-tail afterglow (Cylon / KITT). Hover-bob + slow yaw that
TURNS TOWARD the player and tracks them (with a faint idle drift so the
machine always reads as a solid 3D object, never a flat sprite). An
always-on hologram PORTRAIT floats above it (real PNG, glowing-blue figure
on black, drawn additively so the black vanishes). A defeat EXPLOSION
plays once -- a multi-burst of expanding fire CIRCLES all over the hull,
plus a flash and flung debris sparks -- then the body is gone.

THE ENGINE IS MATHEMATICS-BLIND. This module reads ONLY:
    robot_data.name           -> hologram portrait file + placeholder text
    robot_data.eye_color_key  -> palette.eye(key) -> SCANNER color (MEANING)
It never interprets equations and never picks colors by meaning.

ALL meaning-color comes from `palette.eye(key)`. Hull paint, visor slot,
and explosion fire are DECORATION (chosen here), never meaning. The camera
is RECEIVED as parameters (camera_right / camera_up); a robot never owns or
queries the camera.

Confirmed dependencies (frozen):
    palette.Palette.eye(key) -> (r,g,b) floats 0..1, emissive, no alpha.
    render.draw_billboard(tex, center, cam_right, cam_up, scale=1, alpha=1)
        where tex is the (tid,w,h) tuple; caller manages blend/depth;
        billboard modulates white*alpha and uses tex's own w,h for shape.
    render.TexCache().get_mathtext(latex, color=(r,g,b), fontsize=n)
        -> (tid, w, h).
"""

import os
import math
import numpy as np
import pygame
from OpenGL.GL import *

import palette  # constants only; eye() comes via the Palette instance.


# ----------------------------------------------------------------------
# LIGHT + MATERIAL (fake lighting -- the world is fixed-function flat)
# ----------------------------------------------------------------------
_LIGHT_DIR = np.array([0.35, 0.80, 0.45], dtype=float)
_LIGHT_DIR /= np.linalg.norm(_LIGHT_DIR)

# Hull base grey: cool, slightly blue -- close to mine-rock grey but reads
# as MACHINE, not wall. Decoration only (no meaning).
HULL_GREY   = np.array([0.46, 0.48, 0.53], dtype=float)
# The dark visor housing the scanner sweeps across. Near-black so the
# colored scanner glow pops (Cylon visor / KITT black nose). Decoration.
VISOR_BLACK = np.array([0.05, 0.055, 0.07], dtype=float)

# Fake-shading terms.
_AMBIENT   = 0.32     # base brightness in shadow
_DIFFUSE   = 0.50     # how much |n.L| brightens a facet
_SPEC_GAIN = 0.85     # strength of the metallic glint
_SPEC_POW  = 22.0     # tightness of the glint (higher = sharper, shinier)


# ----------------------------------------------------------------------
# TUNING CONSTANTS  (DeepSeek may adjust ONLY after Nir's flight)
# ----------------------------------------------------------------------
# TODO(DeepSeek): TUNE after Nir flies the demo. | ACCEPTANCE: hover reads
#   as a slow alive bob (not seasick); the robot starts at a random angle
#   then turns toward the player and tracks smoothly (not snapping, never
#   perfectly glued -> always reads 3D); the scanner sweep is hypnotic;
#   the explosion reads as a real machine detonating (not a campfire).
BOB_AMPLITUDE   = 0.35    # world units of vertical bob
BOB_SPEED       = 1.3     # rad/sec of the bob sinusoid
YAW_SPEED       = 1.4     # rad/sec max turn rate toward the player
IDLE_DRIFT_AMP  = 0.18    # rad of slow rotational idle drift (keeps it 3D)
IDLE_DRIFT_SPD  = 0.4     # rad/sec of that idle drift

# Larson scanner (Cylon / KITT) sweep.
SCAN_SPEED      = 1.6     # rad/sec; dot position = sin(t*SCAN_SPEED)
SCAN_SEGMENTS   = 15      # lit segments across the visor slot
SCAN_TAIL       = 3.2     # comet-tail falloff (higher = shorter tail)
SCAN_CORE_BOOST = 1.0     # extra brightness at the moving dot

# Hologram portrait.
HOLO_HEIGHT_ABOVE   = 2.6   # how far above hull center the hologram sits
HOLO_BOB_AMP        = 0.12  # hologram's own subtle bob
HOLO_BOB_SPD        = 1.0
HOLO_ALPHA          = 0.55  # text-placeholder translucency (fallback only)
HOLO_PORTRAIT_ALPHA = 0.85  # additive glow strength for the real portrait
HOLO_SCALE          = 1.4   # billboard scale
HOLO_TINT           = (0.62, 0.84, 1.0)  # cool tint for the text fallback

# ---- DEFEAT EXPLOSION (a real machine detonating) --------------------
# A multi-burst of expanding fire CIRCLES at random spots all over the
# hull (random size + staggered timing -> chain detonation), a bright
# center flash, and flung debris sparks. All additive.
EXPLO_DURATION   = 1.6    # total event length (was a wimpy 0.85)
EXPLO_NUM_FIRE   = 9      # how many fire circles bloom over the hull
EXPLO_SPREAD     = 1.9    # how far from center fire circles spawn (x hull r)
EXPLO_SIZE_MIN   = 1.4    # smallest fire circle peak diameter (x size)
EXPLO_SIZE_MAX   = 4.2    # largest  fire circle peak diameter (x size)
EXPLO_FIRE_LIFE  = 0.7    # seconds each fire circle takes to bloom+fade
EXPLO_STAGGER    = 0.55   # window over which the circles start popping
EXPLO_CIRCLE_SEG = 18     # triangles per fire circle (smooth disk)

EXPLO_FLASH_SIZE = 6.5    # initial white-hot flash diameter (x size)
EXPLO_FLASH_LIFE = 0.22   # the flash is fast

EXPLO_NUM_SPARKS = 22     # flung debris streaks
EXPLO_SPARK_SPD  = 9.0    # initial spark speed (units/sec, x size)
EXPLO_SPARK_LIFE = 1.1    # seconds sparks live
EXPLO_SPARK_DRAG = 2.2    # how fast sparks slow down

EXPLO_HOT  = np.array([1.0, 0.92, 0.55])  # yellow-white hot
EXPLO_MID  = np.array([1.0, 0.55, 0.12])  # orange
EXPLO_EDGE = np.array([0.85, 0.18, 0.03])  # deep red ember


# ----------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------
def _wrap_angle(a):
    while a > math.pi:
        a -= 2.0 * math.pi
    while a < -math.pi:
        a += 2.0 * math.pi
    return a


# ----------------------------------------------------------------------
# HOLOGRAM PORTRAIT LOADER
# ----------------------------------------------------------------------
# DeepSeek's TexCache.get_mathtext() builds *text* textures only. The
# hologram needs to show a real PNG portrait, so we load image files here
# into a GL texture and return the SAME (tid, w, h) tuple draw_billboard
# expects. No new dependencies: pygame + OpenGL are already in use.
#
# Naming convention (matches Nir's files):
#   robot_data.name "Brook Taylor"  ->  "Brook_Taylor-hologram.png"
# Files are looked for in the run folder, then next to this module.
#
# The portraits are a glowing-blue figure on a SOLID BLACK square; draw()
# blends them ADDITIVELY so the black vanishes and only the figure glows.
# They are already blue; we do NOT tint.

_PORTRAIT_CACHE = {}   # filename -> (tid, w, h) or None; load each PNG once


def _portrait_filename(name):
    return name.strip().replace(" ", "_") + "-hologram.png"


def _find_portrait(filename):
    candidates = [
        os.path.join(os.getcwd(), filename),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), filename),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def load_portrait(name):
    """Return (tid, w, h) for the robot's hologram PNG, or None if missing
    (caller then falls back to a text placeholder)."""
    filename = _portrait_filename(name)
    if filename in _PORTRAIT_CACHE:
        return _PORTRAIT_CACHE[filename]

    path = _find_portrait(filename)
    if path is None:
        print("DEBUG: hologram portrait not found: %s "
              "(searched cwd + module dir)" % filename)
        _PORTRAIT_CACHE[filename] = None
        return None

    surf = pygame.image.load(path).convert_alpha()
    w, h = surf.get_width(), surf.get_height()
    data = pygame.image.tostring(surf, "RGBA", True)  # flip=True -> GL order

    tid = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tid)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, data)
    glBindTexture(GL_TEXTURE_2D, 0)

    tex = (tid, w, h)
    _PORTRAIT_CACHE[filename] = tex
    print("DEBUG: loaded hologram portrait %s (%dx%d)" % (filename, w, h))
    return tex


# ----------------------------------------------------------------------
# HULL GEOMETRY  (low-poly faceted, output as triangles (a,b,c))
# ----------------------------------------------------------------------
def _prism(n, rad, half_h, dy=0.0, phase=0.0):
    ring = [(rad * math.cos(2 * math.pi * i / n + phase),
             rad * math.sin(2 * math.pi * i / n + phase)) for i in range(n)]
    y0, y1 = -half_h + dy, half_h + dy
    tris = []
    for i in range(n):
        (xa, za), (xb, zb) = ring[i], ring[(i + 1) % n]
        a0, b0 = (xa, y0, za), (xb, y0, zb)
        a1, b1 = (xa, y1, za), (xb, y1, zb)
        tris += [(a0, b0, b1), (a0, b1, a1)]                   # side
        tris += [((0, y1, dy), a1, b1), ((0, y0, dy), b0, a0)]  # caps
    return tris


def _wedge_snout(base_hw, base_hh, base_z, tip_z, tip_hw, tip_hh):
    bx, by = base_hw, base_hh
    tx, ty = tip_hw, tip_hh
    bz, tz = base_z, tip_z
    b00 = (-bx, -by, bz); b10 = (bx, -by, bz)
    b11 = (bx,  by, bz);  b01 = (-bx, by, bz)
    t00 = (-tx, -ty, tz); t10 = (tx, -ty, tz)
    t11 = (tx,  ty, tz);  t01 = (-tx, ty, tz)
    tris = []
    tris += [(b00, b10, t10), (b00, t10, t00)]   # bottom
    tris += [(b10, b11, t11), (b10, t11, t10)]   # right
    tris += [(b11, b01, t01), (b11, t01, t11)]   # top
    tris += [(b01, b00, t00), (b01, t00, t01)]   # left
    tris += [(t00, t10, t11), (t00, t11, t01)]   # front FACE
    return tris, (t00, t10, t11, t01)


def _box(cx, cy, cz, hx, hy, hz):
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


def _build_hull():
    body = _prism(6, 1.45, 0.85, phase=math.radians(30))
    snout, face = _wedge_snout(base_hw=1.25, base_hh=0.78, base_z=1.25,
                               tip_z=2.15, tip_hw=0.80, tip_hh=0.42)
    pods = (_box(-1.45, -0.15, 0.10, 0.32, 0.32, 0.62)
            + _box(1.45, -0.15, 0.10, 0.32, 0.32, 0.62))
    return body + snout + pods, face


def _shade(tri, base_rgb):
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


# ======================================================================
class Robot:
    """A single hovering DESCENT QED guardian machine.

    PUBLIC INTERFACE (final):
        Robot(robot_data, palette, station_pose, paint=None, size=1.0)
        update(dt, ship_position)
        draw(camera_right, camera_up, texcache)
        play_defeat()
        is_defeated() -> bool
    """

    _hull_tris, _face_quad = _build_hull()
    _HULL_R = 1.6   # approx hull radius for explosion placement scaling

    def __init__(self, robot_data, palette, station_pose,
                 paint=None, size=1.0):
        # --- data path (the ONLY things robots reads from RobotData) ---
        self.name = getattr(robot_data, "name", "[ROBOT]")
        self._eye_key = getattr(robot_data, "eye_color_key", "NEUTRAL")

        self._palette = palette
        self.eye_color = tuple(palette.eye(self._eye_key))  # MEANING

        # --- placement -------------------------------------------------
        if (isinstance(station_pose, (tuple, list)) and len(station_pose) == 2
                and isinstance(station_pose[0], (tuple, list, np.ndarray))):
            self.base_pos = np.asarray(station_pose[0], dtype=float)
            seat_yaw = float(station_pose[1])
        else:
            self.base_pos = np.asarray(station_pose, dtype=float)
            seat_yaw = 0.0

        self.size = float(size)

        # --- paint (DECORATION, never meaning) ------------------------
        self._hull_base = (HULL_GREY if paint is None
                           else np.asarray(paint, dtype=float))
        self._hull_cols = [_shade(t, self._hull_base) for t in self._hull_tris]
        self._hull_verts = np.array(
            [v for t in self._hull_tris for v in t], dtype=float)

        # --- animation state ------------------------------------------
        self._t = 0.0
        self._yaw = seat_yaw + np.random.uniform(-math.pi, math.pi)  # surprised
        self._bob_y = 0.0

        # --- defeat / explosion state ---------------------------------
        self._defeated = False
        self._explo_t = None     # None = not exploding; else elapsed seconds
        self._fires = []         # list of dicts: per fire-circle burst
        self._sparks = []        # list of dicts: flung debris

        # --- hologram state -------------------------------------------
        self._holo_tex = None
        self._holo_tried = False
        self._holo_is_portrait = False

    # ------------------------------------------------------------------
    def update(self, dt, ship_position):
        self._t += dt
        self._bob_y = BOB_AMPLITUDE * math.sin(self._t * BOB_SPEED)

        if ship_position is not None and not self._defeated:
            cx, cy, cz = self._world_center()
            dx = float(ship_position[0]) - cx
            dz = float(ship_position[2]) - cz
            if abs(dx) > 1e-6 or abs(dz) > 1e-6:
                drift = IDLE_DRIFT_AMP * math.sin(self._t * IDLE_DRIFT_SPD)
                target = math.atan2(dx, dz) + drift
                diff = _wrap_angle(target - self._yaw)
                step = YAW_SPEED * dt
                if diff > step:
                    self._yaw += step
                elif diff < -step:
                    self._yaw -= step
                else:
                    self._yaw = target
                self._yaw = _wrap_angle(self._yaw)

        if self._explo_t is not None:
            self._explo_t += dt
            for sp in self._sparks:           # advance debris physics
                sp["age"] += dt
                drag = max(0.0, 1.0 - EXPLO_SPARK_DRAG * dt)
                sp["vel"] *= drag
                sp["pos"] = sp["pos"] + sp["vel"] * dt
            if self._explo_t >= EXPLO_DURATION:
                self._explo_t = None          # done; body stays gone

    # ------------------------------------------------------------------
    def _world_center(self):
        return self.base_pos + np.array([0.0, self._bob_y, 0.0])

    def play_defeat(self):
        """Trigger the multi-burst explosion; afterward the body is gone."""
        if self._defeated:
            return
        self._defeated = True
        self._explo_t = 0.0
        center = self._world_center()
        r = self._HULL_R * self.size

        # Several fire circles: random spot all over the hull, random size,
        # staggered start times -> a chain detonation rather than one puff.
        self._fires = []
        for _ in range(EXPLO_NUM_FIRE):
            offs = np.random.uniform(-1.0, 1.0, 3)
            offs *= r * EXPLO_SPREAD
            self._fires.append(dict(
                offset=offs,
                peak=np.random.uniform(EXPLO_SIZE_MIN, EXPLO_SIZE_MAX) * self.size,
                start=np.random.uniform(0.0, EXPLO_STAGGER),
                life=EXPLO_FIRE_LIFE * np.random.uniform(0.8, 1.3),
                hue=np.random.uniform(0.0, 1.0),   # 0=hot ... 1=ember
            ))

        # Flung debris sparks in random directions.
        self._sparks = []
        for _ in range(EXPLO_NUM_SPARKS):
            d = np.random.uniform(-1.0, 1.0, 3)
            n = np.linalg.norm(d)
            d = d / n if n > 1e-6 else np.array([0.0, 1.0, 0.0])
            speed = EXPLO_SPARK_SPD * self.size * np.random.uniform(0.5, 1.0)
            self._sparks.append(dict(
                pos=center.copy(),
                vel=d * speed,
                age=0.0,
                life=EXPLO_SPARK_LIFE * np.random.uniform(0.7, 1.2),
            ))

    def is_defeated(self) -> bool:
        return self._defeated

    # ------------------------------------------------------------------
    def draw(self, camera_right, camera_up, texcache):
        if self._defeated:
            if self._explo_t is not None:
                self._draw_explosion(camera_right, camera_up)
            return

        cx, cy, cz = self._world_center()

        glPushMatrix()
        glTranslatef(cx, cy, cz)
        glRotatef(math.degrees(self._yaw), 0.0, 1.0, 0.0)
        glScalef(self.size, self.size, self.size)

        glDisable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)

        self._draw_hull()
        self._draw_visor_slot()
        self._draw_scanner()

        glPopMatrix()

        self._draw_hologram(cx, cy, cz, camera_right, camera_up, texcache)

    # ------------------------------------------------------------------
    def _draw_hull(self):
        v = self._hull_verts
        glBegin(GL_TRIANGLES)
        for i, col in enumerate(self._hull_cols):
            glColor3f(*col)
            for vert in v[3 * i:3 * i + 3]:
                glVertex3f(*vert)
        glEnd()

    # ------------------------------------------------------------------
    def _visor_rect(self):
        t00, t10, t11, t01 = self._face_quad
        face_z = t00[2]
        half_w = abs(t10[0]) * 0.82
        cy = (t00[1] + t01[1]) * 0.5
        half_h = abs(t01[1] - t00[1]) * 0.5 * 0.34
        z = face_z + 0.02
        return (-half_w, half_w, cy - half_h, cy + half_h, z)

    def _draw_visor_slot(self):
        x0, x1, y0, y1, z = self._visor_rect()
        fx0, fx1 = x0 - 0.10, x1 + 0.10
        fy0, fy1 = y0 - 0.10, y1 + 0.10
        glColor3f(*VISOR_BLACK)
        glBegin(GL_QUADS)
        glVertex3f(fx0, fy0, z); glVertex3f(fx1, fy0, z)
        glVertex3f(fx1, fy1, z); glVertex3f(fx0, fy1, z)
        glEnd()

    # ------------------------------------------------------------------
    def _draw_scanner(self):
        x0, x1, y0, y1, z = self._visor_rect()
        er, eg, eb = self.eye_color
        zz = z + 0.01
        s = 0.5 + 0.5 * math.sin(self._t * SCAN_SPEED)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glDepthMask(GL_FALSE)

        n = SCAN_SEGMENTS
        seg_w = (x1 - x0) / n
        glBegin(GL_QUADS)
        for i in range(n):
            cpos = (i + 0.5) / n
            d = abs(cpos - s)
            inten = math.exp(-(d * SCAN_TAIL) ** 2)
            if inten < 0.02:
                continue
            inten = min(1.0, inten * (1.0 + SCAN_CORE_BOOST))
            gx0 = x0 + i * seg_w
            gx1 = gx0 + seg_w
            glColor4f(er, eg, eb, inten)
            glVertex3f(gx0, y0, zz); glVertex3f(gx1, y0, zz)
            glVertex3f(gx1, y1, zz); glVertex3f(gx0, y1, zz)
        glEnd()

        dot_x = x0 + s * (x1 - x0)
        hw = (x1 - x0) * 0.10
        hh = (y1 - y0) * 1.6
        cyv = (y0 + y1) * 0.5
        glBegin(GL_QUADS)
        glColor4f(er, eg, eb, 0.35)
        glVertex3f(dot_x - hw, cyv - hh, zz)
        glVertex3f(dot_x + hw, cyv - hh, zz)
        glVertex3f(dot_x + hw, cyv + hh, zz)
        glVertex3f(dot_x - hw, cyv + hh, zz)
        glEnd()

        glDepthMask(GL_TRUE)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_BLEND)

        # TODO(DeepSeek): SCANNER AUDIO HOOK -- soft "wom-wom" once per
        #   end-to-end sweep (s near 0 or 1). Visual-only module; wire a
        #   callback from the audio module.

    # ------------------------------------------------------------------
    def _draw_hologram(self, cx, cy, cz, camera_right, camera_up, texcache):
        if self._holo_tex is None and not self._holo_tried:
            self._holo_tried = True
            self._holo_tex = load_portrait(self.name)
            self._holo_is_portrait = self._holo_tex is not None
            if self._holo_tex is None:
                self._holo_tex = texcache.get_mathtext(
                    "[%s]" % self.name, color=HOLO_TINT, fontsize=15)

        holo_bob = HOLO_BOB_AMP * math.sin(self._t * HOLO_BOB_SPD)
        center = (cx, cy + HOLO_HEIGHT_ABOVE * self.size + holo_bob, cz)

        glEnable(GL_BLEND)
        glDepthMask(GL_FALSE)
        glDisable(GL_DEPTH_TEST)

        if self._holo_is_portrait:
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)   # black vanishes, figure glows
            render.draw_billboard(self._holo_tex, center,
                                  camera_right, camera_up,
                                  scale=HOLO_SCALE * self.size,
                                  alpha=HOLO_PORTRAIT_ALPHA)
        else:
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            render.draw_billboard(self._holo_tex, center,
                                  camera_right, camera_up,
                                  scale=HOLO_SCALE * self.size,
                                  alpha=HOLO_ALPHA)

        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_BLEND)

    # ------------------------------------------------------------------
    # EXPLOSION: a bright flash, several expanding fire CIRCLES at random
    # spots all over the hull (random size + staggered), and flung debris
    # sparks. All additive billboards -> a fiery burst in the dark mine.
    # ------------------------------------------------------------------
    def _fire_color(self, hue, fade):
        """Blend hot->orange->ember by hue, then dim by fade (0..1)."""
        if hue < 0.5:
            base = EXPLO_HOT * (1.0 - hue * 2.0) + EXPLO_MID * (hue * 2.0)
        else:
            h = (hue - 0.5) * 2.0
            base = EXPLO_MID * (1.0 - h) + EXPLO_EDGE * h
        return base * fade

    def _draw_explosion(self, camera_right, camera_up):
        t = self._explo_t
        if t is None:
            return
        r = np.asarray(camera_right, float)
        u = np.asarray(camera_up, float)
        center = self._world_center()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)   # additive fire
        glDepthMask(GL_FALSE)

        # 1) initial white-hot flash (fast)
        if t < EXPLO_FLASH_LIFE:
            f = t / EXPLO_FLASH_LIFE
            sz = EXPLO_FLASH_SIZE * self.size * (0.4 + 0.6 * f)
            self._disk(center, sz, r, u, EXPLO_HOT, (1.0 - f))

        # 2) several expanding fire circles all over the hull
        for fire in self._fires:
            local = t - fire["start"]
            if local < 0.0 or local > fire["life"]:
                continue
            p = local / fire["life"]            # 0..1 progress
            diam = fire["peak"] * (0.25 + 0.95 * p)   # expands
            fade = (1.0 - p) ** 1.4                   # fades out
            col = self._fire_color(fire["hue"], fade)
            pos = center + fire["offset"]
            self._disk(pos, diam, r, u, col, 1.0)

        # 3) flung debris sparks (bright streaks fading as they fly)
        glBegin(GL_LINES)
        for sp in self._sparks:
            if sp["age"] > sp["life"]:
                continue
            life_f = 1.0 - sp["age"] / sp["life"]
            col = self._fire_color(0.3, life_f)
            p1 = sp["pos"]
            p0 = sp["pos"] - sp["vel"] * 0.04   # short tail behind it
            glColor4f(col[0], col[1], col[2], life_f)
            glVertex3f(*p0)
            glColor4f(col[0], col[1], col[2], life_f * 0.3)
            glVertex3f(*p1)
        glEnd()

        glDepthMask(GL_TRUE)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_BLEND)

    def _disk(self, center, diameter, cright, cup, rgb, alpha):
        """A soft glowing CIRCLE (triangle fan) facing the camera: bright
        core fading to transparent at the rim -> reads as a fireball."""
        c = np.asarray(center, float)
        rad = diameter * 0.5
        r = np.asarray(cright, float)
        u = np.asarray(cup, float)
        n = EXPLO_CIRCLE_SEG
        glBegin(GL_TRIANGLE_FAN)
        glColor4f(rgb[0], rgb[1], rgb[2], min(1.0, alpha))   # hot center
        glVertex3f(*c)
        for i in range(n + 1):
            a = 2.0 * math.pi * i / n
            edge = c + (r * math.cos(a) + u * math.sin(a)) * rad
            glColor4f(rgb[0], rgb[1], rgb[2], 0.0)           # transparent rim
            glVertex3f(*edge)
        glEnd()


# ======================================================================
def make_robot(robot_data, palette, station_pose, paint=None, size=1.0):
    return Robot(robot_data, palette, station_pose, paint=paint, size=size)


# render imported last to avoid import-order surprises.
import render  # noqa: E402