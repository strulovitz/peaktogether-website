# LOOM2 — THE PURANAS — PART 1 of 3 — audio/engine.py — VERBATIM, WORD-FOR-WORD, AS-IS, BY FABLE (PARENT 2)

> Saved verbatim, word-for-word, as-is. This is the first PURANA — the king
> module, `audio/engine.py` — written by Claude Fable "Parent 2", July 7, 2026.
> The runnable code is also extracted to `loom2/audio/engine.py`.

---

GO received! 🎼 Here is the first PURANA — the king module, complete.

```python
"""
LOOM2 -- audio/engine.py
The real-time audio thread. OWNS the measure clock. Audio is king (VEDAS).
Allowed imports: numpy, math, threading, sounddevice, config, core.types,
audio.sampler. NO graphics imports ever.

CONTRACT AMENDMENT (approved by Nir, July 7 2026):
    AudioEngine.set_quiz_wav(path_or_None) -- quiz option WAVs play through
    this same engine and output path (required by GITA G4.3 _quiz_select).
    path=None stops playback (30 ms fade). Nothing else changed.

DESIGN NOTES (bodies only; frozen contracts untouched):

* Deterministic time. MEASURE_SAMPLES = MEASURE_SEC * SAMPLE_RATE = 88200,
  which divides EXACTLY by every ring count 1..NMAX_RING. Every pulse lane's
  playback position is therefore a PURE FUNCTION of the absolute sample
  counter: pos = t mod (MEASURE_SAMPLES // n). Consequences:
    - all rings share the downbeat by construction (VEDAS 3.3);
    - voice continuity across set_voices() swaps is automatic -- there is
      no per-voice phase state to hand over, the clock IS the phase;
    - render_block_offline() is byte-identical to live playback:
      ONE mixer (_mix), two callers (SUTRAS 5.3).
* Ring 0 sustains by looping its sample with a gentle linear fade at each
  seam (30 ms in / 45 ms out) -- a "bow change", never a click.
* Lock-free callback. Game-thread setters build fresh record lists and
  publish them with ONE reference assignment. The callback never locks,
  and is the only writer of the running fade/pan values.
* Listener model (SUTRAS 3.3/3.4). pan_angle = stage_angle - camera_azimuth
  (the frozen law). The listener stands at the totem facing the camera's
  12 o'clock: bearing = 90 - pan_angle (0 deg = front, positive = right).
  Stereo folds rear to front at constant power; 5.1/7.1 pan pairwise at
  constant power over standard ITU speaker bearings. LFE stays silent.
"""

import math
import threading

import numpy as np
import sounddevice as sd

import config
from core.types import Voice  # the ONLY audio handoff object (GITA G1.5)

# ---------------------------------------------------------------- constants
MEASURE_SAMPLES = int(round(config.MEASURE_SEC * config.SAMPLE_RATE))  # 88200
for _n in range(1, config.NMAX_RING + 1):
    assert MEASURE_SAMPLES % _n == 0, "measure must divide by every ring"

_FADE_SAMPLES = int(0.030 * config.SAMPLE_RATE)   # voice swap fade (G2.4)
_FLASH_SAMPLES = int(0.050 * config.SAMPLE_RATE)  # get_active_flashes window
_ATTACK_SEC = 0.008                                # pulse attack
_RELEASE_SEC = 0.050                               # pulse release tail
_INV_LOOP_IN = 1.0 / (0.030 * config.SAMPLE_RATE)  # ring-0 seam fade in
_INV_LOOP_OUT = 1.0 / (0.045 * config.SAMPLE_RATE) # ring-0 seam fade out
_INV_TAIL = 1.0 / (0.020 * config.SAMPLE_RATE)     # buffer-end click guard
_PRE_GAIN = 0.35                                   # headroom before tanh
_POST_GAIN = 0.95

_CHANNELS = {"stereo": 2, "surround_5_1": 6, "surround_7_1": 8}
# Speaker bearings, degrees clockwise from front; None = LFE (always silent).
# Channel order is the standard WAVE/WASAPI order sounddevice expects.
_BEARINGS = {
    "stereo": None,
    "surround_5_1": (-30.0, 30.0, 0.0, None, -110.0, 110.0),
    "surround_7_1": (-30.0, 30.0, 0.0, None, -150.0, 150.0, -90.0, 90.0),
}

# Pulse envelopes: one table per possible period, prebuilt (no callback alloc).
_PULSE_ENVS = {}
for _n in range(1, config.NMAX_RING + 1):
    _P = MEASURE_SAMPLES // _n
    _a = max(1, int(_ATTACK_SEC * config.SAMPLE_RATE))
    _r = min(max(1, int(_RELEASE_SEC * config.SAMPLE_RATE)), _P // 3)
    _e = np.ones(_P, np.float32)
    _e[:_a] = np.linspace(0.0, 1.0, _a, endpoint=False, dtype=np.float32)
    _e[_P - _r:] *= (0.5 * (1.0 + np.cos(
        np.linspace(0.0, math.pi, _r, dtype=np.float32)))).astype(np.float32)
    _PULSE_ENVS[_P] = _e


def _lanes(ring):
    """Fractional-ring crossfade law (VEDAS 3.3): between rings n and n+1,
    inner weight = (n+1)-r, outer = r-n. Returns ((n, weight), ...)."""
    if ring <= 0.0:
        return ((0, 1.0),)
    if ring >= config.NMAX_RING:
        return ((config.NMAX_RING, 1.0),)
    lo = int(ring)
    if float(lo) == ring:
        return ((lo, 1.0),)
    return ((lo, (lo + 1) - ring), (lo + 1, ring - lo))


def _load_wav_stereo(path):
    """Minimal RIFF reader for OUR OWN pre-rendered options (SUTRAS 5.3:
    16-bit PCM stereo @ SAMPLE_RATE). No new imports needed -- builtins+numpy."""
    with open(path, "rb") as fh:
        raw = fh.read()
    if raw[:4] != b"RIFF" or raw[8:12] != b"WAVE":
        raise ValueError(f"not a WAV file: {path}")
    fmt = data = None
    i = 12
    while i + 8 <= len(raw):
        cid = raw[i:i + 4]
        size = int.from_bytes(raw[i + 4:i + 8], "little")
        body = raw[i + 8:i + 8 + size]
        if cid == b"fmt ":
            fmt = body
        elif cid == b"data":
            data = body
        i += 8 + size + (size & 1)
    if fmt is None or data is None:
        raise ValueError(f"malformed WAV: {path}")
    channels = int.from_bytes(fmt[2:4], "little")
    rate = int.from_bytes(fmt[4:8], "little")
    bits = int.from_bytes(fmt[14:16], "little")
    if bits != 16 or rate != config.SAMPLE_RATE:
        raise ValueError(f"{path}: expected 16-bit @ {config.SAMPLE_RATE} Hz "
                         f"(got {bits}-bit @ {rate})")
    x = (np.frombuffer(data, dtype="<i2").astype(np.float32) / 32768.0)
    x = x.reshape(-1, channels)
    if channels == 1:
        x = np.repeat(x, 2, axis=1)
    return np.ascontiguousarray(x[:, :2])


class _VoiceRec:
    """Internal per-musician mixing record. Snapshot-published; the audio
    callback is the only writer of `fade` and `chan_gains` after publish."""
    __slots__ = ("buf_a", "buf_b", "g_a", "g_b", "ring", "stage_angle",
                 "gain", "key", "voice_index", "fade", "fade_target",
                 "chan_gains")

    def __init__(self, buf_a, buf_b, g_a, g_b, ring, stage_angle, gain,
                 key, voice_index):
        self.buf_a, self.buf_b = buf_a, buf_b
        self.g_a, self.g_b = g_a, g_b
        self.ring, self.stage_angle, self.gain = ring, stage_angle, gain
        self.key, self.voice_index = key, voice_index
        self.fade, self.fade_target = 0.0, 1.0
        self.chan_gains = None


class _QuizRec:
    __slots__ = ("buf", "pos", "fade", "fade_target")

    def __init__(self, buf):
        self.buf, self.pos = buf, 0
        self.fade, self.fade_target = 0.0, 1.0


class AudioEngine:
    """Thread-safety contract: set_* methods are called from the game thread;
    the sounddevice callback reads a single atomically-swapped snapshot
    (build new dict/list, then one reference assignment -- no locks in the
    callback)."""

    def __init__(self, library):                       # library: SampleLibrary
        self._library = library
        self._records = []          # snapshot: list[_VoiceRec]
        self._quiz = []             # snapshot: list[_QuizRec]
        self._azimuth = 0.0
        self._t = 0                 # absolute sample counter (callback-owned)
        self._phase = 0.0
        self._flashes = []
        self._stream = None
        self._io_lock = threading.Lock()   # start/stop/mode only; NOT callback
        self._mode = "stereo"
        self._requested_mode = "stereo"
        self._channels = 2
        self._spk = None            # (bearings 0..360 sorted, channel indices)
        self._underruns = 0
        self._error = ""
        self._set_layout("stereo")

    # ------------------------------------------------------------ lifecycle
    def start(self) -> None:
        """Open sounddevice.OutputStream with channels per current output
        mode; begin the callback."""
        with self._io_lock:
            if self._stream is not None:
                return
            try:
                self._open_stream(self._mode)
            except Exception as exc:
                if self._mode == "stereo":
                    raise
                self._error = f"{self._mode} failed ({exc}); stereo fallback"
                self._mode = "stereo"
                self._set_layout("stereo")
                self._open_stream("stereo")

    def stop(self) -> None:
        with self._io_lock:
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
                self._stream = None

    def _open_stream(self, mode):
        self._set_layout(mode)
        self._stream = sd.OutputStream(
            samplerate=config.SAMPLE_RATE, blocksize=config.BLOCK_SIZE,
            channels=_CHANNELS[mode], dtype="float32", callback=self._callback)
        self._stream.start()

    def _set_layout(self, mode):
        self._channels = _CHANNELS[mode]
        bearings = _BEARINGS[mode]
        if bearings is None:
            self._spk = None
        else:
            pairs = sorted((b % 360.0, ch) for ch, b in enumerate(bearings)
                           if b is not None)
            self._spk = ([b for b, _ in pairs], [ch for _, ch in pairs])

    # ------------------------------------------------- game-thread setters
    def set_voices(self, voices: list) -> None:
        """Swap in a new list[Voice]. Continuity is keyed by
        (sample_a, stage_angle rounded); since pulse phase is a pure function
        of the shared clock, matched voices continue seamlessly. Vanished
        voices get a 30 ms fade-out, new ones a 30 ms fade-in (no clicks)."""
        old = {}
        dying = []
        for r in self._records:
            if r.fade_target > 0.0:
                old.setdefault(r.key, r)
            elif r.fade > 1e-4:
                dying.append(r)               # still audibly fading out
        new_records = []
        for i, v in enumerate(voices):
            key = (v.sample_a, int(round(v.stage_angle_deg)))
            buf_a = self._library.get(v.sample_a)
            if v.blend > 1e-3:
                buf_b = self._library.get(v.sample_b)
            else:
                buf_b = None
            g_a = math.cos(v.blend * math.pi * 0.5)   # equal-power morph
            g_b = math.sin(v.blend * math.pi * 0.5)
            rec = _VoiceRec(buf_a, buf_b, g_a, g_b, v.ring,
                            v.stage_angle_deg, v.gain, key, i)
            prev = old.pop(key, None)
            if prev is not None:              # continuity: inherit ramps
                rec.fade = prev.fade
                rec.chan_gains = prev.chan_gains
            new_records.append(rec)
        for r in old.values():                # vanished -> 30 ms fade-out
            r.fade_target = 0.0
            r.voice_index = -1
            new_records.append(r)
        new_records.extend(dying)
        self._records = new_records           # ONE reference assignment

    def set_camera_azimuth(self, azimuth_deg: float) -> None:
        """THE surround input (SUTRAS 3.3/3.4). Zoom & elevation NEVER call this."""
        self._azimuth = float(azimuth_deg) % 360.0

    def set_output_mode(self, mode: str) -> None:
        """'stereo' | 'surround_5_1' | 'surround_7_1' (config.OUTPUT_MODES).
        Runtime toggle: close & reopen the stream with the new channel count;
        if the device refuses, fall back to stereo and report via get_status."""
        if mode not in config.OUTPUT_MODES:
            raise ValueError(f"mode must be one of {config.OUTPUT_MODES}")
        with self._io_lock:
            running = self._stream is not None
            if running:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            self._requested_mode = mode
            self._mode = mode
            self._error = ""
            if running:
                try:
                    self._open_stream(mode)
                except Exception as exc:
                    self._error = f"{mode} refused ({exc}); stereo fallback"
                    self._mode = "stereo"
                    self._open_stream("stereo")
            else:
                self._set_layout(self._mode)

    def set_quiz_wav(self, path) -> None:
        """AMENDMENT (approved): loop a pre-rendered option WAV through the
        same output path. path=None stops (30 ms fade). Mutual exclusion with
        live voices is game_state's discipline (G4.3); the mixer just mixes."""
        keep = [q for q in self._quiz if q.fade > 1e-4 or q.fade_target > 0.0]
        for q in keep:
            q.fade_target = 0.0
        if path is not None:
            keep.append(_QuizRec(_load_wav_stereo(path)))
        self._quiz = keep                     # ONE reference assignment

    # -------------------------------------------- shared clock (lock-free)
    def get_measure_phase(self) -> float:
        """0..1 position inside the current 2.0 s measure. Drives the
        conductor's arm, ring pulses, icon flashes. Monotonic per measure."""
        return self._phase

    def get_active_flashes(self) -> list:
        """List of (voice_index, strike_strength 0..1) for notes struck in the
        last ~50 ms -- consumed by helix_panel for icon glow."""
        return self._flashes

    def get_status(self) -> dict:
        recs, quiz = self._records, self._quiz
        live = sum(1 for r in recs if r.fade_target > 0.0)
        return {
            "mode": self._mode,
            "requested_mode": self._requested_mode,
            "device_channels": self._channels,
            "running": self._stream is not None,
            "live_voices": live,
            "dying_voices": len(recs) - live,
            "quiz_playing": any(q.fade_target > 0.0 for q in quiz),
            "underruns": self._underruns,
            "fallback_voices": int(getattr(self._library, "fallback_count", 0)),
            "error": self._error,
        }

    # ------------------------------------------------------- the callback
    def _callback(self, out: np.ndarray, frames: int, t, status) -> None:
        """Per block: measure phase; per voice: ring-pulse envelope with
        fractional-ring crossfade, sample playback, equal-power a/b timbre
        blend, gain, pan to output channels. Sum, soft-clip via tanh, write."""
        if status:
            self._underruns += 1
        t0 = self._t
        out[:] = self._mix(self._records, self._quiz, t0, frames,
                           out.shape[1])
        t1 = t0 + frames
        self._t = t1
        self._phase = (t1 % MEASURE_SAMPLES) / MEASURE_SAMPLES
        self._flashes = self._collect_flashes(self._records, t1)

    def render_block_offline(self, seconds: float) -> np.ndarray:
        """Same mix path WITHOUT a device: (N, 2) float32 stereo, starting on
        a downbeat (t=0), voices at full gain (deterministic, no entry swell).
        ONE mixer, two callers -- byte-identical to live play."""
        total = int(round(seconds * config.SAMPLE_RATE))
        clones = []
        for r in self._records:
            if r.fade_target <= 0.0:
                continue
            c = _VoiceRec(r.buf_a, r.buf_b, r.g_a, r.g_b, r.ring,
                          r.stage_angle, r.gain, r.key, r.voice_index)
            c.fade = 1.0                      # full gain from sample 0
            clones.append(c)
        out = np.zeros((total, 2), np.float32)
        t0 = 0
        while t0 < total:
            n = min(config.BLOCK_SIZE, total - t0)
            out[t0:t0 + n] = self._mix(clones, (), t0, n, 2)
            t0 += n
        return out

    # ------------------------------------------------ the ONE mixer core
    def _mix(self, records, quiz, t0, frames, channels):
        """Device-agnostic block mixer shared by _callback and
        render_block_offline. Mutates only the records it is handed."""
        rel = np.arange(frames, dtype=np.int64)
        abs_t = rel + t0
        u = np.linspace(0.0, 1.0, frames, dtype=np.float32)   # block ramp
        step = frames / _FADE_SAMPLES
        mix = np.zeros((frames, channels), np.float32)

        for rec in records:
            f0 = rec.fade
            f1 = (min(1.0, f0 + step) if rec.fade_target > 0.0
                  else max(0.0, f0 - step))
            if f0 <= 1e-4 and f1 <= 1e-4:
                rec.fade = 0.0
                continue                       # silent corpse; pruned later
            sig = self._voice_mono(rec, abs_t)
            g1 = self._pan_gains(rec.stage_angle, channels) * rec.gain
            g0 = rec.chan_gains
            if g0 is None or g0.shape[0] != channels:
                g0 = g1
            f = f0 + (f1 - f0) * u                             # fade ramp
            g = g0[None, :] + (g1 - g0)[None, :] * u[:, None]  # pan ramp
            mix += sig[:, None] * g * f[:, None]
            rec.fade = f1
            rec.chan_gains = g1

        for q in quiz:
            f0 = q.fade
            f1 = (min(1.0, f0 + step) if q.fade_target > 0.0
                  else max(0.0, f0 - step))
            if f0 <= 1e-4 and f1 <= 1e-4:
                q.fade = 0.0
                continue
            n = q.buf.shape[0]
            idx = (q.pos + rel) % n            # seamless loop (SUTRAS 5.3)
            f = f0 + (f1 - f0) * u
            seg = q.buf[idx]
            mix[:, 0] += seg[:, 0] * f
            mix[:, 1] += seg[:, 1] * f
            q.pos = int((q.pos + frames) % n)
            q.fade = f1

        mix *= _PRE_GAIN
        np.tanh(mix, out=mix)                  # soft-clip, never harsh
        mix *= _POST_GAIN
        return mix

    def _voice_mono(self, rec, abs_t):
        """One musician's mono block: fractional-ring pulse lanes over the
        equal-power a/b timbre pair. Pure function of absolute time."""
        sig = np.zeros(abs_t.shape[0], np.float32)
        for n, w in _lanes(rec.ring):
            if w <= 1e-4:
                continue
            for buf, g in ((rec.buf_a, rec.g_a), (rec.buf_b, rec.g_b)):
                if buf is None or g <= 1e-4:
                    continue
                L = buf.shape[0]
                wg = np.float32(w * g)
                if n == 0:                     # sustain: bow-change loop
                    pos = abs_t % L
                    env = (np.clip(pos * _INV_LOOP_IN, 0.0, 1.0)
                           * np.clip((L - pos) * _INV_LOOP_OUT, 0.0, 1.0)
                           ).astype(np.float32)
                    sig += wg * buf[pos] * env
                else:                          # n pulses, shared downbeat
                    P = MEASURE_SAMPLES // n
                    pos = abs_t % P
                    idx = np.minimum(pos, L - 1)
                    guard = np.clip((L - idx) * _INV_TAIL,
                                    0.0, 1.0).astype(np.float32)
                    sig += wg * buf[idx] * guard * _PULSE_ENVS[P][pos]
        return sig

    def _pan_gains(self, stage_angle, channels):
        """pan_angle = stage_angle - camera_azimuth (frozen law, G2.4).
        bearing = 90 - pan_angle: 0 = front (12 o'clock), positive = right."""
        bearing = (90.0 - (stage_angle - self._azimuth)) % 360.0
        g = np.zeros(channels, np.float32)
        if channels == 2:
            p = math.sin(math.radians(bearing))    # rear folds to front
            g[0] = math.sqrt(max(0.0, (1.0 - p) * 0.5))
            g[1] = math.sqrt(max(0.0, (1.0 + p) * 0.5))
            return g
        bs, chs = self._spk                        # pairwise constant power
        k = len(bs)
        i = k - 1
        for j in range(k):                         # <= 7 speakers: loop is fine
            if bs[j] <= bearing:
                i = j
        lo_b = bs[i]
        hi_b = bs[(i + 1) % k] + (360.0 if i == k - 1 else 0.0)
        b = bearing + (360.0 if bearing < lo_b else 0.0)
        frac = (b - lo_b) / max(1e-9, hi_b - lo_b)
        g[chs[i]] = math.cos(frac * math.pi * 0.5)
        g[chs[(i + 1) % k]] = math.sin(frac * math.pi * 0.5)
        return g

    def _collect_flashes(self, records, t_end):
        """Strikes are deterministic clock events; a lane struck within the
        last ~50 ms iff (t mod period) < window. Ring 0 flashes on downbeats."""
        out = []
        for rec in records:
            if rec.voice_index < 0 or rec.fade <= 1e-3:
                continue
            s = 0.0
            for n, w in _lanes(rec.ring):
                per = MEASURE_SAMPLES if n == 0 else MEASURE_SAMPLES // n
                if (t_end % per) < _FLASH_SAMPLES:
                    s = max(s, w)
            if s > 0.0:
                out.append((rec.voice_index, min(1.0, s * rec.fade)))
        return out
```

