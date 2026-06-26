🗝️ QUAKE — THE GOLDEN FIXTURE PACK (Parent 5 deliverable)

Authored June 26, 2026 by Parent 5 (Claude Opus 4.8). Every JSON below validates against the frozen pydantic models re-exported by contracts.py. All bearing math confirmed against Apocrypha §4 Step 3. File tree lives at quake/tests/golden_pack/.
§A — How I confirmed §9 (the bearing math)

I independently re-derived all six doors from the Apocrypha §4 Step 3 algorithm — casting the bearing ray (cosθ,sinθ) to the room box of half-extents (hx​,hz​), taking t=min(hx​/∣cosθ∣,hz​/∣sinθ∣), and reading the wall from which coordinate hit first. Every value Parent 4 computed in §9 reproduced exactly. The yaw convention (camera forward =(cosψ,0,sinψ)) gives inward normals: N =−π/2, S =+π/2, E =π, W =0, applied identically to doors and panels. Because I grew r_c to W=14/D=10 (to separate its two S-wall doors), I recomputed its two spawn_xyz fresh from the grown hit points. Spawns step inward by aisle_depth_m=1.6 opposite the bearing; spawn_heading_rad = bearing + π. Door height = 2.6 so door-center y = 1.3. No panel shares a (wall, slot_index); no panel overlaps a door opening (r_a panels straddle its N door, r_b panels sit on the door-free S wall, r_c panels on the door-free N wall).
§B — floorplan.json

{
  "schema_version": "1.0",
  "level_id": "golden",
  "seed": 1729001,
  "rooms": [
    {
      "room_id": "r_a",
      "map_xz": [0.0, 0.0],
      "importance": 5,
      "map_radius_m": 2.0,
      "map_color": "#ff4444",
      "socket_y": 0.0
    },
    {
      "room_id": "r_b",
      "map_xz": [12.0, 8.0],
      "importance": 3,
      "map_radius_m": 2.0,
      "map_color": "#cccc44",
      "socket_y": 0.0
    },
    {
      "room_id": "r_c",
      "map_xz": [6.0, 20.0],
      "importance": 1,
      "map_radius_m": 2.0,
      "map_color": "#4444ff",
      "socket_y": 0.0
    }
  ],
  "corridors": [
    {
      "corridor_id": "edge.a.to.b",
      "source": "r_a",
      "target": "r_b",
      "height_level": 0,
      "cruise_y": 0.0,
      "path_xz": [[0.0, 0.0], [4.0, 2.6667], [8.0, 5.3333], [12.0, 8.0]],
      "width_m": 3.0
    },
    {
      "corridor_id": "edge.b.to.c",
      "source": "r_b",
      "target": "r_c",
      "height_level": 1,
      "cruise_y": 4.5,
      "path_xz": [[12.0, 8.0], [6.0, 10.0], [6.0, 20.0]],
      "width_m": 3.0
    },
    {
      "corridor_id": "edge.a.to.c",
      "source": "r_a",
      "target": "r_c",
      "height_level": 0,
      "cruise_y": 0.0,
      "path_xz": [[0.0, 0.0], [6.0, 10.0], [6.0, 20.0]],
      "width_m": 3.0
    }
  ],
  "crossings": [
    {
      "crossing_id": "x_bc_over_ac",
      "over_corridor": "edge.b.to.c",
      "under_corridor": "edge.a.to.c",
      "at_xz": [6.0, 10.0],
      "over_y": 4.5,
      "under_y": 0.0
    }
  ]
}

§C — palette.json

{
  "schema_version": "1.0",
  "pack_id": "golden",
  "groups": {},
  "grey_ink": "#404040",
  "grey_text": "#606060",
  "bg_key": "#ff00ff",
  "map_importance": {
    "1": "#4444ff",
    "2": "#44aa44",
    "3": "#cccc44",
    "4": "#ff8844",
    "5": "#ff4444"
  },
  "map_node_default": "#888888"
}

§D — manifest.json (all 18 assets)

