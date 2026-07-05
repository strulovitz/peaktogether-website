Here it is — the first real thing. 🎉 The forge walking skeleton: a black window, a glowing cyan grid, the first vector arrow sweeping from the origin, a camera slowly orbiting. This is Build Sequence steps 1–2 from the New Testament (bloom comes in the next package — the lines already glow softly via the shader).

Below are 9 complete files. Send each one to DeepSeek exactly as-is, with its path, then follow the "HOW TO RUN" instructions at the end.

File 1 — requirements.txt

```
numpy
moderngl
pyglet>=2.0.9
Pillow
```

File 2 — run.bat

```
@echo off
cd /d %~dp0
echo Starting Homeworld: A Good Basis (forge walking skeleton)...
python -m forge.demo
pause
```

File 3 — settings.json

```
{
    "title": "Homeworld: A Good Basis",
    "version": "0.1.0",
    "width": 1280,
    "height": 720,
    "fullscreen": false,
    "vsync": true,
    "bloom_strength": 0.8,
    "seed": 1234
}
```

File 4 — forge/__init__.py

```python
"""forge — the render engine of Homeworld: A Good Basis.

A real-time Manim: glowing vector graphics in modern OpenGL.
See NEW_TESTAMENT.md Part 1 for the full design. This is the
walking skeleton (build steps 1-2): window, camera, line ribbons,
Line/Arrow/DashedLine/Grid/WireSphere. Bloom and text come next.
"""

from .app import Forge, PULSE_DT
from .camera import Camera
from .vobjects import VObject, Line, Arrow, DashedLine, Grid, WireSphere

__all__ = [
    "Forge", "PULSE_DT", "Camera",
    "VObject", "Line", "Arrow", "DashedLine", "Grid", "WireSphere",
]
```

File 5 — forge/camera.py

```python
"""Camera: ORBIT mode + view/projection math (NEW_TESTAMENT 1.3).

All math is plain numpy, float64. Right-handed, Y up.
FOLLOW and POV modes will be added in a later package; the frozen
interface methods exist now so no caller ever changes.
"""

import numpy as np


def _normalize(v):
    n = np.linalg.norm(v)
    if n < 1e-12:
        return v
    return v / n


def look_at(eye, target, up):
    """Standard right-handed look-at view matrix (4x4 float64)."""
    eye = np.asarray(eye, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    up = np.asarray(up, dtype=np.float64)
    f = _normalize(target - eye)          # forward
    s = _normalize(np.cross(f, up))       # right
    u = np.cross(s, f)                    # true up
    m = np.eye(4, dtype=np.float64)
    m[0, :3] = s
    m[1, :3] = u
    m[2, :3] = -f
    m[0, 3] = -s @ eye
    m[1, 3] = -u @ eye
    m[2, 3] = f @ eye
    return m


def perspective(fov_y, aspect, near, far):
    """Standard OpenGL perspective projection matrix (4x4 float64)."""
    t = 1.0 / np.tan(fov_y * 0.5)
    m = np.zeros((4, 4), dtype=np.float64)
    m[0, 0] = t / aspect
    m[1, 1] = t
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = (2.0 * far * near) / (near - far)
    m[3, 2] = -1.0
    return m


class Camera:
    def __init__(self):
        self.mode = "ORBIT"
        self.target = np.zeros(3, dtype=np.float64)
        self.yaw = 0.8          # radians
        self.pitch = 0.35       # radians, clamped to (-1.55, 1.55)
        self.distance = 32.0    # clamped to (2, 500)
        self.fov_y = 1.05       # ~60 degrees
        self.near = 0.1
        self.far = 2000.0

    # ---- frozen interface (NEW_TESTAMENT 1.3) ----

    def set_orbit(self, target):
        self.mode = "ORBIT"
        self.target = np.asarray(target, dtype=np.float64).copy()

    def orbit_input(self, d_yaw, d_pitch, d_zoom):
        self.yaw += d_yaw
        self.pitch = float(np.clip(self.pitch + d_pitch, -1.55, 1.55))
        self.distance = float(np.clip(self.distance * (1.0 + d_zoom), 2.0, 500.0))

    def eye(self):
        """Camera position: eye = target + d*(cos(p)sin(y), sin(p), cos(p)cos(y))."""
        cp = np.cos(self.pitch)
        offset = self.distance * np.array(
            [cp * np.sin(self.yaw), np.sin(self.pitch), cp * np.cos(self.yaw)],
            dtype=np.float64,
        )
        return self.target + offset

    def view(self):
        return look_at(self.eye(), self.target, np.array([0.0, 1.0, 0.0]))

    def proj(self, aspect):
        return perspective(self.fov_y, aspect, self.near, self.far)
```

