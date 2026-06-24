from __future__ import annotations

from pathlib import Path

from ursina import (
    Ursina,
    Entity,
    camera,
    color,
    mouse,
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
        if inp.pause_pressed():
            application.quit()
            return

        shooter.update(time.dt)
        demon.update(time.dt)

        # --- tiny inline mover (copied from m2_demo) ---
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
            f"Read: {pct:.0f}%   WASD move | mouse look | click = reveal | "
            f"shoot demon to reveal equation | ESC quit"
        )

    # bind update for Ursina to pick up
    globals()["update"] = update
    app.run()


if __name__ == "__main__":
    main()
