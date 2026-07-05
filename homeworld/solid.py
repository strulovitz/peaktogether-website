"""Solid shaded meshes (Amendment A1).

SolidMesh: an opaque triangle mesh vobject — base geometry + painted
per-vertex colors + per-vertex emissive. set_transform(R, pos) places
it in the world each frame. Flat shading falls out naturally because
the shipwright emits duplicated vertices per face.

SolidRenderer: batches every visible SolidMesh into one draw call
with depth testing and no blending — ships are NOT transparent.
"""

import numpy as np
import moderngl

from shaders import MESH_VERT, MESH_FRAG
from vobjects import VObject


def compute_normals(verts, tris):
    n = np.zeros_like(verts)
    v0 = verts[tris[:, 0]]
    v1 = verts[tris[:, 1]]
    v2 = verts[tris[:, 2]]
    fn = np.cross(v1 - v0, v2 - v0)
    for k in range(3):
        np.add.at(n, tris[:, k], fn)
    length = np.linalg.norm(n, axis=1, keepdims=True)
    length[length < 1e-12] = 1.0
    return n / length


class SolidMesh(VObject):
    def __init__(self, vertices, triangles, colors, emissive=None, **kw):
        super().__init__(**kw)
        self._base_v = np.asarray(vertices, dtype=np.float64).copy()
        self._tris = np.asarray(triangles, dtype=np.int64).reshape(-1, 3)
        self._base_n = compute_normals(self._base_v, self._tris)
        self._colors = np.asarray(colors, dtype=np.float64).copy()
        if emissive is None:
            emissive = np.zeros((self._base_v.shape[0], 3))
        self._emissive = np.asarray(emissive, dtype=np.float64).copy()
        self._flat = self._tris.reshape(-1)
        self._hl = 0.0
        self._soup = np.zeros((0, 13), dtype=np.float32)
        self.set_transform(np.eye(3), (0.0, 0.0, 0.0))

    def set_highlight(self, on):
        self._hl = 0.30 if on else 0.0

    def set_transform(self, R, pos):
        R = np.asarray(R, dtype=np.float64)
        pos = np.asarray(pos, dtype=np.float64)
        wv = self._base_v @ R.T + pos
        wn = self._base_n @ R.T
        f = self._flat
        soup = np.concatenate(
            [wv[f], wn[f], self._colors[f], self._emissive[f] + self._hl],
            axis=1)
        self._soup = soup.astype(np.float32)

    def segments(self):
        return np.zeros((0, 2, 3), dtype=np.float64)   # not a line object


class SolidRenderer:
    def __init__(self, ctx):
        self.ctx = ctx
        self.prog = ctx.program(vertex_shader=MESH_VERT,
                                fragment_shader=MESH_FRAG)
        self._vbo = ctx.buffer(reserve=4 * 1024 * 1024, dynamic=True)
        self._vao = self._make_vao()

    def _make_vao(self):
        return self.ctx.vertex_array(
            self.prog,
            [(self._vbo, "3f 3f 4f 3f",
              "in_pos", "in_normal", "in_color", "in_emissive")],
        )

    def draw(self, meshes, mvp_t_f32, eye):
        soups = [m._soup for m in meshes if m._soup.shape[0] > 0]
        if not soups:
            return
        data = np.concatenate(soups, axis=0)
        if data.nbytes > self._vbo.size:
            self._vbo.release()
            self._vbo = self.ctx.buffer(reserve=2 * data.nbytes,
                                        dynamic=True)
            self._vao = self._make_vao()
        self._vbo.write(data.tobytes())
        self.prog["u_mvp"].write(mvp_t_f32)
        self.prog["u_eye"].value = tuple(float(v) for v in eye)
        self._vao.render(moderngl.TRIANGLES, vertices=data.shape[0])