File 6 — forge/shaders.py

```python
"""GLSL shader sources (NEW_TESTAMENT 1.6).

The line ribbon shader: each line is expanded on the CPU into a
camera-facing ribbon with a 'ribbon coordinate' u in [-1, 1] across
its width. The fragment shader shades intensity = (1 - u^2)^2 so
every line has a hot bright core and soft edges even before bloom.
"""

LINE_VERT = """
#version 330
uniform mat4 u_mvp;
in vec3 in_pos;
in vec4 in_color;
in float in_u;
out vec4 v_color;
out float v_u;
void main() {
    gl_Position = u_mvp * vec4(in_pos, 1.0);
    v_color = in_color;
    v_u = in_u;
}
"""

LINE_FRAG = """
#version 330
in vec4 v_color;
in float v_u;
out vec4 f_color;
void main() {
    float k = 1.0 - v_u * v_u;
    f_color = vec4(v_color.rgb * k * k * v_color.a, 1.0);
}
"""
```

File 7 — forge/vobjects.py

```python
"""VObjects: the primitive vocabulary (NEW_TESTAMENT 1.4).

Walking-skeleton set: Line, Arrow, DashedLine, Grid, WireSphere.
(SpannedBox, Ellipsoid, WireMesh, Trail, Label, ImagePanel arrive in
the next packages.)

Every primitive reduces itself to an array of line segments of shape
(N, 2, 3): N segments, each with two endpoints in 3D. set_data()
always copies its numpy inputs (no aliasing of caller memory).
"""

import numpy as np


class VObject:
    def __init__(self, color=(0.5, 0.9, 1.0, 1.0), glow=1.0, width=0.06):
        self.visible = True
        self.color = tuple(color)
        self.glow = float(glow)
        self.width = float(width)   # ribbon HALF-width in world units
        self._segments = np.zeros((0, 2, 3), dtype=np.float64)

    def set_color(self, rgba):
        self.color = tuple(rgba)

    def segments(self):
        return self._segments


class Line(VObject):
    """Polyline through N points. points: (N, 3)."""

    def __init__(self, points, **kw):
        super().__init__(**kw)
        self.set_data(points)

    def set_data(self, points):
        p = np.asarray(points, dtype=np.float64).reshape(-1, 3).copy()
        if p.shape[0] < 2:
            self._segments = np.zeros((0, 2, 3), dtype=np.float64)
            return
        self._segments = np.stack([p[:-1], p[1:]], axis=1)


class Arrow(VObject):
    """THE vector: a shaft plus a 4-line pyramid head with a base ring."""

    def __init__(self, start, end, head_size=0.5, **kw):
        kw.setdefault("width", 0.09)
        super().__init__(**kw)
        self.set_data(start, end, head_size)

    def set_data(self, start, end, head_size=0.5):
        start = np.asarray(start, dtype=np.float64).copy()
        end = np.asarray(end, dtype=np.float64).copy()
        axis = end - start
        length = np.linalg.norm(axis)
        if length < 1e-9:
            self._segments = np.zeros((0, 2, 3), dtype=np.float64)
            return
        d = axis / length
        head = min(head_size, 0.5 * length)
        ref = np.array([0.0, 1.0, 0.0])
        if abs(d @ ref) > 0.9:
            ref = np.array([1.0, 0.0, 0.0])
        u = ref - (ref @ d) * d
        u = u / np.linalg.norm(u)
        w = np.cross(d, u)
        base = end - d * head
        r = head * 0.4
        ring = [base + u * r, base + w * r, base - u * r, base - w * r]
        segs = [(start, end)]
        for i in range(4):
            segs.append((end, ring[i]))                # pyramid edges to tip
            segs.append((ring[i], ring[(i + 1) % 4]))  # base ring
        self._segments = np.array(segs, dtype=np.float64)


class DashedLine(VObject):
    """Straight line from start to end with equal dash/gap lengths."""

    def __init__(self, start, end, dash=0.5, **kw):
        super().__init__(**kw)
        self.set_data(start, end, dash)

    def set_data(self, start, end, dash=0.5):
        start = np.asarray(start, dtype=np.float64).copy()
        end = np.asarray(end, dtype=np.float64).copy()
        axis = end - start
        length = np.linalg.norm(axis)
        if length < 1e-9 or dash <= 0.0:
            self._segments = np.zeros((0, 2, 3), dtype=np.float64)
            return
        n = max(1, int(np.ceil(length / (2.0 * dash))))
        k = np.arange(n, dtype=np.float64)
        t0 = np.minimum((2.0 * k) * dash / length, 1.0)
        t1 = np.minimum((2.0 * k + 1.0) * dash / length, 1.0)
        p0 = start[None, :] + t0[:, None] * axis[None, :]
        p1 = start[None, :] + t1[:, None] * axis[None, :]
        self._segments = np.stack([p0, p1], axis=1)


class Grid(VObject):
    """Plane grid spanned by vectors u and v — THIS is how 'span' is drawn.

    Lines run through center + i*spacing*v along direction u, and
    through center + i*spacing*u along direction v, for i in [-n, n].
    """

    def __init__(self, center, u, v, n=10, spacing=1.0, **kw):
        kw.setdefault("color", (0.10, 0.55, 0.65, 1.0))
        kw.setdefault("width", 0.035)
        super().__init__(**kw)
        self.set_data(center, u, v, n, spacing)

    def set_data(self, center, u, v, n=10, spacing=1.0):
        c = np.asarray(center, dtype=np.float64).copy()
        u = np.asarray(u, dtype=np.float64).copy()
        v = np.asarray(v, dtype=np.float64).copy()
        idx = np.arange(-n, n + 1, dtype=np.float64) * spacing
        ext = n * spacing
        segs = []
        for i in idx:  # lines along u
            segs.append((c + i * v - ext * u, c + i * v + ext * u))
        for i in idx:  # lines along v
            segs.append((c + i * u - ext * v, c + i * u + ext * v))
        self._segments = np.array(segs, dtype=np.float64)


class WireSphere(VObject):
    """Three orthogonal great circles."""

    def __init__(self, center, radius, seg=24, **kw):
        super().__init__(**kw)
        self.set_data(center, radius, seg)

    def set_data(self, center, radius, seg=24):
        c = np.asarray(center, dtype=np.float64).copy()
        t = np.linspace(0.0, 2.0 * np.pi, seg + 1)
        cos_t, sin_t = np.cos(t), np.sin(t)
        zeros = np.zeros_like(t)
        circles = [
            np.stack([cos_t, sin_t, zeros], axis=1),  # XY plane
            np.stack([zeros, cos_t, sin_t], axis=1),  # YZ plane
            np.stack([cos_t, zeros, sin_t], axis=1),  # XZ plane
        ]
        segs = []
        for pts in circles:
            p = c[None, :] + radius * pts
            segs.append(np.stack([p[:-1], p[1:]], axis=1))
        self._segments = np.concatenate(segs, axis=0)
```

