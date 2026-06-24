"""
m0_demo.py — Principia Descent, Milestone 0 walking demo.

A single textured room you can walk around. Demonstrates the CORE VERB:
  - left-click a black-and-white wall panel  -> it turns colourful ("on")
  - left-click the demon a few times          -> it disintegrates
  - on demon death, a blood-red equation appears on the ceiling

Controls:  WASD = move,  mouse = look,  left click = shoot,  ESC = quit.

This file is deliberately standalone and does NOT import the principia package;
it previews the look & feel while the real modules are built milestone by
milestone. Panel textures are drawn with Pillow at runtime to mimic the offline
"baked PNG" pipeline.
"""
from __future__ import annotations

import random
from PIL import Image, ImageDraw

from ursina import (
    Ursina, Entity, camera, color, mouse, raycast, held_keys,
    Text, Texture, destroy, application, time, Vec3, invoke,
)
from ursina.prefabs.first_person_controller import FirstPersonController

# --------------------------------------------------------------------- config
CEILING_H = 3.0
ROOM_W = 12.0
ROOM_D = 12.0
EYE = 1.6

app = Ursina(title="Principia Descent — M0 Walking Demo", borderless=False)
camera.fov = 75

# --------------------------------------------------------------- texture maker
def _hex(rgb_hex: str):
    rgb_hex = rgb_hex.lstrip("#")
    return tuple(int(rgb_hex[i:i + 2], 16) for i in (0, 2, 4))


def make_panel(title: str, on: bool) -> Texture:
    """Draw a placeholder proof-step panel. on=False -> grayscale ('off')."""
    S = 512
    img = Image.new("RGBA", (S, S), (248, 248, 244, 255))
    d = ImageDraw.Draw(img)

    abc = _hex("#0072B2") if on else (90, 90, 90)   # 'angle ABC' group (blue)
    bd = _hex("#D55E00") if on else (130, 130, 130)  # 'segment BD' group (orange)
    ink = (20, 20, 20)

    # frame
    d.rectangle([8, 8, S - 8, S - 8], outline=ink, width=4)
    # title bar
    d.rectangle([8, 8, S - 8, 64], fill=(230, 230, 224, 255))
    d.text((24, 26), title, fill=ink)

    # a little Newton-ish figure: triangle + inscribed arc
    A, B, C = (120, 420), (400, 420), (260, 160)
    d.line([A, B], fill=abc, width=6)          # base — group "abc" (badge ①)
    d.line([B, C], fill=ink, width=4)
    d.line([C, A], fill=ink, width=4)
    d.line([A, C[0], C[1]], fill=bd, width=6)  # (re-uses A) segment — group "bd" (badge ②)
    d.ellipse([235, 380, 285, 430], outline=bd, width=5)

    # redundant cues for colour-blind players (R1): numbered badges
    d.ellipse([90, 430, 118, 458], outline=abc, width=4); d.text((98, 437), "1", fill=abc)
    d.ellipse([250, 120, 278, 148], outline=bd, width=4); d.text((258, 127), "2", fill=bd)

    # a line of "text" referencing the same colours
    d.text((30, 470), "base AB = 1   |   apex C   |   arc 2", fill=ink)
    return Texture(img)


