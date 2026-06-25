from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from bake.baker_figure import bake, BakerFigureConfig, _hex_to_rgb
from bake.asy_compile import AsyResult, AsyConfig
from map.raw_models import Palette, GroupColor


VERBATIM_PALETTE = Palette(
    schema_version="1.0",
    pack_id="principia",
    groups={
        "path": GroupColor(hi="#FFE08A", ink="#E8A200"),
        "radius": GroupColor(hi="#A8D8FF", ink="#1E6FE0"),
    },
    grey_ink="#7A7A7A",
    grey_text="#8A8A8A",
    bg_key="#FF00FF",
    map_importance={
        "1": "#4F6D7A",
        "2": "#3FA796",
        "3": "#E6B800",
        "4": "#E8743B",
        "5": "#F5F2E8",
    },
    map_node_default="#9AA0A6",
)


def _make_magenta_png(path: Path, w: int = 50, h: int = 40) -> None:
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    arr[..., 0] = 255
    arr[..., 1] = 0
    arr[..., 2] = 255
    arr[..., 3] = 255
    Image.fromarray(arr, "RGBA").save(path)


def _make_bordered_png(path: Path, w: int = 50, h: int = 40) -> None:
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    # magenta everywhere
    arr[..., 0] = 255
    arr[..., 1] = 0
    arr[..., 2] = 255
    arr[..., 3] = 255
    # black rectangle x=12..37, y=10..29 inclusive
    arr[10:30, 12:38, 0] = 0
    arr[10:30, 12:38, 1] = 0
    arr[10:30, 12:38, 2] = 0
    arr[10:30, 12:38, 3] = 255
    Image.fromarray(arr, "RGBA").save(path)


def _make_recording_compile(png_writer):
    calls = []

    def fake_compile(src: Path, out_stem: Path, params: dict, cfg: AsyConfig):
        out_path = Path(f"{out_stem}.png")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        png_writer(out_path)
        calls.append(
            {
                "src": src,
                "out_stem": Path(out_stem),
                "params": dict(params),
                "dpi": cfg.dpi,
                "out_path": out_path,
            }
        )
        return AsyResult(ok=True, outputs=[out_path], stderr="", stdout="")

    return fake_compile, calls


def test_n_steps_3_counts(tmp_path):
    fake_compile, calls = _make_recording_compile(_make_magenta_png)

    entries = bake(
        figure_asy=tmp_path / "fig.asy",
        figure_id="prop_1.f1",
        n_steps=3,
        out_dir=tmp_path,
        palette=VERBATIM_PALETTE,
        cfg=BakerFigureConfig(),
        compile_fn=fake_compile,
    )

    assert len(entries) == 4

    # 8 total calls: off×2 + on×6
    assert len(calls) == 8

    dpis = [c["dpi"] for c in calls]
    assert dpis.count(220) == 4
    assert dpis.count(440) == 4

    highlights = [c["params"]["highlight"] for c in calls]
    assert highlights.count("-1") == 2
    assert highlights.count("1") == 2
    assert highlights.count("2") == 2
    assert highlights.count("3") == 2

    off = entries[0]
    assert off.kind == "figure_off"
    assert off.asset_id == "prop_1.f1.off"

    on2 = entries[2]
    assert on2.kind == "figure_on"
    assert on2.asset_id == "prop_1.f1.on.2"


def test_keyout_and_trim(tmp_path):
    fake_compile, _calls = _make_recording_compile(_make_bordered_png)

    entries = bake(
        figure_asy=tmp_path / "fig.asy",
        figure_id="prop_1.f1",
        n_steps=1,
        out_dir=tmp_path,
        palette=VERBATIM_PALETTE,
        cfg=BakerFigureConfig(),
        compile_fn=fake_compile,
    )

    off = entries[0]
    assert off.content_bbox == (12, 10, 38, 30)

    wall_png = tmp_path / "prop_1.f1.off.png"
    assert wall_png.exists()

    with Image.open(wall_png) as im:
        arr = np.array(im.convert("RGBA"))
    assert arr.shape[2] == 4

    # Content rectangle is 26x20; with padding 8 → 42x36
    assert off.px_w == 26 + 2 * 8
    assert off.px_h == 20 + 2 * 8

    # interior black pixels remain opaque; any magenta is transparent
    # the trimmed image's padding region should be transparent
    assert arr[0, 0, 3] == 0


def test_compile_failure_raises(tmp_path):
    def fake_compile(src, out_stem, params, cfg):
        return AsyResult(ok=False, outputs=[], stderr="Asymptote error", stdout="")

    with pytest.raises(RuntimeError, match="Asymptote error"):
        bake(
            figure_asy=tmp_path / "fig.asy",
            figure_id="prop_1.f1",
            n_steps=1,
            out_dir=tmp_path,
            palette=VERBATIM_PALETTE,
            cfg=BakerFigureConfig(),
            compile_fn=fake_compile,
        )


def test_output_path_grammar(tmp_path):
    fake_compile, _calls = _make_recording_compile(_make_magenta_png)

    entries = bake(
        figure_asy=tmp_path / "fig.asy",
        figure_id="prop_1.f1",
        n_steps=3,
        out_dir=tmp_path,
        palette=VERBATIM_PALETTE,
        cfg=BakerFigureConfig(),
        compile_fn=fake_compile,
    )

    off = entries[0]
    assert off.wall_path == "assets/prop_1.f1.off.png"
    assert off.master_path == "assets/prop_1.f1.off@master.png"

    on3 = entries[3]
    assert on3.asset_id == "prop_1.f1.on.3"
    assert on3.wall_path == "assets/prop_1.f1.on.3.png"


def test_hex_to_rgb():
    assert _hex_to_rgb("#FF00FF") == (255, 0, 255)
    assert _hex_to_rgb("#000000") == (0, 0, 0)
    assert _hex_to_rgb("E8A200") == (232, 162, 0)
