# QUAKE CHILD PROMPT — prop_15.room

You are a Quake content child. Write ONE `.room` file for prop_15. Return ONLY the `.room` file text (in a fenced code block).

## THE .room FORMAT (v1.0) — EQUATION ROOM

This is an EQUATION room. The panel uses `term` and `layout` ops instead of geometry.

```
HEADER:
  room <node_id>
  kind equation
  import <citation>
  caption <line>
  final <step#>
  ceiling <eq_id> :: <verbatim LaTeX>

STATION:
  station <n>
    gloss <one sentence>
    color <name> <#hex>
    panel
      term    <colorname>   $<LaTeX_expression>$   (optionally: heart stabilo=#hex)
      layout  $<LaTeX with {colorname|text} spans>$
    text
      <prose with {colorname|words} and $math$>
```

`term` declares a colored term with its LaTeX. `heart` marks the current step's Stabilo highlight. `stabilo=#hex` is the highlight color (optional, light pastel).

`layout` arranges the terms into a rendered equation using `{colorname|text}` spans.

## GOLD EXAMPLE — law_2.room (working EQUATION room!)

```
room      law_2
kind      equation
import    Newton, Principia, Axioms or Laws of Motion, Law II, p.19 (Motte trans., 1729)
caption   The alteration of motion is proportional to, and directed along, the impressed force.
final     2
ceiling   eq0 :: \Delta(\text{motion}) \propto \mathbf{F}
ceiling   eq1 :: \Delta(\text{motion}) \parallel \mathbf{F}

station 1
  gloss   The alteration of motion is proportional to the motive force impressed.
  color   motionblue   #1E6FE0
  color   forceorange  #E8770A
  panel
    term    motionblue   $\Delta(\text{motion})$   heart stabilo=#BBD7FB
    term    forceorange  $\mathbf{F}$
    layout  $\,{motionblue|\Delta(\text{motion})}\;\propto\;{forceorange|\mathbf{F}}\,$
  text
    The Law sets {motionblue|the alteration of motion} in strict proportion to \
    {forceorange|the motive force impressed}. As Newton explains, if any force \
    generates a motion, then {forceorange|a double force} will generate \
    {motionblue|double the motion}. The {motionblue|change $\Delta(\text{motion})$} \
    scales exactly with the impressed {forceorange|$\mathbf{F}$}.

station 2
  gloss   The change of motion is made in the direction of the right line in which the force is impressed.
  color   motionblue   #1E6FE0
  color   forceorange  #E8770A
  color   dirgreen     #00A35A
  panel
    term    motionblue   $\Delta(\text{motion})$
    term    forceorange  $\mathbf{F}$
    term    dirgreen     $\parallel\;\text{(right line of }\mathbf{F}\text{)}$   heart stabilo=#B7E9CF
    layout  $\,{motionblue|\Delta(\text{motion})}\;{dirgreen|\parallel}\;{forceorange|\mathbf{F}}\,$
  text
    The {motionblue|change of motion} is made {dirgreen|in the direction of the right line} \
    in which {forceorange|the force} is impressed. Thus {motionblue|$\Delta(\text{motion})$} \
    runs {dirgreen|parallel} to {forceorange|$\mathbf{F}$}.
```

## YOUR ROOM — prop_15

**prop_15 · EQUATION · 2 step-pairs · importance 5 · ★ KEPLER'S THIRD LAW ★ · no printed figure**

THE GRAND FINALE. Prop. XI proved inverse-square from ellipses. Prop. XV now proves Kepler's Third Law: the square of the period is proportional to the cube of the semi-major axis (T² ∝ a³). This is an EQUATION room — no geometric construction, just a colored equation and matching explanation.

```
room      prop_15
kind      equation
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section III, Proposition XV; (no printed figure).
caption   The periodic times in ellipses are in the sesquiplicate ratio of the greater axes — Kepler's Third Law.
final     2
ceiling   prop15 :: T^2 \propto a^3
ceiling   prop15b :: \text{(Kepler III)}

s1 — Equation-as-figure: T² → timeblue(#1E6FE0); a³ → axisorange(#E8770A) ♥; sesquiplicate ratio → ratiopurple(#8E24AA).
s2 — Derivation: lesser axis as mean proportional → meangreen(#00A35A) ♥; subduct subduplicate ratio of latus rectum → leaves sesquiplicate ratio.

colors_used: timeblue, axisorange, ratiopurple, meangreen
```

### Newton's text (paraphrased from Motte, Prop. XV):

> The periodic times in ellipses are in the sesquiplicate ratio of the greater axes.
>
> For the periodic time is as the area divided by the areal velocity. By Prop. I the areal velocity is constant. The total area of an ellipse is πab (where a is the semi-major axis and b the semi-minor). By Cor. Prop. 14 the lesser axis b is the mean proportional between the greater axis a and the latus rectum L, i.e. b² = aL. The law of force being 1/SP² (Prop. XI), the latus rectum L is in the subduplicate ratio. Subducting, the periodic time T comes out proportional to a^(3/2), i.e. T² ∝ a³. Q.E.I.

### GUIDANCE

This is Kepler's Crown — T² ∝ a³ — proven from first principles. The proof combines everything: Prop. I (areas ∝ times), Prop. XI (inverse-square from ellipses), Prop. XIV (b² = aL), and the sesquiplicate ratio (3/2 power).

**Station 1 — The Law Itself:** The equation-as-figure. `term timeblue` for T² (the periodic time squared), `term axisorange` for a³ (the cube of the greater axis) with `heart`. `term ratiopurple` for the sesquiplicate ratio (3/2 power). Layout: `{timeblue|T^2} \propto {axisorange|a^3}`. Text: explain what Kepler discovered — the farther a planet is from the Sun, the longer its year, and the relationship is exact: period² ∝ distance³. Newton now PROVES this from his inverse-square law. In Newton's own words: "the periodic times in ellipses are in the sesquiplicate ratio of their greater axes."

**Station 2 — The Derivation:** `term meangreen` for b² = aL (the lesser axis as mean proportional) with `heart`. Layout showing the chain: T ∝ area/areal_velocity → T ∝ πab → substitute b² = aL → T ∝ a^(3/2) → T² ∝ a³. Text: walk through the derivation — the periodic time is the total area (πab) divided by the constant areal velocity. By Cor. Prop. 14, b is the mean proportional between a and L, so b² = aL. Subduct the subduplicate ratio of the latus rectum, and the sesquiplicate ratio of the greater axis remains. Thus T² ∝ a³. Q.E.I.

## RULES

1. Colors local per station. Uncolored = BLACK (never `color=black`).
2. At least one `heart` per station (on a `term` op, with optional `stabilo=#hex` for the highlight color).
3. Every declared color used; every used color declared.
4. `term` declares a colored expression. `layout` arranges terms with `{colorname|text}` spans.
5. Text: `{colorname|words}` spans + `$math$`. 4–5 sentences, EDUCATIONAL.
6. This is the FINALE of Book I Section III. Make the text shine.
7. End final station with `\textit{Q.E.I.}`
8. `\` at end of line for long text lines.

Return ONLY the `.room` file text.
