"""
story_view.py — slides, captions, dialogue. [BONE M5]

Scripture: BIBLE par.5-6 + Apocrypha. Baked Pixar-style PNG per scene,
caption, branching dialogue menus (up to 4 options, Player K drives),
next/back, then hand off to the scene's puzzle. Heroes are ONLY ever
"Girlfriend" and "Boyfriend" (LOCKED). Warm, forgiving, no timers.

FATTEN ME LIKE THIS (M5 parent): consume pack_model dataclasses; emit
what the app loop needs: dialogue choice made / scene finished /
start puzzle X. Text rendering with pygame fonts; images pre-scaled
to layout.SCENE_STAGE. No game logic in here — presentation only.
"""

from __future__ import annotations


class StoryView:
    """Frozen interface."""

    def __init__(self, rect) -> None:
        raise NotImplementedError("M5")

    def show_scene(self, pack, scene) -> None:
        raise NotImplementedError("M5")

    def handle_action(self, action) -> str | None:
        """Returns "scene_done" / "start_puzzle:<id>" / None."""
        raise NotImplementedError("M5")

    def draw(self, surface) -> None:
        raise NotImplementedError("M5")
