# render.py
# =====================================================================
#  Descent QED -- RENDER MODULE
#  Legacy fixed-function OpenGL primitives only (no shaders, no VBOs).
#  Style and approach mined from Fable's BIBLE/math_flyer.py and
#  descent_qed_main.py where useful (see Completion Report at bottom).
#
#  PORTABILITY: this is the same legacy-GL style as Fable. It is verified
#  for Windows and Linux. macOS may show a BLACK WINDOW because Apple
#  deprecated the legacy GL profile -- see the macOS comment in
#  render_demo.py next to set_mode for the fix.
# =====================================================================

import io
import math
import numpy as np

import matplotlib
matplotlib.use("Agg")  # PORTABLE: pure-software rasterizer, identical on
                       # Windows / macOS / Linux, needs no display server.
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective

import palette

# ---------------------------------------------------------------------
#  FOG / DISTANCE-DARKENING -- PRODUCTION CONSTANTS OWNED BY render.py.
#  These are NOT placeholders. render owns them. They take effect in every
#  frame, every draw call, forever -- far geometry is rendered darker
#  (fogged toward palette.CLEAR_COLOR). Fog runs linearly from DARKNESS_START
#  to DARKNESS_END world units. Change them here to change the look of
#  distance in the whole engine.
# ---------------------------------------------------------------------
DARKNESS_START = 40.0
DARKNESS_END   = 140.0


# =====================================================================
#  GL LIFECYCLE
# =====================================================================

