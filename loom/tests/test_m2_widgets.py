"""Headless M2 tests: geometry + mapping, no window, no audio."""

import os
import sys
from types import SimpleNamespace

import pygame
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "player"))

from ui.bench_keyboard import KeyboardWidget                  # noqa: E402
from ui.bench_transport import (TransportWidget,              # noqa: E402
                                TransportCommand)
from ui.graph_view import u_to_beats, beats_to_u              # noqa: E402


def fake_spell():
    notes = [SimpleNamespace(index=i, midi=60 + i, start_beat=float(i),
                             duration_beats=1.0, gain=0.9)
             for i in range(4)]
    raw = {"notes": [{"graph_segment":
                      {"x_from": i / 4, "x_to": (i + 1) / 4}}
                     for i in range(4)]}
    return SimpleNamespace(notes=notes, raw=raw, total_beats=4.0)


# ---- keyboard geometry ----------------------------------------------

def test_keyboard_white_and_black_hits():
    kb = KeyboardWidget(pygame.Rect(0, 0, 700, 170), 60, 1)
    ww = 700 / 8
    assert kb.hit_test((int(ww * 0.5), 160)) == 60        # C4, low on key
    assert kb.hit_test((int(ww * 7.5), 160)) == 72        # C5
    assert kb.hit_test((int(ww * 1.0), 20)) == 61         # Cs4 boundary, top
    assert kb.hit_test((int(ww * 1.0), 160)) in (60, 62)  # below black: white
    assert kb.hit_test((9999, 9999)) is None


def test_keyboard_rejects_non_c_base():
    with pytest.raises(ValueError):
        KeyboardWidget(pygame.Rect(0, 0, 700, 170), 61, 1)
    with pytest.raises(ValueError):
        KeyboardWidget(pygame.Rect(0, 0, 700, 170), 60, 3)


# ---- transport: m1_demo's proven click-vs-drag, extracted ------------

def ev(t, **kw):
    return pygame.event.Event(t, **kw)


def test_transport_click_is_jump():
    w = TransportWidget(pygame.Rect(0, 0, 700, 60))
    g = w._groove
    mid = (g.x + g.w // 2, g.centery)
    assert w.handle_event(ev(pygame.MOUSEBUTTONDOWN, button=1, pos=mid), 8.0) == []
    out = w.handle_event(ev(pygame.MOUSEBUTTONUP, button=1, pos=mid), 8.0)
    assert len(out) == 1 and out[0].command is TransportCommand.JUMP
    assert abs(out[0].beats - 4.0) < 0.1


def test_transport_drag_is_scrub_and_release_ends():
    w = TransportWidget(pygame.Rect(0, 0, 700, 60))
    g = w._groove
    p0 = (g.x + 10, g.centery)
    w.handle_event(ev(pygame.MOUSEBUTTONDOWN, button=1, pos=p0), 8.0)
    out = w.handle_event(
        ev(pygame.MOUSEMOTION, pos=(p0[0] + 30, p0[1])), 8.0)
    cmds = [e.command for e in out]
    assert cmds[0] is TransportCommand.SCRUB_BEGIN
    assert TransportCommand.SCRUB_TO in cmds
    out = w.handle_event(
        ev(pygame.MOUSEBUTTONUP, button=1, pos=(p0[0] + 30, p0[1])), 8.0)
    assert [e.command for e in out] == [TransportCommand.SCRUB_END]


def test_transport_tiny_wiggle_is_still_click():
    w = TransportWidget(pygame.Rect(0, 0, 700, 60))
    g = w._groove
    p0 = (g.x + 100, g.centery)
    w.handle_event(ev(pygame.MOUSEBUTTONDOWN, button=1, pos=p0), 8.0)
    out = w.handle_event(
        ev(pygame.MOUSEMOTION, pos=(p0[0] + 2, p0[1])), 8.0)   # <= 3 px
    assert out == []
    out = w.handle_event(
        ev(pygame.MOUSEBUTTONUP, button=1, pos=(p0[0] + 2, p0[1])), 8.0)
    assert [e.command for e in out] == [TransportCommand.JUMP]


# ---- graph mapping: the permitted arithmetic --------------------------

def test_u_to_beats_and_back():
    s = fake_spell()
    assert abs(u_to_beats(s, 0.0) - 0.0) < 1e-9
    assert abs(u_to_beats(s, 0.5) - 2.0) < 1e-9
    assert abs(u_to_beats(s, 1.0) - 4.0) < 1e-9
    assert abs(beats_to_u(s, 2.0) - 0.5) < 1e-9
    assert abs(beats_to_u(s, 3.5) - 0.875) < 1e-9


def test_graph_without_data_is_silent():
    s = SimpleNamespace(notes=[], raw={}, total_beats=0.0)
    assert u_to_beats(s, 0.5) == 0.0
    assert beats_to_u(s, 1.0) == 0.0
