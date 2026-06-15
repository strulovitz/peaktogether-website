# combat.py
# -----------------------------------------------------------------------------
# Brief #9 — COMBAT: find the blocking robot, fire a technique at it, destroy
# it on a matched opaque id, or harmlessly fizzle on a mismatch. Auto-faces the
# explosion on a correct hit.
# Brief #10 — ARSENAL: per-corridor weapon system. Face panel, Xbox/mouse
# selection, cosmetic projectiles. Replaces hardcoded ARSENAL + '['/']' cycling.
#
# PRIME LAW — math-blindness: this module NEVER interprets math meaning. It
# compares OPAQUE STRING IDS only:  loaded_id == robot.required_technique_id.
# Display names and portraits are presentation only, not math interpretation.
# -----------------------------------------------------------------------------

import numpy as np

import render
from render import draw_texture, draw_text_mathtext_2d, draw_plain_text_2d
from robots import load_portrait
from cockpit import CockpitHUD
from OpenGL.GL import (
    glBegin, glEnd, glVertex2f, glVertex3f, glColor4f, GL_LINES,
)

# ---------------------------------------------------------------------------
# constants (Brief #9)
# ---------------------------------------------------------------------------

_AUTOFACE_SECONDS = 1.0
_FIZZLE_SECONDS = 6.0
_WRAP_CHARS = 64        # fizzle panel text wrap width

# ---------------------------------------------------------------------------
# Brief #10: arsenal builder (math-blind — ids/names/filenames only)
# ---------------------------------------------------------------------------

def build_arsenal(robots):
    """robots in file order. Returns [{"id","name","png"}], de-duped by id,
    first-seen. Dedup by id NOT name (same name can be two weapons)."""
    seen, arsenal = set(), []
    for r in robots:
        tid = r.required_technique_id
        if tid in seen:
            continue
        seen.add(tid)
        png = r.name.strip().replace(" ", "_") + "-hologram.png"
        arsenal.append({"id": tid, "name": r.name, "png": png})
    return arsenal[:9]  # 3x3 grid cap