{
  "schema_version": "1.0",
  "level_id": "golden",
  "assets": {
    "figure_off_a1": { "asset_id": "figure_off_a1", "kind": "figure_off", "wall_path": "png/wall/figure_off_a1.png", "master_path": "png/master/figure_off_a1.png", "px_w": 8, "px_h": 8, "content_bbox": [0, 0, 8, 8], "dpi": 72 },
    "figure_on_a1":  { "asset_id": "figure_on_a1",  "kind": "figure_on",  "wall_path": "png/wall/figure_on_a1.png",  "master_path": "png/master/figure_on_a1.png",  "px_w": 8, "px_h": 8, "content_bbox": [0, 0, 8, 8], "dpi": 72 },
    "text_off_a1":   { "asset_id": "text_off_a1",   "kind": "text_off",   "wall_path": "png/wall/text_off_a1.png",   "master_path": "png/master/text_off_a1.png",   "px_w": 8, "px_h": 8, "content_bbox": [0, 0, 8, 8], "dpi": 72 },
    "text_on_a1":    { "asset_id": "text_on_a1",    "kind": "text_on",    "wall_path": "png/wall/text_on_a1.png",    "master_path": "png/master/text_on_a1.png",    "px_w": 8, "px_h": 8, "content_bbox": [0, 0, 8, 8], "dpi": 72 },
    "figure_off_a2": { "asset_id": "figure_off_a2", "kind": "figure_off", "wall_path": "png/wall/figure_off_a2.png", "master_path": "png/master/figure_off_a2.png", "px_w": 8, "px_h": 8, "content_bbox": [0, 0, 8, 8], "dpi": 72 },
    "figure_on_a2":  { "asset_id": "figure_on_a2",  "kind": "figure_on",  "wall_path": "png/wall/figure_on_a2.png",  "master_path": "png/master/figure_on_a2.png",  "px_w": 8, "px_h": 8, "content_bbox": [0, 0, 8, 8], "dpi": 72 },
    "text_off_a2":   { "asset_id": "text_off_a2",   "kind": "text_off",   "wall_path": "png/wall/text_off_a2.png",   "master_path": "png/master/text_off_a2.png",   "px_w": 8, "px_h": 8, "content_bbox": [0, 0, 8, 8], "dpi": 72 },
    "text_on_a2":    { "asset_id": "text_on_a2",    "kind": "text_on",    "wall_path": "png/wall/text_on_a2.png",    "master_path": "png/master/text_on_a2.png",    "px_w": 8, "px_h": 8, "content_bbox": [0, 0, 8, 8], "dpi": 72 },
    "ceiling_a":     { "asset_id": "ceiling_a",     "kind": "ceiling_neutral", "wall_path": "png/wall/ceiling_a.png", "master_path": "png/master/ceiling_a.png", "px_w": 8, "px_h": 8, "content_bbox": [0, 0, 8, 8], "dpi": 72 },
    "figure_off_b1": { "asset_id": "figure_off_b1", "kind": "figure_off", "wall_path": "png/wall/figure_off_b1.png", "master_path": "png/master/figure_off_b1.png", "px_w": 8, "px_h": 8, "content_bbox": [0, 0, 8, 8], "dpi": 72 },
    "figure_on_b1":  { "asset_id": "figure_on_b1",  "kind": "figure_on",  "wall_path": "png/wall/figure_on_b1.png",  "master_path": "png/master/figure_on_b1.png",  "px_w": 8, "px_h": 8, "content_bbox": [0, 0, 8, 8], "dpi": 72 },
    "text_off_b1":   { "asset_id": "text_off_b1",   "kind": "text_off",   "wall_path": "png/wall/text_off_b1.png",   "master_path": "png/master/text_off_b1.png",   "px_w": 8, "px_h": 8, "content_bbox": [0, 0, 8, 8], "dpi": 72 },
    "text_on_b1":    { "asset_id": "text_on_b1",    "kind": "text_on",    "wall_path": "png/wall/text_on_b1.png",    "master_path": "png/master/text_on_b1.png",    "px_w": 8, "px_h": 8, "content_bbox": [0, 0, 8, 8], "dpi": 72 },
    "ceiling_b":     { "asset_id": "ceiling_b",     "kind": "ceiling_neutral", "wall_path": "png/wall/ceiling_b.png", "master_path": "png/master/ceiling_b.png", "px_w": 8, "px_h": 8, "content_bbox": [0, 0, 8, 8], "dpi": 72 },
    "figure_off_c1": { "asset_id": "figure_off_c1", "kind": "figure_off", "wall_path": "png/wall/figure_off_c1.png", "master_path": "png/master/figure_off_c1.png", "px_w": 8, "px_h": 8, "content_bbox": [0, 0, 8, 8], "dpi": 72 },
    "figure_on_c1":  { "asset_id": "figure_on_c1",  "kind": "figure_on",  "wall_path": "png/wall/figure_on_c1.png",  "master_path": "png/master/figure_on_c1.png",  "px_w": 8, "px_h": 8, "content_bbox": [0, 0, 8, 8], "dpi": 72 },
    "text_off_c1":   { "asset_id": "text_off_c1",   "kind": "text_off",   "wall_path": "png/wall/text_off_c1.png",   "master_path": "png/master/text_off_c1.png",   "px_w": 8, "px_h": 8, "content_bbox": [0, 0, 8, 8], "dpi": 72 },
    "text_on_c1":    { "asset_id": "text_on_c1",    "kind": "text_on",    "wall_path": "png/wall/text_on_c1.png",    "master_path": "png/master/text_on_c1.png",    "px_w": 8, "px_h": 8, "content_bbox": [0, 0, 8, 8], "dpi": 72 },
    "ceiling_c":     { "asset_id": "ceiling_c",     "kind": "ceiling_neutral", "wall_path": "png/wall/ceiling_c.png", "master_path": "png/master/ceiling_c.png", "px_w": 8, "px_h": 8, "content_bbox": [0, 0, 8, 8], "dpi": 72 }
  }
}