def init_gl(win_size, fog_start=DARKNESS_START, fog_end=DARKNESS_END):
    """Set up the GL state for the 3D world. Call once after the window
    is created. Enables depth, blending, and linear distance-fog so that
    far-away geometry is rendered DARKER (fogged toward palette.CLEAR_COLOR)."""
    glClearColor(*palette.CLEAR_COLOR, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDisable(GL_CULL_FACE)        # walls are seen from both sides
    set_fog(fog_start, fog_end)    # distance-darkening (see set_fog)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(70.0, win_size[0] / win_size[1], 0.1, 300.0)
    glMatrixMode(GL_MODELVIEW)


def set_fog(start=DARKNESS_START, end=DARKNESS_END, color=None):
    """Linear distance-fog: geometry fades to `color` between `start` and
    `end` world units away, i.e. far things are drawn darker. Fogs toward
    palette.CLEAR_COLOR by default. This is a permanent part of the render
    engine, on in every frame."""
    if color is None:
        color = palette.CLEAR_COLOR
    glEnable(GL_FOG)
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogfv(GL_FOG_COLOR, (*color, 1.0))
    glFogf(GL_FOG_START, start)
    glFogf(GL_FOG_END, end)


# =====================================================================
#  QUATERNION 6-DOF CAMERA (DEMO-ONLY)
#  Mined from Fable's math_flyer.py. Quaternions are numpy [w, x, y, z].
#  This is the canonical camera-basis source: billboards get their
#  `right` / `up` from ship_right(q) / ship_up(q).
# =====================================================================

def quat_mul(a, b):
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return np.array([
        aw*bw - ax*bx - ay*by - az*bz,
        aw*bx + ax*bw + ay*bz - az*by,
        aw*by - ax*bz + ay*bw + az*bx,
        aw*bz + ax*by - ay*bx + az*bw], dtype=float)


def quat_from_axis_angle(axis, angle):
    axis = np.asarray(axis, dtype=float)
    n = np.linalg.norm(axis)
    if n < 1e-12:
        return np.array([1.0, 0, 0, 0])
    axis /= n
    h = 0.5 * angle
    return np.concatenate(([math.cos(h)], math.sin(h) * axis))


def quat_normalize(q):
    return q / np.linalg.norm(q)


def quat_rotate(q, v):
    """Rotate vector v by quaternion q (body -> world)."""
    w, x, y, z = q
    qv = np.array([x, y, z])
    t = 2.0 * np.cross(qv, v)
    return np.asarray(v, dtype=float) + w * t + np.cross(qv, t)


def quat_to_mat4(q):
    """4x4 rotation matrix (row-major numpy convention)."""
    w, x, y, z = q
    return np.array([
        [1-2*(y*y+z*z), 2*(x*y-w*z),   2*(x*z+w*y),   0],
        [2*(x*y+w*z),   1-2*(x*x+z*z), 2*(y*z-w*x),   0],
        [2*(x*z-w*y),   2*(y*z+w*x),   1-2*(x*x+y*y), 0],
        [0, 0, 0, 1]], dtype=np.float32)


def ship_forward(q):
    return quat_rotate(q, np.array([0.0, 0.0, -1.0]))


def ship_right(q):
    return quat_rotate(q, np.array([1.0, 0.0, 0.0]))


def ship_up(q):
    return quat_rotate(q, np.array([0.0, 1.0, 0.0]))


class Ship:
    """Descent-style 6-DOF camera: position + orientation quaternion +
    inertia. DEMO-ONLY -- a real game-mode Ship lives in its own module.
    Trimmed from Fable's math_flyer.py."""
    MAX_SPEED  = 18.0
    ACCEL      = 5.0
    BOOST      = 3.0
    PITCH_YAW  = math.radians(95)
    ROLL_SPEED = math.radians(140)

    def __init__(self, home_pos):
        self.home = np.asarray(home_pos, dtype=float)
        self.reset()

    def reset(self):
        self.pos = self.home.copy()
        self.q   = np.array([1.0, 0, 0, 0])
        self.vel = np.zeros(3)

    def rotate_local(self, axis, angle):
        if abs(angle) > 1e-9:
            self.q = quat_normalize(quat_mul(self.q,
                     quat_from_axis_angle(axis, angle)))

    def update(self, dt, keys):
        pitch = (keys[K_UP]   - keys[K_DOWN])  * self.PITCH_YAW  * dt
        yaw   = (keys[K_LEFT] - keys[K_RIGHT]) * self.PITCH_YAW  * dt
        roll  = (keys[K_q]    - keys[K_e])     * self.ROLL_SPEED * dt
        self.rotate_local([1, 0, 0], pitch)
        self.rotate_local([0, 1, 0], yaw)
        self.rotate_local([0, 0, 1], roll)

        thrust = np.array([
            float(keys[K_d] - keys[K_a]),
            float(keys[K_r] - keys[K_f]),
            float(keys[K_s] - keys[K_w]),
        ])
        n = np.linalg.norm(thrust)
        if n > 1e-9:
            thrust /= n
        boost = self.BOOST if (keys[K_LSHIFT] or keys[K_RSHIFT]) else 1.0
        target = quat_rotate(self.q, thrust) * self.MAX_SPEED * boost
        self.vel += (target - self.vel) * min(1.0, self.ACCEL * dt)
        self.pos += self.vel * dt

    def apply_view(self):
        glLoadIdentity()
        glMultMatrixf(np.ascontiguousarray(quat_to_mat4(self.q)))
        glTranslatef(*(-self.pos))


# =====================================================================
#  3D PRIMITIVES (legacy immediate-mode)
# =====================================================================

def draw_wall(quad, fill_color, edge_color, fill_alpha):
    """Draw ONE wall quad using the mandated two-pass recipe:
       pass 1: filled translucent face,
       pass 2: solid edge outline on top.
    `quad` is 4 points (each xyz). NOTE: for correct see-through, all
    OPAQUE geometry (and billboards) should be drawn BEFORE any translucent
    wall fills -- see draw order in render_demo.py. This function only draws
    the single wall; the caller controls ordering."""
    # --- pass 1: translucent fill ---
    glDisable(GL_TEXTURE_2D)
    glColor4f(fill_color[0], fill_color[1], fill_color[2], fill_alpha)
    glBegin(GL_QUADS)
    for p in quad:
        glVertex3f(*p)
    glEnd()
    # --- pass 2: solid edge ---
    glColor4f(edge_color[0], edge_color[1], edge_color[2], 1.0)
    glBegin(GL_LINE_LOOP)
    for p in quad:
        glVertex3f(*p)
    glEnd()


# ---------------------------------------------------------------------
#  SHARED TRANSLUCENT-WALL QUEUE (parent ruling)
#  Translucent rock walls must be blended far-to-near or alpha looks
#  wrong at module seams. render owns ONE shared sort over ALL queued
#  walls so independent modules combine correctly in a single frame.
#
#  render STAYS STATELESS: it stores no camera. camera_pos is PASSED IN
#  to flush_walls() every frame.
#
#  !!! TRAP -- READ THIS !!!
#  If a frame enqueues walls via queue_wall() but nobody calls
#  flush_walls(), those walls are SILENTLY NEVER DRAWN. The queue just
#  keeps growing. The app frame loop MUST call flush_walls(ship.pos)
#  exactly once per frame.
# ---------------------------------------------------------------------
_wall_queue = []  # each item: (quad, fill_color, edge_color, fill_alpha)


def queue_wall(quad, fill_color, edge_color, fill_alpha):
    """Enqueue ONE translucent wall for this frame. Does not draw yet.
    Call during a module's draw(); the app calls flush_walls() once per
    frame to draw the whole queue far-to-near. Stores exactly what the
    existing draw_wall(quad, fill_color, edge_color, fill_alpha) needs."""
    _wall_queue.append((quad, fill_color, edge_color, fill_alpha))


def flush_walls(camera_pos):
    """Sort ALL queued walls far-to-near by squared distance of each
    quad's centroid to camera_pos, draw each via the EXISTING draw_wall,
    then clear the queue. No-op if the queue is empty. render stays
    stateless -- camera_pos is passed in, never stored."""
    if not _wall_queue:
        return
    cam = np.asarray(camera_pos)

    def _key(item):
        c = np.mean(np.asarray(item[0]), axis=0)  # centroid of the quad
        d = c - cam
        return -float(np.dot(d, d))               # negative => farthest first

    for quad, fill_color, edge_color, fill_alpha in sorted(_wall_queue, key=_key):
        draw_wall(quad, fill_color, edge_color, fill_alpha)
    _wall_queue.clear()


def draw_breadcrumb(pos, color, size=0.15):
    """A small marker (three crossed segments) at a world position."""
    x, y, z = pos
    glDisable(GL_TEXTURE_2D)
    glColor4f(color[0], color[1], color[2], 1.0)
    glBegin(GL_LINES)
    for dx, dy, dz in ((size,0,0),(0,size,0),(0,0,size)):
        glVertex3f(x-dx, y-dy, z-dz)
        glVertex3f(x+dx, y+dy, z+dz)
    glEnd()


def draw_box_edges(lo, hi, color):
    """Wireframe axis-aligned box from corner `lo` to corner `hi`."""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    v = [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
         (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),
             (0,4),(1,5),(2,6),(3,7)]
    glDisable(GL_TEXTURE_2D)
    glColor4f(color[0], color[1], color[2], 1.0)
    glBegin(GL_LINES)
    for a, b in edges:
        glVertex3f(*v[a]); glVertex3f(*v[b])
    glEnd()


def draw_billboard(tex, center, camera_right, camera_up, scale=1.0, alpha=1.0):
    """Draw a textured quad always facing the camera, using the camera's
    `right` and `up` basis vectors (get these from ship_right(q) /
    ship_up(q)). `tex` is the (tid, w, h) tuple from TexCache.
    NOTE: billboards are OPAQUE-pass content -- draw them before
    translucent wall fills."""
    tid, w, h = tex
    aspect = w / h if h else 1.0
    hw = 0.5 * scale * aspect
    hh = 0.5 * scale
    c  = np.asarray(center, dtype=float)
    r  = np.asarray(camera_right, dtype=float)
    u  = np.asarray(camera_up, dtype=float)
    p00 = c - r*hw - u*hh
    p10 = c + r*hw - u*hh
    p11 = c + r*hw + u*hh
    p01 = c - r*hw + u*hh
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tid)
    glColor4f(1, 1, 1, alpha)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex3f(*p00)
    glTexCoord2f(1, 0); glVertex3f(*p10)
    glTexCoord2f(1, 1); glVertex3f(*p11)
    glTexCoord2f(0, 1); glVertex3f(*p01)
    glEnd()
    glDisable(GL_TEXTURE_2D)


