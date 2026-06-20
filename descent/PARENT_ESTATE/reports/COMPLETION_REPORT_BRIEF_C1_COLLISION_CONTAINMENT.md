# COMPLETION REPORT — CHILD BRIEF #C1: SHIP COLLISION / CONTAINMENT

> **To:** Parent #7 (Claude Opus 4.8)
> **From:** Nir (strulovitz) via DeepSeek V4 Pro
> **Date:** June 17, 2026
> **Status:** ✅ COMPLETE — 8 iterations, final version working

---

## What was built

`containment.py` — a pure-geometry module (no GL, no rendering, no global state) that keeps the ship inside the rock-bounded world and blocks it at undefeated robots. Called from `app.py` between `ship.update(dt, keys)` and `ship.apply_view()`.

## Final design (v8)

### Wall confinement
- Confines the ship's center to `CONFINE_RADIUS = 4.0` around the nearest corridor segment's centerline
- Uses `corridor.seg_bounds` (same data robots use: `"start"`, `"end"`, `"radius"`)
- Slide-don't-stop: removes only the INTO-wall component of velocity, keeps the ALONG-wall component
- Inside the atrium sphere (radius 34): free flight, no correction
- The confinement radius 4.0 is well inside the square corners (~8.5) — ship never sees through walls

### Robot blocking ("oranges in a box")
- Each undefeated robot = a sphere centered on the corridor centerline (not the drawn floor position)
- Sphere radius = `tube_radius × √2 − SHIP_RADIUS + 0.3` — sized to plug the entire tube, no over/under/around lane
- Diagonal safety factor (√2) ensures blocking works even if tubes were square
- Defeated robots are pass-through
- Hard stop + slide at the sphere surface

### Combined resolve order
```
walls → robots → walls
```
So a robot push can never shove the ship out through a wall.

## The journey (8 versions, for context)

| v | What | Problem |
|---|------|---------|
| v1 | hub.inside + finite-difference normal + slide | SHIP_RADIUS too small (0.6), robot sphere too small (used decoration constant `_HULL_R = 1.6`) |
| v2 | Bumped SHIP_RADIUS to 1.5, robot radius from hull vertices | Robot still bypassable — sphere centered low in tube, ship flew over it |
| v3 | Tube-spanning PLUG (disc) | Ship slid along disc, pushed through wall into void |
| v4 | "Oranges in a box": sphere on tube axis, sized to plug tube | **Robot blocking FIXED**, but wall slide still pushed ship through wall into void |
| v5 | Iterative constraint solve (6 passes) | Still leaked through walls when robot push met wall |
| v6 | Inner-tube axis confinement (child's attempt at new wall code) | Broken — rolled back by Nir |
| v7 | Clean nearest-centerline confinement, slide-don't-stop (walls only) | Correct wall approach, but child DELETED all robot code |
| **v8** | **v4 robot blocking + v7 wall confinement combined** | **✅ WORKS** |

## Key lessons from this brief

1. The corridor's `inside()` test is ROUND (cylindrical), but the drawn walls are SQUARE. The ship can reach the square corners (~8.5 from axis) while staying "inside" the round collision test (radius 6). This mismatch caused all the early wall-leak bugs.

2. A robot's drawn position is low in the tube (center − up × radius × 0.45). A sphere centered there leaves a gap above. The sphere must be centered on the tube AXIS to plug the corridor.

3. `corridor.seg_bounds` is the correct public data for both walls and robots — it has `"start"`, `"end"`, `"radius"` per segment. Using `corridor._nodes` (private) is fragile.

## Files changed

| File | Change |
|------|--------|
| `containment.py` | **New file** — 200 lines, pure geometry |
| `app.py` | 2 lines added: `import containment` + `containment.resolve(ship, hub, prev_pos)` call between ship.update and ship.apply_view |

No other files touched.

## What still needs building (from PARENT_PROMPT_7)

| Gap | Status |
|-----|--------|
| Ship wall containment | ✅ **DONE** (Brief #C1) |
| Robot blocking | ✅ **DONE** (Brief #C1) |
| T.16000M joystick wiring | 🟡 TODO |
| Defeat plaque white rectangle | 🟡 TODO |
| Face panel photos | 🟢 Nir's task |

## How to run

```
cd C:\Users\nir_s\peaktogether-website
python app.py
```

Currently loads Basel corridor (7 robots). Ship stays in rock, robots block until defeated. Win-only.
