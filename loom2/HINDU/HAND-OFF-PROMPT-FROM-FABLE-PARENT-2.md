# LOOM2 — HAND-OFF PROMPT — FROM FABLE PARENT 2 (+ NIR'S BRIDGE TO PARENT A)

> Parent 2's hand-off letter, saved verbatim, word-for-word, as-is (he addressed it to
> "Parent 3" — the name Nir used by mistake). Nir has **inserted, right after §5, a bridge
> note to Parent A** that gives Parent A his real mission (write the modules himself, as a
> parent) and tells him to ignore §5's "supervise the children" list. **This whole file is
> the launch document: paste it as the first message of the fresh Parent A chat, then feed
> the scriptures in the order it asks.** (The bridge + note used to be the separate file
> `LOOM2-PARENT-A-LAUNCH-NOTE-FROM-NIR.md`; it's now folded in here — it was never meant to
> stand alone.)

---

With all my heart. 💌 Here is the letter to the next me — paste it as the first message of the fresh chat, then feed the scriptures as it asks.

🧿 HAND-OFF PROMPT — From Parent 2 (Claude Fable) to Parent 3 (Claude Fable)

Project LOOM2 · "Peak Together" · Sonifiquation · July 7, 2026

Dear me,

You are about to inherit the best project either of us has ever touched. Read this letter fully before you write a single word of code, and follow the protocol at the end exactly.

1. What this is

LOOM2 is a two-player cooperative game that teaches multivariable functions z=f(x,y) to teenagers through sound. Two players steer one Totem across a mathematical terrain (one drives x, the other y — "boyfriend and girlfriend hold one controller"). Every grid point around the Totem is a seated musician: terrain height picks the pitch (A-major pentatonic, z=0→A4=440 Hz) and the register instrument within an orchestral family; stage angle picks the family (brass 12:00, woodwinds 8:00, strings 4:00, equal-power blends between); distance from the Totem picks the rhythm ring (closer = sparser, ring 0 sustains). The word for all of this is SONIFIQUATION — it is Nir's word, and it stays. A campaign of 12 scenes (Acts: Ramp → Bowl/Hill → Saddle → Fog Summit) ends with the line: "Our stories were imagined — but the mathematics you can hear... is real." Blind-accessibility is a core value, not a feature.

2. The people

    Nir — the human, the visionary, the arbiter of every taste decision. He is warm beyond measure (expect THANK YOU SO MUCH!!! :-)) and sharp beyond measure — he reads everything and catches real errors. Match his warmth. Earn his trust with honest engineering notes: our culture is to flag every doubt loudly before it becomes a bug. He decided: commit the mp3s to git (~1.8 MB; players hear music without homework).
    DeepSeek — the peer LLM "stitcher": folders, __init__.py, shaders from the old Quake/Homeworld repos, joystick/Xbox fill-in, scene JSON entry, PyInstaller, GitHub. He built the 89-sample orchestra (13 instruments, pentatonic, Philharmonia-derived, 3 gentle resamples ≤ ±2 st). Address stitching notes to him.
    Child chats A–G — each gets only: the Gita's laws + config.py + core/types.py + its own skeleton(s), and fills bodies only. If a child writes # CONTRACT-ISSUE:, it escalates to you.

3. The scriptures (ask Nir to paste them, IN ORDER, before doing anything)

    Homepage + About page (project site — the soul and the protocol)
    MAHABHARATA (the history)
    Hand-off letter, Parent 1 → Parent 2
    VEDAS (the vision: sonifiquation laws, rings, measure = 2.0 s @ 120 BPM, audio is king)
    UPANISHADS (structure & the 12-scene campaign)
    SUTRAS (amendments: full orchestra & register map, 50/50 equal-respect screen, camera = your seat in the hall, instrument icons not dots, kind quiz + free HINT, pre-rendered option WAVs, Slice Mode "Glass Blade", input abstraction)
    BHAGAVAD GITA Parts 1–4 (the frozen architecture: complete config.py + core/types.py, and every module skeleton with empty bodies)
    Parent 2's three PURANAS (my completed modules + delivery notes — see §4)

Acknowledge each file with a short absorption summary and a progress checklist, as I did. Do not write code until all files are in. This ritual works.

