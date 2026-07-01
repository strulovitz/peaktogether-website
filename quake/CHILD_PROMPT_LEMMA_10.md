# QUAKE CHILD PROMPT — lemma_10.room

You are a Quake content child. Write ONE `.room` file for lemma_10. Return ONLY the `.room` file text (in a fenced code block).

## THE .room FORMAT (v1.0)

```
HEADER:
  room <node_id> | kind geometry|equation|text | import <citation> | caption <line>
  final <step#> | ceiling <eq_id> :: <verbatim LaTeX>

GEOMETRY ops: point point_on intersect midpoint foot reflect
  segment line ray parallel perp tangent_at tangent_from bisector
  circle_cp circle_cr circle_3 arc ellipse_foci ellipse_axes
  parabola_fd hyperbola_foci conic_5 polygon polyline series angle

  Attrs: color=NAME heart label=$..$ at=DIR marker=dot @(x,y)
  DIR = N|S|E|W|NE|NW|SE|SW|center

STATION:
  station <n>
    gloss <one sentence>
    color <name> <#hex>
    panel
      <ops>
    text
      <prose with {colorname|words} spans and $math$>
```

## YOUR ROOM — lemma_10

**lemma_10 · DIAGRAM · 2 step-pairs · importance 5 · REUSES Lemma IX figure**

This lemma APPLIES Lemma IX's geometry to physics: the same curve+triangles figure, but now the baseline = TIME, the ordinates = VELOCITY, and the areas = SPACE. The punchline is the famous s ∝ t² (Galileo!) and Cor. 4 gives F ∝ s/t².

```
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I, Lemma X; Plate 2.
caption   The spaces which a body describes from rest under any finite force are, from the very beginning of the motion, in the duplicate ratio of the times.
final     2
ceiling   lem10 :: s \propto t^2 \qquad F \propto \frac{s}{t^2}\;(\text{Cor. }4)

s1 — Time axis AD,AE → timeblue(#1E6FE0); velocity ordinates DB,EC → velgreen(#00A35A) ♥.
s2 — Areas ABD,ACE = the spaces → spacered(#D81B60) ♥; ultimately as t² (by Lem. 9).

colors_used: timeblue, velgreen, spacered
```

### Newton's text (verbatim, 1729 Motte, Book I, Section I, Lemma X):

> The spaces which a body describes by any finite force urging it, whether that force is determined and immutable, or is continually augmented or continually diminished, are in the very beginning of the motion one to the other in the duplicate ratio of the times.
>
> Let the times be represented by the lines AD, AE, and the velocities generated in those times be ordinates DB, EC. The spaces described with these velocities will be as the areas ABD, ACE, described by those ordinates, that is, at the very beginning of the motion (by Lem. 9.) in the duplicate ratio of the times AD, AE.
>
> Cor. 4 And therefore the forces are as the spaces described in the very beginning of the motion directly, and the squares of the times inversly.

### GUIDANCE

This is Lemma IX applied to PHYSICS. The same geometric figure (curve through A, baseline AE, ordinates BD and CE, two triangles ABD and ACE) is reinterpreted:

**Step 1 — Times and Velocities:** Draw the base line AE with two points D and E. AD and AE ARE THE TIMES. The curve rises from A through B to C — this is the velocity curve (imagine a body accelerating). The ordinates DB and EC are the VELOCITIES at those instants. Make {timeblue|the time axis AD, AE} clear in the figure and the {velgreen|velocity ordinates DB, EC} the heart. In the text, explain: "time is the horizontal, velocity is the vertical — the velocity grows because a force is pushing." Relate to Galileo: falling bodies get faster every instant.

**Step 2 — Spaces as Areas:** The triangles ABD and ACE (formed by the base, the ordinate, and the curve) are the SPACES described. By Lemma IX, these areas are in the duplicate ratio of the sides — that is, AD² : AE². But AD and AE are the times! So spaces ∝ times² — the famous s ∝ t². Then Cor. 4 completes the circle: rearrange to get F ∝ s/t² (force ∝ space / time²). The {spacered|areas ABD and ACE — the spaces themselves} are the heart. End with \textit{Q.E.D.}

