from __future__ import annotations

from dataclasses import dataclass

from principia.schema import RoomCell, Corridor, RoomContent, Rect, Facing
from principia.assets.manager import AssetManager
from principia.config import CEILING_H, WALL_THICKNESS

# Frozen facing -> rotation_y (degrees about Y). Front of quad faces into room.
_FACING_ROTATION: dict[str, float] = {"N": 0.0, "S": 180.0, "E": 90.0, "W": 270.0}

# How far in front of the solid boundary wall the panel quad sits.
PANEL_INSET: float = 0.05
PANEL_CENTER_Y: float = 1.5
PANEL_MAX_WIDTH: float = 2.4
PANEL_SLOT_FRACTION: float = 0.85


# ---------------------------------------------------------------------------
# Pure, Ursina-free placement math
# ---------------------------------------------------------------------------
@dataclass
class PanelPlacement:
    block_id: str
    position: tuple[float, float, float]
    rotation_y: float
    width: float
    height: float


def place_panels(
    rect: Rect, facing: Facing, block_ids: list[str], ceiling_h: float
) -> list[PanelPlacement]:
    """Distribute block_ids evenly along the interior face of one wall.

    Pure data in / pure data out. No Ursina import required.

    Conventions (frozen):
        N wall at z = rect.z + d (max Z)
        S wall at z = rect.z       (min Z)
        E wall at x = rect.x + w   (max X)
        W wall at x = rect.x       (min X)
    The inset is applied on the perpendicular axis, pushing the panel into
    the room (away from the boundary wall).
    """
    placements: list[PanelPlacement] = []
    n = len(block_ids)
    if n == 0:
        return placements

    rotation_y = _FACING_ROTATION[facing]
    height = min(2.0, ceiling_h - 0.5)

    if facing in ("N", "S"):
        # Panels distributed along X; wall sits at a fixed Z.
        L = rect.w
        slot = L / n
        width = min(slot * PANEL_SLOT_FRACTION, PANEL_MAX_WIDTH)
        if facing == "N":
            z = rect.z + rect.d - WALL_THICKNESS / 2 - PANEL_INSET
        else:  # S
            z = rect.z + WALL_THICKNESS / 2 + PANEL_INSET
        for i, block_id in enumerate(block_ids):
            x = rect.x + slot * (i + 0.5)
            placements.append(
                PanelPlacement(
                    block_id=block_id,
                    position=(x, PANEL_CENTER_Y, z),
                    rotation_y=rotation_y,
                    width=width,
                    height=height,
                )
            )
    else:
        # E / W: panels distributed along Z; wall sits at a fixed X.
        L = rect.d
        slot = L / n
        width = min(slot * PANEL_SLOT_FRACTION, PANEL_MAX_WIDTH)
        if facing == "E":
            x = rect.x + rect.w - WALL_THICKNESS / 2 - PANEL_INSET
        else:  # W
            x = rect.x + WALL_THICKNESS / 2 + PANEL_INSET
        for i, block_id in enumerate(block_ids):
            z = rect.z + slot * (i + 0.5)
            placements.append(
                PanelPlacement(
                    block_id=block_id,
                    position=(x, PANEL_CENTER_Y, z),
                    rotation_y=rotation_y,
                    width=width,
                    height=height,
                )
            )

    return placements


# ---------------------------------------------------------------------------
# Cell handle
# ---------------------------------------------------------------------------
class CellEntities:
    """Owns every entity of one cell so RoomManager (M4) can load/unload it."""

    def __init__(self, root, panels: dict, all_entities: list) -> None:
        self.root = root
        self.panels = panels
        self.all_entities = all_entities

    def enable(self) -> None:
        for e in self.all_entities:
            try:
                e.enabled = True
            except Exception:
                pass

    def disable(self) -> None:
        for e in self.all_entities:
            try:
                e.enabled = False
            except Exception:
                pass

    def destroy(self) -> None:
        from ursina import destroy as _destroy

        for e in self.all_entities:
            try:
                _destroy(e)
            except Exception:
                pass
        self.all_entities = []
        self.panels = {}
        self.root = None


# ---------------------------------------------------------------------------
# build_room
# ---------------------------------------------------------------------------
def build_room(room: RoomCell, content: RoomContent, assets: AssetManager) -> CellEntities:
    # Import Ursina lazily so the pure helper + import of this module stay
    # headless-friendly until an actual build is requested.
    from ursina import Entity, color

    def _rgb01(r, g, b):
        return color.rgba(r / 255, g / 255, b / 255, 1)

    rect = room.rect
    cx = rect.x + rect.w / 2.0
    cz = rect.z + rect.d / 2.0
    h = CEILING_H

    all_entities: list = []
    panels: dict = {}

    root = Entity()
    all_entities.append(root)

    # Floor: plain dark plane sized to the rect, standable.
    floor = Entity(
        parent=root,
        model="plane",
        scale=(rect.w, 1, rect.d),
        position=(cx, 0.0, cz),
        color=_rgb01(40, 40, 46),
        collider="box",
        unlit=True,
    )
    all_entities.append(floor)

    # Ceiling: plain darker plane at y=CEILING_H, flipped to face downward.
    ceiling = Entity(
        parent=root,
        model="plane",
        scale=(rect.w, 1, rect.d),
        position=(cx, h, cz),
        rotation=(180, 0, 0),
        color=_rgb01(22, 22, 26),
        unlit=True,
    )
    all_entities.append(ceiling)

    # Four solid boundary walls (thin cubes), height CEILING_H, collidable.
    t = WALL_THICKNESS
    wall_color = _rgb01(70, 70, 80)
    # N wall: z = max Z
    walls_spec = [
        ((cx, h / 2.0, rect.z + rect.d), (rect.w, h, t)),  # N
        ((cx, h / 2.0, rect.z), (rect.w, h, t)),           # S
        ((rect.x + rect.w, h / 2.0, cz), (t, h, rect.d)),  # E
        ((rect.x, h / 2.0, cz), (t, h, rect.d)),           # W
    ]
    for pos, scale in walls_spec:
        w = Entity(
            parent=root,
            model="cube",
            position=pos,
            scale=scale,
            color=wall_color,
            collider="box",
            unlit=True,
        )
        all_entities.append(w)

    # Content panels.
    for wall in content.walls:
        ordered = sorted(wall.blocks, key=lambda b: b.order)
        block_ids = [b.block_id for b in ordered]
        placements = place_panels(rect, wall.facing, block_ids, h)
        for placement in placements:
            off_tex, on_tex = assets.wall_textures(placement.block_id)
            panel = Entity(
                parent=root,
                model="quad",
                texture=off_tex,
                position=placement.position,
                rotation=(0, placement.rotation_y, 0),
                scale=(placement.width, placement.height, 1),
                double_sided=True,
                collider="box",
                unlit=True,
            )
            panel.kind = "panel"
            panel.block_id = placement.block_id
            panel.off_tex = off_tex
            panel.on_tex = on_tex
            panel.is_on = False
            panels[placement.block_id] = panel
            all_entities.append(panel)

    return CellEntities(root=root, panels=panels, all_entities=all_entities)


def build_corridor(corr: Corridor, assets: AssetManager):
    raise NotImplementedError("M4")
