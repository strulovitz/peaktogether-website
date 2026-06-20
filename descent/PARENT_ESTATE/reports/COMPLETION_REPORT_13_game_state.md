COMPLETION REPORT -- game_state -- June 15, 2026

FILES ADDED/CHANGED:
    game_state.py -- NEW (the whole module, win-only)
    game_state_demo.py -- NEW (reuses app.py loop verbatim + 4 [GS] lines)
    app.py -- CHANGED (4 wiring lines added)
    corridor_builder.py -- CHANGED (1-line hostage draw guard)
    hostages.py, robots.py, hub_builder.py, render.py -- UNCHANGED

RUN-VERIFIED? Y -- both game_state_demo.py and app.py launch and run without errors.

THE REAL robot alive/dead FIELD read:
    Robot.is_defeated() returns self._defeated (robots.py). Read via public method.

THE REAL HUD text call used:
    draw_text_mathtext_2d(cache, latex, x, y, color=, fontsize=, scale=, alpha=)
    No draw_plain_text_2d exists -- use _mt() wrapper mirroring combat._mt.

HOW the couple is made to disappear on rescue:
    On rescue, corridor.hostages_rescued = True (sticky flag). The one-line guard
    in CorridorGeometry.draw_robots skips the hostage draw loop. Robots unaffected.

COMPLETE rule used:
    rescue + robots-dead: complete = rescued AND all(r.is_defeated() for r in robots)

FINAL GameState signatures:
    GameState(hub)
    update(hub, ship_pos, dt) -> None
    rescued_count() -> (done, total)
    corridors_complete() -> (done, total)
    show_rescue_flash() -> bool
    is_level_complete() -> bool
    draw_hud(cache, win_size) -> None

DEEPSEEK tuning TODOs:
    RESCUE_FLASH_SECONDS = 2.2, RESCUE_RADIUS = NEAR_RADIUS = 14.0
    RESCUE_FLASH_TEXT = "HOSTAGES RESCUED", LEVEL_COMPLETE_TEXT = "LEVEL COMPLETE"
    _FLASH_FONTSIZE = 34, _BANNER_FONTSIZE = 40
    _STATUS_COLOR = (0.65, 0.95, 0.70)
