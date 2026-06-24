from __future__ import annotations

from ursina import Entity, Text, camera, color, destroy


class _ZoomImage(Entity):
    """Panel image that zooms on scroll, clamped to a sensible range."""

    _MIN = 0.3
    _MAX = 2.5

    def input(self, key):  # noqa: A003 - ursina hook name
        if key == 'scroll up':
            self._apply_zoom(1.1)
        elif key == 'scroll down':
            self._apply_zoom(0.9)

    def _apply_zoom(self, factor: float) -> None:
        new_x = self.scale_x * factor
        new_y = self.scale_y * factor
        if new_x < self._MIN or new_y < self._MIN:
            return
        if new_x > self._MAX or new_y > self._MAX:
            return
        self.scale = (new_x, new_y)


class ReadMode:
    """Full-screen 2D overlay showing a panel's texture flat for crisp reading."""

    def __init__(self) -> None:
        self._open = False
        self._entities: list = []
        self._block_id = None

    # --- the only methods that touch Ursina entities ---------------------

    def _build(self, texture) -> list:
        backdrop = Entity(
            parent=camera.ui,
            model='quad',
            scale=(2, 2),
            color=color.rgba(8, 8, 12, 235),
            z=1,
        )
        image = _ZoomImage(
            parent=camera.ui,
            model='quad',
            texture=texture,
            scale=(0.8, 0.8),
            position=(0, 0, 0),
            z=0,
        )
        hint = Text(
            parent=camera.ui,
            text="[R] / Esc to close   ·   scroll to zoom",
            origin=(0, 0),
            y=-0.46,
            scale=0.8,
            color=color.azure,
            z=-1,
        )
        return [backdrop, image, hint]

    def _destroy(self, entities) -> None:
        for e in entities:
            try:
                destroy(e)
            except Exception:
                pass

    # --- state machine ----------------------------------------------------

    def open(self, block_id: str, texture) -> None:
        if self._open:
            self.close()
        self._entities = self._build(texture)
        self._open = True
        self._block_id = block_id

    def close(self) -> None:
        if not self._open:
            return
        self._destroy(self._entities)
        self._entities = []
        self._open = False
        self._block_id = None

    def is_open(self) -> bool:
        return self._open
