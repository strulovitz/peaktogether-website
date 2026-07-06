"""
LOOM  --  Milestone 0 (M0)  --  Latency & MP3 spike        [THROWAWAY / not shipped]

Purpose (New Testament II.8):
  Retire the project's two biggest unknowns on Nir's real Windows PC, using the
  REAL Philharmonia MP3 samples:
    (1) Can pygame load real Philharmonia MP3s into preloaded, triggerable buffers?
    (2) Does trigger-to-audible latency feel instant enough for scrubbing
        (binding budget: <= 30 ms; achieved via a small mixer buffer, try 256 then 512)?

What it does:
  * Reads two instrument folders from the Philharmonia library (default: violin + oboe).
  * From each, picks a real C-major scale (8 notes, one MP3 per note) at a chosen
    dynamic (default mezzo-forte) and the plain sustained articulation
    (arco-normal for strings, normal for winds), decoded into memory buffers.
  * Opens a tiny window. You PLAY the real notes and FEEL the latency:
        A S D F G H J K  -> instrument 1 (default violin) scale, low -> high
        1 2 3 4 5 6 7 8  -> instrument 2 (default oboe)   scale, low -> high
  * TAB toggles the mixer output buffer 256 <-> 512 samples (re-initialises audio)
    so you can compare the feel; shows computed output latency for each.
  * Prints a plain-text report (which files loaded, decode times, latency) to paste back.

Run (PowerShell, from this folder):
    python m0_latency_spike.py
    python m0_latency_spike.py --inst violin,cello
    python m0_latency_spike.py --dynamic forte

Headless self-check (no window; proves audio + real-MP3 load + trigger paths):
    python m0_latency_spike.py --selftest
"""

import argparse
import glob
import os
import time

import numpy as np
import pygame

SAMPLE_RATE = 44100
CHANNELS = 2
BIT_DEPTH = -16
BUFFERS = [256, 512]

PHIL_ROOT_DEFAULT = r"C:\Users\nir_s\Downloads\philharmonia"
SCALE_KEYS = ["a", "s", "d", "f", "g", "h", "j", "k"]
NUM_KEYS = ["1", "2", "3", "4", "5", "6", "7", "8"]

LETTER_SEMITONE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
CMAJOR_PC = {0, 2, 4, 5, 7, 9, 11}
DUR_PREF = ["1", "05", "15", "025", "2", "3"]           # nice melodic length first
GOOD_ARTIC = {"arco-normal", "normal"}                   # plain sustained note
NOTE_NAMES = ["C", "Cs", "D", "Ds", "E", "F", "Fs", "G", "Gs", "A", "As", "B"]


def note_to_midi(tok):
    letter = tok[0]
    sharp = len(tok) > 1 and tok[1] == "s"
    octave = int(tok[2:] if sharp else tok[1:])
    return 12 * (octave + 1) + LETTER_SEMITONE[letter] + (1 if sharp else 0)


