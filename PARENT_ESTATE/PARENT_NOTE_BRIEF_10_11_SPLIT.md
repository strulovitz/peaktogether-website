# PARENT NOTE — Brief #10 / #11 split and outstanding items

## 1. Brief #10 and #11 should have been ONE child

`render_rich` (Brief #10) exists ONLY to power Understanding Mode (Brief #11).
Splitting them into two children means:

- Child #11 can't test anything until #10's code is committed and pushed
- Twice the context windows, twice the copy-pasting for Nir
- Risk that child #11 doesn't understand the actual behavior of render_rich
  (e.g. cache key format, blur behavior, arc positioning)

These are one feature. Give them to one child next time.

## 2. Brief #10 completion report — missing

Child #10 gave a short "Definition of Done" checklist but never submitted
the full Completion Report the brief's template asked for (files created,
locked signatures, deviations, DeepSeek TODOs). Not blocking, but the
parent should collect it from the child.

## 3. Outstanding engine infrastructure — NOT YET BUILT

Two things every corridor will need forever, still missing:

A) **Ship wall containment** — the ship flies through corridor walls.
   `HubGeometry.inside(point, margin)` already exists and works. The fix
   belongs in hub_builder.py or corridor_builder.py (walls block by
   nature, not by per-demo patch). See PARENT_PROMPT_POST_FLIGHT_ARCHITECTURE.md
   for details.

B) **No plain-text renderer** — every HUD child reinvents a broken text
   escape (`_mt()`). The engine needs `render.draw_plain_text_2d()`.
   See PARENT_PROMPT_POST_FLIGHT_ARCHITECTURE.md for details.

These should be parent-authored patches (not full child briefs) so all
future children benefit without reinventing them.

## 4. Brief #9 combat HUD text bug — still present

The `_mt()` function in combat.py shows raw code instead of readable text.
After the plain-text renderer (item 3B) is built, retire `_mt()` with a
one-line swap to `render_rich`.
