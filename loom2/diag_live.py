"""
LOOM2 -- diag_live.py  (DeepSeek diagnostic, 2026-07-08)
Confirms suspect (a): does the REAL-TIME callback underrun?
Starts the engine on the real device (NO graphics), plays 10 s, prints
the underrun count from get_status(), then stops cleanly.
Run from the loom2 folder:  python diag_live.py
(You will hear ~10 s of audio.)
"""
import time
import config
from audio.sampler import SampleLibrary
from audio.engine import AudioEngine
from audio import musicians
from core import surfaces
from core.types import TotemState

lib = SampleLibrary()
engine = AudioEngine(lib)
surface = surfaces.get("saddle")
grid = musicians.seat_grid((-4.0, 4.0, -4.0, 4.0))
totem = TotemState(0.6, 0.4, config.HEARING_R)
voices = musicians.build_voices(totem, surface, grid, 2.0)

engine.start()
print("engine started; status:", engine.get_status())
engine.set_voices(voices)
print(f"playing {len(voices)} voices for 10 s ...")
for s in range(1, 11):
    time.sleep(1.0)
    st = engine.get_status()
    print(f"  t={s:2d}s  underruns={st['underruns']}  "
          f"live_voices={st['live_voices']}  running={st['running']}")
final = engine.get_status()
engine.stop()
print("FINAL:", final)
print(f">>> underruns total = {final['underruns']}  "
      f"(0 = timing innocent; climbing = suspect (a) CONFIRMED)")
