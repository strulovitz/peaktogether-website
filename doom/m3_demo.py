"""Standalone M3 demo: shoot panels to colorize; shoot the demon to exorcise
the room (ceiling equation reveals blood-red + sprays). Throwaway glue."""
from __future__ import annotations

from pathlib import Path

from ursina import (
    Ursina, Entity, camera, mouse, application, time, Text, Texture,
)
from PIL import Image, ImageDraw

from principia import config
from principia.content.loader import load_level
from principia.assets.manager import AssetManager
from principia.world.builder import build_room
from principia.walls.state import WallStateManager
from principia.control.input import InputManager
from principia.player.shooter import Shooter
from principia.enemy.demon import Demon
from principia.ceiling.equations import CeilingManager
from principia.schema import CeilingBand


def make_equation_texture(text: str = "q = m v") -> Texture:
    img = Image.new("RGBA", (256, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((10, 20), text, fill=(255, 255, 255, 255))
    return Texture(img)


def main() -> None:
    app = Ursina()
    pack_dir = Path("content_packs/principia")

    # FIX (Symptom 1): the level id is "fixture" (per concept_graph.json /
    # floorplan.json); "lemma1" is the ROOM id, looked up in level.rooms.
    level = load_level(pack_dir, "fixture")
    assets = AssetManager(pack_dir)

    room_cell = next(r for r in level.floorplan.rooms if r.id == "lemma1")
    content = level.rooms["lemma1"]
    cell = build_room(room_cell, content, assets)

    # --- walls ---
    wall_state = WallStateManager(assets)

    for block_id, panel in cell.panels.items():
        wall_state.register(
            "lemma1", block_id, panel, panel.off_tex, panel.on_tex
        )

    # FIX (Symptom 2): the shooter calls on_wall(block_id) with ONE argument —
    # the block_id string itself, not the entity, and no hit point.
    def reveal_panel(block_id):
        if block_id is not None:
            wall_state.toggle(block_id)

    # --- demon ---
    spec = content.demon
    demon = Demon(spec, tuple(spec.position))

    # --- ceiling band ---
    equation_tex = make_equation_texture("q = m v")
    band_entity = Entity(
        model="quad",
        texture=equation_tex,
        position=(6, config.CEILING_H - 0.05, 10),
        rotation=(90, 0, 0),
        double_sided=True,
        scale=3,
    )
    cb = CeilingBand(
        band_id="cb_l1_1",
        above_wall="",
        equation_png="png/eq_l1_1.png",
        hidden_until_demon_dead=True,
    )

    ceiling = CeilingManager(assets)
    ceiling.register_band("lemma1", cb, band_entity)

    # --- death wiring ---
    demon.on_death(lambda: (
        ceiling.reveal("lemma1"),
        ceiling.spray_from(tuple(spec.position), [equation_tex]),
    ))

    # --- shooter handlers (on_demon uses the .demon back-reference) ---
    input_mgr = InputManager()
    shooter = Shooter(camera, input_mgr)
    shooter.register_hit_handlers(
        on_wall=reveal_panel,
        on_demon=(lambda e, p: e.demon.hit(p)),
        on_secret=None,
    )

    # --- camera / player ---
    camera.position = (6, config.EYE_HEIGHT, 0)
    mouse.locked = True
    rot = {"yaw": 0.0, "pitch": 0.0}

    hud = Text(text="", position=(-0.85, 0.45), scale=1.0)

    def update():
        input_mgr.poll()

        dx, dy = input_mgr.aim_delta()
        rot["yaw"] += dx * 40
        rot["pitch"] = max(-89, min(89, rot["pitch"] - dy * 40))
        camera.rotation_y = rot["yaw"]
        camera.rotation_x = rot["pitch"]

        mx, mz = input_mgr.move_axis()
        camera.position += (
            camera.right * mx * config.WALK_SPEED * time.dt
            + camera.forward * mz * config.WALK_SPEED * time.dt
        )
        camera.y = config.EYE_HEIGHT

        shooter.update(time.dt)
        demon.update(time.dt)

        if input_mgr.pause_pressed():
            application.quit()

        hud.text = (
            f"Read: {wall_state.progress('lemma1') * 100:.0f}%  |  "
            f"shoot the demon to reveal the equation  |  ESC quit"
        )

    app.update = update
    app.run()


if __name__ == "__main__":
    main()
