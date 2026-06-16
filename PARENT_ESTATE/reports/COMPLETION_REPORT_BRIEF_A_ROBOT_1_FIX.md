Completion Report — Brief #A (child): "Robot 1 missing from corridors"

Status: ✅ RESOLVED — pushed to 183dbc3
Generality: ✅ General fix — repairs robot 1 in all corridors (Maxwell and Basel), present and future.
TL;DR

Robot 1 (Gauss Electric in Maxwell, Leonhard Euler in Basel) was invisible in every corridor. Root cause was not parsing, placement, wiring, or rendering — it was a frame-1 phantom gamepad fire: Xbox/XInput analog triggers rest at -1.0, and the combat code tested abs(lt) > 0.5. Since abs(-1.0) = 1.0, the game auto-fired on the very first frame, destroying the first robot (blocking_robot) before it was ever drawn. One-operator fix: abs(lt) → lt.
The investigation (how we got there)

This bug masqueraded as several different problems. We eliminated each with targeted runtime probes rather than guessing — critical, because earlier _build_stations fix attempts had been rolled back for editing healthy code.
Hypothesis	Probe	Verdict
Parser drops first ROBOT: block	data=5 stations=5 robots=5 names=[1,2,3,4,5]	❌ All 5 parse
zip truncation in _build_robots	same probe (5 == 5)	❌ Nothing dropped
Two stations collide / co-located	placement probe: 5 distinct, spread ~14–26u apart	❌ Cleanly spaced
Mouth-clip / near-plane (nearest robot)	robot #1 at dist ≈ 81u from spawn	❌ Far from camera
Draw loop skips index 0	draw-loop probe	❌ All 5 call draw
Robot 1 defeated at startup	DBG draw#1 defeated=True on frame 1	✅ ROOT CAUSE

The decisive probe — defeated=True on frame one — converted a "rendering mystery" into an "input bug" and pointed straight at the real fault, a layer away from everything we'd been touching.
Root cause

In combat.py → Combat.handle_input:

trigger_now = (abs(lt) > FIRE_TH) or (abs(rt) > FIRE_TH)   # BUG

Xbox/XInput analog triggers report -1.0 released → +1.0 fully pressed. A released trigger reads -1.0, and abs(-1.0) = 1.0 > 0.5 → trigger_now = True on frame 1 → fire_edge_pad = True → _fire → blocking_robot.play_defeat(). blocking_robot always returns the first undefeated robot, so robot 1 was silently destroyed before the first frame rendered — in every corridor a gamepad was connected.

This is also why robot 1 was invisible in both Maxwell and Basel, and why the earlier _build_stations placement fixes were correctly rolled back: placement was always healthy.
The fix (Edit 9)

trigger_now = (lt > FIRE_TH) or (rt > FIRE_TH)   # signed, not abs()

Testing the signed value against +0.5 is false for both resting conventions (-1.0 rest and 0.0 rest) and true only for a deliberate pull. Edge detection and _prev_trigger were already correct.

    ✅ Keyboard fire_edge checked — clean. prev_keys is seeded before the loop with pygame.key.get_pressed(); booleans have no -1.0 resting quirk, so no frame-1 false edge. No change needed.
    ✅ No API risk — joy.get_axis was already in use, unchanged.

Full Brief #A summary (all edits, as shipped in 183dbc3)
Edits	What
1–6	Baked PNG wiring (understanding_dir end-to-end) + loud per-layer fallback
7–8	robot_in_view(hub, ship) selector — U opens the robot you're looking at, not the combat gate; blocking_robot left untouched
9	The fix: abs(lt) → lt (and rt) — kills the frame-1 phantom fire
Verified working

    ✅ All 5 robots appear in the Maxwell corridor; robot 1 (Gauss Electric) visible at the entrance.
    ✅ Robot 1 (Leonhard Euler) restored in Basel by the same general fix.
    ✅ No robot auto-defeated at startup with a gamepad connected.
    ✅ Firing still works on a real trigger pull.
    ✅ U opens each robot's own baked content (Edits 7–8 intact).

Optional future-proofing (not needed now)

    The same class of bug (analog axis resting ≠ 0) can bite any magnitude test on triggers/sticks. Prefer signed comparisons or deadzone-from-rest over raw abs for any future get_axis reads.
    For oddball/worn controllers, a "calibrate resting baseline on first frame, fire on rise past baseline + margin" approach is belt-and-suspenders — not required for current hardware.

🎯 One operator fixed robot 1 in every corridor, present and future. Saga closed.