Delivery notes (for you and DeepSeek):

    The keystone trick: since 88200 divides exactly by every ring count 1..5, all pulse positions are pure functions of the global sample counter. No per-voice phase state exists — so voice continuity, shared downbeats, and byte-identical offline rendering all fall out of one design decision instead of three mechanisms.
    One mixer, two callers: _callback and render_block_offline both call _mix. Offline clones the records (fade forced to 1, no entry swell), forces stereo, starts at t=0 — a downbeat — so render_offline.py's loop-clean requirement is met by construction.
    Amendment implemented: set_quiz_wav(path_or_None), with a dependency-free RIFF reader (no new imports — the allowed-imports header stays true).
    One soft probe: get_status reads getattr(library, 'fallback_count', 0) — if Child B's sampler exposes that counter, status reports it; if not, 0. No contract strain.
    Honest small print: at a quiz WAV's loop seam, any sustained (ring-0) voices do a gentle bow-change rather than perfect continuity — pulsed lanes are perfectly seamless. Inaudible in practice; noted for completeness.
    Size report (G1.1 law): ~430 lines with its full documentation — slightly over the ~400 guideline; the header docstring is the overage and I judged it worth keeping. DeepSeek may trim comments if he disagrees.

Say "continue" and the second PURANA arrives: core/game_state.py — the conductor of everything. 🧿🎼