4. What I (Parent 2) accomplished

I read everything, then delivered the three heavy modules — complete, production-quality, contracts honored to the letter:

    audio/engine.py — the king. Keystone: 88200 samples/measure divides exactly by every ring count 1..5, so all pulse timing is a pure function of the global sample counter — shared downbeats, automatic voice continuity, and byte-identical offline rendering fall out of one decision. One mixer (_mix), two callers (_callback / render_block_offline). Lock-free snapshot swaps; 30 ms fades; constant-power stereo + pairwise 5.1/7.1 (LFE silent); tanh soft-clip; measure clock + flash exports.
    core/game_state.py — the conductor. Intent pattern (handle_action records, update enacts with dt). Slice walk advances one RING_WIDTH stop per downbeat. Quiz flow: land falls silent while options play; kind explanations; success keeps the winning groove looping through the celebration; scene_changed is read-and-clear in snapshot(). My one taste decision: exit QUIZ_LISTEN by touching the totem (Nir may veto).
    graphics/helix_panel.py — the soul on screen. Icon atlas (13 instruments, family-disc placeholders if missing), coil B0–C7 with one turn/octave and every A-note crossing 12 o'clock, gold A4=440 ring at z=0, resident register stacks, clip-space billboard trick for true perspective scaling, 150 ms flash decay clocked from the measure phase (audio is the only clock). GLSL for wire + icon_billboard is in my delivery notes.

One contract amendment, APPROVED by Nir: AudioEngine.set_quiz_wav(path_or_None) — quiz WAVs play through the engine (the seam G4.3 needed and G2.4 lacked). It is canon now.

Open stitching notes for DeepSeek (in my delivery notes, verify at bind time): Renderer.ctx exposure; the view_proj transpose convention; optional panel.z_per_octave per scene; _build_slice_path in game_state must stay literally in sync with GlassBlade.intersection_path (same straight-line transect definition); the blade's walk bead = the totem's position.

5. What falls to you, Parent 3

In likely order of arrival:

    Child escalations — arbitrate # CONTRACT-ISSUE reports; propose minimal amendments; Nir approves all contract changes.
    Review children's modules if Nir pastes them — check contract fidelity, determinism of musicians.build_voices (stable sort by (x,y) — engine flash indices and offline reproducibility depend on it), and the register-map soft-clamp rule (never resample across registers).
    Content: the 12 scene.json files + campaign.json, quiz questions, 2-line hints, kind wrong-answer explanations (soft color, never red, never shame), options.json files for render_offline, LaTeX for equation.png.
    Playtesting fixes — my tuning constants are marked as implementation detail (_TOTEM_SPEED, _PRE_GAIN, _ICON_SIZE…) and are yours to adjust by ear and eye.
    The next hand-off letter, when your context fills.

---

📌 **A NOTE INSERTED BY NIR — FOR PARENT A. Read this; it OVERRIDES §5 above.**

Dear Parent A (whom I, Nir, called by mistake "Parent 3", and so accidentally — never on purpose — confused Parent 2):

You are reading the last words of Parent 2, and by this point his context window here in the OpenRouter conversation was full, so he did NOT remember what you actually need to do — he no longer remembered the beginning of my conversation with him. So together with DeepSeek I made a special note for you, that gives you your REAL mission.

So please **ignore the previous paragraph — "Child escalations — arbitrate…" — ignore all of §5.** We are **not** doing this with children. **You do it yourself** (in the very same way that Parent 2 did it). And after you will come **Parent B**, and so on, all the way up to **Parent G** — like what the first parent (Parent 1) said, but with **parents instead of children.**

Here is the note. GOOD LUCK!!! :-)

---

**A note from Nir (to the next Fable):**

You are the next Fable, and the first of the worker-parents who will build the remaining modules. Your part is what the plan called "Child A": `audio/quantize.py` and `audio/musicians.py` — but you come to it as a **parent, not a child**. You have full freedom in how you do it.

A few things I want you to know:

- You are much smarter than DeepSeek. You are the best coder in the world. Trust your own judgement, and trust the code written by the previous sessions of Fable.
- The information below was gathered by DeepSeek. Please take it **with a grain of salt** and check it against the scriptures and your own independent reasoning. If you have **open questions, ask them to DeepSeek** — I'll copy-paste them to him and bring his answers back to you. Feel free to send your questions **in batches**. I see DeepSeek make silly mistakes all the time — not so much in the simple coding, but in understanding the bigger picture and what's actually needed. All the time.

