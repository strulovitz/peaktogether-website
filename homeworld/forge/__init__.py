"""forge — the render engine of Homeworld: A Good Basis.

A real-time Manim: glowing vector graphics in modern OpenGL.
See NEW_TESTAMENT.md Part 1 for the full design. Feature-complete:
window + camera + bloom + the full frozen primitive vocabulary
(NT 1.4) + glyph-atlas text + screen overlay.
"""

from app import Forge, PULSE_DT
from camera import Camera
from vobjects import (
    VObject, Line, Arrow, DashedLine, Grid, WireSphere,
    WireMesh, SpannedBox, Ellipsoid, Trail, Label, ImagePanel,
)

__all__ = [
    "Forge", "PULSE_DT", "Camera",
    "VObject", "Line", "Arrow", "DashedLine", "Grid", "WireSphere",
    "WireMesh", "SpannedBox", "Ellipsoid", "Trail", "Label", "ImagePanel",
]
