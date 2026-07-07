# PARENT D — Q&A BATCH 1 + NIR'S DECISIONS (July 7–8, 2026, ~1 AM Israel)

> Parent D (Fable) is writing `graphics/terrain.py` + `graphics/totem.py`.
> After absorbing all scriptures he sent his first question batch (Q1–Q7).
> Below: his questions, then Nir's rulings (couriered by DeepSeek). Every taste
> choice is NIR'S; everything else is a verified FACT from the repo. DeepSeek
> gave ZERO aesthetic opinions in the final answers (see the "incident" note at
> the bottom — a flat-shading opinion slipped out earlier and was corrected).

---

## PARENT D'S QUESTIONS (verbatim summary)

- **Q1 — Conductor's arm direction.** Phase 0 = 12 o'clock = world +y is canon. Which way does the arm sweep — clockwise (90°−phase×360°) or counterclockwise (90°+phase×360°)? Must match helix_panel's already-delivered arm.
- **Q2 — Color bands: hard or smooth?** Proposed HARD discrete bands at fixed absolute z thresholds (same across scenes so shoreline is always A440). Proposed: deep water z<−1.0, shallow −1.0≤z<0, lowland 0≤z<1.1, upland 1.1≤z<2.2, peak z≥2.2.
- **Q3 — Flat shading approach.** Proposed duplicate verts per triangle + baked per-face Lambert into vertex colors, trivial shader.
- **Q4 — Water plane.** Proposed a second small VBO inside TerrainMesh — translucent quad at z=0. Asked: is a second static VBO acceptable, or must everything be one buffer?
- **Q5 — Ring pulses.** Proposed rings brighten at each beat (phase k/n), on the terrain panel. Confirm wanted, and only rings ≤ hearing_radius drawn.
- **Q6 — HDR bloom budget for the totem group.** May the hearing circle, rings, and arm also modestly exceed the 0.80 bloom threshold at strikes, or should ONLY the helix model bloom?
- **Q7 — ground_z wiring + draped vs flat.** Confirm DeepSeek stitches `terrain.height_at(totem.x,totem.y)` → `ground_z` into `totem_visual.draw`. Proposed FLAT disks at z=ground_z+ε (not draped).

---

## NIR'S DECISIONS / ANSWERS (couriered by DeepSeek)

