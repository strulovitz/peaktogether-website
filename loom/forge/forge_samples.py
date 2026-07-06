"""
forge_samples.py — THE SAMPLE FORGE. Design-time tool. [MEAT]

PURPOSE (born 2026-07-06, the day the violin C5 came up short): the
Philharmonia library records each note in several LENGTHS, but not every
length for every note. Melodies must be built from notes of ONE uniform
duration — pitch is the data; duration must never wobble. The Forge
manufactures that uniform set, offline, on the author's PC:

  For each requested note:
    1. gather all numeric-length takes (025/05/1/15) at the requested
       dynamic (with graceful dynamic fallback), SKIPPING long/very-long/
       phrase files (those are expressive multi-attack gestures);
    2. decode the longest take (pygame is the decoder — proven by M0;
       no new software needed);
    3. make it exactly --target-seconds long:
         TRUNCATE + natural raised-cosine release  (take long enough), or
         LOOP-EXTEND the sustain via correlation-matched crossfade loops
         (the 40-year-old sampler technique), then the same release;
    4. loudness-match the whole set (RMS to the set median, peak-safe).

  Outputs into --out (default loom/forge/forged/), mirroring the library:
    forged/<instrument>/<instrument>_<note>_forged<T>_<dynamic>_<articulation>.wav
    forged/<instrument>/_audition_scale_<...>.wav   <- Nir LISTENS to this
    forged/<instrument>/_forge_report.txt           <- what was done, per note

  Nir's approval loop: play the audition scale; if any note sticks out,
  paste the report to DeepSeek/Fable. Originals are NEVER modified.

Usage (DeepSeek runs this; one line per spell's needs):
  python forge_samples.py --library "C:/Users/nir_s/Downloads/philharmonia" ^
      --instrument violin --articulation arco-normal --dynamic forte ^
      --notes C4,D4,E4,G4,A4,C5,D5,E5 --target-seconds 1.3

Dependencies: numpy (installed), pygame (installed). Nothing new.
"""

from __future__ import annotations

import argparse
import os
import wave

import numpy as np

RATE = 44100
LENGTH_TOKENS = ("15", "1", "05", "025")          # longest first; no "2" exists
DYNAMIC_FALLBACK = ["forte", "mezzo-forte", "fortissimo", "mezzo-piano", "piano"]
SILENCE_DB = -50.0        # leading-silence trim threshold
RELEASE_MS = 250          # synthetic/natural release fade length
XFADE_MS = 80             # loop-junction crossfade (masks phase/vibrato seams)
LOOP_WIN_MS = 60          # correlation window for loop-point matching


# ---------------- decode (pygame as the MP3 decoder, per M0) ----------------

def decode_mono(path: str) -> np.ndarray:
    import pygame
    if not pygame.mixer.get_init():
        pygame.mixer.init(RATE, -16, 2, 512)      # offline tool: buffer irrelevant
    import pygame.sndarray
    arr = pygame.sndarray.array(pygame.mixer.Sound(path)).astype(np.float32)
    if arr.ndim == 2:                             # stereo -> mono
        arr = arr.mean(axis=1)
    return arr / 32768.0


# ---------------- small DSP helpers (all offline, all auditable) ----------------

