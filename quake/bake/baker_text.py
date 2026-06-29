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
    text_bg_hex: str = "#ffffff"
    white_threshold: int = 210


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


def _strip_textcolor(latex: str) -> str:
    """Remove \\textcolor{name}{...} wrappers, leaving just the content.
    Handles nested braces in the content by counting."""
    result = []
    i = 0
    while i < len(latex):
        # Match \textcolor{name}{
        if latex[i:].startswith("\\textcolor{"):
            # Find the closing } of the name
            name_end = latex.index("}", i + 12)
            # Find the { starting the content (immediately after name's })
            content_brace = latex.index("{", name_end)
            content_start = content_brace + 1
            # Find matching } for content (handle nested braces)
            depth = 0
            j = content_start
            while j < len(latex):
                if latex[j] == "{":
                    depth += 1
                elif latex[j] == "}":
                    if depth == 0:
                        break
                    depth -= 1
                j += 1
            # Append just the content (skip \textcolor{name}{ and the closing })
            result.append(latex[content_start:j])
            i = j + 1
        else:
            result.append(latex[i])
            i += 1
    return "".join(result)


def _wrap_tex(
    text_block: TextBlock,
    *,
    for_off: bool,
    cfg_preamble: str,
) -> str:
    """Build the full standalone .tex source for OFF (all black) or ON (colored)."""
    parts: list[str] = []
    parts.append(r"\documentclass[border=4pt]{standalone}")
    parts.append(r"\usepackage{amsmath,amssymb,mathtools,xcolor,varwidth}")
    if not for_off:
        parts.append(_colors_tex(text_block))
    if cfg_preamble:
        parts.append(cfg_preamble)
    parts.append(r"\begin{document}")
    parts.append(r"\begin{varwidth}{28em}")
    parts.append(r"\large\bfseries")
    if for_off:
        parts.append(_strip_textcolor(text_block.latex))
    else:
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


def _trim_save(
    src_png: Path,
    out_png: Path,
    cfg: BakerTextConfig,
    *,
    want_bbox: bool,
):
    arr = np.array(Image.open(src_png).convert("RGBA"))
    bbox = _imageops.content_bbox(arr) if want_bbox else None
    trimmed = _imageops.trim(arr, cfg.trim_padding_px)
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
    _validate(text_block)

    out_dir.mkdir(parents=True, exist_ok=True)
    block_id = text_block.block_id

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

    off_wall_stem = out_dir / f"{block_id}.off"
    off_master_stem = Path(str(off_wall_stem) + "@master")
    result = compile_fn(off_tex, off_wall_stem, {}, AsyConfig(dpi=cfg.wall_dpi))
    if not result.ok:
        raise RuntimeError(result.stderr)
    result = compile_fn(off_tex, off_master_stem, {}, AsyConfig(dpi=cfg.master_dpi))
    if not result.ok:
        raise RuntimeError(result.stderr)

    on_wall_stem = out_dir / f"{block_id}.on"
    on_master_stem = Path(str(on_wall_stem) + "@master")
    result = compile_fn(on_tex, on_wall_stem, {}, AsyConfig(dpi=cfg.wall_dpi))
    if not result.ok:
        raise RuntimeError(result.stderr)
    result = compile_fn(on_tex, on_master_stem, {}, AsyConfig(dpi=cfg.master_dpi))
    if not result.ok:
        raise RuntimeError(result.stderr)

    off_bbox = None
    off_w, off_h = 0, 0
    on_w, on_h = 0, 0

    off_png = Path(str(off_wall_stem) + ".png")
    off_master_png = Path(str(off_master_stem) + ".png")
    if off_png.exists():
        off_bbox, off_w, off_h = _trim_save(
            off_png,
            out_dir / f"{block_id}.off.png",
            cfg, want_bbox=True,
        )
        if off_master_png.exists():
            _trim_save(
                off_master_png,
                out_dir / f"{block_id}.off@master.png",
                cfg, want_bbox=False,
            )

    on_png = Path(str(on_wall_stem) + ".png")
    on_master_png = Path(str(on_master_stem) + ".png")
    if on_png.exists():
        _, on_w, on_h = _trim_save(
            on_png,
            out_dir / f"{block_id}.on.png",
            cfg, want_bbox=True,
        )
        if on_master_png.exists():
            _trim_save(
                on_master_png,
                out_dir / f"{block_id}.on@master.png",
                cfg, want_bbox=False,
            )

    off_entry = AssetEntry(
        asset_id=f"{block_id}.off",
        kind="text_off",
        wall_path=f"assets/{block_id}.off.png",
        master_path=f"assets/{block_id}.off@master.png",
        px_w=off_w,
        px_h=off_h,
        content_bbox=off_bbox if off_bbox else (0, 0, off_w, off_h),
        dpi=cfg.wall_dpi,
    )
    on_entry = AssetEntry(
        asset_id=f"{block_id}.on",
        kind="text_on",
        wall_path=f"assets/{block_id}.on.png",
        master_path=f"assets/{block_id}.on@master.png",
        px_w=on_w,
        px_h=on_h,
        content_bbox=off_bbox if off_bbox else (0, 0, on_w, on_h),
        dpi=cfg.wall_dpi,
    )
    return [off_entry, on_entry]
