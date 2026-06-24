"""Layered rendering diagnostic. Run: python m1_diag.py
Prints facts at each layer so we stop guessing."""
from __future__ import annotations

from ursina import Ursina, Entity, camera, color, scene, application, mouse

app = Ursina()

print("=" * 50)
print("STEP 0: window + camera baseline")
print("camera type:", type(camera).__name__)
print("camera world_position:", camera.world_position)
print("camera rotation:", camera.rotation)
print("clip near/far:", camera.clip_plane_near, camera.clip_plane_far)

# --- LAYER 1: one bright cube directly in front of the camera. ------------
camera.position = (0, 0, -5)
camera.rotation = (0, 0, 0)        # look toward +Z
camera.clip_plane_near = 0.05
camera.clip_plane_far = 500

test_cube = Entity(
    model="cube",
    color=color.red,
    position=(0, 0, 0),
    scale=2,
    unlit=True,                    # <-- ignore lighting entirely
)
print("=" * 50)
print("STEP 1: a RED unlit cube at origin, camera 5 units back facing it.")
print(">>> Do you see a RED square? (y/n) — report this.")
print("    cube enabled:", test_cube.enabled, "visible:", test_cube.visible)

frame = 0
def update():
    global frame
    frame += 1
    if frame == 30:   # after ~0.5s, dump render state once
        print("-" * 50)
        print("RENDER DUMP @ frame 30")
        print("  scene children count:", len(scene.children))
        print("  cube world_pos:", test_cube.world_position)
        print("  cube on screen?:", test_cube.visible and test_cube.enabled)
        print("  window size:", application.base.win.get_size()
              if hasattr(application, "base") else "?")
        print("-" * 50)

def input(key):
    if key == "escape":
        application.quit()

app.run()