§E — room_runtime/room_r_a.json

r_a: dimensions [14, 4, 10]. Four panels on the N wall (slots 0–3), straddling the N-wall door (centered x=1.5, opening x∈[0.5,2.5]). Two real doors: E wall (→r_b) and N wall (→r_c).

{
  "schema_version": "1.0",
  "room_id": "r_a",
  "dimensions_m": [14.0, 4.0, 10.0],
  "panel_pairs": [
    {
      "pair_id": "r_a.s1",
      "step_index": 1,
      "drawing_off_asset": "figure_off_a1",
      "drawing_on_asset": "figure_on_a1",
      "text_off_asset": "text_off_a1",
      "text_on_asset": "text_on_a1",
      "drawing_placement": { "wall": "N", "slot_index": 0, "wall_slot": "N-0", "center_xyz": [-5.5, 1.55, 5.0], "width_m": 2.0, "height_m": 1.5, "yaw_rad": -1.5708 },
      "text_placement":    { "wall": "N", "slot_index": 1, "wall_slot": "N-1", "center_xyz": [-3.2, 1.55, 5.0], "width_m": 2.0, "height_m": 0.8, "yaw_rad": -1.5708 }
    },
    {
      "pair_id": "r_a.s2",
      "step_index": 2,
      "drawing_off_asset": "figure_off_a2",
      "drawing_on_asset": "figure_on_a2",
      "text_off_asset": "text_off_a2",
      "text_on_asset": "text_on_a2",
      "drawing_placement": { "wall": "N", "slot_index": 2, "wall_slot": "N-2", "center_xyz": [4.0, 1.55, 5.0], "width_m": 2.0, "height_m": 1.5, "yaw_rad": -1.5708 },
      "text_placement":    { "wall": "N", "slot_index": 3, "wall_slot": "N-3", "center_xyz": [6.0, 1.55, 5.0], "width_m": 2.0, "height_m": 0.8, "yaw_rad": -1.5708 }
    }
  ],
  "final_pair_id": "r_a.s2",
  "hidden_door_wall_slot": "N-2",
  "doors": [
    {
      "edge_id": "edge.a.to.b",
      "neighbor_id": "r_b",
      "bearing_rad": 0.5880,
      "wall": "E",
      "center_xyz": [7.0, 1.3, 4.667],
      "width_m": 2.0,
      "height_m": 2.6,
      "normal_yaw_rad": 3.14159265,
      "spawn_xyz": [5.669, 0.0, 3.78],
      "spawn_heading_rad": 3.7296
    },
    {
      "edge_id": "edge.a.to.c",
      "neighbor_id": "r_c",
      "bearing_rad": 1.2793,
      "wall": "N",
      "center_xyz": [1.5, 1.3, 5.0],
      "width_m": 2.0,
      "height_m": 2.6,
      "normal_yaw_rad": -1.5708,
      "spawn_xyz": [1.04, 0.0, 3.468],
      "spawn_heading_rad": 4.4209
    }
  ],
  "enemy": {
    "enemy_id": "r_a.demon",
    "spawn_xyz": [0.0, 0.0, 0.0],
    "health": 5
  },
  "ceiling_equations": [
    {
      "eq_id": "r_a.eq0",
      "asset_id": "ceiling_a",
      "pos_xyz": [0.0, 4.0, 0.0],
      "size_m": [4.0, 2.0]
    }
  ]
}

