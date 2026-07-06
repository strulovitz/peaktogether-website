"""
input_actions.py — the mandatory input-abstraction layer. [M2 — Parent 3]

Scripture: BIBLE par.5 (LOCKED): named actions + ONE device->action
config file (player/data/input_mapping.json), so keyboard/mouse today
can become joystick/Xbox controller later WITHOUT touching game code.
Player K (keyboard, canonically Boyfriend): story, menus, Choice
answers, transport hotkeys. Player M (mouse, canonically Girlfriend):
piano, OK/Cancel, transport + scrubbing. Solo: everything mouse-usable.

ROUTING DOCTRINE (M2, frozen): the InputMapper translates KEY events
into named Actions via the JSON file. POINTER events (motion, buttons)
are NOT translated here — they flow raw to the widgets, which hit-test
their own rects (KeyboardWidget.hit_test, TransportWidget.handle_event,
GraphView.handle_event). The JSON's "mouse" section documents this
routing; the mapper skips it. A future gamepad parent adds a "gamepad"
section + entries here, ZERO game-code changes — exactly as scripture
demands. Game code must NEVER test ev.key/ev.button directly.
"""

from __future__ import annotations

import json
from enum import Enum, auto

import pygame


class Action(Enum):
    # transport (either player)
    PLAY_PAUSE = auto(); STOP = auto(); NUDGE_LEFT = auto(); NUDGE_RIGHT = auto()
    # Player K: story & menus
    MENU_UP = auto(); MENU_DOWN = auto(); MENU_CONFIRM = auto(); MENU_BACK = auto()
    # Player M: bench commitment
    OK = auto(); CANCEL = auto()
    # app
    QUIT = auto()


# Key names used in input_mapping.json -> pygame key constants.
# Explicit aliases first (stable, spelling-proof); pygame.key.key_code
# is the fallback for names not listed here.
_KEY_ALIASES = {
    "SPACE": pygame.K_SPACE, "HOME": pygame.K_HOME,
    "LEFT": pygame.K_LEFT, "RIGHT": pygame.K_RIGHT,
    "UP": pygame.K_UP, "DOWN": pygame.K_DOWN,
    "RETURN": pygame.K_RETURN, "ENTER": pygame.K_RETURN,
    "BACKSPACE": pygame.K_BACKSPACE, "ESCAPE": pygame.K_ESCAPE,
    "END": pygame.K_END, "TAB": pygame.K_TAB,
}

# JSON action names that are documentation, not mappable Actions:
_DOC_ONLY_ACTIONS = {"POINTER_PRIMARY"}


class InputMapper:
    """Frozen interface."""

    def __init__(self, key_to_action: dict[int, Action]) -> None:
        self._key_to_action = key_to_action

    @staticmethod
    def load(mapping_path: str) -> "InputMapper":
        with open(mapping_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        key_to_action: dict[int, Action] = {}
        for key_name, action_name in data.get("keyboard", {}).items():
            if key_name.startswith("_"):
                continue                       # _comment fields
            if action_name in _DOC_ONLY_ACTIONS:
                continue
            try:
                action = Action[action_name]
            except KeyError:
                raise ValueError(
                    f"{mapping_path}: unknown action {action_name!r} for key "
                    f"{key_name!r}. Known actions: "
                    f"{', '.join(a.name for a in Action)}") from None
            keycode = _KEY_ALIASES.get(key_name.upper())
            if keycode is None:
                try:
                    keycode = pygame.key.key_code(key_name.lower())
                except Exception:
                    raise ValueError(
                        f"{mapping_path}: unknown key name {key_name!r}"
                    ) from None
            key_to_action[keycode] = action
        # "mouse" section intentionally ignored: pointer events route
        # raw to widgets (see ROUTING DOCTRINE in the module docstring).
        return InputMapper(key_to_action)

    def map_event(self, pygame_event) -> list[Action]:
        if pygame_event.type == pygame.KEYDOWN:
            action = self._key_to_action.get(pygame_event.key)
            if action is not None:
                return [action]
        if pygame_event.type == pygame.QUIT:
            return [Action.QUIT]
        return []
