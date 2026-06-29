from pathlib import Path

from map.raw_models import Palette, GroupColor, GroupName, Hex, LocalColor


def _hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    """Convert '#RRGGBB' → (R, G, B) integers 0–255."""
    s = hex_str.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def gen(palette: Palette, out_asy: Path, out_tex: Path) -> None:
    """Write palette.asy and palette.tex from the Palette model.
    
    ⚠️ 2026-06-29 — the global-palette model is DEPRECATED (Nir's correction).
    Per-station local colors and Stabilo hearts are the new standard.
    If palette.groups is empty, stub files are generated."""
    group_names = sorted(palette.groups) if palette.groups else []

    # --- palette.asy ---
    asy_lines: list[str] = []
    asy_lines.append("// palette.asy — generated. v1.0")
    asy_lines.append("// NOTE 2026-06-29: global groups DEPRECATED — use per-element local colors")
    if palette.grey_ink:
        gr, gg, gb = _hex_to_rgb(palette.grey_ink)
        asy_lines.append(f"pen greyInk = rgb({gr}/255, {gg}/255, {gb}/255);  // DEPRECATED")
    else:
        asy_lines.append("// (no greyInk — uncolored ink is black/white)")
    asy_lines.append("")
    asy_lines.append("pen hi(string g) {")
    for name in group_names:
        gc = palette.groups[name]
        if gc is not None:
            r, g, b = _hex_to_rgb(gc.hi)
            asy_lines.append(
                f'  if (g == "{name}")   return rgb({r}/255, {g}/255, {b}/255);'
            )
    asy_lines.append('  abort("unknown hi group: " + g);')
    asy_lines.append("  return greyInk;")
    asy_lines.append("}")
    asy_lines.append("")
    asy_lines.append("pen ink(string g) {")
    for name in group_names:
        gc = palette.groups[name]
        if gc is not None:
            r, g, b = _hex_to_rgb(gc.ink)
            asy_lines.append(
                f'  if (g == "{name}")   return rgb({r}/255, {g}/255, {b}/255);'
            )
    asy_lines.append('  abort("unknown ink group: " + g);')
    asy_lines.append("  return greyInk;")
    asy_lines.append("}")
    asy_lines.append("")

    out_asy.write_text("\n".join(asy_lines))

    # --- palette.tex ---
    tex_lines: list[str] = []
    tex_lines.append("% palette.tex — generated. v1.0")
    tex_lines.append("% NOTE 2026-06-29: global groups DEPRECATED — use per-text-block color definitions")
    tex_lines.append(r"\usepackage{xcolor}")
    tex_lines.append("")
    for name in group_names:
        gc = palette.groups[name]
        if gc is not None:
            ink_hex = gc.ink.lstrip("#").upper()
            tex_lines.append(f"\\definecolor{{{name}}}{{HTML}}{{{ink_hex}}}")
    tex_lines.append("")
    if palette.grey_text:
        grey_text_hex = palette.grey_text.lstrip("#").upper()
        tex_lines.append(f"\\definecolor{{grey_text}}{{HTML}}{{{grey_text_hex}}}  % DEPRECATED")
    tex_lines.append(r"\newcommand{\cg}[2]{{\color{#1}#2}}  % DEPRECATED — use \\color{name}{text}")
    tex_lines.append("")

    out_tex.write_text("\n".join(tex_lines))
