"""
input_actions.py — the mandatory input-abstraction layer. [BONE M2]

Scripture: BIBLE par.6 (LOCKED): named actions + ONE device->action
config file (player/data/input_mapping.json), so keyboard/mouse today
can become joystick/Xbox controller later WITHOUT touching game code.
Player K (keyboard, canonically Boyfriend): story, menus, Choice
answers, transport hotkeys. Player M (mouse, canonically Girlfriend):
piano, OK/Cancel, transport + scrubbing. Solo: everything mouse-usable.

FATTEN ME LIKE THIS (M2 parent): implement InputMapper.map_event()
translating raw pygame events into Action values via the JSON file.
Game code must NEVER test ev.key/ev.button directly (m1_demo did, as
throwaway scaffolding; the real app never will).
"""

from __future__ import annotations

from enum import Enum, auto


class Action(Enum):
    # transport (either player)
    PLAY_PAUSE = auto(); STOP = auto(); NUDGE_LEFT = auto(); NUDGE_RIGHT = auto()
    # Player K: story & menus
    MENU_UP = auto(); MENU_DOWN = auto(); MENU_CONFIRM = auto(); MENU_BACK = auto()
    # Player M: bench commitment
    OK = auto(); CANCEL = auto()
    # app
    QUIT = auto()


class InputMapper:
    """Frozen interface."""

    @staticmethod
    def load(mapping_path: str) -> "InputMapper":
        raise NotImplementedError("M2: read input_mapping.json")

    def map_event(self, pygame_event) -> list[Action]:
        raise NotImplementedError("M2")
