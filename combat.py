# combat.py
# -----------------------------------------------------------------------------
# Brief #9 — COMBAT: find the blocking robot, fire a technique at it, destroy
# it on a matched opaque id, or harmlessly fizzle on a mismatch. Auto-faces the
# explosion on a correct hit. Draws a MINIMAL text-only HUD.
#
# PRIME LAW — math-blindness: this module NEVER interprets math meaning. It
# compares OPAQUE STRING IDS only:  robot.required_technique_id == fired id.
# The ARSENAL display names are OUR labels, not math interpretation.
#
# Scope fences honored: NO weapons/face panel (child #10), NO hostages
# (child #11), NO scoring/lives/timers/fail state, NO quaternion reinvention
# (uses render.quat_* only).
# -----------------------------------------------------------------------------

import numpy as np
import render

# (id, display-name) — display names are OUR labels for the HUD only.
ARSENAL = [
    ("gauss_e", "Gauss"),
    ("gauss_m", "Gauss"),
    ("faraday", "Faraday"),
    ("ampere",  "Ampere"),
    ("maxwell", "Maxwell"),
]

# id -> display name lookup (OUR label; not math interpretation).
_NAME_BY_ID = {tid: name for tid, name in ARSENAL}

# Auto-face state durations.
_AUTOFACE_SECONDS = 1.0
_FIZZLE_SECONDS = 6.0

# HUD wrap width (characters) for the fizzle panel.
_WRAP_CHARS = 64


class Combat:
    """Owns combat state for the active (single) corridor test."""

    def __init__(self):
        self._loaded_index = 0          # index into ARSENAL
        self._autoface_t = 0.0          # seconds remaining of auto-face turn
        self._autoface_target = None    # world point to look toward
        self._fizzle_t = 0.0            # seconds remaining of fizzle panel
        self._fizzle_text = ""          # current fizzle message

    # -- selection (temporary; real selector is child #10) -------------------
    @property
    def loaded_id(self):
        return ARSENAL[self._loaded_index][0]

    @property
    def loaded_name(self):
        return ARSENAL[self._loaded_index][1]

    def _select_prev(self):
        self._loaded_index = (self._loaded_index - 1) % len(ARSENAL)

    def _select_next(self):
        self._loaded_index = (self._loaded_index + 1) % len(ARSENAL)

    # -- blocking robot ------------------------------------------------------
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

    # -- input ---------------------------------------------------------------
    def handle_input(self, fire_edge, prev_edge, next_edge, ship, hub):
        """Rising-edge driven. fire_edge=SPACE, prev_edge='[', next_edge=']'.

        Keys chosen: SPACE (fire), '[' (prev), ']' (next).
        Existing controls are WASD/RF (move), arrow keys (rotate), Q/E (roll),
        Shift (boost), SPACE (fire). '[' and ']' do NOT collide with any of
        those, and SPACE is read on its RISING EDGE here (not held) so a held
        boost/move never re-triggers a shot.
        """
        if prev_edge:
            self._select_prev()
        if next_edge:
            self._select_next()
        if fire_edge:
            self._fire(ship, hub)

    def _fire(self, ship, hub):
        robot = self.blocking_robot(hub)
        if robot is None:
            return  # no blocking robot -> SPACE does nothing
        fired = self.loaded_id
        if fired == robot.required_technique_id:
            # MATCH -> autonomous explosion + gentle auto-face turn.
            robot.play_defeat()
            self._autoface_target = np.array(robot.position, dtype=float)
            self._autoface_t = _AUTOFACE_SECONDS
            self._fizzle_t = 0.0
            self._fizzle_text = ""
        else:
            # MISMATCH -> HARMLESS fizzle. No defeat, no penalty.
            msg = robot.fizzles.get(fired)
            if not msg:
                msg = ("That technique doesn't apply to this robot. "
                       "Look at the blue hologram for the face that fits.")
            self._fizzle_text = msg
            self._fizzle_t = _FIZZLE_SECONDS

    # -- per-frame update ----------------------------------------------------
    def update(self, dt, ship, hub):
        self._hud_robot = self.blocking_robot(hub)

        # Tick down the fizzle panel timer.
        if self._fizzle_t > 0.0:
            self._fizzle_t = max(0.0, self._fizzle_t - dt)

        # Auto-face: smoothly nlerp ship.q toward looking at the explosion.
        if self._autoface_t > 0.0 and self._autoface_target is not None:
            self._autoface_t = max(0.0, self._autoface_t - dt)
            direction = self._autoface_target - np.array(ship.pos, dtype=float)
            if np.dot(direction, direction) > 1e-12:
                target_q = render.quat_look_along(direction)
                # nlerp step: lerp 4 components toward target (short way),
                # then normalize. Step size scales with dt for a gentle turn.
                step = min(1.0, dt * 5.0)
                ship.q = _nlerp(ship.q, target_q, step)
            if self._autoface_t <= 0.0:
                self._autoface_target = None

    # -- HUD (text only; between begin_2d/end_2d by caller) ------------------
    def draw_hud(self, cache, win_size):
        w, h = win_size
        # We are inside begin_2d/end_2d (caller wraps). Origin top-left, y-down.
        x = 24
        y = 28
        line_h = 26
        col = (0.85, 0.85, 0.90)

        robot = self._hud_robot
        if robot is None:
            render.draw_text_mathtext_2d(
                cache, r"\mathrm{PATH\ CLEAR}", x, y, color=(0.6, 0.95, 0.6),
                fontsize=18)
        else:
            need_name = _NAME_BY_ID.get(robot.required_technique_id, "?")
            render.draw_text_mathtext_2d(
                cache, _mt(f"VULNERABLE TO: {need_name}"), x, y,
                color=col, fontsize=18)
        y += line_h

        render.draw_text_mathtext_2d(
            cache, _mt(f"LOADED: {self.loaded_name}"), x, y,
            color=(0.95, 0.85, 0.55), fontsize=18)
        y += line_h

        # Fizzle panel (wrapped) lower on the screen.
        if self._fizzle_t > 0.0 and self._fizzle_text:
            fy = int(h * 0.62)
            render.draw_text_mathtext_2d(
                cache, _mt("That technique fizzled harmlessly:"), x, fy,
                color=(0.95, 0.7, 0.6), fontsize=16)
            fy += line_h
            for line in _wrap(self._fizzle_text, _WRAP_CHARS):
                render.draw_text_mathtext_2d(
                    cache, _mt(line), x, fy, color=(0.9, 0.85, 0.8),
                    fontsize=15)
                fy += 22


# -----------------------------------------------------------------------------
# small free helpers
# -----------------------------------------------------------------------------
def _nlerp(qa, qb, t):
    """Normalized lerp from qa toward qb, taking the short way (sign fix)."""
    a = np.array(qa, dtype=float)
    b = np.array(qb, dtype=float)
    if np.dot(a, b) < 0.0:
        b = -b
    out = a * (1.0 - t) + b * t
    return render.quat_normalize(out)


def _mt(text):
    r"""Wrap a plain string as mathtext \mathrm{...} so draw_text_mathtext_2d
    renders it as upright readable text. Spaces -> \ ; backslash-safe input
    only (we feed plain ASCII labels and fizzle prose)."""
    safe = (text.replace("\\", "")
                .replace("{", "")
                .replace("}", "")
                .replace("$", "")
                .replace("^", " ")
                .replace("_", " ")
                .replace("&", "and")
                .replace("%", " percent"))
    safe = safe.replace(" ", r"\ ")
    return r"\mathrm{" + safe + r"}"


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
