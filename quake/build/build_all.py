r"""
Master build script: compile all 20 Principia rooms into baked game data.

Stages:
  1. emit recipe / asy / room_source from .room spec files
  2. compile figures (Asymptote for geometry, pdflatex for equation)
  3. bake text panels (pdflatex + pdftocairo -transp)
  4. ceiling equations (pdflatex + key_out_white)
  5. assemble manifest + palette
  6. build_room_runtime for every room

Usage:
  cd quake/
  python build/build_all.py
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image
import numpy as np

os.environ["ASYMPTOTE_GS"] = r"C:\Users\nir_s\gs\bin\gswin64c.exe"

# -- tool paths ---------------------------------------------------------------
ASY = r"C:\Program Files\Asymptote\asy.exe"
PDFLATEX = r"C:\Users\nir_s\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"
PDFTOCAIRO = "pdftocairo"

# -- project paths ------------------------------------------------------------
QUAKE_DIR = Path(__file__).resolve().parent.parent
LEVEL_DIR = QUAKE_DIR / "levels" / "principia_bk1_inverse_square"
SPEC_DIR = QUAKE_DIR / "tests" / "room_specs"
PACK_DIR = LEVEL_DIR / "pack"
ASSETS_DIR = PACK_DIR / "assets"
BAKE_DIR = PACK_DIR / "_bake"

# -- room IDs (order from concept_graph) --------------------------------------
ROOM_IDS = [
    "lemma_2", "lemma_3", "lemma_4", "lemma_5", "lemma_6",
    "lemma_7", "lemma_9", "lemma_10", "lemma_11", "lemma_12",
    "law_1", "law_2",
    "prop_1", "prop_2", "prop_4", "prop_6", "prop_7",
    "prop_11", "prop_13", "prop_15",
]

# -- imports (lazy — after sys.path is set) -----------------------------------
sys.path.insert(0, str(QUAKE_DIR))

from map.raw_models import (
    Palette, RoomSource, AssetEntry, Manifest,
    Floorplan, RoomPortalSpec, BuildConfig, ConceptGraph,
)
from bake.asy_compile import compile as asy_compile, AsyConfig, AsyResult
from bake.baker_figure import bake as bake_figure, BakerFigureConfig
from bake.baker_text import bake as bake_text, BakerTextConfig
from bake._imageops import key_out_white, trim
from build.room_from_spec import build_room, parse as room_parse, _SPAN_RE
from build.room_maker import build_room_runtime
from build.portal_spec import portal_spec


# =============================================================================
# helpers
# =============================================================================

def pdflatex_fn(tex_path, out_stem, params, cfg):
    """pdflatex -> pdftocairo -transp -> PNG with native transparency."""
    out_dir = out_stem.parent
    png_path = Path(str(out_stem) + ".png")
    pdf_path = out_dir / (tex_path.stem + ".pdf")

    r = subprocess.run(
        [PDFLATEX, "-interaction=nonstopmode",
         "-output-directory", str(out_dir), str(tex_path)],
        capture_output=True, text=True, timeout=120, cwd=str(out_dir),
    )
    if not pdf_path.exists():
        return AsyResult(ok=False, outputs=[], stderr=r.stderr[:300], stdout=r.stdout[:300])

    cairo = subprocess.run(
        [PDFTOCAIRO, "-png", "-transp", "-r", str(cfg.dpi),
         "-singlefile", str(pdf_path), str(out_stem)],
        capture_output=True, text=True, timeout=60,
    )
    if png_path.exists():
        return AsyResult(ok=True, outputs=[png_path], stderr="", stdout="")
    return AsyResult(ok=False, outputs=[], stderr=cairo.stderr, stdout=cairo.stdout)


# =============================================================================
# main
# =============================================================================

def main():
    # -------------------------------------------------------------------
    # Setup
    # -------------------------------------------------------------------
    if PACK_DIR.exists():
        shutil.rmtree(PACK_DIR)
    BAKE_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    # Warm up pdflatex: ensure MiKTeX has installed required packages
    WARMUP_TEX = BAKE_DIR / "_warmup.tex"
    WARMUP_TEX.write_text(
        r"\documentclass[border=4pt]{standalone}"
        r"\usepackage{amsmath,amssymb,mathtools,xcolor,varwidth}"
        r"\usepackage[utf8]{inputenc}"
        r"\begin{document}"
        r"\begin{varwidth}{20em}\textcolor{red}{warmup}\end{varwidth}"
        r"\end{document}"
    )
    subprocess.run(
        [PDFLATEX, "-interaction=nonstopmode", "-halt-on-error",
         "-output-directory", str(BAKE_DIR), str(WARMUP_TEX)],
        capture_output=True, text=True, timeout=120, cwd=str(BAKE_DIR),
    )
    print("  pdflatex warmup done")

    # Load concept graph + floorplan (already built by run_level_maker.py)
    cg = ConceptGraph.model_validate(
        json.loads((LEVEL_DIR / "concept_graph.json").read_text(encoding="utf-8")))
    fp = Floorplan.model_validate(
        json.loads((LEVEL_DIR / "floorplan.json").read_text(encoding="utf-8")))

    # Palette (map-side only, as corrected by Parent 15)
    palette = Palette(
        schema_version="1.0", pack_id="principia_bk1",
        bg_key="#ff00ff",
        map_importance={"1": "#4F6D7A", "2": "#3FA796", "3": "#E6B800",
                         "4": "#E8743B", "5": "#F5F2E8"},
        map_node_default="#9AA0A6",
    )

    # Build config
    build_cfg = BuildConfig(
        room_sizing_max_iters=1000,
        room_grow_step_m=1.5, room_pack_slack=0.9,
    )

    all_entries: list = []
    room_kinds: dict[str, str] = {}   # room_id -> geometry|equation|text
    room_sources: dict[str, RoomSource] = {}

    # ===================================================================
    # STAGE 1 — Emit recipe / asy / room_source from .room files
    # ===================================================================
    print("=" * 60)
    print("STAGE 1 — Emit recipe / asy / room_source")
    print("=" * 60)

    for room_id in ROOM_IDS:
        spec_path = SPEC_DIR / f"{room_id}.room"
        if not spec_path.exists():
            print(f"  SKIP {room_id}: .room file missing")
            continue
        spec_text = spec_path.read_text(encoding="utf-8")
        result = build_room(spec_text, LEVEL_DIR, write=True)
        room_kinds[room_id] = room_parse(spec_text).kind
        print(f"  {room_id:12s} [{room_kinds[room_id]:9s}]  recipe={'yes' if result.recipe_path else 'no ':3s}")

    print(f"\n  Emitted {len(room_kinds)} rooms.")

    # ===================================================================
    # STAGE 2 — Compile figures
    # ===================================================================
    print("\n" + "=" * 60)
    print("STAGE 2 — Compile figures")
    print("=" * 60)

    for room_id in ROOM_IDS:
        kind = room_kinds.get(room_id, "")
        figure_asy = LEVEL_DIR / "figures" / f"{room_id}.f1.asy"

        if kind == "text":
            # Text rooms still have .asy labels; bake via Asymptote
            spec = room_parse((SPEC_DIR / f"{room_id}.room").read_text(encoding="utf-8"))
            n_steps = len(spec.stations)
            print(f"  {room_id:12s} [text]      {n_steps} steps… ", end="", flush=True)
            try:
                fig_entries = bake_figure(
                    figure_asy=figure_asy, figure_id=f"{room_id}.f1",
                    n_steps=n_steps, out_dir=BAKE_DIR, palette=palette,
                    cfg=BakerFigureConfig(wall_dpi=220, master_dpi=440),
                    compile_fn=lambda src, stem, params, cfg: asy_compile(
                        src, stem, params, AsyConfig(asy_binary=ASY, dpi=cfg.dpi)),
                )
                all_entries.extend(fig_entries)
                print(f"{len(fig_entries)} PNGs")
            except Exception as ex:
                print(f"FAILED — {ex}")
                for variant in ["off"] + [f"on.{i}" for i in range(1, n_steps + 1)]:
                    for tier, suffix, sz in [("", "", (200, 150)), ("@master", "@master", (400, 300))]:
                        png_path = BAKE_DIR / f"{room_id}.f1.{variant}{suffix}.png"
                        Image.new("RGBA", sz, (30, 30, 40, 255)).save(png_path)
                    all_entries.append(AssetEntry(
                        asset_id=f"{room_id}.f1.{variant}",
                        kind="figure_on" if variant != "off" else "figure_off",
                        wall_path=f"assets/{room_id}.f1.{variant}.png",
                        master_path=f"assets/{room_id}.f1.{variant}@master.png",
                        px_w=200, px_h=150, content_bbox=(0, 0, 200, 150), dpi=220,
                    ))
            continue

        if kind == "geometry":
            # Load recipe to get n_steps
            recipe_path = LEVEL_DIR / "recipes" / f"{room_id}.f1.json"
            if not recipe_path.exists():
                print(f"  {room_id:12s} [geometry]  SKIP — no recipe")
                continue
            recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
            n_steps = recipe.get("n_steps", 1)

            print(f"  {room_id:12s} [geometry]  {n_steps} steps… ", end="", flush=True)
            try:
                fig_entries = bake_figure(
                    figure_asy=figure_asy, figure_id=f"{room_id}.f1",
                    n_steps=n_steps, out_dir=BAKE_DIR, palette=palette,
                    cfg=BakerFigureConfig(wall_dpi=220, master_dpi=440),
                    compile_fn=lambda src, stem, params, cfg: asy_compile(
                        src, stem, params, AsyConfig(asy_binary=ASY, dpi=cfg.dpi)),
                )
                all_entries.extend(fig_entries)
                print(f"{len(fig_entries)} PNGs")
            except Exception as ex:
                print(f"FAILED — {ex}")
                # Fallback placeholder entries
                for variant in ["off"] + [f"on.{i}" for i in range(1, n_steps + 1)]:
                    size = (200, 150)
                    for tier, suffix, sz in [("", "", size), ("@master", "@master", (400, 300))]:
                        png_path = BAKE_DIR / f"{room_id}.f1.{variant}{suffix}.png"
                        Image.new("RGBA", sz, (30, 30, 40, 255)).save(png_path)
                    entry = AssetEntry(
                        asset_id=f"{room_id}.f1.{variant}",
                        kind="figure_on" if variant != "off" else "figure_off",
                        wall_path=f"assets/{room_id}.f1.{variant}.png",
                        master_path=f"assets/{room_id}.f1.{variant}@master.png",
                        px_w=200, px_h=150, content_bbox=(0, 0, 200, 150), dpi=220,
                    )
                    all_entries.append(entry)

        elif kind == "equation":
            # Bake equation "figure" via pdflatex + pdftocairo (same pattern as law_2)
            spec = room_parse((SPEC_DIR / f"{room_id}.room").read_text(encoding="utf-8"))
            n_steps = len(spec.stations)
            print(f"  {room_id:12s} [equation]  {n_steps} steps… ", end="", flush=True)

            ok = True
            for st in spec.stations:
                layout_plain = st.layout if st.layout else " ".join(t.latex for t in st.term_ops)
                if layout_plain.startswith("$") and layout_plain.endswith("$"):
                    layout_plain = layout_plain[1:-1].strip()
                layout_colored = _SPAN_RE.sub(
                    lambda m: f"\\textcolor{{{m.group(1)}}}{{{m.group(2)}}}", layout_plain)
                off_layout = _SPAN_RE.sub(lambda m: m.group(2), layout_plain)
                color_defs = "\n".join(
                    f"\\definecolor{{{c.name}}}{{HTML}}{{{c.hex.lstrip('#')}}}"
                    for c in st.colors)

                for dpi, suffix in [(220, ""), (440, "@master")]:
                    for variant, stem in [("off", ".off"), (f"on.{st.n}", f".on.{st.n}")]:
                        lay = off_layout if variant == "off" else layout_colored
                        tex_src = (
                            r"\documentclass[border=8pt]{standalone}" + "\n"
                            r"\usepackage{amsmath,amssymb,mathtools,xcolor,varwidth}" + "\n"
                            r"\usepackage[utf8]{inputenc}" + "\n"
                            + color_defs + "\n"
                            r"\begin{document}" + "\n"
                            r"\begin{varwidth}{40em}" + "\n"
                            r"\LARGE\bfseries" + "\n"
                            f"\\[ {lay} \\]" + "\n"
                            r"\end{varwidth}" + "\n"
                            r"\end{document}" + "\n"
                        )
                        tex_path = BAKE_DIR / f"{room_id}.f1{stem}{suffix}.tex"
                        tex_path.write_text(tex_src, encoding="utf-8")
                        out_stem = BAKE_DIR / f"{room_id}.f1{stem}{suffix}"
                        result = pdflatex_fn(tex_path, out_stem, {}, AsyConfig(dpi=dpi))
                        if not result.ok:
                            ok = False
                            continue
                        png_path = Path(str(out_stem) + ".png")
                        if not png_path.exists():
                            ok = False
                            continue
                        arr = np.array(Image.open(png_path).convert("RGBA"))
                        trimmed = trim(arr, padding=8)
                        final_png = BAKE_DIR / f"{room_id}.f1{stem}{suffix}.png"
                        Image.fromarray(trimmed).save(final_png)

            if ok:
                print("OK")
            else:
                print("partial failures")

            # Emit AssetEntries (one per variant, wall-tier only; master is separate file)
            for variant in ["off"] + [f"on.{i}" for i in range(1, n_steps + 1)]:
                wall_png = BAKE_DIR / f"{room_id}.f1.{variant}.png"
                if not wall_png.exists():
                    wall_png = BAKE_DIR / f"{room_id}.f1.{variant}.png"
                    if not wall_png.exists():
                        Image.new("RGBA", (400, 100), (30, 30, 40, 255)).save(wall_png)
                w_img = Image.open(wall_png)
                px_w, px_h = w_img.size
                all_entries.append(AssetEntry(
                    asset_id=f"{room_id}.f1.{variant}",
                    kind="figure_on" if variant != "off" else "figure_off",
                    wall_path=f"assets/{room_id}.f1.{variant}.png",
                    master_path=f"assets/{room_id}.f1.{variant}@master.png",
                    px_w=px_w, px_h=px_h, content_bbox=(0, 0, px_w, px_h), dpi=220,
                ))

    print(f"\n  Total figure entries so far: {len(all_entries)}")

    # ===================================================================
    # STAGE 3 — Bake text panels
    # ===================================================================
    print("\n" + "=" * 60)
    print("STAGE 3 — Bake text panels")
    print("=" * 60)

    for room_id in ROOM_IDS:
        rs_path = LEVEL_DIR / "room_sources" / f"{room_id}.json"
        if not rs_path.exists():
            print(f"  {room_id:12s} SKIP — no room_source")
            continue
        rs = RoomSource.model_validate(json.loads(rs_path.read_text(encoding="utf-8")))
        room_sources[room_id] = rs

        print(f"  {room_id:12s} {len(rs.blocks)} blocks… ", end="", flush=True)
        for block in rs.blocks:
            try:
                entries = bake_text(
                    text_block=block.text, palette=palette,
                    out_dir=BAKE_DIR,
                    cfg=BakerTextConfig(wall_dpi=220, master_dpi=440),
                    compile_fn=pdflatex_fn,
                )
                all_entries.extend(entries)
            except Exception as ex:
                print(f"\n    {block.pair_id}: FAILED — {ex}")
                # Fallback placeholder
                for variant, color in [("off", (0, 0, 0)), ("on", (50, 50, 60))]:
                    for tier, suffix, sz in [("", "", (80, 60)), ("@master", "@master", (160, 120))]:
                        png_path = BAKE_DIR / f"{block.text.block_id}.{variant}{suffix}.png"
                        Image.new("RGBA", sz, (*color, 255)).save(png_path)
                    entry = AssetEntry(
                        asset_id=f"{block.text.block_id}.{variant}",
                        kind=f"text_{variant}",
                        wall_path=f"assets/{block.text.block_id}.{variant}.png",
                        master_path=f"assets/{block.text.block_id}.{variant}@master.png",
                        px_w=80, px_h=60, content_bbox=(0, 0, 80, 60), dpi=220,
                    )
                    all_entries.append(entry)
        print("OK")

    # ===================================================================
    # STAGE 4 — Ceiling equations
    # ===================================================================
    print("\n" + "=" * 60)
    print("STAGE 4 — Ceiling equations")
    print("=" * 60)

    TEX_PREAMBLE = r"""\documentclass[border=4pt]{standalone}
