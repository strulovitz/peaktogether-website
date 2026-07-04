# COMMENTARIES — repository memory. Updated: July 4, 2026 (forge feature-complete)

Note: "repository" here means the Homeworld game root at `homeworld/` inside the
Peak Together monorepo (github.com/strulovitz/peaktogether-website). Game code
lives under `homeworld/`; the design scriptures live under `homeworld/BIBLE/`;
the Strang book excerpts live under `homeworld/algebra/`.

## FILE INDEX
homeworld/requirements.txt — Python dependencies (numpy, moderngl, pyglet, Pillow) — WORKING
homeworld/run.bat — double-click launcher (runs `python -m forge.demo`) — WORKING
homeworld/settings.json — human-editable config (v0.3.0; title, size, vsync, bloom_strength, exposure, seed) — WORKING
homeworld/forge/__init__.py — forge package exports (Forge, PULSE_DT, Camera, full VObject vocabulary) — WORKING
homeworld/forge/app.py — Forge class: window, GL, 10 Hz loop, scene FBO -> panels -> labels -> bloom -> screen overlay (fps, F1) — WORKING
homeworld/forge/camera.py — Camera: ORBIT mode + look_at/perspective math (NT 1.3) — WORKING
homeworld/forge/shaders.py — GLSL: line ribbon + bloom pipeline + textured-quad (text/image) shaders (NT 1.5/1.6/1.7) — WORKING
homeworld/forge/bloom.py — Bloom: 3-FBO classic bloom (RGBA16F scene, downsample, Gaussian, composite + tone map) (NT 1.6) — WORKING
homeworld/forge/text.py — GlyphAtlas + TextRenderer (3D labels + screen overlay) + PanelRenderer (ImagePanels) (NT 1.7) — WORKING
homeworld/forge/vobjects.py — FULL primitives: Line, Arrow, DashedLine, Grid, WireSphere, WireMesh, SpannedBox, Ellipsoid, Trail, Label, ImagePanel (NT 1.4) — WORKING
homeworld/forge/batches.py — CPU segment->camera-facing-ribbon expansion (+ per-segment color for Trail), vectorized numpy (NT 1.5) — WORKING
homeworld/forge/demo.py — FULL forge acceptance demo: trail, floating text, flattening det box, live SVD image panel, ellipsoid, F1 overlay (NT Part 6) — WORKING (awaiting owner's eyes)

## INTERFACES
INTERFACES.md not yet committed as a standalone file. Frozen contracts in force
come from NEW_TESTAMENT.md Part 5 (v1.0). forge is now FEATURE-COMPLETE:
Forge(settings), .window, .camera, .add/.remove, .set_debug_lines (F1 overlay
live), .screenshot, .run(tick_cb, frame_cb); Camera .set_orbit, .orbit_input,
.eye, .view, .proj; the FULL VObject vocabulary (Line, Arrow, DashedLine, Grid,
WireSphere, WireMesh, SpannedBox, Ellipsoid, Trail, Label, ImagePanel); bloom;
glyph-atlas text (3D labels + screen overlay).
Not yet implemented (later packages): FOLLOW/POV camera modes; forge is
otherwise done. Next modules: helm, then fleet.

## DEMO STATUS
forge.demo — not yet confirmed on owner's machine — PENDING (requirements already
installed: numpy 2.4.6, moderngl 5.12.0, pyglet 2.1.14, Pillow 12.2.0; run via
run.bat). Now the FULL acceptance demo (trail, floating text, flattening
determinant box counting to vol 0.00, live SVD image panel rank 1->32, ellipsoid,
fps corner, F1 debug overlay).
helm.demo — not built yet.
fleet.demo — not built yet (self-test target: 12/12).
bridge.demo / campaign.demo / intel.demo — not built yet.

## CHANGE LOG (newest first, keep the last ~30 entries)
July 4, 2026 — NT step 4: text (glyph atlas) + remaining primitives — forge feature-complete — by Parent Fable (via DeepSeek)
July 4, 2026 — NT step 3: bloom (RGBA16F scene FBO, gaussian blur, composite + tone map) — by Parent Fable (via DeepSeek)
July 4, 2026 — NT steps 1-2: forge walking skeleton (window, camera, ribbons, grid, first arrow) — by Parent Fable (via DeepSeek)

## PLACEHOLDER LEDGER
(none yet — content/ book-excerpt files not created until the campaign packages begin)