def midi_to_name(m):
    return "%s%d" % (NOTE_NAMES[m % 12], m // 12 - 1)


def parse_phil(path):
    """violin_A3_025_forte_arco-normal.mp3 -> dict, or None if it doesn't parse."""
    stem = os.path.basename(path)[:-4]          # strip .mp3
    parts = stem.split("_")
    if len(parts) < 5:
        return None
    try:
        midi = note_to_midi(parts[1])
    except (KeyError, ValueError, IndexError):
        return None
    return {
        "path": path,
        "note": parts[1],
        "midi": midi,
        "dur": parts[2],
        "dyn": parts[3],
        "artic": "_".join(parts[4:]),
    }


def select_scale(folder, dynamic):
    """Return up to 8 (midi, note_name, path) forming a C-major scale from `folder`."""
    if not os.path.isdir(folder):
        return []
    parsed = [p for p in (parse_phil(f)
              for f in glob.glob(os.path.join(folder, "**", "*.mp3"), recursive=True)) if p]
    good = [p for p in parsed if p["dyn"] == dynamic and p["artic"] in GOOD_ARTIC]
    if not good:                                  # relax articulation, then dynamic
        good = [p for p in parsed if p["dyn"] == dynamic] or parsed
    best = {}                                     # midi -> (dur_rank, path)
    for p in good:
        rank = DUR_PREF.index(p["dur"]) if p["dur"] in DUR_PREF else 99
        if p["midi"] not in best or rank < best[p["midi"]][0]:
            best[p["midi"]] = (rank, p["path"])
    midis = sorted(best)
    diatonic = [m for m in midis if m % 12 in CMAJOR_PC]
    for start in [m for m in diatonic if m % 12 == 0 and m >= 48]:   # from a low-mid C
        seq = [m for m in diatonic if m >= start][:8]
        if len(seq) == 8:
            return [(m, midi_to_name(m), best[m][1]) for m in seq]
    return [(m, midi_to_name(m), best[m][1]) for m in midis[:8]]     # fallback


def init_mixer(buffer_size):
    if pygame.mixer.get_init():
        pygame.mixer.quit()
    pygame.mixer.pre_init(SAMPLE_RATE, BIT_DEPTH, CHANNELS, buffer_size)
    pygame.mixer.init()
    pygame.mixer.set_num_channels(16)
    return pygame.mixer.get_init()


def output_latency_ms(buffer_size):
    return buffer_size / SAMPLE_RATE * 1000.0


def load_bank(folder, dynamic, keys):
    """Decode the selected scale into Sounds. Returns (entries, report_rows)."""
    entries, rows = [], []
    for key, (midi, name, path) in zip(keys, select_scale(folder, dynamic)):
        try:
            t0 = time.perf_counter()
            snd = pygame.mixer.Sound(path)
            dt = (time.perf_counter() - t0) * 1000.0
            entries.append({"key": key, "name": name, "snd": snd})
            rows.append((os.path.basename(path), True, dt, snd.get_length()))
        except Exception as exc:  # noqa: BLE001
            rows.append((os.path.basename(path), False, 0.0, str(exc)))
    return entries, rows


def build_banks(buffer_size, root, insts, dynamic):
    init_info = init_mixer(buffer_size)
    keybanks = [SCALE_KEYS, NUM_KEYS]
    banks, reports = [], []
    for i, inst in enumerate(insts[:2]):
        entries, rows = load_bank(os.path.join(root, inst), dynamic, keybanks[i])
        banks.append({"inst": inst, "keys": keybanks[i], "entries": entries})
        reports.append((inst, rows))
    return init_info, banks, reports


def print_report(buffer_size, init_info, reports):
    print("\n" + "=" * 66)
    print("LOOM M0 SPIKE REPORT  (real Philharmonia MP3s)")
    print("=" * 66)
    print("pygame:", pygame.version.ver, "| SDL:",
          ".".join(str(x) for x in pygame.get_sdl_version()))
    print("mixer init (rate, fmt, ch):", init_info, "| buffer:", buffer_size, "samples")
    lat = output_latency_ms(buffer_size)
    print("computed output latency: %.2f ms  (budget <= 30 ms -> %s)"
          % (lat, "PASS" if lat <= 30 else "OVER"))
    for inst, rows in reports:
        oks = [r for r in rows if r[1]]
        print("-- %s: %d/%d notes decoded --" % (inst, len(oks), len(rows)))
        for name, ok, dt, extra in rows:
            if ok:
                print("   [OK ] %-46s decode %6.1f ms  len %.2fs" % (name, dt, extra))
            else:
                print("   [FAIL] %-46s %s" % (name, extra))
    print("=" * 66 + "\n")


def selftest(root, insts, dynamic):
    pygame.init()
    for buf in BUFFERS:
        init_info, banks, reports = build_banks(buf, root, insts, dynamic)
        for bank in banks:
            for e in bank["entries"]:
                e["snd"].play()
        print_report(buf, init_info, reports)
        time.sleep(0.2)
    pygame.quit()
    print("SELFTEST OK -- audio init, real-MP3 load, and trigger paths all ran.")


def run_window(root, insts, dynamic):
    pygame.init()
    screen = pygame.display.set_mode((760, 320))
    pygame.display.set_caption("LOOM M0 -- real Philharmonia latency spike")
    font = pygame.font.SysFont("consolas", 17)
    big = pygame.font.SysFont("consolas", 22, bold=True)
    clock = pygame.time.Clock()

    buf_idx = 0
    buffer_size = BUFFERS[buf_idx]
    init_info, banks, reports = build_banks(buffer_size, root, insts, dynamic)
    print_report(buffer_size, init_info, reports)

    keymap = {}
    for bank in banks:
        for e in bank["entries"]:
            keymap[e["key"]] = e
    last_msg = "press the keys to play; TAB toggles buffer; ESC quits"

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_TAB:
                    buf_idx = (buf_idx + 1) % len(BUFFERS)
                    buffer_size = BUFFERS[buf_idx]
                    init_info, banks, reports = build_banks(buffer_size, root, insts, dynamic)
                    keymap = {e["key"]: e for bank in banks for e in bank["entries"]}
                    last_msg = "buffer -> %d  (latency %.2f ms)" % (
                        buffer_size, output_latency_ms(buffer_size))
                    print_report(buffer_size, init_info, reports)
                elif event.key == pygame.K_r:
                    print_report(buffer_size, init_info, reports)
                    last_msg = "report printed to console"
                else:
                    key = pygame.key.name(event.key)
                    if key in keymap:
                        e = keymap[key]
                        t0 = time.perf_counter()
                        e["snd"].play()
                        ov = (time.perf_counter() - t0) * 1000.0
                        last_msg = "'%s' -> %s  (play() overhead %.3f ms)" % (
                            key, e["name"], ov)

        screen.fill((18, 20, 28))
        lat = output_latency_ms(buffer_size)
        b1 = banks[0] if banks else {"inst": "-", "entries": []}
        b2 = banks[1] if len(banks) > 1 else {"inst": "-", "entries": []}
        lines = [
            (big, "LOOM  M0  --  real Philharmonia latency spike", (235, 235, 245)),
            (font, "buffer %d samples   output latency %.2f ms   (budget <=30 -> %s)"
                   % (buffer_size, lat, "PASS" if lat <= 30 else "OVER"),
                   (150, 230, 150) if lat <= 30 else (240, 150, 150)),
            (font, "%-7s  A S D F G H J K   ->  %s"
                   % (b1["inst"], " ".join(e["name"] for e in b1["entries"])),
                   (200, 210, 230)),
            (font, "%-7s  1 2 3 4 5 6 7 8   ->  %s"
                   % (b2["inst"], " ".join(e["name"] for e in b2["entries"])),
                   (230, 210, 200)),
            (font, "TAB = buffer 256/512     R = report     ESC = quit", (160, 160, 175)),
            (font, last_msg, (245, 220, 140)),
        ]
        y = 22
        for f, text, color in lines:
            screen.blit(f.render(text, True, color), (18, y))
            y += 46
        pygame.display.flip()
        clock.tick(60)

    print_report(buffer_size, init_info, reports)
    pygame.quit()


def main():
    parser = argparse.ArgumentParser(description="LOOM M0 real-Philharmonia latency spike")
    parser.add_argument("--root", default=PHIL_ROOT_DEFAULT, help="Philharmonia library root")
    parser.add_argument("--inst", default="violin,oboe",
                        help="comma-separated instrument folders (first two are keyed)")
    parser.add_argument("--dynamic", default="mezzo-forte", help="dynamic to sample")
    parser.add_argument("--selftest", action="store_true", help="headless: run paths, no window")
    args = parser.parse_args()
    insts = [s.strip() for s in args.inst.split(",") if s.strip()]

    if args.selftest:
        selftest(args.root, insts, args.dynamic)
    else:
        run_window(args.root, insts, args.dynamic)


if __name__ == "__main__":
    main()
