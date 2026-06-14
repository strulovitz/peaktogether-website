"""understanding.py -- Brief #11: Understanding Mode.
Four depth-stacked explanation panels (mathematician/physicist/biologist/engineer).
Mouse wheel = depth, mouse motion = pan, CTRL = engineer unlock, ESC = exit."""

import pygame
from OpenGL.GL import *
import render

LAYER_KEYS  = ["mathematician", "physicist", "biologist", "engineer"]
LAYER_TITLE = {"mathematician":"MATHEMATICIAN", "physicist":"PHYSICIST",
               "biologist":"BIOLOGIST", "engineer":"ENGINEER"}

BG_COLOR     = (0.04, 0.05, 0.07)   # near-black; text is light (render_rich default)
PAN_SPEED    = 1.0                  # mouse px -> pan px
STICK_SPEED  = 600.0                # right-stick units -> pan px per second
DEPTH_SPEED_WHEEL = 1.0             # focus units per wheel click
BASE_FONTSIZE = 22

class UnderstandingMode:
    def __init__(self):
        self.active   = False
        self.robot    = None        # RobotData of the subject
        self.focus    = 0.0         # 0..3, which layer is sharp (float, animates)
        self.target   = 0.0         # integer-ish target focus the wheel/trigger sets
        self.pan_x    = 0.0
        self.pan_y    = 0.0
        self.ctrl     = False       # engineer-unlock held this frame

    # ---- entry / exit ----
    def open(self, robot_data):
        if robot_data is None:
            return
        self.active = True
        self.robot  = robot_data
        self.focus  = 0.0
        self.target = 0.0
        self.pan_x  = 0.0
        self.pan_y  = 0.0
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        pygame.mouse.get_rel()        # discard initial jump

    def close(self):
        self.active = False
        self.robot  = None
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

    # ---- per-frame input (called from app loop) ----
    def handle_input(self, events, keys, gamepads, dt):
        if not self.active:
            return
        # CTRL = engineer unlock (polled — keys + mods for robustness)
        # Holding CTRL also jumps focus straight to the engineer panel.
        mods = pygame.key.get_mods()
        self.ctrl = (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
                     or bool(mods & pygame.KMOD_CTRL))
        if self.ctrl:
            self.target = float(len(LAYER_KEYS) - 1)  # snap to engineer

        # DEPTH: mouse wheel (events)
        for ev in events:
            if ev.type == pygame.MOUSEWHEEL:
                self.target += ev.y * DEPTH_SPEED_WHEEL
        # allow backing out past the front to EXIT
        if self.target < -0.6:
            self.close()
            return
        self.target = max(0.0, min(float(len(LAYER_KEYS) - 1), self.target))

        # smooth focus toward target
        self.focus += (self.target - self.focus) * min(1.0, dt * 10.0)

        # PAN: mouse relative motion
        dx, dy = pygame.mouse.get_rel()
        self.pan_x -= dx * PAN_SPEED
        self.pan_y -= dy * PAN_SPEED
        # PAN: right stick (additive, simultaneous)
        if gamepads is not None:
            rx, ry = gamepads.manipulator_right_stick()
            self.pan_x -= rx * STICK_SPEED * dt
            self.pan_y -= ry * STICK_SPEED * dt

        # ESC also exits
        if keys[pygame.K_ESCAPE]:
            self.close()

    # ---- draw (called between begin_2d/end_2d in app loop) ----
    def draw(self, cache, win_size):
        if not self.active or self.robot is None:
            return
        w, h = win_size
        # 1) opaque background replaces the world
        glDisable(GL_TEXTURE_2D)
        glColor4f(*BG_COLOR, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(0, 0); glVertex2f(w, 0); glVertex2f(w, h); glVertex2f(0, h)
        glEnd()

        # 2) draw layers FAR-to-NEAR so nearer sheets paint over farther ones.
        order = sorted(range(len(LAYER_KEYS)),
                       key=lambda i: abs(self.focus - i), reverse=True)
        for i in order:
            d = abs(self.focus - i)
            scale = max(0.45, 1.0 - 0.18 * d)
            alpha = max(0.0,  1.0 - 0.55 * d)
            blur  = min(8.0,  3.5 * d)
            if alpha <= 0.02:
                continue
            key  = LAYER_KEYS[i]
            text = self.robot.explain.get(key, "")
            # ENGINEER is locked (blurred) until CTRL held
            if key == "engineer" and not self.ctrl:
                blur = max(blur, 6.0)
                title_suffix = "   [hold CTRL]"
            else:
                title_suffix = ""
            title = LAYER_TITLE[key] + title_suffix
            # pan only the focused-ish sheet; far sheets stay centered-ish
            px = (w * 0.08) + (self.pan_x if d < 0.5 else 0.0)
            py = (h * 0.18) + (self.pan_y if d < 0.5 else 0.0)
            fs = int(BASE_FONTSIZE * scale)
            # title
            render.render_rich(cache, title, px, py - fs*1.6,
                               color=(0.55,0.7,0.95), fontsize=max(10,int(fs*0.8)),
                               alpha=alpha)
            # body
            render.render_rich(cache, text, px, py,
                               color=(0.95,0.96,0.98), fontsize=max(10,fs),
                               scale=1.0, alpha=alpha, blur=blur)
