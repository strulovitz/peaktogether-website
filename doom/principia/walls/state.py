from __future__ import annotations

import json
import os
from typing import Any

import principia.config as config


class WallStateManager:
    """Tracks per-block read/not-read state, swaps panel textures, reports
    per-room progress, and persists the 'blocks_on' slice of the save file.

    Does NOT import ursina. It only assigns attributes (entity.texture,
    entity.is_on) on whatever entity object it is given, so it is fully
    unit-testable with fake entities.
    """

    def __init__(self, assets) -> None:
        # 'assets' is an AssetManager, reserved/unused in M2. Stored only.
        self._assets = assets
        # block_id -> {"room_id", "entity", "off_tex", "on_tex", "is_on"}
        self._blocks: dict[str, dict] = {}
        # room_id -> set of block_ids
        self._rooms: dict[str, set[str]] = {}
        # authoritative set of block ids currently 'on', including ids from
        # rooms not yet registered (persisted; consulted at register time so
        # save/load is order-independent under lazy room loading).
        self._restore_on: set[str] = set()

    def register(self, room_id: str, block_id: str, entity, off_tex, on_tex) -> None:
        is_on = block_id in self._restore_on
        self._blocks[block_id] = {
            "room_id": room_id,
            "entity": entity,
            "off_tex": off_tex,
            "on_tex": on_tex,
            "is_on": is_on,
        }
        self._rooms.setdefault(room_id, set()).add(block_id)
        self._apply_visual(block_id)

    def toggle(self, block_id: str) -> bool:
        rec = self._blocks[block_id]  # raises KeyError if not registered
        rec["is_on"] = not rec["is_on"]
        if rec["is_on"]:
            self._restore_on.add(block_id)
        else:
            self._restore_on.discard(block_id)
        self._apply_visual(block_id)
        return rec["is_on"]

    def state(self, block_id: str) -> bool:
        return self._blocks[block_id]["is_on"]  # raises KeyError if unknown

    def progress(self, room_id: str) -> float:
        block_ids = self._rooms.get(room_id)
        if not block_ids:
            return 0.0
        total = len(block_ids)
        on = sum(1 for bid in block_ids if self._blocks[bid]["is_on"])
        return on / total

    def save(self, path: str) -> None:
        data: dict[str, Any] = {}
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    loaded = json.load(fh)
                if isinstance(loaded, dict):
                    data = loaded
            except (OSError, json.JSONDecodeError):
                data = {}

        data["schema_version"] = config.SCHEMA_VERSION
        data["blocks_on"] = sorted(self._restore_on)

        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    def load(self, path: str) -> None:
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        self._restore_on = set(data.get("blocks_on", []))

        for block_id, rec in self._blocks.items():
            rec["is_on"] = block_id in self._restore_on
            self._apply_visual(block_id)

    def _apply_visual(self, block_id: str) -> None:
        rec = self._blocks[block_id]
        entity = rec["entity"]
        is_on = rec["is_on"]
        entity.texture = rec["on_tex"] if is_on else rec["off_tex"]
        entity.is_on = is_on
