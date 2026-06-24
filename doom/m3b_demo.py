"""Standalone M3b demo: full M3 build + read mode.

Run:  python m3b_demo.py
Controls:
  WASD + mouse  : move / look
  click         : reveal panel / shoot demon
  R             : read the panel you're looking at (full-screen); R/Esc to close
  ESC           : quit
"""
from __future__ import annotations

from ursina import (
    Ursina,
    Entity,
    camera,
    color,
    mouse,
    raycast,
    application,
    time,
    Text,
    Vec3,
    Texture,
)
from PIL import Image, ImageDraw

import principia.config as config
from principia.content.loader import load_level
from principia.assets.manager import AssetManager
from principia.world.builder import build_room
from principia.walls.state import WallStateManager
from principia.control.input import InputManager
from principia.player.shooter import Shooter
from principia.enemy.demon import Demon
from principia.ceiling.equations import CeilingManager
from principia.schema import CeilingBand
from principia.ui.readmode import ReadMode


def make_equation_texture(text: str = "q = m v") -> Texture:
    img = Image.new("RGBA", (256, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((10, 20), text, fill=(255, 255, 255, 255))
    return Texture(img)


def main():
    app = Ursina()

    # --- Load level + build lemma1 room ---
    level = load_level("content_packs/principia", "fixture")
    room = next(r for r in level.floorplan.rooms if r.id == "lemma1")
    assets = AssetManager("content_packs/principia")
    cell = build_room(room, level.rooms["lemma1"], assets)

    # --- Wall state ---
    wall_state = WallStateManager(assets)
    for block_id, panel in cell.panels.items():
        wall_state.register("lemma1", block_id, panel, panel.off_tex, panel.on_tex)

    # --- Demon ---
    spec = level.rooms["lemma1"].demon
    demon = Demon(spec, tuple(spec.position))

    # --- Ceiling band ---
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

    demon.on_death(lambda: (
        ceiling.reveal("lemma1"),
        ceiling.spray_from(tuple(spec.position), [equation_tex]),
    ))

    # --- Input + shooter ---
    inp = InputManager()
    shooter = Shooter(camera, inp)

    def reveal(block_id: str):
        if not wall_state.state(block_id):
            wall_state.toggle(block_id)

    shooter.register_hit_handlers(
        on_wall=reveal,
        on_demon=(lambda e, p: e.demon.hit(p)),
        on_secret=None,
    )

    # --- Read mode ---
    read_mode = ReadMode()

    # --- Camera / manual mover setup ---
    mouse.locked = True
    crosshair = Entity(
        parent=camera.ui,
        model="quad",
        color=color.red,
        scale=0.008,
    )

    camera.position = (6, config.EYE_HEIGHT, 2)
    camera.rotation = (0, 0, 0)

    hud = Text(text="", position=(-0.85, 0.45), scale=1.0)

    LO, HI = 0.6, 11.4

    def update():
        inp.poll()

        # --- Read mode: world is frozen for reading ---
        if read_mode.is_open():
            if inp.read_mode_pressed() or inp.pause_pressed():
                read_mode.close()
            return

        if inp.pause_pressed():
            application.quit()
            return

        # --- Enter read mode: raycast forward, open if looking at a panel ---
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

        # --- Normal play ---
        shooter.update(time.dt)
        demon.update(time.dt)

        strafe, forward = inp.move_axis()

        fwd = camera.forward
        rgt = camera.right
        forward_flat = Vec3(fwd[0], 0, fwd[2])
        right_flat = Vec3(rgt[0], 0, rgt[2])
        if forward_flat.length() > 0:
            forward_flat = forward_flat.normalized()
        if right_flat.length() > 0:
            right_flat = right_flat.normalized()

        move = (right_flat * strafe + forward_flat * forward) * config.WALK_SPEED * time.dt
        new_pos = camera.position + move

        nx = max(LO, min(HI, new_pos[0]))
        nz = max(LO, min(HI, new_pos[2]))
        camera.position = (nx, config.EYE_HEIGHT, nz)

        pct = wall_state.progress("lemma1") * 100
        hud.text = (
            f"Read: {pct:.0f}%  |  click=reveal  ·  shoot demon=exorcise  ·  "
            f"R=read panel  ·  ESC quit"
        )

    globals()["update"] = update
    app.run()


if __name__ == "__main__":
    main()