class Combat:
    """Owns combat + arsenal state for the active corridor."""

    # ---- 2D panel layout (cosmetic) ------------------------------------
    _COLS, _ROWS = 3, 3
    _CELL = 96
    _PAD = 14
    _MARGIN_X = 24
    _MARGIN_Y = 24

    def __init__(self):
        # ---- Brief #9 state ----
        self._autoface_t = 0.0
        self._autoface_target = None
        self._fizzle_t = 0.0
        self._fizzle_text = ""

        # ---- Brief #10: arsenal + selection state ----
        self.loaded_id = None
        self.arsenal = []
        self._arsenal_corridor = None

        # controller edge-detection state
        self._prev_trigger = False
        self._prev_btn = {0: False, 1: False, 2: False, 3: False, 4: False, 5: False}
        #                 A         B         X         Y         LB        RB

        # cosmetic projectile state
        self._proj = None  # {"from":(x,y,z),"to":(x,y,z),"t":float,"dur":float}|None

        # Brief #15: Descent-style cockpit HUD
        self._cockpit = CockpitHUD()

    # ==================================================================
    # ARSENAL SOURCING — multi-corridor
    # ==================================================================

    @staticmethod
    def current_corridor(hub):
        r = Combat.blocking_robot(hub)
        if r is not None:
            for c in hub.corridors:
                if r in c.get_robots():
                    return c
        return hub.corridors[0]  # fallback if nothing engaged

    def _sync_arsenal(self, hub):
        """Rebuild arsenal iff the engaged corridor changed. Identity-keyed."""
        corr = self.current_corridor(hub)
        if corr is not self._arsenal_corridor:
            self._arsenal_corridor = corr
            self.arsenal = build_arsenal(corr.get_robots())
            ids = {w["id"] for w in self.arsenal}
            if self.loaded_id not in ids:
                self.loaded_id = self.arsenal[0]["id"] if self.arsenal else None

    def _loaded_slot(self):
        for i, w in enumerate(self.arsenal):
            if w["id"] == self.loaded_id:
                return i
        return 0 if self.arsenal else -1

    # ==================================================================
    # blocking robot (Brief #9 — UNCHANGED)
    # ==================================================================

    @staticmethod
    def blocking_robot(hub):
        """First robot in path order that is not yet defeated, else None."""
        if not getattr(hub, "corridors", None):
            return None
        robots = hub.corridors[0].get_robots()
        for r in robots:
            if not r.is_defeated():
                return r
        return None

    # ==================================================================
    # INPUT (Brief #9 keyboard + Brief #10 controller/mouse)
    # ==================================================================

    def handle_input(self, fire_edge, prev_edge, next_edge, ship, hub,
                     mouse_click_edge, mouse_x, mouse_y, gamepads):
        """Rising-edge driven. SPACE=fire (keyboard fallback), controller for
        grid nav + cycle + trigger fire, mouse for click-to-select. prev_edge/
        next_edge ('['/']') are RETIRED — accepted but ignored."""
        self._sync_arsenal(hub)
        if not self.arsenal:
            return

        slot = self._loaded_slot()
        fire_now = bool(fire_edge)  # keyboard SPACE fallback

        # ---- controller (safe if absent) ----
        joy = getattr(gamepads, "manip_joy", None) if gamepads else None
        if joy is not None:
            # grid nav — edge-detected
            if self._btn_edge(joy, 3):   # Y -> UP
                self._try_move(slot - self._COLS)
            if self._btn_edge(joy, 0):   # A -> DOWN
                self._try_move(slot + self._COLS)
            if self._btn_edge(joy, 1):   # B -> RIGHT
                self._try_move(slot + 1, horizontal=True)
            if self._btn_edge(joy, 2):   # X -> LEFT
                self._try_move(slot - 1, horizontal=True)
            slot = self._loaded_slot()
            # linear cycle — edge-detected, wrap
            if self._btn_edge(joy, 4):   # LB -> prev
                self._cycle(-1)
            if self._btn_edge(joy, 5):   # RB -> next
                self._cycle(+1)

            # triggers -> FIRE (magnitude + edge, rest-value-agnostic)
            FIRE_TH = 0.5
            try:
                lt = joy.get_axis(4); rt = joy.get_axis(5)
            except Exception:
                lt = rt = 0.0
            trigger_now = (abs(lt) > FIRE_TH) or (abs(rt) > FIRE_TH)
            fire_edge_pad = trigger_now and not self._prev_trigger
            self._prev_trigger = trigger_now
            fire_now = fire_now or fire_edge_pad

        # ---- mouse (alternate) ----
        if mouse_click_edge:
            hit = self._face_hit_test(mouse_x, mouse_y, hub)
            if hit is not None:
                self.loaded_id = self.arsenal[hit]["id"]

        # ---- fire ----
        if fire_now:
            self._fire(ship, hub)

    def _btn_edge(self, joy, idx):
        try:
            now = bool(joy.get_button(idx))
        except Exception:
            now = False
        edge = now and not self._prev_btn[idx]
        self._prev_btn[idx] = now
        return edge

    def _try_move(self, target, horizontal=False):
        """Clamp/ignore moves leaving the grid or crossing a row edge."""
        if target < 0 or target >= len(self.arsenal):
            return
        if horizontal:
            cur = self._loaded_slot()
            if cur // self._COLS != target // self._COLS:
                return
        self.loaded_id = self.arsenal[target]["id"]

    def _cycle(self, step):
        if not self.arsenal:
            return
        i = (self._loaded_slot() + step) % len(self.arsenal)
        self.loaded_id = self.arsenal[i]["id"]

    # ==================================================================
    # FIRE (Brief #9 match/mismatch + Brief #10 projectile)
    # ==================================================================

    def _fire(self, ship, hub):
        robot = self.blocking_robot(hub)

        # Brief #10: spawn projectile (cosmetic)
        if robot is not None:
            try:
                ship_pos = getattr(ship, "pos", (0, 0, 0))
                self._proj = {
                    "from": tuple(ship_pos),
                    "to": tuple(robot.position),
                    "t": 0.0, "dur": 0.18,
                }
            except Exception:
                self._proj = None

        # Brief #9: existing resolve logic (UNCHANGED)
        if robot is None:
            return
        if self.loaded_id == robot.required_technique_id:
            robot.play_defeat()
            self._autoface_target = np.array(robot.position, dtype=float)
            self._autoface_t = _AUTOFACE_SECONDS
            self._fizzle_t = 0.0
            self._fizzle_text = ""
        else:
            msg = robot.fizzles.get(self.loaded_id)
            if not msg:
                msg = ("That technique doesn't apply to this robot. "
                       "Look at the blue hologram for the face that fits.")
            self._fizzle_text = msg
            self._fizzle_t = _FIZZLE_SECONDS

    # ==================================================================
    # UPDATE (Brief #9 auto-face/fizzle + Brief #10 projectile advance)
    # ==================================================================

    def update(self, dt, ship, hub):
        self._hud_robot = self.blocking_robot(hub)

        # Brief #10: advance cosmetic projectile
        if self._proj is not None:
            self._proj["t"] += dt / max(self._proj["dur"], 1e-6)
            if self._proj["t"] >= 1.0:
                self._proj = None

        # Brief #9: fizzle timer
        if self._fizzle_t > 0.0:
            self._fizzle_t = max(0.0, self._fizzle_t - dt)

        # Brief #9: auto-face nlerp
        if self._autoface_t > 0.0 and self._autoface_target is not None:
            self._autoface_t = max(0.0, self._autoface_t - dt)
            direction = self._autoface_target - np.array(ship.pos, dtype=float)
            if np.dot(direction, direction) > 1e-12:
                target_q = render.quat_look_along(direction)
                step = min(1.0, dt * 5.0)
                ship.q = _nlerp(ship.q, target_q, step)
            if self._autoface_t <= 0.0:
                self._autoface_target = None

    # ==================================================================
    # 3D PROJECTILE — parent inserts call between app.py lines 240-243
    # ==================================================================

    def draw_projectile_3d(self, cr, cu, texcache=None):
        """Cosmetic world-space streak. Drawn AFTER flush_walls, BEFORE 2D."""
        if self._proj is None:
            return
        t = self._proj["t"]
        fx, fy, fz = self._proj["from"]
        tx, ty, tz = self._proj["to"]
        head = t
        tail = max(0.0, t - 0.25)
        hx = fx + (tx - fx) * head; hy = fy + (ty - fy) * head; hz = fz + (tz - fz) * head
        sx = fx + (tx - fx) * tail; sy = fy + (ty - fy) * tail; sz = fz + (tz - fz) * tail
        glColor4f(1.0, 0.9, 0.3, 1.0)
        glBegin(GL_LINES)
        glVertex3f(sx, sy, sz)
        glVertex3f(hx, hy, hz)
        glEnd()

    # ==================================================================
    # HUD (Brief #9 text labels + fizzle + Brief #10 face panel)
    # ==================================================================

    def _weapon_by_id(self, tid):
        for w in self.arsenal:
            if w["id"] == tid:
                return w
        return None

    def _slot_rect(self, slot):
        """Pixel rect (x, y, w, h) for a grid slot. Top-left origin."""
        col = slot % self._COLS
        row = slot // self._COLS
        step = self._CELL + self._PAD
        x = self._MARGIN_X + col * step
        y = self._MARGIN_Y + row * step
        return (x, y, self._CELL, self._CELL)

    def _face_hit_test(self, mx, my, hub):
        self._sync_arsenal(hub)
        return self._cockpit.face_at_pixel(mx, my)

    def draw_hud(self, cache, win_size):
        """Cockpit HUD (struts, dashboard, gauge, left box, 3x3 face grid).
        Called between begin_2d/end_2d."""
        w, h = win_size
        robot = self._hud_robot

        vuln = None
        if robot is not None:
            wd = self._weapon_by_id(robot.required_technique_id)
            vuln = wd["name"] if wd else "?"

        wd = self._weapon_by_id(self.loaded_id)
        loaded_name = wd["name"] if wd else ("?" if self.arsenal else "NONE")

        state = {
            "arsenal":      self.arsenal,
            "loaded_slot":  self._loaded_slot(),
            "vulnerable":   vuln,
            "loaded_name":  loaded_name,
            "path_clear":   robot is None,
            "gauge_number": None,
            "fizzle_text":  self._fizzle_text if self._fizzle_t > 0.0 else None,
            "fizzle_alpha": min(1.0, self._fizzle_t / 1.0),
        }
        self._cockpit.draw(w, h, state)

    @staticmethod
    def _draw_border(x, y, w, h, color):
        r, g, b, a = color
        glColor4f(r, g, b, a)
        glBegin(GL_LINES)
        glVertex2f(x, y);         glVertex2f(x + w, y)
        glVertex2f(x + w, y);     glVertex2f(x + w, y + h)
        glVertex2f(x + w, y + h); glVertex2f(x, y + h)
        glVertex2f(x, y + h);     glVertex2f(x, y)
        glEnd()


# -----------------------------------------------------------------------------
# small free helpers (Brief #9 — UNCHANGED)
# -----------------------------------------------------------------------------

def _nlerp(qa, qb, t):
    """Normalized lerp from qa toward qb, taking the short way (sign fix)."""
    a = np.array(qa, dtype=float)
    b = np.array(qb, dtype=float)
    if np.dot(a, b) < 0.0:
        b = -b
    out = a * (1.0 - t) + b * t
    return render.quat_normalize(out)


def _wrap(text, width):
    """Greedy word-wrap into lines of <= width characters."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= width:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines
