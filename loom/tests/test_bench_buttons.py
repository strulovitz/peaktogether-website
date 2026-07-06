"""Headless tests for ui/bench_buttons.py (M3): the activation contract.
Rect math and event handling need no display or font."""

import pygame

from player.ui.bench_buttons import BenchButton

R = (100, 100, 120, 34)


def down(pos):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                              {"button": 1, "pos": pos})


def up(pos):
    return pygame.event.Event(pygame.MOUSEBUTTONUP,
                              {"button": 1, "pos": pos})


def test_click_inside_activates_once():
    b = BenchButton(R, "OK")
    assert b.handle_event(down((110, 110))) is False   # press: not yet
    assert b.handle_event(up((110, 110))) is True      # release inside: fire
    assert b.handle_event(up((110, 110))) is False     # no double fire


def test_drag_off_before_release_aborts():
    b = BenchButton(R, "OK")
    b.handle_event(down((110, 110)))
    assert b.handle_event(up((500, 500))) is False


def test_release_inside_without_press_inside_is_nothing():
    b = BenchButton(R, "Cancel")
    b.handle_event(down((500, 500)))
    assert b.handle_event(up((110, 110))) is False


def test_disabled_button_is_deaf():
    b = BenchButton(R, "OK")
    b.enabled = False
    b.handle_event(down((110, 110)))
    assert b.handle_event(up((110, 110))) is False
    b.enabled = True                                    # re-enabling is clean
    assert b.handle_event(up((110, 110))) is False      # old press forgotten
