from __future__ import annotations

import numpy as np


def key_out(rgba: np.ndarray, key_rgb: tuple[int, int, int], threshold: int) -> np.ndarray:
    """Set alpha=0 for pixels matching key_rgb within threshold. Returns RGBA uint8 array."""
    arr = np.asarray(rgba)
    if arr.ndim != 3 or arr.shape[2] not in (3, 4):
        raise ValueError("key_out expects an (H, W, 3) or (H, W, 4) array")

    h, w = arr.shape[:2]

    if arr.shape[2] == 3:
        out = np.empty((h, w, 4), dtype=np.uint8)
        out[..., :3] = arr
        out[..., 3] = 255
    else:
        out = arr.astype(np.uint8, copy=True)

    # Euclidean RGB distance to the key color.
    rgb = out[..., :3].astype(np.float64)
    key = np.asarray(key_rgb, dtype=np.float64)
    dist = np.linalg.norm(rgb - key, axis=2)

    mask = dist < threshold
    out[mask, 3] = 0
    return out


def key_out_white(rgba: np.ndarray, threshold: int = 210) -> np.ndarray:
    """Key out near-white background pixels. Keeps anti-aliased grey text edges.
    Any pixel where ALL RGB channels are above threshold gets alpha=0.
    Black/dark text and grey anti-alias edges are preserved with their natural alpha."""
    arr = np.asarray(rgba)
    if arr.ndim != 3 or arr.shape[2] not in (3, 4):
        raise ValueError("key_out_white expects an (H, W, 3) or (H, W, 4) array")

    if arr.shape[2] == 3:
        out = np.empty((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)
        out[..., :3] = arr
        out[..., 3] = 255
    else:
        out = arr.astype(np.uint8, copy=True)

    rgb = out[..., :3]
    mask = (rgb[..., 0] > threshold) & (rgb[..., 1] > threshold) & (rgb[..., 2] > threshold)
    out[mask, 3] = 0
    return out


def content_bbox(rgba: np.ndarray) -> tuple[int, int, int, int]:
    """Return (x_min, y_min, x_max_excl, y_max_excl) of non-transparent pixels.

    Pixel convention: top-left origin, half-open (max is exclusive).
    If fully transparent, return (0, 0, 0, 0).
    """
    arr = np.asarray(rgba)
    if arr.ndim != 3 or arr.shape[2] != 4:
        raise ValueError("content_bbox expects an (H, W, 4) RGBA array")

    alpha = arr[..., 3]
    opaque = alpha > 0

    if not opaque.any():
        return (0, 0, 0, 0)

    ys = np.any(opaque, axis=1)  # rows containing content
    xs = np.any(opaque, axis=0)  # cols containing content

    y_indices = np.nonzero(ys)[0]
    x_indices = np.nonzero(xs)[0]

    y_min = int(y_indices[0])
    y_max = int(y_indices[-1])
    x_min = int(x_indices[0])
    x_max = int(x_indices[-1])

    return (x_min, y_min, x_max + 1, y_max + 1)


def trim(rgba: np.ndarray, padding: int = 0) -> np.ndarray:
    """Crop to non-transparent content + padding on all sides. Clamped to image bounds."""
    arr = np.asarray(rgba)
    if arr.ndim != 3 or arr.shape[2] != 4:
        raise ValueError("trim expects an (H, W, 4) RGBA array")

    bbox = content_bbox(arr)
    if bbox == (0, 0, 0, 0):
        return arr

    h, w = arr.shape[:2]
    x0, y0, x1, y1 = bbox

    x0 = max(0, x0 - padding)
    y0 = max(0, y0 - padding)
    x1 = min(w, x1 + padding)
    y1 = min(h, y1 + padding)

    return arr[y0:y1, x0:x1].copy()
