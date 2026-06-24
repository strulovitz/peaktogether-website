Excellent — three milestones in and the pipeline is humming! 🎉 The fact that the data-driven room reads left-to-right and panels flip on shot means the whole content→geometry→texture chain is solid.

Now for M2. As the architect, I'm splitting it the same way we split M1 (→ M1 + M1b), because it gives us better tests and cleaner children:

    M2a (this child): walls/state.py — the sticky off↔on state engine + save/load. This is the data backbone and is 100% unit-testable headless (no Ursina, no window), so it deserves a focused child with thorough tests.
    M2b (next child): control/input.py + player/shooter.py + m2_demo.py — the interactive glue (keyboard+mouse → raycast → calls into WallStateManager), best validated together by the demo.

    ⚠️ Architect interface decision (tell DeepSeek to update the ledger): the master doc's frozen WallStateManager.register(block_id, entity, off_tex, on_tex) is missing the room context that progress(room_id) needs. I'm explicitly versioning it to register(room_id, block_id, entity, off_tex, on_tex). This is the new frozen signature.

Copy everything between the markers into a fresh Opus chat. 🙂
=== BEGIN M2a CHILD PROMPT (walls/state.py) ===
ROLE

You are an implementation child for the Principia Descent educational FPS engine (Python 3.11, Windows, Ursina/Panda3D). You implement one runtime module to its frozen contract, plus tests. You do not touch other modules and you do not change any frozen signature except the one explicitly versioned below. Your memory is expendable — ask "Nir" for any file I didn't include before writing code.

Architecture rule: modules talk only through typed signatures and the pydantic contracts in principia/schema.py. Never import another module's internals.
YOUR TASK

Implement principia/walls/state.py: the manager that tracks each wall block's off/on ("not-read"/"read") state, swaps the panel entity's texture accordingly, reports per-room reading progress, and persists state to a save file. Produce:

    principia/walls/state.py
    tests/test_state.py

This module must NOT import ursina. It only assigns attributes (entity.texture, entity.is_on) on whatever entity object it's given. This makes it fully unit-testable with fake entities.
FROZEN CONTRACT (note the versioned register)

class WallStateManager:
    def __init__(self, assets) -> None: ...                      # 'assets' is an AssetManager; reserved/unused in M2
    def register(self, room_id: str, block_id: str, entity, off_tex, on_tex) -> None: ...  # VERSIONED: room_id added
    def toggle(self, block_id: str) -> bool: ...                 # flips state; returns new state (True = on)
    def state(self, block_id: str) -> bool: ...                  # current state
    def progress(self, room_id: str) -> float: ...              # fraction of that room's blocks that are 'on' (0..1)
    def save(self, path: str) -> None: ...
    def load(self, path: str) -> None: ...

BINDING DECISIONS (do not deviate)

__init__(self, assets)

    Store assets for future use; do not call any method on it in M2 (so tests may pass None). Initialize internal structures.

Internal model (recommended):

    self._blocks: dict[str, dict] mapping block_id -> {"room_id", "entity", "off_tex", "on_tex", "is_on"}.
    self._rooms: dict[str, set[str]] mapping room_id -> set of block_ids.
    self._restore_on: set[str] — the authoritative set of block ids that are "on", including blocks from rooms not yet registered. This is what gets persisted, and it's consulted at register time so save/load is order-independent under lazy room loading.

register(room_id, block_id, entity, off_tex, on_tex)

    Compute initial is_on = block_id in self._restore_on.
    Store the record, add block_id to self._rooms[room_id].
    Apply the visual immediately: entity.texture = on_tex if is_on else off_tex and entity.is_on = is_on.
    Re-registering an existing block_id overwrites silently.

toggle(block_id) -> bool

    Flip is_on (literal toggle — off→on and on→off both allowed; the caller enforces "sticky on" by only toggling off→on during normal play; on→off is reserved for future spaced-repetition).
    Apply the visual (entity.texture, entity.is_on), and keep self._restore_on in sync (add if now on, discard if now off).
    Return the new state. Raise KeyError if block_id is not registered.

state(block_id) -> bool — return is_on; raise KeyError if not registered.

progress(room_id) -> float — 0.0 if the room has no registered blocks (no division by zero); otherwise count(on) / count(total) for that room's registered blocks.

