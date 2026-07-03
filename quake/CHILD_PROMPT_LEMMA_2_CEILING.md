# CHILD PROMPT — lemma_2: Write ceiling equations per station

**Your task:** Write one ceiling equation per station for this room. You are working from the original Newton text, NOT from any prior AI's work.

**The room:** Lemma II — If in any figure AacE, terminated by the right lines Aa, AE and the curve aE, there be inscribed any number of parallelograms Ab, Bc, Cd, etc. on equal bases AB, BC, CD, etc., and the sides Bb, Cc, Dd, etc. parallel to Aa; and the parallelograms aKbl, bLcm, cMdn, etc. are completed: then, if the breadth of those parallelograms is diminished and their number increased to infinity, the ultimate ratios which the inscribed figure AKbLcMdD, the circumscribed figure AalbmcndoE, and the curvilinear figure AabcdE have to one another, are ratios of equality.

**The 3 stations:**

- **Station 1:** The setup — the curvilinear figure AacE with its inscribed and circumscribed rectangles. The inscribed rectangles fill from below, the circumscribed enclose from above. The curve aE forms the upper boundary.

- **Station 2:** The shrinking — as the base AB → 0, the difference between inscribed and circumscribed rectangles goes to zero. The gap AabB collapses. In the limit, the two constructions become indistinguishable.

- **Station 3:** The conclusion — the ultimate equality: inscribed figure = circumscribed figure = curvilinear area. Newton states "if you deny this, you deny the foundations of geometry." The method of exhaustion yields the exact area.

**Format:** Give me one `ceiling` line per station, each capturing that step's key math result in LaTeX:

```
ceiling   eq0 :: <LaTeX for station 1>
ceiling   eq1 :: <LaTeX for station 2>
ceiling   eq2 :: <LaTeX for station 3>
```
