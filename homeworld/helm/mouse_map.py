"""MouseMapper: the Navigator's baseline device (NEW_TESTAMENT 2.2).

The pointer is the Navigator's ENTIRE interface: position in window
pixels (origin bottom-left, pyglet's native convention), primary and
secondary buttons, and accumulated wheel delta. The bridge module
consumes PointerState directly; there are no named Navigator buttons.
"""

from pyglet.window import mouse

from .actions import PointerState


class MouseMapper:
    def __init__(self, settings):
        self._x = 0.0
        self._y = 0.0
        self._primary = False
        self._secondary = False
        self._wheel = 0.0

    # ---- Mapper protocol ----

    def attach(self, window):
        window.push_handlers(
            on_mouse_motion=self._on_motion,
            on_mouse_drag=self._on_drag,
            on_mouse_press=self._on_press,
            on_mouse_release=self._on_release,
            on_mouse_scroll=self._on_scroll,
        )

    def poll_events(self):
        return []

    def poll_axes(self):
        return {}

    def poll_pointer(self):
        state = PointerState(
            x=self._x, y=self._y,
            primary=self._primary, secondary=self._secondary,
            wheel=self._wheel,
        )
        self._wheel = 0.0
        return state

    # ---- pyglet handlers ----

    def _on_motion(self, x, y, dx, dy):
        self._x, self._y = float(x), float(y)

    def _on_drag(self, x, y, dx, dy, buttons, modifiers):
        self._x, self._y = float(x), float(y)

    def _on_press(self, x, y, button, modifiers):
        if button & mouse.LEFT:
            self._primary = True
        if button & mouse.RIGHT:
            self._secondary = True

    def _on_release(self, x, y, button, modifiers):
        if button & mouse.LEFT:
            self._primary = False
        if button & mouse.RIGHT:
            self._secondary = False

    def _on_scroll(self, x, y, scroll_x, scroll_y):
        self._wheel += float(scroll_y)