**A1 — Conductor's arm direction ✅ (verified fact)**
`helix_panel.py` line 253: `a = math.radians(90.0 - measure_phase * 360.0)`.
Use exactly `angle = 90° − measure_phase × 360°` (CLOCKWISE viewed from above;
phase 0 → 12 o'clock = world +y). Match verbatim so both panels' arms agree.

**A2 — Color bands: HARD (Nir's decision) 🗺️**
Use **hard, discrete color bands** — sharp thresholds, NOT smooth gradients — so
the crisp band edges paint the level curves (the calculus we teach). Config
provides the 5 palette colors. Parent D's proposed thresholds are a fine starting
point; adjust for good spread.

**A3 — Shading: GOURAUD (Nir's decision) 🎨**
Nir wants **GOURAUD shading** (smoothly interpolated per-vertex lighting), NOT
flat. (Fable's plan reconciles this beautifully: Gouraud lighting per-vertex +
hard color bands per-fragment → smooth shading AND pixel-sharp level curves.)

**A4 — NO water plane (Nir's decision) 💙**
Do **not** draw a flat sea-level water sheet. The region below z=0 is part of the
**same terrain mesh**, colored with **hard blue bands that get darker with depth**
(light blue near z=0 → dark blue in deep valleys), using
`COLOR_SHALLOW=(50,140,230)` / `COLOR_DEEP_WATER=(20,60,140)`. This is a calculus
surface, NOT a sea simulation. No second water VBO needed. (Fact for the record:
a second STATIC VBO would have been contract-legal — "Static VBO" means built once
per scene, not literally one buffer — but Nir's design removes the need entirely.)

**A5 — NO pulsing on the left terrain panel (Nir's decision) 🟢**
On the LEFT Cartesian terrain view, the rhythm rings are **calm, steady, static
circles** — no blinking/flashing (it distracts the user). The visual rhythm
feedback lives on the RIGHT helix panel. Fact: draw only rings inside the hearing
radius (RING_WIDTH=0.8, default HEARING_R=2.5 → 3 rings at 0.8, 1.6, 2.4).

**A6 — Gentle glow on ALL totem parts (Nir's decision) 🌟**
The helix, hearing circle, rings, and arm may **all glow gently** (bloom threshold
= 0.80), but softly — every shape must stay clearly readable (the helix still
looks like a helix, never a blinding white cylinder). Keep peaks modest so the
cores don't blow out to pure white.

**A7 — DRAPED ground rings (Nir's decision) 🫓 + EXPLICIT CONTRACT PERMISSION 🔓**
The hearing circle and rhythm rings must **hug the terrain surface** (draped),
following every bump/dip — never flat disks that float or clip into hillsides.
Extra plumbing is welcome.

Technical fact: draping means the totem must sample terrain height all around each
ring. The Gita's frozen `TotemVisual.draw(self, view_proj, totem_state, ground_z,
measure_phase)` passes only a single `ground_z`, not the terrain function — so
Parent D needs terrain-height access around the whole circle (e.g. DeepSeek passes
`terrain.height_at` into `draw`, or the terrain provides sampled ring points).

🔓 **EXPLICIT MESSAGE FROM NIR:** *"I have NO problem with you guys unfreezing
contracts and changing scripture for this. Do whatever it takes to get the draped
rings right — change the signature, amend the Gita, whatever is cleanest. You have
my full blessing."* So Parent D should pick the cleanest approach, raise a
`# CONTRACT-ISSUE` documenting the change, and DeepSeek will update the scripture +
wire up whatever he chooses.

---

## FABLE'S CONFIRMED DESIGN (his own good-night summary, saved verbatim)

- Gouraud lighting per-vertex + hard bands chosen per-fragment → smooth shading
  AND pixel-sharp level curves, both at full quality.
- Water as part of the same mesh, blue bands darkening with depth.
- Arm matching helix_panel verbatim; calm static rings; gentle glow on all totem
  parts; draped rings via the blessed contract amendment.
- Delivery order tomorrow: `terrain.py` complete + the `terrain.vert`/`terrain.frag`
  GLSL he owns + numbered remarks for DeepSeek; then `totem.py` after that.
- Tomorrow Nir just writes **"continue"** (no re-paste needed) — Fable has it all
  in context.

---

## ⚠️ THE INCIDENT (documented so it never repeats)

1. **DeepSeek's chat error:** in the FIRST draft of the answers, DeepSeek wrote
   "A3 — flat shading, no objection." Nir had NOT asked for flat; he wants GOURAUD.
   This was DeepSeek steering a design choice — forbidden. It was ONLY in chat,
   never saved/pushed. Corrected above.
2. **Repo contamination (pre-existing, committed earlier):** the Parent D launch
   doc `HAND-OFF-PROMPT-FROM-FABLE-PARENT-C.md` §5 (lines ~154–155) contains a
   DeepSeek OPINION: *"Per-vertex hypsometric color (Gouraud) reads well; a simple
   directional term is fine too."* The DeepSeek info block is supposed to be
   FACTS ONLY. **TODO tomorrow (with Nir's approval): remove that opinion sentence,
   keep only verbatim config facts.** NOT done yet — Nir stopped the edit tonight.
3. **Lesson (locked):** DeepSeek gives VERIFIED FACTS ONLY. Every taste/design
   choice goes to NIR to decide — DeepSeek never decides aesthetics, never says
   "reads well / looks good / is fine." Parents are smarter coders; Nir is the
   designer.

---

## WHY WE STOPPED TONIGHT

Communication problems: the provider truncated Fable's reply TWICE mid-answer
(long messages choke). It was almost 1 AM in Israel. Nir chose to stop and resume
tomorrow from this exact point. Nothing is lost — Fable holds the full design in
context; Nir writes "continue" tomorrow and Fable delivers `terrain.py`.
