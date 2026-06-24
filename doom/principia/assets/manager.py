from __future__ import annotations

import json
import os

from PIL import Image, ImageDraw, ImageFont

from principia.schema import AssetEntry

_DEFAULT_PX = 1024


class AssetManager:
    def __init__(self, pack_dir: str) -> None:
        self.pack_dir: str = pack_dir
        self.manifest: dict[str, AssetEntry] = self._load_manifest(pack_dir)
        self._wall_cache: dict[str, tuple[object, object]] = {}

    @staticmethod
    def _load_manifest(pack_dir: str) -> dict[str, AssetEntry]:
        path = os.path.join(pack_dir, "manifest.json")
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        if not isinstance(raw, dict):
            raise ValueError("manifest.json must be a JSON object")
        return {bid: AssetEntry.model_validate(entry) for bid, entry in raw.items()}

    # ------------------------------------------------------------------
    # Pure-PIL layer (testable without Ursina)
    # ------------------------------------------------------------------
    def _entry_size(self, block_id: str) -> tuple[int, int]:
        entry = self.manifest.get(block_id)
        if entry is not None:
            return (entry.w_px, entry.h_px)
        return (_DEFAULT_PX, _DEFAULT_PX)

    def _make_placeholder(
        self, label: str, on: bool, size: tuple[int, int]
    ) -> Image.Image:
        w, h = size
        if on:
            bg = (40, 120, 80, 255)     # colored for the "on" state
            fg = (255, 255, 255, 255)
            state = "ON"
        else:
            bg = (90, 90, 90, 255)      # grayscale for the "off" state
            fg = (20, 20, 20, 255)
            state = "OFF"
        img = Image.new("RGBA", (w, h), bg)
        draw = ImageDraw.Draw(img)
        # frame so off/on differ structurally as well as in color
        draw.rectangle([2, 2, w - 3, h - 3], outline=fg, width=max(2, w // 256))
        # Load a TrueType font at a LARGE size so text fills the panel.
        font = None
        for name in ("arial.ttf", "DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf"):
            try:
                font = ImageFont.truetype(name, min(w, h) // 12)
                break
            except OSError:
                continue
        if font is None:
            font = ImageFont.load_default()
        label_text = f"{label} [{state}]"
        bbox = draw.textbbox((0, 0), label_text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (w - tw) / 2 - bbox[0]
        y = (h - th) / 2 - bbox[1]
        draw.text((x, y), label_text, fill=fg, font=font)
        return img

    def _resolve_image(self, rel_path: str, label: str, on: bool) -> Image.Image:
        """Return a real PNG if it exists on disk, else a labeled placeholder.

        `rel_path` is interpreted relative to `pack_dir`. Never raises for a
        missing PNG — that is an expected condition before baking.
        """
        size = self._entry_size(label)
        if rel_path:
            abs_path = os.path.join(self.pack_dir, rel_path)
            if os.path.isfile(abs_path):
                try:
                    return Image.open(abs_path).convert("RGBA")
                except OSError:
                    pass  # fall through to placeholder
        return self._make_placeholder(label, on, size)

    # ------------------------------------------------------------------
    # Ursina layer (thin wrapper + cache)
    # ------------------------------------------------------------------
    def wall_textures(self, block_id: str):
        if block_id in self._wall_cache:
            return self._wall_cache[block_id]

        from ursina import Texture  # imported lazily so the PIL layer is headless

        entry = self.manifest.get(block_id)
        off_rel = entry.off_png if entry is not None else ""
        on_rel = entry.on_png if entry is not None else ""

        off_img = self._resolve_image(off_rel, block_id, on=False)
        on_img = self._resolve_image(on_rel, block_id, on=True)

        off_tex = Texture(off_img)
        on_tex = Texture(on_img)

        result = (off_tex, on_tex)
        self._wall_cache[block_id] = result
        return result

    def equation_texture(self, eq_id: str):
        raise NotImplementedError("M3")

    def floor_map_texture(self, level_id: str):
        raise NotImplementedError("M4")

    def name_tile_texture(self, room_id: str):
        raise NotImplementedError("M4")
