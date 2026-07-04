"""forge — the render engine of Homeworld: A Good Basis.

A real-time Manim: glowing vector graphics in modern OpenGL.
See NEW_TESTAMENT.md Part 1 for the full design. This is the
walking skeleton (build steps 1-2): window, camera, line ribbons,
Line/Arrow/DashedLine/Grid/WireSphere. Bloom and text come next.
"""

from .app import Forge, PULSE_DT
from .camera import Camera
from .vobjects import VObject, Line, Arrow, DashedLine, Grid, WireSphere

__all__ = [
    "Forge", "PULSE_DT", "Camera",
    "VObject", "Line", "Arrow", "DashedLine", "Grid", "WireSphere",
]
