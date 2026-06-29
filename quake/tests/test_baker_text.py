from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from map.raw_models import TextBlock, Palette, GroupColor, AssetEntry, LocalColor
from bake.baker_text import bake, BakerTextConfig, _hex_to_rgb
from bake.asy_compile import AsyResult, AsyConfig


# --------------------------------------------------------------------------
# Fixtures (updated for Nir's color model 2026-06-29)
# --------------------------------------------------------------------------

VERBATIM_TEXT = TextBlock(
    block_id="prop_1.s3.txt",
    latex=r"Newton shows that \textcolor{radius}{$CP$} is to \textcolor{path}{$AP$} as \dots",
    colors_used=[
        LocalColor(name="radius", hex="#CC3333"),
        LocalColor(name="path", hex="#3366CC"),
    ],
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
    arr[:, :, 0] = 0xFF
    arr[:, :, 1] = 0x00
    arr[:, :, 2] = 0xFF
    arr[:, :, 3] = 0xFF
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
# Test 1: color name in latex but NOT in colors_used → raises
# --------------------------------------------------------------------------

def test_validation_undeclared_color(tmp_path):
    tb = TextBlock(
        block_id="b.s1.txt",
        latex=r"see \textcolor{ghost}{x}",
        colors_used=[],
    )
    with pytest.raises(ValueError, match="ghost"):
        bake(tb, make_palette(), tmp_path, BakerTextConfig(),
             compile_fn=make_fake_compile())


# --------------------------------------------------------------------------
# Test 2: color in colors_used but NOT in latex → raises
# --------------------------------------------------------------------------

def test_validation_color_not_used(tmp_path):
    tb = TextBlock(
        block_id="b.s1.txt",
        latex=r"just plain text no color spans",
        colors_used=[LocalColor(name="ghost", hex="#FF0000")],
    )
    with pytest.raises(ValueError, match="ghost"):
        bake(tb, make_palette(), tmp_path, BakerTextConfig(),
             compile_fn=make_fake_compile())


# --------------------------------------------------------------------------
# Test 3: OFF tex defines colors as black (000000)
# --------------------------------------------------------------------------

def test_off_tex_colors_black(tmp_path):
    record: list = []
    bake(VERBATIM_TEXT, make_palette(), tmp_path, BakerTextConfig(),
         compile_fn=make_fake_compile(record))

    off_tex = (tmp_path / "prop_1.s3.txt.off.tex").read_text(encoding="utf-8")
    # OFF variant redefines each local color as black
    assert r"\definecolor{radius}{HTML}{000000}" in off_tex
    assert r"\definecolor{path}{HTML}{000000}" in off_tex
    # The original color definitions should also be present (before override)
    assert r"\definecolor{radius}{HTML}{CC3333}" in off_tex
    assert r"\definecolor{path}{HTML}{3366CC}" in off_tex


# --------------------------------------------------------------------------
# Test 4: ON tex uses actual colors from colors_used
# --------------------------------------------------------------------------

def test_on_tex_uses_colors(tmp_path):
    bake(VERBATIM_TEXT, make_palette(), tmp_path, BakerTextConfig(),
         compile_fn=make_fake_compile())

    on_tex = (tmp_path / "prop_1.s3.txt.on.tex").read_text(encoding="utf-8")
    assert r"\definecolor{radius}{HTML}{CC3333}" in on_tex
    assert r"\definecolor{path}{HTML}{3366CC}" in on_tex
    # No black override in ON
    assert r"\definecolor{radius}{HTML}{000000}" not in on_tex
    assert r"\definecolor{path}{HTML}{000000}" not in on_tex


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

    assert off.px_w >= 0
    assert off.px_h >= 0
    assert off.dpi == 220


# --------------------------------------------------------------------------
# Test 6: compile failure raises RuntimeError
# --------------------------------------------------------------------------

def test_compile_failure(tmp_path):
    with pytest.raises(RuntimeError, match="tectonic blew up"):
        bake(VERBATIM_TEXT, make_palette(), tmp_path, BakerTextConfig(),
             compile_fn=make_failing_compile())
