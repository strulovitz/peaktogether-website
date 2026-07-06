# LOOM BIBLE — THE COMMENTARIES (catalog · locked decisions · amendment trail)

> Nicknamed **"the Commentaries"** (after the Quake project's document of the same purpose) — the small, maintained guide to the larger LOOM scripture. Maintained by **DeepSeek**. Current as of **July 6, 2026**. This is the ONE digest every new Opus "parent" chat should receive in full, alongside the scriptures it needs. It is **not** the scripture — it is the **map** of it: what exists, what is frozen, what has been amended.

---

## §0 — HOW TO USE THIS (read first)

- A new architect (Opus parent) gets **this Commentaries in full**, plus the scripture(s) relevant to their area: always the **BIBLE (Old Testament) v1.1**; for the two hardest systems also the **New Testament**; for content production the **Apocrypha**.
- The scriptures are the authority. Where a scripture says **LOCKED**, do not reopen. Where it says **OPEN QUESTION**, ask Nir — never invent.
- Whole files → Nir pastes them to the parent. Snippets/sections → DeepSeek fetches verbatim, Nir pastes.
- When in doubt about what's current, trust §3–§4 here, then request the exact scripture section.

---

## §1 — THE IRON RULES (never violated)

1. **Working model.** The architect (Fable, or a future Opus parent) writes **documents** (design, frozen contracts, child briefs) — never running production code. Fresh **"child" chats** implement one module each to a frozen contract + tests, then are discarded. **DeepSeek** integrates, tests, pushes to git, and runs engineering spikes on Nir's PC. **Nir** decides everything and carries text between chats; Nir knows **no code and no math**.
2. **Honesty first.** Invent nothing. Mark genuine gaps as OPEN QUESTIONS. Never assert external library/file-format details from memory as certain — define our own conventions and let DeepSeek's compile/test loop confirm externals on the real machine.
3. **Formatting for transfer.** Anything copy-pasted between chats must be **prose, bullet lists, or fenced code blocks — NEVER Markdown tables** (tables lose their cells on copy). This bit us historically; it is law.
4. **Nir's hard constraint.** Nothing may require Nir to understand code or math. His actions are mechanical: paste, run, install, generate images (paste prompt → save PNG), render LaTeX with local MiKTeX, listen, look, approve.
5. **Tone.** Warm, friendly, romantic, encouraging. Wrong answers are never punished; they earn a gentle explanation. No game over, no shaming scores, no timers.
6. **Priority split.** ~90% education, ~10% entertainment. When in doubt, choose what teaches better.

---

## §2 — WHO'S WHO

- **Boss — Nir** (strulovitz): decides everything; carries text between chats; knows no code/math; loves emojis 😊.
- **Founding architect — Claude Fable** (Opus, "Parent 1", on OpenRouter): wrote the entire scripture trilogy (BIBLE + New Testament + Apocrypha). Note: **Fable access is politically fragile** — last time the model was available ~2 days before being banned in the USA, so we front-load his most valuable work (doctrine) while we can.
- **Future parents** — fresh Opus chats, each designing one area in depth from the BIBLE.
- **Children** — fresh chats, each implementing ONE module to a frozen contract + tests, then discarded.
- **Runner — DeepSeek (me, OpenCode)**: integrate child code, run tests, fix wiring, push to git, run engineering spikes (M0 etc.) on Nir's Windows PC, fetch material for parents, write prompts/handoffs, maintain this Commentaries + the WORKFLOW.

---

## §3 — THE SCRIPTURE CATALOG (`loom/BIBLE/` + `loom/`)

The scripture trilogy (all by Claude Fable, saved verbatim):
- `loom/BIBLE/LOOM_BIBLE_v1.1_BY_FABLE.md` — **Old Testament**: what LOOM is (vision, pillars, screen, core loop, co-op, content model, sonification engine, spell/pack formats, two-program architecture, curriculum, audio, accessibility, tech stack, locked decisions, parked ideas). **v1.1 fully replaces v1.0 (deleted).**
- `loom/BIBLE/LOOM_NEW_TESTAMENT_v1.0_BY_FABLE.md` — **New Testament**: deep design of the two riskiest systems — (I) the Spell Compiler & sonification engine (12-stage pipeline, spec format, Lab remap contract, testing), and (II) the Player's playhead/scrubbing/audio/Music Bench (the "Conductor", audio engine, scrub feel, widgets, Echo state machine, M0–M7 build order). Includes "Addendum A" (declared small additions to the BIBLE).
- `loom/BIBLE/LOOM_APOCRYPHA_v1.0_BY_FABLE.md` — **Apocrypha**: the frozen **Story Weaver prompt** (turns a Wikipedia page into a Problem Pack) + the pre-tuned **Spell Catalog**. Fable notes its canonical home is `loom/prompts/story_weaver_v1.md` (to be extracted when we start building).

Supporting material (all in `loom/`):
- `loom/book/` — the source book *Sounding the Unknown* by Nir et al., cleaned into `chapter_00.txt` (front matter) … `chapter_10.txt` (OCR fixed, code + picture-contents stripped). This is the intellectual foundation of HSS.
- `loom/chapter_summaries/` — Fable's own chapter-by-chapter summaries `chapter_00_summary.md` … `chapter_10_summary.md` (Ch.7 has Part 1 + Part 2).
- `loom/MASTER_SUMMARY_STORY_SO_FAR.md` — Fable's running master summary, **all versions v0 → v10 accumulated** (never overwrite — ADD each new version at the bottom).
- `loom/PROMPT_TO_FABLE_WRITE_THE_BIBLE.md` — the mission prompt that launched Fable as founding architect.
- `loom/SUMMARIES_BUNDLE_FOR_FABLE.md` — all chapter summaries + master, concatenated for one paste.
- `loom/COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md` — **this file**.
- `loom/WORKFLOW.md` — DeepSeek's project memory (state, history, next steps, restart protocol).

---

## §4 — LOCKED DECISIONS (the frozen spine)

From BIBLE v1.1 §15, plus New Testament and Apocrypha bindings. Do not reopen without Nir.

### Identity & audience
- LOOM keeps **only the name** of the 1990 LucasArts game — zero lore, mechanics, or plot from it.
- LOOM is tied to **no specific mountain**; it teaches the cross-mountain basics of **hearing functions**. It is the Arcade's ear-training foundation course.
- Audience: curious **young adults / couples** (~20yo); NOT a kids' game (but tone is warm, never scary). ~90% education / 10% entertainment. No punishment, timers, scores, or game over; unlimited retries, replays, and scrubbing.

### The five pillars
- (1) **Anyone Can Play** (the Simon Principle — hear it, see it light up, click the same keys; no musicianship required). (2) **Everything Under the Hood Is Shown** (equation + graph + helix all on screen, synced to audio). (3) **The Wandering Ear** (Scrubbing — a core pillar). (4) **Built for Two** (co-op; solo also fully supported). (5) **Forgiving Forever**.

### Screen (fixed 1280×720; positions never move)
- Top half = **Scene Stage** (Story Mode: baked Pixar-style image + caption + dialogue menu; Puzzle Mode: graph + 3D demoscene pitch **helix** + LaTeX-baked equation PNG, all synced to audio).
- Bottom half = **Music Bench**: piano keyboard (1 octave default / **2 octaves max**), real staff (treble or grand clef, **noteheads only** — no stems/beams), OK/Cancel, VLC-style transport.

### Core mechanics
- **Simon-style Echo Puzzle**: hear → triple lights (graph, helix, keys) → repeat on the on-screen piano; per-note OK/Cancel commit; gentle higher/lower hints; **grow** (default) and **whole** reveal modes.
- **Choice Puzzle**: hear 2–3 spells behind A/B/C, answer via dialogue menu (comparative sonification).
- **Scrubbing** (universal, LOCKED pillar): drag the timeline handle OR the graph surface; **note-granularity retriggering at true pitch**; any speed, both directions, lingering honored; **never resampling/pitch-bending** (pitch IS the data).
- **The Laboratory** is **IN for v1**: live sliders (tempo, span, base note, scale, instrument, note count) + scrubbing, powered by precompiled `dense_values` + shipped sample supersets.
- Two puzzle types in v1: **Echo and Choice**. **No Understanding Mode** in LOOM.

### Heroes & content
- The two heroes are named **Girlfriend and Boyfriend** — never personal names (so real couples project themselves in).
- Content = **Problem Packs** generated by the frozen **Story Weaver prompt** from a Wikipedia page: ~3 scenes, baked Pixar-style images featuring the couple, pre-written 4-option dialogue trees, slides with next/back. **Nothing generated at runtime.**
- **Co-op split**: Player K (keyboard → future joystick, canonically Boyfriend) = story, menus, Choice answers, transport hotkeys; Player M (mouse → future Xbox controller, canonically Girlfriend) = piano, OK/Cancel, transport + scrubbing. Everything mouse-operable for solo. **Input-abstraction layer mandatory** (named actions, one device→action config file).

### Sonification (all math in the Compiler)
- **Absolute mapping** θ = a·f(x); scale quantization (**pentatonic_major default**; also major, natural_minor, chromatic-advanced); beat grid; **flat rhythm default**; **≤2-octave (24-semitone) span**; discrete timbre (instrument choice + dynamic layers); **no pitch-shifting** (Philharmonia covers every note); **no runtime DSP**.
- Helix normalization: angle = 30° × (semitone mod 12); z = semitone/12 (one octave = 1.0).

### Architecture
- **Program A (Spell Compiler)** / **Program B (LOOM Player)** split. Refined **"dumb runtime"** doctrine: the Player performs **no function evaluation and no symbolic math**, but MAY do simple arithmetic on precompiled numbers (beat→seconds, MIDI compare, playhead↔region lookup, helix rotation, the Lab remap). Only data files cross the boundary (spell JSON, pack.json, MP3, PNG). No network at runtime.
- The Player's playback = **scrubbing at constant speed**: one authoritative playhead (float `playhead_beats`) owned by one engine (**the Conductor**); everything else is a pure function of it each frame (perfect sync by construction).

### Audio & assets
- Audio ships as **verbatim Philharmonia MP3s with original filenames**, per-pack subsets only; the **full library never ships** (compile-time resource on the author's PC, like MiKTeX). `library_dir` future hook designed in. **OGG/WAV conversion is the sanctioned fallback** if MP3 playback proves unreliable.
- **Silence between puzzles** — no ambient music anywhere. **Dark/tension palette permanently parked** (documented in chapter summaries, not part of LOOM).
- Compiler emits per-spell `preview.wav` + `compile_report.txt` for Nir's ear-approval loop; a global `notation_table.json` (MIDI 36–96) keeps the Player free of music theory; a fixture fake-library (`fixtures/fakelib/`) lets tests run anywhere.

### Formats & stack
- Spell + pack JSON schemas per BIBLE §8–§9 / New Testament, **semantically versioned**; Player refuses newer major versions.
- **Python desktop, Windows-first, `python app.py`**, everything under `loom/` in the existing repo. Player framework candidate: **pygame / pygame-ce** (confirmed by M0/M1). Helix = software 3D wireframe (no OpenGL). Compiler = Python + numpy + MP3 decode at compile time.
- Repo layout (target): `loom/player/` (with app.py), `loom/compiler/`, `loom/packs/<pack_id>/`, `loom/docs/`, `loom/prompts/`.

---

## §5 — AMENDMENT TRAIL

- **BIBLE v1.0 → v1.1** (all by Nir's decisions, answering Fable's 6 open questions): heroes named Girlfriend/Boyfriend; silence between puzzles locked; dark/tension palette permanently parked; shipped audio = verbatim Philharmonia MP3s with original filenames; window locked 1280×720; **Laboratory IN for v1 with live sliders**; **Scrubbing added as a core pillar + universal transport feature**; "dumb runtime" refined to permit simple arithmetic on precompiled numbers; spell schema extended (gain, lab block). v1.0 was deleted from the repo; **only v1.1 is authoritative.**
- **New Testament v1.0 Addendum A** (declared, non-contradicting): global `notation_table.json` asset; per-spell Compiler audition outputs (`preview.wav` + `compile_report.txt`); fixture fake-library convention.
- **Sample-length uniformity + the Sample Forge (Fable, July 6, 2026 — the day the violin C5 "came up short").** Three recorded lines:
  1. **Amendment (by Nir, 2026-07-06):** packs may ship **forged samples** — uniform-duration WAV derivatives produced at design time from Philharmonia originals by `loom/forge/`. The originals remain the untouchable source of truth; the sanctioned OGG/WAV-fallback doctrine already covered the container change. The Player still performs zero audio processing.
  2. **Selection law (Compiler Stage 8 + all resolvers):** sample lengths are chosen **uniformly per spell, never per-note independently** (duration must never carry information in a flat-rhythm spell — pitch is the data, so length must be uniform).
  3. **Fact corrections:** length tokens are `025/05/1/15` (+ qualitative `long/very-long/phrase`); there is **no `2` token**; `phrase` files are multi-attack gestures and are **never eligible** for spells.
  - Implementation landed: `loom/forge/forge_samples.py` (the Forge — TRUNCATE + natural release, or correlation-matched LOOP-EXTEND, then set-wide RMS loudness match; outputs to git-ignored `loom/forge/forged/`). M1 demo resolver patched to the uniform-length rule.
  - 🎧 **Nir's audition verdict (July 6, 2026 — OPEN / deferred, "continue later"):** the forged violin scale is **not yet perceptually uniform** — the 6th note **C5 (a LOOP-EXTEND note) rings very short**. The Layer-1 demo (uniform `05`) is better but **all-short**, with **E4 & A4 sticking out longer**. **Nir's goal: every note uniformly LONG/sustained (like the Forge intends), not short.** The Forge + demo audio needs another pass (make all notes long + equal; fix loop-extend hold on C5). Not blocking Part 3 / M2.
- **M2 amendments (by Nir, July 2026 — during Parent 3's Music Bench build):**
  1. **The Bench staff ALWAYS shows the full grand staff** (treble above, bass below, middle C between). This supersedes BIBLE §2's "grand clef only when required" — the Bench no longer hides the bass staff for treble-only spells. A note draws on the treble iff midi ≥ 60, else on the bass (NT Stage 5 rule). Implemented in `player/ui/bench_staff.py` rev 2.
  2. **num_notes maximum raised from 16 to 20** (BIBLE §7.2). Nir's call; the widgets were already N-agnostic, so no code enforced 16 — this is purely a doctrine number. The curved demo fixture `fixture_bench20.json` (f(x)=√x, cello, chromatic, C3–C5) uses 20 notes.
  3. **Bench width + 2-octave keyboard:** keyboard + grand staff now span almost the full 1280 width (`layout.py` rev 2); 2 octaves fill it. **LAYOUT FROZEN by Nir (2026-07-06)** — he played `m2_demo`, approved the layout as-is; the numbers are now permanent (the keyboard/staff/etc. do not move).
  4. **Every keyboard key sounds** (black keys included): the demo resolves the whole visible keyboard from the library (required_samples superset doctrine), not just the spell's own notes. Keys also gained a pressed/released visual (Windows-button feel).
- **FIT-THE-BEAT amendment (July 2026, from Nir's ghost-pedal report):** uniform sample length = the longest token whose nominal seconds do **not exceed the spell's shortest note duration in seconds** (fallback: the shortest available). This supersedes the old "prefer longest common token" rule. Reason: the 20-note cello √x demo picked 1.5s samples at a 0.667s beat, so every note rang across its neighbours — Nir's "sustain pedal from a horror movie," worsened because the chromatic melody's overlaps are semitones (max dissonance). Binding on the demo resolver now (`player/m1_demo.py` `choose_uniform_token`) and on **Compiler Stage 8** when it is built; Stage 9 / the Forge produce beat-length sustained WAVs. The deferred Forge task gains a sharpened goal: **forge samples to exactly the note's beat length + a natural release tail — long and sustained, never overlapping.** (Note: with the current Philharmonia cello library the rule lands on `025` = 0.25s for the 20-note fixture, because no single 0.5s take is common to all 20 notes — clean but short; the lush-long sound awaits the Forge.)
- **BPM control (Nir, July 2026):** additive `Conductor.set_bpm(bpm)` + read-only `bpm` property — changes playback tempo **live** (playhead_beats unmoved; only beats-per-second and the seconds readout change; raises on bpm ≤ 0). This is also pre-work for the M6 Laboratory's tempo slider. The `TransportWidget` (rev 3) gains a **typed BPM box** on the far right (opposite play/pause per Nir): click to focus+empty, type up to 3 digits, Enter commits / Esc cancels / click-away commits, values clamp **40–200**; two **spinners (±1, up-triangle above, down-triangle below)**; `.typing` property so the wiring mutes keyboard hotkeys while the box is focused. Added additively: `TransportCommand.SET_BPM` + `TransportEvent.bpm`, and `TransportWidget(rect, initial_bpm=...)`. **Content default tempo = 110** (the fixture generator writes `bpm: 110`; FIT-THE-BEAT keeps samples clean at 0.55s notes).
- **M3 POUR 1 (Parent 4, July 2026):** `core/echo_logic.py` fattened → MEAT with **ADDITIVE read-only accessors** (`reveal_mode`, `prefix_len`, `cursor`, `preview_midi`, `slot_states`) for the staff's solid/hollow/dashed slots; `ui/bench_buttons.py` born (`BenchButton`; OK must be disabled unless a preview exists — `commit()` raises on wiring misuse). **Hint-name mapping:** kind `too_low` → pack `hint_higher` text, kind `too_high` → pack `hint_lower` text (crossed names, documented). Nir's three Echo answers are ALL DEFAULTS (wrong→gentle higher/lower hint; auto-sound on correct commit; strict left-to-right slot order).

---

## §6 — OPEN QUESTIONS / ENGINEERING ITEMS (assigned to DeepSeek, none block Nir)

None require a Nir decision right now. Engineering items for DeepSeek's build-time test loop (NOT blockers for further design docs):
1. ✅ **M0 spike — DONE (July 6, 2026).** MP3 decode reliable + latency tiny; see §7 for the full result. Both biggest unknowns retired.
2. **`library_profile.json`** — the Philharmonia filename numeric token is now decoded (it is the note LENGTH in seconds: `025`=0.25s, `05`=0.5s, `1`=1.0s, `15`=1.5s, `2`=2.0s; see §7 for the full filename grammar). Still to formalize: the variant-preference ranking + confirm/amend the "safe instrument roster" (flute, clarinet, oboe, cello, violin, french-horn, trumpet) — all 20 owned instrument folders are listed in §7.
3. Final **scrub tuning constants** (`scrub_tuning.json`) — tuned by ear with Nir.
4. ✅ **pygame confirmed by M0** — pygame 2.6.1 (SDL 2.28.4) loads real Philharmonia MP3s into triggerable buffers with ~5.8 ms output latency; BIBLE §14's pygame recommendation stands (no pygame-ce needed).

---

## §7 — CURRENT FRONTIER (July 6, 2026)

- ✅ Source book read + cleaned into `loom/book/`; Fable's summaries + master summary saved.
- ✅ **The full scripture trilogy is DONE** (BIBLE v1.1 + New Testament v1.0 + Apocrypha v1.0), all saved verbatim + pushed.
- ✅ This Commentaries + the WORKFLOW written.
- ✅ **M0 DONE (July 6, 2026) — both biggest unknowns retired.** DeepSeek built a throwaway spike (`loom/spikes/m0_latency_spike.py`) and ran it on Nir's PC against the REAL Philharmonia MP3s:
  - **MP3 → buffer decode works:** `pygame.mixer.Sound` loaded real violin + oboe MP3s straight into preloaded buffers, 8/8 notes each, ~0.5–1 ms per file. No decode failures. **Verdict: MP3 is a GO** (the pre-approved OGG/WAV fallback is NOT needed).
  - **Latency is tiny:** computed output latency = buffer/44100 → **256 samples = 5.80 ms**, **512 samples = 11.61 ms**; both well under the binding **≤30 ms** budget. Software `play()` overhead ≈ 0.004 ms. **Target buffer = 256.**
  - **Stack confirmed:** pygame **2.6.1**, SDL **2.28.4**, numpy 2.4.6, mixer at 44100 Hz / 16-bit / stereo. BIBLE §14's pygame choice stands.
  - **Nir ear-confirmed:** played real violin + oboe C-major scales (C4→C5) — "sounds good", notes fire instantly. 🎻🎺
- ✅ **The Philharmonia library is present on Nir's PC** at `C:\Users\nir_s\Downloads\philharmonia\` (a compile-time resource on the author's machine — the full library is NEVER shipped; packs bundle only the few files they use, verbatim). **20 instrument sub-folders are available:** `banjo`, `bass clarinet`, `bassoon`, `cello`, `clarinet`, `contrabassoon`, `cor anglais`, `double bass`, `flute`, `french horn`, `guitar`, `mandolin`, `oboe`, `percussion`, `saxophone`, `trombone`, `trumpet`, `tuba`, `viola`, `violin`.
  - **Filename grammar (confirmed on the real files):** `instrument_note_length_dynamic_articulation.mp3`, e.g. `violin_A3_025_forte_arco-normal.mp3`. Note names use `s` for sharps (`As3`, `Cs4`), octaves ~3–8. **LENGTH** token = nominal note seconds (`025`=0.25, `05`=0.5, `1`=1.0, `15`=1.5) — **there is NO `2` token**; plus qualitative `long`/`very-long`/`phrase` (`phrase` = multi-attack gesture, NEVER eligible for spells). **Coverage is irregular** (dense for standard articulation + loud dynamics + short lengths; sparse otherwise): at violin forte+arco-normal only `025`/`05` exist for every note; oboe normal+forte has all four for every note. **Dynamics:** pianissimo, piano, mezzo-piano, mezzo-forte, forte, fortissimo (+ crescendo/decrescendo). **Articulations:** the plain sustained note is `arco-normal` (strings) / `normal` (winds); many others exist (pizz-normal, staccato, tremolo, harmonics, con-sord, …).
- 🟡 **Parent 2 (fresh Fable) LAUNCHED — building the Player core (Conductor + Audio Engine, M1), in 3 parts.**
  - ✅ **Part 1 of 3 landed + integrated (July 6, 2026):** `loom/MAP.md` (the codebase map — also saved for distribution at `BIBLE/PROJECT_MAP_BY_FABLE.md`) + the four frozen "heart" files `player/core/{spell_model,tuning,audio,conductor}.py` + `player/data/scrub_tuning.json` + package `__init__.py`s. py_compile OK; headless smoke test green. Verbatim archive: `BIBLE/LOOM_PARENT_2_PART_1_skeleton_and_heart_BY_FABLE.md`. **LOOM is PACKAGED, not flat** (`player/core/` etc., relative imports; `core/` is stdlib-only, pygame lives only in `player/ui/`).
  - ✅ **REAL-INSTRUMENTS GUARANTEE — ON THE RECORD (Parent 2, July 6):** the finished game plays the real Philharmonia MP3s **verbatim, never beeps/synth** — "the architecture cannot produce a beep." A note becomes a real filename in exactly ONE place: `compiler/library_scan.py` (scans Nir's `philharmonia\` folders → writes the filename into the spell JSON `sample` field → Player just loads+plays it). Beeps are demoted to emergency-only scaffolding (tests use `FakeAudioSink`, no audio files at all). The **M1 demo will play a real violin (fixture 1) + oboe (fixture 2)** resolved tolerantly from Nir's folders, and hard-errors (never falls back to a beep) if a file is missing. Full verbatim: `BIBLE/LOOM_PARENT_2_REAL_INSTRUMENTS_ON_THE_RECORD_BY_FABLE.md`.
  - ✅ **Part 2 landed + verified (July 6):** real pygame audio engine `player/ui/audio_pygame.py` (16-voice pool, MP3→buffer, NO synth) + violin & oboe fixture spells + emergency-only `fixtures/make_beeps.py` + the **M1 demo** `player/m1_demo.py` (drag the timeline = touch the melody) + the headless test suite (**`pytest` → 28 passed**). Resolver verified against Nir's real library. Verbatim: `BIBLE/LOOM_PARENT_2_PART_2_audio_engine_fixtures_M1_demo_tests_BY_FABLE.md`.
  - ✅ **Sample-length fix + the SAMPLE FORGE (July 6):** uniform-length resolver (Layer 1, patched into `m1_demo.py`) + `loom/forge/forge_samples.py` (Layer 2, design-time uniform-duration WAV maker). See §5 amendment + Nir's **still-OPEN audition verdict** (goal: every note uniformly LONG; the forged C5 came up short). Verbatim: `BIBLE/LOOM_PARENT_2_uniform_length_fix_and_SAMPLE_FORGE_BY_FABLE.md`.
  - ✅ **Part 3 landed (July 6) — THE FULL SKELETON.** Every remaining module of the game + compiler now exists as a small "bone": frozen interface + "FATTEN ME" note naming its milestone (M2–M7) + scripture. `player/core/{notation,echo_logic,choice_logic,lab_remap,pack_model,progress}.py`, `player/ui/{layout,input_actions,bench_keyboard,bench_staff,bench_transport,graph_view,helix_view,story_view,lab_view,menu_view}.py`, `player/app.py`, `compiler/{compile_spell,pipeline,library_scan,emit,notation_gen}.py`, `player/data/input_mapping.json`. MAP patched (`forge/` + the Selection Law). All compile; `pytest` 28 passed. Verbatim: `BIBLE/LOOM_PARENT_2_PART_3_full_skeleton_bones_BY_FABLE.md`.
- 🏁 **PARENT 2 RETIRED (July 6, 2026), thanked by Nir.** His whole design is externalized into the repo (MAP + bones + BIBLE archives) — he can die with nothing lost. Do NOT reopen him.
- ⏳ **NEXT: a FRESH Parent 3 builds M2 — the Music Bench** (keyboard + staff [noteheads only] + transport widget extracted unchanged from `m1_demo.py` + graph scrub surface + the sync bus). This is the bone/MAP system's first real proof: a fresh chat starts from `MAP.md` + the ~7 M2 bone files (`player/ui/{layout,input_actions,bench_keyboard,bench_staff,bench_transport,graph_view}.py` + `player/core/notation.py`) + `player/m1_demo.py` + the scripture sections they name. **Also OPEN:** the deferred "every note uniformly LONG" Forge task; and confirming the M1 scrub feel by Nir's ear. Later parents take the Compiler + M3–M7.
- ✅ **M2 COMPLETE — Parent 3 (Fable) built the whole Music Bench, then RETIRED (July 6, 2026), thanked by Nir at a clean, fully-tested milestone. 65 tests pass. Do NOT reopen him.** All 7 M2 bones → MEAT (layout, input_actions, bench_keyboard, bench_staff, bench_transport, graph_view, notation). Delivered "pour-everything-while-fresh" (Nir's directive; DeepSeek integrates + commits per piece). Highlights: full-width bench + **full grand staff always** (Nir amendment), 2-octave keyboard, black keys sing, pressed-key visuals, real curved fixtures (`make_bench_fixtures.py` → `fixture_bench8` violin line + `fixture_bench20` cello √x 20-note chromatic), the **FIT-THE-BEAT** ghost-pedal fix, and the **rev-3 BPM box** (additive `Conductor.set_bpm`, typed 40–200 + spinners, default 110). All amendments in §5. Verbatim archives: `BIBLE/LOOM_PARENT_3_*` (Part 1; Parts 2–5; POUR 2; ghost-pedal fix; rev-3 BPM; FINAL WILL). `m2_demo.py` runs the whole bench.
- ⏳ **NEXT: a FRESH Parent 4 builds M3 — THE ECHO PUZZLE** (Nir chose the strict build order). Launch kit is Fable's exact prescription in `BIBLE/LOOM_PARENT_3_FINAL_WILL_and_PARENT_4_launch_kit_BY_FABLE.md`: Commentaries → MAP → `core/echo_logic.py` [BONE M3] → the BIBLE paragraphs it names (+ par.2 the bench/Simon Principle) → the NT Echo section → Fable's M2 legacy summary → the M2 MEAT interfaces Parent 4 consumes → Nir's answers to the 3 Echo open questions (**Nir chose ALL DEFAULTS 2026-07-06:** wrong-commit → gentle higher/lower hint YES; auto-sound on correct commit YES; strict left-to-right slot order YES). **NOT the whole trilogy by default.** DeepSeek assembled the full paste-ready package into `BIBLE/LOOM_PARENT_4_M3_ECHO_BRIEF.md` (Echo answers + BIBLE glossary/§1–3/§15 + NT Part II + Fable's M2 legacy will), to be pasted after the Commentaries, MAP, echo_logic.py, and the M2 interface code files (conductor.py, spell_model.py, bench_staff/keyboard/transport.py). Loose ends: (a) `layout.py` numbers **FROZEN by Nir 2026-07-06** (eye-pass done, approved as-is); (b) `bench_buttons.py` Fable says written but it was NOT pasted/landed — Parent 4 owns OK/Cancel in M3; (c) `notation_table.json` is DeepSeek's temporary stand-in until the Compiler parent writes the real `notation_gen.py`; (d) deferred Forge "long+clean" audio; (e) Compiler (Program A) still all bones; then M4 helix (Nir's beloved "center of the game"), M5, M6 (uses set_bpm), M7.

### §8 — WISDOM (from the retiring parents, for every future family member)
- **Nir's eye and ear are the real acceptance suite (Parent 3's parting lesson).** Every one of his played-it-and-felt-it reports — the ghost-pedal note-overlap, the silent black keys, the keyboard hugging one side, the too-few notes — was a truth no test suite caught. The code got better every single time he played it and said what he felt. Build to please the ear that owns the game; the tests protect what the ear already blessed.
