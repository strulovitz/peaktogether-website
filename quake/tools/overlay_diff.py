"""Build-time visual overlay-diff tool.

Single-file Tkinter app to compare scanned book figures against AI-generated
renders by aligning them and viewing mismatches as glowing white
"shine-through". Build-time only — never ships.

The four pure helpers (binarize, transform, dilate, compose) are deterministic
and tested headless. run() launches the Tkinter GUI and is skipped in CI.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image

try:  # scipy is preferred but optional
    from scipy.ndimage import maximum_filter as _scipy_maximum_filter
except Exception:  # pragma: no cover - exercised only when scipy missing
    _scipy_maximum_filter = None


# --------------------------------------------------------------------------- #
# Pure helpers (tested headless)
# --------------------------------------------------------------------------- #
def binarize(img: np.ndarray, threshold: int) -> np.ndarray:
    """Return boolean mask: True where pixel is dark (< threshold).

    Accepts RGB (H,W,3) or grayscale (H,W) uint8. Uses luminance if RGB.
    """
    arr = np.asarray(img)
    if arr.ndim == 3:
        if arr.shape[2] >= 3:
            r = arr[..., 0].astype(np.float64)
            g = arr[..., 1].astype(np.float64)
            b = arr[..., 2].astype(np.float64)
            lum = 0.299 * r + 0.587 * g + 0.114 * b
        else:  # single-channel stored as (H,W,1)
            lum = arr[..., 0].astype(np.float64)
    elif arr.ndim == 2:
        lum = arr.astype(np.float64)
    else:
        raise ValueError(f"Unsupported image shape: {arr.shape!r}")

    return lum < float(threshold)


def transform(
    mask: np.ndarray,
    tx: float,
    ty: float,
    scale: float,
    rot_deg: float,
) -> np.ndarray:
    """Apply affine transform (translate, scale, rotate) via Pillow.

    Rotation/scale are about the image center. Returns a bool array with the
    same shape as the input.
    """
    mask = np.asarray(mask, dtype=bool)
    h, w = mask.shape
    u8 = (mask.astype(np.uint8)) * 255
    src = Image.fromarray(u8, mode="L")

    cx = w / 2.0
    cy = h / 2.0
    theta = math.radians(rot_deg)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)

    # Forward transform applied to a point p (in pixel coords):
    #   1. translate to center-origin: p - c
    #   2. scale by `scale`
    #   3. rotate by rot_deg
    #   4. translate back: + c
    #   5. translate by (tx, ty)
    #
    # Pillow's Image.transform(AFFINE) maps OUTPUT coords -> INPUT coords,
    # i.e. it needs the INVERSE transform. We build the forward matrix, then
    # invert it for Pillow.
    a = scale * cos_t
    b = -scale * sin_t
    c = scale * sin_t
    d = scale * cos_t
    e = cx + tx - (a * cx + b * cy)
    f = cy + ty - (c * cx + d * cy)

    # Invert the forward 2x3 affine to get output->input mapping for Pillow.
    det = a * d - b * c
    if abs(det) < 1e-12:
        # Degenerate (scale ~ 0): everything collapses; return empty mask.
        return np.zeros_like(mask)

    ia = d / det
    ib = -b / det
    ic = -c / det
    id_ = a / det
    ie = -(ia * e + ib * f)
    if_ = -(ic * e + id_ * f)

    out = src.transform(
        (w, h),
        Image.Transform.AFFINE,
        (ia, ib, ie, ic, id_, if_),
        resample=Image.Resampling.NEAREST,
        fillcolor=0,
    )
    return np.asarray(out) > 0


def dilate(mask: np.ndarray, px: int) -> np.ndarray:
    """Dilate boolean mask by px pixels (square structuring element).

    Uses scipy.ndimage.maximum_filter when available, otherwise a pure-NumPy
    sliding max via array shifting.
    """
    mask = np.asarray(mask, dtype=bool)
    if px <= 0:
        return mask.copy()

    size = 2 * px + 1
    if _scipy_maximum_filter is not None:
        return _scipy_maximum_filter(mask, size=size).astype(bool)

    # Pure-NumPy fallback: pad then OR over every offset in the square kernel.
    padded = np.pad(mask, px, mode="constant", constant_values=False)
    h, w = mask.shape
    out = np.zeros_like(mask)
    for dy in range(size):
        for dx in range(size):
            out |= padded[dy : dy + h, dx : dx + w]
    return out


def compose(back_ink: np.ndarray, front_ink: np.ndarray) -> np.ndarray:
    """Composite on mid-grey (128) field.

    back-ink pixels -> WHITE (255); front-ink pixels -> BLACK (0) over them.
    White-remaining = back has ink the front lacks = MISMATCH.
    """
    back = np.asarray(back_ink, dtype=bool)
    front = np.asarray(front_ink, dtype=bool)
    if back.shape != front.shape:
        raise ValueError(
            f"shape mismatch: back {back.shape} vs front {front.shape}"
        )

    out = np.full(back.shape, 128, dtype=np.uint8)
    out[back] = 255
    out[front] = 0
    return out


# --------------------------------------------------------------------------- #
# GUI entry (NOT tested — Tkinter, skipped in CI)
# --------------------------------------------------------------------------- #
def run(back_png: Path, front_png: Path) -> None:
    """Launch Tkinter GUI. back=scan, front=render (default; Flip swaps)."""
    import tkinter as tk
    from tkinter import filedialog
    from PIL import ImageTk

    back_png = Path(back_png)
    front_png = Path(front_png)

    def load_array(path: Path) -> np.ndarray:
        return np.asarray(Image.open(path).convert("RGB"))

    state = {
        "back_img": load_array(back_png),
        "front_img": load_array(front_png),
        # per-layer transform: tx, ty, scale, rot
        "back": {"tx": 0.0, "ty": 0.0, "scale": 1.0, "rot": 0.0},
        "front": {"tx": 0.0, "ty": 0.0, "scale": 1.0, "rot": 0.0},
        "threshold": 128,
        "thicken": 0,
        "composite": None,  # last composed uint8 array (full-res)
        "active": "front",  # layer dragged with the mouse
    }

    root = tk.Tk()
    root.title("overlay_diff — shine-through mismatch viewer")

    # --- top button bar ------------------------------------------------- #
    bar = tk.Frame(root)
    bar.pack(side=tk.TOP, fill=tk.X)

    def do_load(layer: str) -> None:
        path = filedialog.askopenfilename(
            title=f"Load {layer}",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"),
                       ("All files", "*.*")],
        )
        if path:
            state[f"{layer}_img"] = load_array(Path(path))
            redraw()

    def do_flip() -> None:
        state["back_img"], state["front_img"] = (
            state["front_img"],
            state["back_img"],
        )
        state["back"], state["front"] = state["front"], state["back"]
        _sync_sliders()
        redraw()

    def do_save() -> None:
        if state["composite"] is None:
            return
        path = filedialog.asksaveasfilename(
            title="Save Composite",
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
        )
        if path:
            Image.fromarray(state["composite"], mode="L").save(path)

    tk.Button(bar, text="Load Back", command=lambda: do_load("back")).pack(
        side=tk.LEFT, padx=2, pady=2
    )
    tk.Button(bar, text="Load Front", command=lambda: do_load("front")).pack(
        side=tk.LEFT, padx=2, pady=2
    )
    tk.Button(bar, text="Flip", command=do_flip).pack(side=tk.LEFT, padx=2, pady=2)
    tk.Button(bar, text="Save Composite", command=do_save).pack(
        side=tk.LEFT, padx=2, pady=2
    )

    # --- slider construction helper ------------------------------------- #
    sliders: dict[str, tk.Scale] = {}

    def make_slider(parent, key, label, lo, hi, init, resolution):
        frame = tk.Frame(parent)
        frame.pack(side=tk.TOP, fill=tk.X)
        tk.Label(frame, text=label, width=8, anchor="w").pack(side=tk.LEFT)
        s = tk.Scale(
            frame,
            from_=lo,
            to=hi,
            orient=tk.HORIZONTAL,
            resolution=resolution,
            length=300,
            command=lambda _v: redraw(),
        )
        s.set(init)
        s.pack(side=tk.LEFT, fill=tk.X, expand=True)
        sliders[key] = s

    controls = tk.Frame(root)
    controls.pack(side=tk.TOP, fill=tk.X)

    for layer in ("back", "front"):
        tk.Label(controls, text=f"{layer.capitalize()} layer:",
                 anchor="w").pack(side=tk.TOP, fill=tk.X)
        st = state[layer]
        make_slider(controls, f"{layer}_tx", "Pan X", -200, 200, st["tx"], 1)
        make_slider(controls, f"{layer}_ty", "Pan Y", -200, 200, st["ty"], 1)
        make_slider(controls, f"{layer}_scale", "Scale", 0.25, 4.0,
                    st["scale"], 0.01)
        make_slider(controls, f"{layer}_rot", "Rotate", -180, 180, st["rot"], 1)

    tk.Label(controls, text="Global:", anchor="w").pack(side=tk.TOP, fill=tk.X)
    make_slider(controls, "threshold", "Threshold", 0, 255,
                state["threshold"], 1)
    make_slider(controls, "thicken", "Thicken", 0, 12, state["thicken"], 1)

    def _sync_sliders() -> None:
        """Push state -> slider widgets (after a Flip)."""
        for layer in ("back", "front"):
            st = state[layer]
            sliders[f"{layer}_tx"].set(st["tx"])
            sliders[f"{layer}_ty"].set(st["ty"])
            sliders[f"{layer}_scale"].set(st["scale"])
            sliders[f"{layer}_rot"].set(st["rot"])

    # --- canvas --------------------------------------------------------- #
    canvas = tk.Canvas(root, width=700, height=500, bg="grey50",
                       highlightthickness=0)
    canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    canvas_img_id = {"id": None}
    photo_ref = {"img": None}  # keep a reference so Tk doesn't GC it

    def _read_sliders() -> None:
        for layer in ("back", "front"):
            state[layer]["tx"] = float(sliders[f"{layer}_tx"].get())
            state[layer]["ty"] = float(sliders[f"{layer}_ty"].get())
            state[layer]["scale"] = float(sliders[f"{layer}_scale"].get())
            state[layer]["rot"] = float(sliders[f"{layer}_rot"].get())
        state["threshold"] = int(float(sliders["threshold"].get()))
        state["thicken"] = int(float(sliders["thicken"].get()))

    def compute_composite() -> np.ndarray:
        _read_sliders()
        thr = state["threshold"]

        back_mask = binarize(state["back_img"], thr)
        front_mask = binarize(state["front_img"], thr)

        # Front must match back's grid; resize front to back's shape if needed.
        if front_mask.shape != back_mask.shape:
            h, w = back_mask.shape
            fimg = Image.fromarray(front_mask.astype(np.uint8) * 255, mode="L")
            fimg = fimg.resize((w, h), Image.Resampling.NEAREST)
            front_mask = np.asarray(fimg) > 0

        b = state["back"]
        f = state["front"]
        back_t = transform(back_mask, b["tx"], b["ty"], b["scale"], b["rot"])
        front_t = transform(front_mask, f["tx"], f["ty"], f["scale"], f["rot"])

        if state["thicken"] > 0:
            front_t = dilate(front_t, state["thicken"])

        return compose(back_t, front_t)

    def redraw(*_args) -> None:
        comp = compute_composite()
        state["composite"] = comp

        cw = max(canvas.winfo_width(), 1)
        ch = max(canvas.winfo_height(), 1)
        h, w = comp.shape
        scale = min(cw / w, ch / h)
        scale = scale if scale > 0 else 1.0
        disp_w = max(int(w * scale), 1)
        disp_h = max(int(h * scale), 1)

        pil = Image.fromarray(comp, mode="L").resize(
            (disp_w, disp_h), Image.Resampling.NEAREST
        )
        photo = ImageTk.PhotoImage(pil)
        photo_ref["img"] = photo
        if canvas_img_id["id"] is None:
            canvas_img_id["id"] = canvas.create_image(
                cw // 2, ch // 2, image=photo, anchor=tk.CENTER
            )
        else:
            canvas.coords(canvas_img_id["id"], cw // 2, ch // 2)
            canvas.itemconfig(canvas_img_id["id"], image=photo)

    # --- mouse drag pans the active (front) layer ----------------------- #
    drag = {"x": 0, "y": 0}

    def on_press(event) -> None:
        drag["x"] = event.x
        drag["y"] = event.y

    def on_drag(event) -> None:
        dx = event.x - drag["x"]
        dy = event.y - drag["y"]
        drag["x"] = event.x
        drag["y"] = event.y
        layer = state["active"]
        s = sliders[f"{layer}_tx"]
        s.set(_clamp(s.get() + dx, -200, 200))
        s = sliders[f"{layer}_ty"]
        s.set(_clamp(s.get() + dy, -200, 200))
        redraw()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<Configure>", lambda _e: redraw())

    redraw()
    root.mainloop()


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


if __name__ == "__main__":  # pragma: no cover
    import argparse

    parser = argparse.ArgumentParser(description="Overlay-diff viewer")
    parser.add_argument("back", type=Path, help="back image (scan)")
    parser.add_argument("front", type=Path, help="front image (render)")
    args = parser.parse_args()
    run(args.back, args.front)
