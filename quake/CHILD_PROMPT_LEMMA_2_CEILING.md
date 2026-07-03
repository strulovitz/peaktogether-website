# CHILD PROMPT — lemma_2: Write the FULL .room file from scratch

Build the complete Quake `.room` file for Lemma II.

## The format

You write in the ROOMSPEC format. Header:

```
room <id>
kind <geometry|equation|text>
import <citation>
caption <one line>
final <step#>
ceiling <eq_id> :: <LaTeX>     (one per station)

station <n>
  gloss <one sentence>
  color <name> <#hex>          (repeat; local to this station)
  panel
    <geometry ops: point, segment, polygon, polyline, circle, arc, series, etc.>
  text
    <prose with {colorname|words} spans and $math$>
```

Geometry ops: `point`, `segment`, `polygon`, `polyline`, `circle_cp`, `arc`, `series`, `parallel`, `perp`, `intersect`, `midpoint`, `tangent_at`, etc. Each can take: `color=NAME heart label=$..$ at=DIR marker=dot stabilo=#hex @(x,y)` for free points. Colors are local per station. Uncolored = black. Never grey.

## The room: lemma_2

Newton, Principia, Book I, Section I, Lemma II (Plate 1, Fig. 6):
**If in any figure AacE there be inscribed any number of parallelograms on equal bases, and circumscribed parallelograms completed: then as the breadth of those parallelograms is diminished without limit, the inscribed figure, the circumscribed figure, and the curvilinear figure have to one another the ultimate ratio of equality.**

This is the method of exhaustion applied to the area under a curve.

## The 3 stations

**Station 1:** The setup. The curvilinear figure AacE — bounded by the curve aE on top, the baseline AE on the bottom, and the vertical side Aa on the left. On equal bases AB, BC, CD along the baseline, rectangles are inscribed (touching the curve from below) and circumscribed (enclosing from above). The heart is the inscribed rectangles — they approximate the area from below.

**Station 2:** The limit. As the base AB is diminished to nothing (AB → 0), the difference between the sum of inscribed and sum of circumscribed rectangles vanishes. The gap AabB — the tiny difference at each base — collapses. In the limit, the two constructions become indistinguishable. The heart is the vanishing base AB → 0.

**Station 3:** The conclusion. The inscribed figure, the circumscribed figure, and the curvilinear area AacE are ultimately equal — all three have the ratio of equality. Newton writes: "if you deny their ultimate ratios to be ratios of equality, you deny the foundations of geometry." The heart is the ultimate equality of all three figures.

## What you produce

The complete `.room` file text — header, 3 stations, everything. One `ceiling` equation per station. Use the name `lemma_2` as the room id. Kind is `geometry`.
