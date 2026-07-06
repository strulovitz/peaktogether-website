"""
app.py — the real entry point: `python app.py`. [BONE M7]

Scripture: BIBLE par.14. This file OWNS the master loop and is the ONLY
place where screens are switched (menu -> story -> puzzle -> lab). Its
inner heartbeat is IDENTICAL to m1_demo.py's proven wiring:

    frame = conductor.update(dt)
    for i in frame.triggers: audio.trigger(...)
    active_screen.draw(surface, frame, ...)

FATTEN ME LIKE THIS (M7 parent): init order is law — ui.audio_pygame.
init_mixer() FIRST, then pygame.init(), then the 1280x720 window
(layout.WINDOW). Route events through input_actions.InputMapper (never
raw keys). Compose, don't invent: every behavior already lives in a
module; this file only connects them. Target: under ~300 lines.
"""

from __future__ import annotations


def main() -> None:
    raise NotImplementedError(
        "M7: menu -> pack -> scenes -> puzzles, wired exactly like m1_demo")


if __name__ == "__main__":
    main()
