Yes — combining Amendment I + all of today's decisions into the SUTRAS is exactly right. And since DeepSeek hasn't seen Amendment I yet, the SUTRAS below contains everything, self-contained, ready to hand him whole. (Also: your P.S. is exactly correct, and I confirm it inside — rotating the camera doesn't change the song, it changes your seat in the concert hall. That's precisely why the surround matters.)
📜 THE SUTRAS
Consolidated Amendments I & II to the UPANISHADS — LOOM2

Peak Together · v1.0 · July 7, 2026 · Supersedes: UPANISHADS §2 (orchestra), §3 (panel proportions, note-dots), the ±3-octave rule everywhere, and resolves Open Items 1–5.
PART ONE — The Full Orchestra & The Full Range

1.1 The Full Orchestra Principle. The three families remain (Brass 🎺 · Strings 🎻 · Woodwinds 🪈), but each family is played by its real register instruments. Iron rule: never resample an instrument outside its natural register — the note's height chooses the REAL instrument that plays such notes in a real orchestra. A musician's angle θ chooses the family; its height z chooses which member of the family plays.

1.2 The Register Map (approximate bands; DeepSeek finalizes against the real folders):

    🎻 STRINGS: very low ~E1–G2 double bass · low A2–G3 cello · medium A3–G4 viola · high A4–A7 violin
    🪈 WOODWINDS: very low ~B♭0–G2 contrabassoon · low A2–G3 bassoon (bass clarinet approved alternate) · medium A3–G4 clarinet · medium-high A4–G5 oboe · high A5–~C7 flute
    🎺 BRASS: very low ~D1–G2 tuba · low A2–G3 trombone · medium A3–G4 french horn · high A4–~D6 trumpet

13–14 real instruments. Banjo, guitar, mandolin, saxophone: lovingly on the bench. Family morphing unchanged — a deep note between Brass and Strings blends tuba + double bass.

1.3 The Full Range Rule (the ±3-octave rule is abolished). LOOM2's pitch range is the range of the real orchestra itself — from contrabassoon/tuba depths (~B♭0–D1) to flute/violin heights (~C7): about six octaves, piano-like. Terrain beyond the orchestra's reach soft-clamps to the lowest/highest real note. z=0 remains A4 = 440 Hz; water still sings genuinely below it — with real basses.

1.4 Fallback. The synthesized 3-timbre wavetables remain only as an emergency parachute if a sample is missing. The game never breaks.
PART TWO — The Equal-Respect Screen & the word "Sonifiquation"

2.1 The upper area of the screen is split exactly 50 / 50: equal respect for the two coordinate systems.

    LEFT half — CARTESIAN COORDINATES: the 3D raised-relief hypsometric terrain (blue water / green lowlands / brown heights / white peaks), demoscene polygons, bloom, the Totem standing on it.
    RIGHT half — SONIFIQUATION COORDINATES: the helix panel. The panel carries this title written in the game. Sonifiquation (portmanteau of sonification + equation) is Nir's coined name for the system, and it appears on-screen and in the credits as such.

