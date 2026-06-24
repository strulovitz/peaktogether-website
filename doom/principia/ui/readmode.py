"""Crisp full-screen 2D overlay of a panel PNG (no perspective blur)."""
from __future__ import annotations


class ReadMode:
    def open(self, block_id: str, texture) -> None:
        raise NotImplementedError("M3")

    def close(self) -> None:
        raise NotImplementedError("M3")

    def is_open(self) -> bool:
        raise NotImplementedError("M3")
