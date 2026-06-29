"""
Text block baker — wraps LaTeX in standalone template, compiles via injected
compile_fn (Tectonic), keys out bg, trims, emits text_off/text_on AssetEntries.

⚠️ 2026-06-29 — UPDATED for Nir's color system:
- No global palette groups; no grey_text; no \\cg macro.
- Per-text-block local colors from `colors_used: list[LocalColor]`.
- LaTeX uses \\textcolor{name}{text} (standard xcolor) instead of \\cg{group}{text}.
- OFF bake: defines every local color as black (000000).
- ON bake: uses the actual hex from each LocalColor.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
from PIL import Image
from pydantic import BaseModel, ConfigDict

from map.raw_models import TextBlock, Palette, AssetEntry, LocalColor
from bake import _imageops
from bake.asy_compile import AsyConfig


# Matches \\textcolor{name}{...} spans in the LaTeX source.
TEXTCOLOR_RE = re.compile(r"\\textcolor\{([^}]+)\}\{")


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


def _colors_tex(text_block: TextBlock) -> str:
    """Generate \\definecolor lines from text_block.colors_used (per-station local colors)."""
    lines: list[str] = []
    for lc in text_block.colors_used:
        hexv = lc.hex.lstrip("#")
        lines.append(rf"\definecolor{{{lc.name}}}{{HTML}}{{{hexv}}}")
    return "\n".join(lines)


def _wrap_tex(
    text_block: TextBlock,
    *,
    for_off: bool,
    cfg_preamble: str,
) -> str:
    """Build the full standalone .tex source for OFF (all black) or ON (colored)."""
    parts: list[str] = []
    parts.append(r"\documentclass{standalone}")
    parts.append(r"\usepackage{amsmath,amssymb,mathtools,xcolor,varwidth}")
    parts.append(_colors_tex(text_block))
    if cfg_preamble:
        parts.append(cfg_preamble)
    if for_off:
        # Override each local color to black so text renders black.
        for lc in text_block.colors_used:
            parts.append(rf"\definecolor{{{lc.name}}}{{HTML}}{{000000}}")
    parts.append(r"\begin{document}")
    parts.append(r"\begin{varwidth}{\maxdimen}")
    parts.append(text_block.latex)
    parts.append(r"\end{varwidth}")
    parts.append(r"\end{document}")
    return "\n".join(parts) + "\n"


def _validate(text_block: TextBlock) -> None:
    """Check that every \\textcolor{name}{...} in the latex has its name in colors_used,
    and every colors_used entry appears in the latex."""
    used_in_latex = set(TEXTCOLOR_RE.findall(text_block.latex))
    declared = {lc.name for lc in text_block.colors_used}

    for name in used_in_latex:
        if name not in declared:
            raise ValueError(
                f"color name '{name}' appears in \\textcolor span but is not listed in colors_used"
            )

    for lc in text_block.colors_used:
        if lc.name not in used_in_latex:
            raise ValueError(
                f"color name '{lc.name}' in colors_used does not appear in any \\textcolor span"
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
    palette: Palette,             # still needed for bg_key (keyout color)
    out_dir: Path,
    cfg: BakerTextConfig,
    *,
    compile_fn,
) -> list[AssetEntry]:
    _validate(text_block)

    out_dir.mkdir(parents=True, exist_ok=True)
    block_id = text_block.block_id
    bg_rgb = _hex_to_rgb(palette.bg_key)

    # --- Write tex sources ---
    off_tex = out_dir / f"{block_id}.off.tex"
    on_tex = out_dir / f"{block_id}.on.tex"
    off_tex.write_text(
        _wrap_tex(text_block, for_off=True, cfg_preamble=cfg.preamble),
        encoding="utf-8",
    )
    on_tex.write_text(
        _wrap_tex(text_block, for_off=False, cfg_preamble=cfg.preamble),
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

    off_png = Path(str(off_stem) + ".png")
    if off_png.exists():
        _key_trim_save(
            off_png,
            out_dir / f"{block_id}.off.png",
            bg_rgb, cfg, want_bbox=True,
        )
        _key_trim_save(
            Path(str(off_stem) + "@master.png"),
            out_dir / f"{block_id}.off@master.png",
            bg_rgb, cfg, want_bbox=False,
        )

    on_png = Path(str(on_stem) + ".png")
    if on_png.exists():
        _key_trim_save(
            on_png,
            out_dir / f"{block_id}.on.png",
            bg_rgb, cfg, want_bbox=True,
        )
        _key_trim_save(
            Path(str(on_stem) + "@master.png"),
            out_dir / f"{block_id}.on@master.png",
            bg_rgb, cfg, want_bbox=False,
        )

    off_bbox = None
    off_w, off_h = 0, 0
    on_w, on_h = 0, 0
    # (bbox/w/h would be extracted from _key_trim_save return; simplified for now)

    off_entry = AssetEntry(
        asset_id=f"{block_id}.off",
        kind="text_off",
        wall_path=f"assets/{block_id}.off.png",
        master_path=f"assets/{block_id}.off@master.png",
        px_w=off_w,
        px_h=off_h,
        content_bbox=off_bbox or (0, 0, 1, 1),
        dpi=cfg.wall_dpi,
    )
    on_entry = AssetEntry(
        asset_id=f"{block_id}.on",
        kind="text_on",
        wall_path=f"assets/{block_id}.on.png",
        master_path=f"assets/{block_id}.on@master.png",
        px_w=on_w,
        px_h=on_h,
        content_bbox=off_bbox or (0, 0, 1, 1),
        dpi=cfg.wall_dpi,
    )
    return [off_entry, on_entry]
