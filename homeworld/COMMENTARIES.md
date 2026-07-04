# COMMENTARIES — repository memory. Updated: July 4, 2026 (forge walking skeleton)

Note: "repository" here means the Homeworld game root at `homeworld/` inside the
Peak Together monorepo (github.com/strulovitz/peaktogether-website). Game code
lives under `homeworld/`; the design scriptures live under `homeworld/BIBLE/`;
the Strang book excerpts live under `homeworld/algebra/`.

## FILE INDEX
homeworld/requirements.txt — Python dependencies (numpy, moderngl, pyglet, Pillow) — WORKING
homeworld/run.bat — double-click launcher (runs `python -m forge.demo`) — WORKING
homeworld/settings.json — human-editable config (title, version, size, vsync, bloom, seed) — WORKING
homeworld/forge/__init__.py — forge package exports (Forge, PULSE_DT, Camera, VObjects) — WORKING
homeworld/forge/app.py — Forge class: window, GL context, 10 Hz accumulator loop, additive render — WORKING
homeworld/forge/camera.py — Camera: ORBIT mode + look_at/perspective math (NT 1.3) — WORKING
homeworld/forge/shaders.py — GLSL line-ribbon shader sources (hot core + soft edge) (NT 1.6) — WORKING
homeworld/forge/vobjects.py — primitives: Line, Arrow, DashedLine, Grid, WireSphere (NT 1.4) — WORKING
homeworld/forge/batches.py — CPU segment->camera-facing-ribbon expansion, vectorized numpy (NT 1.5) — WORKING
homeworld/forge/demo.py — forge walking-skeleton acceptance demo (`python -m forge.demo`) — WORKING (awaiting owner's eyes)

## INTERFACES
INTERFACES.md not yet committed as a standalone file. Frozen contracts in force
come from NEW_TESTAMENT.md Part 5 (v1.0). forge implements the subset:
Forge(settings), .window, .camera, .add/.remove, .set_debug_lines (stub until
forge/text.py), .screenshot, .run(tick_cb, frame_cb); Camera .set_orbit,
.orbit_input, .eye, .view, .proj; VObjects Line/Arrow/DashedLine/Grid/WireSphere.
Not yet implemented (later packages): bloom, text/Label, SpannedBox, Ellipsoid,
WireMesh, Trail, ImagePanel, FOLLOW/POV camera modes.

## DEMO STATUS
forge.demo — not yet run on owner's machine — PENDING (owner to install Python +
`pip install -r requirements.txt`, then double-click run.bat).
helm.demo — not built yet.
fleet.demo — not built yet (self-test target: 12/12).
bridge.demo / campaign.demo / intel.demo — not built yet.

## CHANGE LOG (newest first, keep the last ~30 entries)
July 4, 2026 — NT steps 1-2: forge walking skeleton (window, camera, ribbons, grid, first arrow) — by Parent Fable (via DeepSeek)

## PLACEHOLDER LEDGER
(none yet — content/ book-excerpt files not created until the campaign packages begin)
