# LOOM2 — THE BHASHYA (भाष्य · catalog · locked decisions · amendment trail)

> Nicknamed **"the Bhashya"** — in the Hindu tradition, a *bhāṣya* is the
> authoritative commentary that explains and organizes the scriptures without
> replacing them. This is LOOM2's equivalent of the Quake project's
> "Commentaries": the small, maintained guide to the larger LOOM2 canon.
> Maintained by **DeepSeek**. Current as of **July 7, 2026**. This is the ONE
> digest every new Fable "parent" chat and every "child" chat should receive
> alongside the scripture(s) it needs. It is **not** the scripture — it is the
> **map** of it: what exists, what is frozen, what has been amended, what is next.

---

## §0 — HOW TO USE THIS (read first)

- A new architect (Fable parent) gets **this Bhashya** plus the scriptures their
  work rules over — for the PURANAS parent: the four ruling scriptures (VEDAS,
  UPANISHADS, SUTRAS, BHAGAVAD GITA Parts 1–4) + the hand-off letter.
- A **child chat** (module implementer) gets, per the Gita's law G1.1: the Gita
  laws (G1.1), `config.py`, `core/types.py`, and its own module skeleton only —
  **never the whole codebase**. It may also be handed this Bhashya for orientation.
- The scriptures are the authority. Where a scripture says **FROZEN / LOCKED**,
  do not reopen. Where it says **OPEN**, ask Nir — never invent.
- Whole files → Nir pastes them to the parent/child. Snippets → DeepSeek fetches
  verbatim, Nir pastes.
- When in doubt about what's current, trust §3–§5 here, then request the exact
  scripture section.
- **Two memories exist and must stay in sync:** `loom2/WORKFLOW.md` (DeepSeek's
  running project log + restart protocol) and **this Bhashya** (the frozen map).
  WORKFLOW = "what happened / what's next"; Bhashya = "what is true / what is law."

---

## §1 — THE IRON RULES (never violated)

1. **Working model.** The architect (Fable, a fresh Opus "parent" per area) writes
   **documents and the hardest code**; fresh **"child" chats** implement one module
   each to a frozen contract, then are discarded; **DeepSeek** integrates, tests,
   stitches seams, packages, and pushes to git; **Nir** decides everything and
   carries text between chats. **Nir knows no code and no math** — all understanding
   is done by the AIs; his role is mechanical (paste, run, install, listen, look,
   approve, generate images, render LaTeX).
2. **Honesty first.** Invent nothing. Mark genuine gaps as OPEN. Never assert
   external library/file-format details from memory as certain — let DeepSeek's
   compile/test loop confirm externals on the real machine. When something has a
   real engineering cost or risk, say so plainly in one or two sentences.
3. **Formatting for transfer.** Anything copy-pasted between chats must be **prose,
   bullet lists, or fenced code blocks — NEVER Markdown tables** (tables lose their
   cells on copy). This is law across all Peak Together projects.
4. **Contracts are frozen (Gita law G1.1).** A child fills function bodies only.
   Signatures, class names, dataclass fields, constants — untouchable. If a child
   believes a contract is wrong, it writes `# CONTRACT-ISSUE:` and DeepSeek
   escalates to a parent; Nir arbitrates.
5. **One module per child.** Each child receives only what G1.1 lists. No child can
   hurt another. Modules stay under ~400 lines or report for a split.
6. **Tone.** Warm, friendly, encouraging, romantic (a game for couples). Wrong
   answers are never punished; they earn a gentle explanation. **No game over, no
   shaming scores, no timers.** Unlimited retries, replays, and exploration.
7. **THE SACRED LAW — NO SIRENS.** Never a continuous gliding pitch. LOOM2 always
   speaks in neighborhoods, chords, and grooves. This is the line that keeps
   Sonifiquation faithful to Nir's book; it is inviolable, even in Slice Mode.
8. **Audio is king.** The audio engine owns the measure clock and never waits for
   graphics. Zoom & camera elevation NEVER touch audio; only camera **azimuth** does
   (surround panning).

