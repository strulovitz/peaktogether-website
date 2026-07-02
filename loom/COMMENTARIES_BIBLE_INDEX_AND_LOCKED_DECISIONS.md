# LOOM BIBLE — THE COMMENTARIES (catalog · locked decisions · amendment trail)

> Nicknamed **"the Commentaries"** (after the Quake project's document of the same purpose) — the small, maintained guide to the larger LOOM scripture. Maintained by **DeepSeek**. Current as of **July 2, 2026**. This is the ONE digest every new Opus "parent" chat should receive in full, alongside the scriptures it needs. It is **not** the scripture — it is the **map** of it: what exists, what is frozen, what has been amended.

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

---

## §6 — OPEN QUESTIONS / ENGINEERING ITEMS (assigned to DeepSeek, none block Nir)

None require a Nir decision right now. Engineering items for DeepSeek's build-time test loop (NOT blockers for further design docs):
1. **M0 spike** — MP3 decode reliability + trigger latency on Nir's Windows PC (target ≤30 ms; fallback OGG/WAV pre-approved).
2. **`library_profile.json`** — decode the meaning of the Philharmonia filename numeric token + the variant-preference ranking; confirm/amend the "safe instrument roster" (flute, clarinet, oboe, cello, violin, french-horn, trumpet).
3. Final **scrub tuning constants** (`scrub_tuning.json`) — tuned by ear with Nir.
4. **pygame vs pygame-ce** (or fallback) — decided by M0/M1 evidence, reported back to confirm/amend BIBLE §14.

---

## §7 — CURRENT FRONTIER (July 2, 2026)

- ✅ Source book read + cleaned into `loom/book/`; Fable's summaries + master summary saved.
- ✅ **The full scripture trilogy is DONE** (BIBLE v1.1 + New Testament v1.0 + Apocrypha v1.0), all saved verbatim + pushed.
- ✅ This Commentaries + the WORKFLOW written.
- ⏳ **NEXT (build phase, when Nir is ready):** (1) DeepSeek runs M0; (2) open Parent A for Compiler module specs; (3) open Parent B for Player core; (4) optionally test-drive the Story Weaver prompt on the Square Root Wikipedia page (needs no code).
- 🧵 Nir's immediate plan after this: **restart OpenCode (fresh DeepSeek), then start the BIBLE for ANOTHER game** while Claude Fable access lasts (politically fragile — front-load doctrine).