def rms_envelope(x: np.ndarray, win: int = 1323, hop: int = 441) -> np.ndarray:
    n = max(1, (len(x) - win) // hop)
    return np.array([np.sqrt(np.mean(x[i * hop:i * hop + win] ** 2) + 1e-12)
                     for i in range(n)])


def trim_leading_silence(x: np.ndarray) -> np.ndarray:
    env = rms_envelope(x)
    thresh = env.max() * (10 ** (SILENCE_DB / 20))
    idx = np.argmax(env > thresh)                 # first frame above threshold
    return x[max(0, idx * 441 - 441):]            # keep ~10 ms of the attack ramp


def raised_cosine_release(x: np.ndarray, release_n: int) -> np.ndarray:
    out = x.copy()
    r = min(release_n, len(out))
    fade = 0.5 * (1 + np.cos(np.linspace(0, np.pi, r)))
    out[-r:] *= fade
    return out


def find_loop_points(x: np.ndarray) -> tuple[int, int]:
    """Pick loop end 'e' late in the stable body, then search for the loop
    start 's' whose preceding LOOP_WIN best matches the audio preceding
    'e' — so jumping from e back to s is (nearly) seamless; the crossfade
    hides the rest. Plain-language failure if the take is too short."""
    w = int(RATE * LOOP_WIN_MS / 1000)
    e = len(x) - int(RATE * RELEASE_MS / 1000)    # leave room for a tail
    lo = int(RATE * 0.20)                          # skip the bow/breath attack
    hi = e - int(RATE * 0.15)                      # loop body >= 150 ms
    if hi - lo < int(RATE * 0.05) or e <= w:
        raise SystemExit(
            "ERROR: a take is too short to loop-extend (audio "
            f"{len(x)/RATE:.2f}s). Paste this to Fable: lower "
            "--target-seconds or pick another dynamic.")
    ref = x[e - w:e]
    ref_n = ref / (np.linalg.norm(ref) + 1e-9)
    best_s, best_score = lo, -2.0
    for s in range(lo, hi, 147):                  # ~3 ms grid: fast + fine enough
        cand = x[s - w:s]
        score = float(np.dot(ref_n, cand / (np.linalg.norm(cand) + 1e-9)))
        if score > best_score:
            best_s, best_score = s, score
    return best_s, e


def crossfade_append(out: np.ndarray, seg: np.ndarray, xfade_n: int) -> np.ndarray:
    """Equal-power crossfade join (no clicks, energy preserved)."""
    a, b = out[-xfade_n:], seg[:xfade_n]
    t = np.linspace(0, np.pi / 2, xfade_n)
    mixed = a * np.cos(t) + b * np.sin(t)
    return np.concatenate([out[:-xfade_n], mixed, seg[xfade_n:]])


def forge_one(x: np.ndarray, target_s: float) -> tuple[np.ndarray, str]:
    x = trim_leading_silence(x)
    target_n = int(RATE * target_s)
    release_n = int(RATE * RELEASE_MS / 1000)
    if len(x) >= target_n:                        # the happy, most natural path
        return raised_cosine_release(x[:target_n], release_n), "TRUNCATE"
    s, e = find_loop_points(x)                    # the sampler path
    xfade_n = int(RATE * XFADE_MS / 1000)
    out = x[:e]
    while len(out) < target_n:
        out = crossfade_append(out, x[s:e], xfade_n)
    return raised_cosine_release(out[:target_n], release_n), "LOOP-EXTEND"


# ---------------- library plumbing ----------------

def find_takes(folder: str, instrument: str, note: str,
               dynamic: str, articulation: str) -> list[str]:
    files = os.listdir(folder)
    for dyn in [dynamic] + [d for d in DYNAMIC_FALLBACK if d != dynamic]:
        got = [f for f in files
               if f.split("_")[:2] == [instrument, note]
               and f.endswith(f"_{dyn}_{articulation}.mp3")
               and f.split("_")[2] in LENGTH_TOKENS]
        if got:   # longest nominal take first: most real audio, least looping
            return sorted(got, key=lambda f: LENGTH_TOKENS.index(f.split("_")[2]))
    return []


def write_wav(path: str, x: np.ndarray) -> None:
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
        w.writeframes(pcm.tobytes())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--library", required=True)
    ap.add_argument("--instrument", required=True)
    ap.add_argument("--articulation", required=True)
    ap.add_argument("--dynamic", default="forte")
    ap.add_argument("--notes", required=True, help="comma list, e.g. C4,D4,E4")
    ap.add_argument("--target-seconds", type=float, default=1.3)
    ap.add_argument("--out", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "forged"))
    a = ap.parse_args()

    src = os.path.join(a.library, a.instrument)
    dst = os.path.join(a.out, a.instrument)
    os.makedirs(dst, exist_ok=True)
    token = f"forged{str(a.target_seconds).replace('.', '')}"
    report, forged, names = [], [], []

    for note in [n.strip() for n in a.notes.split(",")]:
        takes = find_takes(src, a.instrument, note, a.dynamic, a.articulation)
        if not takes:
            raise SystemExit(f"ERROR: no numeric-length take for {a.instrument} "
                             f"{note} ({a.articulation}) in {src}")
        y, how = forge_one(decode_mono(os.path.join(src, takes[0])),
                           a.target_seconds)
        forged.append(y); names.append(note)
        report.append(f"{note}: {takes[0]}  ->  {how}, {a.target_seconds}s")

    # loudness-match the SET (median RMS target; peak-safe)
    rms = [float(np.sqrt(np.mean(y ** 2))) for y in forged]
    target = float(np.median(rms))
    for i, y in enumerate(forged):
        g = target / (rms[i] + 1e-9)
        y *= g
        peak = float(np.abs(y).max())
        if peak > 0.99:
            y *= 0.99 / peak
        fn = f"{a.instrument}_{names[i]}_{token}_{a.dynamic}_{a.articulation}.wav"
        write_wav(os.path.join(dst, fn), y)
        report[i] += f", gain x{g:.2f}"

    gap = np.zeros(int(RATE * 0.2), np.float32)
    scale = np.concatenate(sum(([y, gap] for y in forged), []))
    write_wav(os.path.join(dst, f"_audition_scale_{a.instrument}_{token}.wav"), scale)
    with open(os.path.join(dst, "_forge_report.txt"), "a", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n")
    print("\n".join(report))
    print(f"\nDone. LISTEN to _audition_scale_{a.instrument}_{token}.wav — "
          f"every note must ring the same length. Report saved.")


if __name__ == "__main__":
    main()
