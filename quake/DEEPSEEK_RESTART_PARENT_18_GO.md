🌙 DEEPSEEK RESTART HANDOFF — PARENT 18 LAUNCH — July 1, 2026 (late night)

## ⚠️ ON RESTART: READ THIS FIRST, THEN WORKFLOW, THEN COMMENTARIES ⚠️

---

## 🏆 WHERE WE ARE

**446/446 tests green 🟢**

**Build pipeline: COMPLETE.** All 20 Principia rooms have baked runtimes, PNG assets, manifest. The entire `levels/principia_bk1_inverse_square/pack/` directory is fully populated.

**Parent 17: DONE.** Best-fit-decreasing wall packer integrated. 20/20 room runtimes build.

**Game startup: WORKS.** `new_state()` starts in room mode (first room = "law_1" lexicographically). Savegame auto-upgrade handles old corridor saves.

**Door exit: PLACEHOLDER.** When you walk through a door, the game switches to "corridor" mode and shows a filtered 2-room wireframe (the ugly map, but only 2 nodes). This is NOT a real corridor — it's the same `render_mode_a()` wireframe renderer with a minimal floorplan. Nir called this "lying" and is correct.

---

## 🔴 THE CRITICAL PROBLEM

**There are NO real 3D corridors between rooms.** Zero. The codebase has:

- `render_wire.py` — renders flat 2D wireframe on the XZ plane (what Nir calls the "ugly map")
- `render_room.py` — renders solid rooms (walls, panels, ceiling equations)
- `nav_collision.py` — `_CorridorNav` navigates the flat wireframe corridors
- Nothing that generates or renders actual 3D tunnel geometry between two 3D door positions

**What Nir wants:**
1. Walk through a room door → enter a real 3D corridor tunnel
2. The corridor has walls, floor, ceiling (solid rendering, not wireframe)
3. Walk through it → emerge at the connected room's door
4. No map. No teleport. No flat wireframe.

---

## 📋 PARENT 18 — OUR ONE JOB ON RESTART

**Launch Parent 18** to design real 3D corridor geometry + rendering + navigation.

The frozen handoff is at:
`quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_18_CORRIDORS.md`

Parent 18 will produce a DESIGN DOCUMENT (not code). DeepSeek implements it.

---

## 🔗 GITHUB URLS FOR COPY-PASTE TO OPUS

Give these to Nir for a FRESH Opus 4.8 chat:

1. **The Commentaries** (project map):
   `https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md`

2. **Old Testament** (Fusion's master doctrine):
   `https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_DOCTRINE_BY_FUSION.md`

3. **New Testament** (Opus's two-legs design):
   `https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_NEW_TESTAMENT_TWO_LEGS_BY_OPUS.md`

4. **Parent 18 handoff** (the mission):
   `https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_18_CORRIDORS.md`

---

## 📋 STEP-BY-STEP ON RESTART

1. Re-read WORKFLOW.md + Commentaries + this handoff
2. Ask Nir: "Ready to launch Parent 18 (real 3D corridors)?"
3. Give Nir the 4 GitHub URLs above for copy-paste
4. Parent 18 will talk first (state understanding, ask questions)
5. When Parent 18 asks for files: fetch them from disk, give to Nir to paste
6. When Parent 18 delivers: save verbatim to `QUAKE_PARENT_18_FROZEN_DELIVERABLE.md`
7. DeepSeek implements per the frozen design
8. Update WORKFLOW + Commentaries + commit push

---

## ⚠️ CRITICAL REMINDERS (from today's disaster)

1. **Never lie about what was built.** If the corridor is really filtered wireframe, say so.
2. **Test with the game, not just pytest.** pytest only tests pure logic.
3. **Delete the savegame when changing startup behavior.** `Remove-Item savegame.json`
4. **Nir's instructions from today's session:**
   - "make the big program work" = app.py should run and play
   - "i do not want to start in your ugly map" = start in room (DONE)
   - "when i exit a room, i do not want to get into your ugly map" = real corridors (Parent 18)
   - "i want corridors asshole" = 3D solid tunnels, NOT wireframe map subset
   - "what is this lines and circles?" = the flat 2D map (Parent 19 will fix this)

---

## 🛠️ QUICK COMMANDS

```powershell
# Run the game (from quake directory)
cd C:\Users\nir_s\peaktogether-website\quake
python app.py

# Run tests
python -m pytest quake/tests -q

# Delete stale savegame
Remove-Item savegame.json -ErrorAction SilentlyContinue

# View a room
python -m tools.room_viewer lemma_2 "levels/principia_bk1_inverse_square/pack"
```

---

## 📊 CURRENT FILE STATE

### Modified but NOT committed (build artifacts):
- `quake/build/build_all.py` — removed explicit panel size overrides (uses defaults)
- `quake/build/room_maker.py` — removed `text_px_per_m` (uses `room_px_per_m`)
- `quake/map/raw_models.py` — removed `text_px_per_m` field, lowered `panel_max_w_m` (3.2) and `panel_max_h_m` (2.4)
- `quake/levels/.../pack/room_runtime/*.json` — all 20 regenerated
- `quake/levels/.../pack/_bake/*.pdf` — all regenerated
- `quake/savegame.json` — stale corridor save (DELETE THIS)

### Key source files (committed):
- `quake/app.py` — single_corridor_floorplan, travel_edge_id, savegame fix, room nav pre-build
- `quake/gameplay.py` — door exit → corridor mode, direction fix, atan2 import
- `quake/state.py` — starts in room mode with first door spawn
- `quake/tests/test_gameplay.py` — test_modeswitch_out_of_room updated
- `quake/tests/test_state.py` — test_new_state_starts_in_room updated

---

*Written by DeepSeek after a very bad session. Parent 18 is the real fix. Let's do this right.* 🔧💖
