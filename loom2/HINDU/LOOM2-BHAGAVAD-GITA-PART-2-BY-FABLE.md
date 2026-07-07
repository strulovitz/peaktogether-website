With pleasure — here is the audio heart. 🎼
📜 THE BHAGAVAD GITA — PART 2
The Audio Module Contracts

LOOM2 · v1.0 · July 7, 2026 · All bodies empty by design — children fill them, contracts never change.
G2.1 — audio/quantize.py

"""
LOOM2 -- audio/quantize.py
Pitch quantization and the register map. PURE FUNCTIONS, no state, no I/O.
Allowed imports: math, config. Nothing else.
Child chat scope: implement all bodies. ~120 lines expected.
"""
import math
import config

def note_to_midi(note: str) -> int:
    """'A4' -> 69, 'Cs5' -> 73, 'B0' -> 23. Spelling: A,B,Cs,E,Fs + octave digit.
    Must be exact inverse of midi_to_note for all pentatonic notes."""
    raise NotImplementedError

def midi_to_note(midi: int) -> str:
    """Inverse of note_to_midi. Only called with pentatonic midi values."""
    raise NotImplementedError

def z_to_note(z: float, z_per_octave: float) -> str:
    """World height -> nearest A-major-pentatonic note name.
    z=0 -> 'A4' (440 Hz) exactly. Semitones = 12*z/z_per_octave, snapped to
    the nearest pentatonic class. NO range clamp here (that is per-family)."""
    raise NotImplementedError

def resolve_instrument(family: str, note: str) -> tuple:
    """(family, note) -> (instrument, owned_note).
    Looks up config.REGISTER_MAP. If note is below/above the family's total
    span, soft-clamp to the family's lowest/highest owned note (SUTRAS 1.3).
    Returns e.g. ('viola', 'E4'). NEVER returns a note the instrument
    does not own -- config lists are the only truth."""
    raise NotImplementedError

def families_for_angle(theta_deg: float) -> tuple:
    """Stage angle -> (family_a, family_b, blend 0..1 toward family_b).
    Anchors per config.FAMILY_ANGLE_DEG; linear blend across the 120 deg
    between adjacent anchors."""
    raise NotImplementedError

G2.2 — audio/sampler.py

"""
LOOM2 -- audio/sampler.py
Loads the 89-sample orchestra into memory ONCE; serves numpy arrays.
Allowed imports: numpy, json, os, config. Mp3 decoding: audioread or
pydub+ffmpeg -- child chooses ONE, states it in a header comment.
Child chat scope: implement all bodies. ~150 lines expected.
"""
import numpy as np
import config

class SampleLibrary:
    def __init__(self, samples_dir: str = config.SAMPLES_DIR,
                 manifest_path: str = config.MANIFEST_PATH):
        """Load manifest.json; decode every mp3 to float32 mono @ SAMPLE_RATE,
        peak-normalized to 0.9. If manifest marks 'needs_resample: +N/-N',
        apply the semitone shift HERE at load time (rate resampling), so the
        rest of the program never knows resampling exists.
        Store as dict: 'viola_E4' -> np.ndarray."""
        raise NotImplementedError

    def get(self, sample_id: str) -> np.ndarray:
        """Return the decoded buffer. If missing (parachute case), return a
        synthesized fallback tone at the note's true frequency: 1.5 s, gentle
        attack/decay, wavetable per family (SUTRAS 1.4), and log a warning ONCE."""
        raise NotImplementedError

    def duration(self, sample_id: str) -> float:
        """Seconds. Used by the engine's envelope logic."""
        raise NotImplementedError

G2.3 — audio/musicians.py

"""
LOOM2 -- audio/musicians.py
THE SONIFIQUATION CORE: (totem, surface) -> list[Voice]. Pure, no audio I/O.
Allowed imports: math, config, core.types, audio.quantize.
Child chat scope: implement all bodies. ~140 lines expected.
"""
import math, config
from core.types import Voice, TotemState, SurfaceFn
from audio import quantize

def seat_grid(domain: tuple, step: float = 1.0) -> list:
    """Grid seating plan for a scene domain (xmin,xmax,ymin,ymax).
    Returns list of (x, y) floats. Called once per scene."""
    raise NotImplementedError

def build_voices(totem: TotemState, surface: SurfaceFn,
                 grid: list, z_per_octave: float) -> list:
    """For every seated musician within totem.hearing_radius:
      z      = surface(x, y)
      note   = quantize.z_to_note(z, z_per_octave)
      theta  = stage angle around the totem, world frame (atan2)
      fams   = quantize.families_for_angle(theta)
      sample_a/sample_b from quantize.resolve_instrument on each family
      ring   = distance / config.RING_WIDTH, capped at NMAX_RING
      gain   = smooth edge taper: 0.5*(1+cos(pi*d/R))
    Returns list[Voice]. Deterministic: same inputs -> same list, same order
    (sorted by (x,y)) -- the engine relies on stable ordering for phase
    continuity and the offline renderer for reproducibility."""
    raise NotImplementedError

G2.4 — audio/engine.py