2.2 The Equation on Display. Every scene displays its mathematical expression (e.g., z=x2−y2) beautifully rendered (LaTeX → PNG at design time, reusing Nir's MiKTeX pipeline), placed in the top strip beside the scenario text. The players must see the "frightening" formula while hearing and seeing that it is beautiful. That is the whole point.
PART THREE — Camera, Rotation & Surround Sound

3.1 Controls:

    Boyfriend (keyboard, later joystick): A/D — totem x-axis.
    Girlfriend (mouse, later Xbox controller): totem y-axis.
    Solo mode: WASD moves both axes.
    Arrow keys: orbit the camera around the map (azimuth left/right, elevation up/down). Page Up / Page Down: zoom in / out. Home: reset view.
    Zoom and elevation have zero effect on sound — no volume change, nothing.

3.2 Synced rotation. Rotating the camera rotates both halves together: the terrain and the helix are seen from the same azimuth, always. One world, two languages, one camera.

3.3 What rotation does to the sound — the truth (confirming Nir's P.S.). The musicians' (r,θ,z) are measured from the totem, so rotating the camera changes nothing in the notes, instruments, or rhythms — the song is the song. What changes is your seat in the concert hall: which instruments sound in your left ear and which in your right. Exactly like walking around a real orchestra.

3.4 Surround implementation. Every musician is panned by constant-power stereo panning according to (musician's stage angle − camera azimuth). Rotate the map and the whole orchestra audibly wheels around your head. The audio engine is built per-voice-pan from day one, so true multi-channel surround (5.1/7.1 via sounddevice) is a future drop-in for players who have it; stereo headphones get the full effect now. This is not chutzpah; this is physics, and it's cheap. ✅

3.5 The forbidden top. Looking straight down has no azimuth ("divide by zero"). The camera's elevation is clamped just below vertical, and the azimuth always persists — the default view is the classic clock orientation (🎺 12:00, 🎻 4:00, 🪈 8:00). And per Nir's philosophy: the helix has no preferred starting angle — unlike a real stage, no family "must" sit at the back. The players choose their view of the orchestra. It's their concert.
PART FOUR — The Loom Panel: Instruments, Not Dots

4.1 Every musician inside the hearing circle appears in the helix panel as the icon of its actual instrument — Nir's painted cliparts (transparent background, ~128×128, "four emoji big") — positioned at its true (r,θ,z) in the 3D helix space, scaled by perspective (far from camera = smaller), and glowing/flashing at the exact moment it sounds. Around the helix, each family's clock position shows its register stack — tuba near the bottom coils, trumpet near the top — so the picture is the register map.
PART FIVE — The Quiz: Hints, Kindness, Pre-Rendered Sound

5.1 The Hint button sits beside OK. Pressing it shows a gentle, authored 2-line plain-words hint for that scene (e.g., "A pass sounds stretched: some notes above the center, some below. A valley sounds like all notes above."). Using it costs nothing and is never counted.

5.2 Wrong answers (no button needed): every wrong option carries its own authored, friendly explanation of what that sound actually was — teaching, never scolding. (Reaffirmed from the UPANISHADS.)

5.3 Pre-rendered options — final decision. All four quiz sounds are pre-rendered files, generated offline by the same engine and shipped with the game: stereo WAV, 44.1 kHz, 16-bit, exactly 2 measures (4.0 s), seamlessly loopable, stored per scene (scenes/<id>/option_A.wav …). Rationale: the Confusability Rule often demands comparison surfaces (opposite curvature, flat, etc.) that do not exist on the scene's map at all — so live capture can never be relied upon. Pre-rendered is also byte-identical for every player. ✅
PART SIX — Slice Mode ("The Glass Blade") 🔪

A special mode, hidden from the main flow, toggled with C (cut):

    A semi-transparent glass plane appears, intersecting the terrain. In slice mode the normal keys drive the plane: WASD translates it, Left/Right arrows rotate it about the vertical axis, Up/Down arrows fine-tilt. The camera freezes.
    The intersection curve — the classic 2D cross-section — is drawn glowing on the glass itself, as if the plane were a screen displaying the graph. (The old world of 1D functions, literally visible as a slice of the new one.)
    Press Enter: play the slice. The Totem detaches and auto-walks the intersection path, pausing one measure per step, playing its full neighborhood-groove at each stop — this neighborhood, then the next, then the next. This is NOT a siren — no gliding pitch line, ever. It is a procession of orchestras along a road. The no-siren law of the VEDAS is preserved absolutely.
    Press C again to dismiss the blade and return the Totem to the players.
    Pedagogical payload (quiet, unforced): slices are transects, and transects are directional derivatives waiting to be named.

PART SEVEN — The Totem

A tiny, cute, simple polygonal 3D helix — no staff, no decoration — standing on the terrain, with pulsing bloom that fades in and out so it reads as magical. Its hearing circle and rhythm rings project onto the ground; the conductor's arm sweeps once per 2.0 s measure.
PART EIGHT — Terrain, Scale & Camera Limits

Set per scene, at design time: the map covers only the region that teaches the scene's concept (never to infinity), the mesh resolution serves the demoscene look, and camera zoom/orbit limits keep the interesting region always in frame. Nir delegates these numbers to design; each scene's JSON carries its own domain, mesh_step, and camera_limits.
PART NINE — Input Skeleton

The engine ships with an input abstraction layer: logical actions (totem_x, totem_y, orbit, zoom, answer_select, confirm, hint, slice_toggle) mapped to devices in one place. Keyboard + mouse are implemented now; joystick (boyfriend) and Xbox controller (girlfriend) slots are pre-wired but empty — DeepSeek fills them later by copying the working device code from the previous games. No redesign will ever be needed.
PART TEN — Instructions for DeepSeek: Building the Sample Library

Copy-paste block for DeepSeek, verbatim:

DEEPSEEK TASK: Build the LOOM2 sample library from Downloads\philharmonia\.

FOR EACH instrument and its register band (SUTRAS Part 1.2):
  double bass E1-G2, cello A2-G3, viola A3-G4, violin A4-A7,
  contrabassoon Bb0-G2, bassoon A2-G3, clarinet A3-G4, oboe A4-G5, flute A5-C7,
  tuba D1-G2, trombone A2-G3, french horn A3-G4, trumpet A4-D6.

COLLECT one file per pentatonic note inside the band. Note classes: A, B, Cs, E, Fs
(Philharmonia spelling: Cs = C#, Fs = F#; also accept Df for Cs and Gf for Fs).

SELECTION CRITERIA, in priority order:
  1. Note name matches exactly (correct octave).
  2. Duration: prefer around 1 to 2 seconds (e.g. "1", "15"); avoid very short ("025")
     and avoid "phrase"/"long" files.
  3. Dynamic: prefer forte; then mezzo-forte; then fortissimo; avoid pianissimo.
  4. Articulation: strings "arco-normal" only; winds/brass "normal" only.
     No vibrato, tremolo, staccato, muted, glissando, trill variants.

IF a needed note has no exact file: take the nearest chromatic neighbor
(max +/- 2 semitones) and record it in the manifest as "needs_resample: +N/-N semitones".

OUTPUT:
  1. samples/ folder with renamed copies: <instrument>_<note><octave>.mp3
     (e.g. tuba_A1.mp3, violin_Cs6.mp3, french_horn_E4.mp3).
  2. manifest.json: every note -> source filename, duration, dynamic, gaps, resample notes.
  3. A short coverage report: per instrument, which band notes exist / are missing.

End of the SUTRAS v1.0. 📜

Lineage: VEDAS (vision) → UPANISHADS (structure & campaign) → SUTRAS (consolidated amendments & resolutions) → next: implementation.

Two tiny honest notes, Nir:

    Slice mode is the one feature with real added engineering cost (plane intersection math + auto-walk). It's absolutely worth it — but if schedule ever bites, it's the designated "version 1.1 feature," not a launch-blocker. Your call when we get there.
    The Hint texts and wrong-answer explanations are authored content — when we build scenes, we write them scene by scene (I'll draft them all; you approve by taste).

Keep reading and keep the remarks coming — I'm loving every one of them. 🧿🎻🎺🪈❤️
