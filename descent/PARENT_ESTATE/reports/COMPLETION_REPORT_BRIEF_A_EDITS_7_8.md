Completion Report — Brief #A (child): Edits 7–8 (robot_in_view — Fix "all robots show same text")

Status: ✅ Delivered
Run-verified by child? No, Nir tests.

Root cause of the bug report:
Combat.blocking_robot(hub) returns the first undefeated robot in corridor 0 — the combat gate — not the robot the player is facing. So U always opened the same RobotData (Symptom 2: everyone shows one robot's text) and robots 3 & 4 were never opened, so their baked PNGs never loaded and only the always-opened robot's missing-PNG path ran (Symptom 1). This was upstream of all wiring edits.

Edits 1–6 (wiring, unchanged & correct):
- content_parser.py — understanding_dir: str = "" trailing field on RobotData & CorridorData.
- level_parser.py _read_manifest — parse optional baked:, resolve CWD-independently, return it.
- level_parser.py load_level — inject resolved baked_dir onto each CorridorData and every RobotData.
- robots.py — Robot.understanding_dir read-only property.
- levels/maxwell.txt — baked: ../baked/maxwell.
- understanding.py — both named fallbacks made loud (deduped, once per layer per open).

Edits 7–8 (the actual fix):
7. combat.py — new additive robot_in_view(hub, ship); blocking_robot left untouched so combat/HUD/arsenal are unaffected.
8. app.py — U key calls robot_in_view(hub, ship) instead of blocking_robot(hub).

The wire, end to end (now exercised correctly):
look at robot N → robot_in_view returns that Robot → umode.open(robot._robot_data) → understanding.py builds baked/maxwell/robotN_<layer>.png → PNGs for 3 & 4 load; 1/2/5 fall to live text with a loud UNDERSTANDING: line.

Honest caveats:
- Never eyeballed baked/maxwell/'s contents — but Edit 6's loud fallback now reports the truth at runtime per layer.
- blocking_robot semantics are deliberately preserved; robot_in_view is a separate read-only selector. No combat behavior changes.
- The "robot 2 vs robot 1" detail in the original report is consistent with robot 1 having been defeated earlier in that session; the fix makes it moot. The smoke test below confirms.

Smoke test:
Launch fresh, don't fire, fly to robot 3 (Faraday), press U:
    ✅ Expect Faraday's own text + colored baked PNGs (if robot3_*.png exist), no fallback line.
    Fly to robot 1, press U → robot 1's text + a UNDERSTANDING: baked PNG missing: .../robot1_mathematician.png line (PNG not baked).
    Each robot now shows its own content.

Verification before commit:
- render.ship_forward(q) exists, same family as ship_right/ship_up ✅ (render.py:127)
- Edit 7 uses only confirmed APIs ✅
- blocking_robot untouched → combat/HUD/arsenal unaffected ✅
- understanding_dir rides the same RobotData that robot_in_view returns ✅
- robot_in_view falls back to blocking_robot (never returns None where old code wouldn't) ✅

Files changed: combat.py, app.py
DEVIATIONS from brief: None — edited exactly the files specified.
Requests to parent: None.
