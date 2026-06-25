"""
Text block baker — wraps LaTeX in standalone template, compiles via injected
compile_fn (Tectonic), keys out bg, trims, emits text_off/text_on AssetEntries.

Key design notes:
- Both .tex sources include the full palette.tex content (\\definecolor for
  every group + standard \\newcommand{\\cg}). The OFF variant appends a
  \\renewcommand{\\cg}[2]{{\\color{grey_text}#2}} AFTER the palette content,
  so the active definition ignores the group argument and renders all in
  grey_text. The ON variant adds no override — the standard colored \\cg wins.
- compile_fn writes wall-tier (dpi < 440) to <stem>.png and master-tier
  (dpi >= 440) to <stem>@master.png; both tiers are invoked from the same stem.
  Wall is called first so <stem>.png exists for bbox computation.
- Validation runs before any directory creation or compilation — clean
  fail-fast without side effects.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
from PIL import Image
from pydantic import BaseModel, ConfigDict

from map.raw_models import TextBlock, Palette, AssetEntry, GroupName
from bake import _imageops
from bake.asy_compile import AsyConfig


CG_RE = re.compile(r"\\cg\{([^}]+)\}\{")


class BakerTextConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    wall_dpi: int = 220
    master_dpi: int = 440
    alpha_threshold: int = 16
    trim_padding_px: int = 8
    preamble: str = ""


def _hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    s = hex_str.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def _palette_tex(palette: Palette) -> str:
    """Render palette.tex content: \\definecolor lines + standard \\cg macro."""
    lines: list[str] = []
    for group, color in palette.groups.items():
        hexv = color.ink.lstrip("#")
        lines.append(rf"\definecolor{{{group}}}{{HTML}}{{{hexv}}}")
    lines.append(
        rf"\definecolor{{grey_text}}{{HTML}}{{{palette.grey_text.lstrip('#')}}}"
    )
    lines.append(r"\newcommand{\cg}[2]{{\color{#1}#2}}")
    return "\n".join(lines)


def _wrap_tex(
    text_block: TextBlock,
    palette: Palette,
    *,
    for_off: bool,
    cfg_preamble: str,
) -> str:
    """Build the full standalone .tex source for OFF (grey) or ON (colored)."""
    parts: list[str] = []
    parts.append(r"\documentclass{standalone}")
    parts.append(r"\usepackage{amsmath,amssymb,mathtools,xcolor,varwidth}")
    parts.append(_palette_tex(palette))
    if cfg_preamble:
        parts.append(cfg_preamble)
    if for_off:
        parts.append(r"\renewcommand{\cg}[2]{{\color{grey_text}#2}}")
    parts.append(r"\begin{document}")
    parts.append(r"\begin{varwidth}{\maxdimen}")
    parts.append(text_block.latex)
    parts.append(r"\end{varwidth}")
    parts.append(r"\end{document}")
    return "\n".join(parts) + "\n"


def _validate(text_block: TextBlock, palette: Palette) -> None:
    used_in_latex = set(CG_RE.findall(text_block.latex))
    declared = set(text_block.groups_used)

    for g in used_in_latex:
        if g not in declared:
            raise ValueError(
                f"group '{g}' appears in \\cg span but is not listed in groups_used"
            )

    for g in text_block.groups_used:
        if g not in palette.groups:
            raise ValueError(
                f"group '{g}' in groups_used does not exist in palette.groups"
            )


def _key_trim_save(
    src_png: Path,
    out_png: Path,
    bg_rgb: tuple[int, int, int],
    cfg: BakerTextConfig,
    *,
    want_bbox: bool,
):
    arr = np.array(Image.open(src_png).convert("RGBA"))
    keyed = _imageops.key_out(arr, bg_rgb, cfg.alpha_threshold)
    bbox = _imageops.content_bbox(keyed) if want_bbox else None
    trimmed = _imageops.trim(keyed, cfg.trim_padding_px)
    Image.fromarray(trimmed).save(out_png)
    h, w = trimmed.shape[0], trimmed.shape[1]
    return bbox, w, h


def bake(
    text_block: TextBlock,
    palette: Palette,
    out_dir: Path,
    cfg: BakerTextConfig,
    *,
    compile_fn,
) -> list[AssetEntry]:
    _validate(text_block, palette)

    out_dir.mkdir(parents=True, exist_ok=True)
    block_id = text_block.block_id
    bg_rgb = _hex_to_rgb(palette.bg_key)

    # --- Write tex sources ---
    off_tex = out_dir / f"{block_id}.off.tex"
    on_tex = out_dir / f"{block_id}.on.tex"
    off_tex.write_text(
        _wrap_tex(text_block, palette, for_off=True, cfg_preamble=cfg.preamble),
        encoding="utf-8",
    )
    on_tex.write_text(
        _wrap_tex(text_block, palette, for_off=False, cfg_preamble=cfg.preamble),
        encoding="utf-8",
    )

    # --- Compile OFF (wall + master) ---
    off_stem = out_dir / f"{block_id}.off"
    result = compile_fn(off_tex, off_stem, {}, AsyConfig(dpi=cfg.wall_dpi))
    if not result.ok:
        raise RuntimeError(result.stderr)
    result = compile_fn(off_tex, off_stem, {}, AsyConfig(dpi=cfg.master_dpi))
    if not result.ok:
        raise RuntimeError(result.stderr)

    # --- Compile ON (wall + master) ---
    on_stem = out_dir / f"{block_id}.on"
    result = compile_fn(on_tex, on_stem, {}, AsyConfig(dpi=cfg.wall_dpi))
    if not result.ok:
        raise RuntimeError(result.stderr)
    result = compile_fn(on_tex, on_stem, {}, AsyConfig(dpi=cfg.master_dpi))
    if not result.ok:
        raise RuntimeError(result.stderr)

    # --- Key out + trim OFF ---
    off_bbox, off_w, off_h = _key_trim_save(
        out_dir / f"{block_id}.off.png",
        out_dir / f"{block_id}.off.png",
        bg_rgb,
        cfg,
        want_bbox=True,
    )
    _key_trim_save(
        out_dir / f"{block_id}.off@master.png",
        out_dir / f"{block_id}.off@master.png",
        bg_rgb,
        cfg,
        want_bbox=False,
    )

    # --- Key out + trim ON ---
    on_bbox, on_w, on_h = _key_trim_save(
        out_dir / f"{block_id}.on.png",
        out_dir / f"{block_id}.on.png",
        bg_rgb,
        cfg,
        want_bbox=True,
    )
    _key_trim_save(
        out_dir / f"{block_id}.on@master.png",
        out_dir / f"{block_id}.on@master.png",
        bg_rgb,
        cfg,
        want_bbox=False,
    )

    off_entry = AssetEntry(
        asset_id=f"{block_id}.off",
        kind="text_off",
        wall_path=f"assets/{block_id}.off.png",
        master_path=f"assets/{block_id}.off@master.png",
        px_w=off_w,
        px_h=off_h,
        content_bbox=off_bbox,
        dpi=cfg.wall_dpi,
    )
    on_entry = AssetEntry(
        asset_id=f"{block_id}.on",
        kind="text_on",
        wall_path=f"assets/{block_id}.on.png",
        master_path=f"assets/{block_id}.on@master.png",
        px_w=on_w,
        px_h=on_h,
        content_bbox=on_bbox,
        dpi=cfg.wall_dpi,
    )
    return [off_entry, on_entry]
