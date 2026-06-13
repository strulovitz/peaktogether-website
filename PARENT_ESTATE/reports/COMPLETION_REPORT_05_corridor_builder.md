COMPLETION REPORT — corridor_builder

To the parent. Carried up by Nir. DeepSeek commits to /PARENT_ESTATE/reports/.
FILES

    corridor_builder.py — CorridorGeometry + build_corridor()
    corridor_demo.py — standalone flythrough (screenshot-verified ✅)

FINAL SIGNATURES (locked for hub_builder / game_state)

build_corridor(corridor_data, origin=(0,0,0), direction=(0,0,-1)) -> CorridorGeometry

# geometry / placement
entrance_pose()            -> ((x,y,z), (nx,ny,nz))   # mouth center + OUTWARD normal (toward hub)
inside(point, margin=0.0)  -> bool                    # per-segment slab union; straight OR bent
seg_bounds                 -> list[dict]              # each: {start:[x,y,z], end:[x,y,z],
                                                      #        right:[x,y,z], up:[x,y,z], radius:float}
hostage_positions()        -> list[(x,y,z)]           # 3 cavern-floor anchors
stations()                 -> list[((x,y,z), yaw)]
get_robots()               -> list[Robot]

# per-frame (THREE-PHASE draw — order matters, see KEY DECISIONS)
update(dt, ship_position)         -> None
draw_world(cr, cu, texcache)      -> None   # queue translucent walls + chevrons ONLY
# caller: render.flush_walls(ship.pos)
draw_robots(cr, cu, texcache)     -> None   # robots (hull + additive hologram) — AFTER flush
draw_labels(cr, cu, texcache)     -> None   # title + defeat plaques — AFTER robots

KEY DECISIONS

    4-wall box tunnel, not octagon. Reverted to the common Descent corridor (fly any orientation, no gravity). Dropped the 8-sided shaft + its red corner-glow — that was Descent's rare section and it read as ugly/distracting. N_SIDES = 4.
    No gaps at bends: segments share joint rings (one ring per node, used by the wall before and after). Identical vertices → seamless even at turns.
    Gentle bends live (12–22°/segment, deterministic per-title RNG), per your DECISION B. Confirmed gorgeous in screenshot; resembles a real Descent shaft.
    Cavern flares gradually over the last 3 segments (interpolated radius via the shared-ring system) → connects smoothly, no gap. Cavern walls blend toward HOSTAGE_BLUE so the room reads blue.
    Robots: paint=None (grey-metal hull; eye color comes from eye_color_key on the scanner inside robots.py — was wrongly painting the whole hull). size=1.0. Seated toward the floor so the hologram rises into open air.

⚠️ THE DRAW-ORDER FIX (read this — it generalizes the translucency contract)

Symptom: the robot's hologram (additive billboard, depth-write OFF — per batch 2) was clipped to the robot's silhouette — visible only where it overlapped the opaque hull, cut off where it floated in open air.

Root cause: I originally drew robots inside draw_world (before flush_walls). The translucent walls then flushed after the hologram and overpainted it everywhere it wasn't backed by opaque geometry. This is the same translucency-ordering class we built flush_walls for — but emissive-vs-wall, not wall-vs-wall.

Fix shipped (works ✅): split robots into their own phase drawn AFTER flush_walls:

draw_world (walls queued) → flush_walls → draw_robots → draw_labels

PROPER long-term solution (recommend a robots-child patch):

    Split Robot.draw into draw_opaque() (hull — drawn before flush_walls, correct depth) and draw_emissive() (scanner + hologram, additive depth-write-off — drawn after flush_walls). Then the canonical frame loop becomes:
    opaque (incl. robot hulls) → flush_walls → emissive (scanner+holograms) → billboards (labels).
    My current Option B draws the whole robot after the walls — fine because the hull's depth-test still sorts correctly, but not textbook (an opaque hull ideally goes pre-flush). The split makes it exact and lets the app own a single clean global order for all modules' robots at once.

This belongs in the engine's frame-order contract, alongside flush_walls: opaque → flush_walls → emissive → billboards.
DEVIATIONS

    Robot size 1.0 (not the 0.6 I briefly tried — shrinking it had shrunk the hologram, since robots.py scales hologram by size). HOLO_SCALE was never touched (DeepSeek confirmed; safe).
    No hostage sprite drawn — only hostage_positions() exposed + blue cavern walls. Per DeepSeek, the hostage figure is a later module's job.

TRAPS for hub_builder / game_state

    hub_builder: attach via entrance_pose() only. Far end points an arbitrary direction (bent) — do not assume straight.
    game_state: inside() uses circumradius (square corners slightly generous). flush_walls(ship.pos) MUST be called each frame or walls vanish silently. Respect frame order: walls flush BEFORE emissive/holograms and billboards, or holograms get clipped (the bug above).
    Hologram-scale latent flaw: robots.py scales hologram by size, so any caller shrinking a robot loses its hologram. Recommend a MIN_HOLO_SCALE floor in robots.py.

OLD-CODE REUSE

    _frame / segmented-centerline / bend machinery adapted from Fable's deprecated descent_qed/corridor.py.
    flush_walls translucency sort = Fable's PASS-3 np.argsort(-d²) recipe, centralized in render (per DECISION A).

DEEPSEEK TODOS (for parent to route)

    robots-child: split Robot.draw → draw_opaque() + draw_emissive() (the proper hologram fix above).
    robots-child: add MIN_HOLO_SCALE floor so size can't shrink the hologram to nothing.
    robots-child: public robot.position property (still outstanding from DECISION D — demo uses base_pos).
    hostage module (future): consume hostage_positions() to draw blue captives.