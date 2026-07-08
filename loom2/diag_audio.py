"""
LOOM2 -- diag_audio.py  (DeepSeek diagnostic harness, 2026-07-08)
Runs the SAME mixer path as the live game with NO device and NO graphics:
  * builds a real Voice list via musicians.build_voices (saddle @ origin),
  * checks whether the mp3 samples actually decoded or the parachute synth
    fired (get_status fallback_voices),
  * renders 10 s via engine.render_block_offline (the exact _mix path),
  * writes diag_offline.wav for Nir to listen to,
  * prints peak / RMS / clip stats to quantify distortion.
Run from the loom2 folder:  python diag_audio.py
"""
import wave
import numpy as np

import config
from audio.sampler import SampleLibrary
from audio.engine import AudioEngine
from audio import musicians
from core import surfaces
from core.types import TotemState

print("=" * 64)
print("LOOM2 audio diagnostic -- offline mixer render (no device)")
print("=" * 64)

lib = SampleLibrary()
print(f"SampleLibrary built. fallback_count = {lib.fallback_count} "
      f"(0 = all real mp3 samples decoded; >0 = synth parachute in use)")

engine = AudioEngine(lib)
surface = surfaces.get("saddle")
domain = (-4.0, 4.0, -4.0, 4.0)
grid = musicians.seat_grid(domain)
totem = TotemState(0.6, 0.4, config.HEARING_R)   # off-origin for pitch variety
voices = musicians.build_voices(totem, surface, grid, 2.0)
print(f"seated musicians (voices) = {len(voices)}")
rings = sorted(round(v.ring, 2) for v in voices)
print(f"voice rings (dist/RING_WIDTH) = {rings}")

engine.set_voices(voices)
st = engine.get_status()
print(f"get_status after set_voices: fallback_voices={st['fallback_voices']}, "
      f"live_voices={st['live_voices']}, error={st['error']!r}")

print("rendering 10.0 s through render_block_offline (the live _mix path) ...")
buf = engine.render_block_offline(10.0)   # (N, 2) float32
buf = np.asarray(buf, dtype=np.float32)

peak = float(np.max(np.abs(buf)))
rms = float(np.sqrt(np.mean(buf ** 2)))
clip = float(np.mean(np.abs(buf) > 0.99))
near = float(np.mean(np.abs(buf) > 0.80))
print(f"  samples={buf.shape[0]}, channels={buf.shape[1]}")
print(f"  PEAK={peak:.4f}  RMS={rms:.4f}  "
      f"frac|x|>0.99={clip*100:.2f}%  frac|x|>0.80={near*100:.2f}%")

# write 16-bit stereo WAV
out_path = "diag_offline.wav"
i16 = np.clip(buf, -1.0, 1.0)
i16 = (i16 * 32767.0).astype("<i2")
with wave.open(out_path, "wb") as w:
    w.setnchannels(buf.shape[1])
    w.setsampwidth(2)
    w.setframerate(config.SAMPLE_RATE)
    w.writeframes(i16.tobytes())
print(f"wrote {out_path}  <-- LISTEN TO THIS (double-click it)")
print("=" * 64)
