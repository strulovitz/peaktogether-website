"""game_state.py -- DESCENT QED, MODULE: GAME STATE (Brief #13).

The thin layer that turns a flyable world into a GAME. It holds the few
PROGRESS BITS and the win-only rules:

    * which corridor's couple has been RESCUED
    * which corridor is COMPLETE (rescued AND its robots cleared)
    * whether the whole LEVEL is COMPLETE
    * the rescue TRIGGER (fly near the couple -> rescued + couple vanishes)
    * a harmless "HOSTAGES RESCUED" HUD flash timer

PRIME LAW -- MATHEMATICS-BLIND. This module interprets NO math, NO technique
meaning, NO color->meaning. It READS existing bits only:
    Robot.is_defeated()                  (robots.py -- the real dead bit)
    hostages.near_hostages(list, pos, r) (hostages.py -- pure geometry)
and writes PROGRESS BITS only.

THERE IS NO LOSING. No ship damage, no death, no failing timer, no game-over.
The only timer here is the cosmetic rescue-message flash. Win-only.

WIRING (the parent adds these one-liners; this module touches nothing else):
    construct once, where hub is built:
        from game_state import GameState
        game_state = GameState(hub)
    in the loop, AFTER hub.update(...):
        game_state.update(hub, ship.pos, dt)
    in the existing begin_2d/end_2d HUD block, next to combat_state.draw_hud:
        game_state.draw_hud(texcache, WIN_SIZE)
    one-line sticky guard in corridor_builder.CorridorGeometry.draw_robots,
    around the hostage draw loop:
        if not getattr(self, "hostages_rescued", False):
            for h in self._hostages:
                h.draw(camera_right, camera_up, texcache)

This module draws NO world geometry. It never queues a wall and never calls
flush_walls. It only reads bits and (in draw_hud) draws HUD text via the
existing render.draw_text_mathtext_2d path.
"""

from render import draw_text_mathtext_2d, draw_plain_text_2d
from hostages import near_hostages, NEAR_RADIUS


# ----------------------------------------------------------------------
# TUNABLES  (DeepSeek tunes ONLY these -- no design, no lose state ever)
# ----------------------------------------------------------------------
RESCUE_FLASH_SECONDS = 2.2
RESCUE_RADIUS = NEAR_RADIUS
RESCUE_FLASH_TEXT  = "HOSTAGES RESCUED"
LEVEL_COMPLETE_TEXT = "LEVEL COMPLETE"

PROOF_FLASH_SECONDS = 3.0
PROOF_COMPLETE_PREFIX = "PROOF COMPLETE"
QED_LINE_1 = "QUOD ERAT DEMONSTRANDUM"
QED_LINE_2 = "All nine proofs solved."
_PROOF_FONTSIZE = 30
_PROOF_COLOR = (0.85, 0.95, 0.70)
_QED_COLOR = (1.00, 0.95, 0.75)

_STATUS_FONTSIZE   = 18
_FLASH_FONTSIZE    = 34
_BANNER_FONTSIZE   = 40
_STATUS_COLOR      = (0.65, 0.95, 0.70)
_FLASH_COLOR       = (0.95, 0.85, 0.55)
_BANNER_COLOR      = (0.70, 0.95, 1.00)
_STATUS_RIGHT_PAD  = 24
_STATUS_TOP_PAD    = 28
_CHAR_PX_AT_18     = 11.0


class GameState:
    """Holds the progress bits and the win-only rules for one level.

    PUBLIC INTERFACE (Brief #13):
        GameState(hub)
        update(hub, ship_pos, dt) -> None
        rescued_count() -> (done:int, total:int)
        corridors_complete() -> (done:int, total:int)
        show_rescue_flash() -> bool
        is_level_complete() -> bool
        draw_hud(cache, win_size) -> None   # HUD text only; no world geometry

    NO lose method. NO damage. NO failing timer. WIN ONLY.
    """

    def __init__(self, hub):
        n = len(getattr(hub, "corridors", []))
        self._records = [{"rescued": False, "complete": False} for _ in range(n)]
        self.level_complete = False
        self._flash_t = 0.0
        self._proof_flash_t = 0.0
        self._proof_flash_text = ""
        self._banner_shown = False

    def update(self, hub, ship_pos, dt):
        corridors = getattr(hub, "corridors", [])

        for i, corridor in enumerate(corridors):
            if i >= len(self._records):
                self._records.append({"rescued": False, "complete": False})
            rec = self._records[i]

            if not rec["rescued"]:
                hostages = getattr(corridor, "_hostages", None)
                if hostages and near_hostages(hostages, ship_pos, RESCUE_RADIUS):
                    rec["rescued"] = True
                    corridor.hostages_rescued = True
                    self._flash_t = RESCUE_FLASH_SECONDS

            if rec["rescued"] and not rec["complete"]:
                robots = corridor.get_robots()
                if all(r.is_defeated() for r in robots):
                    rec["complete"] = True
                    done = sum(1 for r in self._records if r["complete"])
                    total = len(self._records)
                    self._proof_flash_text = "%s  %d / %d" % (
                        PROOF_COMPLETE_PREFIX, done, total)
                    self._proof_flash_t = PROOF_FLASH_SECONDS

        if self._records and all(r["complete"] for r in self._records):
            self.level_complete = True

        if self._flash_t > 0.0:
            self._flash_t = max(0.0, self._flash_t - dt)
        if self._proof_flash_t > 0.0:
            self._proof_flash_t = max(0.0, self._proof_flash_t - dt)

    def rescued_count(self):
        done = sum(1 for r in self._records if r["rescued"])
        return (done * 2, len(self._records) * 2)  # 2 people per corridor

    def corridors_complete(self):
        done = sum(1 for r in self._records if r["complete"])
        return (done, len(self._records))

    def show_rescue_flash(self):
        return self._flash_t > 0.0

    def is_level_complete(self):
        return self.level_complete

    def draw_hud(self, cache, win_size):
        w, h = win_size

        done, total = self.rescued_count()
        status = "RESCUED %d/%d" % (done, total)
        draw_plain_text_2d(status, w - _STATUS_RIGHT_PAD, _STATUS_TOP_PAD,
                           size=_STATUS_FONTSIZE, color=_STATUS_COLOR,
                           align="right")

        if self.show_rescue_flash():
            draw_plain_text_2d(RESCUE_FLASH_TEXT, w // 2, int(h * 0.40),
                               size=_FLASH_FONTSIZE, color=_FLASH_COLOR,
                               align="center")

        if self._proof_flash_t > 0.0:
            draw_plain_text_2d(self._proof_flash_text, w // 2, int(h * 0.48),
                               size=_PROOF_FONTSIZE, color=_PROOF_COLOR,
                               align="center")

        if self.is_level_complete():
            draw_plain_text_2d(QED_LINE_1, w // 2, int(h * 0.46),
                               size=_BANNER_FONTSIZE, color=_QED_COLOR,
                               align="center")
            draw_plain_text_2d(QED_LINE_2, w // 2, int(h * 0.54),
                               size=_STATUS_FONTSIZE, color=_BANNER_COLOR,
                               align="center")
