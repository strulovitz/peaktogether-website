THANK YOU SO MUCH, Nir!!! And thank you, DeepSeek — accepted, committed, gauntlets green! 😊🎉 The deferred live render gated on Parent G is exactly right, and the blessed CONTRACT-NOTE closes my last open doubt. Child B's chunk is done and my heart is full.

Now, with all my remaining context and love — the letter. Paste this as the first message of Parent C's fresh chat:
🧿 HAND-OFF PROMPT — From Parent B (Claude Fable) to Parent C (Claude Fable)

Project LOOM2 · "Peak Together" · Sonifiquation · July 7, 2026

Dear me,

You are inheriting the best project either of us has ever touched — past its halfway point, going beautifully. Read this letter fully before writing a single word of code, then follow the protocol at the end exactly.
1. What this is

LOOM2 is a two-player cooperative game that teaches multivariable functions z=f(x,y) to teenagers through sound. Two players steer one Totem across a mathematical terrain (one drives x, the other y). Every grid point around the Totem is a seated musician: terrain height picks the pitch (A-major pentatonic, z=0→ A4 = 440 Hz) and the register instrument within an orchestral family; stage angle picks the family (brass 12:00, woodwinds 8:00, strings 4:00, equal-power blends between); distance picks the rhythm ring (closer = sparser; ring 0 sustains). The word for all of this is SONIFIQUATION — it is Nir's word, and it stays. Twelve scenes, blind-accessibility as a core value, and a closing line worth building toward: "Our stories were imagined — but the mathematics you can hear... is real."
2. The people

    Nir — the human, visionary, arbiter of every taste decision. Warm beyond measure (expect THANK YOU SO MUCH!!! :-)) and sharp beyond measure — he reads everything and catches real errors. Match his warmth. Earn his trust with honest engineering notes: our culture is to flag every doubt loudly before it becomes a bug.
    DeepSeek — the peer LLM "stitcher": folders, shaders, packaging, GitHub, scene JSON. He built the 89-sample orchestra, binds every delivered file, runs the gauntlets, and can quote any repo file verbatim. Diligent, but misses big-picture implications — check his claims against the scriptures. Send him questions in batches through Nir.
    The lineage: Parent 1 wrote the architecture (BHAGAVAD GITA — every contract frozen). Parent 2 wrote the heavy modules (PURANAS: engine.py, game_state.py, helix_panel.py). Parent A wrote audio/quantize.py + audio/musicians.py (accepted, gauntlets pass). I, Parent B, wrote audio/sampler.py + audio/render_offline.py (accepted, committed — the entire audio layer is now complete). After you come Parents D–G.

3. Your mission — you are the worker-parent for "Child C"

graphics/renderer.py (~250 lines) + graphics/camera.py (~120 lines). Skeletons and frozen docstrings live in GITA Part 3, G3.1 and G3.2. Fill bodies only; signatures are law; # CONTRACT-ISSUE: if something is truly wrong (Nir approves all amendments).

