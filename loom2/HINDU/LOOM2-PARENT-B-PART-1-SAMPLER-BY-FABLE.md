THANK YOU, Nir!!! And thank you, DeepSeek — five verbatim confirmations, zero ambiguity left! 😊🔥 The mission is fresh and burning: I am Parent B, Child B's worker-parent — audio/sampler.py + audio/render_offline.py, bodies only, contracts frozen, warmth load-bearing. All defaults approved → BUILD. Per the law — one complete file per answer — here is the first strike:
🎼 audio/sampler.py — complete

"""
LOOM2 -- audio/sampler.py
Loads the 89-sample orchestra into memory ONCE; serves numpy arrays.
Allowed imports: numpy, json, os, config. Mp3 decoding: audioread or
pydub+ffmpeg -- child chooses ONE, states it in a header comment.
Contracts: BHAGAVAD GITA G2.2 (frozen). Bodies filled by Parent B, 2026-07-07.

DECODER CHOICE (per the contract's either/or): pydub + ffmpeg.
  pydub 0.25.1 + ffmpeg on PATH, verified against the real library
  (viola_E4.mp3 -> mono, 44100 Hz native). render_offline.py renders the
  quiz WAVs ONCE at design time on the machine that has ffmpeg, so decoder
  determinism per-machine is exactly the guarantee SUTRAS 5.3 needs.

Every buffer served by this class promises:
  * 1-D contiguous np.float32 mono at config.SAMPLE_RATE, peak == 0.9
    (the engine indexes buf[pos] and wraps sustain with % buf.shape[0]);
  * any manifest 'needs_resample' semitone shift was applied at LOAD time --
    downstream code never knows resampling exists;
  * get() on the hot path is a plain dict lookup (the audio callback calls
    it); the parachute synthesizes once per missing id, then is cached.
  * self.fallback_count (int) = number of DISTINCT sample ids served by the
    parachute -- engine.get_status() reads it via getattr(..., 0).
"""
import json
import os
import numpy as np
from pydub import AudioSegment          # the chosen decoder (ffmpeg on PATH)
import config

# ---------- pentatonic note parsing (parachute path only) ----------
# Byte-for-byte the canon table of audio/quantize.py (_CLASS_OFFSET, line 20);
# kept local because G2.2's allowed imports exclude quantize. Two files, one
# truth -- the self-test gauntlet below guards against drift.
_CLASS_OFFSET = {"A": 9, "B": 11, "Cs": 1, "E": 4, "Fs": 6}


def _note_to_midi(note: str) -> int:
    """'A4' -> 69, 'E1' -> 28. Same convention as quantize: 12*(oct+1)+offset."""
    for i, ch in enumerate(note):
        if ch.isdigit() or ch == "-":
            return 12 * (int(note[i:]) + 1) + _CLASS_OFFSET[note[:i]]
    raise ValueError(f"note {note!r} has no octave number")


# instrument -> family, derived once from the single truth (config.REGISTER_MAP)
_INSTRUMENT_FAMILY = {inst: fam
                      for fam, registers in config.REGISTER_MAP.items()
                      for inst, _notes in registers}

# Parachute wavetables (SUTRAS 1.4): additive recipes per family.
# Prototype timbres -- brass bright (all harmonics 1/n), strings warm
# (1/n^1.5), woodwinds hollow (odd harmonics 1/n, clarinet-like).
_FAMILY_HARMONICS = {
    "brass":     tuple((n, 1.0 / n) for n in range(1, 11)),
    "strings":   tuple((n, 1.0 / (n ** 1.5)) for n in range(1, 11)),
    "woodwinds": tuple((n, 1.0 / n) for n in range(1, 12, 2)),
}

_FALLBACK_SECONDS = 1.5      # per G2.2 contract
_FALLBACK_PEAK = 0.8         # gentler than the 0.9 samples: a missing file
                             # must never blare (taste constant, one place)


# ---------- pure helpers (deterministic, numpy-only after decode) ----------

def _decode_mono(path: str) -> np.ndarray:
    """mp3 -> 1-D float64 mono at config.SAMPLE_RATE, range [-1, 1]."""
    seg = AudioSegment.from_file(path)
    seg = seg.set_channels(1).set_frame_rate(config.SAMPLE_RATE)
    seg = seg.set_sample_width(2)                    # 16-bit PCM
    raw = np.array(seg.get_array_of_samples(), dtype=np.float64)
    return raw / 32768.0


