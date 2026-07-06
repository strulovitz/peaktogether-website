"""
make_bench_fixtures.py — design-time generator for the M2 bench
fixtures. [demo/design scaffolding — stdlib only]

Math is allowed HERE (author's machine, like the Compiler); the Player
never evaluates anything. Writes into fixtures/spells/:

  fixture_bench8.json   f(x)=x   violin, 8 notes, major, C4..C5
  fixture_bench20.json  f(x)=sqrt(x) cello, 20 notes, CHROMATIC,
                        span 24, C3..C5 (grand staff + black keys)

NIR'S AMENDMENT (July 2026): the curved fixture uses 20 notes. The
BIBLE §7.2 num_notes cap is raised from 16 to 20 by Nir's decision
(recorded in Commentaries §5). The widgets are N-agnostic; this is
purely the note count of the demo tune.

Segments use the canonical midpoint tiling of Compiler Stage 10:
boundaries at midpoints between consecutive x_i; first=0, last=1.

Run:  python fixtures/make_bench_fixtures.py
"""

from __future__ import annotations

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "spells")

NOTE_NAMES = ["C", "Cs", "D", "Ds", "E", "F", "Fs", "G", "Gs", "A", "As", "B"]


def note_name(midi: int) -> str:
    return f"{NOTE_NAMES[midi % 12]}{midi // 12 - 1}"


def midpoint_segments(xs):
    bounds = [0.0]
    for a, b in zip(xs, xs[1:]):
        bounds.append((a + b) / 2.0)
    bounds.append(1.0)
    return [(bounds[i], bounds[i + 1]) for i in range(len(xs))]


def build(spell_id, display, func_text, f, n_notes, dense, base_midi,
          span, scale_semis, instrument, articulation, low, high):
    xs = [i / (n_notes - 1) for i in range(n_notes)]
    ys = [f(x) for x in xs]
    y_min, y_max = min(ys), max(ys)

    def norm(y):
        return 0.0 if y_max == y_min else (y - y_min) / (y_max - y_min)

    scale_set = sorted({12 * q + d for q in range(3) for d in scale_semis
                        if 12 * q + d <= span} | {0})
    segs = midpoint_segments(xs)
    notes = []
    for i, (x, y) in enumerate(zip(xs, ys)):
        theta = span * norm(y)
        snapped = min(scale_set,
                      key=lambda s: (abs(theta - s), s))   # ties downward
        midi = base_midi + snapped
        notes.append({
            "index": i, "note_name": note_name(midi), "midi": midi,
            "start_beat": float(i), "duration_beats": 1.0,
            "dynamic": "forte",
            "sample": (f"audio/{instrument}_{note_name(midi)}"
                       f"_05_forte_{articulation}.mp3"),
            "gain": 0.9, "key_index": midi - base_midi,
            "graph_segment": {"x_from": round(segs[i][0], 6),
                              "x_to": round(segs[i][1], 6)},
        })
    points = [[round(i / (dense - 1), 6), round(norm(f(i / (dense - 1))), 6)]
              for i in range(dense)]
    return {
        "format": "loom-spell", "format_version": "1.0",
        "spell_id": spell_id, "display_name": display,
        "function_text": func_text,
        "instrument": instrument, "articulation": articulation,
        "bpm": 110, "base_note": note_name(base_midi),
        "total_beats": float(n_notes),
        "keyboard": {"low_note": note_name(low), "high_note": note_name(high)},
        "staff": {"clef": "grand" if any(n["midi"] < 60 for n in notes)
                  else "treble"},
        "notes": notes,
        "graph": {"points": points, "x_label": "x", "y_label": "f(x)"},
        "notes_for_humans": f"Generated M2 fixture: {func_text}.",
    }


MAJOR = (0, 2, 4, 5, 7, 9, 11)
CHROMATIC = tuple(range(12))


def main():
    os.makedirs(OUT, exist_ok=True)
    specs = [
        build("fixture_bench8", "M2 Bench Fixture - a straight line, heard",
              "f(x) = x on [0, 1]", lambda x: x, 8, 65,
              60, 12, MAJOR, "violin", "arco-normal", 60, 72),
        build("fixture_bench20", "M2 Bench Fixture - the square root's curve",
              "f(x) = sqrt(x) on [0, 1]", math.sqrt, 20, 200,
              48, 24, CHROMATIC, "cello", "arco-normal", 48, 72),
    ]
    for s in specs:
        path = os.path.join(OUT, s["spell_id"] + ".json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(s, fh, indent=2)
        print(f"wrote {path}  ({len(s['notes'])} notes)")


if __name__ == "__main__":
    main()
