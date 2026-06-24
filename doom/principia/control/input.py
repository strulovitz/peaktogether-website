"""The ONLY module that touches input devices. Everything else asks here for
semantic actions, never raw keys. Mover = boyfriend; Shooter = girlfriend."""
from __future__ import annotations


class InputManager:
    def poll(self) -> None:
        """Call once per frame to refresh device state."""
        raise NotImplementedError("M2")

    # --- MOVER (boyfriend) ---
    def move_axis(self) -> tuple[float, float]:
        """(strafe, forward), each in [-1, 1]."""
        raise NotImplementedError("M2")

    def body_yaw_delta(self) -> float:
        raise NotImplementedError("M6")

    # --- SHOOTER (girlfriend) ---
    def aim_delta(self) -> tuple[float, float]:
        """(yaw_delta, pitch_delta)."""
        raise NotImplementedError("M2")

    def shoot_pressed(self) -> bool:
        """Edge-triggered: True on the frame the trigger goes down."""
        raise NotImplementedError("M2")

    # --- SHARED ---
    def toggle_map_pressed(self) -> bool:
        raise NotImplementedError("M4")

    def read_mode_pressed(self) -> bool:
        raise NotImplementedError("M3")

    def pause_pressed(self) -> bool:
        raise NotImplementedError("M2")
