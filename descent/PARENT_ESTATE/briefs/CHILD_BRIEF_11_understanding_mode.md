================================================================
BRIEF #11 — UNDERSTANDING MODE (the heart)

This is the big one. It sits ENTIRELY on top of render_rich (Brief #10, commit
f19c377) and the existing 2D bracket. It is composition + input, not new rendering.
Touch app.py (the loop + input + startup) and add ONE new file understanding.py and
ONE new file gamepad.py. Do NOT modify combat.py, hub.py, render.py, content_parser.py.

============================================================
WHAT IT IS
============================================================
Press U near a robot. Reality suspends. The four explanations of that robot's law —
mathematician, physicist, biologist, engineer — hang in DEPTH, like four sheets of
glass stacked away from you. ONE is in focus (sharp, full size, opaque). The others
recede: smaller, dimmer, Gaussian-blurred more the further they are from focus —
present but misty, "there's more here I don't fully grasp yet." You move THROUGH them
(mouse wheel / right trigger of depth) and you PAN across the focused sheet (move the
mouse / right stick) because a sheet can be larger than the screen. The engineer sheet
is special: it's blurred-and-locked until you hold CTRL (the "I'm an engineer, show me
the numbers" gesture), which sharpens it and reveals the value-arcs. Backing out past
the nearest sheet exits. Forgiving: any robot found by combat.blocking_robot(hub) is
the subject; no aiming, no distance math.

============================================================
GROUND TRUTH (verbatim — reuse exactly)
============================================================
The 2D overlay bracket (render.py, do NOT modify):

    def begin_2d(w, h):
        glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
        glOrtho(0, w, h, 0, -1, 1)   # y-down = screen/mouse coords
        glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_FOG)
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def end_2d():
        glMatrixMode(GL_PROJECTION); glPopMatrix()
        glMatrixMode(GL_MODELVIEW); glPopMatrix()
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_FOG)

The panel renderer (render.py, reuse — do NOT modify). Locked signature:

    render_rich(cache, text, x, y, color=(0.95,0.96,0.98),
                fontsize=15, scale=1.0, alpha=1.0, blur=0.0)  -> (w, h)

It rasterizes mixed prose+math, handles \n stacking, draws value-arcs [[ $e$ | v ]],
and blurs via Pillow when blur>0. It caches; calling it every frame is fine.

Solid-color fullscreen quad (between begin_2d/end_2d) — use this verbatim pattern:

    glDisable(GL_TEXTURE_2D)
    glColor4f(r, g, b, a)
    glBegin(GL_QUADS)
    glVertex2f(0, 0); glVertex2f(w, 0); glVertex2f(w, h); glVertex2f(0, h)
    glEnd()

Robot data (content_parser.py, read-only). The subject's four strings:

    robot_data.explain["mathematician"]
    robot_data.explain["physicist"]
    robot_data.explain["biologist"]
    robot_data.explain["engineer"]     # contains [[ ... | ... ]] arcs

The subject robot: combat.blocking_robot(hub) returns the first non-defeated robot,
or None. Get its RobotData the same way combat/hub already does (find how combat reads
the current robot's data and copy that access — do NOT invent a new path).

Screen size: app.WIN_SIZE == (1280, 800). Pass it in as win_size; w, h = win_size.

The frame loop (app.py:168-234) — verbatim relevant parts:

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            running = False
    keys = pygame.key.get_pressed()
    fire_edge = keys[pygame.K_SPACE] and not prev_keys[pygame.K_SPACE]
    ...
    glClearColor(*palette.CLEAR_COLOR, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    ship.update(dt, keys)
    ...
    render.begin_2d(*WIN_SIZE)
    combat_state.draw_hud(texcache, WIN_SIZE)
    render.end_2d()
    ...
    pygame.display.flip()
    prev_keys = keys

pygame 2.6.1 / SDL 2.28.4. pygame.init() already inits joystick.

============================================================
FILE 1 — gamepad.py (copy the verbatim GamepadManager)
============================================================
Create gamepad.py and paste the GamepadManager class EXACTLY as provided in the
fact-find (including the manipulator_right_stick method). Add this module header:

    import math
    import numpy as np
    import pygame

Do not change its logic. The Xbox right-stick axis indices are XBOX_RSTICK_X = 3,
XBOX_RSTICK_Y = 4 — these are the COMMON SDL2 mapping but UNVERIFIED on this pad. See
the runtime axis-picker in FILE 3 step D; the user will confirm/fix them in 5 seconds.

============================================================
FILE 2 — understanding.py (the mode object)
============================================================
Create understanding.py. One class, fully self-contained. It owns its own state and
draws itself. It does NOT update the world.

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
        # events: the list from pygame.event.get() THIS frame (for MOUSEWHEEL)
        # keys:   pygame.key.get_pressed()
        # gamepads: GamepadManager instance (or None)
        def handle_input(self, events, keys, gamepads, dt):
            if not self.active:
                return
            # CTRL = engineer unlock (polled)
            self.ctrl = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]

            # DEPTH: mouse wheel (events) + right trigger optional later
            for ev in events:
                if ev.type == pygame.MOUSEWHEEL:
                    self.target -= ev.y * DEPTH_SPEED_WHEEL   # wheel up = go deeper/forward
            # clamp target to layer range; allow backing out past the front to EXIT
            if self.target < -0.6:        # backed out past the nearest sheet
                self.close()
                return
            self.target = max(0.0, min(float(len(LAYER_KEYS) - 1), self.target))

            # smooth focus toward target
            self.focus += (self.target - self.focus) * min(1.0, dt * 10.0)
            # reset pan when the focused layer changes meaningfully
            # (optional nicety; keep pan continuous is fine too)

            # PAN: mouse relative motion
            dx, dy = pygame.mouse.get_rel()
            self.pan_x -= dx * PAN_SPEED
            self.pan_y -= dy * PAN_SPEED
            # PAN: right stick (additive, simultaneous)
            if gamepads is not None:
                rx, ry = gamepads.manipulator_right_stick()
                self.pan_x -= rx * STICK_SPEED * dt
                self.pan_y -= ry * STICK_SPEED * dt

            # ESC also exits (safety) — handled in app loop, but allow here too:
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
            #    distance d = abs(focus - i). Far sheets: smaller, dimmer, blurrier.
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

============================================================
FILE 3 — app.py wiring (FOUR small edits, nothing else)
============================================================
A) STARTUP, after pygame.init() and window creation, near other singletons:
       from gamepad import GamepadManager
       from understanding import UnderstandingMode
       import combat
       gamepads = GamepadManager()
       umode = UnderstandingMode()
   (If GamepadManager raises with no controller, wrap in try/except and set
    gamepads = None; the mode handles None.)