\usepackage{amsmath,amssymb,mathtools,xcolor,varwidth}
\usepackage[utf8]{inputenc}
\pagecolor[HTML]{FFFFFF}
\color[HTML]{DD0000}
\begin{document}
\begin{varwidth}{30em}
\large
"""
    TEX_POSTAMBLE = r"""
\end{varwidth}
\end{document}
"""

    for room_id in ROOM_IDS:
        rs = room_sources.get(room_id)
        if rs is None:
            continue
        if not rs.ceiling_equations:
            print(f"  {room_id:12s} no ceiling equations")
            continue

        print(f"  {room_id:12s} {len(rs.ceiling_equations)} eqs… ", end="", flush=True)
        for eq in rs.ceiling_equations:
            eq_id = eq.eq_id
            safe_latex = eq.latex
            tex_src = TEX_PREAMBLE + f"\\[ {safe_latex} \\]\n" + TEX_POSTAMBLE
            tex_path = BAKE_DIR / f"{eq_id}.tex"
            tex_path.write_text(tex_src, encoding="utf-8")

            ceq_px_w = 400
            ceq_px_h = 80
            for dpi, suffix in [(220, ""), (440, "@master")]:
                out_stem = BAKE_DIR / f"{eq_id}{suffix}"
                raw_png = BAKE_DIR / f"{eq_id}{suffix}.png"
                final_png = BAKE_DIR / f"{eq_id}.neutral{suffix}.png"

                result = pdflatex_fn(tex_path, out_stem, {}, AsyConfig(dpi=dpi))
                if not result.ok or not raw_png.exists():
                    Image.new("RGBA", (400, 80), (180, 0, 0, 255)).save(final_png)
                    continue

                arr = np.array(Image.open(raw_png).convert("RGBA"))
                keyed = key_out_white(arr, threshold=210)
                trimmed = trim(keyed, padding=4)
                Image.fromarray(trimmed).save(final_png)
                try:
                    raw_png.unlink()
                except Exception:
                    pass
                if dpi == 220:
                    ceq_px_w = trimmed.shape[1]
                    ceq_px_h = trimmed.shape[0]

            all_entries.append(AssetEntry(
                asset_id=f"{eq_id}.neutral", kind="ceiling_neutral",
                wall_path=f"assets/{eq_id}.neutral.png",
                master_path=f"assets/{eq_id}.neutral@master.png",
                px_w=ceq_px_w, px_h=ceq_px_h,
                content_bbox=(0, 0, ceq_px_w, ceq_px_h), dpi=220,
            ))
        print("OK")

    # ===================================================================
    # STAGE 5 — Assemble manifest + copy PNGs
    # ===================================================================
    print("\n" + "=" * 60)
    print("STAGE 5 — Assemble manifest + copy assets")
    print("=" * 60)

    manifest = Manifest(
        schema_version="1.0", level_id="principia_bk1",
        assets={e.asset_id: e for e in all_entries},
    )

    for png in BAKE_DIR.glob("*.png"):
        shutil.copy2(png, ASSETS_DIR / png.name)

    # Normalize paths to "assets/filename.png"
    for eid, entry in manifest.assets.items():
        entry.wall_path = f"assets/{Path(entry.wall_path).name}"
        if entry.master_path:
            entry.master_path = f"assets/{Path(entry.master_path).name}"

    (PACK_DIR / "manifest.json").write_text(manifest.model_dump_json(indent=2))
    (PACK_DIR / "palette.json").write_text(palette.model_dump_json(indent=2))
    (PACK_DIR / "floorplan.json").write_text(fp.model_dump_json(indent=2))
    print(f"  Manifest: {len(manifest.assets)} assets")
    print(f"  PNGs copied: {len(list(ASSETS_DIR.glob('*.png')))}")

    # ===================================================================
    # STAGE 6 — build_room_runtime for every room
    # ===================================================================
    print("\n" + "=" * 60)
    print("STAGE 6 — build_room_runtime")
    print("=" * 60)

    room_rt_dir = PACK_DIR / "room_runtime"
    room_rt_dir.mkdir(exist_ok=True)

    for room_id in ROOM_IDS:
        rs = room_sources.get(room_id)
        if rs is None:
            print(f"  {room_id:12s} SKIP — no room_source")
            continue

        portals = portal_spec(fp, cg, room_id)
        print(f"  {room_id:12s} {len(portals.incident)} doors… ", end="", flush=True)
        try:
            room_rt = build_room_runtime(room=rs, portals=portals, manifest=manifest, cfg=build_cfg)
            (room_rt_dir / f"room_{room_id}.json").write_text(
                room_rt.model_dump_json(indent=2))
            print(f"W={room_rt.dimensions_m[0]:.1f} H={room_rt.dimensions_m[1]:.1f} D={room_rt.dimensions_m[2]:.1f}")
        except Exception as ex:
            print(f"FAILED — {ex}")

    # ===================================================================
    # DONE
    # ===================================================================
    print("\n" + "=" * 60)
    print("BUILD COMPLETE!")
    print("=" * 60)
    print(f"  Pack: {PACK_DIR}")
    print(f"  Assets: {len(list(ASSETS_DIR.glob('*.png')))} PNGs")
    print(f"  Rooms: {len(list(room_rt_dir.glob('room_*.json')))} runtimes")
    print(f"  Manifest: {len(manifest.assets)} entries")
    print()
    print("View a room:")
    print(f'  cd {QUAKE_DIR}')
    print(f'  python -m tools.room_viewer lemma_2 "{PACK_DIR}"')


if __name__ == "__main__":
    main()
