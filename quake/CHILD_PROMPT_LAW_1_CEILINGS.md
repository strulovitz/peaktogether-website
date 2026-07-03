# CHILD PROMPT — law_1: Write ceiling equations

Your only task: replace the single `ceiling` line in this `.room` file with one ceiling equation per station (4 stations = 4 equations). Each equation should capture the key physical/mathematical idea of that specific step, in LaTeX. Do NOT change any other part of the file — not the stations, not the colors, not the text, not the phrases.

Here is the current file:

```
room      law_1
kind      text
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Axioms, or Laws of Motion, Law I.
caption   Law I -- Every body perseveres in its state of rest, or of uniform motion in a right line, unless it is compelled to change that state by forces impressed.
final     4
ceiling   eq0 :: \text{no force} \Rightarrow \text{no change of motion}

station 1
  gloss   The statement of the first law: rest, uniform motion, and impressed forces.
  color   restblue    #1E6FE0
  color   motiongreen #00A35A
  color   forceorange #E8770A
  panel
    phrase  restblue    "a state of rest"
    phrase  motiongreen "uniform motion in a right line"
    phrase  forceorange "forces impress'd" heart
  text
    Every body perseveres in its {restblue|state of rest}, or of {motiongreen|uniform motion in a right line}, unless compelled to change that state by {forceorange|forces impress'd}.

station 2
  gloss   The spinning top persists in rotation until the air retards it.
  color   topblue #1E6FE0
  color   dragred #D81B60
  panel
    phrase  topblue "a spinning top" heart
    phrase  dragred "retarded by the air"
  text
    {topblue|A top} does not cease its rotation, otherwise than as it is {dragred|retarded by the air}.

station 3
  gloss   Planets and comets move freely in space for vast times.
  color   planetpurple #8E24AA
  color   freeteal     #00897B
  panel
    phrase  planetpurple "the planets and comets" heart
    phrase  freeteal     "more free spaces"
  text
    The greater bodies of {planetpurple|the planets and comets}, meeting less resistance in {freeteal|more free spaces}, preserve their motions for a much longer time.

station 4
  gloss   Projectiles preserve their motion except as hindered by air resistance and gravity.
  color   projblue    #1E6FE0
  color   dragred     #D81B60
  color   gravorange  #E8770A
  panel
    phrase  projblue    "projectiles" heart
    phrase  dragred     "the resistance of the air"
    phrase  gravorange  "gravity"
  text
    {projblue|Projectiles} persevere, so far as not {dragred|retarded by the resistance of the air}, or impell'd downwards by {gravorange|gravity}.
```

Give me ONLY the new `ceiling` lines, one per station. Format: `ceiling   eq0 :: <LaTeX>`, `ceiling   eq1 :: <LaTeX>`, etc.
