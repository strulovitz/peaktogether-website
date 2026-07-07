💌 The letter is absorbed, the mission burns bright and fresh: I am Parent A, the worker-parent for audio/quantize.py + audio/musicians.py. All scriptures read, all seams quoted, all decisions locked. Per the law — one complete file per answer — here is the first strike.
🎼 audio/quantize.py — complete

"""
LOOM2 -- audio/quantize.py
Pitch quantization and the register map. PURE FUNCTIONS, no state, no I/O.
Allowed imports: math, config. Nothing else.
Contracts: BHAGAVAD GITA G2.1 (frozen). Bodies filled by Parent A, 2026-07-07.

Internal conventions (this module's only consumer is audio/musicians.py):
  * TIE-BREAKING: wherever a value lies exactly between two candidates
    (z_to_note midpoints, resolve_instrument equidistant clamps), the
    LOWER pitch wins.  Deterministic on every machine, every run.
  * Angles are normalized to [0, 360) before family blending.
"""
import math
import config

# ---------- derived tables (immutable, computed once from config) ----------

# Semitone offset of each pentatonic class within the MIDI octave (C = 0).
# Music-theory constants; asserted against config so config stays the truth.
_CLASS_OFFSET = {"A": 9, "B": 11, "Cs": 1, "E": 4, "Fs": 6}
_OFFSET_CLASS = {v: k for k, v in _CLASS_OFFSET.items()}
_PENTA_OFFSETS = frozenset(_CLASS_OFFSET.values())
assert set(_CLASS_OFFSET) == set(config.PENTA_CLASSES), \
    "quantize._CLASS_OFFSET disagrees with config.PENTA_CLASSES"

_A4_MIDI = 69  # z = 0 -> A4 = 440 Hz (config.F0_HZ), origin of the helix


def note_to_midi(note: str) -> int:
    """'A4' -> 69, 'Cs5' -> 73, 'B0' -> 23. Spelling: A,B,Cs,E,Fs + octave digit.
    Must be exact inverse of midi_to_note for all pentatonic notes."""
    for i, ch in enumerate(note):
        if ch.isdigit() or ch == "-":      # '-' admits sub-zero octaves,
            break                          # keeping the inverse exact everywhere
    else:
        raise ValueError(f"note {note!r} has no octave number")
    cls, octave = note[:i], int(note[i:])
    if cls not in _CLASS_OFFSET:
        raise ValueError(
            f"note class {cls!r} is not pentatonic {tuple(config.PENTA_CLASSES)}")
    return 12 * (octave + 1) + _CLASS_OFFSET[cls]


def midi_to_note(midi: int) -> str:
    """Inverse of note_to_midi. Only called with pentatonic midi values."""
    offset = midi % 12
    if offset not in _OFFSET_CLASS:
        raise ValueError(f"midi {midi} is not an A-major-pentatonic pitch")
    return f"{_OFFSET_CLASS[offset]}{midi // 12 - 1}"


def z_to_note(z: float, z_per_octave: float) -> str:
    """World height -> nearest A-major-pentatonic note name.
    z=0 -> 'A4' (440 Hz) exactly. Semitones = 12*z/z_per_octave, snapped to
    the nearest pentatonic class. NO range clamp here (that is per-family).
    Exact midpoints snap DOWN (lower pitch wins; see module conventions)."""
    target = _A4_MIDI + 12.0 * z / z_per_octave
    # The widest pentatonic gap is 3 semitones, so the nearest pentatonic
    # midi lies within 1.5 st of target; a +/-3 window is ample.
    best_midi, best_dist = None, None
    for m in range(int(math.floor(target)) - 3, int(math.ceil(target)) + 4):
        if m % 12 in _PENTA_OFFSETS:
            d = abs(m - target)
            if best_dist is None or d < best_dist:   # strict '<': lower wins ties
                best_midi, best_dist = m, d
    return midi_to_note(best_midi)


def _build_family_tables() -> dict:
    """family -> (owned: {note: instrument}, ordered: [(midi, note), ...])."""
    tables = {}
    for family, registers in config.REGISTER_MAP.items():
        owned = {}
        for instrument, notes in registers:
            for n in notes:
                owned[n] = instrument
        ordered = sorted((note_to_midi(n), n) for n in owned)
        tables[family] = (owned, ordered)
    return tables


_FAMILY_TABLES = _build_family_tables()


