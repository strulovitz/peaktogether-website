from __future__ import annotations

import numpy as np

from bake._imageops import key_out, content_bbox, trim


MAGENTA = (255, 0, 255)


def test_key_out_magenta_transparent_black_opaque():
    img = np.zeros((4, 4, 3), dtype=np.uint8)
    # two magenta pixels
    img[0, 0] = (255, 0, 255)
    img[0, 1] = (255, 0, 255)
    # two black pixels
    img[1, 0] = (0, 0, 0)
    img[1, 1] = (0, 0, 0)

    out = key_out(img, key_rgb=MAGENTA, threshold=16)

    assert out.shape == (4, 4, 4)
    assert out.dtype == np.uint8
    # magenta -> transparent
    assert out[0, 0, 3] == 0
    assert out[0, 1, 3] == 0
    # black -> opaque
    assert out[1, 0, 3] == 255
    assert out[1, 1, 3] == 255


def test_key_out_threshold_tolerance():
    img = np.zeros((1, 1, 3), dtype=np.uint8)
    img[0, 0] = (255, 10, 250)  # dist to magenta ≈ 11.18

    out_in = key_out(img, key_rgb=MAGENTA, threshold=12)
    assert out_in[0, 0, 3] == 0

    out_out = key_out(img, key_rgb=MAGENTA, threshold=10)
    assert out_out[0, 0, 3] == 255


def test_key_out_rgba_input_preserved():
    img = np.zeros((2, 2, 4), dtype=np.uint8)
    img[..., 3] = 128
    img[0, 0, :3] = (255, 0, 255)  # magenta
    img[0, 1, :3] = (0, 0, 0)      # black

    out = key_out(img, key_rgb=MAGENTA, threshold=16)

    assert out.shape == (2, 2, 4)
    # magenta keyed out
    assert out[0, 0, 3] == 0
    # non-magenta keep original alpha
    assert out[0, 1, 3] == 128
    assert out[1, 0, 3] == 128
    assert out[1, 1, 3] == 128
    # input not mutated
    assert img[0, 0, 3] == 128


def test_key_out_does_not_mutate_input():
    img = np.zeros((1, 1, 4), dtype=np.uint8)
    img[..., 3] = 255
    img[0, 0, :3] = (255, 0, 255)
    snapshot = img.copy()

    key_out(img, key_rgb=MAGENTA, threshold=16)

    assert np.array_equal(img, snapshot)


def test_content_bbox_single_pixel():
    rgba = np.zeros((10, 10, 4), dtype=np.uint8)
    rgba[3, 5, 3] = 255  # y=3, x=5

    assert content_bbox(rgba) == (5, 3, 6, 4)


def test_content_bbox_rectangle():
    rgba = np.zeros((10, 10, 4), dtype=np.uint8)
    # x in 3..6, y in 4..7
    rgba[4:8, 3:7, 3] = 255

    assert content_bbox(rgba) == (3, 4, 7, 8)


def test_content_bbox_fully_transparent():
    rgba = np.zeros((10, 10, 4), dtype=np.uint8)
    assert content_bbox(rgba) == (0, 0, 0, 0)


def test_trim_basic_crop():
    rgba = np.zeros((10, 10, 4), dtype=np.uint8)
    # opaque column at x=3, y from 1 to 8 inclusive
    rgba[1:9, 3, 3] = 255
    # give those pixels distinct rgb to verify value match
    rgba[1:9, 3, 0] = 77

    bbox = content_bbox(rgba)
    assert bbox == (3, 1, 4, 9)

    out = trim(rgba, padding=0)
    assert out.shape == (8, 1, 4)
    assert np.array_equal(out, rgba[1:9, 3:4])


def test_trim_with_padding():
    rgba = np.zeros((10, 10, 4), dtype=np.uint8)
    rgba[1:9, 3, 3] = 255  # bbox (3, 1, 4, 9)

    out = trim(rgba, padding=2)
    # padded bbox (1, -1, 6, 11) -> clamped (1, 0, 6, 10)
    assert out.shape == (10, 5, 4)
    assert np.array_equal(out, rgba[0:10, 1:6])


def test_trim_fully_transparent_unchanged():
    rgba = np.zeros((10, 10, 4), dtype=np.uint8)
    out = trim(rgba, padding=3)
    assert out.shape == (10, 10, 4)
    assert np.array_equal(out, rgba)
    # spec says return the original array unchanged
    assert out is rgba


def test_trim_does_not_mutate_input():
    rgba = np.zeros((10, 10, 4), dtype=np.uint8)
    rgba[2:5, 2:5, 3] = 255
    snapshot = rgba.copy()

    out = trim(rgba, padding=1)
    out[0, 0, 0] = 200  # mutate the crop

    assert np.array_equal(rgba, snapshot)
