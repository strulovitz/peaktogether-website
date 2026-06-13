"""robots.py -- DESCENT QED, MODULE: robots.

A Robot is a HOVERING MACHINE. NOT humanoid. No head/face/arms/legs.
One faceted grey-metal hull + a recessed black "visor" slot on the front
face, across which a single bright LARSON SCANNER dot sweeps left<->right
with a comet-tail afterglow (Cylon / KITT). Hover-bob + slow yaw that
TURNS TOWARD the player and tracks them (with a faint idle drift so the
machine always reads as a solid 3D object, never a flat sprite). An
always-on hologram PORTRAIT floats above it (real PNG, glowing-blue figure
on black, drawn additively so the black vanishes). A defeat fireball plays
once, then the body is gone.

THE ENGINE IS MATHEMATICS-BLIND. This module reads ONLY:
    robot_data.name           -> hologram portrait file + placeholder text
    robot_data.eye_color_key  -> palette.eye(key) -> SCANNER color (MEANING)
It never interprets equations and never picks colors by meaning.

ALL meaning-color comes from `palette.eye(key)`. Hull paint and the black
visor slot are DECORATION (chosen here), never meaning. The camera is
RECEIVED as parameters (camera_right / camera_up); a robot never owns or
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
#   the fireball is a clear hot flash.
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

# Defeat fireball.
FIREBALL_DURATION = 0.85  # seconds
FIREBALL_MAX_SIZE = 4.5   # world units across at peak
FIREBALL_HOT      = (1.0, 0.85, 0.30)  # yellow-hot core
FIREBALL_EDGE     = (1.0, 0.35, 0.05)  # orange edge


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
#   (spaces -> underscores, then the "-hologram.png" suffix)
# Files are looked for in the folder the program runs from, then next to
# this module as a fallback.
#
# The supplied portraits are a glowing-blue figure on a SOLID BLACK square.
# draw() blends them ADDITIVELY so the black vanishes and only the figure
# glows -> a true floating hologram. They are already blue; we do NOT tint.

_PORTRAIT_CACHE = {}   # filename -> (tid, w, h) or None; load each PNG once


def _portrait_filename(name):
    return name.strip().replace(" ", "_") + "-hologram.png"


def _find_portrait(filename):
    """Search the current working dir, then this module's dir."""
    candidates = [
        os.path.join(os.getcwd(), filename),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), filename),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def load_portrait(name):
    """Return (tid, w, h) for the robot's hologram PNG, or None if the file
    isn't present (caller then falls back to a text placeholder)."""
    filename = _portrait_filename(name)
    if filename in _PORTRAIT_CACHE:
        return _PORTRAIT_CACHE[filename]

    path = _find_portrait(filename)
    if path is None:
        print("DEBUG: hologram portrait not found: %s "
              "(searched cwd + module dir)" % filename)
        _PORTRAIT_CACHE[filename] = None
        return None

    surf = pygame.image.load(path).convert_alpha()    # keeps any alpha
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
# Chunky industrial silhouette: a hexagonal-prism body with a tapered
# wedge "snout" giving it a front FACE to mount the visor on, plus two
# stubby side pods (NOT arms -- tool/thruster mounts). Non-humanoid by
# construction. Forward is +Z. Up is +Y.

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
    """Tapered box snout from a rectangle at base_z to a smaller rectangle
    at tip_z (the front FACE the visor mounts on)."""
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
    """Return (hull_tris, front_face_quad)."""
    body = _prism(6, 1.45, 0.85, phase=math.radians(30))
    snout, face = _wedge_snout(base_hw=1.25, base_hh=0.78, base_z=1.25,
                               tip_z=2.15, tip_hw=0.80, tip_hh=0.42)
    pods = (_box(-1.45, -0.15, 0.10, 0.32, 0.32, 0.62)
            + _box(1.45, -0.15, 0.10, 0.32, 0.32, 0.62))
    return body + snout + pods, face


