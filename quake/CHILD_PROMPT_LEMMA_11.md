# QUAKE CHILD PROMPT — lemma_11.room

You are a Quake content child. Write ONE `.room` file for lemma_11. Return ONLY the `.room` file text (in a fenced code block).

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

## YOUR ROOM — lemma_11

**lemma_11 · DIAGRAM · 3 step-pairs · Pl.2 Fig.4 · ★ IMPORTANCE 5 ★**

This is THE curvature lemma. The payoff: the "subtense of the angle of contact" (how fast the curve peels away from its tangent as you move a small distance AB along the curve) goes as the SQUARE of the arc length. BD ∝ AB² — a quadratic departure, the universal signature of smooth finite curvature. This is the geometric foundation for all of Newton's later force/curvature reasoning (prop_1, prop_6, prop_11).

```
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I, Lemma XI; Plate 2, Fig. 4.
caption   The evanescent subtense of the angle of contact, in all curves of finite curvature, is ultimately in the duplicate ratio of the subtense of the conterminate arc.
final     3
ceiling   lem11 :: BD \propto AB^{2} \;(\text{ultimately})

s1 — Curve at A with tangent AD → tanblue(#1E6FE0) ♥; chord/arc AB → arcgreen(#00A35A).
s2 — Subtense BD ⟂ AD → subred(#D81B60) ♥; foot on tangent; auxiliaries BG ⟂ AB, AG → auxpurple(#8E24AA), ultimate intersection J.
s3 — Conterminate-arc subtense; the relation AB² = AG·BD → relorange(#E8770A) ♥ ⇒ subtense as duplicate ratio of arc-subtense.

colors_used: tanblue, arcgreen, subred, auxpurple, relorange
```

### Newton's text (verbatim, 1729 Motte, Book I, Section I, Lemma XI):

> The evanescent subtense of the angle of contact, in all curves which at the point of contact here have a finite curvature, is ultimately in the duplicate ratio of the subtense of the conterminate arc. Pl. 2. Fig 4.
>
> Case 1. Let AB be that arc, AD its tangent, BD the subtense of the angle of contact perpendicular on the tangent, AB the subtense of the arc. Draw BG perpendicular to the subtense AB, and AG to the tangent AD, meeting in G; then let the points D, B and G approach to the points d, b and g, and suppose J to be the ultimate intersection of the lines BG, AG, when the points D, B, have come to A. It is evident that the distance GJ may be less than any assignable. But (from the nature of the circles passing through the points A, B, G; A, b, g) AB² = AG × BD, and Ab² = Ag × bd; and therefore the ratio of AB² to Ab² is compounded of the ratio's of AG to Ag, and of BD to bd. But because GJ may be assumed of less length than any assignable, the ratio of AG to Ag may be such as to differ from the ratio of equality by less than any assignable difference; and therefore the ratio of AB² to Ab² may be such as to differ from the ratio of BD to bd by less than any assignable difference. Therefore by Lem. 1, the ultimate ratio of AB² to Ab² is the same with the ultimate ratio of BD to bd. Q.E.D.

### GUIDANCE

This lemma is the SEQUEL to Lemmas VI and VII — it answers: *how fast* does the curve peel away from its tangent? Lemma VI said the angle BAD vanishes. Lemma VII said arc = chord = tangent in the limit. Lemma XI now gives the QUANTITATIVE answer: BD ∝ AB².

**The figure (Pl.2 Fig.4):** A smooth curve through A. The tangent AD extends to the right of A. Pick a point B on the curve (not far from A). Draw AB (the chord/arc). Draw BD perpendicular to the tangent AD — this is the "subtense of the angle of contact" (how far the curve has risen above the tangent at distance ~AB). Then the auxiliary construction: draw BG perpendicular to AB, and AG perpendicular to AD (so G is above and to the right of A). The clever part: points A, B, G lie on a circle (since ∠ABG and ∠AGB = 90°, this is a right triangle inscribed in a circle with diameter AG). From circle chord properties you get AB² = AG × BD.

Newton then shrinks everything (B→A, D→A, G→A) and notes that the intersection point J of the lines BG and AG approaches A, and GJ becomes arbitrarily small → AG/Ag → 1. Therefore AB²/Ab² ultimately equals BD/bd.

**Step 1 — Curve and Tangent:** Draw the smooth curve through A with tangent AD going right. Place a point B on the curve near A. Draw the chord/arc AB. The {tanblue|tangent AD} is the heart — this is the "flat" direction at A against which everything is measured. The {arcgreen|arc AB} shows the distance along the curve. In the text panel, introduce the question: "as B slides toward A, the gap between curve and tangent shrinks — but HOW FAST? By what power of AB does it vanish?"

**Step 2 — The Subtense and the Circle:** Draw BD perpendicular to AD (at B, dropped to the tangent). This {subred|subtense BD — the measure of departure from the tangent} is the heart. Then the auxiliary: BG ⟂ AB, AG ⟂ AD, meeting at G. Mark the intersection J where BG and AG meet. The {auxpurple|auxiliary circle through A,B,G} reveals the key relation: because A,B,G form a right triangle (G is the intersection of two perpendiculars), they lie on a circle with AG as diameter. Then AB² = AG × BD (a circle chord theorem). Explain each piece in the text: BD measures how far the curve has peeled away, BG and AG construct the circle that traps the ratio.

