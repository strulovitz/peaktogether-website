Completion Report (draft — finalized after the 5 confirms)

    FILES: corridor_builder.py, corridor_demo.py
    entrance_pose() → ((x,y,z), (nx,ny,nz)) mouth center + outward normal (points back toward hub).
    inside(point, margin=0.0) → bool — per-segment octagonal-slab union; straight or bent.
    seg_bounds (public list) — each: {"start","end","right","up","radius"} (lists/float).
    hostage_positions() → list[(x,y,z)] cavern floor anchors.
    stations() → list[((x,y,z), yaw)]; get_robots() → list[Robot].
    KEY DECISIONS: bends live (12–22° per seg, deterministic per-title RNG); cavern = last 2 segments flared to CAVERN_RADIUS; walls enqueued via queue_wall, never sorted locally; mouth normal points to hub.
    TRAPS for hub_builder: attach to entrance_pose() only; far end is arbitrary direction (bent) — do NOT assume the corridor is straight. For game_state: inside() uses circumradius (octagon corners slightly generous); flush_walls MUST be called or walls vanish; defeat plaques use briefing_hint placeholder until reading_system lands.
    OLD-CODE REUSE: _frame/segment/ELBOW seam-overlap adapted from Fable's descent_qed/corridor.py.

Once DeepSeek confirms the 5 TODOs, I'll patch, then we iterate TUBE_RADIUS/turn angles/chevrons/plaque size by screenshot. Ready.