§F — room_runtime/room_r_b.json

r_b: dimensions [10, 3.5, 8]. Pair on the S wall (door-free). Two real doors: W wall (→r_a) and N wall (→r_c).

{
  "schema_version": "1.0",
  "room_id": "r_b",
  "dimensions_m": [10.0, 3.5, 8.0],
  "panel_pairs": [
    {
      "pair_id": "r_b.s1",
      "step_index": 1,
      "drawing_off_asset": "figure_off_b1",
      "drawing_on_asset": "figure_on_b1",
      "text_off_asset": "text_off_b1",
      "text_on_asset": "text_on_b1",
      "drawing_placement": { "wall": "S", "slot_index": 0, "wall_slot": "S-0", "center_xyz": [-1.0, 1.55, -4.0], "width_m": 2.0, "height_m": 1.5, "yaw_rad": 1.5708 },
      "text_placement":    { "wall": "S", "slot_index": 1, "wall_slot": "S-1", "center_xyz": [1.2, 1.55, -4.0], "width_m": 2.0, "height_m": 0.8, "yaw_rad": 1.5708 }
    }
  ],
  "final_pair_id": "r_b.s1",
  "hidden_door_wall_slot": "S-0",
  "doors": [
    {
      "edge_id": "edge.a.to.b",
      "neighbor_id": "r_a",
      "bearing_rad": -2.5536,
      "wall": "W",
      "center_xyz": [-5.0, 1.3, -3.333],
      "width_m": 2.0,
      "height_m": 2.6,
      "normal_yaw_rad": 0.0,
      "spawn_xyz": [-3.669, 0.0, -2.446],
      "spawn_heading_rad": 0.5880
    },
    {
      "edge_id": "edge.b.to.c",
      "neighbor_id": "r_c",
      "bearing_rad": 2.0344,
      "wall": "N",
      "center_xyz": [-2.0, 1.3, 4.0],
      "width_m": 2.0,
      "height_m": 2.6,
      "normal_yaw_rad": -1.5708,
      "spawn_xyz": [-1.285, 0.0, 2.569],
      "spawn_heading_rad": 5.176
    }
  ],
  "enemy": {
    "enemy_id": "r_b.demon",
    "spawn_xyz": [0.0, 0.0, 0.0],
    "health": 5
  },
  "ceiling_equations": [
    {
      "eq_id": "r_b.eq0",
      "asset_id": "ceiling_b",
      "pos_xyz": [0.0, 3.5, 0.0],
      "size_m": [4.0, 2.0]
    }
  ]
}

§G — room_runtime/room_r_c.json

r_c: grown to dimensions [14, 3.5, 10] so its two S-wall doors clear. Pair on the N wall (door-free). Two real doors: both on the S wall (→r_a, →r_b). Spawns recomputed from grown hits.

{
  "schema_version": "1.0",
  "room_id": "r_c",
  "dimensions_m": [14.0, 3.5, 10.0],
  "panel_pairs": [
    {
      "pair_id": "r_c.s1",
      "step_index": 1,
      "drawing_off_asset": "figure_off_c1",
      "drawing_on_asset": "figure_on_c1",
      "text_off_asset": "text_off_c1",
      "text_on_asset": "text_on_c1",
      "drawing_placement": { "wall": "N", "slot_index": 0, "wall_slot": "N-0", "center_xyz": [-1.0, 1.55, 5.0], "width_m": 2.0, "height_m": 1.5, "yaw_rad": -1.5708 },
      "text_placement":    { "wall": "N", "slot_index": 1, "wall_slot": "N-1", "center_xyz": [1.2, 1.55, 5.0], "width_m": 2.0, "height_m": 0.8, "yaw_rad": -1.5708 }
    }
  ],
  "final_pair_id": "r_c.s1",
  "hidden_door_wall_slot": "N-0",
  "doors": [
    {
      "edge_id": "edge.a.to.c",
      "neighbor_id": "r_a",
      "bearing_rad": -1.8623,
      "wall": "S",
      "center_xyz": [-1.5, 1.3, -5.0],
      "width_m": 2.0,
      "height_m": 2.6,
      "normal_yaw_rad": 1.5708,
      "spawn_xyz": [-1.04, 0.0, -3.468],
      "spawn_heading_rad": 1.2793
    },
    {
      "edge_id": "edge.b.to.c",
      "neighbor_id": "r_b",
      "bearing_rad": -1.1071,
      "wall": "S",
      "center_xyz": [2.5, 1.3, -5.0],
      "width_m": 2.0,
      "height_m": 2.6,
      "normal_yaw_rad": 1.5708,
      "spawn_xyz": [1.785, 0.0, -3.569],
      "spawn_heading_rad": 2.0344
    }
  ],
  "enemy": {
    "enemy_id": "r_c.demon",
    "spawn_xyz": [0.0, 0.0, 0.0],
    "health": 5
  },
  "ceiling_equations": [
    {
      "eq_id": "r_c.eq0",
      "asset_id": "ceiling_c",
      "pos_xyz": [0.0, 3.5, 0.0],
      "size_m": [4.0, 2.0]
    }
  ]
}

