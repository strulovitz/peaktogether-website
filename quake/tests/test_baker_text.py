from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from map.raw_models import TextBlock, Palette, GroupColor, AssetEntry
from bake.baker_text import bake, BakerTextConfig, _hex_to_rgb
from bake.asy_compile import AsyResult, AsyConfig


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

VERBATIM_TEXT = TextBlock(
    block_id="prop_1.s3.txt",
    latex=r"Newton shows that \cg{radius}{$CP$} is to \cg{path}{$AP$} as \dots",
    groups_used=["radius", "path"],
)


def make_palette() -> Palette:
    return Palette(
        schema_version="1.0",
        pack_id="test",
        groups={
            "radius": GroupColor(hi="#FFCCCC", ink="#CC3333"),
            "path": GroupColor(hi="#CCCCFF", ink="#3366CC"),
        },
        grey_ink="#888888",
        grey_text="#AAAAAA",
        bg_key="#FF00FF",
        map_importance={
            "1": "#111111", "2": "#222222", "3": "#333333",
            "4": "#444444", "5": "#555555",
        },
        map_node_default="#666666",
    )


def _make_bordered_png(path: Path, w: int = 40, h: int = 24) -> None:
    """Canned PNG: magenta (bg_key) border with an opaque interior block."""
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    # Fill everything with magenta-keyed background, fully opaque.
    arr[:, :, 0] = 0xFF
    arr[:, :, 1] = 0x00
    arr[:, :, 2] = 0xFF
    arr[:, :, 3] = 0xFF
    # Opaque "content" block in the middle (non-magenta).
    arr[6 : h - 6, 6 : w - 6, 0] = 0x10
    arr[6 : h - 6, 6 : w - 6, 1] = 0x20
    arr[6 : h - 6, 6 : w - 6, 2] = 0x30
    arr[6 : h - 6, 6 : w - 6, 3] = 0xFF
    Image.fromarray(arr).save(path)


def make_fake_compile(record: list | None = None):
    """Return a compile_fn that writes a canned PNG and optionally records args."""

    def _compile(src: Path, out_stem: Path, params: dict, cfg: AsyConfig):
        if record is not None:
            record.append((Path(src), Path(out_stem), dict(params), cfg.dpi))
        out_stem = Path(out_stem)
        if cfg.dpi >= 440:
            png = out_stem.parent / f"{out_stem.name}@master.png"
        else:
            png = out_stem.parent / f"{out_stem.name}.png"
        _make_bordered_png(png)
        return AsyResult(ok=True, outputs=[png], stderr="", stdout="")

    return _compile


def make_failing_compile():
    def _compile(src: Path, out_stem: Path, params: dict, cfg: AsyConfig):
        return AsyResult(ok=False, outputs=[], stderr="tectonic blew up", stdout="")

    return _compile


# --------------------------------------------------------------------------
# Test 1: group in latex but NOT in groups_used
# --------------------------------------------------------------------------

def test_validation_undeclared_group(tmp_path):
    tb = TextBlock(
        block_id="b.s1.txt",
        latex=r"see \cg{ghost}{x}",
        groups_used=[],
    )
    with pytest.raises(ValueError, match="ghost"):
        bake(tb, make_palette(), tmp_path, BakerTextConfig(),
             compile_fn=make_fake_compile())


# --------------------------------------------------------------------------
# Test 2: group in groups_used but NOT in palette
# --------------------------------------------------------------------------

def test_validation_group_not_in_palette(tmp_path):
    tb = TextBlock(
        block_id="b.s1.txt",
        latex=r"see \cg{ghost}{x}",
        groups_used=["ghost"],
    )
    with pytest.raises(ValueError, match="ghost"):
        bake(tb, make_palette(), tmp_path, BakerTextConfig(),
             compile_fn=make_fake_compile())


# --------------------------------------------------------------------------
# Test 3: OFF tex overrides \cg to grey_text
# --------------------------------------------------------------------------

def test_off_tex_overrides_cg_grey(tmp_path):
    record: list = []
    bake(VERBATIM_TEXT, make_palette(), tmp_path, BakerTextConfig(),
         compile_fn=make_fake_compile(record))

    off_tex = (tmp_path / "prop_1.s3.txt.off.tex").read_text(encoding="utf-8")
    assert r"\renewcommand{\cg}[2]{{\color{grey_text}#2}}" in off_tex
    assert r"\renewcommand{\cg}[2]{{\color{#1}#2}}" not in off_tex


# --------------------------------------------------------------------------
# Test 4: ON tex uses standard \cg from palette.tex
# --------------------------------------------------------------------------

def test_on_tex_uses_standard_cg(tmp_path):
    bake(VERBATIM_TEXT, make_palette(), tmp_path, BakerTextConfig(),
         compile_fn=make_fake_compile())

    on_tex = (tmp_path / "prop_1.s3.txt.on.tex").read_text(encoding="utf-8")
    assert r"\newcommand{\cg}[2]{{\color{#1}#2}}" in on_tex
    assert r"\renewcommand{\cg}[2]{{\color{grey_text}#2}}" not in on_tex


# --------------------------------------------------------------------------
# Test 5: output — 2 AssetEntries with correct ids + kinds
# --------------------------------------------------------------------------

def test_output_entries(tmp_path):
    entries = bake(VERBATIM_TEXT, make_palette(), tmp_path, BakerTextConfig(),
                   compile_fn=make_fake_compile())

    assert len(entries) == 2
    off, on = entries
    assert isinstance(off, AssetEntry) and isinstance(on, AssetEntry)

    assert off.asset_id == "prop_1.s3.txt.off"
    assert off.kind == "text_off"
    assert off.wall_path == "assets/prop_1.s3.txt.off.png"
    assert off.master_path == "assets/prop_1.s3.txt.off@master.png"

    assert on.asset_id == "prop_1.s3.txt.on"
    assert on.kind == "text_on"
    assert on.wall_path == "assets/prop_1.s3.txt.on.png"
    assert on.master_path == "assets/prop_1.s3.txt.on@master.png"

    assert off.px_w > 0 and off.px_h > 0
    assert off.content_bbox is not None
    assert off.dpi == 220


# --------------------------------------------------------------------------
# Test 6: compile failure raises RuntimeError
# --------------------------------------------------------------------------

def test_compile_failure(tmp_path):
    with pytest.raises(RuntimeError, match="tectonic blew up"):
        bake(VERBATIM_TEXT, make_palette(), tmp_path, BakerTextConfig(),
             compile_fn=make_failing_compile())
