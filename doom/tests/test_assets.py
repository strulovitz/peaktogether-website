from __future__ import annotations

import pytest
from PIL import Image

from principia.assets.manager import AssetManager

PACK = "content_packs/principia"


def test_resolve_image_placeholder_size_and_off_on_differ() -> None:
    am = AssetManager(PACK)

    # l1_step1 is in the manifest (1024x1024) but its PNGs don't exist on disk.
    off = am._resolve_image("png/l1_step1_off.png", "l1_step1", on=False)
    on = am._resolve_image("png/l1_step1_on.png", "l1_step1", on=True)

    assert isinstance(off, Image.Image)
    assert isinstance(on, Image.Image)
    assert off.size == (1024, 1024)
    assert on.size == (1024, 1024)
    assert off.tobytes() != on.tobytes()


def test_unknown_block_placeholder_default_size() -> None:
    am = AssetManager(PACK)
    img = am._resolve_image("", "totally_unknown_block", on=False)
    assert isinstance(img, Image.Image)
    assert img.size == (1024, 1024)


def test_wall_textures_cached() -> None:
    am = AssetManager(PACK)
    try:
        off, on = am.wall_textures("l1_step1")
    except Exception as exc:  # no display / Ursina unavailable in headless CI
        pytest.skip(f"Ursina/Texture unavailable: {exc}")

    assert off is not on
    off2, on2 = am.wall_textures("l1_step1")
    assert off2 is off
    assert on2 is on