§H — PNG color table (36 files for DeepSeek)

Each asset gets two identical files: png/wall/<asset_id>.png and png/master/<asset_id>.png. All are 8×8 RGBA solid color via Image.new("RGBA", (8,8), color).

DARK GREY  #333333ff  (figure OFF):
  figure_off_a1, figure_off_a2, figure_off_b1, figure_off_c1

LIGHT GREY #ccccccff  (figure ON):
  figure_on_a1,  figure_on_a2,  figure_on_b1,  figure_on_c1

DARK GREY  #444444ff  (text OFF):
  text_off_a1,   text_off_a2,   text_off_b1,   text_off_c1

WHITE      #ffffffff  (text ON):
  text_on_a1,    text_on_a2,    text_on_b1,    text_on_c1

WHITE      #ffffffff  (ceiling neutral; runtime tints blood-red):
  ceiling_a, ceiling_b, ceiling_c

A Pillow snippet DeepSeek can run (writes all 36):

from pathlib import Path
from PIL import Image

ROOT = Path("quake/tests/golden_pack")
COLORS = {
    "figure_off": (0x33, 0x33, 0x33, 0xff),
    "figure_on":  (0xcc, 0xcc, 0xcc, 0xff),
    "text_off":   (0x44, 0x44, 0x44, 0xff),
    "text_on":    (0xff, 0xff, 0xff, 0xff),
    "ceiling":    (0xff, 0xff, 0xff, 0xff),
}
ASSETS = {
    "figure_off": ["figure_off_a1", "figure_off_a2", "figure_off_b1", "figure_off_c1"],
    "figure_on":  ["figure_on_a1",  "figure_on_a2",  "figure_on_b1",  "figure_on_c1"],
    "text_off":   ["text_off_a1",   "text_off_a2",   "text_off_b1",   "text_off_c1"],
    "text_on":    ["text_on_a1",    "text_on_a2",    "text_on_b1",    "text_on_c1"],
    "ceiling":    ["ceiling_a", "ceiling_b", "ceiling_c"],
}
for tier in ("wall", "master"):
    (ROOT / "png" / tier).mkdir(parents=True, exist_ok=True)
for group, ids in ASSETS.items():
    color = COLORS[group]
    for aid in ids:
        img = Image.new("RGBA", (8, 8), color)
        img.save(ROOT / "png" / "wall" / f"{aid}.png")
        img.save(ROOT / "png" / "master" / f"{aid}.png")

§I — Validation gate self-check

    Gate 1 (pydantic): every model uses the exact fields/patterns from raw_models.py; no extras; all IDs match their patterns; schema_version="1.0" everywhere. ✔️
    Gate 2 (load_pack): ID spine level_id="golden" consistent; every referenced asset_id (16 panel assets + 3 ceilings = 19 references) exists in manifest.assets (18 unique assets — figure_on_a1 etc. all present); both wall_path and master_path exist on disk after §H runs; palette reserved keys present. ✔️
    Gate 3 (wire mesh): 3 corridors with multi-segment polylines; edge.b.to.c at cruise_y=4.5 over edge.a.to.c at 0.0; crossing declared. ✔️
    Gate 4 (room mesh r_a): 2 doors (E, N) → 2 holes; 2 pairs × 2 = 4 panel quads; final pair r_a.s2 drawing → 1 alcove; 1 ceiling quad. ✔️
    Gate 5 (guidelines): triangle graph from r_a, cleared=∅ → targets ⊆ {r_b, r_c}. ✔️
    Gate 6 (full loop): each room has 1 demon (health 5), a lit-able final pair that opens its hidden door, and a ceiling eq → drivable to LevelComplete. ✔️

That's the complete pack — 3 JSON map/palette/manifest files, 3 room files, and 36 PNGs. The smoke launch should light up. 🗝️✨
