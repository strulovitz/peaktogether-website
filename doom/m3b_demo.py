"""Standalone M3b demo: full M3 build + read mode.

Run:  python m3b_demo.py
Controls:
  WASD + mouse  : move / look
  click         : reveal panel / shoot demon
  R             : read the panel you're looking at (full-screen); R/Esc to close
  ESC           : quit
"""
from __future__ import annotations

from math import sin
import random

from ursina import (
    Ursina, Entity, camera, color, mouse, held_keys, raycast,
    application, time, Text, Vec3, destroy,
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
from principia.ui.readmode import ReadMode


PACK_DIR = "content_pack"
ROOM_ID = "lemma1"


def make_band_texture():
    """Inline Pillow placeholder ceiling equation band."""
    img = Image.new("RGBA", (1024, 128), (10, 10, 16, 255))
    d = ImageDraw.Draw(img)
    d.text((20, 50), "a^2 + b^2 = c^2   (Q.E.D.)", fill=(220, 220, 255, 255))
    from ursina import Texture
    return Texture(img)


def main():
    app = Ursina()

    # --- load + build ----------------------------------------------------
    level = load_level(PACK_DIR, ROOM_ID)
    assets = AssetManager(PACK_DIR)

    room = next(r for r in level.floorplan.rooms if r.id == ROOM_ID)
    content = level.rooms[ROOM_ID]

    cell = build_room(room, content, assets)

    wall_state = WallStateManager(assets)
    for block_id, panel in cell.panels.items():
        wall_state.register(ROOM_ID, block_id, panel, panel.off_tex, panel.on_tex)
    try:
        wall_state.load(config.SAVE_FILE)
    except Exception:
        pass

    # --- demon -----------------------------------------------------------
    demon = Demon(content.demon, position=Vec3(0, config.EYE_HEIGHT, 6))

    # --- ceiling band ----------------------------------------------------
    ceiling = CeilingManager(assets)
    band = Entity(
        model='quad',
        texture=make_band_texture(),
        position=(0, config.CEILING_H - 0.05, 6),
        rotation_x=90,
        scale=(8, 1),
        double_sided=True,
    )
    ceiling.register_band(ROOM_ID, band, band)

    def on_demon_death():
        ceiling.reveal(ROOM_ID)
        glyphs = [p.on_tex for p in cell.panels.values()]
        ceiling.spray_from(demon.position, glyphs)

    demon.on_death(on_demon_death)

    # --- camera (manual fps) --------------------------------------------
    camera.position = (0, config.EYE_HEIGHT, 0)
    camera.rotation = (0, 0, 0)
    mouse.locked = True

    # --- input + shooter -------------------------------------------------
    inp = InputManager()

    def reveal_panel(entity, point):
        wall_state.toggle(ROOM_ID, entity.block_id)

    shooter = Shooter(camera, inp)
    shooter.register_hit_handlers(
        on_wall=reveal_panel,
        on_demon=lambda e, p: e.demon.hit(p),
        on_secret=None,
    )

    read_mode = ReadMode()

    hud = Text(text="", origin=(-0.5, 0.5), x=-0.86, y=0.46, scale=0.9)

    def update():
        inp.poll()

        if read_mode.is_open():
            # world frozen for reading
            if inp.read_mode_pressed() or inp.pause_pressed():
                read_mode.close()
            return

        if inp.pause_pressed():
            application.quit()
            return

        if inp.read_mode_pressed():
            hit = raycast(
                camera.world_position,
                camera.forward,
                distance=config.SHOOT_RANGE,
                ignore=(camera,),
            )
            if hit.hit and getattr(hit.entity, "kind", None) == "panel":
                read_mode.open(hit.entity.block_id, hit.entity.texture)
                return

        # --- normal play ------------------------------------------------
        shooter.update(time.dt)
        demon.update(time.dt)

        # inline mover (look + walk)
        dx, dy = inp.aim_delta()
        camera.rotation_y += dx
        camera.rotation_x = max(-89, min(89, camera.rotation_x - dy))

        ax, az = inp.move_axis()
        fwd = camera.forward
        right = camera.right
        move = (right * ax + fwd * az)
        move.y = 0
        if move.length() > 0:
            move = move.normalized() * config.WALK_SPEED * time.dt
            camera.position += move
        camera.y = config.EYE_HEIGHT

        hud.text = (
            f"Read: {wall_state.progress(ROOM_ID) * 100:.0f}%  |  "
            f"click=reveal  ·  shoot demon=exorcise  ·  "
            f"R=read panel  ·  ESC quit"
        )

    app.update = update
    app.run()


if __name__ == "__main__":
    main()
