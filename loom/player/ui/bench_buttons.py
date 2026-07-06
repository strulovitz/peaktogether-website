"""
bench_buttons.py — the OK / Cancel bench buttons. [M3 — Parent 4]

Scripture: BIBLE par.2 (OK/Cancel in fixed positions on the Bench) +
par.3.1 (OK commits the current note; Cancel clears the selection).
Parent 3 wrote a version that was never landed; this is Parent 4's,
matching the M2 widget family (pressed visual per bench_keyboard,
palette per bench_transport).

NO logic and NO audio in here: handle_event returns True exactly when
the button is activated (left-mouse released inside after pressing
inside — the standard forgiving button contract: dragging off before
release aborts). The wiring routes OK -> EchoLogic.commit() and
Cancel -> EchoLogic.cancel().

The wiring MUST keep OK disabled (.enabled = False) while EchoLogic
.preview_midi is None or the phase is not ECHOING — commit() raises on
misuse by design (wiring bugs fail loudly; players never do).

Keyboard mirrors (Enter = OK, Backspace = Cancel) belong to the
input-action layer in the wiring, NOT here — and must respect the
transport's .typing guard so the BPM box owns Enter while focused.
"""

from __future__ import annotations

import pygame

_BTN = (60, 60, 72)
_BTN_DISABLED = (42, 42, 50)
_TEXT = (225, 225, 225)
_TEXT_DISABLED = (110, 110, 120)
_OUTLINE = (70, 70, 80)
_SHADOW = (10, 10, 12)
_OK_ACCENT = (255, 196, 64)      # the family glow, on OK's outline only


class BenchButton:
    """Frozen interface. One fixed-position bench button."""

    def __init__(self, rect, label: str, accent: bool = False) -> None:
        self.rect = pygame.Rect(rect)
        self.label = label
        self.accent = accent          # OK gets the warm outline
        self.enabled = True
        self._down = False
        self._font = None

    def handle_event(self, pygame_event) -> bool:
        """Returns True exactly once per activation."""
        ev = pygame_event
        if not self.enabled:
            self._down = False
            return False
        if (ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1
                and self.rect.collidepoint(ev.pos)):
            self._down = True
        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
            was_down = self._down
            self._down = False
            if was_down and self.rect.collidepoint(ev.pos):
                return True
        return False

    def draw(self, surface) -> None:
        if self._font is None:
            self._font = pygame.font.SysFont("consolas", 16, bold=True)
        pressed = self._down and self.enabled
        body = self.rect.move(0, 3) if pressed else self.rect
        if pressed:
            pygame.draw.rect(surface, _SHADOW, self.rect, border_radius=4)
        color = _BTN if self.enabled else _BTN_DISABLED
        pygame.draw.rect(surface, color, body, border_radius=4)
        outline = (_OK_ACCENT if (self.accent and self.enabled)
                   else _OUTLINE)
        pygame.draw.rect(surface, outline, body, 1, border_radius=4)
        if not pressed and self.enabled:
            pygame.draw.line(surface, _SHADOW,
                             (body.x + 2, body.bottom - 1),
                             (body.right - 3, body.bottom - 1), 2)
        text_color = _TEXT if self.enabled else _TEXT_DISABLED
        img = self._font.render(self.label, True, text_color)
        surface.blit(img, img.get_rect(center=body.center))