File 8 — forge/batches.py

```python
"""CPU geometry expansion (NEW_TESTAMENT 1.5).

Every line segment becomes a camera-facing ribbon (two triangles).
For a segment p0 -> p1 with half-width w and camera eye e:
    side = normalize( (p1 - p0) x (e - p0) )
    quad corners: p0 -/+ w*side, p1 +/- w*side
Each vertex carries a ribbon coordinate u in [-1, +1] across the
width; the fragment shader turns that into a hot core + soft edge.

Everything is vectorized numpy over ALL segments at once. The walking
skeleton rebuilds all geometry every frame (a few thousand segments is
trivial); the static/dynamic batch split is a later optimization.

Output vertex format (float32): x, y, z, r, g, b, a, u  -> '3f 4f 1f'.
"""

import numpy as np

_U_PATTERN = np.array([-1.0, 1.0, 1.0, -1.0, 1.0, -1.0], dtype=np.float64)


def build_vertices(vobjects, eye):
    """Collect all visible vobjects and expand to a (M, 8) float32 array."""
    seg_list, col_list, wid_list = [], [], []
    for vob in vobjects:
        if not vob.visible:
            continue
        s = vob.segments()
        n = s.shape[0]
        if n == 0:
            continue
        seg_list.append(s)
        c = np.empty((n, 4), dtype=np.float64)
        c[:, 0] = vob.color[0] * vob.glow
        c[:, 1] = vob.color[1] * vob.glow
        c[:, 2] = vob.color[2] * vob.glow
        c[:, 3] = vob.color[3]
        col_list.append(c)
        wid_list.append(np.full(n, vob.width, dtype=np.float64))
    if not seg_list:
        return np.zeros((0, 8), dtype=np.float32)
    segs = np.concatenate(seg_list, axis=0)
    cols = np.concatenate(col_list, axis=0)
    wids = np.concatenate(wid_list, axis=0)
    return _expand(segs, cols, wids, np.asarray(eye, dtype=np.float64))


def _expand(segs, cols, wids, eye):
    p0 = segs[:, 0, :]
    p1 = segs[:, 1, :]
    d = p1 - p0
    side = np.cross(d, eye[None, :] - p0)
    norms = np.linalg.norm(side, axis=1)
    bad = norms < 1e-9
    if np.any(bad):
        # Segment points straight at the eye (or is degenerate):
        # fall back to any vector perpendicular to d.
        for i in np.where(bad)[0]:
            alt = np.cross(d[i], np.array([0.0, 1.0, 0.0]))
            if np.linalg.norm(alt) < 1e-9:
                alt = np.cross(d[i], np.array([1.0, 0.0, 0.0]))
            if np.linalg.norm(alt) < 1e-9:
                alt = np.array([1.0, 0.0, 0.0])
            side[i] = alt
            norms[i] = np.linalg.norm(alt)
    side = side / norms[:, None]
    off = side * wids[:, None]

    a = p0 - off
    b = p0 + off
    c = p1 + off
    e2 = p1 - off

    n = segs.shape[0]
    pos = np.empty((n, 6, 3), dtype=np.float64)
    pos[:, 0] = a
    pos[:, 1] = b
    pos[:, 2] = c
    pos[:, 3] = a
    pos[:, 4] = c
    pos[:, 5] = e2

    col = np.repeat(cols[:, None, :], 6, axis=1)
    u = np.broadcast_to(_U_PATTERN, (n, 6))[..., None]

    out = np.concatenate([pos, col, u], axis=2).astype(np.float32)
    return out.reshape(-1, 8)
```