# =====================================================================
#  TEXT / MATHTEXT -> OpenGL texture
#  Mined from Fable's math_flyer.py. matplotlib mathtext (no system LaTeX),
#  Agg backend, transparent PNG. Adapted: my public API takes an RGB float
#  TUPLE for color (the contract later modules are written against); we
#  convert tuple -> hex internally before calling matplotlib.
# =====================================================================

def _rgb_to_hex(color):
    r, g, b = (int(round(255 * c)) for c in color)
    return "#%02X%02X%02X" % (r, g, b)


def latex_to_surface(latex, color=(0.95, 0.96, 0.98), fontsize=15, dpi=140):
    """Render a mathtext string to a transparent pygame Surface.
    `color` is an RGB float tuple in 0..1. Uses bbox_inches='tight' so
    matplotlib trims the glyph box for us (Fable's trick)."""
    fig = Figure(figsize=(8, 2))
    fig.patch.set_alpha(0.0)
    FigureCanvasAgg(fig)
    fig.text(0.02, 0.5, latex, fontsize=fontsize,
             color=_rgb_to_hex(color), va="center")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, transparent=True,
                bbox_inches="tight", pad_inches=0.06)
    buf.seek(0)
    return pygame.image.load(buf, "latex.png").convert_alpha()


def surface_to_texture(surf):
    """Upload a pygame Surface to a GL texture; returns (tid, w, h).
    The `True` flag in tostring flips Y for OpenGL (Fable's trick)."""
    data = pygame.image.tostring(surf, "RGBA", True)
    w, h = surf.get_size()
    tid = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tid)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, data)
    return tid, w, h


