MODULE COMPLETION REPORT — robots

Author: Claude Opus 4.8
Status: ✅ Complete, demo-proven, ready for integration
Files delivered: robots.py, robots_demo.py
1. What this module is

A Robot is a hovering guardian machine (never humanoid — no head/face/arms/legs). It renders a faceted grey-metal hull with a Larson-scanner "eye," a floating hologram portrait, and a defeat explosion. The engine stays mathematics-blind: this module interprets nothing and assigns no color by meaning.
	
	
	
	
	
	
	
2. The data path (the contract that matters)

The module reads only two fields from robot_data:
Field read	Used for
robot_data.name	Hologram portrait filename + text fallback
robot_data.eye_color_key	palette.eye(key) → scanner color (MEANING)

    All meaning-color flows through palette.eye(key). Hull grey, visor black, and explosion fire are decoration, chosen locally, never meaning. The scanner color is the only meaning-bearing color, and it comes entirely from the ledger.

3. Public interface (final, frozen)

Robot(robot_data, palette, station_pose, paint=None, size=1.0)
update(dt, ship_position)
draw(camera_right, camera_up, texcache)
play_defeat()
is_defeated() -> bool

    The camera is received as camera_right / camera_up; a robot never owns or queries the camera.
    station_pose accepts either (x,y,z) or ((x,y,z), base_yaw_radians).
    A make_robot(...) factory mirrors the constructor for cleaner call sites.

4. Confirmed decisions (resolved during build)
#	Question	Resolution
1	Does palette.ROBOT_HULL / ROBOT_* exist?	No (DeepSeek confirmed). Hull uses a local default grey-metal (decoration).
2	Spin vs. yaw-toward-player?	Option C (Nir): random start → slow face/track + idle drift. Keeps the 3D feel.
3	Eye style?	Larson scanner (Cylon / KITT), per Nir — sweeping dot + comet-tail on the front face.
4	Visor slot color?	Near-black housing (decoration), confirmed by Nir.
5	Hologram = "later"?	No. Built now, in-module. Real PNG loader added (load_portrait).
6	Portrait blend?	Portraits are glowing-blue figures on solid black → additive blend (black vanishes), no tint (already blue).
7	Explosion too wimpy?	Rebuilt as a multi-burst explosion with random fire circles, flash, and sparks.
5. Asset & naming conventions (for the art pipeline)

    Hologram portraits: <Name_with_underscores>-hologram.png, e.g. Brook_Taylor-hologram.png, Leonhard_Euler-hologram.png.
    Format: 512×512 PNG, glowing-blue figure on solid black background.
    Location: searched in the run folder first, then next to robots.py.
    Missing file → automatic text-placeholder fallback (no crash), with a DEBUG: print naming the file it looked for.

6. Where other modules' code lives (FYI to the parent)

Fable's earlier prototype contained logic that is out of scope for robots and was deliberately not copied here — but it exists and may be useful elsewhere:

    find_lock, blocked, _brackets (targeting/lock reticle) → weapons
    neutralize hit-logic → weapons / game_state
    ROBOT_SLOTS / corridor import / module-level ROBOTS list → corridor_builder / game_state

7. Open hooks left for other modules (named, not dangling)

8. Tuning (for DeepSeek, after Nir's flight)

Every behavior is a named constant at the top of robots.py — no magic numbers buried in logic. Adjust only after flight-test.
Area	Key constants
Hover / motion	BOB_AMPLITUDE, BOB_SPEED, YAW_SPEED, IDLE_DRIFT_AMP/SPD
Scanner	SCAN_SPEED, SCAN_SEGMENTS, SCAN_TAIL, SCAN_CORE_BOOST
Hologram	HOLO_HEIGHT_ABOVE, HOLO_SCALE, HOLO_PORTRAIT_ALPHA, HOLO_BOB_*
Explosion	EXPLO_DURATION, EXPLO_NUM_FIRE, EXPLO_SIZE_MIN/MAX, EXPLO_NUM_SPARKS, EXPLO_SPARK_*
9. Integration note (one likely first-run snag)

The demo assumes these content_parser field names: corridor.ledger, corridor.robots, robot_data.name, robot_data.eye_color_key. If any differ, only robots_demo.py needs a one-line fix — robots.py itself is insulated via getattr defaults.
10. Credits

    Fable — per-facet flat shading idea (_shade) and the corridor-sealing size insight, both adopted.
    DeepSeek — confirmed the palette had no ROBOT_* constants; flagged the wimpy explosion.
    Nir — every design call that made this good: the Larson scanner, Option C motion, the insistence that the hologram ship now (not "later"), and the random expanding fire circles. 🙂