File 9 — forge/app.py

```python
"""The Forge class: window, GL context, main loop (NEW_TESTAMENT 1.2).

Owns the pyglet window, the moderngl context, the fixed-timestep
accumulator (10 Hz pulses -> tick_cb; every display frame -> frame_cb
with interpolation alpha), and the render pipeline.

Walking skeleton: single scene pass with additive blending; bloom FBOs
arrive in the next package. Additive blending is order-independent, so
no sorting is ever needed — overlapping glow simply gets brighter.
"""

import datetime
import os
import time

import numpy as np
import moderngl
import pyglet
from pyglet.window import key

from .camera import Camera
from .shaders import LINE_VERT, LINE_FRAG
from .batches import build_vertices

PULSE_DT = 0.1                       # 10 Hz logic pulse (frozen)
_INITIAL_VBO_BYTES = 4 * 1024 * 1024  # room for ~20k segments


class Forge:
    def __init__(self, settings):
        self._settings = dict(settings)
        width = int(settings.get("width", 1280))
        height = int(settings.get("height", 720))
        title = settings.get("title", "Homeworld: A Good Basis")
        version = settings.get("version", "0.0.0")
        self._caption_base = f"{title} — forge v{version}"

        config = pyglet.gl.Config(
            double_buffer=True, major_version=3, minor_version=3, depth_size=24
        )
        self.window = pyglet.window.Window(
            width=width,
            height=height,
            caption=self._caption_base,
            resizable=True,
            config=config,
            vsync=bool(settings.get("vsync", True)),
            fullscreen=bool(settings.get("fullscreen", False)),
        )
        self.window.switch_to()
        self.ctx = moderngl.create_context()

        self._prog = self.ctx.program(
            vertex_shader=LINE_VERT, fragment_shader=LINE_FRAG
        )
        self._vbo = self.ctx.buffer(reserve=_INITIAL_VBO_BYTES, dynamic=True)
        self._vao = self._make_vao()

        self.camera = Camera()
        self._vobjects = []
        self._want_screenshot = False

        # F12 = screenshot (system button). push_handlers keeps pyglet's
        # default handler alive, so ESC still closes the window.
        def _on_key_press(symbol, modifiers):
            if symbol == key.F12:
                self._want_screenshot = True

        self.window.push_handlers(on_key_press=_on_key_press)

        # fps counter shown in the window title once per second
        self._fps_frames = 0
        self._fps_t0 = time.perf_counter()

    # ---- frozen interface (NEW_TESTAMENT 1.2) ----

    def add(self, vob):
        if vob not in self._vobjects:
            self._vobjects.append(vob)

    def remove(self, vob):
        if vob in self._vobjects:
            self._vobjects.remove(vob)

    def set_debug_lines(self, lines):
        # Text rendering arrives with forge/text.py in a later package.
        # The interface exists now so callers never change.
        self._debug_lines = list(lines)

    def screenshot(self, path=None):
        os.makedirs("screenshots", exist_ok=True)
        if path is None:
            stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join("screenshots", f"{stamp}.png")
        pyglet.image.get_buffer_manager().get_color_buffer().save(path)
        return path

    def run(self, tick_cb, frame_cb):
        """Main loop. tick_cb(dt) at exactly 10 Hz; frame_cb(alpha) per frame."""
        prev = time.perf_counter()
        accumulator = 0.0
        while not self.window.has_exit:
            self.window.dispatch_events()
            if self.window.has_exit:
                break
            now = time.perf_counter()
            real_dt = min(now - prev, 0.25)  # clamp to survive hitches
            prev = now
            accumulator += real_dt
            while accumulator >= PULSE_DT:
                tick_cb(PULSE_DT)
                accumulator -= PULSE_DT
            frame_cb(accumulator / PULSE_DT)
            self._render()
            if self._want_screenshot:
                self._want_screenshot = False
                saved = self.screenshot()
                print(f"screenshot saved: {saved}")
            self.window.flip()
            self._count_fps()
        self.window.close()

    # ---- internals ----

    def _make_vao(self):
        return self.ctx.vertex_array(
            self._prog, [(self._vbo, "3f 4f 1f", "in_pos", "in_color", "in_u")]
        )

    def _render(self):
        w, h = self.window.get_framebuffer_size()
        if w <= 0 or h <= 0:
            return
        self.ctx.viewport = (0, 0, w, h)
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = (moderngl.ONE, moderngl.ONE)  # additive glow

        mvp = self.camera.proj(w / h) @ self.camera.view()
        self._prog["u_mvp"].write(np.ascontiguousarray(mvp.T, dtype=np.float32))

        data = build_vertices(self._vobjects, self.camera.eye())
        if data.shape[0] == 0:
            return
        if data.nbytes > self._vbo.size:
            self._vbo.release()
            self._vbo = self.ctx.buffer(reserve=2 * data.nbytes, dynamic=True)
            self._vao = self._make_vao()
        self._vbo.write(data.tobytes())
        self._vao.render(mode=moderngl.TRIANGLES, vertices=data.shape[0])

    def _count_fps(self):
        self._fps_frames += 1
        now = time.perf_counter()
        if now - self._fps_t0 >= 1.0:
            fps = self._fps_frames / (now - self._fps_t0)
            self.window.set_caption(f"{self._caption_base} — {fps:.0f} fps")
            self._fps_frames = 0
            self._fps_t0 = now
```

