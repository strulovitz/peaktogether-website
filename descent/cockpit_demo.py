"""
cockpit_demo.py -- standalone visual test for cockpit.py.

Run:  python cockpit_demo.py

Proves resolution-independence: the window is RESIZABLE and number keys
snap to presets. The cockpit re-fits on every size change.

  drag window edges  -> live VIDEORESIZE re-layout
  1 = 1280x800   2 = 1920x1080   3 = 2560x1440   4 = 2560x1080 (ultrawide)
  LEFT / RIGHT    -> move the selected face cell
  ESC            -> quit

Uses fake arsenal entries; faces fall back gracefully to empty squares if
load_portrait can't find the named PNGs (you'll still see the grid frame).
"""

import sys
import pygame
from OpenGL.GL import glClearColor, glClear, glViewport, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT

import render
from cockpit import CockpitHUD

PRESETS = {
    pygame.K_1: (1280, 800),
    pygame.K_2: (1920, 1080),
    pygame.K_3: (2560, 1440),
    pygame.K_4: (2560, 1080),
}

FAKE_ARSENAL = [
    {"id": "t%d" % i, "name": n, "png": n + "-hologram.png"}
    for i, n in enumerate([
        "Maxwell", "Gauss", "Euler", "Riemann", "Noether",
        "Hilbert", "Cauchy", "Fourier", "Laplace",
    ])
]


def _resize(size):
    flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE
    pygame.display.set_mode(size, flags)
    glViewport(0, 0, size[0], size[1])
    return size


def main():
    pygame.init()
    size = (1280, 800)
    size = _resize(size)
    pygame.display.set_caption("DESCENT QED -- cockpit demo")
    render.init_gl(size)

    cockpit = CockpitHUD()
    loaded = 0
    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(60)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.VIDEORESIZE:
                size = _resize((ev.w, ev.h))
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key in PRESETS:
                    size = _resize(PRESETS[ev.key])
                elif ev.key == pygame.K_RIGHT:
                    loaded = (loaded + 1) % len(FAKE_ARSENAL)
                elif ev.key == pygame.K_LEFT:
                    loaded = (loaded - 1) % len(FAKE_ARSENAL)
                elif ev.key == pygame.K_DOWN:
                    loaded = (loaded + 3) % len(FAKE_ARSENAL)
                elif ev.key == pygame.K_UP:
                    loaded = (loaded - 3) % len(FAKE_ARSENAL)
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                hit = cockpit.face_at_pixel(*ev.pos)
                if hit is not None:
                    loaded = hit

        glClearColor(0.05, 0.06, 0.08, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        state = {
            "arsenal": FAKE_ARSENAL,
            "loaded_slot": loaded,
            "vulnerable": FAKE_ARSENAL[loaded]["name"],
            "loaded_name": FAKE_ARSENAL[loaded]["name"],
            "path_clear": False,
            "gauge_number": "90",
            "fizzle_text": None,
        }

        render.begin_2d(*size)
        cockpit.draw(size[0], size[1], state)
        render.end_2d()

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
