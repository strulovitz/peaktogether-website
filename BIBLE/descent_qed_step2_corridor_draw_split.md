Robots must render between the opaque pass and the translucent fills (so walls correctly ghost them), so draw splits in two:

def draw_opaque():
    """Pass 1+2: chevron frames + wireframe edges (unchanged logic)."""
    glBegin(GL_QUADS)
    for col, quad in chevron_quads:
        glColor3f(*col)
        for v in quad:
            glVertex3f(*v)
    glEnd()
    for width, alpha in ((3.0, 0.25), (1.0, 1.0)):
        glLineWidth(width)
        glColor4f(*palette.WALL_EDGE, alpha)
        glBegin(GL_LINES)
        for a, b in edge_lines:
            glVertex3f(*a)
            glVertex3f(*b)
        glEnd()


def draw_fills(wall_alpha, cam_pos):
    """Pass 3: translucent rock, sorted far-to-near (unchanged logic)."""
    d2 = ((_fill_centers - np.asarray(cam_pos)) ** 2).sum(axis=1)
    order = np.argsort(-d2)
    glDepthMask(GL_FALSE)
    glColor4f(*palette.WALL_FILL, wall_alpha)
    glBegin(GL_QUADS)
    for i in order:
        for v in _fill_quads[i]:
            glVertex3f(*v)
    glEnd()
    glDepthMask(GL_TRUE)
