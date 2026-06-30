# QUAKE CHILD PROMPT — lemma_9.room

You are a Quake content child. Write ONE `.room` file for lemma_9. Return ONLY the `.room` file text (in a fenced code block).

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

## YOUR ROOM — lemma_9

**lemma_9 · DIAGRAM · 3 step-pairs · Pl.2 (Newton's Fig for Lem. IX)**

This lemma is the bridge to dynamics: it proves that the tiny triangles formed by ordinates under a curve are ultimately in the duplicate ratio of the side lengths. Lemma X will use this to prove "spaces as square of times."

```
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I, Lemma IX; Plate 2.
caption   The areas of triangles formed by ordinates under a curve are ultimately one to the other in the duplicate ratio of the sides.

s1 — Line AE → lineblue(#1E6FE0); curve ABC → curvegreen(#00A35A); ordinates BD, CE → ordorange(#E8770A) ♥; triangles ABD, ACE.
s2 — Auxiliary: produced Ad,Ae ∝ AD,AE; similar curve Abc; tangent Ag → auxpurple(#8E24AA) ♥; points F,G,f,g.
s3 — Vanishing cAg: rectilinear areas Afd, Age → arearred(#D81B60) ♥; duplicate ratio of sides.

colors_used: lineblue, curvegreen, ordorange, auxpurple, arearred
ceiling: \triangle ABD : \triangle ACE \to AD^2 : AE^2
```

### Newton's text (verbatim, 1729 Motte, Lemma IX):

> If a right line AE and a curve line ABC, both given by position, cut each other in a given angle; and to that right line, in another given angle, BD, CE are ordinately applied, meeting the curve in B, C; and the points B and C together approach towards, and meet in, the point A: I say that the areas of the triangles ABD, ACE, will ultimately be one to the other in the duplicate ratio of the sides.
>
> For while the points B, C approach towards the point A, suppose always AD to be produced to the remote points d and e, so as Ad, Ae may be proportional to AD, AE; and the ordinates db, ec, to be drawn parallel to the ordinates DB and EC, and meeting AB and AC produced in b and c. Let the curve Abc be similar to the curve ABC, and draw the right line Ag so as to touch both curves in A, and cut the ordinates DB, EC, db, ec, in F, G, f, g. Then supposing the length Ae to remain the same, let the points B and C meet the point A; and the angle cAg vanishing, the curvilinear areas Abd, Ace will coincide with the rectilinear areas Afd, Age; and therefore (by Lem 5) will be one to other in the duplicate ratio of the sides Ad, Ae. But the areas ABD, ACE are always proportional to these areas; and so the sides AD, AE are to these sides. And therefore the areas ABD, ACE are ultimately one to the other in the duplicate ratio of the sides AD, AE. Q.E.D.

### GUIDANCE

Another "blow-up" proof (same trick as Lemma VII). We have a curve ABC cutting the baseline AE at A. Ordinates BD and CE drop from the curve to the baseline, forming triangles ABD and ACE. As B and C slide toward A, the triangles shrink. Newton proves their areas tend to the ratio AD²:AE².

**Step 1:** Draw the baseline AE from A to E (rightward). Draw the curve ABC above it, meeting AE at A. Drop ordinates BD and CE from curve points B and C perpendicular to AE. Triangles ABD and ACE appear. The {ordorange|ordinates BD and CE forming the triangles} are the heart. Text: introduce the setup — a curve over a baseline, ordinates forming triangles, the question of their ultimate area ratio.

**Step 2:** The blow-up. Produce AD to Ad and AE to Ae (proportional). Draw ordinates db, ec parallel to DB, EC. Draw similar curve Abc. Draw tangent Ag touching both curves at A, intersecting the ordinates at F,G,f,g. The {auxpurple|auxiliary construction — similar curve Abc, tangent Ag, and the produced ordinates} is the heart. Text: explain the blow-up trick — everything stays proportional but the distant version stays finite.

**Step 3:** The payoff. As B,C→A, angle cAg vanishes. Curvilinear areas Abd, Ace → rectilinear Afd, Age. By Lemma V (similar figures!), these rectilinear areas are in the duplicate ratio Ad²:Ae² = AD²:AE². Therefore the original triangles ABD, ACE are also in that ratio. The {arearred|rectilinear areas Afd and Age — proving the duplicate ratio} are the heart. Text: 4–5 sentences. End Q.E.D. Mention Lemma V by name!

**Layout:** Baseline along bottom. Curve rising above. Ordinates dropping down. The blow-up portion off to the right (distant points d,e, similar curve Abc). Keep it visually connected — the original is a mini-version of the auxiliary.

**Practical:**
- Use `point` for all points, `polyline` for curves, `segment` for ordinates and baselines
- Use `tangent_at` for the tangent Ag (touching the curve at A)
- The "triangles" can be drawn as `polygon` ops connecting A-B-D and A-C-E
- Label points clearly: A, E, B, C, D, E for original; A, d, e, b, c for auxiliary; F, G, f, g for intersection points; Ag for tangent

## GOLD EXAMPLE — lemma_7.room (same blow-up proof style!)

```
room      lemma_7
kind      geometry
...
station 2
  gloss   The auxiliary blow-up: AB and AD produced to distant b and d, the parallel bd, and a similar arc Acb that stays finite.
  color   auxpurple #8E24AA
  color   arcblue   #1E6FE0
  panel
    point   A   @(0,0)     marker=dot label=$A$ at=SW
    ...
    ray     Ab A b         color=auxpurple
    ray     Ad A d         color=auxpurple
    segment bd b d         color=auxpurple
    polyline auxarc A c b  color=auxpurple heart
  text
    Here is the device... the original figure dwindles toward $A$, but the \
    enlarged copy out at $b,d$ stays a fixed, finite size ...
```

## RULES

1. Colors LOCAL per station. Uncolored = BLACK. Never grey.
2. At least one `heart` per station.
3. Every used color declared; every declared color used.
4. Define geometry ops BEFORE referencing them.
5. Text: `{colorname|words}` spans + `$math$`. 4–5 sentences each, EDUCATIONAL.
6. `@(x,y)` on point ops = cosmetic hint only.
7. Lemma IX depends on Lemma V (similar figures) and Lemma VII (vanishing angle/arc=chord=tangent). Mention these in text.
8. End final station with \textit{Q.E.D.}
9. `\\` at end of line to continue long lines.

Return ONLY the `.room` file text.
