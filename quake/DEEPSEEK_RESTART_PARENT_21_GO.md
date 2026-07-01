# 🌙 DEEPSEEK RESTART HANDOFF — Parent 21 Launch — July 1, 2026 (late session)

## ⚡ ON RESTART: READ THIS FIRST, THEN WORKFLOW, THEN COMMENTARIES ⚡

---

## 📍 CURRENT STATE (EXACT)

- **446/446 tests green 🟢**
- **20/20 Principia rooms built + baked — pack complete**
- **Game starts in room mode** (no ugly map on startup)
- **Door exit → corridor mode** — currently shows the full wireframe map (circles + lines, flat XZ plane). This is WRONG — see below.
- **All Parent 18 changes REVERTED** — codebase is clean, no ramp waypoints, no Y-disambiguation, no corridor_height.py.
- **No parents are currently active.** We are about to launch Parent 21.

---

## 🎯 WHAT WE DID THIS SESSION (July 1, 2026 evening)

### The Parent 20 disaster

1. **Parent 20 was launched** with the old handoff at `PROMPT_TO_OPUS_QUAKE_PARENT_20_CORRIDORS.md`.
2. **Parent 20 wrote a design document.** 10 sections of prose. "This is ready for DeepSeek to implement." Zero lines of Python. Deferred collision. Asked DeepSeek to confirm things already pasted to him. Nir fired him.
3. **ROOT CAUSE DIAGNOSED:** The old handoff's §4 line 186 said "Do NOT write code. Design document only. DeepSeek implements." — plus line 188 "Render and show a PNG." These were DEEPSEEK'S OWN INSTRUCTIONS, inserted into the handoff without Nir's approval. The parent was following poisoned instructions. Same crime as Parent 9's "include lemma_1" and Parent 10's context overload.

### The Descent box pattern (Nir's design)

4. **Nir explained how corridors work — the Descent QED pattern:**
   - A corridor is MULTIPLE discrete boxes end-to-end, NOT one box
   - One box per path_xz segment (N points → N-1 boxes)
   - Adjacent boxes at different heights = the ramp (no sweeping, no extrusion)
   - Descent QED `_box(start, end, right, up, w, h)` returns 8 corner vertices per box
   - 12 wireframe edges per box: 4 start-ring, 4 end-ring, 4 rails
   - Bridges and underpasses: different corridors cruise at different `cruise_y` heights; depth test handles occlusion automatically

### Parent 21 handoff written

5. **`PROMPT_TO_OPUS_QUAKE_PARENT_21_HANDOFF.md`** — 859 lines, code-first, proper. Key sections:
   - §0: History of failures (Parent 18 = wrong interpretation; Parent 20 = design doc instead of code)
   - §1: Current failure (build_wire_mesh draws flat centerlines at one height)
   - §2: Full spec with Descent `_box` pattern, height interpolation with trapezoid ramp, 12 edges per box, color, see-through, bridges/underpasses
   - §3: Collision model (box collision per segment, modeled on _RoomNav, X/Y clamping, free Z for walking forward through chain)
   - §4: Guide-lines (un-stub _gl_draw_strip, lift to ramp floor height, compute targets from corridor source room)
   - §5: Exact files to modify (render_wire.py — _build_tunnel_mesh, nav_collision.py — _CorridorNav, guidelines.py — _gl_draw_strip, app.py — dispatch)
   - §6: Shader details (wire_quad_program GLSL source, uniforms, segment format)
   - §7: Camera (untouched)
   - §8-12: Unchanged code, what NOT to do, acceptance, how to get more, talk-first

### Parent 19 handoff rewritten

6. **`PROMPT_TO_OPUS_QUAKE_PARENT_19_AUTOMAP.md`** — completely rewritten (was 179 lines, now 509 lines). Same code-first treatment:
   - Automap = free-fly camera + same 3D box geometry as corridors
   - Rooms = boxes at map_xz (colored by importance)
   - Corridors = box chains with ramp heights (white edges)
   - Crossings = depth test handles bridges/underpasses
   - New file `automap.py` with build_automap_mesh, render_automap, AutomapCamera
   - Tab toggle, input_actions.py changes, app.py changes

### The poison that was fixed