def resolve_instrument(family: str, note: str) -> tuple:
    """(family, note) -> (instrument, owned_note).
    Looks up config.REGISTER_MAP. If note is below/above the family's total
    span, soft-clamp to the family's lowest/highest owned note (SUTRAS 1.3).
    Returns e.g. ('viola', 'E4'). NEVER returns a note the instrument
    does not own -- config lists are the only truth.

    Implementation: nearest-owned-note search. Because each family's
    registers are contiguous in pentatonic space (verified: no gaps,
    no overlaps), the nearest owned note to any out-of-span note IS the
    span end -- exactly the SUTRAS 1.3 soft-clamp -- while unexpected
    inputs still resolve gracefully and deterministically."""
    try:
        owned, ordered = _FAMILY_TABLES[family]
    except KeyError:
        raise ValueError(
            f"unknown family {family!r}; valid: {sorted(_FAMILY_TABLES)}") from None
    if note in owned:
        return (owned[note], note)
    m = note_to_midi(note)
    _, best_note = min(ordered, key=lambda pair: (abs(pair[0] - m), pair[0]))
    return (owned[best_note], best_note)


# Anchors sorted by angle; sectors between adjacent anchors partition the circle.
_ANCHORS = tuple(sorted((ang % 360.0, fam)
                        for fam, ang in config.FAMILY_ANGLE_DEG.items()))


def families_for_angle(theta_deg: float) -> tuple:
    """Stage angle -> (family_a, family_b, blend 0..1 toward family_b).
    Anchors per config.FAMILY_ANGLE_DEG; linear blend across the 120 deg
    between adjacent anchors. At an anchor exactly: (that_family, next, 0.0)
    -- the equal-power crossfade then yields the pure family."""
    t = theta_deg % 360.0
    n = len(_ANCHORS)
    for i in range(n):
        ang_a, fam_a = _ANCHORS[i]
        ang_b, fam_b = _ANCHORS[(i + 1) % n]
        span = (ang_b - ang_a) % 360.0
        offset = (t - ang_a) % 360.0
        if offset < span:
            return (fam_a, fam_b, offset / span)
    # Mathematically unreachable (sectors cover the circle); float paranoia:
    return (_ANCHORS[0][1], _ANCHORS[1][1], 0.0)


if __name__ == "__main__":
    # Dev-time sanity gauntlet (not imported by the game; runs in a second).
    assert note_to_midi("A4") == 69 and note_to_midi("Cs5") == 73
    assert note_to_midi("B0") == 23
    for _fam, _regs in config.REGISTER_MAP.items():           # all 89 round-trip
        for _inst, _notes in _regs:
            for _n in _notes:
                assert midi_to_note(note_to_midi(_n)) == _n
                assert resolve_instrument(_fam, _n) == (_inst, _n)
    assert z_to_note(0.0, 2.0) == "A4"                        # the origin law
    assert z_to_note(2.0, 2.0) == "A5" and z_to_note(-2.0, 2.0) == "A3"
    assert resolve_instrument("brass", "A7") == ("trumpet", "Cs6")   # high clamp
    assert resolve_instrument("strings", "B0") == ("double_bass", "E1")  # low clamp
    assert families_for_angle(90.0) == ("brass", "woodwinds", 0.0)
    _a, _b, _bl = families_for_angle(0.0)
    assert (_a, _b) == ("strings", "brass") and abs(_bl - 0.25) < 1e-12
    print("quantize.py: all sanity checks passed -- 89 notes round-trip clean.")

🔍 Engineering notes (flagged honestly, per our culture)

    Signatures and docstring contracts untouched — I only appended implementation notes beneath the frozen docstring text.
    The nearest-owned-note trick: because I verified (back at Gita Part 1) that every family's registers are contiguous and non-overlapping in pentatonic space, "nearest owned" is the SUTRAS soft-clamp at the span ends — one mechanism, zero special cases, and graceful under any unexpected input.
    Tie-break law: lower pitch wins, everywhere, documented at the top. Deterministic → byte-identical offline WAVs.
    The '-' in note parsing is pure robustness: a very deep scene could push z_to_note below octave 0 (no clamp there, per contract), and the inverse must survive the round trip until resolve_instrument clamps it into the orchestra.
    Derived tables at import are immutable data computed once from config — the "no state" law means no mutable state; config remains the single truth (there's even an assert enforcing it).
    Line count: ~135 including the self-test gauntlet — within the Gita's ~120 estimate spirit and far under the 400 law.
    For DeepSeek: run python -m audio.quantize once after binding — it round-trips all 89 canon notes and both clamp directions in under a second.

Say "continue" and I deliver audio/musicians.py — the Sonifiquation core. 🧿🎻🎺🪈
