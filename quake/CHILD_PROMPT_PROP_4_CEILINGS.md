# CHILD PROMPT — prop_4: Fix ceiling equations

Your only task: replace the single `ceiling` line in this `.room` file with one ceiling equation per station (2 stations = 2 equations). Each equation should capture the key mathematical result of that specific step, in LaTeX. Do NOT change any other part of the file — not the stations, not the colors, not the text, not the layout.

Here is the current file:

```
room      prop_4
kind      equation
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section II, Proposition IV.
caption   The centripetal force of a body moving uniformly in a circle is as the square of the speed divided by the radius.
final     2
ceiling   eq0 :: F \propto \dfrac{v^2}{r}

station 1
  gloss   The centripetal pull grows with the square of the speed and is inversely as the distance from the centre.
  color   velblue   #1E6FE0
  color   radgreen  #00A35A
  color   forceorange #E8770A
  panel
    term  velblue   $v^2$  heart
    term  forceorange  $F$
    term  radgreen  $r$
  text
    The {forceorange|pull toward the centre} is as the {velblue|square of the speed} divided by the {radgreen|distance from the centre}.

station 2
  gloss   A small circular arc swept in equal time; the versed sine gives the force.
  color   velblue   #1E6FE0
  color   radgreen  #00A35A
  panel
    term  velblue   $v^2$  heart
    term  radgreen  $r$
  text
    In a small {velblue|arc of the circle} the {radgreen|radius} leads to the {velblue|versed sine}, which gives the force by Cor.~4 Prop.~1 and Lem.~7.
```

Give me ONLY the new `ceiling` lines, one per station. Format: `ceiling   eq0 :: <LaTeX>` and `ceiling   eq1 :: <LaTeX>`.