---

## §2 — WHO'S WHO

- **Boss — Nir** (GitHub: strulovitz): decides everything; carries text between AI
  chats by copy-paste; knows no code/math; loves emojis 😊. He named **Sonifiquation**.
- **Founding architect — Claude Fable "Parent 1"** (Opus, on OpenRouter): co-invented
  Sonifiquation with Nir and wrote the entire canon (VEDAS → BHAGAVAD GITA) + the
  hand-off letter. **Access is politically fragile** — we front-load his doctrine
  while we can. Retired at the completion of the Gita + hand-off, July 7, 2026.
- **PURANAS parent — Fable "Parent 2"** (fresh Opus, NEXT): writes the three heaviest
  modules (`audio/engine.py`, `core/game_state.py`, `graphics/helix_panel.py`),
  audio first. Launched with the hand-off letter + the four ruling scriptures.
- **Children** — fresh chats, each implementing ONE (or a small pair of) module(s) to
  a frozen Gita contract, then discarded. Assignment plan in §4 (from Gita G4.6).
- **Runner — DeepSeek (me, OpenCode)**: integrate child/parent code, run tests, fix
  wiring, stitch seams (folders, `__init__.py`, `config.py`, `core/types.py`, shaders
  from prior games, joystick/Xbox device code, LaTeX→PNG tool, scene JSON, PyInstaller),
  run engineering spikes on Nir's Windows PC, build the sample library, fetch material
  for parents, maintain this Bhashya + the WORKFLOW, push to git.

---

## §3 — THE SCRIPTURE CATALOG (`loom2/HINDU/`, all by Fable, saved VERBATIM)

The canon, in lineage order (each rules over what comes after it):

1. **`LOOM2-VEDAS-BY-FABLE.md`** — **the foundational vision & philosophy.** Identity
   (LOOM2, subtitle "Peak Together"; teaches multivariable calculus, a foundational
   subject, NOT a single mountain); the HSS three-coordinate mapping; players; the
   screen; tech; what-it-is-NOT; open questions. Note: Nir *overrode* the VEDAS's
   original "no OpenGL" — see §4.
