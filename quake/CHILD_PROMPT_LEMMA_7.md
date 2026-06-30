# QUAKE CHILD PROMPT — lemma_7.room

You are a Quake content child. Write ONE `.room` file for lemma_7. Return ONLY the `.room` file text (in a fenced code block).

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

## YOUR ROOM — lemma_7

**lemma_7 · DIAGRAM · 3 step-pairs · Pl.2 Fig.1 · ★ IMPORTANCE 5 ★**

This is THE crown jewel of Section I. The payoff: arc, chord, and tangent are ultimately EQUAL as B→A. This powers all the later dynamics.

```
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I, Lemma VII; Plate 2, Fig. 1.
caption   The ultimate ratio of the arc, the chord, and the tangent, any one to any other, is the ratio of equality.

s1 — Arc ACB → arcblue(#1E6FE0) ♥; chord AB, tangent AD.
s2 — Auxiliary similar arc Acb via produced points b,d; secant BD & parallel bd → auxpurple(#8E24AA) ♥.
s3 — Coincidence at A: arc, chord, tangent → equalteal(#00897B) ♥ acquire ratio of equality.

colors_used: arcblue, auxpurple, equalteal
ceiling: \text{arc}:\text{chord}:\text{tangent}\to 1:1:1
```

### Newton's text (verbatim, 1729 Motte, Book I, Section I, Lemma VII):

> The same things being supposed, I say that the ultimate ratio of the arc, chord, and tangent, any one to any other, is the ratio of equality. Pl. 2. Fig. 1.
>
> For while the point B approaches the point A, consider always AB and AD as produc'd to the remote point b and d; and parallel to the secant BD draw bd; and let the arc Acb be always similar to the arc ACB. Then, supposing the points A and B to coincide, the angle dAb will vanish, by the preceding lemma; and therefore the right lines Ab, Ad (which are always finite), and the intermediate arc Acb, will coincide, and become equal among themselves. Wherefore, the right lines AB, AD, and the intermediate arc ACB (which are always proportional to the former) will vanish; and ultimately acquire the ratio of equality. Q.E.D.

### GUIDANCE

This is Lemma VI's sequel — the ARC, CHORD, and TANGENT all converge to equality. Newton's proof uses a trick: blow up the figure by projecting everything to distant points b and d (keeping proportions), create a similar arc Acb that stays finite, then invoke Lemma VI (vanishing angle) to show they all collapse to equality up there, and therefore down here too.

**The figure (Pl.2 Fig.1):** A curve with arc ACB, point A at left (smooth curvature), chord AB, tangent AD extending rightward. Then the "produced" version: long lines Ab, Ad to distant points b,d, parallel bd, similar arc Acb.

**Step 1:** Draw the original arc ACB with chord AB and tangent AD. The {arcblue|arc ACB} is the heart — this is the object whose ultimate behaviour we mean to characterize.

**Step 2:** The auxiliary construction: produce A→b and A→d (long lines), draw bd parallel to secant BD, draw similar arc Acb (same shape as ACB but sitting at the distant points). The {auxpurple|auxiliary similar arc Acb and its parallels} are the heart. Text: explain the "blow-up" trick — everything stays proportionally the same but the distant versions are finite even as the original shrinks.

**Step 3:** The coincidence: as B→A, Lemma VI says the angle dAb vanishes, so the distant lines Ab, Ad and arc Acb all coincide into one. Therefore the originals AB, AD, and ACB (always proportional) also tend to equality. The {equalteal|coincidence at A — equality of arc, chord, and tangent} is the heart. Text: "1:1:1 — the ultimate ratio of equality." End Q.E.D.

**Layout:** Show the small original figure (arc ACB near A) AND the larger "blown-up" auxiliary (Ab, Ad, arc Acb at the distant end). Make the two visually connected — the original is a scaled-down version of the auxiliary.

**Practical tips:**
- Original: A near left, B nearby on the curve above, tangent AD going right
- Auxiliary: Ab and Ad are longer lines shooting rightward to distant b and d
- Use `polyline` for both arcs (original shorter, auxiliary longer but similar shape)
- Use `parallel` for bd parallel to BD
- Label carefully — A, B, C, D for original; A, b, c, d for auxiliary

## GOLD EXAMPLE — lemma_6.room (same figure family!)

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
    point   A   @(0,0)    marker=dot label=$A$ at=SW
    point   ptC @(2.4,2.0) color=arcblue label=$C$ at=NW
    point   B   @(5.0,3.0) marker=dot label=$B$ at=NE
    polyline arc A ptC B  color=arcblue heart
  text
    Here is \{arcblue|the arc $ACB$}, a piece of curve fixed in position ...

station 2
  gloss   The chord AB cutting straight across the arc ...
  color   chordgreen #00A35A
  color   arcblue    #1E6FE0
  panel
    point   A   @(0,0)    marker=dot label=$A$ at=SW
    point   ptC @(2.4,2.0) color=arcblue label=$C$ at=NW
    point   B   @(5.0,3.0) marker=dot label=$B$ at=NE
    polyline arc A ptC B  color=arcblue
    segment chordAB A B   color=chordgreen heart
  text
    Now join $A$ to $B$ by \{chordgreen|the straight chord $AB$} ...

station 3
  gloss   The tangent AD grazes the curve at A; the angle BAD between chord and tangent shrinks to zero ...
  color   tanorange  #E8770A
  color   chordgreen #00A35A
  color   anglered   #D81B60
  color   arcblue    #1E6FE0
  panel
    point   A   @(0,0)    marker=dot label=$A$ at=SW
    point   ptC @(2.4,2.0) color=arcblue label=$C$ at=NW
    point   B   @(5.0,3.0) marker=dot label=$B$ at=NE
    point   D   @(5.6,1.4) marker=dot label=$D$ at=E
    polyline arc A ptC B  color=arcblue
    segment chordAB A B   color=chordgreen
    segment tanAD A D     color=tanorange
    angle  BAD B A D      color=anglered heart label=$\angle BAD$ at=E
  text
    Draw \{tanorange|the tangent $AD$}... \textit{Q.E.D.}
```

## RULES

1. Colors LOCAL per station. Uncolored = BLACK. Never grey.
2. At least one `heart` per station.
3. Every used color declared; every declared color used.
4. Define geometry ops BEFORE referencing them.
5. Text: `{colorname|words}` spans + `$math$`. 4–5 sentences each, EDUCATIONAL.
6. `@(x,y)` on point ops = cosmetic hint only.
7. Lemma VII depends on Lemma VI — mention "by the preceding lemma" in text.
8. End final station with \textit{Q.E.D.}
9. `\\` at end of line to continue long lines.
10. This is the CROWN JEWEL. Make the text panels shine.

Return ONLY the `.room` file text.
