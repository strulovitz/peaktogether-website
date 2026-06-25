from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image
from pydantic import BaseModel, ConfigDict

from bake._imageops import key_out as imageops_key_out, content_bbox, trim
from bake.asy_compile import compile as default_compile, AsyConfig
from map.raw_models import AssetEntry, FigureId, Palette, Hex


class BakerFigureConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    wall_dpi: int = 220
    master_dpi: int = 440
    alpha_threshold: int = 16
    trim_padding_px: int = 8


def _hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    s = hex_str.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def _load_rgba(path: Path) -> np.ndarray:
    with Image.open(path) as im:
        return np.array(im.convert("RGBA"))


def _save_rgba(arr: np.ndarray, path: Path) -> None:
    Image.fromarray(arr, "RGBA").save(path)


def _render(
    compile_fn,
    figure_asy: Path,
    out_stem: Path,
    params: dict[str, str],
    cfg: AsyConfig,
) -> Path:
    result = compile_fn(figure_asy, out_stem, params, cfg)
    if not result.ok:
        raise RuntimeError(result.stderr)
    return Path(result.outputs[0])


def bake(
    figure_asy: Path,
    figure_id: FigureId,
    n_steps: int,
    out_dir: Path,
    palette: Palette,
    cfg: BakerFigureConfig,
    *,
    compile_fn=default_compile,
) -> list[AssetEntry]:
    out_dir.mkdir(parents=True, exist_ok=True)

    key_rgb = _hex_to_rgb(palette.bg_key)

    wall_cfg = AsyConfig(dpi=cfg.wall_dpi)
    master_cfg = AsyConfig(dpi=cfg.master_dpi)

    def process(
        wall_stem: Path,
        master_stem: Path,
        params: dict[str, str],
        wall_png_out: Path,
        master_png_out: Path,
    ) -> tuple[int, int, tuple[int, int, int, int]]:
        # Wall tier
        wall_out = _render(compile_fn, figure_asy, wall_stem, params, wall_cfg)
        wall_arr = _load_rgba(wall_out)
        keyed = imageops_key_out(wall_arr, key_rgb, cfg.alpha_threshold)
        bbox = content_bbox(keyed)
        trimmed = trim(keyed, cfg.trim_padding_px)
        px_h, px_w = trimmed.shape[0], trimmed.shape[1]
        _save_rgba(trimmed, wall_png_out)

        # Master tier
        master_out = _render(compile_fn, figure_asy, master_stem, params, master_cfg)
        master_arr = _load_rgba(master_out)
        master_keyed = imageops_key_out(master_arr, key_rgb, cfg.alpha_threshold)
        master_trimmed = trim(master_keyed, cfg.trim_padding_px)
        _save_rgba(master_trimmed, master_png_out)

        return px_w, px_h, bbox

    entries: list[AssetEntry] = []

    # --- OFF ---
    off_wall_stem = out_dir / f"{figure_id}.off"
    off_master_stem = out_dir / f"{figure_id}.off@master"
    off_wall_png = out_dir / f"{figure_id}.off.png"
    off_master_png = out_dir / f"{figure_id}.off@master.png"

    px_w, px_h, bbox = process(
        off_wall_stem,
        off_master_stem,
        {"highlight": "-1"},
        off_wall_png,
        off_master_png,
    )

    entries.append(
        AssetEntry(
            asset_id=f"{figure_id}.off",
            kind="figure_off",
            wall_path=f"assets/{figure_id}.off.png",
            master_path=f"assets/{figure_id}.off@master.png",
            px_w=px_w,
            px_h=px_h,
            content_bbox=bbox,
            dpi=cfg.wall_dpi,
        )
    )

    # --- ON for each step ---
    for k in range(1, n_steps + 1):
        on_wall_stem = out_dir / f"{figure_id}.on.{k}"
        on_master_stem = out_dir / f"{figure_id}.on.{k}@master"
        on_wall_png = out_dir / f"{figure_id}.on.{k}.png"
        on_master_png = out_dir / f"{figure_id}.on.{k}@master.png"

        px_w, px_h, bbox = process(
            on_wall_stem,
            on_master_stem,
            {"highlight": str(k)},
            on_wall_png,
            on_master_png,
        )

        entries.append(
            AssetEntry(
                asset_id=f"{figure_id}.on.{k}",
                kind="figure_on",
                wall_path=f"assets/{figure_id}.on.{k}.png",
                master_path=f"assets/{figure_id}.on.{k}@master.png",
                px_w=px_w,
                px_h=px_h,
                content_bbox=bbox,
                dpi=cfg.wall_dpi,
            )
        )

    return entries
