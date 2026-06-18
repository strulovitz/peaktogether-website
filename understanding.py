"""understanding.py -- Brief #U1: Understanding Mode, fog-and-glass flight.

ROAD-SIGN PHYSICS (Brief #U1 rewrite):
  The player is a CAR driving FORWARD down a foggy road past a fixed line of
  GLASS SIGNS (explanation panels: mathematician -> physicist -> biologist ->
  engineer), baked offline as transparent PNGs. Gaze is fixed STRICTLY FORWARD.
  The car never turns around. You drive forward/back (mouse wheel) and pan to
  read a sign bigger than the screen.

  SIGNED DISTANCE is the heart of the model. Let f = the car's continuous
  position along the road, and i = a sign's integer index (0 = mathematician /
  front, increasing into depth). For each sign:

        s_i = i - f

      * s_i > 0  -> sign is AHEAD  -> visible; size/blur/fog depend on s_i.
      * s_i = 0  -> car is AT the sign (largest; overflows; pan to read).
      * s_i < 0  -> sign is BEHIND -> CULLED. Drawn not at all, ever. (This one
                    rule kills the old "conveyor belt": a passed sign vanishes
                    instead of reversing and drifting away in front of you.)

  ENTRY: f starts at ENTRY_FOCUS = -1.0, so sign 0 has s_0 = 1 and sits at the
  "fits-on-screen with a tiny margin" framing (FITS_S = 1). The first forward
  wheel click raises f toward 0, smoothly growing sign 0 past the edges (then
  you pan). No snap, no jump.

  REVERSE & EXIT: reverse falls out of the signed math for free. Backing up in
  the middle just reveals the previous (harder) sign ahead -- it never exits.
  Exit happens ONLY by reversing PAST sign 0 by 1/3 of a spacing: when
  f < -EXIT_THRESHOLD (= -1/3), call close(). While f is in (-1/3, 0) sign 0 is
  still drawn (s_0 = -f, a small positive -> visibly shrinking) so the player
  SEES it shrink before the mode closes.

PHYSICAL MODEL (unchanged in spirit):
  * Each sign is real glass. Transparency is a FIXED baked property -- it does
    NOT change with approach. Signs are drawn at full alpha; the PNG's own alpha
    is the only transparency.
  * What changes with distance is the AIR: FOG (color = FOG_COLOR) sits between
    you and a sign, and a sign is blurrier the farther ahead it is. Darkening of
    a far sign is done by the FOG QUAD in front of it (draw_texture always draws
    at glColor 1,1,1 -- the only honest way to darken here is fog), NOT by
    dimming the texture.

Input: mouse wheel = depth (drive forward/back). mouse + right stick = pan.
CTRL / T.16000M back-center button (index 1) = engineer reveal (HELD).
ESC = INERT inside Understanding Mode (Brief #U1). app.py already refuses to
quit the game while umode.active, so deleting the old ESC->close() here makes
ESC fully inert in this mode while still quitting the game everywhere else.

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

PILOT_ENGINEER_BTN = 1

BG_COLOR   = (0.04, 0.05, 0.07)
PAN_SPEED   = 1.0
STICK_SPEED = 1200.0
DEPTH_SPEED_WHEEL = 0.18
BASE_FONTSIZE = 22

# === Brief #U1: SIGNED-DISTANCE ROAD-SIGN MODEL ===============================
# f = car position along the road; per sign s_i = i - f (see module docstring).
#
# ENTRY_FOCUS: where the car starts. -1.0 puts sign 0 at s=1 (the "fits"
#   framing) so it appears whole-with-a-tiny-margin on entry, NOT overflowing.
ENTRY_FOCUS    = -1.0
# FITS_S: the signed distance at which a sign "fits on screen in all its glory".
#   Sign-revealing math is anchored here. Keep == 1.0 (one full spacing).
FITS_S         = 1.0
# EXIT_THRESHOLD: reverse this far (index units = spacings) PAST sign 0 to exit.
#   1/3 of a spacing, per Brief #U1 S3.7.
EXIT_THRESHOLD = 1.0 / 3.0

# --- Perspective SIZE as a MONOTONIC function of signed distance s (s >= 0) ----
# Targets (Brief #U1 S5):
#   s -> 0   : sign grows past the screen so the player must PAN (liked).
#   s == 1   : whole sign fits with a tiny L/R margin  -> fill ~= FITS_FILL.
#   s  > 1   : shrinks with distance toward FAR_FILL (perspective preview).
# We use a true-ish perspective law fill = NEAR_K / (s + NEAR_K), clamped to a
# far floor. NEAR_K is chosen so that fill(1) == FITS_FILL exactly:
#       FITS_FILL = NEAR_K / (1 + NEAR_K)  ->  NEAR_K = FITS_FILL / (1 - FITS_FILL)
# At s=0 this gives fill=1.0 (full screen width); panning pushes a touch beyond
# via the +PAN_OVERFILL bump so s near 0 clearly overflows. Monotonic decreasing
# in s, so a passed-but-not-yet-culled sign only ever shrinks -- never a bell.
FITS_FILL     = 0.90
FAR_FILL      = 0.42
NEAR_K        = FITS_FILL / (1.0 - FITS_FILL)
PAN_OVERFILL  = 0.55

# --- BLUR as a function of signed distance s (farther ahead = more veiled) -----
# Uses the EXISTING pre-baked blur rungs (no live blur). Tuned so:
#   s <= ~0.4 : crisp (rung 0-ish).
#   s == 1    : readable-as-current, lightly softened.
#   s == 2    : clearly veiled (next sign behind doesn't compete).
BLUR_PER_S   = 4.0

# --- FOG: darkens/veils farther signs (the only honest darkening here) ---------
# Glass keeps its baked alpha (drawn full alpha). A fog quad laid IN FRONT of a
# farther sign darkens & washes it. fog_strength rises with s.
FOG_COLOR    = (0.04, 0.05, 0.07)
FOG_PER_S    = 0.34
FOG_MAX      = 0.92

# --- Pre-blur ladder (built once per open; ZERO per-frame blur cost) ----------
BLUR_RUNGS = 10
BLUR_STEP  = 1.2
MAX_DRAW_BLUR = (BLUR_RUNGS - 1) * BLUR_STEP

# --- Source cap: allow bigger-than-screen panels (we roam them; don't compress) -
PANEL_MAX_W = 4096

# --- Minimap -------------------------------------------------------------------
MINIMAP_W      = 200
MINIMAP_MARGIN = 18
MINIMAP_BG     = (0.10, 0.12, 0.16, 0.72)
MINIMAP_FRAME  = (0.55, 0.70, 0.95, 0.95)


class UnderstandingMode:
    def __init__(self):
        self.active = False
        self.robot  = None
        self.focus  = ENTRY_FOCUS
        self.target = ENTRY_FOCUS
        self.pan_x  = 0.0
        self.pan_y  = 0.0
        self.ctrl   = False
        self._nearest_i = None
        self._panels = {}
        self._all_tids = []

    # ---- texture building (load once per open) ------------------------------
    def _surface_to_texture(self, surf):
        w, h = surf.get_width(), surf.get_height()
        data = pygame.image.tostring(surf, "RGBA", True)
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
            print("UNDERSTANDING: no baked PNG for robot=%r layer=%r "
                  "(understanding_dir=%r) -> live-text fallback"
                  % (num, layer, d))
            return None
        path = os.path.join(d, f"robot{num}_{layer}.png")
        if not os.path.isfile(path):
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
        rungs = [self._surface_to_texture(surf)]
        for r in range(1, BLUR_RUNGS):
            rungs.append(self._surface_to_texture(
                render.blur_surface(surf, r * BLUR_STEP)))
        return rungs

    def _rung_for_blur(self, blur_px):
        idx = int(round(min(MAX_DRAW_BLUR, max(0.0, blur_px)) / BLUR_STEP))
        return max(0, min(BLUR_RUNGS - 1, idx))

    # ---- continuous appearance from SIGNED distance s (>= 0 only) ------------
    def _size_fill(self, s):
        """Monotonic-decreasing perspective fill. fill(0) ~= 1.0 + PAN_OVERFILL
        (overflow -> pan), fill(1) == FITS_FILL, decays toward FAR_FILL far away."""
        s = max(0.0, s)
        fill = NEAR_K / (s + NEAR_K)
        fill += PAN_OVERFILL * math.exp(-s * s / 0.5)
        return max(FAR_FILL, fill)

    def _blur_px(self, s):
        return BLUR_PER_S * max(0.0, s)

    def _fog_strength(self, s):
        return max(0.0, min(FOG_MAX, FOG_PER_S * max(0.0, s)))

    # ---- entry / exit --------------------------------------------------------
    def open(self, robot_data):
        if robot_data is None:
            return
        self.active = True
        self.robot  = robot_data
        self.focus = self.target = ENTRY_FOCUS
        self.pan_x = self.pan_y = 0.0
        self._nearest_i = None
        self._panels = {}
        self._all_tids = []
        for key in LAYER_KEYS:
            self._panels[key] = self._load_panel_ladder(key)
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        pygame.mouse.get_rel()

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
        self._nearest_i = None
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

    # ---- per-frame input -----------------------------------------------------
    def handle_input(self, events, keys, gamepads, dt):
        if not self.active:
            return

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
            self.target = float(len(LAYER_KEYS) - 1)

        for ev in events:
            if ev.type == pygame.MOUSEWHEEL:
                self.target += ev.y * DEPTH_SPEED_WHEEL

        if self.target < -EXIT_THRESHOLD:
            self.close()
            return
        self.target = max(-EXIT_THRESHOLD,
                          min(float(len(LAYER_KEYS) - 1), self.target))

        self.focus += (self.target - self.focus) * min(1.0, dt * 8.0)

        if self.focus < -EXIT_THRESHOLD:
            self.close()
            return

        nearest = self._nearest_ahead_index()
        if nearest != self._nearest_i:
            self.pan_x = self.pan_y = 0.0
            self._nearest_i = nearest

        dx, dy = pygame.mouse.get_rel()
        self.pan_x -= dx * PAN_SPEED
        self.pan_y -= dy * PAN_SPEED
        if gamepads is not None:
            rx, ry = gamepads.manipulator_right_stick()
            self.pan_x -= rx * STICK_SPEED * dt
            self.pan_y -= ry * STICK_SPEED * dt

    # ---- helpers -------------------------------------------------------------
    def _nearest_ahead_index(self):
        """Index of the sign the player is currently READING: the smallest s_i
        with s_i >= 0 (nearest sign still ahead-or-at the car)."""
        best_i = None
        best_s = None
        for i in range(len(LAYER_KEYS)):
            s = i - self.focus
            if s >= -1e-6:
                if best_s is None or s < best_s:
                    best_s = s
                    best_i = i
        return best_i

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

        glDisable(GL_TEXTURE_2D)
        glColor4f(*BG_COLOR, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(0, 0); glVertex2f(w, 0); glVertex2f(w, h); glVertex2f(0, h)
        glEnd()

        nearest_i = self._nearest_ahead_index()

        foc_draw_w = foc_draw_h = 0.0
        foc_rungs = None
        if nearest_i is not None:
            foc_rungs = self._panels.get(LAYER_KEYS[nearest_i])
            if foc_rungs:
                s_near = max(0.0, nearest_i - self.focus)
                fill0 = self._size_fill(s_near)
                foc_draw_w, foc_draw_h = self._draw_dims(foc_rungs, fill0, w)
                self._clamp_pan(foc_draw_w, foc_draw_h, w, h)

        visible = []
        for i in range(len(LAYER_KEYS)):
            s = i - self.focus
            if s >= -1e-6:
                visible.append((i, max(0.0, s)))

        visible.sort(key=lambda t: t[1], reverse=True)
        for i, s in visible:
            key = LAYER_KEYS[i]
            rungs = self._panels.get(key)

            self._fog_quad(w, h, self._fog_strength(s))

            blur = self._blur_px(s)
            if key == "engineer" and not self.ctrl:
                blur = max(blur, 7.0)
                title_suffix = "   [hold CTRL]"
            else:
                title_suffix = ""
            title = LAYER_TITLE[key] + title_suffix

            if rungs:
                fill = self._size_fill(s)
                draw_w, draw_h = self._draw_dims(rungs, fill, w)
                pan_x = self.pan_x if i == nearest_i else 0.0
                pan_y = self.pan_y if i == nearest_i else 0.0
                px = (w - draw_w) * 0.5 + pan_x
                py = (h - draw_h) * 0.5 + pan_y
                scale = draw_w / rungs[0][1]
                tex = rungs[self._rung_for_blur(blur)]
                render.draw_texture(tex, px, py, scale=scale, alpha=1.0)
                tfs = max(10, int(BASE_FONTSIZE * min(1.0, fill / (FITS_FILL + PAN_OVERFILL))))
                render.render_rich(cache, title, px + 8, py + draw_h + 6,
                                   color=(0.55, 0.70, 0.95), fontsize=tfs)
            else:
                fs = max(10, int(BASE_FONTSIZE * min(1.0, self._size_fill(s) / (FITS_FILL + PAN_OVERFILL))))
                text = self.robot.explain.get(key, "")
                px = w * 0.08 + (self.pan_x if i == nearest_i else 0.0)
                py = h * 0.18 + (self.pan_y if i == nearest_i else 0.0)
                render.render_rich(cache, title, px, py - fs * 1.6,
                                   color=(0.55, 0.70, 0.95), fontsize=int(fs * 0.8))
                render.render_rich(cache, text, px, py,
                                   color=(0.95, 0.96, 0.98), fontsize=fs, blur=blur)

        if foc_rungs and (foc_draw_w > w or foc_draw_h > h):
            self._draw_minimap(foc_rungs, foc_draw_w, foc_draw_h, w, h)

    # ---- minimap (fully clamped inside the thumbnail) -----------------------
    def _draw_minimap(self, rungs, draw_w, draw_h, w, h):
        _, sw, sh = rungs[0]
        mm_w = MINIMAP_W
        mm_h = mm_w * (sh / sw)
        mx = w - mm_w - MINIMAP_MARGIN
        my = h - mm_h - MINIMAP_MARGIN

        glDisable(GL_TEXTURE_2D)
        glColor4f(*MINIMAP_BG)
        glBegin(GL_QUADS)
        glVertex2f(mx - 4, my - 4); glVertex2f(mx + mm_w + 4, my - 4)
        glVertex2f(mx + mm_w + 4, my + mm_h + 4); glVertex2f(mx - 4, my + mm_h + 4)
        glEnd()

        render.draw_texture(rungs[-1], mx, my, scale=mm_w / sw, alpha=0.95)

        sign_left = (w - draw_w) * 0.5 + self.pan_x
        sign_top  = (h - draw_h) * 0.5 + self.pan_y
        vx = (-sign_left) / draw_w
        vy = (-sign_top) / draw_h
        vw = w / draw_w
        vh = h / draw_h
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
