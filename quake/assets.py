"""QUAKE runtime engine — M6 module #9: assets.py

Loads all baked content into a contracts.Pack and validates everything so the
renderers can trust the data blindly. Pure file I/O + validation; NO GL, NO
window. Fully testable headless.

All shared types come from contracts.py — never redefined here.
"""

from __future__ import annotations

import glob
import os

from contracts import (
    Pack,
    load_json,
    Floorplan,
    RoomRuntime,
    PanelPairRT,
    PanelPlacementRT,
    CeilingEqRT,
    DoorRT,
    Manifest,
    AssetEntry,
    Palette,
    GroupColor,
    NodeId,
    Vec3,
)


def load_pack(dir: str) -> Pack:
    """Load all baked content into a Pack.

    See module brief for the full contract. Validates the ID spine, asset
    references, PNG paths, and palette reserved keys. Raises ValueError
    (loudly, naming the offending id/path) on any validation failure.
    """
    # ------------------------------------------------------------------ #
    # 1. Load top-level JSON files (each asserts schema_version == "1.0").
    # ------------------------------------------------------------------ #
    floorplan: Floorplan = load_json(os.path.join(dir, "floorplan.json"), Floorplan)
    palette: Palette = load_json(os.path.join(dir, "palette.json"), Palette)
    manifest: Manifest = load_json(os.path.join(dir, "manifest.json"), Manifest)

    # ------------------------------------------------------------------ #
    # 2. Collect rooms: glob dir/room_runtime/room_*.json.
    # ------------------------------------------------------------------ #
    rooms: dict[NodeId, RoomRuntime] = {}
    room_glob = os.path.join(dir, "room_runtime", "room_*.json")
    for room_path in sorted(glob.glob(room_glob)):
        room: RoomRuntime = load_json(room_path, RoomRuntime)
        rooms[room.room_id] = room

    # ------------------------------------------------------------------ #
    # 3. Validate ID SPINE: every room_id must appear in floorplan.rooms.
    # ------------------------------------------------------------------ #
    floorplan_room_ids = {fr.room_id for fr in floorplan.rooms}
    for room_id in rooms:
        if room_id not in floorplan_room_ids:
            raise ValueError(
                f"ID spine mismatch: room_id {room_id!r} not present in "
                f"floorplan.rooms"
            )

    # ------------------------------------------------------------------ #
    # 4. Validate ASSET REFERENCES: every referenced asset_id must exist
    #    as a key in manifest.assets.
    # ------------------------------------------------------------------ #
    for room in rooms.values():
        for pair in room.panel_pairs:
            for asset_id in (
                pair.drawing_off_asset,
                pair.drawing_on_asset,
                pair.text_off_asset,
                pair.text_on_asset,
            ):
                if asset_id not in manifest.assets:
                    raise ValueError(
                        f"Missing asset reference: asset_id {asset_id!r} "
                        f"(referenced by room {room.room_id!r} pair "
                        f"{pair.pair_id!r}) not present in manifest.assets"
                    )
        for eq in room.ceiling_equations:
            if eq.asset_id not in manifest.assets:
                raise ValueError(
                    f"Missing asset reference: asset_id {eq.asset_id!r} "
                    f"(referenced by room {room.room_id!r} ceiling eq "
                    f"{eq.eq_id!r}) not present in manifest.assets"
                )

    # ------------------------------------------------------------------ #
    # 5. Validate PNG PATHS: wall_path and master_path must exist on disk.
    #    Paths are relative to `dir`. We DO NOT load pixels.
    # ------------------------------------------------------------------ #
    for asset_id, entry in manifest.assets.items():
        for rel_path in (entry.wall_path, entry.master_path):
            full_path = os.path.join(dir, rel_path)
            if not os.path.isfile(full_path):
                raise ValueError(
                    f"Missing PNG path: {full_path!r} (asset {asset_id!r}) "
                    f"does not exist on disk"
                )

    # ------------------------------------------------------------------ #
    # 6. Validate PALETTE reserved keys.
    #    grey_ink / grey_text / bg_key / map_node_default are guaranteed by
    #    pydantic. map_importance must contain "1".."5".
    # ------------------------------------------------------------------ #
    for key in ("1", "2", "3", "4", "5"):
        if key not in palette.map_importance:
            raise ValueError(
                f"Palette reserved key missing: map_importance[{key!r}] "
                f"is required but absent"
            )

    # ------------------------------------------------------------------ #
    # 7. asset_dir == dir (relative paths resolve from here).
    # ------------------------------------------------------------------ #
    return Pack(
        floorplan=floorplan,
        rooms=rooms,
        manifest=manifest,
        palette=palette,
        asset_dir=dir,
    )
