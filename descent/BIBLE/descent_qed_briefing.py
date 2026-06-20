"""briefing.py -- typewriter briefing panel (the couple speaks on lock-on)."""

from OpenGL.GL import *
import palette

CPS = 45.0          # typewriter speed, chars/second
LINE_H, PAD = 22, 12


def draw_text_2d(text, x, y, color):
    """TODO(DeepSeek): 2D text at window coords (origin bottom-left).
    Same recipe as your draw_overlay_text: pygame.font.Font(None, 22),
    render(text, True, 255*color), tostring RGBA flipped, then
    glWindowPos2d(x, y) + glDrawPixels. Cache fonts; call sites are hot.
    Acceptance: panel title + typing lines visible; console fallback in
    update() keeps working meanwhile."""
    pass


class TypewriterPanel:
    def __init__(self):
        self.active = False

    def start(self, title, lines, color):
        self.title, self.lines, self.color = title, list(lines), color
        self.t, self._printed, self.active = 0.0, set(), True

    def update(self, dt):
        if not self.active:
            return
        self.t += dt
        for i, ln in enumerate(self._revealed()):          # console fallback
            if i not in self._printed and ln == self.lines[i]:
                self._printed.add(i)
                print("BRIEFING| " + ln)

    def _revealed(self):
        budget = int(self.t * CPS)
        out = []
        for ln in self.lines:
            take = min(len(ln), max(0, budget))
            out.append(ln[:take])
            budget -= len(ln)
            if budget <= 0:
                break
        return out

    def draw(self, win_w, win_h):
        if not self.active:
            return
        x0, y0 = 20, 16
        y1 = y0 + 2 * PAD + LINE_H * (len(self.lines) + 1)
        x1 = win_w - 20
        _begin2d(win_w, win_h)
        glColor4f(*palette.PANEL_BG, palette.PANEL_ALPHA)
        glBegin(GL_QUADS)
        for vx, vy in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            glVertex2f(vx, vy)
        glEnd()
        glLineWidth(2.0)
        glColor4f(*self.color, 0.9)
        glBegin(GL_LINE_LOOP)
        for vx, vy in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            glVertex2f(vx, vy)
        glEnd()
        draw_text_2d(self.title, x0 + PAD, y1 - PAD - LINE_H, self.color)
        for i, ln in enumerate(self._revealed()):
            draw_text_2d(ln, x0 + PAD, y1 - PAD - LINE_H * (i + 2),
                         (0.85, 0.88, 0.92))
        _end2d()


def _begin2d(w, h):
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_FOG)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, w, 0, h, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()


def _end2d():
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_FOG)
    glEnable(GL_DEPTH_TEST)