B) EVENT LOOP — keep a reference to the events list so the mode can read MOUSEWHEEL.
   Change the loop so events are captured into a list, and add the U-key open edge:
       events = pygame.event.get()
       for ev in events:
           if ev.type == pygame.QUIT:
               running = False
           elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE and not umode.active:
               running = False
           elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_u and not umode.active:
               umode.open(combat.blocking_robot(hub))   # use the real RobotData access
   (NOTE: blocking_robot returns the robot object; get its RobotData exactly the way
    combat already does. If combat exposes the RobotData directly, pass that.)

C) UPDATE GATING — when umode.active, SUSPEND the world: skip ship.update,
   combat handle_input/update, hub.update. Wrap the existing update calls:
       keys = pygame.key.get_pressed()
       if umode.active:
           umode.handle_input(events, keys, gamepads, dt)
       else:
           # ... ALL existing per-frame update/input code stays here unchanged ...
   The world still DRAWS behind, but the mode paints an opaque bg over it, so it's
   hidden. (Drawing the world is harmless; gating UPDATE is what "suspends reality".)

D) DRAW — add the mode's overlay AFTER the combat HUD block, still using the bracket:
       render.begin_2d(*WIN_SIZE)
       combat_state.draw_hud(texcache, WIN_SIZE)
       umode.draw(texcache, WIN_SIZE)
       render.end_2d()

   RIGHT-STICK AXIS PICKER (temporary, REQUIRED so the user can confirm axes):
   While umode.active, draw one debug line at the bottom showing the live raw axes:
       if umode.active and gamepads is not None and gamepads.manip_joy is not None:
           j = gamepads.manip_joy
           dbg = "axes: " + " ".join("a%d=%+.2f"%(k, j.get_axis(k))
                                     for k in range(j.get_numaxes()))
           render.draw_text_mathtext_2d(texcache, dbg, 20, WIN_SIZE[1]-30,
                                        color=(0.6,0.9,0.6), fontsize=12)
   The user wiggles the right stick, reads which axis numbers move, and (if not 3/4)
   edits XBOX_RSTICK_X / XBOX_RSTICK_Y in gamepad.py. Leave a comment saying so.

============================================================
CONSTRAINTS
============================================================
- New files: gamepad.py, understanding.py. Edits: app.py ONLY.
- Do NOT modify render.py, combat.py, hub.py, content_parser.py.
- Mouse: relative motion = pan, wheel = depth. Use set_grab/set_visible on open/close.
- CTRL = engineer unlock (polled K_LCTRL/K_RCTRL).
- Keyboard, mouse, controller all work simultaneously (additive) — do NOT make them
  exclusive.
- render_rich is called every frame; it caches, that's fine.
- If no controller: gamepads may be None; everything still works on mouse+keyboard.

============================================================
DEFINITION OF DONE
============================================================
1. Pressing U near a robot suspends the world and shows four depth-stacked panels,
   one sharp, the rest smaller/dimmer/blurrier with distance.
2. Mouse wheel moves focus through the four layers (forward = deeper); the sharp
   layer changes; blur/scale/alpha update smoothly.
3. Moving the mouse pans the focused sheet in all four directions (mouse hidden+grabbed).
4. The engineer panel stays blurred until CTRL is held, then sharpens and its
   value-arcs [[ ... | ... ]] become readable; releasing CTRL re-blurs it.
5. Scrolling back past the front sheet (or ESC) exits cleanly: mouse visible again,
   world resumes exactly where it was.
6. With an Xbox pad connected, the right stick ALSO pans (additive with mouse), and a
   debug line shows live axis values so the right-stick axis indices can be confirmed.
7. combat.py / hub.py / render.py / content_parser.py are byte-for-byte unchanged.

REPORT BACK (fill this out — do not skip):
- Files created / files modified (with line counts).
- Final verbatim signatures of UnderstandingMode methods.
- How you accessed the subject's RobotData from blocking_robot (verbatim line).
- Confirmed: which axis numbers moved the right stick at runtime (or "untested,
  left at 3/4").
- Any deviations from this brief. If none, "NONE".
- Confirm the four untouched files are byte-for-byte unchanged. YES/NO.
================================================================
