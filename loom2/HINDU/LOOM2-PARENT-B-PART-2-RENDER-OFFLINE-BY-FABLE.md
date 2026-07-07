THANK YOU, Nir!!! 😊💿 Here is the second strike — the quiz-WAV press. One complete file per answer:
💿 audio/render_offline.py — complete

"""
LOOM2 -- audio/render_offline.py
DESIGN-TIME TOOL (not shipped in the EXE): renders quiz option WAVs.
Allowed imports: numpy, wave, json, argparse, config, core (types, surfaces),
audio (sampler, musicians, engine).
Contracts: BHAGAVAD GITA G2.5 (frozen). Bodies filled by Parent B, 2026-07-07.

Determinism chain (why every player hears the same bytes -- SUTRAS 5.3):
  sampler decodes/resamples deterministically -> musicians is order-independent
  and tie-break-documented -> engine.render_block_offline starts at t=0
  (a downbeat), voices at full gain, no camera (azimuth 0.0) -> int16
  conversion below is clip/scale/round, bit-stable. Rendered once, shipped.

Conventions of this tool:
  * run from the REPO ROOT (config paths and 'out' paths are CWD-relative;
    'os' is not an allowed import, so no path resolution happens here);
  * output directories must already exist (scenes/<id>/ always does);
  * the engine is never start()ed -- no audio device is touched.
"""
import json
import argparse
import wave
import numpy as np

import config
from core.types import TotemState
from core import surfaces
from audio.sampler import SampleLibrary
from audio import musicians
from audio.engine import AudioEngine

# ---------- seating-lattice controls (design-time pragmatism) ----------
# CONTRACT-NOTE (not an issue -- an under-specification, resolved additively):
# render_option's frozen signature carries no scene domain, but live play
# seats musicians on the SCENE's lattice (seat_grid(domain, step)). Defaults
# below reproduce that lattice exactly whenever the scene domain has integer
# bounds, step is 1.0, and the quiz spot lies >= hearing_radius inside the
# edge (true for all current scenes). For exact control, options.json may
# carry optional "domain" ([xmin,xmax,ymin,ymax]) and "step" keys per option;
# main() pins these module-level knobs before each render.
GRID_DOMAIN = None   # None -> integer-aligned window around the totem
GRID_STEP = 1.0

_ENGINE = None       # lazy singleton: decode the 89 samples once per run


def _engine() -> AudioEngine:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = AudioEngine(SampleLibrary())   # offline only: no .start()
    return _ENGINE


def _integer_window(x: float, y: float, r: float) -> tuple:
    """Smallest integer-cornered domain covering the hearing circle."""
    return (float(np.floor(x - r)), float(np.ceil(x + r)),
            float(np.floor(y - r)), float(np.ceil(y + r)))


def _write_wav(out_path: str, block: np.ndarray) -> None:
    """(N, 2) float32 in (-1, 1) -> 16-bit stereo WAV. Bit-deterministic:
    clip -> scale by 32767 -> round -> little-endian int16."""
    pcm = np.clip(block, -1.0, 1.0)
    ints = np.round(pcm * 32767.0).astype("<i2")
    with wave.open(out_path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)                       # 16-bit
        w.setframerate(config.SAMPLE_RATE)
        w.writeframes(np.ascontiguousarray(ints).tobytes())


def render_option(surface_name: str, totem_xy: tuple, hearing_radius: float,
                  z_per_octave: float, out_path: str) -> None:
    """Build voices at the given spot, run AudioEngine.render_block_offline
    for exactly config.OPTION_WAV_SECONDS (2 measures), write 16-bit stereo
    WAV at SAMPLE_RATE. Loop-clean: render starts on a downbeat and the
    buffer length is an exact multiple of the measure."""
    surface = surfaces.get(surface_name)
    tx, ty = float(totem_xy[0]), float(totem_xy[1])
    totem = TotemState(x=tx, y=ty, hearing_radius=float(hearing_radius))

    domain = GRID_DOMAIN if GRID_DOMAIN is not None \
        else _integer_window(tx, ty, totem.hearing_radius)
    grid = musicians.seat_grid(domain, GRID_STEP)
    voices = musicians.build_voices(totem, surface, grid, z_per_octave)
    if not voices:
        print(f"[render_offline] WARNING: no musicians within "
              f"r={totem.hearing_radius} at ({tx}, {ty}) -- "
              f"{out_path} will be silence. Authoring mistake?")

    eng = _engine()
    eng.set_voices(voices)                       # offline: full gain, no swell
    block = eng.render_block_offline(config.OPTION_WAV_SECONDS)

    # the loop-clean law: length is an exact multiple of the measure
    measure_samples = int(round(config.MEASURE_SEC * config.SAMPLE_RATE))
    assert block.shape[0] % measure_samples == 0, \
        f"loop-clean violation: {block.shape[0]} % {measure_samples} != 0"

    _write_wav(out_path, block)


