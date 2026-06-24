"""
app.py — full-game entry point (NOT the demo). Wires managers and drives the
per-frame update order. Implemented incrementally; run m0_demo.py for now.

Per-frame order: input.poll -> mover -> shooter -> navigator
                 -> demon/ceiling updates -> hud/map/readmode.
"""
from __future__ import annotations


def main(pack: str, level: str) -> None:
    raise NotImplementedError("Built across M1..M6; use m0_demo.py today.")


if __name__ == "__main__":
    main("content_packs/principia", "fixture")
