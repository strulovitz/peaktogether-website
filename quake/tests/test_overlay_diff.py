"""Headless tests for the pure helpers in tools/overlay_diff.py.

Must NOT import Tkinter or call run().
"""
from __future__ import annotations

import numpy as np

from tools.overlay_diff import binarize, transform, dilate, compose


# --------------------------------------------------------------------------- #
# Test 1: binarize — grey ramp + RGB
# --------------------------------------------------------------------------- #
def test_binarize_grey_ramp():
    ramp = np.arange(256, dtype=np.uint8).reshape(1, 256)
    mask = binarize(ramp, 128)

    assert mask.shape == (1, 256)
    assert mask.dtype == bool
    # pixels < 128 are True, >= 128 are False
    assert mask[0, 0] == True
    assert mask[0, 127] == True
    assert mask[0, 128] == False
    assert mask[0, 255] == False
    assert np.array_equal(mask, ramp < 128)


def test_binarize_rgb():
    dark = np.array([[[30, 30, 30]]], dtype=np.uint8)
    light = np.array([[[200, 200, 200]]], dtype=np.uint8)

    assert binarize(dark, 128).shape == (1, 1)
    assert binarize(dark, 128)[0, 0] == True
    assert binarize(light, 128)[0, 0] == False


# --------------------------------------------------------------------------- #
# Test 2: transform — 90° rotation
# --------------------------------------------------------------------------- #
def test_transform_rotate_90():
    mask = np.zeros((10, 10), dtype=bool)
    mask[:, 2] = True  # a vertical column at x=2
    n_in = int(mask.sum())

    out = transform(mask, tx=0, ty=0, scale=1.0, rot_deg=90)

    assert out.shape == mask.shape
    assert out.dtype == bool
    # Pixel count approximately preserved.
    assert abs(int(out.sum()) - n_in) <= 2

    # The column of True should become a horizontal row.
    rows_with_true = np.where(out.any(axis=1))[0]
    # All True pixels should lie in (about) a single row.
    assert len(rows_with_true) <= 2
    # That row should be near y=2 or y=7 (center-of-rotation dependent, but a
    # single row regardless). Confirm it's a row, not a column:
    cols_with_true = np.where(out.any(axis=0))[0]
    assert len(cols_with_true) >= 8  # spans most of the width like a row


# --------------------------------------------------------------------------- #
# Test 3: dilate — expands mask
# --------------------------------------------------------------------------- #
def test_dilate_px1():
    mask = np.zeros((10, 10), dtype=bool)
    mask[5, 5] = True

    out = dilate(mask, px=1)
    assert out.shape == mask.shape
    assert out.dtype == bool
    # 3x3 block around (5,5)
    expected = np.zeros((10, 10), dtype=bool)
    expected[4:7, 4:7] = True
    assert np.array_equal(out, expected)


def test_dilate_px2():
    mask = np.zeros((10, 10), dtype=bool)
    mask[5, 5] = True

    out = dilate(mask, px=2)
    expected = np.zeros((10, 10), dtype=bool)
    expected[3:8, 3:8] = True
    assert np.array_equal(out, expected)


def test_dilate_px0_noop():
    mask = np.zeros((10, 10), dtype=bool)
    mask[5, 5] = True
    assert np.array_equal(dilate(mask, px=0), mask)


# --------------------------------------------------------------------------- #
# Test 4: compose — back-only mismatch shows white
# --------------------------------------------------------------------------- #
def test_compose_back_only_white():
    back = np.zeros((5, 5), dtype=bool)
    back[:, 2] = True
    front = np.zeros((5, 5), dtype=bool)

    out = compose(back, front)
    assert out.shape == (5, 5)
    assert out.dtype == np.uint8

    # column 2 is white
    assert np.all(out[:, 2] == 255)
    # everything else grey
    rest = out.copy()
    rest[:, 2] = 128
    assert np.all(rest == 128)
    # no black pixels
    assert not np.any(out == 0)


# --------------------------------------------------------------------------- #
# Test 5: compose — front covers back
# --------------------------------------------------------------------------- #
def test_compose_front_covers_back():
    back = np.ones((5, 5), dtype=bool)
    front = np.zeros((5, 5), dtype=bool)
    front[2, 2] = True

    out = compose(back, front)
    # (2,2) is black — front covers
    assert out[2, 2] == 0
    # all other pixels are white shine-through
    others = out.copy()
    others[2, 2] = 255
    assert np.all(others == 255)


# --------------------------------------------------------------------------- #
# Test 6: compose — thicken makes near-miss vanish
# --------------------------------------------------------------------------- #
def test_compose_thicken_vanishes_near_miss():
    back = np.zeros((5, 5), dtype=bool)
    back[:, 2] = True
    front = np.zeros((5, 5), dtype=bool)
    front[:, 3] = True

    # Without thickening: col 2 white (mismatch), col 3 black.
    out = compose(back, front)
    assert np.all(out[:, 2] == 255)
    assert np.all(out[:, 3] == 0)

    # After dilating front by 1 px, it covers column 2.
    dilated = dilate(front, px=1)
    out2 = compose(back, dilated)
    assert np.all(out2[:, 2] == 0)   # near-miss now covered (black)
    assert not np.any(out2 == 255)   # no white mismatch remains
