"""
menu_view.py — main menu / pack picker. [BONE M7]

Scripture: BIBLE par.6. Scans loom/packs/ for pack.json manifests,
shows warm titles, offers Continue (via core/progress.py). No network
(LOCKED). Player refuses packs with a newer major format_version —
with a kind message, never a crash.

FATTEN ME LIKE THIS (M7 parent): keep it humble — a list, a cursor,
Enter. The romance budget goes to the scenes, not the menu.
"""

from __future__ import annotations


class MenuView:
    """Frozen interface."""

    def __init__(self, rect, packs_dir: str) -> None:
        raise NotImplementedError("M7")

    def handle_action(self, action) -> str | None:
        """Returns "open_pack:<pack_id>" or None."""
        raise NotImplementedError("M7")

    def draw(self, surface) -> None:
        raise NotImplementedError("M7")
