"""
LOOM2 -- Build the sample library from the Philharmonia collection.
Implements SUTRAS Part Ten (Fable, v1.0, 2026-07-07).

Scans Downloads/philharmonia/, collects one file per pentatonic note (A, B, Cs,
E, Fs) inside each instrument's real register band, applying the selection
criteria (exact note > duration ~1-2s > dynamic forte-first > strict articulation).
Missing notes fall back to the nearest chromatic neighbour (<= +/-2 semitones),
recorded as needs_resample.

Outputs (under loom2/):
  samples/<instrument>_<note><octave>.mp3   (renamed copies, only what we need)
  manifest.json                             (every note -> source, duration, ...)
  coverage_report.txt                       (per-instrument exists/missing)
"""
import os
import json
import shutil

PHIL = r"C:\Users\nir_s\Downloads\philharmonia"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
MANIFEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manifest.json")
REPORT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coverage_report.txt")

# pitch-class numbers (sharps only, as Philharmonia spells them)
PC = {'C': 0, 'Cs': 1, 'D': 2, 'Ds': 3, 'E': 4, 'F': 5, 'Fs': 6,
      'G': 7, 'Gs': 8, 'A': 9, 'As': 10, 'B': 11}
PC_TO_NAME = {v: k for k, v in PC.items()}
PENTATONIC = {9, 11, 1, 4, 6}          # A, B, Cs, E, Fs

DURATION_SECONDS = {'025': 0.25, '05': 0.5, '1': 1.0, '15': 1.5}
DURATION_RANK = {'15': 100, '1': 95, '05': 50, '025': 10}   # others excluded
DYNAMIC_RANK = {'forte': 100, 'mezzo-forte': 80, 'fortissimo': 60,
                'mezzo-piano': 30, 'piano': 20, 'pianissimo': 5}

# folder, output-name, family, required articulation, low-note, high-note
INSTRUMENTS = [
    ("double bass",   "double_bass",   "strings", "arco-normal", "E1",  "G2"),
    ("cello",         "cello",         "strings", "arco-normal", "A2",  "G3"),
    ("viola",         "viola",         "strings", "arco-normal", "A3",  "G4"),
    ("violin",        "violin",        "strings", "arco-normal", "A4",  "A7"),
    ("contrabassoon", "contrabassoon", "wood",    "normal",      "As0", "G2"),  # Bb0
    ("bassoon",       "bassoon",       "wood",    "normal",      "A2",  "G3"),
    ("clarinet",      "clarinet",      "wood",    "normal",      "A3",  "G4"),
    ("oboe",          "oboe",          "wood",    "normal",      "A4",  "G5"),
    ("flute",         "flute",         "wood",    "normal",      "A5",  "C7"),
    ("tuba",          "tuba",          "brass",   "normal",      "D1",  "G2"),
    ("trombone",      "trombone",      "brass",   "normal",      "A2",  "G3"),
    ("french horn",   "french_horn",   "brass",   "normal",      "A3",  "G4"),
    ("trumpet",       "trumpet",       "brass",   "normal",      "A4",  "D6"),
]


def parse_note(token):
    """'As0' -> midi.  Returns None if not parseable."""
    if len(token) < 2:
        return None
    if token[1] == 's':
        letter, octave = token[:2], token[2:]
    else:
        letter, octave = token[:1], token[1:]
    if letter not in PC or not octave.lstrip('-').isdigit():
        return None
    return (int(octave) + 1) * 12 + PC[letter]


