"""main.py -- Descent QED, Build Step 2: the robots appear.
NOTE(DeepSeek): port your draw_overlay_text() and F3 toggle here."""

import math
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective, gluLookAt
import corridor
import robots
import briefing
import content
import palette

WIN_SIZE      = (1280, 720)
MOVE_SPEED    = 12.0
TURN_SPEED    = 80.0
PLAYER_RADIUS = 0.6


class DebugCamera:
    def __init__(self):
        self.pos = np.array([0.0, 0.0, -4.0])
        self.yaw, self.pitch = 0.0, 0.0

    def direction(self):
        y, p = math.radians(self.yaw), math.radians(self.pitch)
        return np.array([-math.sin(y) * math.cos(p), math.sin(p),
                         -math.cos(y) * math.cos(p)])

    def right(self):
        ry = math.radians(self.yaw)
        return np.array([math.cos(ry), 0.0, -math.sin(ry)])

    def update(self, keys, dt):
        if keys[K_LEFT]:  self.yaw += TURN_SPEED * dt
        if keys[K_RIGHT]: self.yaw -= TURN_SPEED * dt
        if keys[K_UP]:    self.pitch = min(85.0, self.pitch + TURN_SPEED * dt)
        if keys[K_DOWN]:  self.pitch = max(-85.0, self.pitch - TURN_SPEED * dt)
        d, right = self.direction(), self.right()
        delta = np.zeros(3)
        if keys[K_w]: delta += d
        if keys[K_s]: delta -= d
        if keys[K_d]: delta += right
        if keys[K_a]: delta -= right
        if keys[K_r]: delta += np.array([0.0, 1.0, 0.0])
        if keys[K_f]: delta -= np.array([0.0, 1.0, 0.0])
        self._try_move(delta * MOVE_SPEED * dt)

    def _legal(self, p):
        return (corridor.inside(p, PLAYER_RADIUS)
                and not robots.blocked(p, PLAYER_RADIUS))

    def _try_move(self, delta):
        cand = self.pos + delta
        if self._legal(cand):
            self.pos = cand
            return
        cur = self.pos.copy()
        for axis in range(3):
            c = cur.copy()
            c[axis] += delta[axis]
            if self._legal(c):
                cur = c
        self.pos = cur

    def apply(self):
        d, p = self.direction(), self.pos
        gluLookAt(p[0], p[1], p[2], p[0] + d[0], p[1] + d[1], p[2] + d[2], 0, 1, 0)


def init_gl():
    glClearColor(*palette.BG, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDisable(GL_CULL_FACE)
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
    """TODO(DeepSeek): paste your working implementation here."""
    pass


def main():
    pygame.init()
    pygame.display.set_mode(WIN_SIZE, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Descent QED -- EULER-1734 (Step 2: Robots)")
    init_gl()
    cam, panel = DebugCamera(), briefing.TypewriterPanel()
    clock = pygame.time.Clock()
    wall_alpha = palette.WALL_ALPHA_DEFAULT
    wireframe, t = False, 0.0
    lock, brief_sid = None, None
    fps_n, fps_t = 0, 0.0

    while True:
        dt = clock.tick(60) / 1000.0
        t += dt
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
                # TODO(DeepSeek): paste your working F3 toggle here.
            if ev.type == KEYDOWN and ev.key == K_n:
                robots.neutralize(lock)        # DEBUG stand-in for combat

        cam.update(pygame.key.get_pressed(), dt)
        robots.update_all(dt, t)
        new_lock = robots.find_lock(cam.pos, cam.direction())
        if new_lock is not None and new_lock.sid != brief_sid:
            brief_sid = new_lock.sid
            b = content.BRIEFINGS[brief_sid]
            panel.start(b["name"], b["lines"], new_lock.eye)
        lock = new_lock
        panel.update(dt)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        cam.apply()
        corridor.draw_opaque()
        cam_up = np.cross(cam.right(), cam.direction())
        robots.draw_all(t, lock, cam.right(), cam_up)
        corridor.draw_fills(wall_alpha, cam.pos)
        panel.draw(*WIN_SIZE)
        status = "wall alpha %.2f   [ ] adjust   F3 wireframe" % wall_alpha
        if lock is not None:
            status += "   LOCK: %s   (N neutralize)" % lock.sid
        draw_overlay_text(status)
        pygame.display.flip()

        fps_n, fps_t = fps_n + 1, fps_t + dt
        if fps_t >= 1.0:
            print("FPS %d | wall alpha %.2f" % (fps_n, wall_alpha))
            fps_n, fps_t = 0, 0.0


if __name__ == "__main__":
    main()
