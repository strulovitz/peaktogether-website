"""The QED / Halmos-tombstone tile. Shooting it opens it and spawns a boss."""
from __future__ import annotations
from principia.schema import SecretDoorSpec


class SecretDoor:
    def __init__(self, spec: SecretDoorSpec) -> None:
        raise NotImplementedError("M5")

    def shoot(self) -> None:
        raise NotImplementedError("M5")

    def on_boss_killed(self, callback) -> None:
        raise NotImplementedError("M5")
