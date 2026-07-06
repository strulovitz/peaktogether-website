"""
make_beeps.py — EMERGENCY SCAFFOLDING ONLY. [MEAT, but deliberately unloved]

ON THE RECORD (Nir's requirement, 2026-07-06): the game plays REAL
Philharmonia recordings, never beeps. This script exists for exactly one
situation: a machine that does NOT have the Philharmonia library (e.g.
some future automated test runner) and still needs to run the demo. On
Nir's PC it is never needed; the demo defaults to the real library and
refuses to fall back silently (beeps require an explicit --beeps flag).
The headless tests don't need audio files at all (FakeAudioSink).

Stdlib only. Writes loom/fixtures/audio_beeps/beep_<midi>.wav:
1.5 s mono 16-bit 44100 Hz sine at the MIDI pitch, 5 ms attack,
exponential decay (tau 0.4 s) so scrub-lingering is audible.
"""

import math
import os
import wave

MIDIS = [60, 62, 64, 67, 69, 72, 74, 76]  # union of both fixtures' pitches
RATE = 44100
SECONDS = 1.5
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio_beeps")


def midi_to_freq(m: int) -> float:
    return 440.0 * (2.0 ** ((m - 69) / 12.0))


def render(midi: int) -> bytes:
    freq = midi_to_freq(midi)
    n = int(RATE * SECONDS)
    attack = int(RATE * 0.005)
    out = bytearray()
    for i in range(n):
        t = i / RATE
        amp = 0.5 * math.exp(-t / 0.4)
        if i < attack:
            amp *= i / attack
        s = int(32767 * amp * math.sin(2 * math.pi * freq * t))
        out += s.to_bytes(2, "little", signed=True)
    return bytes(out)


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    for m in MIDIS:
        path = os.path.join(OUT_DIR, f"beep_{m}.wav")
        with wave.open(path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(render(m))
        print(f"wrote {path}")
    print("Done. Reminder: these are emergency test tones, NOT game audio.")


if __name__ == "__main__":
    main()
