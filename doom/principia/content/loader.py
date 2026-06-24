from __future__ import annotations

import json
import os
from typing import Any

from pydantic import ValidationError

from principia.config import SCHEMA_VERSION
from principia.schema import (
    AssetEntry,
    ConceptGraph,
    Floorplan,
    Level,
    RoomContent,
)


def _read_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _rooms_dir(pack_dir: str) -> str:
    return os.path.join(pack_dir, "rooms")


def _list_room_files(pack_dir: str) -> list[str]:
    rooms_dir = _rooms_dir(pack_dir)
    if not os.path.isdir(rooms_dir):
        return []
    return sorted(
        os.path.join(rooms_dir, name)
        for name in os.listdir(rooms_dir)
        if name.endswith(".json")
    )


def load_manifest(pack_dir: str) -> dict[str, AssetEntry]:
    path = os.path.join(pack_dir, "manifest.json")
    try:
        raw = _read_json(path)
    except FileNotFoundError as exc:
        raise ValueError(f"manifest.json not found in {pack_dir!r}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"manifest.json is not valid JSON: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValueError("manifest.json must be a JSON object of block_id -> entry")

    out: dict[str, AssetEntry] = {}
    for block_id, entry in raw.items():
        try:
            out[block_id] = AssetEntry.model_validate(entry)
        except ValidationError as exc:
            raise ValueError(
                f"manifest entry {block_id!r} failed validation: {exc}"
            ) from exc
    return out


def load_level(pack_dir: str, level_id: str) -> Level:
    # --- concept_graph.json (validated, but not stored in Level) ---
    cg_path = os.path.join(pack_dir, "concept_graph.json")
    try:
        cg = ConceptGraph.model_validate(_read_json(cg_path))
    except FileNotFoundError as exc:
        raise ValueError(f"concept_graph.json not found in {pack_dir!r}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"concept_graph.json is not valid JSON: {exc}") from exc
    except ValidationError as exc:
        raise ValueError(f"concept_graph.json failed validation: {exc}") from exc
    if cg.level_id != level_id:
        raise ValueError(
            f"concept_graph.json level_id {cg.level_id!r} != requested {level_id!r}"
        )

    # --- floorplan.json ---
    fp_path = os.path.join(pack_dir, "floorplan.json")
    try:
        floorplan = Floorplan.model_validate(_read_json(fp_path))
    except FileNotFoundError as exc:
        raise ValueError(f"floorplan.json not found in {pack_dir!r}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"floorplan.json is not valid JSON: {exc}") from exc
    except ValidationError as exc:
        raise ValueError(f"floorplan.json failed validation: {exc}") from exc
    if floorplan.level_id != level_id:
        raise ValueError(
            f"floorplan.json level_id {floorplan.level_id!r} != requested {level_id!r}"
        )

    # --- rooms/*.json (load whatever exists; do not crash on absent rooms) ---
    rooms: dict[str, RoomContent] = {}
    for room_path in _list_room_files(pack_dir):
        try:
            room = RoomContent.model_validate(_read_json(room_path))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{room_path} is not valid JSON: {exc}") from exc
        except ValidationError as exc:
            raise ValueError(f"{room_path} failed validation: {exc}") from exc
        rooms[room.room_id] = room

    return Level(level_id=level_id, floorplan=floorplan, rooms=rooms)


def validate_pack(pack_dir: str) -> list[str]:
    errors: list[str] = []

    # ---- concept_graph.json ----
    cg: ConceptGraph | None = None
    cg_path = os.path.join(pack_dir, "concept_graph.json")
    try:
        cg = ConceptGraph.model_validate(_read_json(cg_path))
        if cg.schema_version != SCHEMA_VERSION:
            errors.append(
                f"concept_graph.json schema_version {cg.schema_version!r} "
                f"!= {SCHEMA_VERSION!r}"
            )
    except FileNotFoundError:
        errors.append("concept_graph.json not found")
    except json.JSONDecodeError as exc:
        errors.append(f"concept_graph.json is not valid JSON: {exc}")
    except ValidationError as exc:
        errors.append(f"concept_graph.json failed validation: {exc}")

    # ---- floorplan.json ----
    floorplan: Floorplan | None = None
    fp_path = os.path.join(pack_dir, "floorplan.json")
    try:
        floorplan = Floorplan.model_validate(_read_json(fp_path))
        if floorplan.schema_version != SCHEMA_VERSION:
            errors.append(
                f"floorplan.json schema_version {floorplan.schema_version!r} "
                f"!= {SCHEMA_VERSION!r}"
            )
    except FileNotFoundError:
        errors.append("floorplan.json not found")
    except json.JSONDecodeError as exc:
        errors.append(f"floorplan.json is not valid JSON: {exc}")
    except ValidationError as exc:
        errors.append(f"floorplan.json failed validation: {exc}")

    # ---- manifest.json ----
    mf_path = os.path.join(pack_dir, "manifest.json")
    try:
        raw_mf = _read_json(mf_path)
        if not isinstance(raw_mf, dict):
            errors.append("manifest.json must be a JSON object of block_id -> entry")
        else:
            for block_id, entry in raw_mf.items():
                try:
                    AssetEntry.model_validate(entry)
                except ValidationError as exc:
                    errors.append(
                        f"manifest entry {block_id!r} failed validation: {exc}"
                    )
    except FileNotFoundError:
        errors.append("manifest.json not found")
    except json.JSONDecodeError as exc:
        errors.append(f"manifest.json is not valid JSON: {exc}")

    # ---- rooms/*.json ----
    rooms: dict[str, RoomContent] = {}
    for room_path in _list_room_files(pack_dir):
        try:
            room = RoomContent.model_validate(_read_json(room_path))
            if room.schema_version != SCHEMA_VERSION:
                errors.append(
                    f"{room_path} schema_version {room.schema_version!r} "
                    f"!= {SCHEMA_VERSION!r}"
                )
            rooms[room.room_id] = room
        except json.JSONDecodeError as exc:
            errors.append(f"{room_path} is not valid JSON: {exc}")
        except ValidationError as exc:
            errors.append(f"{room_path} failed validation: {exc}")

    # ---- cross-checks (only if floorplan parsed) ----
    if floorplan is not None:
        room_ids = {rc.id for rc in floorplan.rooms}
        door_ids = {d.id for d in floorplan.doors}

        # every floorplan room must have a rooms/<id>.json
        for rid in room_ids:
            if rid not in rooms:
                errors.append(
                    f"floorplan room {rid!r} has no matching rooms/{rid}.json"
                )

        # every RoomContent.room_id must be in floorplan.rooms
        for rid in rooms:
            if rid not in room_ids:
                errors.append(
                    f"rooms/{rid}.json room_id {rid!r} not present in floorplan.rooms"
                )

        # every door referenced by a room cell must exist in floorplan.doors
        for rc in floorplan.rooms:
            for door_id in rc.doors:
                if door_id not in door_ids:
                    errors.append(
                        f"floorplan room {rc.id!r} references door {door_id!r} "
                        f"not in floorplan.doors"
                    )

        # every corridor from/to must be an existing room id
        for corr in floorplan.corridors:
            if corr.from_room not in room_ids:
                errors.append(
                    f"corridor {corr.id!r} 'from' room {corr.from_room!r} "
                    f"is not an existing room id"
                )
            if corr.to_room not in room_ids:
                errors.append(
                    f"corridor {corr.id!r} 'to' room {corr.to_room!r} "
                    f"is not an existing room id"
                )

    return errors
