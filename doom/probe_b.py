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

def input(key):
    if key == "escape": application.quit()
app.run()