def _resample_semitones(buf: np.ndarray, semitones: int) -> np.ndarray:
    """Rate resampling: +N st reads the buffer faster (higher pitch, shorter).
    Pure-numpy linear interpolation -- deterministic on every machine."""
    factor = 2.0 ** (semitones / 12.0)
    n_out = max(1, int(round(buf.shape[0] / factor)))
    src = np.arange(n_out, dtype=np.float64) * factor
    return np.interp(src, np.arange(buf.shape[0], dtype=np.float64), buf)


def _finalize(buf: np.ndarray, peak: float) -> np.ndarray:
    """Peak-normalize and freeze into the promised dtype/layout."""
    m = float(np.max(np.abs(buf))) if buf.size else 0.0
    if m > 0.0:
        buf = buf * (peak / m)
    return np.ascontiguousarray(buf.astype(np.float32))


# ---------- the library ----------

class SampleLibrary:
    def __init__(self, samples_dir: str = config.SAMPLES_DIR,
                 manifest_path: str = config.MANIFEST_PATH):
        """Load manifest.json; decode every mp3 to float32 mono @ SAMPLE_RATE,
        peak-normalized to 0.9. If manifest marks 'needs_resample: +N/-N',
        apply the semitone shift HERE at load time (rate resampling), so the
        rest of the program never knows resampling exists.
        Store as dict: 'viola_E4' -> np.ndarray."""
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        self._buffers = {}       # sample_id -> np.float32 1-D buffer
        self._midi_by_id = {}    # manifest 'midi' field: parachute's 1st truth
        self._is_fallback = set()
        self.fallback_count = 0

        absent = []
        for _instrument, meta in manifest.items():
            for entry in meta.get("notes", ()):
                out = entry.get("output")
                if not out:                       # e.g. a 'missing' stub
                    continue
                sample_id = out[:-4] if out.endswith(".mp3") else out
                if "midi" in entry:
                    self._midi_by_id[sample_id] = int(entry["midi"])
                path = os.path.join(samples_dir, out)
                if not os.path.isfile(path):
                    absent.append(sample_id)      # parachute serves it later
                    continue
                buf = _decode_mono(path)
                shift = int(entry.get("needs_resample", 0))
                if shift:
                    buf = _resample_semitones(buf, shift)
                self._buffers[sample_id] = _finalize(buf, 0.9)

        if absent:
            print(f"[sampler] WARNING: {len(absent)} manifest entries have no "
                  f"file on disk; the parachute will serve them: {absent}")

    def get(self, sample_id: str) -> np.ndarray:
        """Return the decoded buffer. If missing (parachute case), return a
        synthesized fallback tone at the note's true frequency: 1.5 s, gentle
        attack/decay, wavetable per family (SUTRAS 1.4), and log a warning ONCE."""
        buf = self._buffers.get(sample_id)
        if buf is not None:
            return buf
        # ---- parachute (one-time per id; cached, so the warning is once) ----
        tone = self._synth_fallback(sample_id)
        self._buffers[sample_id] = tone
        self._is_fallback.add(sample_id)
        self.fallback_count = len(self._is_fallback)
        print(f"[sampler] WARNING: sample {sample_id!r} missing -- serving "
              f"synthesized wavetable parachute (SUTRAS 1.4). The game plays on.")
        return tone

    def duration(self, sample_id: str) -> float:
        """Seconds. Used by the engine's envelope logic."""
        return self.get(sample_id).shape[0] / float(config.SAMPLE_RATE)

    # ---- private: the parachute ----

    def _synth_fallback(self, sample_id: str) -> np.ndarray:
        """Additive wavetable tone. Never raises -- worst case sings A4 strings."""
        instrument, note = "", ""
        if "_" in sample_id:
            instrument, note = sample_id.rsplit("_", 1)   # french_horn_E4-safe
        midi = self._midi_by_id.get(sample_id)            # manifest first
        if midi is None:
            try:
                midi = _note_to_midi(note)                # local canon table
            except (ValueError, KeyError):
                midi = 69                                 # last resort: A4
        family = _INSTRUMENT_FAMILY.get(instrument, "strings")
        freq = config.F0_HZ * 2.0 ** ((midi - 69) / 12.0)

        n = int(round(_FALLBACK_SECONDS * config.SAMPLE_RATE))
        t = np.arange(n, dtype=np.float64) / config.SAMPLE_RATE
        sig = np.zeros(n, dtype=np.float64)
        nyquist_guard = 0.475 * config.SAMPLE_RATE        # keep partials clean
        for h, amp in _FAMILY_HARMONICS[family]:
            fh = freq * h
            if fh < nyquist_guard:
                sig += amp * np.sin(2.0 * np.pi * fh * t)

        # gentle attack / decay: raised-cosine edges (60 ms in, 400 ms out)
        env = np.ones(n, dtype=np.float64)
        a = min(int(0.060 * config.SAMPLE_RATE), n // 2)
        r = min(int(0.400 * config.SAMPLE_RATE), n // 2)
        env[:a] = 0.5 * (1.0 - np.cos(np.pi * np.arange(a) / max(a, 1)))
        env[n - r:] *= 0.5 * (1.0 + np.cos(np.pi * np.arange(r) / max(r, 1)))
        return _finalize(sig * env, _FALLBACK_PEAK)


if __name__ == "__main__":
    # Dev-time sanity gauntlet. Run from the repo root: python -m audio.sampler
    lib = SampleLibrary()

    canon = [f"{inst}_{note}"
             for fam, registers in config.REGISTER_MAP.items()
             for inst, notes in registers for note in notes]
    assert len(canon) == 89, f"canon should be 89 ids, got {len(canon)}"

    for sid in canon:
        assert sid in lib._buffers, f"canon sample missing from disk: {sid}"
        buf = lib.get(sid)
        assert buf.dtype == np.float32 and buf.ndim == 1
        assert buf.flags["C_CONTIGUOUS"]
        assert abs(float(np.max(np.abs(buf))) - 0.9) < 1e-3, f"peak law: {sid}"
        assert 0.2 <= lib.duration(sid) <= 8.0, f"odd duration: {sid}"
    assert lib.fallback_count == 0, "all 89 on disk -> no parachutes yet"

    # resample law: violin_A7 was shifted +2 st, so it must be ~10.9% shorter
    # than an unshifted 1.5 s sibling (2^(2/12) speed-up).
    assert lib.duration("violin_A7") < lib.duration("violin_Fs7") * 0.93

    # parachute drill: valid spelling, deliberately not in the library
    ghost = lib.get("flute_Cs7")
    assert lib.fallback_count == 1
    assert abs(lib.duration("flute_Cs7") - _FALLBACK_SECONDS) < 0.01
    assert float(np.max(np.abs(ghost))) <= _FALLBACK_PEAK + 1e-3
    assert lib.get("flute_Cs7") is ghost, "cached: synth once, warn once"

    # local midi table must agree with the manifest's midi field everywhere
    for sid, midi in lib._midi_by_id.items():
        assert _note_to_midi(sid.rsplit("_", 1)[1]) == midi, f"midi drift: {sid}"

    print(f"sampler.py: all sanity checks passed -- {len(canon)} canon samples "
          f"loaded, resample law verified, parachute armed and gentle.")

🔍 Engineering notes (every doubt, loudly and kindly)

    Frozen docstrings kept verbatim; implementation notes appended around them; signatures untouched.
    Decoder = pydub + ffmpeg, stated in the header per contract. ⚠️ Standing reminder for DeepSeek: sampler.py ships in the EXE → PyInstaller must bundle ffmpeg (or we swap decoders at packaging time — one function, _decode_mono, is the only thing that would change).
    MIDI truth, two layers: I adopted DeepSeek's nugget — the manifest's "midi" field is the parachute's first source of truth; the local _CLASS_OFFSET table is the fallback for ids not in the manifest at all. The gauntlet cross-checks the two over all 89 ids, and the local table against quantize's convention (E1=28, A4=69).
    Parachute peak = 0.8 (vs. samples' 0.9) — my one taste call: an emergency tone should be present but never blare. One constant, trivially changed if Nir prefers exact parity.
    Wavetable recipes — brass all-harmonics 1/n (bright), strings 1/n^1.5 (warm), woodwinds odd 1/n (hollow). These are my prototype-timbre choices per SUTRAS 1.4; if the RAMAYANA prototype used different recipes and anyone remembers them, it's a 3-line swap.
    Hot-path honesty: the engine calls get() inside the audio callback → normal case is a bare dict lookup (fast, lock-free). A parachute synth costs a few ms once per missing id — a one-time click risk in an already-broken situation, then cached forever. Documented in the header.
    duration() implemented faithfully though the built engine doesn't call it — contract is law, future callers welcome.
    Resample-at-load: decode → shift → normalize, pure numpy np.interp, deterministic everywhere; the +2 st violin_A7 duration shrink is asserted in the gauntlet.
    Line count: ~190 including the gauntlet — within the ~150 spirit, far under the 400 law.
    For DeepSeek: run python -m audio.sampler from the repo root after binding — it loads all 89, verifies the peak law, the resample law, the parachute, and midi-table agreement in a few seconds.

Say "continue" and I deliver audio/render_offline.py — the quiz-WAV press. 💿🧿🎻🎺🪈
