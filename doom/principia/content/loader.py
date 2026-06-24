"""Loads a content pack (JSON) into validated pydantic models."""
from __future__ import annotations
from principia.schema import Level, AssetEntry


def load_level(pack_dir: str, level_id: str) -> Level:
    """Read concept_graph/floorplan/rooms/*.json -> a validated Level."""
    raise NotImplementedError("M1")


def load_manifest(pack_dir: str) -> dict[str, AssetEntry]:
    """Read manifest.json -> {block_id: AssetEntry}."""
    raise NotImplementedError("M1")


def validate_pack(pack_dir: str) -> list[str]:
    """Return a list of human-readable error strings; [] means the pack is OK."""
    raise NotImplementedError("M1")