def midi_to_name(midi):
    """69 -> 'A4' (sharp spelling)."""
    return PC_TO_NAME[midi % 12] + str(midi // 12 - 1)


def scan_folder(folder, articulation):
    """Return {midi: [candidate dicts]} of all sustained files passing the
    articulation filter, keyed by their note's midi number."""
    by_midi = {}
    for fn in os.listdir(folder):
        if not fn.endswith('.mp3'):
            continue
        base = fn[:-4]
        parts = base.split('_')
        if len(parts) < 5:
            continue
        note_tok, length_tok, dynamic, artic = parts[1], parts[2], parts[3], parts[4]
        if artic != articulation:
            continue
        if length_tok not in DURATION_RANK:      # excludes phrase/long/very-long
            continue
        midi = parse_note(note_tok)
        if midi is None:
            continue
        cand = {
            "filename": fn,
            "note": note_tok,
            "length": length_tok,
            "dynamic": dynamic,
            "articulation": artic,
            "score": DURATION_RANK[length_tok] * 1000 + DYNAMIC_RANK.get(dynamic, 0),
        }
        by_midi.setdefault(midi, []).append(cand)
    return by_midi


def best_candidate(cands):
    """Highest score; pianissimo only if nothing else exists."""
    non_pp = [c for c in cands if c["dynamic"] != "pianissimo"]
    pool = non_pp if non_pp else cands
    return max(pool, key=lambda c: c["score"])


def build():
    if os.path.isdir(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    os.makedirs(OUT_DIR)

    manifest = {}
    report_lines = []
    grand_exact = grand_resampled = grand_missing = 0

    for folder_name, out_name, family, artic, lo, hi in INSTRUMENTS:
        folder = os.path.join(PHIL, folder_name)
        lo_midi, hi_midi = parse_note(lo), parse_note(hi)
        targets = [m for m in range(lo_midi, hi_midi + 1) if (m % 12) in PENTATONIC]

        if not os.path.isdir(folder):
            report_lines.append(f"{out_name}: FOLDER MISSING ({folder})")
            continue
        by_midi = scan_folder(folder, artic)

        entries = []
        exact = resampled = missing = 0
        missing_notes = []
        for tm in targets:
            target_name = midi_to_name(tm)
            out_file = f"{out_name}_{target_name}.mp3"
            if tm in by_midi:
                c = best_candidate(by_midi[tm])
                shutil.copyfile(os.path.join(folder, c["filename"]),
                                os.path.join(OUT_DIR, out_file))
                entries.append({
                    "note": target_name, "midi": tm, "output": out_file,
                    "source": c["filename"], "duration_s": DURATION_SECONDS[c["length"]],
                    "dynamic": c["dynamic"], "articulation": c["articulation"],
                    "needs_resample": 0, "status": "exact",
                })
                exact += 1
            else:
                # nearest chromatic neighbour, <= +/- 2 semitones
                found = None
                for off in (-1, 1, -2, 2):
                    if (tm + off) in by_midi:
                        found = (tm + off, off)
                        break
                if found:
                    src_midi, off = found
                    c = best_candidate(by_midi[src_midi])
                    shutil.copyfile(os.path.join(folder, c["filename"]),
                                    os.path.join(OUT_DIR, out_file))
                    shift = tm - src_midi          # +N means shift source UP to target
                    entries.append({
                        "note": target_name, "midi": tm, "output": out_file,
                        "source": c["filename"], "duration_s": DURATION_SECONDS[c["length"]],
                        "dynamic": c["dynamic"], "articulation": c["articulation"],
                        "needs_resample": shift, "status": "resampled",
                    })
                    resampled += 1
                else:
                    entries.append({
                        "note": target_name, "midi": tm, "output": None,
                        "source": None, "status": "missing", "needs_resample": None,
                    })
                    missing += 1
                    missing_notes.append(target_name)

        manifest[out_name] = {
            "family": family, "folder": folder_name, "articulation": artic,
            "band": f"{lo}-{hi}", "targets": len(targets),
            "exact": exact, "resampled": resampled, "missing": missing,
            "notes": entries,
        }
        grand_exact += exact
        grand_resampled += resampled
        grand_missing += missing
        line = (f"{out_name:14s} [{family:7s}] {lo}-{hi}: "
                f"{len(targets):2d} targets -> {exact:2d} exact, "
                f"{resampled} resampled, {missing} missing")
        if missing_notes:
            line += "  MISSING: " + ", ".join(missing_notes)
        report_lines.append(line)

    total = grand_exact + grand_resampled + grand_missing
    header = [
        "LOOM2 SAMPLE LIBRARY -- COVERAGE REPORT",
        "Built per SUTRAS Part Ten (pentatonic A/B/Cs/E/Fs, real register bands).",
        f"TOTAL: {total} target notes -> {grand_exact} exact, "
        f"{grand_resampled} resampled (<=+/-2 st), {grand_missing} missing.",
        f"Files written to: {OUT_DIR}",
        "-" * 78,
    ]
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(header + report_lines) + "\n")
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("\n".join(header + report_lines))
    print(f"\nmanifest.json + coverage_report.txt written under loom2/.")
    file_count = len([f for f in os.listdir(OUT_DIR) if f.endswith('.mp3')])
    print(f"samples/ now holds {file_count} mp3 files.")


if __name__ == "__main__":
    build()