def make_equation(text: str) -> Texture:
    S = 512
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((40, S // 2 - 10), text, fill=(255, 255, 255, 255))
    return Texture(img)


def make_name_tile(text: str) -> Texture:
    S = 512
    img = Image.new("RGBA", (S, S), (15, 15, 20, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([6, 6, S - 6, S - 6], outline=(120, 120, 140), width=6)
    d.text((S // 2 - 60, S // 2 - 10), text, fill=(220, 220, 235))
    return Texture(img)


# --------------------------------------------------------------------- room
# floor (walkable)
Entity(model="plane", scale=(ROOM_W, 1, ROOM_D), texture="white_cube",
       texture_scale=(ROOM_W, ROOM_D), color=color.rgb(60, 60, 70),
       collider="box", position=(0, 0, 0))

# big readable name tile in the centre of the floor
Entity(model="quad", texture=make_name_tile("LEMMA I"), rotation_x=90,
       scale=4, position=(0, 0.02, 0), double_sided=True)

# ceiling (low)
Entity(model="plane", scale=(ROOM_W, 1, ROOM_D), texture="white_cube",
       texture_scale=(ROOM_W, ROOM_D), color=color.rgb(30, 30, 36),
       position=(0, CEILING_H, 0), rotation=(180, 0, 0))

# four walls (thin boxes, with collision)
half_w, half_d = ROOM_W / 2, ROOM_D / 2
wall_kw = dict(model="cube", texture="brick", color=color.rgb(95, 80, 75),
               collider="box")
Entity(**wall_kw, scale=(ROOM_W, CEILING_H, 0.3), position=(0, CEILING_H / 2,  half_d))   # N
Entity(**wall_kw, scale=(ROOM_W, CEILING_H, 0.3), position=(0, CEILING_H / 2, -half_d))   # S
Entity(**wall_kw, scale=(0.3, CEILING_H, ROOM_D), position=( half_w, CEILING_H / 2, 0))   # E
Entity(**wall_kw, scale=(0.3, CEILING_H, ROOM_D), position=(-half_w, CEILING_H / 2, 0))   # W

# --------------------------------------------------------------- wall panels
panels = []


def add_panel(title, pos, rot):
    off_tex = make_panel(title, on=False)
    on_tex = make_panel(title, on=True)
    p = Entity(model="quad", texture=off_tex, scale=2.2,
               position=pos, rotation=rot, double_sided=True, collider="box")
    p.kind = "panel"
    p.is_on = False
    p.off_tex = off_tex
    p.on_tex = on_tex
    panels.append(p)
    return p


add_panel("STEP 1", (-2.4, 1.5,  half_d - 0.31), (0,   0, 0))   # N wall, left
add_panel("STEP 2", ( 2.4, 1.5,  half_d - 0.31), (0,   0, 0))   # N wall, right
add_panel("STEP 3", (-half_w + 0.31, 1.5, -2.4), (0,  90, 0))   # W wall
add_panel("QED",    ( half_w - 0.31, 1.5,  2.4), (0, -90, 0))   # E wall

# ------------------------------------------------------- ceiling equation (hidden)
equation = Entity(model="quad", texture=make_equation("q = m v"),
                  scale=3, position=(0, CEILING_H - 0.05, 3),
                  rotation=(90, 0, 0), double_sided=True,
                  color=color.rgb(180, 0, 0), enabled=False)

# ------------------------------------------------------------------- demon
demon_parts = []


def build_demon():
    demon_parts.clear()
    spec = [
        ((0, 0, 0),        0.6, "#FF7AB6"),  # body
        ((-0.2, 0.25, 0.5), 0.1, "#3B6BFF"),  # eye
        ((0.2, 0.25, 0.5),  0.1, "#3B6BFF"),  # eye
        ((0, -0.1, 0.55),   0.07, "#FFFFFF"),  # tooth
        ((-0.12, -0.1, 0.55), 0.06, "#FFFFFF"),
        ((0.12, -0.1, 0.55),  0.06, "#FFFFFF"),
    ]
    base = Vec3(6 - ROOM_W / 2, 1.2, 0)  # sit it off-centre in the room
    for off, r, hx in spec:
        part = Entity(model="sphere",
                      color=color.rgb(*_hex(hx)),
                      scale=r * 2,
                      position=base + Vec3(*off),
                      collider="sphere")
        part.kind = "demon"
        demon_parts.append(part)


build_demon()
demon_alive = {"hp": 3, "dead": False}


def disintegrate_demon():
    if demon_alive["dead"]:
        return
    demon_alive["dead"] = True
    for part in demon_parts:
        dir_ = Vec3(random.uniform(-1, 1), random.uniform(0.2, 1),
                    random.uniform(-1, 1)).normalized()
        part.animate_position(part.position + dir_ * 3, duration=0.6)
        part.animate_scale(0, duration=0.6)
        invoke(destroy, part, delay=0.65)
    demon_parts.clear()
    # the demonic algebra is released:
    equation.enabled = True
    equation.scale = 0.1
    equation.animate_scale(3, duration=0.5)


# ------------------------------------------------------------------- player
player = FirstPersonController(y=EYE, speed=4, position=(0, EYE, -4))
player.jump_height = 0          # no jumping (flat-world invariant)
player.cursor.visible = False

# crosshair (the girlfriend's reticle, conceptually)
Entity(parent=camera.ui, model="quad", scale=0.008,
       color=color.rgb(255, 60, 60), rotation_z=45)

hint = Text(
    "WASD move | mouse look | LEFT-CLICK = shoot | ESC = quit\n"
    "Shoot a panel to colour it. Shoot the demon to exorcise the room.",
    origin=(0, 0), y=-0.43, scale=0.7, color=color.azure,
)


def shoot():
    hit = raycast(camera.world_position, camera.forward,
                  distance=25, ignore=(player,))
    if not hit.hit:
        return
    e = hit.entity
    kind = getattr(e, "kind", None)
    if kind == "panel" and not e.is_on:
        e.texture = e.on_tex          # off -> on (sticky)
        e.is_on = True
    elif kind == "demon":
        demon_alive["hp"] -= 1
        for p in demon_parts:         # quick flash
            p.blink(color.white, duration=0.1)
        if demon_alive["hp"] <= 0:
            disintegrate_demon()


def input(key):
    if key == "escape":
        application.quit()
    if key == "left mouse down":
        shoot()
    if key == "r":                    # convenience: instant exorcism
        disintegrate_demon()


app.run()