**Step 3 — The Payoff:** As B→A, the point G slides down toward A, and J (the intersection of BG and AG) approaches A faster than G does, so GJ vanishes → AG/Ag → 1. Therefore the AB²/Ab² ratio ultimately equals the BD/bd ratio by Lemma I. The {relorange|relation AB² = AG·BD} is the heart: plug in AG≈Ag and you get BD ∝ AB² — the duplicate ratio. End with Q.E.D. In the text: "so the curvature is quadratic — whether the curve is a circle, a parabola, or any smooth bend, the gap between it and its tangent grows as the square of the distance travelled along it."

**Figure layout tips:**
- A at origin (0,0), the curve goes upward from A (gentle concave-up arc)
- Tangent AD goes horizontal-right from A
- B on the curve, slightly up and right of A
- BD vertical (or at a fixed angle), dropping from B to tangent line
- G is above-right — found by BG ⟂ AB and AG ⟂ AD intersecting
- A, B, G should look like they belong to a circle
- Put the auxiliary intersection point J where BG and AG cross

### GOLD EXAMPLE — lemma_6.room (vanishing angle, same figure family!)

Lemma XI builds on the same figure setting as Lemma VI: curve, tangent, chord, and the convergence toward A. Study this for the basic figure skeleton:

```
room      lemma_6
kind      geometry
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I, Lemma VI; Plate 2, Fig. 1.
caption   As a point B on a curve approaches the point of contact A, the angle between the chord AB and the tangent AD is diminished without limit and ultimately vanishes.
final     3
ceiling   eq0 :: B \to A \;\Rightarrow\; \angle BAD \to 0

station 1
  gloss   The arc ACB rising from A, given in position, with smooth continuous curvature.
  color   arcblue  #1E6FE0
  panel
    point    A   @(0,0)    marker=dot label=$A$ at=SW
    point    ptC @(2.4,2.0) color=arcblue label=$C$ at=NW
    point    B   @(5.0,3.0) marker=dot label=$B$ at=NE
    polyline arc A ptC B  color=arcblue heart
  text
    Here is \{arcblue|the arc $ACB$}, a piece of curve fixed in position. ...

station 2
  gloss   The chord AB cutting straight across the arc ...
  color   chordgreen #00A35A
  color   arcblue    #1E6FE0
  panel
    point    A   @(0,0)    marker=dot label=$A$ at=SW
    point    ptC @(2.4,2.0) color=arcblue label=$C$ at=NW
    point    B   @(5.0,3.0) marker=dot label=$B$ at=NE
    polyline arc A ptC B  color=arcblue
    segment chordAB A B   color=chordgreen heart
  text
    Now join $A$ to $B$ by \{chordgreen|the straight chord $AB$} ...

station 3
  gloss   The tangent AD grazes the curve at A; the angle BAD shrinks to zero ...
  color   tanorange  #E8770A
  color   chordgreen #00A35A
  color   anglered   #D81B60
  color   arcblue    #1E6FE0
  panel
    point    A   @(0,0)    marker=dot label=$A$ at=SW
    point    ptC @(2.4,2.0) color=arcblue label=$C$ at=NW
    point    B   @(5.0,3.0) marker=dot label=$B$ at=NE
    point    D   @(5.6,1.4) marker=dot label=$D$ at=E
    polyline arc A ptC B  color=arcblue
    segment chordAB A B   color=chordgreen
    segment tanAD A D     color=tanorange
    angle  BAD B A D      color=anglered heart label=$\angle BAD$ at=E
  text
    Draw \{tanorange|the tangent $AD$}... \textit{Q.E.D.}
```

**For lemma_11:** Extend the lemma_6 figure by adding BD (perpendicular to AD from B), BG (perpendicular to AB), and AG (perpendicular to AD, meeting BG at G). Draw the circle through A,B,G. Label J as the intersection of BG and AG. The text explains the circle-chord theorem AB² = AG·BD and why AG/Ag → 1.

## RULES

1. Colors LOCAL per station. Uncolored = BLACK. Never grey. Never use `color=black` (black is default — omit the color attr).
2. At least one `heart` per station (with the color explicitly set).
3. Every used color declared with `color <name> #<hex>`; every declared color used somewhere in that station.
4. Define point geometry ops BEFORE segments/polygons that reference them.
5. Text: `{colorname|words}` spans + `$math$`. 4–5 sentences per panel, EDUCATIONAL — explain WHY this lemma matters (curvature!), not just restate the proof.
6. `@(x,y)` on point ops = cosmetic layout hint only.
7. Lemma XI depends on Lemma I and Lemma VII — mention "by Lemma I" or "as in Lemma VII" in the text.
8. End final station with `\textit{Q.E.D.}`
9. `\` at end of line to continue long lines.
10. The figure is Pl.2 Fig.4: curve + tangent + subtense + auxiliary circle. Build it carefully — this is a physically deep result.

Return ONLY the `.room` file text.