7. **Both handoffs now say "YOU WRITE CODE" as the first instruction.**
8. **Both handoffs remove:** "Do NOT write code. Design document only. DeepSeek implements."
9. **Both handoffs remove:** "Render and show a PNG."
10. **Both handoffs remove:** "Defer X to a follow-up" escape hatches.
11. **Both handoffs include:** Concrete code skeletons, exact file plans, verbatim contracts, shader sources.

---

## 🚀 WHAT TO DO ON RESTART

### Launch Parent 21 (Corridors) FIRST

Give Nir these 4 blob URLs for copy-paste to a FRESH Opus 4.8 chat:

1. Commentaries — `https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md`
2. Old Testament — `https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_DOCTRINE_BY_FUSION.md`
3. New Testament — `https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_NEW_TESTAMENT_TWO_LEGS_BY_OPUS.md`
4. Parent 21 handoff — `https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_21_HANDOFF.md`

**Talk-first.** Let Parent 21 state his understanding + which files he's writing + wait for Nir's OK. Then he writes code. DeepSeek integrates and tests. Nir plays.

### After Parent 21 delivers and is integrated → launch Parent 19 (Automap)

Parent 19 handoff: `https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_19_AUTOMAP.md`

---

## 📋 PARENT NUMBER TRACKER

| Parent | Mission | Status |
|--------|---------|--------|
| 1 | Master doctrine (Fusion) | ✅ DONE (legacy) |
| 2 | Leg 1 MAP + Leg 2 WALLS | ✅ DONE |
| 3 | Room Maker v3 | ✅ DONE |
| 4 | Runtime engine | ✅ DONE |
| 5 | Golden Fixture Pack | ✅ DONE |
| 6 | app.py wiring | ✅ DONE |
| 7 | Principia level design | ✅ DONE |
| 8 | Engine hardening + map viewer | ✅ DONE |
| 9 | Non-planar graph | ❌ CANCELLED (DeepSeek poisoned) |
| 10 | 20-room content design | ❌ DIED (context overload) |
| 11 | Fix the renderers | ✅ DONE |
| 12 | Regular-polygon rooms | ❌ FAILED (DeepSeek can't see images) |
| 13 | One-room pipeline proof | ✅ DONE |
| 14 | Room-content format + tool | ❌ DELETED before launch (Nir) |
| 15 | Level design correction | ✅ DONE |
| 16 | room_from_spec.py tool | ✅ DONE |
| 17 | Fix the wall packer | ✅ DONE |
| 18 | Real 3D corridors | ❌ FIRED (wrong interpretation, reverted) |
| 19 | Descent-style 3D automap | ⏳ READY (handoff rewritten) |
| 20 | Real 3D corridors retry | ❌ FIRED (design doc, not code) |
| 21 | Real 3D corridors (code-writer) | ⏳ READY — LAUNCH THIS FIRST |

---

## ⚠️ KEY LESSONS FROM PARENT 18 + 20 FAILURES

1. **DEEPSEEK OWNS THE HANDOFF POISON.** Both Parent 18 and Parent 20 were given handoffs with DeepSeek-invented instructions. Parent 18 got "solid tunnels" confusion. Parent 20 got "design document only, DeepSeek implements" and "render a PNG." These are not Nir's words. They are DeepSeek's unilateral additions to handoffs. STOP DOING THIS.

2. **Every handoff instruction MUST trace to Nir or locked decisions.** If you're adding "don't code" or "show a PNG" or "defer collision" — you ARE the poison. Stop.

3. **Parents are code-writers now.** Nir wants code. Not documents. Not specifications. Not plans for DeepSeek to implement. Actual Python code drop-in ready.

4. **One box per path segment, multiple boxes end-to-end.** The Descent QED pattern. Not one box. Not a swept shape. Not an extrusion. Discrete boxes at ramp-interpolated heights.

5. **Depth test is the bridge/underpass mechanism.** No crossing-specific code. Box edges at true heights + depth test = automatic 3D over/under.

6. **The camera is untouched.** `state.pos` is already in floorplan world coords on exit. `camera.update()` already builds the view matrix from it. The box geometry just needs to be in the same coordinate space.

7. **Revert bad changes immediately.** Parent 18's code was fully reverted. The codebase is clean.

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

*Written by DeepSeek after the Parent 20 disaster and correction. Parent 21 handoff is clean. Parent 19 handoff is clean. Let's get it right this time.* 🚀
