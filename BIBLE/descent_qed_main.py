"""main.py -- Descent QED, Build Step 1 entry point. python main.py"""

import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective, gluLookAt
import corridor
import palette

WIN_SIZE   = (1280, 720)
MOVE_SPEED = 12.0      # units/s
TURN_SPEED = 80.0      # deg/s


class DebugCamera:
    """TEMPORARY free-fly camera; replaced by the Pi-Rho GX in a later step."""

    def __init__(self):
        self.pos = [0.0, 0.0, -4.0]    # just inside the MOUTH
        self.yaw, self.pitch = 0.0, 0.0

    def direction(self):
        y, p = math.radians(self.yaw), math.radians(self.pitch)
        return (-math.sin(y) * math.cos(p), math.sin(p), -math.cos(y) * math.cos(p))

    def update(self, keys, dt):
        if keys[K_LEFT]:  self.yaw += TURN_SPEED * dt
        if keys[K_RIGHT]: self.yaw -= TURN_SPEED * dt
        if keys[K_UP]:    self.pitch = min(85.0, self.pitch + TURN_SPEED * dt)
        if keys[K_DOWN]:  self.pitch = max(-85.0, self.pitch - TURN_SPEED * dt)
        d = self.direction()
        ry = math.radians(self.yaw)
        right = (math.cos(ry), 0.0, -math.sin(ry))
        step = MOVE_SPEED * dt
        for axis in range(3):
            if keys[K_w]: self.pos[axis] += d[axis] * step
            if keys[K_s]: self.pos[axis] -= d[axis] * step
            if keys[K_d]: self.pos[axis] += right[axis] * step
            if keys[K_a]: self.pos[axis] -= right[axis] * step
        if keys[K_r]: self.pos[1] += step
        if keys[K_f]: self.pos[1] -= step

    def apply(self):
        d = self.direction()
        p = self.pos
        gluLookAt(p[0], p[1], p[2], p[0] + d[0], p[1] + d[1], p[2] + d[2], 0, 1, 0)


def init_gl():
    glClearColor(*palette.BG, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDisable(GL_CULL_FACE)
    # DARKNESS, not fog: there is no weather in a mine. Fog color == BG
    # exactly, so geometry fades into black depth, never into mist.
    glEnable(GL_FOG)
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogfv(GL_FOG_COLOR, (*palette.BG, 1.0))
    glFogf(GL_FOG_START, palette.DARKNESS_START)
    glFogf(GL_FOG_END, palette.DARKNESS_END)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(70.0, WIN_SIZE[0] / WIN_SIZE[1], 0.1, 300.0)
    glMatrixMode(GL_MODELVIEW)


def draw_overlay_text(text):
    """TODO(DeepSeek): on-screen overlay (bottom-left) showing this text.
    Recipe: render `text` with pygame.font.Font(None, 24) to a surface,
    pygame.image.tostring(surf, "RGBA", True), then glWindowPos2d(10, 10)
    + glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, data). Disable
    GL_FOG and GL_DEPTH_TEST around the call, re-enable after.
    Acceptance: alpha value visibly updates on screen when [ ] pressed.
    Until then the console print in main() covers this."""
    pass


def main():
    pygame.init()
    pygame.display.set_mode(WIN_SIZE, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Descent QED -- EULER-1734 (Step 1: The Empty Mine)")
    init_gl()
    cam = DebugCamera()
    clock = pygame.time.Clock()
    wall_alpha = palette.WALL_ALPHA_DEFAULT
    wireframe = False
    fps_n, fps_t = 0, 0.0

    while True:
        dt = clock.tick(60) / 1000.0
        for ev in pygame.event.get():
            if ev.type == QUIT or (ev.type == KEYDOWN and ev.key == K_ESCAPE):
                pygame.quit()
                return
            if ev.type == KEYDOWN and ev.key == K_LEFTBRACKET:
                wall_alpha = max(palette.WALL_ALPHA_MIN, wall_alpha - palette.WALL_ALPHA_STEP)
            if ev.type == KEYDOWN and ev.key == K_RIGHTBRACKET:
                wall_alpha = min(palette.WALL_ALPHA_MAX, wall_alpha + palette.WALL_ALPHA_STEP)
            if ev.type == KEYDOWN and ev.key == K_F3:
                wireframe = not wireframe
                # TODO(DeepSeek): apply debug wireframe toggle here.
                # Hint: glPolygonMode(GL_FRONT_AND_BACK,
                #                     GL_LINE if wireframe else GL_FILL)
                # Acceptance: F3 flips the whole world to automap mode.

        cam.update(pygame.key.get_pressed(), dt)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        cam.apply()
        corridor.draw(wall_alpha)
        draw_overlay_text("wall alpha %.2f   [ ] adjust   F3 wireframe" % wall_alpha)
        pygame.display.flip()

        fps_n, fps_t = fps_n + 1, fps_t + dt
        if fps_t >= 1.0:
            print("FPS %d | wall alpha %.2f" % (fps_n, wall_alpha))
            fps_n, fps_t = 0, 0.0


if __name__ == "__main__":
    main()