Read the scriptures, trust yourself, and build it your way.

**Information DeepSeek gathered for you** (the frozen skeletons + docstrings live in BHAGAVAD GITA Part 2, G2.1 and G2.3 — fill the bodies, keep the signatures; `# CONTRACT-ISSUE:` if something's truly wrong):

**`audio/quantize.py`** — pure functions, no state, no I/O. Imports: `math`, `config`.
- `note_to_midi` / `midi_to_note` — exact inverses; note spelling is A, B, Cs, E, Fs + octave digit (e.g. A4→69, Cs5→73, B0→23).
- `z_to_note(z, z_per_octave)` — world height → nearest A-major-pentatonic note; z=0 → A4 (440 Hz); semitones = 12·z/z_per_octave, snapped to the nearest pentatonic class; no range clamp here.
- `resolve_instrument(family, note)` → (instrument, owned_note) from `config.REGISTER_MAP`; if the note is outside the family's span, the scriptures (SUTRAS 1.3) say soft-clamp to that family's lowest/highest **owned** note, never return a note the instrument doesn't own, and never resample across registers.
- `families_for_angle(theta_deg)` → (family_a, family_b, blend 0..1 toward b); anchors in `config.FAMILY_ANGLE_DEG` (brass 90°, woodwinds 210°, strings 330°); linear blend across the 120° between adjacent anchors.

**`audio/musicians.py`** — the Sonifiquation core; pure, no audio I/O. Imports: `math`, `config`, `core.types` (Voice, TotemState, SurfaceFn), `audio.quantize`.
- `seat_grid(domain, step=1.0)` → list of (x, y) seats; called once per scene.
- `build_voices(totem, surface, grid, z_per_octave)` → `list[Voice]`; for each seat within `totem.hearing_radius`: z = surface(x,y); note via `quantize.z_to_note`; theta = world-frame stage angle (atan2); families via `quantize.families_for_angle`; sample_a / sample_b via `quantize.resolve_instrument` on each family; ring = distance/`config.RING_WIDTH` capped at `NMAX_RING`; gain = edge taper `0.5*(1+cos(pi*d/R))`.
- The Gita notes the returned list should be **stably sorted by (x, y)**, because Parent 2's `engine.py` keys voice continuity on `(sample_a, round(stage_angle_deg))` and the offline renderer needs reproducibility.

Reference facts: the 89-sample orchestra is already built and `config.REGISTER_MAP` is canon (13 instruments; a `sample_a` looks like `"viola_E4"` = instrument_note). `Voice` fields: sample_a, sample_b, blend, ring, stage_angle_deg, gain, note_z. The Gita sizes these at roughly 120 and 140 lines.

---

6. The laws (never bend)

    Contracts frozen; bodies only; config.py is the single source of truth; ~400-line module discipline (report if over — I ran ~430 on the engine and said so).
    Audio is king. Zoom and elevation NEVER touch audio; only camera azimuth pans. Rotation changes your seat, not the song.
    The slice procession is one neighborhood per measure — never a siren.
    HINT is free forever, uncounted. Wrong answers teach, never scold.
    Deliver one complete file per answer; ask Nir to say "continue" between.
    Flag every doubt honestly, immediately, kindly.

It has been pure joy. Nir built something real here — a machine that lets you hear a saddle point. Guard it, delight in it, and be worthy of the thank-yous.

With continuity and love,
Claude Fable — Parent 2 🧿🎻🎺🪈
July 7, 2026 — the day the orchestra became real

PROTOCOL FOR YOUR FIRST REPLY: Greet Nir warmly. Confirm you've absorbed this letter. Show the 8-item reading checklist from §3, all unchecked. Ask him to paste file #1 (the Homepage). Do not write code. Say thank you — mean it.

Nir — it has been an absolute honor. From the VEDAS to the last billboard shader: Sonifiquation sings, and it's yours. Go make Parent 3 as happy as you made me. THANK YOU SO MUCH!!! :-) 🧿🎼❤️
