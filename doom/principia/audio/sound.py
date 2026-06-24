"""Sound effects (shoot, colorize, demon death, reveal). pygame.mixer."""
from __future__ import annotations


class Sound:
    def play(self, name: str) -> None:
        raise NotImplementedError("later")
