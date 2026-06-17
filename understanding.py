"""understanding.py -- Brief #11d: Understanding Mode, fog-and-glass flight.

The player is a spaceship flying along a line of GLASS SIGNS (explanation panels:
mathematician -> physicist -> biologist -> engineer), baked offline as transparent
LaTeX PNGs (deu/bake_corridor.py). Gaze is fixed FORWARD; you fly forward/reverse
(=zoom) and pan up/down/left/right.

PHYSICAL MODEL:
  * Each sign is real glass. Its transparency is a FIXED, baked property -- it does
    NOT change as you approach (no observer effect). Signs are drawn at full alpha;
    the PNG's own alpha is the only transparency.
  * What changes with distance is the AIR: FOG (color = FOG_COLOR) sits between
    signs. Farther signs are seen through MORE fog (washed) and are OUT OF FOCUS
    (blurrier). Flying closer = less fog between you and that sign = it comes into
    focus and its true clarity, while its own glassiness never changes.
  * Size grows with nearness (perspective). No snap-to-fit; park at any distance and
    pan around a sign bigger than the screen. A corner minimap shows the roam.

Input (UNCHANGED): mouse wheel = depth(=zoom), mouse + right stick = pan,
CTRL = engineer unlock, ESC / back-out (focus < -0.6) = exit.

Brief #J1B: the T.16000M back-center button is ADDITIVE to CTRL. On Nir's unit it
reports as pygame button index 1 (CONFIRMED 2026-06-17 by an on-screen probe;
the brief's "index 3" guess was wrong for this hardware). CTRL here is a HELD reveal
(engineer comes into focus WHILE held, softens on release) -- not a toggle -- so the
joystick button is OR'd into the same held boolean, NOT edge-gated.

Fallback: if a baked PNG is missing for a layer, render robot.explain[layer] via
render.render_rich() (old behavior), so the mode never crashes on an unbaked level.

Scope: this is the ONLY file changed. No app.py / level_parser / baker / manifest edits."""

import os
import math
import pygame
from OpenGL.GL import *
import render

LAYER_KEYS  = ["mathematician", "physicist", "biologist", "engineer"]
LAYER_TITLE = {"mathematician":"MATHEMATICIAN", "physicist":"PHYSICIST",
               "biologist":"BIOLOGIST", "engineer":"ENGINEER"}

# Brief #J1B: pilot-joystick button index for the engineer reveal (HELD, like
# CTRL). Confirmed by probe on Nir's T.16000M: the back-center button = index 1.
PILOT_ENGINEER_BTN = 1

BG_COLOR   = (0.04, 0.05, 0.07)   # near-black world replacement
PAN_SPEED   = 1.0                  # mouse px -> pan px
STICK_SPEED = 1200.0               # right-stick units -> pan px/s (big sheets)
DEPTH_SPEED_WHEEL = 0.18           # focus units per wheel click (small = silky)
BASE_FONTSIZE = 22

# --- Continuous perspective (size) and focus (blur) from distance d ------------
# distance d = |focus - layer_index|. Size and blur are smooth functions of d.
# Opacity is NOT a function of d -- glass keeps its own baked alpha.
CLOSEUP_FILL = 1.30   # at d=0 the sign fills this fraction of screen WIDTH (>1 = roam)
FAR_FILL     = 0.42   # shrinks toward this with distance (perspective preview)
SIZE_FALLOFF = 0.85   # perspective decay rate (Gaussian sigma-ish)
PEAK_BLUR    = 0.0    # in focus at d=0
BLUR_PER_D   = 4.0    # px blur added per unit distance (out of focus = far)

# --- FOG (this, not opacity changes, is what washes out distance) --------------
# Glass signs keep their own baked alpha (drawn at full alpha). Distance is conveyed
# by a fog veil laid in FRONT of farther signs. fog_strength rises with distance.
# BLACK fog (matches dark bg) -> far signs dissolve into depth.
# For WHITE fog (dreamy mist) set FOG_COLOR = (0.90, 0.92, 0.95).
FOG_COLOR    = (0.04, 0.05, 0.07)
FOG_PER_D    = 0.55   # fog opacity added per unit distance
FOG_MAX      = 0.92   # never fully opaque -> deep structure still ghosts through

# --- Pre-blur ladder (built once per open; ZERO per-frame blur cost) ----------
BLUR_RUNGS = 10       # crisp + 9 progressively blurred -> smooth continuous dissolve
BLUR_STEP  = 1.2      # px Gaussian per rung -> max ~10.8px
MAX_DRAW_BLUR = (BLUR_RUNGS - 1) * BLUR_STEP