File 10 — forge/demo.py

```python
"""python -m forge.demo — the walking-skeleton acceptance demo.

EXPECTED (plain words, for the project owner):
A black window titled "Homeworld: A Good Basis — forge v0.1.0 — 60 fps".
A glowing cyan grid plane seen at an angle. At the grid's center, three
small arrows (red = X, green = Y, blue = Z) mark the origin. One larger
WHITE ARROW sweeps slowly around the origin like a clock hand tilted in
3D — this is the first vector, drawn live from numpy. A red dashed line
crosses the scene. A soft green wire sphere sits to one side. The camera
orbits slowly by itself and gently bobs up and down. Lines are bright in
the middle with soft edges; where lines cross, they get brighter.
ESC closes the window. F12 saves a screenshot into screenshots/ and
prints the path in the console. Any crash writes crashlog.txt.
"""

import json
import math
import os
import sys
import time
import traceback

import numpy as np

from .app import Forge
from .vobjects import Arrow, DashedLine, Grid, WireSphere


def _load_settings():
    if os.path.exists("settings.json"):
        with open("settings.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def main():
    settings = _load_settings()
    forge = Forge(settings)
    print("forge demo running. ESC = quit, F12 = screenshot.")

    # The reference plane: span of e1=(1,0,0) and e3=(0,0,1) through origin.
    grid = Grid(center=(0, 0, 0), u=(1, 0, 0), v=(0, 0, 1), n=10, spacing=2.0)
    forge.add(grid)

    # Origin axes: x red, y green, z blue.
    forge.add(Arrow((0, 0, 0), (3, 0, 0), head_size=0.6,
                    color=(1.0, 0.25, 0.25, 1.0)))
    forge.add(Arrow((0, 0, 0), (0, 3, 0), head_size=0.6,
                    color=(0.25, 1.0, 0.35, 1.0)))
    forge.add(Arrow((0, 0, 0), (0, 0, 3), head_size=0.6,
                    color=(0.35, 0.55, 1.0, 1.0)))

    # THE first vector from the origin — animated every frame.
    first_vector = Arrow((0, 0, 0), (8, 4, 0), head_size=1.1,
                         color=(1.0, 1.0, 1.0, 1.0), glow=1.2)
    forge.add(first_vector)

    forge.add(DashedLine((-9, 0.5, -9), (9, 3.5, 9), dash=0.7,
                         color=(1.0, 0.35, 0.30, 1.0)))
    forge.add(WireSphere((-7, 2.0, 5), 2.0,
                         color=(0.35, 1.0, 0.55, 0.8)))

    start = time.perf_counter()
    pulse_count = [0]

    def tick(dt):
        # 10 Hz logic pulse. Nothing to simulate yet — fleet comes later.
        pulse_count[0] += 1

    def frame(alpha):
        t = time.perf_counter() - start
        # Self-orbiting camera with a gentle vertical bob.
        forge.camera.yaw = 0.8 + 0.12 * t
        forge.camera.pitch = 0.35 + 0.10 * math.sin(0.30 * t)
        # The first vector sweeps around the origin, tilting as it goes.
        end = np.array([
            8.0 * math.cos(0.40 * t),
            4.0 + 1.5 * math.sin(0.70 * t),
            8.0 * math.sin(0.40 * t),
        ])
        first_vector.set_data((0.0, 0.0, 0.0), end, head_size=1.1)

    forge.run(tick, frame)


def run_with_crashlog(fn):
    try:
        fn()
    except Exception:
        text = traceback.format_exc()
        with open("crashlog.txt", "w", encoding="utf-8") as f:
            f.write("forge.demo crash\n")
            f.write(text)
        print("Something broke — please copy crashlog.txt to the team.")
        print(text)
        sys.exit(1)


if __name__ == "__main__":
    run_with_crashlog(main)
```

