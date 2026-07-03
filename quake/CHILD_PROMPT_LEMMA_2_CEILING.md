# CHILD PROMPT — lemma_2: Write the FULL .room file from scratch

You are building content for a game where the player walks through Newton's Principia as a 3D dungeon. Each "room" is one idea. The player shoots panels on the walls to reveal colored geometry figures, kills a demon, and then the room's ceiling equations appear in blood-red above each station.

## The room: Lemma II (Method of Exhaustion)

Here is Newton's actual text from the 1729 Motte translation:

---

If in any figure AacE (Pl.1.Fig.6.) terminated by the right lines Aa, AE, and the curve acE, there be inscrib'd any number of parallelograms Ab, Bc, Cd, etc. comprehended under equal bases AB, BC, CD, etc. and the sides Bb, Cc, Dd, etc. parallel to one side Aa of the figure; and the parallelograms aKbl, bLcm, cMdn, etc. are compleated. Then if the breadth of those parallelograms be suppos'd to be diminished, and their number to be augmented in infinitum: I say that the ultimate ratio's which the inscrib'd figure AKbLcMdD, the circumscribed figure AalbmcndoE, and the curvilinear figure AabcdE, will have to one another, are ratio's of equality.

For the difference of the inscrib'd and circumscrib'd figures is the sum of the parallelograms Kl, Lm, Mn, Do, that is, (from the equality of all their bases) the rectangle under one of their bases Kb and the sum of their altitudes Aa, that is, the rectangle ABla. But this rectangle, because its breadth AB is suppos'd diminished in infinitum, becomes less than any given space. And therefore (by Lem. I.) the figures inscribed and circumscribed become ultimately equal one to the other; and much more will the intermediate curvilinear figure be ultimately equal to either. Q.E.D.

---

## The format — geometry room

The `.room` file uses a keyword-block format. Full syntax:

```
room <id>
kind geometry
import <citation>
caption <one line>
final <step#>

station <n>
  ceiling <eq_id> :: <LaTeX>
  gloss <one sentence>
  color <name> <#hex>
  panel
    point <name> @(x,y) [color=NAME] [heart] [label=$..$ at=DIR] [marker=dot]
    segment <name> <A> <B> [color=NAME] [heart] [label=$..$ at=DIR]
    polygon <name> <P1> <P2> ... [color=NAME]
    polyline <name> <P1> <P2> ...
    series <name> along <curve> to <guide_curve> count <N> kind inscribed_rects|circumscribed_rects [color=NAME] [heart]
    parallel <name> through <pt> to <direction_pt>
    perp <name> through <pt> to <direction_pt>
    intersect <name> of <curveA> <curveB>
    midpoint <name> of <A> <B>
    tangent_at <name> on <curve> at <point>
  text
    <explanation with {colorname|words} spans and $math$>
```

- `ceiling`: INSIDE each station. LaTeX formula. Blood-red on ceiling when demon dies.
- `color`: local to each station. Matching words in text use `{colorname|words}`.
- `heart`: marks the current step's key element — bright Stabilo highlighter.
- `@(x,y)`: rough coordinate for free points in cm (Asymptote units).
- Uncolored = black. Never grey. Text panels: 3–4+ sentences.

## The 3 stations

**Station 1 — The setup:** The curvilinear figure AacE, bounded by curve aE, baseline AE, and side Aa. Inscribed rectangles fill it from below; circumscribed rectangles enclose from above. The equal bases AB, BC, CD shrink. The heart is the inscribed rectangles — they approximate the area from below.

**Station 2 — The limit:** The difference between inscribed and circumscribed sums equals the rectangle ABla (base × total altitude). As AB → 0, this rectangle vanishes — becoming less than any given space. The two constructions become indistinguishable. The heart is the vanishing base AB → 0.

**Station 3 — The conclusion:** By Lemma I, when the difference vanishes, the inscribed and circumscribed figures become ultimately equal — and the curvilinear figure between them shares that equality. All three have the ultimate ratio of equality. The method of exhaustion yields the exact area. The heart is the ultimate equality of all three figures.

## What you produce

Complete `.room` file — header, 3 stations, each with its own `ceiling`. Room id: `lemma_2`. Kind: `geometry`. Import: "Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I, Lemma II; Plate 1, Fig. 6."
