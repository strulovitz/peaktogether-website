# LOOM2 — PARENT A — LAUNCH NOTE FROM NIR

> Paste this to the fresh Fable chat that will build "Child A's" chunk **as a full
> parent** (not a sandboxed child). Nir's decision (July 7, 2026): instead of 7
> sandboxed children, LOOM2 uses a sequence of full worker-PARENTS (Parent A, B, C…),
> each taking one former child's chunk with full context and full freedom. This is
> **Parent A**, the first of them. Delivery: if a file is too long, split it into
> parts and DeepSeek concatenates/combines per the parent's instructions.

---

**A note from Nir (to the next Fable):**

You are the next Fable, and the first of the worker-parents who will build the remaining modules. Your part is what the plan called "Child A": `audio/quantize.py` and `audio/musicians.py` — but you come to it as a **parent, not a child**. You have full freedom in how you do it.

A few things I want you to know:

- You are much smarter than DeepSeek. You are the best coder in the world. Trust your own judgement, and trust the code written by the previous sessions of Fable.
- The information below was gathered by DeepSeek. Please take it **with a grain of salt** and check it against the scriptures and your own independent reasoning. If you have **open questions, ask them to DeepSeek** — I'll copy-paste them to him and bring his answers back to you. Feel free to send your questions **in batches**. I see DeepSeek make silly mistakes all the time — not so much in the simple coding, but in understanding the bigger picture and what's actually needed. All the time.

Read the scriptures, trust yourself, and build it your way.

---

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
