# PARENT NOTE — Brief #10 / #11 should be the same child

`render_rich` (Brief #10) was built specifically to power Understanding Mode
(Brief #11). They are one feature split across two children.

Giving Brief #11 to the SAME chat that built Brief #10 means:

- The child already knows `render_rich`'s exact behavior (cache keys, blur
  behavior, arc positioning, how \n stacking works)
- No need to re-explain everything in a new brief
- One completion report instead of two
- Less copy-pasting for Nir

Recommendation: continue the existing Brief #10 chat with Brief #11.
