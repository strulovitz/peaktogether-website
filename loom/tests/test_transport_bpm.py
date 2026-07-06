"""BPM box + spinner tests (rev 3), headless."""

import os
import sys

import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "player"))

from ui.bench_transport import (TransportWidget,               # noqa: E402
                                TransportCommand)


def ev(t, **kw):
    return pygame.event.Event(t, **kw)


def key(k, uni=""):
    return ev(pygame.KEYDOWN, key=k, unicode=uni)


def make():
    return TransportWidget(pygame.Rect(0, 0, 950, 30), initial_bpm=110)


def click(w, pos):
    return w.handle_event(ev(pygame.MOUSEBUTTONDOWN, button=1, pos=pos), 8.0)


def test_type_and_commit():
    w = make()
    click(w, w._bpm_box.center)
    assert w.typing is True
    for ch, kc in (("1", pygame.K_1), ("5", pygame.K_5), ("0", pygame.K_0)):
        w.handle_event(key(kc, ch), 8.0)
    out = w.handle_event(key(pygame.K_RETURN), 8.0)
    assert w.typing is False and w.bpm == 150
    assert [e.command for e in out] == [TransportCommand.SET_BPM]
    assert out[0].bpm == 150.0


def test_commit_clamps_40_to_200():
    w = make()
    click(w, w._bpm_box.center)
    for ch, kc in (("9", pygame.K_9),) * 3:
        w.handle_event(key(kc, ch), 8.0)
    out = w.handle_event(key(pygame.K_RETURN), 8.0)
    assert w.bpm == 200 and out[0].bpm == 200.0
    click(w, w._bpm_box.center)
    w.handle_event(key(pygame.K_5, "5"), 8.0)
    out = w.handle_event(key(pygame.K_RETURN), 8.0)
    assert w.bpm == 40 and out[0].bpm == 40.0


def test_escape_cancels_and_empty_commit_reverts():
    w = make()
    click(w, w._bpm_box.center)
    w.handle_event(key(pygame.K_7, "7"), 8.0)
    w.handle_event(key(pygame.K_ESCAPE), 8.0)
    assert w.typing is False and w.bpm == 110
    click(w, w._bpm_box.center)
    out = w.handle_event(key(pygame.K_RETURN), 8.0)   # nothing typed
    assert out == [] and w.bpm == 110


def test_click_away_commits():
    w = make()
    click(w, w._bpm_box.center)
    w.handle_event(key(pygame.K_9, "9"), 8.0)
    w.handle_event(key(pygame.K_0, "0"), 8.0)
    out = click(w, (w._groove.centerx, w._groove.centery - 60))  # outside all
    assert any(e.command is TransportCommand.SET_BPM and e.bpm == 90.0
               for e in out)
    assert w.typing is False


def test_spinners_step_and_clamp():
    w = make()
    out = click(w, w._spin_up.center)
    assert w.bpm == 111 and out[0].bpm == 111.0
    out = click(w, w._spin_down.center)
    assert w.bpm == 110 and out[0].bpm == 110.0
    w2 = TransportWidget(pygame.Rect(0, 0, 950, 30), initial_bpm=40)
    out = click(w2, w2._spin_down.center)
    assert w2.bpm == 40 and out == []                 # no event on no-change


def test_hotkeys_ignored_while_typing_is_wirings_job():
    # the widget only exposes .typing; SPACE while focused must not be
    # eaten here (unicode " " is not a digit -> ignored, no crash):
    w = make()
    click(w, w._bpm_box.center)
    out = w.handle_event(key(pygame.K_SPACE, " "), 8.0)
    assert out == [] and w.typing is True
