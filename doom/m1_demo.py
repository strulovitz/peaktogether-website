"""Throwaway end-to-end demo for M1. Not imported by any test/runtime module.

Run:  python m1_demo.py
Walk: WASD + mouse. Left-click a wall panel to turn it 'on'. Esc to quit.
"""
from __future__ import annotations

from ursina import (
    Ursina, Entity, camera, color, raycast, application,
    Sky, DirectionalLight, AmbientLight,
)
from ursina.prefabs.first_person_controller import FirstPersonController

from principia.content.loader import load_level
from principia.assets.manager import AssetManager
from principia.world.builder import build_room

app = Ursina()
camera.fov = 75

# --- Lighting + sky so the scene isn't a flat white void. -----------------
Sky()
AmbientLight(color=color.rgb(180, 180, 190))
sun = DirectionalLight()
sun.look_at((1, -1, 1))
# --------------------------------------------------------------------------

level = load_level("content_packs/principia", "fixture")
room = next(r for r in level.floorplan.rooms if r.id == "lemma1")
content = level.rooms["lemma1"]
assets = AssetManager("content_packs/principia")

cell = build_room(room, content, assets)

# Start near the south wall (min Z) facing north so the N-wall panels show.
player = FirstPersonController(y=1.6, speed=4, position=(6, 1.6, 2))
player.jump_height = 0
player.cursor.visible = False

# FirstPersonController resets orientation on creation; force it to look
# NORTH (+Z, toward the N wall at z=12 where the panels live) and level.
player.rotation_y = 0      # face +Z
player.camera_pivot.rotation_x = 0  # level pitch (no looking at floor/ceiling)

Entity(
    parent=camera.ui,
    model="quad",
    scale=0.008,
    color=color.rgb(255, 60, 60),
    rotation_z=45,
)


def input(key):
    if key == "escape":
        application.quit()
    if key == "left mouse down":
        hit = raycast(camera.world_position, camera.forward, distance=25, ignore=(player,))
        if hit.hit and getattr(hit.entity, "kind", None) == "panel" and not hit.entity.is_on:
            hit.entity.texture = hit.entity.on_tex
            hit.entity.is_on = True


app.run()
