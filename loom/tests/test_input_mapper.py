"""Headless InputMapper tests (M2)."""

import json
import os
import sys

import pygame
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "player"))

from ui.input_actions import InputMapper, Action              # noqa: E402


def write(tmp_path, data):
    p = tmp_path / "input_mapping.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return str(p)


GOOD = {"keyboard": {"SPACE": "PLAY_PAUSE", "HOME": "STOP",
                     "LEFT": "NUDGE_LEFT", "RIGHT": "NUDGE_RIGHT",
                     "UP": "MENU_UP", "DOWN": "MENU_DOWN",
                     "RETURN": "MENU_CONFIRM", "BACKSPACE": "MENU_BACK",
                     "ESCAPE": "QUIT"},
        "mouse": {"_comment": "doc", "BUTTON_1": "POINTER_PRIMARY"}}


def test_maps_keys_to_actions(tmp_path):
    m = InputMapper.load(write(tmp_path, GOOD))
    e = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
    assert m.map_event(e) == [Action.PLAY_PAUSE]
    e = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    assert m.map_event(e) == [Action.QUIT]


def test_unmapped_key_yields_nothing(tmp_path):
    m = InputMapper.load(write(tmp_path, GOOD))
    e = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z)
    assert m.map_event(e) == []


def test_mouse_section_and_comments_ignored(tmp_path):
    m = InputMapper.load(write(tmp_path, GOOD))       # must not raise
    e = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0))
    assert m.map_event(e) == []


def test_unknown_action_name_rejected(tmp_path):
    bad = {"keyboard": {"SPACE": "FLY_TO_THE_MOON"}}
    with pytest.raises(ValueError):
        InputMapper.load(write(tmp_path, bad))


def test_quit_event_maps_to_quit(tmp_path):
    m = InputMapper.load(write(tmp_path, GOOD))
    assert m.map_event(pygame.event.Event(pygame.QUIT)) == [Action.QUIT]
