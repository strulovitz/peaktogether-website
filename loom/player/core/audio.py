"""
audio.py — the AudioSink contract + the test fake. [MEAT]

Scripture: New Testament par.II.2. The Conductor never touches audio
directly (par.II.9 headless-testing doctrine): the wiring layer forwards
ConductorFrame.triggers to an AudioSink. Two implementations exist:

  - FakeAudioSink (here): records calls; used by every headless test.
  - PygameAudioEngine (player/ui/audio_pygame.py): the real 16-voice pool.

Imports: standard library ONLY.
"""

from __future__ import annotations

from typing import Protocol, Sequence


class AudioSink(Protocol):
    """What the game needs from any audio backend. Frozen interface."""

    def preload(self, base_dir: str, sample_paths: Sequence[str]) -> None:
        """Decode every sample fully into memory, BEFORE play begins
        (never during — BIBLE par.7.3). sample_paths are the relative
        paths exactly as written in the spell JSON; base_dir is the
        folder they are relative to. Must raise a plain-language error
        naming any file that fails."""
        ...

    def trigger(self, sample_path: str, gain: float) -> None:
        """Start the preloaded buffer from its beginning at this gain and
        let it ring to its natural decay (never cut at note end — real
        instruments overlapping is warm, not wrong). Must never block."""
        ...

    def stop_all(self, fade_ms: int) -> None:
        """Fade out everything currently sounding (stop button, scene
        changes)."""
        ...


class FakeAudioSink:
    """Records every call, for assertions in headless tests.

    Raises KeyError if a sample is triggered without being preloaded —
    the same mistake would be a crash in the real engine, so tests
    should catch it early.
    """

    def __init__(self) -> None:
        self.preloaded: set[str] = set()
        self.triggered: list[tuple[str, float]] = []   # (sample_path, gain)
        self.stop_all_calls: list[int] = []            # fade_ms values

    def preload(self, base_dir: str, sample_paths: Sequence[str]) -> None:
        self.preloaded.update(sample_paths)

    def trigger(self, sample_path: str, gain: float) -> None:
        if sample_path not in self.preloaded:
            raise KeyError(
                f"FakeAudioSink: {sample_path!r} was triggered but never "
                f"preloaded — the wiring forgot to preload the spell.")
        self.triggered.append((sample_path, gain))

    def stop_all(self, fade_ms: int) -> None:
        self.stop_all_calls.append(fade_ms)