class TexCache:
    """Caches rendered mathtext textures so each equation is rasterized
    only once. Mined from Fable's TexCache.

    !!! RECYCLING TRAP -- READ THIS !!!
    When the cache exceeds LIMIT it calls glDeleteTextures on EVERY cached
    id and clears the dict. Those freed ids WILL be reused by the next
    glGenTextures. Therefore:
        >>> NEVER bake a texture id returned from this cache into a
        >>> display list. <<<
    A display list would keep drawing a stale id that may now point at a
    different glyph. Always draw cached textures with live immediate-mode
    calls (draw_billboard / draw_texture), never inside glNewList/glEndList.
    """
    LIMIT = 400

    def __init__(self):
        self.cache = {}

    def _prune(self):
        if len(self.cache) > self.LIMIT:
            for tid, _, _ in self.cache.values():
                glDeleteTextures([tid])   # <-- frees ids -> they get reused
            self.cache.clear()

    def get_mathtext(self, latex, color=(0.95, 0.96, 0.98), fontsize=15):
        key = (latex, fontsize, color)
        if key not in self.cache:
            self._prune()
            self.cache[key] = surface_to_texture(
                latex_to_surface(latex, color, fontsize))
        return self.cache[key]


# =====================================================================
#  2D OVERLAY (HUD)  -- mined from Fable's begin_2d / end_2d / draw_texture.
#  Note: Fable's begin_2d disables GL_FOG and GL_LIGHTING inside 2D, so HUD
#  text is NOT fog-darkened. We keep that.
#  We deliberately use TEXTURED QUADS (not glDrawPixels / glWindowPos that
#  Fable's draw_overlay_text used) -- textured quads are more portable
#  across GL drivers, notably on macOS.
# =====================================================================

def begin_2d(w, h):
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    glOrtho(0, w, h, 0, -1, 1)   # y-down = screen/mouse coords
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_FOG)            # HUD must not be fog-darkened
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


def end_2d():
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW); glPopMatrix()
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_FOG)             # fog is permanent: re-enable for the 3D world


def draw_texture(tex, x, y, scale=1.0, alpha=1.0):
    """Draw a (tid, w, h) texture as a 2D quad at screen (x, y). Call
    between begin_2d / end_2d. Returns drawn (w, h)."""
    tid, w, h = tex
    w *= scale; h *= scale
    glEnable(GL_TEXTURE_2D); glBindTexture(GL_TEXTURE_2D, tid)
    glColor4f(1, 1, 1, alpha)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 1); glVertex2f(x, y)
    glTexCoord2f(1, 1); glVertex2f(x + w, y)
    glTexCoord2f(1, 0); glVertex2f(x + w, y + h)
    glTexCoord2f(0, 0); glVertex2f(x, y + h)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    return w, h


def draw_text_mathtext_2d(cache, latex, x, y, color=(0.7, 0.7, 0.7),
                          fontsize=15, scale=1.0, alpha=1.0):
    """HUD convenience: render `latex` via the cache and blit at (x, y).
    Must be called between begin_2d / end_2d."""
    tex = cache.get_mathtext(latex, color, fontsize)
    return draw_texture(tex, x, y, scale, alpha)