📋 HOW TO RUN (your steps, in order)

    Send to DeepSeek: paste each of the 10 files above with its exact path, tell it to save verbatim, update COMMENTARIES.md, and commit with the message: NT steps 1-2: forge walking skeleton (window, camera, ribbons, grid, first arrow).
    Install Python (once): from python.org, Python 3.12 for Windows — during install, tick the checkbox "Add python.exe to PATH".
    Install the libraries (once): open the folder, click the address bar, type cmd, press Enter, then run: pip install -r requirements.txt
    Run: double-click run.bat.

👀 WHAT YOU SHOULD SEE

A black window. A glowing cyan grid floor seen at an angle. At its center, three small arrows (red/green/blue) marking the origin. One large white arrow sweeping slowly around the origin like a tilted clock hand — that's the first vector of the project, drawn live from numpy 60 times a second. A red dashed line, a soft green wire sphere. The camera orbits by itself and gently bobs. Where lines cross, they get brighter (that's the additive glow working). Window title shows the fps (should say ~60). ESC closes; F12 saves a screenshot.

📝 WHAT TO REPORT BACK

Just tell me one of: (a) "I saw exactly that" 🎉, (b) "I saw something different: ..." (describe in plain words), or (c) paste crashlog.txt / the console error. That's a full bug report — the code was built for your eyes.

The next packages after your confirmation: bloom (the real Homeworld glow), then text + the remaining primitives, then helm — and then three ships flying combination orders. 🚀❤️