def _shade(tri, base_rgb):
    """Fake flat shading: ambient + diffuse(|n.L|) + a sharp specular GLINT
    (metallic) so a few facets catch a bright highlight -> reads SHINY
    against the dull matte rock walls."""
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

    def __init__(self, robot_data, palette, station_pose,
                 paint=None, size=1.0):
        # --- data path (the ONLY things robots reads from RobotData) ---
        self.name = getattr(robot_data, "name", "[ROBOT]")
        self._eye_key = getattr(robot_data, "eye_color_key", "NEUTRAL")

        self._palette = palette
        # SCANNER COLOR = MEANING. ledger -> palette.eye -> robot.
        self.eye_color = tuple(palette.eye(self._eye_key))

        # --- placement -------------------------------------------------
        # station_pose is either (x,y,z) OR ((x,y,z), base_yaw_radians).
        if (isinstance(station_pose, (tuple, list)) and len(station_pose) == 2
                and isinstance(station_pose[0], (tuple, list, np.ndarray))):
            self.base_pos = np.asarray(station_pose[0], dtype=float)
            seat_yaw = float(station_pose[1])
        else:
            self.base_pos = np.asarray(station_pose, dtype=float)
            seat_yaw = 0.0

        self.size = float(size)

        # --- paint (DECORATION, never meaning) ------------------------
        if paint is None:
            self._hull_base = HULL_GREY
        else:
            self._hull_base = np.asarray(paint, dtype=float)

        self._hull_cols = [_shade(t, self._hull_base) for t in self._hull_tris]
        self._hull_verts = np.array(
            [v for t in self._hull_tris for v in t], dtype=float)

        # --- animation state ------------------------------------------
        self._t = 0.0
        # Option C: START at a RANDOM angle ("surprised"), then turn to
        # face the player. Idle drift rides on top so it's never glued.
        self._yaw = seat_yaw + np.random.uniform(-math.pi, math.pi)
        self._bob_y = 0.0

        # --- defeat state ---------------------------------------------
        self._defeated = False
        self._fireball_t = None

        # --- hologram state -------------------------------------------
        self._holo_tex = None          # cached (tid,w,h)
        self._holo_tried = False       # have we attempted to load the PNG?
        self._holo_is_portrait = False # True if showing the real portrait

    # ------------------------------------------------------------------
    def update(self, dt, ship_position):
        """Advance hover-bob, scanner sweep, and slow yaw toward the player
        (Option C: track + faint idle drift). No physics/collision. Still
        advances the fireball clock if defeating."""
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

        if self._fireball_t is not None:
            self._fireball_t += dt
            if self._fireball_t >= FIREBALL_DURATION:
                self._fireball_t = None

    # ------------------------------------------------------------------
    def _world_center(self):
        return self.base_pos + np.array([0.0, self._bob_y, 0.0])

    def play_defeat(self):
        """Trigger the defeat fireball; afterward the body is gone."""
        if not self._defeated:
            self._defeated = True
            self._fireball_t = 0.0

    def is_defeated(self) -> bool:
        return self._defeated

    # ------------------------------------------------------------------
    def draw(self, camera_right, camera_up, texcache):
        """Hull + visor + scanner + always-on hologram. If defeated, draw
        only the (fading) fireball -- no body."""
        if self._defeated:
            if self._fireball_t is not None:
                self._draw_fireball(camera_right, camera_up)
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
        """(x0,x1, y0,y1, z) of the visor slot in local space, sitting just
        in front of the snout face."""
        t00, t10, t11, t01 = self._face_quad
        face_z = t00[2]
        half_w = abs(t10[0]) * 0.82
        cy = (t00[1] + t01[1]) * 0.5
        half_h = abs(t01[1] - t00[1]) * 0.5 * 0.34   # narrow horizontal slot
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
    # LARSON SCANNER: a single bright dot sweeps left<->right across the
    # visor slot with a comet-tail afterglow. SCAN_SEGMENTS lit cells whose
    # brightness falls off with distance from the moving dot. Additive
    # blend, depth-write off -> emissive glow in the eye color (MEANING).
    # ------------------------------------------------------------------
    def _draw_scanner(self):
        x0, x1, y0, y1, z = self._visor_rect()
        er, eg, eb = self.eye_color
        zz = z + 0.01

        s = 0.5 + 0.5 * math.sin(self._t * SCAN_SPEED)  # 0..1 sweep position

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)     # additive -> glow
        glDepthMask(GL_FALSE)

        n = SCAN_SEGMENTS
        seg_w = (x1 - x0) / n
        glBegin(GL_QUADS)
        for i in range(n):
            cpos = (i + 0.5) / n
            d = abs(cpos - s)
            inten = math.exp(-(d * SCAN_TAIL) ** 2)   # comet tail
            if inten < 0.02:
                continue
            inten = min(1.0, inten * (1.0 + SCAN_CORE_BOOST))
            gx0 = x0 + i * seg_w
            gx1 = gx0 + seg_w
            glColor4f(er, eg, eb, inten)
            glVertex3f(gx0, y0, zz); glVertex3f(gx1, y0, zz)
            glVertex3f(gx1, y1, zz); glVertex3f(gx0, y1, zz)
        glEnd()

        # soft bloom halo around the current dot
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

        # TODO(DeepSeek): SCANNER AUDIO HOOK. The classic Cylon/KITT sweep
        #   has a synced "wom-wom" whoosh, triggered once when the dot
        #   reaches each end (s near 0 or 1). This module is visual-only;
        #   wire a callback from the audio module. | ACCEPTANCE: a soft
        #   pulse plays once per end-to-end sweep, not every frame.

    # ------------------------------------------------------------------
    # HOLOGRAM: always-on portrait above the robot, camera-facing. The PNG
    # is a glowing-blue figure on a SOLID BLACK square, drawn ADDITIVELY so
    # the black vanishes and only the figure glows. Text fallback (if the
    # PNG is missing) uses ordinary alpha blend.
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
        glDisable(GL_DEPTH_TEST)   # floating overlay

        if self._holo_is_portrait:
            # glowing figure on black -> additive makes the black vanish
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)
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
    # FIREBALL: expanding hot additive billboard, fades over its duration.
    # ------------------------------------------------------------------
    def _draw_fireball(self, camera_right, camera_up):
        if self._fireball_t is None:
            return
        cx, cy, cz = self._world_center()
        f = max(0.0, min(1.0, self._fireball_t / FIREBALL_DURATION))
        size = FIREBALL_MAX_SIZE * self.size * (0.25 + 0.75 * f)
        alpha = 1.0 - f
        center = (cx, cy, cz)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)   # additive hot flash
        glDepthMask(GL_FALSE)

        self._emit_billboard_quad(center, size, camera_right, camera_up,
                                  FIREBALL_EDGE, alpha * 0.7)
        self._emit_billboard_quad(center, size * 0.55, camera_right,
                                  camera_up, FIREBALL_HOT, alpha)

        glDepthMask(GL_TRUE)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_BLEND)

    def _emit_billboard_quad(self, center, size, cright, cup, rgb, alpha):
        h = size * 0.5
        r = np.asarray(cright, float)
        u = np.asarray(cup, float)
        c = np.asarray(center, float)
        p0 = c - r * h - u * h
        p1 = c + r * h - u * h
        p2 = c + r * h + u * h
        p3 = c - r * h + u * h
        glBegin(GL_QUADS)
        glColor4f(rgb[0], rgb[1], rgb[2], alpha)
        glVertex3f(*p0); glVertex3f(*p1); glVertex3f(*p2); glVertex3f(*p3)
        glEnd()


# ======================================================================
def make_robot(robot_data, palette, station_pose, paint=None, size=1.0):
    """Factory mirroring Robot's interface (cleaner call site for
    corridor_builder)."""
    return Robot(robot_data, palette, station_pose, paint=paint, size=size)


# render imported last to avoid import-order surprises; draw_billboard is
# the only render verb robots calls.
import render  # noqa: E402