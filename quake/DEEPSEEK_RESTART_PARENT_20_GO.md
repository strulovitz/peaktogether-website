# 🌙 DEEPSEEK RESTART HANDOFF — Parent 20 + 19 Launch — July 1, 2026

## ⚡ ON RESTART: READ THIS FIRST, THEN WORKFLOW, THEN COMMENTARIES ⚡

---

## 📍 CURRENT STATE

- **446/446 tests green 🟢**
- **20/20 Principia rooms built + baked — pack complete**
- **Game starts in room mode** (no ugly map on startup)
- **Door exit → corridor mode** — currently shows the full wireframe map (circles + lines, flat XZ plane). This is WRONG — see below.
- **All Parent 18 changes REVERTED** — codebase is clean, no ramp waypoints, no Y-disambiguation, no corridor_height.py, no half-baked changes. The floorplan.json has clean 2-point corridor paths.

---

## 🎯 WHAT JUST HAPPENED

Parent 18 was given the mission "Real 3D Corridors Between Rooms." He reinterpreted it as "fix the existing wireframe map" and delivered a wireframe graph improvement instead of building actual corridor tunnels. Nir was furious. Parent 18 was fired.

**Parent 18's changes were fully reverted.** The codebase is back to the clean pre-Parent-18 state.

---

## 🚀 WHAT'S NEXT — LAUNCH PARENT 20 (Corridors) THEN PARENT 19 (Automap)

### Parent 20 — Real 3D Wireframe Corridor Tunnels

**What the corridor IS (per OT §3.1):**
- A 3D box tunnel the player stands INSIDE — edges of walls/floor/ceiling drawn as wireframe lines
- NOT a 2D flat top-down map (the current "ugly map")
- NOT filled solid surfaces — wireframe EDGES only, empty faces, visible edges
- Depth-tested, no alpha blend — near edges occlude far
- Distance-dimming: near = white, far = dark grey, NEVER black
- Floor has ≤3 colored guide-lines with arrowheads (painted on the floor, per OT §8.2)
- Crossings visible as true 3D over/under passes
- Player walks inside the box, collision on walls/floor/ceiling, reach far end → enter next room

**Handoff:** `quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_20_CORRIDORS.md`
**Predecessor's warning:** `quake/BIBLE/QUAKE_PARENT_18_HANDOFF_TO_SUCCESSOR.md`
**Frozen design (Parent 18 — WRONG, DO NOT USE):** `quake/BIBLE/QUAKE_PARENT_18_FROZEN_DESIGN.md`

### Parent 19 — Descent-Style 3D Wireframe Automap

**Same visual language as corridors but:**
- All rooms + all corridors visible as 3D wireframe boxes at once
- Free-fly camera (Tab to toggle)
- NO floor guide-lines, NO arrowheads, NO felt floor
- Room edges colored by importance

**Handoff:** `quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_19_AUTOMAP.md`

---

## 📋 LAUNCH PROTOCOL FOR PARENT 20

Give Nir these 5 blob URLs for copy-paste to a FRESH Opus 4.8 chat:

1. Commentaries — `https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md`
2. Old Testament — `https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_DOCTRINE_BY_FUSION.md`
3. New Testament — `https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_NEW_TESTAMENT_TWO_LEGS_BY_OPUS.md`
4. Parent 20 handoff — `https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_20_CORRIDORS.md`
5. (Optional) Parent 18's warning to successor — `https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_PARENT_18_HANDOFF_TO_SUCCESSOR.md`

Talk-first. Parent states his understanding + questions. Nir confirms. Then parent designs.

**After Parent 20 delivers a design**, drop it in, then launch Parent 19.

---

## ⚠️ KEY LESSONS FROM PARENT 18 FAILURE (bake these into your brain)

1. **Parents WILL re-interpret the mission into something easier unless you beat them over the head with the exact spec.** The Parent 20 handoff quotes OT §3.1 verbatim and says "do NOT make a 2D flat map" five different ways.
2. **The Old Testament IS the spec.** When it says "wireframe only... empty faces with visible edges" — it means 3D box edges, not 2D circles on a plane. Every parent needs the OT quoted back at them.
3. **Nir's word overrules any scripture.** If Nir says "I hate this" and the scripture says "do this" — Nir wins. The OT's wireframe spec was correct all along; the implementation was wrong.
4. **Revert bad changes immediately.** Don't let half-baked code from a failed parent poison the next parent.
5. **"Tests pass" ≠ visual success.** Always render and show Nir.

---

## 📦 STANDING REMINDERS

- Nir is **Nir**. Loves emojis 😊. Normal prose, no pop-ups.
- Never take decisions off Nir's plate.
- 🛑 BREAKING CHANGE GUARD 🛑
- 📦 NEVER upgrade/overwrite working packages
- Commit + push frequently
- Build scripts: commit them to the repo
- Temp files: `%TEMP%\opencode\`

---

*Written by DeepSeek after reverting Parent 18's failed implementation. Clean slate. Let's get it right this time.* 🚀