save(path) — merge-friendly, forward-compatible

    If the file already exists, read it into a dict first (so other managers' future fields like demons_dead/secrets_open are preserved). If it doesn't exist or is unreadable, start from {}.
    Set data["schema_version"] = principia.config.SCHEMA_VERSION and data["blocks_on"] = sorted(self._restore_on).
    Write JSON (UTF-8, indent=2). Create parent directories if needed.

load(path)

    If the file doesn't exist, do nothing (treat as empty/fresh).
    Read it; set self._restore_on = set(data.get("blocks_on", [])).
    Re-apply to every currently registered block: set its is_on to membership in self._restore_on, update entity.texture and entity.is_on. Block ids in the file that aren't registered yet are left in self._restore_on so they're applied when their room registers later (order-independence).

TESTS YOU MUST WRITE — tests/test_state.py (fully headless; use fakes)

Use simple fakes so no Ursina is needed:

class FakeEntity:
    def __init__(self): self.texture = None; self.is_on = False
OFF = "OFF_TEX"; ON = "ON_TEX"   # any sentinel objects

Cover at least:

    toggle flips and updates visuals: register a block (off); toggle returns True, entity.texture is ON, entity.is_on is True; toggle again returns False, entity.texture is OFF.
    state() reflects current value; unknown block_id raises KeyError for both state and toggle.
    progress(): register 2 blocks in "room1"; progress 0.0; toggle one on → 0.5; both on → 1.0. progress("nonexistent") → 0.0.
    save/load round-trip: toggle some blocks on, save(tmp_path/'s.json'); build a new manager, register the same blocks, load(...), assert each block's state() and entity.texture match what was saved.
    order-independence: new manager, load(...) before registering, then register a block whose id was on in the file → it must initialize to on (entity.texture is ON).
    merge preserves foreign keys: pre-write a file containing {"demons_dead": ["d1"]}, call save, re-read the file, assert "demons_dead" is still ["d1"] and "blocks_on" is present.
    schema_version is written and equals principia.config.SCHEMA_VERSION.
    __init__(None) works (assets unused in M2).

OUTPUT FORMAT

First confirm in one line that you have everything (or ask for a missing file). Then output two separate copy-paste code blocks, each preceded by its bold file path: principia/walls/state.py, tests/test_state.py. End with one line for DeepSeek: the exact pytest command and what "pass" looks like.
REFERENCE FILES (already in the repo — do not rewrite)

principia/config.py (relevant constant):

SCHEMA_VERSION: str = "1.0"

principia/schema.py — SaveGame (for reference only; you do NOT need to strictly validate against it in M2, but your blocks_on field matches it):

class SaveGame(_Base):
    schema_version: str = SCHEMA_VERSION
    level_id: str
    blocks_on: list[str] = Field(default_factory=list)
    demons_dead: list[str] = Field(default_factory=list)
    secrets_open: list[str] = Field(default_factory=list)

    Note: SaveGame.level_id is required, but WallStateManager does not know the level id and must not write it. A future "save coordinator" will own level_id and orchestrate all managers; for now you only own the blocks_on slice, written via read-modify-write so other slices are preserved.

AssetManager (passed to __init__; do not call it in M2):

class AssetManager:
    def __init__(self, pack_dir: str) -> None: ...
    def wall_textures(self, block_id: str): ...   # -> (off_texture, on_texture)

Context — the panel entities you'll be given at runtime carry these attributes (set by world/builder.py), so assigning entity.texture and entity.is_on is exactly what's expected:

panel.kind = "panel"; panel.block_id = ...; panel.off_tex = ...; panel.on_tex = ...; panel.is_on = False

Current stub principia/walls/state.py (replace; the __init__/register/toggle signatures shown there are the OLD ones — use the VERSIONED register from this brief):

from __future__ import annotations
from principia.assets.manager import AssetManager

class WallStateManager:
    def __init__(self, assets: AssetManager) -> None:
        raise NotImplementedError("M2")
    def register(self, block_id: str, entity, off_tex, on_tex) -> None:  # OLD — replace with versioned signature
        raise NotImplementedError("M2")
    def toggle(self, block_id: str) -> bool:
        raise NotImplementedError("M2")
    def state(self, block_id: str) -> bool:
        raise NotImplementedError("M2")
    def progress(self, room_id: str) -> float:
        raise NotImplementedError("M2")
    def save(self, path: str) -> None:
        raise NotImplementedError("M2")
    def load(self, path: str) -> None:
        raise NotImplementedError("M2")

=== END M2a CHILD PROMPT ===

Notes for you, Nir:

    This child produces no demo (state isn't visual on its own) — but it'll have the richest test suite yet (toggle, progress, save/load round-trip, lazy-load order-independence, save-file merging). That save-merge design is important groundwork: it's what lets the demon manager (M3) and secret-door manager (M5) later write their slices into the same save file without clobbering each other.
    Tell DeepSeek to note the register signature version bump in the project ledger, so when M1b's builder eventually hands panels to this manager (in M2b's demo), it passes room_id too.

When DeepSeek reports green, M2b wires it all together: real control/input.py (keyboard+mouse, with the mover/shooter split designed so it's trivial to add the Xbox/joystick in M6) + player/shooter.py (raycast → dispatch to wall/demon/secret handlers) + m2_demo.py (the throwaway shoot-glue from m1_demo.py gets promoted into the real, save/load-able coloring loop). Want me to draft M2b next, or pause so you can run M2a first? 🙂