def _report(label: str, path: str, n_voices: int) -> str:
    """One line per file, measured from the ARTIFACT ON DISK (real QA)."""
    with wave.open(path, "rb") as w:
        n, sr, ch = w.getnframes(), w.getframerate(), w.getnchannels()
        data = np.frombuffer(w.readframes(n), dtype="<i2")
    peak = float(np.max(np.abs(data))) / 32767.0 if data.size else 0.0
    db = f"{20.0 * np.log10(peak):+.1f} dBFS" if peak > 0.0 else "-inf (SILENT)"
    return (f"  {label}: {path} -- {n / sr:.3f} s, {ch} ch, "
            f"peak {db}, {n_voices} musicians")


def main() -> None:
    """CLI: python -m audio.render_offline scenes/hannibal_saddle/options.json
    where options.json lists label -> {surface, xy, radius, out}.
    Prints a one-line report per file (duration, peak level)."""
    global GRID_DOMAIN, GRID_STEP
    ap = argparse.ArgumentParser(
        description="LOOM2 quiz-option WAV renderer (design-time tool). "
                    "Optional per-option keys: z_per_octave, domain, step.")
    ap.add_argument("options_json", help="path to a scene's options.json")
    args = ap.parse_args()

    with open(args.options_json, "r", encoding="utf-8") as f:
        spec = json.load(f)

    print(f"[render_offline] {args.options_json}: {len(spec)} option(s)")
    for label in sorted(spec):                   # deterministic order
        opt = spec[label]
        GRID_DOMAIN = tuple(opt["domain"]) if "domain" in opt else None
        GRID_STEP = float(opt.get("step", 1.0))
        z_oct = float(opt.get("z_per_octave", config.Z_PER_OCTAVE))

        render_option(opt["surface"], tuple(opt["xy"]),
                      float(opt["radius"]), z_oct, opt["out"])

        # voice count recomputed for the report (pure math, microseconds)
        totem = TotemState(float(opt["xy"][0]), float(opt["xy"][1]),
                           float(opt["radius"]))
        dom = GRID_DOMAIN if GRID_DOMAIN is not None else _integer_window(
            totem.x, totem.y, totem.hearing_radius)
        n_voices = len(musicians.build_voices(
            totem, surfaces.get(opt["surface"]),
            musicians.seat_grid(dom, GRID_STEP), z_oct))
        print(_report(label, opt["out"], n_voices))


if __name__ == "__main__":
    main()

🔍 Engineering notes (every doubt, loudly and kindly)

    The one real gap I found — the seating lattice. render_option's frozen signature has no scene domain, but live play seats musicians on the scene's lattice. My resolution is additive and signature-clean: default = smallest integer-cornered window around the hearing circle (identical seats to live play whenever the scene domain has integer bounds, step 1.0, and the spot is ≥ R inside the edge — true for all current scenes), plus optional per-option "domain"/"step" keys in options.json that pin the exact lattice via the two module-level knobs. Marked CONTRACT-NOTE in the code (deliberately not CONTRACT-ISSUE — nothing frozen is wrong, it was under-specified). 🙏 Please have DeepSeek bless this default — and content authors should simply include "domain" (copied from scene.json) whenever a quiz spot sits near an edge.
    The report measures the artifact on disk — main() re-opens each written WAV and reports duration/channels/peak from the actual bytes, not from memory. A silent file screams -inf (SILENT).
    Loop-clean law asserted: block length must be an exact multiple of round(2.0×44100)=88,200; with OPTION_WAV_SECONDS = 4.0 that's 176,400=2×88,200. ✅
    int16 conversion is bit-stable: clip → ×32767 → np.round → <i2. The engine's tanh soft-clip already keeps ∣x∣<1; the clip is belt-and-braces.
    No os, by law — so no path resolution: out paths and options_json are used verbatim, CWD-relative; run from the repo root (config paths demand that anyway). Output folders must exist — scenes/<id>/ always does. Documented in the header.
    Engine lifecycle: lazy singleton, never start()ed — the 89 samples decode once per CLI run, no audio device is ever touched, set_voices → render_block_offline per option (DeepSeek confirmed: full gain from sample 0, azimuth 0.0, t=0 downbeat).
    Deterministic option order: sorted(spec) — reports and renders always run A, B, C, D.
    Line count: ~135 — over the ~100 estimate by the width of the CONTRACT-NOTE and the artifact-QA report, far under the 400 law. Reported honestly.
    Example options.json for DeepSeek (with the optional keys shown on B):

{
  "A": {"surface": "saddle", "xy": [2.0, 0.0], "radius": 2.5,
        "out": "data/scenes/hannibal_saddle/option_A.wav"},
  "B": {"surface": "saddle", "xy": [0.0, 2.0], "radius": 2.5,
        "domain": [-6.0, 6.0, -6.0, 6.0], "step": 1.0, "z_per_octave": 2.0,
        "out": "data/scenes/hannibal_saddle/option_B.wav"}
}

Parent B's mission is delivered — sampler.py + render_offline.py, complete, deterministic, contract-clean. The librarian guards the 89 and the press stamps loop-clean, byte-identical WAVs. 🧿

Whenever you're ready: paste both to DeepSeek for binding — python -m audio.sampler first, then a trial python -m audio.render_offline on a real options.json — and bring me his findings or any # CONTRACT-ISSUE: echoes. I stand by for review rounds. THANK YOU SO MUCH, Nir!!! :-) 🎻🎺🪈❤️
