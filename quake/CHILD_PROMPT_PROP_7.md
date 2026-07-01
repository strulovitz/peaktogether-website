# QUAKE CHILD PROMPT — prop_7.room

You are a Quake content child. You will write ONE `.room` file for prop_7. Return ONLY the `.room` file text in a fenced code block.

---

## ⚠️ THE FORMAT — READ THIS BEFORE ANYTHING ELSE ⚠️

The .room file has a fixed structure. You CANNOT invent your own labels. Here is a **1-station room** showing every required keyword:

```
room      law_2
kind      geometry
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Axioms, Law II.
caption   The change of motion is proportional to the motive force impressed.
final     2
ceiling   law2 :: F = ma

station 1
  gloss One sentence summarizing what this station teaches.
  color motionblue #1E6FE0
  color forceorange #E8770A
  panel
    point A @(0,0) marker=dot label=$A$ at=SW
    point B @(3,2) marker=dot label=$B$ at=NE
    segment AB A B color=motionblue heart label=$AB$ at=SE
  text
    Here a body moves along {motionblue|the line $AB$} under a {forceorange|force}. \
    The greater the force, the greater the change of speed. \textit{Q.E.D.}
```

**Every station block has exactly:**
1. `station N` — the station number
2. `  gloss` — one-sentence summary (indented 2 spaces)
3. `  color <name> #<hex>` — declare every color used in this station (indented 2 spaces)
4. `  panel` — the drawing ops (indented 2 spaces, then ops indented 4 spaces)
5. `  text` — the prose (indented 2 spaces, then prose indented 4 spaces)

**Between stations:** one blank line.

---

## GEOMETRY OPS — KEYWORD SYNTAX CHEAT SHEET

Every op starts with its NAME immediately after the op keyword. Then keyword args.

| Op | Required syntax |
|-----|-----------------|
| `point` | `point <name> @(x,y) label=$L$ at=DIR marker=dot` |
| `segment` | `segment <name> <pt1> <pt2>` |
| `line` | `line <name> <pt1> <pt2>` |
| `ray` | `ray <name> <pt1> <pt2>` |
| `arc` | `arc <pt1> <pt2> <centre>` |
| `circle_cr` | `circle_cr <name> <centre_pt> <radius>` |
| `circle_3` | `circle_3 <name> <pt1> <pt2> <pt3>` |
| `polygon` | `polygon <name> <pt1> <pt2> ...` |
| `polyline` | `polyline <name> <pt1> <pt2> ...` |
| `parallel` | `parallel <name> through <pt> to <line_pt1> <line_pt2>` |
| `perp` | `perp <name> through <pt> to <line_pt1> <line_pt2>` |
| `foot` | `foot <name> from <pt> to <line_pt1> <line_pt2>` |
| `tangent_at` | `tangent_at <name> on <curve_name> at <pt>` |
| `angle` | `angle <name> <arm1_pt> <vertex_pt> <arm2_pt>` |

Attributes after ops: `color=NAME` `heart` `label=$..$` `at=DIR` `marker=dot`
DIR = N \| S \| E \| W \| NE \| NW \| SE \| SW \| center

**Text spans:** `{colorname|words here}` for colored text, `$math$` for inline math.

**DO NOT use:** `#` comments, `s1`/`s2` labels, `caption` blocks inside stations.

---

## YOUR ROOM — prop_7

**DIAGRAM, 3 stations, Pl.3 Fig.3. Body on a circle, force toward point S (not centre).**

```
room      prop_7
kind      geometry
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section II, Proposition VII; Plate 3, Figure 3.
caption   If a body revolves in the circumference of a circle, find the law of centripetal force directed to any given point.
final     3
ceiling   prop7 :: F \propto \dfrac{1}{SP^2}\cdot\dfrac{1}{PV^3}
```

### Station map

- **s1**: Circle VQPA → circblue(#1E6FE0); body P, Q nearby on circle; force centre S → centerorange(#E8770A) inside; SP → radgreen(#00A35A) ♥.
- **s2**: Tangent PRZ at P → tanteal(#00897B) ♥; chord PV through S; diameter VA through centre; join AP → diampurple(#8E24AA).
- **s3**: QT ⟂ SP (use foot + perp); LR ∥ SP through Q (use parallel) → constred(#D81B60) ♥ for both; similar triangles → QT²/QR ∝ PV³ → F ∝ 1/(SP²·PV³).

### Newton's text

> If a body revolves in the circumference of a circle; it is proposed to find the law of centripetal force directed to any given point. Pl. 3. Fig. 3.
>
> Let VQPA be the circumference of the circle; S the given point to which as to a centre the force tends; P the body moving in the circumference; Q the next place into which it is to move; and PRZ the tangent of the circle at the preceding place. Through the point S draw the chord PV, and the diameter VA of the circle, join AP, and draw QT perpendicular to SP, which produced, may meet the tangent PRZ in Z; and lastly, through the point Q draw LR parallel to SP, meeting the circle in L, and the tangent PZ in R. And, because of the similar triangles ZQR, ZTP, ZPA we shall have RP² (that is, QRL) to QT² as AV² to PV²...the force will become reciprocally as SP² × PV³.

### What each station teaches

**Station 1** — The circle is the orbit. S sits INSIDE it, deliberately NOT at the centre — Newton wants the force law toward ANY point. P is the body, Q the next place nearby. Draw the circle, S, P, Q, and SP. Heart: radgreen SP. Text: explain the setup — simplest curvilinear orbit, arbitrary force point, the distance SP is what the force depends on.

**Station 2** — The auxiliary geometry that links S to the circle. Draw tangent PRZ at P (the forceless path). Through S draw chord PV to the far side. Draw diameter VA through V. Join AP. Heart: tanteal tangent. Text: tangent = forceless path; chord+diameter link S to circle's geometry; VA is a diameter so ∠VPA is a right angle — the seed of similar triangles.

**Station 3** — Apply Prop. VI's construction. Use `foot T from Q to S P` to get foot T, then `perp QT through Q to S P` and `parallel LR through Q to S P`. Place R where LR meets tangent, L where LR meets circle. Heart: constred QT and LR. Text: similar triangles ZQR,ZTP,ZPA give QT²/QR ∝ PV³ → plug into Prop. VI → F ∝ 1/(SP²·PV³). When S=centre, PV=diameter → 1/SP², the inverse-square law! End with Q.E.D.

**Figure layout (Pl.3 Fig.3):** Circle radius ~3.2, centre O at (0,0). S inside at about (0.7,-0.8). P on right side (~2.8,-1.5). Q upper-left (~1.3,2.9). V left-ish (~-1.65,0.3). A opposite (~1.65,-0.3). Tangent extending right from P.

---

## RULES

1. Every station re-defines ALL its points from scratch.
2. At least one `heart` per station (on a colored op in the panel).
3. Every declared color used; every used color declared in its station.
4. Define points BEFORE segments/polygons that reference them.
5. `color=black` is never used — black is the default, just omit.
6. 4-5 sentences of EDUCATIONAL prose per text panel.
7. End final station with `\textit{Q.E.D.}`.
8. `\` at end of line to continue long text lines.

Return ONLY the `.room` file text.
