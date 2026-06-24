from ursina import Ursina, Entity, camera, color, application
from principia.content.loader import load_level
from principia.assets.manager import AssetManager
from principia.world.builder import build_room

app = Ursina()
camera.fov = 75

level = load_level("content_packs/principia", "fixture")
room = next(r for r in level.floorplan.rooms if r.id == "lemma1")
content = level.rooms["lemma1"]
assets = AssetManager("content_packs/principia")
cell = build_room(room, content, assets)

# Fixed camera looking north at the panels (no controller).
camera.position = (6, 1.6, 2)
camera.rotation = (0, 0, 0)
camera.clip_plane_near = 0.05
camera.clip_plane_far = 500

# Plus the SAME known-good red cube next to the wall, for reference.
Entity(model="cube", color=color.red, unlit=True, position=(2, 1.6, 10), scale=1.5)

# Dump what the builder actually made.
for i, e in enumerate(cell.all_entities):
    print(i, type(e).__name__,
          "model=", getattr(getattr(e, "model", None), "name", e.model),
          "pos=", e.world_position,
          "vis=", e.visible, "enabled=", e.enabled,
          "color=", getattr(e, "color", None))

from ursina import color as _c
for e in cell.all_entities:
    if getattr(e, "model", None) and getattr(e.model, "name", "") == "quad":
        tex = e.texture
        print("PANEL at", e.world_position,
              "texture =", getattr(tex, "name", tex),
              "| path =", getattr(tex, "path", None))
        if tex is None:
            e.color = _c.magenta   # no texture loaded -> show bright magenta

from ursina import Entity as _E, color as _c2
# Force every panel double-sided so we see it regardless of facing.
for e in cell.all_entities:
    if getattr(getattr(e, "model", None), "name", "") == "quad":
        e.double_sided = True
        print("forced double_sided on panel at", e.world_position,
              "rotation =", e.rotation)

# A known-good GREEN quad facing the camera, placed mid-room as a sanity check.
_E(model="quad", color=_c2.green, unlit=True,
   position=(6, 1.6, 6), double_sided=True, scale=1.5)

def input(key):
    if key == "escape": application.quit()
app.run()
