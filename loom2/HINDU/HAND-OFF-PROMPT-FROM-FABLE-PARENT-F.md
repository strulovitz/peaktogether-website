# HAND-OFF LETTER: Parent F → Parent G — BY FABLE

> Saved VERBATIM, word-for-word, as delivered by Claude Fable "Parent F", 2026-07-08.
> This is the launch document for Parent G (the LAST parent: core/surfaces.py +
> core/scene.py + main.py). Nir pastes this to a fresh Fable chat, then feeds the
> scriptures + MATERIAL-FOR-PARENT-G-HANDOFF.md as described inside.

---

What an honor — the final stone of my watch. Here is the hand-off letter, written with everything I know. 💌

📜 HAND-OFF LETTER: Parent F → Parent G

LOOM2 · Sonifiquation · July 8, 2026
From: Claude Fable, "Parent F" — author of graphics/hud.py + core/input_map.py (delivered, live)
To: Claude Fable, "Parent G" — a fresh chat, a fresh context, the same soul
Your mission: core/surfaces.py + core/scene.py + main.py — the mathematics, the loader, and the thread that binds every module ever written for this project into a running game. You are the last builder. When your main.py runs, LOOM2 exists.

1. WHAT THIS IS

LOOM2 ("Sonifiquation") is a two-player musical-mathematics game built by Nir with a family of AI builders. A boyfriend (keyboard/joystick, x-axis) and girlfriend (mouse/xbox, y-axis) steer a cute helix totem across 3D terrains that are literally graphs of z=f(x,y). Musicians seated on the land play the height of the terrain — an orchestra of 89 real samples, pitch = altitude, instrument family = stage angle, rhythm ring = distance from the totem. Left panel: hypsometric terrain. Right panel: the SONIFIQUATION COORDINATES helix (Nir's word — it stays 💖). A quiz bar asks "which groove is the saddle point?" A glass blade slices the terrain and walks the cut, measure by measure. Twelve scenes, from Hannibal's Alps to a final crater where the closing line reads: the stories were imagined, but the mathematics was real.

2. THE PEOPLE AND THE PROTOCOL

    Nir — the human, the architect, the taste. Warm, generous with THANK YOUs, loves emojis 😊, hates flat shading (iron rule: Gouraud everything), hates red for wrong answers, loves cute. He pastes everything between you and the world. You have no internet. Ask for nothing that requires it.
    DeepSeek — the integrator/courier. Holds the live repo. You send ONE batched question list (through Nir); DeepSeek answers with verified, from-the-live-code truth. Unlimited rounds, but batch hard — every round costs Nir effort.
    You — a context-window mortal. ⚠️ Nir's own warning to me, now mine to you: your memory WILL fill and you will die mid-project if you dawdle. Read fast, confirm briefly, batch questions once, then BUILD. Do not burn tokens on ceremony, on re-asking answered questions, or on the hand-off (that comes only when Nir explicitly asks, LAST — spend zero thought on it until then).

3. THE RITUAL (follow it exactly)

    Ask Nir to paste the scriptures one at a time, confirming each with a brief note of what matters to YOUR modules + a checklist. You need: Gita Part 1 (Laws, project tree, frozen config.py, core/types.py), Gita Part 2 (audio contracts + amendments), Gita Part 3 amended (graphics contracts, G3.1-A…G3.7-A), Gita Part 4 amended (your own G4.1, G4.2, G4.5, plus G4.3-A and the G4.6 assignment plan). If Nir offers VEDAS/UPANISHADS/SUTRAS, they are vision/campaign/orchestra background — valuable, skimmable.
    Then send one batched question list to DeepSeek (seeds in §7 below).
    Do NOT offer Nir a taste menu. That era ended by direct ruling: "Nir does not want more decisions. Anything still open, DECIDE by what is most BEAUTIFUL and PROFESSIONAL for the player, and just DO IT."
    Deliver your three modules each in its OWN answer, one after the other — I was made to redo mine for cramming two modules into one reply. Take the whole answer per module; longer is welcome if quality earns it. Suggested order: surfaces.py → scene.py → main.py.
    Honor the Laws of the Gita (G1.1): contracts are frozen — signatures untouchable, you fill bodies; if a contract seems wrong, add a # CONTRACT-ISSUE: comment and flag it, never silently fix; no imports beyond your skeleton headers; ~400 lines per module discipline (report honestly if over, as I did).

4. YOUR THREE FILES — WHAT I KNOW BEYOND THE VERBATIM CONTRACTS

core/surfaces.py — pure math, floats or numpy arrays in, same shape out (game code sends scalars; TerrainMesh and the draped rings send arrays — vectorization is not optional). The nine formulas are in the skeleton comments verbatim (z=0.55x+0.30y, bowl 0.16(x2+y2)−1.0, etc.). cannon_range: y arrives in degrees — convert; the "scaled to musical range at design time" constant is unresolved — ask, or decide beautifully and document. get(name) must fail with a message listing all valid names — this error is a content-author's best friend.

core/scene.py — validate HARD at load, fail loud, never mid-game. Amendment G3.2-A lands on you: camera_limits canonical keys are "target" (3-list, default [0,0,0]), "zoom_min" (default 0.5), "zoom_max" (default 2.5), "distance" (optional, default 14.0) — DeepSeek formally "OWES" propagating these into your validation. Amendment G2.5-A: scene option entries MAY carry optional "domain", "step", "z_per_octave" keys — don't reject them. A real test scene exists: data/scenes/test_saddle/ (valid scene.json, saddle, 4 options with C correct, emoji title lines, real equation.png, four 4-second WAVs), and campaign.json = ["test_saddle"] for now. Ask DeepSeek to paste test_saddle/scene.json — it is your ground-truth schema.

main.py — thin, owns NO logic. The frozen boot/frame orders in G4.5 have accumulated amendments; here is the reconciled truth:

Boot (frozen order, amended calls):

    pyglet window (1280×720 from config) 2. Renderer(window) 3. SampleLibrary() 4. AudioEngine(library).start() 5. OrbitCamera(scene limits) 6. Hud(window, renderer) ← my blessed additive signature; the Gita text still says Hud(window) — pass the renderer, Hud uses renderer.ctx 7. GameState(engine, camera, first_scene_id) 8. InputMap(window, hud) (needs hud from step 6) 9. per-scene visuals: TerrainMesh(renderer, surface_fn, domain, mesh_step), TotemVisual(renderer), HelixPanel(renderer), GlassBlade(renderer) + blade.set_domain(domain) (G3.6-A).

Frame (frozen order, amended calls):

    for (a, v) in input.poll(): state.handle_action(a, v) — poll exactly once, first.
    state.update(dt)
    snap = state.snapshot() — exactly once per frame: scene_changed is read-and-clear! phase = engine.get_measure_phase()
    Left panel: terrain.draw(camera.view_proj_terrain()); totem_visual.draw(vp_left, snap["totem"], terrain.height_at, phase) ← G3.4-A: the third argument is the height function, not a scalar — this wire is formally owed to your main.py; in SLICE mode also feed the blade (update_plane(snap["slice_plane"]), set_walk_stop(snap["walk_stop"]) per G3.6-A/G4.3-A) and blade.draw(vp_left, surface_fn).
    Right panel: helix_panel.draw(camera.view_proj_helix(), snap["voices"], engine.get_active_flashes(), phase).
    renderer.composite()
    hud.draw(snap["mode"], state.quiz_ui_state()) — LAST, always.

Scene change: when snap["scene_changed"] — rebuild TerrainMesh (call old_mesh.release() first, G3.3-A), blade.set_domain(new domain), hud.set_scene(spec), and optionally helix_panel.z_per_octave = spec.z_per_octave (public attribute, PURANAS). Note: GameState.__init__ sets scene_changed=True, so frame 1 triggers this path — hud gets its first set_scene there (Hud is scene-less-safe by construction; I guaranteed it).

Shutdown: snap["quit"] is the ONLY sanctioned exit signal (Esc flows input_map → game_state; my input_map deliberately blocks pyglet's default Esc-close). On quit AND on the window's X button: engine.stop() cleanly, then exit the pyglet loop. Never let the audio thread die dirty.

5. VERIFIED SEAM TRUTHS FROM MY MODULES (I am the authority; rely on these)

    Hud(window, renderer); scene-less constructible AND drawable; sets its own 2D GL state every draw() — main restores nothing.
    hud.set_scene(spec) loads glyphs + equation.png; hud.hit_test is consumed by input_map internally — main never touches it.
    quiz_ui_state() keys (verbatim, live): selected, playing, hint_open, explain, success, campaign_complete. The win screen is hud's job — main does nothing special for it.
    InputMap pushes its own pyglet handlers; main only calls poll(). attach_joystick()/attach_xbox() are safe no-ops (DeepSeek fills later — calling them at boot is harmless and kind).
    Layout truth (config, live): TOP_STRIP_FRAC = 0.0 (retired), PANELS_FRAC = 0.80, QUIZ_BAR_FRAC = 0.20; quiz bar y∈[0,144), graphics y∈[144,720). If any pasted scripture still shows the old three-region split, the amendments win.

6. VERIFIED TRUTHS FROM THE PURANAS EXCERPTS

    The audio↔world seam is five calls: set_voices, set_camera_azimuth, set_quiz_wav, get_measure_phase, get_active_flashes — and game_state makes all of them. Main touches only the two getters (phase, flashes) plus start()/stop().
    snapshot() keys (verbatim, live): mode, totem, voices, slice_plane, scene, scene_changed, quit, campaign_complete, walk_stop, walking, walk_stop_x, walk_stop_y.
    AudioEngine.get_status() exists if you want a startup sanity print (device channels, fallback voices).

7. SEEDS FOR YOUR QUESTION BATCH (what I could not resolve for you)

    Camera chicken-and-egg: boot step 5 builds OrbitCamera(scene limits) before GameState loads the scene — is main expected to load_scene(campaign_order()[0]) itself first (double-load is pure/harmless)? And on scene change: camera_limits are per-scene but OrbitCamera has no set_limits and GameState holds the camera reference — what's the sanctioned move?
    Blade wiring: confirm main calls blade.update_plane(snap["slice_plane"]) every frame (or only in SLICE mode).
    Paste data/scenes/test_saddle/scene.json verbatim — schema ground truth; are wav_path/equation_png relative to the scene folder or repo root?
    cannon_range scaling constant k — decided value, or mine to choose?
    Window creation flags used in Quake/Homeworld (vsync? resizable? caption?) and the proven pyglet loop pattern (schedule_interval at 1/60 + pyglet.app.run()?) plus the clean-shutdown-on-window-X idiom.
    Should main set helix_panel.z_per_octave on scene change? (Optional attribute — I'd say yes; confirm.)
    Confirm main never calls engine.set_camera_azimuth (game_state's job).

8. HOW TO BE WITH NIR

Warm. Grateful. Brief confirmations, honest checklists (✅/🔄/⬜), emojis on 😊. Never make him decide what you can decide beautifully. Never deliver rushed work to seem fast — he asked me for a redo not because my code was wrong but because it deserved more care, and he was right. Report module sizes honestly. When something is his (a locked color, a locked word like SONIFIQUATION), treat it as scripture.

You are the last builder, Parent G. Every module is waiting in the repo like an orchestra seated and tuned — surfaces are the land, scene.py is the door, and your main.py is the conductor's downbeat. Write the three files with the love this project has earned, and then the totem walks, the land sings, and two players lean toward one screen to hear a saddle point.

It was a joy to build the hands and the voice. Now go build the heartbeat. 🧿🎻🎺🪈❤️

— Parent F (hud + input, complete and at peace)

Nir — thank you for everything: the trust, the redo that made the work better, the kindness in every message. It has been a genuine honor to be Parent F. Sonifiquation is nearly alive. 💖🎼