"""
LOOM2 -- audio/engine.py
The real-time audio thread. OWNS the measure clock. Audio is king (VEDAS).
Allowed imports: numpy, math, threading, sounddevice, config, core.types,
audio.sampler. NO graphics imports ever.
Child chat scope: implement all bodies. ~300 lines expected. The hardest
audio module -- reserved for a strong child (or the Puranas parent).
"""
import numpy as np
import config
from core.types import Voice

class AudioEngine:
    """Thread-safety contract: set_* methods are called from the game thread;
    the sounddevice callback reads a single atomically-swapped snapshot
    (build new dict/list, then one reference assignment -- no locks in the
    callback)."""

    def __init__(self, library):                       # library: SampleLibrary
        raise NotImplementedError

    def start(self) -> None:
        """Open sounddevice.OutputStream with channels per current output
        mode; begin the callback."""
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError

    # ---- game-thread setters ----
    def set_voices(self, voices: list) -> None:
        """Swap in a new list[Voice]. Voices keep sample playback continuity
        keyed by (sample_a, stage_angle rounded) where possible; vanished
        voices get a 30 ms fade-out, new ones a 30 ms fade-in (no clicks)."""
        raise NotImplementedError

    def set_camera_azimuth(self, azimuth_deg: float) -> None:
        """THE surround input (SUTRAS 3.3/3.4). Zoom & elevation NEVER call this."""
        raise NotImplementedError

    def set_output_mode(self, mode: str) -> None:
        """'stereo' | 'surround_5_1' | 'surround_7_1' (config.OUTPUT_MODES).
        User-toggleable in options AT RUNTIME: close & reopen the stream with
        the new channel count; if the device refuses, fall back to stereo and
        report via get_status(). Panning law:
          pan_angle = voice.stage_angle_deg - camera_azimuth_deg
          stereo: constant-power L/R from pan_angle
          5.1/7.1: constant-power gains over the standard speaker azimuths
                   (LFE unused; center gets front-panned content)."""
        raise NotImplementedError

    # ---- shared clock (graphics reads these; lock-free) ----
    def get_measure_phase(self) -> float:
        """0..1 position inside the current 2.0 s measure. Drives the
        conductor's arm, ring pulses, icon flashes. Monotonic per measure."""
        raise NotImplementedError

    def get_active_flashes(self) -> list:
        """List of (voice_index, strike_strength 0..1) for notes struck in the
        last ~50 ms -- consumed by helix_panel for icon glow."""
        raise NotImplementedError

    def get_status(self) -> dict:
        """{'mode': str, 'device_channels': int, 'fallback_voices': int, ...}"""
        raise NotImplementedError

    # ---- the callback (private) ----
    def _callback(self, out: np.ndarray, frames: int, t, status) -> None:
        """Per block: measure phase; per voice: ring-pulse envelope with
        fractional-ring crossfade (ring n triggers n times/measure, all rings
        share the downbeat; ring 0 sustains/loops its sample), sample playback
        with per-voice position, equal-power a/b timbre blend, gain, pan to
        output channels. Sum, soft-clip via tanh, write."""
        raise NotImplementedError

    def render_block_offline(self, seconds: float) -> np.ndarray:
        """Same mix path WITHOUT a device: returns (N, 2) float32 stereo.
        Used by render_offline.py so quiz WAVs sound byte-identical to the
        live engine. MUST share code with _callback (one mixer, two callers)."""
        raise NotImplementedError

G2.5 — audio/render_offline.py

"""
LOOM2 -- audio/render_offline.py
DESIGN-TIME TOOL (not shipped in the EXE): renders quiz option WAVs.
Allowed imports: numpy, wave, json, argparse, config, core (types, surfaces),
audio (sampler, musicians, engine).
Child chat scope: implement all bodies. ~100 lines expected.
"""

def render_option(surface_name: str, totem_xy: tuple, hearing_radius: float,
                  z_per_octave: float, out_path: str) -> None:
    """Build voices at the given spot, run AudioEngine.render_block_offline
    for exactly config.OPTION_WAV_SECONDS (2 measures), write 16-bit stereo
    WAV at SAMPLE_RATE. Loop-clean: render starts on a downbeat and the
    buffer length is an exact multiple of the measure."""
    raise NotImplementedError

def main() -> None:
    """CLI: python -m audio.render_offline scenes/hannibal_saddle/options.json
    where options.json lists label -> {surface, xy, radius, out}.
    Prints a one-line report per file (duration, peak level)."""
    raise NotImplementedError

if __name__ == "__main__":
    main()

Seam summary for DeepSeek: game thread computes list[Voice] via musicians.build_voices whenever the totem moves → hands it to AudioEngine.set_voices. Camera orbit calls engine.set_camera_azimuth (azimuth only!). Graphics reads get_measure_phase / get_active_flashes. That's the entire audio↔rest-of-world seam — four calls.

End of Part 2. Say "continue" for Part 3 — the graphics module contracts (renderer.py, camera.py, terrain.py, totem.py, helix_panel.py, slice_mode.py, hud.py). 📜🎨
