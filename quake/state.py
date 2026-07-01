"""state.py (M7, module #12) — owns GameState and its persistence as SaveGame.

This module is pure serialization + atomic file I/O. It contains NO GL and NO
window code, so it is fully testable headless.

DIVISION OF LABOR: state.py does serialization + atomic IO. gameplay.py is the
ONLY writer of progress semantics. state.py never decides game rules.
"""

import os
import warnings

from contracts import (
    GameState,
    SaveGame,
    PlayerSave,
    LevelProgress,
    RoomProgress,
    Pack,
    Floorplan,
    FloorRoom,
    NodeId,
    LevelId,
    Vec3,
    load_json,
)


def new_state(pack: Pack, profile_id: str = "default") -> GameState:
    """Create a fresh GameState for a new game. Starts inside the first room."""
    start_room: FloorRoom = min(pack.floorplan.rooms, key=lambda r: r.room_id)
    room_id: NodeId = start_room.room_id
    room_rt = pack.rooms.get(room_id)

    # Default spawn: first door, or room center at floor level.
    pos: Vec3 = (0.0, 0.0, 0.0)
    heading: float = 0.0
    if room_rt is not None and room_rt.doors:
        first_door = room_rt.doors[0]
        pos = first_door.spawn_xyz
        heading = first_door.spawn_heading_rad

    level_id: LevelId = pack.floorplan.level_id

    save_game = SaveGame(
        schema_version="1.0",
        profile_id=profile_id,
        levels={level_id: LevelProgress()},
        player=PlayerSave(
            level_id=level_id,
            mode="room",
            current_room_id=room_id,
            position_xyz=pos,
            heading_rad=heading,
        ),
    )

    return GameState(
        save=save_game,
        mode="room",
        current_room_id=room_id,
        pos=pos,
        heading_rad=heading,
        pitch_rad=0.0,
        lit=set(),
        cleared=set(),
    )


def state_to_save(state: GameState) -> SaveGame:
    """Convert runtime GameState -> persisted SaveGame. PURE helper.

    Returns a NEW SaveGame (does not mutate state.save in place).
    pitch is NOT written (PlayerSave has no pitch field).
    """
    old_player = state.save.player

    new_player = PlayerSave(
        level_id=old_player.level_id,
        mode=state.save.player.mode,
        current_room_id=state.save.player.current_room_id,
        position_xyz=state.pos,
        heading_rad=state.heading_rad,
    )

    # Deep-copy levels so we don't share/mutate the original dict.
    new_levels: dict[LevelId, LevelProgress] = {
        lvl_id: lp.model_copy(deep=True) for lvl_id, lp in state.save.levels.items()
    }

    return SaveGame(
        schema_version="1.0",
        profile_id=state.save.profile_id,
        levels=new_levels,
        player=new_player,
    )


def save_to_state(save: SaveGame, pack: Pack) -> GameState:
    """Rebuild runtime GameState from a loaded SaveGame. PURE helper.

    pitch_rad always resets to 0.0 (runtime-only).
    lit = union of all pairs_on across all rooms of the current level.
    cleared = set of room_ids where room_cleared is True for the current level.
    """
    pos: Vec3 = save.player.position_xyz
    heading_rad: float = save.player.heading_rad
    mode = save.player.mode
    current_room_id: NodeId | None = save.player.current_room_id

    level_id: LevelId = pack.floorplan.level_id

    lit: set[str] = set()
    cleared: set[NodeId] = set()

    level_progress = save.levels.get(level_id)
    if level_progress is not None:
        for room_id, room_prog in level_progress.rooms.items():
            for pair_id in room_prog.pairs_on:
                lit.add(pair_id)
            if room_prog.room_cleared:
                cleared.add(room_id)

    return GameState(
        save=save,
        mode=mode,
        current_room_id=current_room_id,
        pos=pos,
        heading_rad=heading_rad,
        pitch_rad=0.0,
        lit=lit,
        cleared=cleared,
    )


def save(state: GameState, path: str) -> None:
    """Atomically persist the GameState to disk."""
    save_game = state_to_save(state)
    payload = save_game.model_dump_json(indent=2)

    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)

    tmp_path = path + ".atomic_tmp"

    try:
        # Write + flush + fsync the temp file.
        fd = os.open(tmp_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(payload)
                f.flush()
                os.fsync(f.fileno())
        except Exception:
            # fdopen took ownership of fd; fd already closed on exit.
            raise

        # Atomic rename on the same filesystem.
        os.replace(tmp_path, path)
    except Exception:
        # Clean up the temp file if anything failed.
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except OSError:
            pass
        raise


def load(path: str, pack: Pack) -> GameState:
    """Load persisted GameState from disk.

    Reads + validates SaveGame (asserts schema_version == "1.0"), drops any
    progress for rooms that no longer exist in the current pack, then rebuilds
    the runtime GameState.
    """
    save_game: SaveGame = load_json(path, SaveGame)

    # Forward-compat: drop progress for rooms not in the current pack.
    for level_id, level_progress in save_game.levels.items():
        stale_room_ids = [
            room_id
            for room_id in level_progress.rooms
            if room_id not in pack.rooms
        ]
        for room_id in stale_room_ids:
            del level_progress.rooms[room_id]
            warnings.warn(
                f"Dropping progress for unknown room '{room_id}' in level "
                f"'{level_id}' (not present in current pack).",
                stacklevel=2,
            )

    return save_to_state(save_game, pack)
