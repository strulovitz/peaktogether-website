import pytest

from readmode import read_uv_transform, draw_read, MAX_ZOOM
from contracts import Vec2
from conftest import skip_if_no_gl


def test_zoom_clamped_low():
    z, pan = read_uv_transform(0.5, (0.0, 0.0))
    assert z == 1.0


def test_zoom_clamped_high():
    z, pan = read_uv_transform(100.0, (0.0, 0.0))
    assert z == MAX_ZOOM


def test_pan_clamped():
    # At zoom 2: max pan per axis = (1 - 1/2) * 0.5 = 0.25
    z, (px, py) = read_uv_transform(2.0, (5.0, 5.0))
    assert z == 2.0
    assert abs(px) <= 0.25 + 1e-9
    assert abs(py) <= 0.25 + 1e-9
    # Check exact clamp: input 5.0 -> clamped to 0.25
    assert abs(px) == pytest.approx(0.25)
    assert abs(py) == pytest.approx(0.25)


def test_pan_zero_at_zoom1():
    z, (px, py) = read_uv_transform(1.0, (0.5, -0.3))
    assert z == 1.0
    assert px == 0.0
    assert py == 0.0


@skip_if_no_gl
def test_draw_smoke():
    import tempfile, os
    from PIL import Image
    # Create a tiny PNG
    tmp = tempfile.mkdtemp()
    path = os.path.join(tmp, "test.png")
    img = Image.new("RGB", (8, 8), (255, 0, 0))
    img.save(path)
    # Should not raise
    draw_read(path, 1.0, (0.0, 0.0))
