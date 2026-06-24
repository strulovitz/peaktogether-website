from ursina import Ursina, Entity, camera, color, application
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()
camera.fov = 75

# Known-good red cube, placed in front of where the player will look (north = +Z).
Entity(model="cube", color=color.red, unlit=True, position=(6, 1.6, 10), scale=2)

player = FirstPersonController(speed=4, position=(6, 1.6, 2))
player.gravity = 0
player.jump_height = 0
player.cursor.visible = False
player.rotation_y = 0
player.camera_pivot.rotation_x = 0

def input(key):
    if key == "escape": application.quit()
app.run()