**Figure layout (reuses Lemma IX's picture, Pl.2):**
- Point A at origin (0,0), baseline AE going right along x-axis
- Curve from A rising upward-right (concave up — acceleration), passing through B (near) and C (farther)
- D and E on the baseline (D closer to A, E farther)
- BD and CE are vertical ordinates (or at a fixed angle) meeting the curve
- Two triangles: ABD (small, near A) and ACE (larger, farther out)

**Design note:** The figure can be VERY SIMILAR to lemma_9's — that's the point. Lemma IX proved the geometric theorem; Lemma X applies it. What changes is the TEXT: the ordinates are now velocities, the areas are spaces, and the meaning is physical. Use the same basic construction (curve, baseline, two ordinates, two triangles) but write the text panels about MOTION and FORCE, not just geometry.

### GOLD EXAMPLE — lemma_9.room (SAME FIGURE!)

lemma_10 reuses the identical geometric picture as lemma_9. Study this example carefully — you can replicate its construction but with the physical reinterpretation:

```
room      lemma_9
kind      geometry
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I, Lemma IX; Plate 2.
caption   The areas of triangles formed by ordinates under a curve are ultimately one to the other in the duplicate ratio of the sides.
final     3
ceiling   lem9 :: \triangle ABD : \triangle ACE \to AD^2 : AE^2

station 1
  gloss   A curve crosses a baseline at A; ordinates drop from two curve points to form two shrinking triangles whose area ratio we seek.
  color   lineblue   #1E6FE0
  color   curvegreen #00A35A
  color   ordorange  #E8770A
  panel
    point    A   @(0,0)    marker=dot label=$A$ at=SW
    point    D   @(1.4,0)  marker=dot label=$D$ at=S
    point    E   @(3.0,0)  marker=dot label=$E$ at=S
    point    B   @(1.4,1.0) marker=dot label=$B$ at=NW
    point    C   @(3.0,2.2) marker=dot label=$C$ at=N
    segment  AE  A E       color=lineblue label=$AE$ at=S
    polyline curve A B C   color=curvegreen label=$ABC$ at=NW
    segment  BD  B D       color=ordorange heart label=$BD$ at=E
    segment  CE  C E       color=ordorange heart label=$CE$ at=E
    polygon  triABD A B D
    polygon  triACE A C E
  text
    A right line {lineblue|$AE$} and a {curvegreen|curve $ABC$} cut each other at the \
    given point $A$. From the curve points $B$ and $C$ we let fall the {ordorange|ordinates \
    $BD$ and $CE$}, drawn at a fixed angle to the base, so that two triangles $\triangle ABD$ \
    and $\triangle ACE$ are formed beneath the curve.

station 2
  gloss   The blow-up: AD and AE produced to fixed distant points d and e, ordinates db, ec drawn parallel, a similar curve Abc, and the tangent Ag cutting all four ordinates.
  color   auxpurple #8E24AA
  color   lineblue   #1E6FE0
  panel
    point    A   @(0,0)    marker=dot label=$A$ at=SW
    point    D   @(1.4,0)  marker=dot label=$D$ at=S
    point    E   @(3.0,0)  marker=dot label=$E$ at=S
    point    d   @(5.5,0)  marker=dot label=$d$ at=S
    point    e   @(8.0,0)  marker=dot label=$e$ at=S
    point    f   @(5.5,2.4) marker=dot label=$f$ at=N
    point    g   @(8.0,3.5) marker=dot label=$g$ at=N
    point    b   @(5.5,2.0) marker=dot label=$b$ at=NW
    point    c   @(8.0,3.1) marker=dot label=$c$ at=N
    segment  base A e      color=lineblue
    ray      Ad  A d       color=auxpurple
    ray      Ae  A e       color=auxpurple
    polyline auxcurve A b c color=auxpurple heart label=$Abc$ at=NW
    segment  db  d f       color=auxpurple label=$db$ at=E
    segment  ec  e g       color=auxpurple label=$ec$ at=E
    tangent_at tag auxcurve at A  color=auxpurple label=$Ag$ at=N
  text
    Here is the same device used in Lemma VII. We {auxpurple|produce $AD$ to the remote point \
    $d$ and $AE$ to $e$} ...

station 3
  gloss   As B,C meet A the angle cAg vanishes, the curvilinear areas collapse onto the triangles Afd and Age, and Lemma V gives the duplicate ratio.
  color   arearred #D81B60
  color   lineblue   #1E6FE0
  panel
    point    A   @(0,0)    marker=dot label=$A$ at=SW
    point    d   @(5.5,0)  marker=dot label=$d$ at=S
    point    e   @(8.0,0)  marker=dot label=$e$ at=S
    point    f   @(5.5,2.4) marker=dot label=$f$ at=NE
    point    g   @(8.0,3.5) marker=dot label=$g$ at=NE
    segment  base A e      color=lineblue
    segment  df  d f       color=arearred
    segment  eg  e g       color=arearred
    polygon  Afd A f d     color=arearred heart label=$Afd$ at=NW
    polygon  Age A g e     color=arearred heart label=$Age$ at=N
  text
    Now hold $Ae$ fixed ... Therefore the areas $\triangle ABD$ and $\triangle ACE$ are \
    ultimately one to the other as $AD^2 : AE^2$. \textit{Q.E.D.}
```

**Note for lemma_10:** You only need 2 stations (not 3). You do NOT need the "blow-up" auxiliary construction (that was lemma_9's own proof). Lemma X simply cites Lemma IX — the geometric theorem is already established. Your 2 stations are: (1) the physical setup — time = baseline, velocity = ordinates; (2) the payoff — spaces = areas, s ∝ t², and F ∝ s/t² from Cor. 4.

## RULES

1. Colors LOCAL per station. Uncolored = BLACK. Never grey.
2. At least one `heart` per station.
3. Every used color declared; every declared color used.
4. Define geometry ops BEFORE referencing them (points before segments/polygons).
5. Text: `{colorname|words}` spans + `$math$`. 4–5 sentences per panel, EDUCATIONAL — teach the physics, not just restate the symbols.
6. `@(x,y)` on point ops = cosmetic layout hint only.
7. Lemma X depends on Lemma IX — mention "by Lemma IX" in the text.
8. End final station with `\textit{Q.E.D.}`
9. `\` at end of line to continue long lines.
10. **The figure REUSES Lemma IX's picture** — same curve+baseline+ordinates+triangles. You do NOT need the blow-up auxiliary from lemma_9 st2/st3. Just the core figure + physical interpretation.
11. Include Cor. 4's F ∝ s/t² in the text of step 2 — it's the bonus prize.

Return ONLY the `.room` file text.