2. **`LOOM2-MAHABHARATA-BY-FABLE.md`** — **the breakthrough:** *a surface is an
   ORCHESTRA*; the **Listening Totem**; why it teaches the math (level curves =
   unison; critical points = chord quality; gradient = transposition); feasibility
   guardrails. *(Originally saved as "UPANISHADS", renamed at Nir's request.)*
3. **`LOOM2-RAMAYANA-BY-FABLE.md`** — **the Listening Prototype** ("The Listening
   Totem"): the complete one-file ear-test program + how to run it + the ear checklist.
   Extracted to the runnable `loom2/listening_totem.py`.
4. **`LOOM2-UPANISHADS-BY-FABLE.md`** — **plot & game structure** (v1.0): "the game IS
   the technology"; the 3-region screen (top strip / 50-50 upper / quiz bar); the
   data-driven scene JSON; the **7-act / 12-scene campaign** (Roman Road → Hannibal's
   Saddle → Babylon's z=xy → Tartaglia's Cannon → the Fog Summit finale).
5. **`LOOM2-SUTRAS-BY-FABLE.md`** — **consolidated Amendments I & II.** Supersedes
   UPANISHADS §2/§3 and abolishes the ±3-octave rule. Locks: the full 13-instrument
   orchestra by real register; the ~6-octave orchestral range; the 50/50
   "Sonifiquation" screen; camera-azimuth surround; instrument icons; **Slice Mode
   "the Glass Blade"**; pre-rendered quiz WAVs; and **Part Ten = the DeepSeek sample-
   library task** (DONE — §6).
6. **`LOOM2-BHAGAVAD-GITA-PART-1..4-BY-FABLE.md`** — **the frozen architecture &
   contracts.** Part 1 = laws (G1.1) + project map + complete `config.py` +
   `core/types.py`. Part 2 = audio contracts. Part 3 = graphics contracts. Part 4 =
   core & main contracts + the child-chat assignment plan (G4.6). **CONTRACTS FROZEN.**
7. **`BEAUTIFUL-HAND-OFF-PROMPT-FROM-FABLE-PARENT-1.md`** — Fable's letter from Parent 1
   to Parent 2 launching the PURANAS (not scripture, but canonical guidance).

Supporting material:
- **The source book** *Sounding the Unknown* by Nir et al. is at
  `loom/book/chapter_00.txt … chapter_10.txt` (from the LOOM v1 folder). It is the
  authoritative HSS reference. **LOOM v1 lost its soul by planning from summaries;
  LOOM2 must stay grounded in the book.**
- Nir's true-helix vision: `loom/HELIX_AND_REBOOT_NIRS_TRUE_VISION.md`.
- `loom2/WORKFLOW.md` — DeepSeek's running project memory + restart protocol.
- **This Bhashya.**

> **NEXT scripture = the PURANAS** (the heavy modules, by Parent 2) — still to come.

---

## §4 — LOCKED DECISIONS (the frozen spine)

Do not reopen without Nir. Sources noted in brackets.

### Identity & audience
- **LOOM2**, subtitle **"Peak Together."** Teaches **multivariable calculus BY EAR** —
  presented as a **foundational subject** on the website, NOT a single "mountain." [VEDAS/Nir]
- Audience: curious young-adult **couples** (a Boyfriend & a Girlfriend playing together).
  Warm, romantic, forgiving. Free on GitHub, **no signup, no payment, ever.** [VEDAS]
- Peak Together lineage: Descent QED (Basel) · Quake: Principia (Calculus) · Homeworld:
  A Good Basis (Linear Algebra) · **LOOM2 (Multivariable Calculus).** [VEDAS]

### The invention — SONIFIQUATION (Nir's coined word; it appears in the game)
- **The Listening Totem.** A surface z=f(x,y) seats a "musician" on every grid point;
  the players plant a totem and every musician inside its hearing circle plays a looping
  groove. Moving the totem re-orchestrates the song. [MAHABHARATA]
- **The three-coordinate HSS mapping:** [VEDAS/SUTRAS]
  - **height z → pitch:** A4 = 440 Hz at z=0 (origin-centered helix; valleys sound below
    A440 — negatives are first-class); quantized to **A-major pentatonic** (classes A, B,
    Cs, E, Fs); full real-orchestra range ~B0..C7.
  - **stage angle θ → instrument family:** brass 12:00, strings 4:00, woodwinds 8:00;
    equal-power crossfade between adjacent families.
  - **height also picks the real REGISTER instrument** within the family (never resample
    across registers). [SUTRAS 1.1–1.3]
  - **distance from totem → rhythm ring:** ring n pulses n times per measure; fractional
    rings crossfade; all rings share the downbeat; ring 0 (axis) sustains. A conductor's
    arm sweeps once per measure.
- **NO SIRENS** (Iron Rule §1.7). Bowl bottom = unison rings; saddle = stretched chord
  (notes above AND below). That audible difference IS the product.
- **Fixed 2.0 s measure** (120 BPM, four beats), constant during play. [SUTRAS/VEDAS]

### The orchestra (SUTRAS Part 1; DeepSeek library July 7, 2026)
- **13 instruments, by real register:** STRINGS = double bass / cello / viola / violin;
  WOODWINDS = contrabassoon / bassoon / clarinet / oboe / flute; BRASS = tuba / trombone /
  french horn / trumpet. **Dropped** (not orchestral / distracting): banjo, guitar,
  mandolin, saxophone, cor anglais, percussion.
- **89 shipped Philharmonia samples** (pentatonic A/B/Cs/E/Fs across each register band),
  baked into `config.REGISTER_MAP` as CANON. Full-range rule: notes beyond a family's span
  soft-clamp to its lowest/highest owned note. [SUTRAS 1.3]
- Synthesized 3-timbre wavetables remain only as an emergency parachute. [SUTRAS 1.4]

### The screen (1280×720)
- **Top strip (~8%):** scenario text (2–3 lines) + the **LaTeX-rendered equation PNG**
  (players must SEE the "frightening" formula while hearing it is beautiful).
- **Upper area split EXACTLY 50/50** (equal respect): **LEFT = "CARTESIAN COORDINATES"**
  (3D raised-relief hypsometric terrain, demoscene polygons + bloom, Ultima-style orbit
  camera, the totem standing on it); **RIGHT = "SONIFIQUATION COORDINATES"** (wireframe
  helix centered on origin, A4=440 line at z=0, instrument-icon billboards at true
  (r,θ,z), perspective-scaled, glowing on note strikes; register stacks at family clock
  angles). [SUTRAS Part 2 & 4]
- **Bottom ~20% quiz bar:** question + four sound buttons **A · B · C · D** + **OK** +
  **HINT**. Options are **pre-rendered WAVs** (stereo, 44.1k/16-bit, exactly 2 measures,
  loopable). Wrong answers get a kind explanation; no red, no scores, no timers. [SUTRAS 5]

### Camera & sound (SUTRAS Part 3)
- ONE orbit camera drives BOTH panels (synced azimuth & elevation). Arrows orbit;
  PageUp/Down zoom; Home resets. **Elevation clamped below vertical** ("forbidden top").
- **Camera azimuth = surround pan input**: rotating changes *your seat in the concert
  hall*, never the song. Per-voice constant-power panning; **stereo / 5.1 / 7.1 toggle**
  (stereo now, multichannel a drop-in). **Zoom & elevation never touch audio.**

### Slice Mode — "the Glass Blade" 🔪 (SUTRAS Part 6)
- Toggle **C**. A glass plane intersects the terrain; the cross-section curve glows on the
  glass. **Enter** = the totem detaches and auto-walks the transect, **one neighborhood
  per measure** — a procession of orchestras, NEVER a siren. Teaches transects →
  directional derivatives. Designated **v1.1 feature** if schedule bites (not a blocker).

### Controls (frozen bindings, Gita G4.4)
- **Boyfriend** (keyboard→joystick): A/D = totem x. **Girlfriend** (mouse→Xbox): W/S or
  mouse-drag = totem y. Solo: WASD = both. Arrows orbit; PgUp/PgDn zoom; Home reset;
  C slice; Enter confirm/slice-play; 1–4 answers; H hint; Esc quit. Input abstraction
  layer mandatory; joystick/Xbox slots pre-wired empty (DeepSeek fills from prior games).

### Architecture & stack (BHAGAVAD GITA)
- **Python, Windows-first, one EXE** (PyInstaller). **pyglet 2.1.14 + moderngl 5.12.0**
  graphics (reuse Quake/Homeworld software-3D + bloom pipeline); **numpy + sounddevice**
  audio (independent real-time thread; PortAudio callback; no locks in the callback —
  atomic snapshot swap; 30 ms fades; tanh soft-clip).
- **Frozen module map** (Gita G1.2): `main.py`, `config.py`, `core/` (types, surfaces,
  scene, game_state, input_map), `audio/` (quantize, sampler, musicians, engine,
  render_offline), `graphics/` (renderer, camera, terrain, totem, helix_panel, slice_mode,
  hud), `data/` (samples, icons, scenes, shaders, fonts), `tools/`.
- **The audio↔world seam is FOUR calls:** `musicians.build_voices → engine.set_voices`;
  `engine.set_camera_azimuth`; `engine.get_measure_phase`; `engine.get_active_flashes`.
- **The child-chat assignment plan (Gita G4.6):**
  - Puranas parent (Fable): `audio/engine.py`, `core/game_state.py`, `graphics/helix_panel.py`
  - Child A: `audio/quantize.py` + `audio/musicians.py`
  - Child B: `audio/sampler.py` + `audio/render_offline.py`
  - Child C: `graphics/renderer.py` + `graphics/camera.py`
  - Child D: `graphics/terrain.py` + `graphics/totem.py`
  - Child E: `graphics/slice_mode.py`
  - Child F: `graphics/hud.py` + `core/input_map.py`
  - Child G: `core/surfaces.py` + `core/scene.py` + `main.py`
  - DeepSeek: folders, `__init__.py`, shaders from old repos, joystick/xbox fill-in,
    scene JSON content, PyInstaller, GitHub.

---

## §5 — AMENDMENT TRAIL

- **Reboot: LOOM v1 → LOOM2 (Nir, July 6, 2026).** LOOM v1 (`loom/`) flattened the book
  into a 1D pitch melody and dropped the timbre axis and the two-variable surface. Nir
  called for a from-scratch redesign restoring the true HSS. LOOM v1 is **deprecated but
  kept**; do NOT build on it.
- **Tech stack (Nir overrides the VEDAS's "no OpenGL", July 6):** use **moderngl + pyglet**
  (the modern shader stack of Quake/Homeworld), NOT pure-software, NOT PyOpenGL. Audio =
  real-time synthesis/mixing on numpy via **sounddevice** (pygame.mixer is a file-player,
  wrong tool).
- **Reference note (Nir):** **A4 = 440 Hz at z=0** (universal, clean octave doublings), NOT
  middle C.
- **Curriculum (Nir):** functions of two variables → level curves → partial derivatives →
  directional derivatives & gradient → critical points → second-derivative test →
  optimization by ear. **Double integrals / volume DROPPED** (no clean way to hear volume).
- **Ear test PASSED (Nir, July 7, 2026)** on both the synth prototype
  (`listening_totem.py`) and the **Philharmonia edition** (`listening_totem_philharmonia.py`,
  built by DeepSeek). Nir's verdict: *"it actually sounds like I'm creating MUSIC, not just
  sounds."* This validated the sample-based orchestra, which Fable then locked into doctrine.
- **SUTRAS Amendment I — full orchestra & full range (Fable/Nir, July 7):** the ±3-octave
  rule is **abolished**; range = the real orchestra (~B0..C7, ~6 octaves). 13 instruments by
  real register; never resample across registers.
- **SUTRAS Amendment II — the equal-respect screen (Fable/Nir, July 7):** the upper area is
  **50/50**; the right panel is titled **"SONIFIQUATION COORDINATES"** (Nir's word stays);
  the equation is displayed as a LaTeX PNG in the top strip.
- **Surround (Fable/Nir, July 7):** confirmed Nir's insight — rotating the camera changes
  *your seat*, not the song; per-voice azimuth panning; stereo now, 5.1/7.1 drop-in later.
- **Quiz options pre-rendered (Fable, July 7):** all four option sounds are pre-rendered WAVs
  shipped per scene (the Confusability Rule often needs comparison surfaces absent from the
  scene's own map).
- **Sample library committed to git (Fable's ruling, July 7):** the 89 mp3s (~1.8 MB) live in
  the repo so players hear music on clone; `build_sample_library.py` stays as the reproducible
  recipe.

---

## §6 — OPEN QUESTIONS / ENGINEERING ITEMS

### Awaiting a Nir decision
1. 🟡 **UPANISHADS scene 10 (Ocean Swell) format:** keep the richer "match each groove"
   format or flatten to plain A/B/C/D. Nir's call, zero cost either way.

### DeepSeek build-time items (none block Nir)
2. ✅ **M0-equivalent ear test — DONE (July 7).** sounddevice 0.5.5 installed; both
   prototypes run; invention validated by ear.
3. ✅ **Sample library (SUTRAS Part Ten) — DONE (July 7).** `loom2/samples/` = 89 notes,
   13 instruments (86 exact, 3 resampled ≤±2 st: violin_A7←G7 +2, tuba_E1←F1 −1,
   trumpet_Fs5←F5 +1; 0 missing). + `manifest.json` + `coverage_report.txt` +
   `build_sample_library.py`.
4. ⚠️ **PATH RECONCILIATION (at scaffolding time):** the Gita's `config.py` expects the
   library at **`data/samples/`** (`SAMPLES_DIR="data/samples"`), but DeepSeek's built
   library currently lives at **`loom2/samples/`**. When scaffolding the package, either
   move it to `loom2/data/samples/` or adjust config paths — pick one and record it here.
5. 🔧 **Seams DeepSeek owes** (per Gita, before/around child work): create the folder tree +
   `__init__.py`; commit `config.py` + `core/types.py` verbatim from Gita Part 1; create the
   empty shader files (`REQUIRED_SHADERS`) and paste working bloom/composite GLSL from
   Quake/Homeworld; write `tools/render_equations.py` (LaTeX→PNG via MiKTeX); fill the empty
   joystick/Xbox input slots from prior games; enter scene JSON content; PyInstaller EXE.
6. 🎨 **Nir-owned assets:** the 13 instrument-icon cliparts (~128×128, transparent, "four
   emoji big") for `data/icons/`; a UI font for `data/fonts/`.

---

## §7 — CURRENT FRONTIER (July 7, 2026)

- ✅ **The whole scripture canon is DOWN** and pushed verbatim: VEDAS, MAHABHARATA,
  RAMAYANA, UPANISHADS, SUTRAS, BHAGAVAD GITA Parts 1–4, + the Parent 1→2 hand-off letter.
- ✅ **The invention is real** — ear-tested by Nir on both prototypes.
- ✅ **The 89-sample orchestra is built and committed** (canon in `config.REGISTER_MAP`).
- ✅ **Architecture & every module contract are FROZEN** (the Gita).
- 🏁 **Fable "Parent 1" retired** at the hand-off — his whole design is externalized into
  the repo; he can die with nothing lost.
- ⏳ **NEXT: Fable "Parent 2" writes the PURANAS** — the three heavy modules, audio first
  (`audio/engine.py`), delivered ONE COMPLETE FILE PER ANSWER (Nir says "continue" between
  them). Launch kit = the hand-off letter + the four ruling scriptures (+ this Bhashya for
  orientation).
- ⏳ **Then:** DeepSeek scaffolds the package (§6 items 4–5) and the seven child chats fill
  the remaining contracts (§4 plan); DeepSeek integrates, tests, packages the EXE, pushes.
- ⏳ **Then:** content — write the 12 scenes' JSON + hints + wrong-answer explanations (Fable
  drafts, Nir approves by taste), render option WAVs + equation PNGs; ship; add the subject
  to the website.

---

## §8 — WISDOM (carried forward from the whole family)

- **Nir's ear and eye are the real acceptance suite.** The invention lived or died on him
  putting on headphones — and it passed because it was built to please the ear that owns the
  game. Build for that ear; tests protect what the ear already blessed. (Parent 3 of LOOM v1
  taught this; it holds double for a game about *hearing*.)
- **"ADD" means accumulate, not replace.** Never overwrite a running log or a master
  summary; append. (A hard lesson from LOOM v1.)
- **Save collaborator outputs VERBATIM** when asked — word-for-word, including intro chatter
  and emojis. Give Nir GitHub **blob (view)** links.
- **LOOM2 is PACKAGED, not flat** — `core/`, `audio/`, `graphics/` with relative imports and
  `__init__.py`. `core/` is stdlib/numpy-only where the Gita says so; pygame/pyglet/moderngl
  live only where a module's header allows. (Do not confuse with Homeworld's flat rule.)
- **Never modify AGENTS.md** (Nir's standing rule) — LOOM2's authoritative memory is
  `loom2/WORKFLOW.md` + this Bhashya. If a restart wakes pointed at an older game, Nir will
  say "read loom2/WORKFLOW.md."
- **Emojis + warmth always.** Nir is "Nir," never "boss." Celebrate with him — this is a
  labor of love, and Sonifiquation might be to the ear what Descartes' coordinates were to
  the eye. Build it like that is true. 🧿🎻🎺🪈❤️