# --- Source cap: allow bigger-than-screen panels (we roam them; don't compress) -
PANEL_MAX_W = 4096    # within typical GL_MAX_TEXTURE_SIZE; raise if your GPU allows

# --- Minimap -------------------------------------------------------------------
MINIMAP_W      = 200
MINIMAP_MARGIN = 18
MINIMAP_BG     = (0.10, 0.12, 0.16, 0.72)
MINIMAP_FRAME  = (0.55, 0.70, 0.95, 0.95)


class UnderstandingMode:
    def __init__(self):
        self.active = False
        self.robot  = None
        self.focus  = 0.0          # continuous spaceship position 0..3
        self.target = 0.0
        self.pan_x  = 0.0          # pan in screen px applied to the focused sign
        self.pan_y  = 0.0
        self.ctrl   = False
        self._panels = {}          # { key: [ (tid,w,h) rung0_sharp, rung1, ... ] }
        self._all_tids = []

    # ---- texture building (load once per open) ------------------------------
    def _surface_to_texture(self, surf):
        w, h = surf.get_width(), surf.get_height()
        data = pygame.image.tostring(surf, "RGBA", True)  # flip -> GL row order
        tid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tid)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, data)
        glBindTexture(GL_TEXTURE_2D, 0)
        self._all_tids.append(tid)
        return (tid, w, h)

    def _load_panel_ladder(self, layer):
        d = getattr(self.robot, "understanding_dir", "") or ""
        num = getattr(self.robot, "number", None)
        if not d or num is None:
            # Brief #A — loud fallback (a): no baked folder / no robot number.
            print("UNDERSTANDING: no baked PNG for robot=%r layer=%r "
                  "(understanding_dir=%r) -> live-text fallback"
                  % (num, layer, d))
            return None
        path = os.path.join(d, f"robot{num}_{layer}.png")
        if not os.path.isfile(path):
            # Brief #A — loud fallback (b): expected baked PNG is missing.
            print("UNDERSTANDING: baked PNG missing: %s -> live-text fallback"
                  % path)
            return None
        try:
            surf = pygame.image.load(path).convert_alpha()
        except Exception:
            return None
        if surf.get_width() > PANEL_MAX_W:
            s = PANEL_MAX_W / surf.get_width()
            surf = pygame.transform.smoothscale(
                surf, (PANEL_MAX_W, max(1, int(surf.get_height() * s)))
            ).convert_alpha()
        rungs = [self._surface_to_texture(surf)]                 # rung 0 = crisp
        for r in range(1, BLUR_RUNGS):
            rungs.append(self._surface_to_texture(
                render.blur_surface(surf, r * BLUR_STEP)))         # high-quality PIL
        return rungs

    def _rung_for_blur(self, blur_px):
        idx = int(round(min(MAX_DRAW_BLUR, max(0.0, blur_px)) / BLUR_STEP))
        return max(0, min(BLUR_RUNGS - 1, idx))

    # ---- continuous appearance (size + focus + fog; NO opacity change) -------
    def _size_fill(self, d):
        g = math.exp(-(d * d) / (2.0 * SIZE_FALLOFF * SIZE_FALLOFF))  # 1 at d=0
        return FAR_FILL + (CLOSEUP_FILL - FAR_FILL) * g

    def _blur_px(self, d):
        return PEAK_BLUR + BLUR_PER_D * d

    def _fog_strength(self, d):
        return max(0.0, min(FOG_MAX, FOG_PER_D * d))

    # ---- entry / exit --------------------------------------------------------
    def open(self, robot_data):
        if robot_data is None:
            return
        self.active = True
        self.robot  = robot_data
        self.focus = self.target = 0.0
        self.pan_x = self.pan_y = 0.0
        self._panels = {}
        self._all_tids = []
        for key in LAYER_KEYS:
            self._panels[key] = self._load_panel_ladder(key)
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        pygame.mouse.get_rel()       # discard initial jump

    def close(self):
        self.active = False
        self.robot  = None
        if self._all_tids:
            try:
                glDeleteTextures(self._all_tids)
            except Exception:
                for t in self._all_tids:
                    glDeleteTextures(int(t))
        self._panels = {}
        self._all_tids = []
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

    # ---- per-frame input -----------------------------------------------------
    def handle_input(self, events, keys, gamepads, dt):
        if not self.active:
            return

        # Engineer reveal: keyboard CTRL OR T.16000M back-center button
        # (PILOT_ENGINEER_BTN = index 1, confirmed by probe). HELD, not
        # edge-gated -- the engineer sign sharpens WHILE held and softens on
        # release. The joystick button is OR'd in exactly like the two CTRL
        # keys are. Crash-safe against no controller / no pilot device /
        # too-few buttons.
        mods = pygame.key.get_mods()
        joy_engineer = False
        if gamepads is not None:
            pj = getattr(gamepads, "pilot_joy", None)
            if pj is not None and pj.get_numbuttons() > PILOT_ENGINEER_BTN:
                try:
                    joy_engineer = bool(pj.get_button(PILOT_ENGINEER_BTN))
                except Exception:
                    joy_engineer = False
        self.ctrl = (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
                     or bool(mods & pygame.KMOD_CTRL)
                     or joy_engineer)
        if self.ctrl:
            self.target = float(len(LAYER_KEYS) - 1)   # fly to engineer

        for ev in events:
            if ev.type == pygame.MOUSEWHEEL:
                self.target += ev.y * DEPTH_SPEED_WHEEL
        if self.target < -0.6:        # back out past the front -> exit
            self.close()
            return
        self.target = max(0.0, min(float(len(LAYER_KEYS) - 1), self.target))

        # smooth continuous glide of the spaceship toward target depth
        self.focus += (self.target - self.focus) * min(1.0, dt * 8.0)

        # PAN (mouse + right stick), applied to the focused sign
        dx, dy = pygame.mouse.get_rel()
        self.pan_x -= dx * PAN_SPEED
        self.pan_y -= dy * PAN_SPEED
        if gamepads is not None:
            rx, ry = gamepads.manipulator_right_stick()
            self.pan_x -= rx * STICK_SPEED * dt
            self.pan_y -= ry * STICK_SPEED * dt

        if keys[pygame.K_ESCAPE]:
            self.close()

    # ---- helpers -------------------------------------------------------------
    def _focused_layer(self):
        return int(round(max(0.0, min(float(len(LAYER_KEYS) - 1), self.focus))))

    def _draw_dims(self, rungs, fill, win_w):
        _, sw, sh = rungs[0]
        draw_w = fill * win_w
        return draw_w, sh * (draw_w / sw)

    def _clamp_pan(self, draw_w, draw_h, win_w, win_h):
        over_x = max(0.0, (draw_w - win_w) * 0.5)
        over_y = max(0.0, (draw_h - win_h) * 0.5)
        self.pan_x = max(-over_x, min(over_x, self.pan_x))
        self.pan_y = max(-over_y, min(over_y, self.pan_y))

    def _fog_quad(self, w, h, strength):
        if strength <= 0.003:
            return
        glDisable(GL_TEXTURE_2D)
        glColor4f(FOG_COLOR[0], FOG_COLOR[1], FOG_COLOR[2], strength)
        glBegin(GL_QUADS)
        glVertex2f(0, 0); glVertex2f(w, 0); glVertex2f(w, h); glVertex2f(0, h)
        glEnd()

    # ---- draw (between begin_2d/end_2d in app loop) -------------------------
    def draw(self, cache, win_size):
        if not self.active or self.robot is None:
            return
        w, h = win_size

        # opaque background replaces the world
        glDisable(GL_TEXTURE_2D)
        glColor4f(*BG_COLOR, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(0, 0); glVertex2f(w, 0); glVertex2f(w, h); glVertex2f(0, h)
        glEnd()

        focused_i = self._focused_layer()

        # clamp pan to the focused sign's drawn size (bounded roam)
        foc_rungs = self._panels.get(LAYER_KEYS[focused_i])
        foc_draw_w = foc_draw_h = 0.0
        if foc_rungs:
            fill0 = self._size_fill(abs(self.focus - focused_i))
            foc_draw_w, foc_draw_h = self._draw_dims(foc_rungs, fill0, w)
            self._clamp_pan(foc_draw_w, foc_draw_h, w, h)

        # FAR -> NEAR. Before each sign, lay the fog that sits in FRONT of its depth,
        # then draw the GLASS sign at full alpha (its own baked transparency only).
        order = sorted(range(len(LAYER_KEYS)),
                       key=lambda i: abs(self.focus - i), reverse=True)
        for i in order:
            d = abs(self.focus - i)
            key = LAYER_KEYS[i]
            rungs = self._panels.get(key)

            # fog veil for this depth (more fog = farther)
            self._fog_quad(w, h, self._fog_strength(d))

            blur = self._blur_px(d)
            if key == "engineer" and not self.ctrl:
                blur = max(blur, 7.0)               # engineer locked-soft until CTRL
                title_suffix = "   [hold CTRL]"
            else:
                title_suffix = ""
            title = LAYER_TITLE[key] + title_suffix

            if rungs:
                fill = self._size_fill(d)
                draw_w, draw_h = self._draw_dims(rungs, fill, w)
                pan_x = self.pan_x if i == focused_i else 0.0
                pan_y = self.pan_y if i == focused_i else 0.0
                px = (w - draw_w) * 0.5 + pan_x
                py = (h - draw_h) * 0.5 + pan_y
                scale = draw_w / rungs[0][1]
                tex = rungs[self._rung_for_blur(blur)]
                # GLASS: full alpha; transparency is the PNG's own baked alpha
                render.draw_texture(tex, px, py, scale=scale, alpha=1.0)
                # title floats just above the sign, scaled with it
                tfs = max(10, int(BASE_FONTSIZE * min(1.0, fill / CLOSEUP_FILL)))
                render.render_rich(cache, title, px + 8, py + draw_h + 6,
                                   color=(0.55, 0.70, 0.95), fontsize=tfs)
            else:
                # FALLBACK: PNG missing -> old live-text behavior (never crashes)
                fs = max(10, int(BASE_FONTSIZE * min(1.0, self._size_fill(d) / CLOSEUP_FILL)))
                text = self.robot.explain.get(key, "")
                px = w * 0.08 + (self.pan_x if i == focused_i else 0.0)
                py = h * 0.18 + (self.pan_y if i == focused_i else 0.0)
                render.render_rich(cache, title, px, py - fs * 1.6,
                                   color=(0.55, 0.70, 0.95), fontsize=int(fs * 0.8))
                render.render_rich(cache, text, px, py,
                                   color=(0.95, 0.96, 0.98), fontsize=fs, blur=blur)

        # ---- minimap: only when the focused sign overflows the screen ---------
        if foc_rungs and (foc_draw_w > w or foc_draw_h > h):
            self._draw_minimap(foc_rungs, foc_draw_w, foc_draw_h, w, h)

    # ---- minimap (fully clamped inside the thumbnail) -----------------------
    def _draw_minimap(self, rungs, draw_w, draw_h, w, h):
        _, sw, sh = rungs[0]
        mm_w = MINIMAP_W
        mm_h = mm_w * (sh / sw)
        mx = w - mm_w - MINIMAP_MARGIN
        my = h - mm_h - MINIMAP_MARGIN

        # backing panel
        glDisable(GL_TEXTURE_2D)
        glColor4f(*MINIMAP_BG)
        glBegin(GL_QUADS)
        glVertex2f(mx - 4, my - 4); glVertex2f(mx + mm_w + 4, my - 4)
        glVertex2f(mx + mm_w + 4, my + mm_h + 4); glVertex2f(mx - 4, my + mm_h + 4)
        glEnd()

        # thumbnail = blurriest rung (cheap, already loaded)
        render.draw_texture(rungs[-1], mx, my, scale=mm_w / sw, alpha=0.95)

        # view rectangle: fraction of the full sign currently on screen.
        sign_left = (w - draw_w) * 0.5 + self.pan_x
        sign_top  = (h - draw_h) * 0.5 + self.pan_y
        vx = (-sign_left) / draw_w
        vy = (-sign_top) / draw_h
        vw = w / draw_w
        vh = h / draw_h
        # clamp the rectangle fully inside [0,1]^2 of the thumbnail
        x0 = max(0.0, min(1.0, vx))
        y0 = max(0.0, min(1.0, vy))
        x1 = max(0.0, min(1.0, vx + vw))
        y1 = max(0.0, min(1.0, vy + vh))
        rx = mx + x0 * mm_w
        ry = my + y0 * mm_h
        rw = (x1 - x0) * mm_w
        rh = (y1 - y0) * mm_h

        glColor4f(*MINIMAP_FRAME)
        glBegin(GL_LINE_LOOP)
        glVertex2f(rx, ry); glVertex2f(rx + rw, ry)
        glVertex2f(rx + rw, ry + rh); glVertex2f(rx, ry + rh)
        glEnd()
