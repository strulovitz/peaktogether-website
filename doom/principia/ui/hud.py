"""Reticle, prompts, reading-progress indicator."""
from __future__ import annotations


class HUD:
    def update(self, ctx) -> None:
        raise NotImplementedError("M2")
