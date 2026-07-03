# CHILD PROMPT — lemma_2: Write the FULL .room file from scratch

Build the complete Quake `.room` file for Lemma II.

## The format

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
    <geometry ops: point, segment, polygon, polyline, circle_cp, arc, series, parallel, perp, intersect, midpoint, tangent_at, etc.>
  text
    <prose with {colorname|words} spans and $math$>
```

The `ceiling` line goes INSIDE the station block, just after `station <n>`. Each station has exactly one `ceiling` equation — a LaTeX formula capturing the key mathematical result of that step, displayed in blood-red on the ceiling above that station when the demon dies. Geometry ops take `color=NAME heart label=$..$ at=DIR marker=dot stabilo=#hex @(x,y)` for free points. Colors are local per station. Uncolored = black. Never grey.

## The room: lemma_2

Newton, Principia, Book I, Section I, Lemma II (Plate 1, Fig. 6):
**If in any figure AacE there be inscribed any number of parallelograms on equal bases, and circumscribed parallelograms completed: then as the breadth of those parallelograms is diminished without limit, the inscribed figure, the circumscribed figure, and the curvilinear figure have to one another the ultimate ratio of equality.**

## The 3 stations

**Station 1:** The setup. The curvilinear figure AacE — bounded by the curve aE, the baseline AE, and the vertical side Aa. On equal bases AB, BC, CD along the baseline, rectangles are inscribed (touching the curve from below) and circumscribed (enclosing from above). The heart is the inscribed rectangles.

**Station 2:** The limit. As the base AB → 0, the difference between inscribed and circumscribed sums vanishes. The gap AabB collapses. In the limit, the two constructions become indistinguishable. The heart is the vanishing base AB → 0.

**Station 3:** The conclusion. The inscribed figure, the circumscribed figure, and the curvilinear area AacE are ultimately equal — all three have the ratio of equality. Newton writes "if you deny this, you deny the foundations of geometry." The heart is the ultimate equality of all three.

## What you produce

The complete `.room` file — header, 3 stations, everything from scratch. Each station MUST contain its own `ceiling` line. Use the name `lemma_2` as the room id.