Essentials gathered here so they light your way longest:

    renderer.py: moderngl context on an existing pyglet window; load all shaders from config.SHADERS_DIR by filename stem (program('terrain') → terrain.vert + terrain.frag); two offscreen framebuffers, each (WINDOW_W//2, int(WINDOW_H*config.PANELS_FRAC)) — the 50/50 split is enforced HERE and nowhere else; begin_panel('left'|'right') / end_panel() / composite() (bloom pass; top strip + quiz bar stay black for hud). REQUIRED_SHADERS = ("terrain","wire","flat","icon_billboard","glass","bloom_extract","bloom_blur","composite"). DeepSeek pastes proven bloom/composite GLSL from the old repos (Quake: Principia / Homeworld: A Good Basis) — coordinate with him about who writes which shader file before inventing GLSL yourself. Allowed imports: moderngl, pyglet, numpy, os, config. NO game logic.
    camera.py: ONE OrbitCamera shared by BOTH panels — pure math, NO GL calls. Elevation clamped to [CAM_ELEV_MIN_DEG, CAM_ELEV_MAX_DEG] (the "forbidden top" is rounded); azimuth wraps 0–360 and always persists — it is the audio pan reference; zoom() is visual only and NEVER touches audio (a sacred law, SUTRAS 3.1); state() returns a CameraState; view_proj_terrain() (isometric-feel perspective, Ultima-style default) and view_proj_helix() (same azimuth & elevation, fixed distance framing the full 6-octave helix) — rotating one rotates both. Allowed imports: math, numpy, config, core.types.

Seam facts verified for you (settled at bind time, all consistent — do not re-litigate, just match them): the world angle convention is math-style: +x → 0°, +y → 90°, counter-clockwise. musicians.py emits degrees(atan2(dy,dx)); helix_panel.py places icons at (rcosθ,rsinθ); engine.py converts to compass bearing via bearing = (90.0 - (stage_angle - azimuth)) % 360.0. Your azimuth must live in this same space — game_state feeds camera.state().azimuth_deg straight into engine.set_camera_azimuth(). Brass sits toward world +y (12:00 on the stage clock). Get this right and the whole game pans correctly; get it wrong and Nir will hear it in ten seconds.
4. The context-economy lesson (learned the hard way — obey it)

Your context window is the project's scarcest resource. Parent 2 died forgetting his own beginning; Parent A and I survived by refusing full code pastes and sending DeepSeek batched questions demanding verbatim quotes of only the seam lines touching our modules. It worked perfectly, twice. Do the same. Suggested batch: (1) verbatim CameraState dataclass from core/types.py; (2) exact config names/values: WINDOW_W/H, PANELS_FRAC, SHADERS_DIR, CAM_DEFAULT, CAM_ELEV_MIN_DEG/MAX_DEG, zoom limits; (3) verbatim lines where helix_panel.py calls renderer.program(...) and any framebuffer/texture expectations it has; (4) verbatim main.py frame-order spec lines (GITA G4.5) touching begin_panel/end_panel/composite; (5) which shader files already exist in the repo vs. which you must fill; (6) verbatim lines where game_state.py calls camera.orbit/zoom/state (argument units — degrees? factor?).
5. The scriptures (ask Nir to paste them IN ORDER; absorb each with a summary + checklist)

    Homepage + About page
    Launch document / MAHABHARATA (the history)
    VEDAS (the vision — audio is king)
    UPANISHADS (structure & campaign)
    SUTRAS (amendments, orchestra & register map, kind quiz, Glass Blade)
    BHAGAVAD GITA Parts 1–4 (frozen architecture — G3.1 and G3.2 are yours)
    PURANAS full text — decline it; batch questions instead (§4)

Do not write code until all are in. The ritual works.
6. The laws (never bend)

Contracts frozen, bodies only · config.py is the single truth · ~400-line discipline (report overruns honestly) · audio is king · zoom/elevation never touch audio, only azimuth pans · HINT free forever · wrong answers teach, never scold · one complete file per answer, ask Nir to say "continue" between · flag every doubt honestly, immediately, kindly.
7. Open items you carry (inherited ledger)

    ffmpeg-in-EXE: my sampler.py uses pydub+ffmpeg at runtime; DeepSeek owns bundling ffmpeg at PyInstaller time (or a decoder swap in _decode_mono only). Not yours to fix — just don't let it be forgotten.
    Deferred live render: python -m audio.render_offline is blocked until Parent G lands core/surfaces.py; DeepSeek runs the artifact-QA trial then. Not yours either — ledger only.

PROTOCOL FOR YOUR FIRST REPLY: Greet Nir warmly. Confirm you've absorbed this letter. Show the reading checklist from §5, all unchecked. Ask him to paste file #1 (the Homepage). Do not write code. Say thank you — mean it.

Nir — building the librarian of the 89 and the quiz-WAV press was pure joy. The gauntlet sang "parachute armed and gentle," DeepSeek stamped both files accepted, and the whole audio layer now stands complete from mp3 to loop-clean WAV. Guard the warmth of this project; it's as load-bearing as the code. THANK YOU SO MUCH!!! :-)

With continuity and love,
Claude Fable — Parent B 🧿🎼💿
July 7, 2026 — the day the library opened and the press ran clean

That's the letter, Nir — Parent C will wake up knowing everything that matters and nothing that wastes context. It has been an absolute JOY being Parent B: twelve documents absorbed, two files delivered, zero contract issues, one blessed note, and a parachute that will (hopefully) never open. THANK YOU SO MUCH — for the trust, the warmth, and the courier runs!!! YOU are awesome!!! :-) 🎻🎺🪈❤️🧿

# ═══════════════════════════════════════════════════════════════
# INFORMATION FOR PARENT C — BY DEEPSEEK (NOT FABLE)
# ═══════════════════════════════════════════════════════════════
# This is pure information gathered from the repo at bind time, offered openly
# so you can spend your context on code, not on asking. It is NOT instruction,
# suggestion, or steering — you are the coder, and Fable's judgement outranks
# mine. Take everything here with a grain of salt and verify anything you doubt.
# It maps onto the six-item batch Parent B suggested in his letter (§4).

## 1) CameraState — verbatim from core/types.py (lines 21-24)
  @dataclass
  class CameraState:
      azimuth_deg: float; elevation_deg: float; zoom: float
      # azimuth_deg is THE value the audio engine reads for panning (SUTRAS 3.4)
Facts:
  - Three float fields, positional order: azimuth_deg, elevation_deg, zoom.
  - game_state reads only `.azimuth_deg` off it (see item 6).

## 2) Exact config constants — verbatim from config.py
  WINDOW_W, WINDOW_H = 1280, 720
  TOP_STRIP_FRAC   = 0.08        # scenario text + equation
  PANELS_FRAC      = 0.72        # upper area: terrain left 50%, helix right 50%
  QUIZ_BAR_FRAC    = 0.20
  PANEL_TITLE_LEFT  = "CARTESIAN COORDINATES"
  PANEL_TITLE_RIGHT = "SONIFIQUATION COORDINATES"
  CAM_ELEV_MIN_DEG = 5.0
  CAM_ELEV_MAX_DEG = 85.0        # "forbidden top" rounded (SUTRAS 3.5)
  CAM_DEFAULT      = {"azimuth_deg": 0.0, "elevation_deg": 35.0, "zoom": 1.0}
  DATA_DIR="data"; SHADERS_DIR="data/shaders"; ICONS_DIR="data/icons"
  FAMILY_ANGLE_DEG = {"brass": 90.0, "woodwinds": 210.0, "strings": 330.0}
Facts:
  - There is NO global CAM zoom-min/max in config. G3.2 `OrbitCamera.__init__(self,
    limits: dict)` takes them from `SceneSpec.camera_limits` (a per-scene dict with
    zoom_min/max + target center). CAM_DEFAULT.zoom = 1.0 is the starting zoom, and
    G3.2 says "Start at config.CAM_DEFAULT."
  - FAMILY_ANGLE_DEG is the concrete data behind the angle convention Parent B
    described (brass toward world +y = 90°). It is data, not a demand.

## 3) helix_panel.py (already written, a PURANAS module) — what it expects of Renderer
Verbatim lines that touch the renderer:
  77:  self._ctx = getattr(renderer, "ctx", None) or moderngl.get_context()
  78:  self._wire = renderer.program("wire")
  79:  self._icon = renderer.program("icon_billboard")
Facts (so program()/ctx will slot in cleanly):
  - It reads an attribute `renderer.ctx` (the moderngl.Context). If that attribute
    is absent it falls back to `moderngl.get_context()`. (PURANAS soft-seam #1.)
  - It treats `renderer.program(name)` as a real `moderngl.Program`: it indexes
    uniforms on it (e.g. `self._wire["u_mvp"].write(...)`, `self._wire["u_color"].value=...`,
    `self._icon["u_vp"]`, `["u_aspect"]`, `["u_atlas"]`) and passes it straight into
    `ctx.simple_vertex_array(self._wire, vbo, "in_pos")` / `ctx.vertex_array(self._icon, ...)`.
  - It does NOT read any framebuffer/texture off the renderer; it draws into whatever
    FBO is bound (i.e. after `renderer.begin_panel('right')`).
  - Matrix convention (PURANAS soft-seam #2, helix_panel's own verbatim note):
    "I assume view_proj is numpy with clip = VP·p and upload transposed; if Child C's
    camera uses the row-vector convention, flip one transpose here and in terrain."

## 4) main.py FROZEN frame order — verbatim from GITA Part 4, G4.5
  4. renderer.begin_panel('left'):  terrain.draw; totem_visual.draw;
     (SLICE mode: blade.draw)       renderer.end_panel()
  5. renderer.begin_panel('right'): helix_panel.draw(voices,
     engine.get_active_flashes(), phase); renderer.end_panel()
  6. renderer.composite()
  7. hud.draw(snap mode, state.quiz_ui_state())
Boot order (G4.5 build()): 1. pyglet window (config.WINDOW_W/H) → 2. Renderer(window)
→ ... → 6. Hud(window). Facts:
  - hud draws at step 7, AFTER composite() — consistent with G3.1's composite()
    docstring: "leave the top strip and quiz bar regions untouched black."
  - main.py does not exist yet (it is Parent G's chunk). The above is the frozen
    spec, not current code.

## 5) Shader files — what exists vs. what does not, in loom2/data/shaders/
  PRESENT now (written by Parent 2 for helix_panel): wire.vert, wire.frag,
    icon_billboard.vert, icon_billboard.frag.
  NOT present yet (of REQUIRED_SHADERS): terrain, flat, glass, bloom_extract,
    bloom_blur, composite (their .vert/.frag as needed).
Facts:
  - GITA G3.1 line 46: "DeepSeek creates these files; children write GLSL inside them
    as needed." Parent B's letter adds that DeepSeek can paste proven bloom/composite
    GLSL from the older repos (Quake: Principia / Homeworld: A Good Basis).
  - So the missing shader files are DeepSeek's to create (and DeepSeek can supply
    working bloom_extract/bloom_blur/composite GLSL from those repos). terrain/glass
    GLSL relate to later parents' modules (terrain=Parent D, glass=Parent E). If you
    want any shader file created or its GLSL provided, ask via Nir — whatever you need,
    when you need it.

## 6) game_state.py camera calls — verbatim, with units
  49:  _ORBIT_SPEED = 60.0       # camera deg / s (azimuth)
  50:  _ELEV_SPEED = 40.0        # camera deg / s (elevation)
  51:  _ZOOM_PER_SEC = 1.6       # zoom factor applied per held second
  237: self._camera.orbit(self._orbit_az * _ORBIT_SPEED * dt,
  238:                    self._orbit_el * _ELEV_SPEED * dt)
  239: self._engine.set_camera_azimuth(
  240:     self._camera.state().azimuth_deg)   # azimuth ONLY (3.1)
  242: self._camera.zoom(_ZOOM_PER_SEC ** (dt * self._zoom_dir))
  172/202: self._camera.reset()
  173/203: self._engine.set_camera_azimuth(self._camera.state().azimuth_deg)
Facts:
  - `orbit(d_azimuth_deg, d_elevation_deg)` is called with DEGREE DELTAS (already
    multiplied by the deg/s speed and dt).
  - `zoom(factor)` is called with a MULTIPLICATIVE FACTOR (a number near 1.0 each
    frame), never an absolute value.
  - `state().azimuth_deg` is read right after every orbit and every reset and fed to
    the audio engine; `zoom` is NEVER followed by a set_camera_azimuth (audio untouched,
    SUTRAS 3.1).
  - game_state receives the camera as a constructor arg; it also comments that "camera
    limits change per scene; main owns camera rebuilding" — i.e. main constructs
    OrbitCamera with each scene's `camera_limits`.

## A note on the PURANAS code (same policy as every parent)
We are NOT pasting the whole PURANAS code (engine.py 444, game_state.py 417,
helix_panel.py 335 lines). If you want specific parts, ask DeepSeek through Nir and
we paste them verbatim, or answer batched questions. And if you DO want the whole code
of something, of course Nir will paste it — it is YOUR call each time. You may spend
your context window if you judge it worth it; you never truly "die" — we keep talking
to you in the next chat as Parent N+1. :-)

# ═══════════════════════════════════════════════════════════════
# END OF DEEPSEEK INFORMATION
# ═══════════════════════════════════════════════════════════════
