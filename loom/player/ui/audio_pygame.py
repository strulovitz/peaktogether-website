"""
audio_pygame.py — the real audio engine: a 16-voice pool over pygame.mixer. [MEAT]

Scripture: New Testament par.II.2. M0 (2026-07-06) proved this path on
Nir's PC: pygame 2.6.1 / SDL 2.28.4 loads real Philharmonia MP3s into
preloaded buffers, buffer 256 = 5.8 ms output latency (budget: <= 30 ms).

THE ONE RULE OF THIS MODULE: it plays recorded files it was handed —
nothing else. There is no synthesis of any kind here. A note becomes a
real file in exactly one place in the whole project (the Compiler's
library scan, compiler/library_scan.py); this engine just obeys.

This file is in ui/ because it imports pygame. Core logic never does.

DeepSeek items (behavior is the contract; exact pygame calls may be
adjusted freely if the real machine disagrees):
  - voice stealing below reuses the oldest channel directly; if Nir ever
    hears a click on very fast scrub flurries, refine with a short
    fadeout + reserve-channel scheme (steal_fade_ms is already in the
    tuning file, waiting).
"""

from __future__ import annotations

import os
import time
from typing import Sequence

import pygame


AUDIO_FREQ_HZ = 44100     # confirmed by M0
AUDIO_SIZE = -16          # 16-bit signed
AUDIO_CHANNELS = 2        # stereo
AUDIO_BUFFER = 256        # M0: 5.8 ms; pre-approved fallback: 512
NUM_VOICES = 16           # New Testament par.II.2


def init_mixer() -> None:
    """Call BEFORE pygame.init() (or any display init) for the small
    buffer to take effect. Safe to call once at app start."""
    pygame.mixer.pre_init(AUDIO_FREQ_HZ, AUDIO_SIZE, AUDIO_CHANNELS, AUDIO_BUFFER)


class AudioLoadError(Exception):
    """Plain-language error naming the file that failed."""


class PygameAudioEngine:
    """Implements the AudioSink protocol (player/core/audio.py).

    preload() decodes every sample fully into memory; trigger() starts a
    preloaded buffer on a free voice (stealing the oldest if all 16 are
    busy) and lets it ring to natural decay. Never blocks, never decodes
    during play.
    """

    def __init__(self) -> None:
        if not pygame.mixer.get_init():
            pygame.mixer.init(AUDIO_FREQ_HZ, AUDIO_SIZE, AUDIO_CHANNELS, AUDIO_BUFFER)
        pygame.mixer.set_num_channels(NUM_VOICES)
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._channels = [pygame.mixer.Channel(i) for i in range(NUM_VOICES)]
        self._started_at = [0.0] * NUM_VOICES   # for oldest-voice stealing

    # ---- AudioSink protocol ----

    def preload(self, base_dir: str, sample_paths: Sequence[str]) -> None:
        for rel in sample_paths:
            full = os.path.join(base_dir, rel) if base_dir else rel
            if not os.path.isfile(full):
                raise AudioLoadError(
                    f"Audio file not found: {full}\n"
                    f"(sample reference: {rel!r})")
            try:
                self._sounds[rel] = pygame.mixer.Sound(full)
            except Exception as e:
                raise AudioLoadError(
                    f"Could not decode audio file: {full}\n({e})")

    def trigger(self, sample_path: str, gain: float) -> None:
        sound = self._sounds.get(sample_path)
        if sound is None:
            raise AudioLoadError(
                f"trigger() called for a sample that was never preloaded: "
                f"{sample_path!r}")
        voice = self._find_voice()
        ch = self._channels[voice]
        ch.play(sound)                    # reusing a busy channel = stealing it
        ch.set_volume(max(0.0, min(1.0, gain)))
        self._started_at[voice] = time.monotonic()

    def stop_all(self, fade_ms: int) -> None:
        pygame.mixer.fadeout(max(0, int(fade_ms)))

    # ---- internals ----

    def _find_voice(self) -> int:
        for i, ch in enumerate(self._channels):
            if not ch.get_busy():
                return i
        # all busy: steal the OLDEST (New Testament par.II.2)
        return min(range(NUM_VOICES), key=lambda i: self._started_at[i])
