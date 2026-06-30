# 🧰 QUAKE PARENT 16 — FROZEN DELIVERABLE (verbatim from Opus 4.8)

> Room-content format (.room spec) + `build/room_from_spec.py` tool design + child brief.
> Anchored to the gold lemma_2 triplet; enforces the corrected local-color model structurally.

---

## PART I — THE FORMAT SPEC (ROOMSPEC.md)

This is the document a child AI receives (together with its room's station map + the source text). It writes one .room file. It never touches JSON, LaTeX color macros, or Asymptote.

```
# QUAKE .room FORMAT — v1.0

You are filling in ONE room of the Quake Principia level. You write a single plain-text
`.room` file in the keyword-block format below. You NEVER write JSON, Asymptote, or
\textcolor — the build tool does all of that. You describe constructions and meanings; the
tool computes geometry, colors, ids, and files.

## THE SHAPE OF A ROOM

A room is a HEADER, then one STATION block per proof step (in order), then nothing else.
A station is one wall panel (the thing you look at + shoot) beside its explanation text.

There are three KINDs of room. The skeleton is identical; only the PANEL body differs:
- `geometry`  — the panel is a drawn figure (a construction).
- `equation`  — the panel IS the equation; you color its terms.
- `text`      — the panel is a colored statement / foundational idea; you color its words.

A room is ALL ONE kind. (If a room mixes — e.g. an equation step and a sketch step —
use `geometry` and express the equation step with `term` ops; see "MIXED ROOMS".)

## THE COLOR RULE (read this twice)

Colors are LOCAL to each station. You invent fresh colors every station. The SAME concept
may be a different color, or no color, in another station. There is NO global palette.

- In a station, each IMPORTANT element gets its own distinct color: a `name` + a `hex`.
- The matching WORDS in that station's explanation carry the SAME color (you mark them).
- UNIMPORTANT things get NO color → they render plain black. NEVER use grey.
- Exactly the current step's HEART (its single most important element) also gets a bright
  Stabilo highlighter swipe. Mark it with `heart`. The Stabilo is NEVER cumulative — only
  this step. Pick a Stabilo hue per heart (suggestions: yellow green orange pink cyan).

Pick beautiful, distinct, high-contrast hexes. Variety between rooms is good.

## HEADER KEYWORDS (one per line, before the first STATION)

```
room      <node_id>            # lowercase, e.g. lemma_2 / prop_4 / law_1
kind      geometry|equation|text
import    <full free-text citation string>   # the "edition" — copy from your station map
caption   <one-line figure caption>          # what the panel depicts, plain words
final     <step number of the final/closing station>   # usually the last
ceiling   <eq_id> :: <verbatim LaTeX>        # repeat this line per ceiling equation;
                                             #   copy VERBATIM from your station map
```

## A STATION BLOCK

```
station <n>                    # 1, 2, 3 … contiguous from 1, in proof order
  gloss   <one plain sentence: what this step shows>
  color   <name> <#hex>        # declare each local color used in THIS station; repeat
  color   <name> <#hex>
  ...
  panel
    <PANEL BODY — depends on kind, see below>
  text
    <EXPLANATION PROSE with {color|words} spans and $math$; see "WRITING TEXT">
```

Rules the tool enforces (it will reject your file with a line number if you break them):
- Stations numbered 1..N with no gaps.
- Every `{name|...}` span in `text` must have a matching `color name #hex` in that station.
- Every declared `color` must be USED at least once (in a panel element or a text span).
- Exactly the heart element(s) of the step carry `heart`; at least one heart per station.
- `marker` may only be `dot` (or omitted → none).

## WRITING THE PANEL — `geometry`

List CONSTRUCTION ops, one per line. You give the logic; Asymptote computes coordinates.
You may give a rough position `@(x,y)` for free points to shape the drawing — these are
HINTS, not the math; the overlay tool absorbs scale/rotation later.

Op syntax (each may end with attributes — see ATTRIBUTES):
```
point   <Name> [@(x,y)]
point_on   <Name>  on <path>  [t=<0..1> | near=(x,y)]
intersect  <Name>  of <pathA> <pathB>  [near=(x,y)]
midpoint   <Name>  of <A> <B>
foot       <Name>  from <P> to <line>
reflect    <Name>  of <P> over <line>
segment <Name>  <A> <B>
line    <Name>  <A> <B>
ray     <Name>  <A> <B>
parallel   <Name>  through <P>  to <line>
perp       <Name>  through <P>  to <line>
tangent_at <Name>  on <curve>  at <P>
tangent_from <Name>  to <curve>  from <P>  [near=(x,y)]
bisector   <Name>  <A> <vertex> <B>
circle_cp  <Name>  center <C>  through <P>
circle_cr  <Name>  center <C>  radius <A> <B>        # radius = |AB|
circle_cr  <Name>  center <C>  radiusval <number>
circle_3   <Name>  <A> <B> <C>
arc        <Name>  center <C>  from <A> to <B>  [cw|ccw]
ellipse_foci   <Name>  foci <F1> <F2>  through <P>
ellipse_axes   <Name>  center <C>  major <P>  minor <Q>
parabola_fd    <Name>  focus <F>  directrix <line>
hyperbola_foci <Name>  foci <F1> <F2>  through <P>
conic_5    <Name>  <P1> <P2> <P3> <P4> <P5>
polygon    <Name>  <A> <B> <C> ...                   # >=3 points
polyline   <Name>  <A> <B> <C> ...                   # >=2 points
series     <Name>  along <basepath> to <curve> count <N> kind <K>
           # K: inscribed_rects | circumscribed_rects | ordinates | chords | tangent_polygon
angle      <Name>  <A> <vertex> <B>  [right]
```
`<Name>` is referenced by later ops. `<path>`/`<line>`/`<curve>` are earlier op names.

## WRITING THE PANEL — `equation`

The equation IS the figure. List its important terms, each its own color:
```
term  <local_color_name>  $<latex fragment>$   [heart]
```
Plus an optional structural skeleton line so the terms read as a real equation on the panel:
```
layout  $<full LaTeX equation, with the SAME color names wrapping the same fragments>$
```
If you omit `layout`, the tool lays the terms out left-to-right with their LaTeX, which is
fine for simple relations. Use `layout` whenever the equation has real structure (fractions,
proportions). In `layout`, wrap each colored fragment as `{name|$frag$}` exactly like text.

## WRITING THE PANEL — `text`

The statement IS the figure. List the key phrases, each its own color:
```
phrase  <local_color_name>  "<the exact words from the book>"   [heart]
```
The tool renders these as a colored statement panel (the phrases shown in their colors, the
connective words black). Use the book's own words; if the book gives none for a foundational
idea, write a short faithful phrase (no invented math).

## WRITING TEXT (the explanation, all three kinds)

Plain prose. Mark colored words with `{colorname|the words}`. Use `$...$` for math.
The colorname must be one you declared with `color` in this station.
```
text
  The {forceorange|pull toward the centre} is as the {velblue|square of the speed}
  divided by the {radgreen|distance from the centre}.
```
The tool turns `{forceorange|pull toward the centre}` into the right colored LaTeX and
auto-fills the machine bookkeeping. Do not write \textcolor yourself.

## MIXED ROOMS

If a room has both a drawn step and an equation step, set `kind geometry` and use `term`
ops inside the geometry panel for the equation step (a `term` op is allowed in a geometry
panel; it places a colored equation fragment as a label). Each station is still one panel.

## ATTRIBUTES (geometry ops)

Append to any drawing op, space-separated, any order:
```
color=<name>        # use a declared local color for this element's ink (omit → black)
heart               # this element is the step's Stabilo heart
label=$<tex>$       # a lettered label (book lettering, e.g. $A$); rendered black
at=N|S|E|W|NE|NW|SE|SW|center   # label placement (default NE)
marker=dot          # draw a dot at a point (points only)
stabilo=<#hex>      # the Stabilo swipe color for a heart (default: a bright yellow)
```

## A COMPLETE EXAMPLE (geometry)

```
room      lemma_2
kind      geometry
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Sec I, Lemma II.
caption   Inscribed and circumscribed parallelograms under the curve aE on equal bases.
final     3
ceiling   eq0 :: \lim_{AB \to 0}\bigl(\text{circ}-\text{insc}\bigr)\longrightarrow 0
ceiling   eq1 :: \text{insc}=\text{circ}=\text{area}\quad(\text{ultimately})

station 1
  gloss   The curvilinear figure AacE: curve aE, baseline AE, side Aa.
  color   curveblue  #1E6FE0
  color   basegreen  #00A35A
  color   sideorange #E8770A
  panel
    point   A @(0,0)   marker=dot label=$A$ at=SW
    point   E @(8,0)   marker=dot label=$E$ at=SE
    point   B @(2,0)   marker=dot label=$B$ at=S
    point   C @(4,0)   marker=dot label=$C$ at=S
    point   D @(6,0)   marker=dot label=$D$ at=S
    point   pa @(0,1.4)  color=curveblue label=$a$ at=NW
    point   pb @(2,2.6)  color=curveblue label=$b$ at=N
    point   pc @(4,3.4)  color=curveblue label=$c$ at=N
    point   pd @(6,3.9)  color=curveblue label=$d$ at=N
    point   pe @(8,4.2)  color=curveblue
    polyline curve pa pb pc pd pe   color=curveblue heart stabilo=#FFE000
    segment baseAE A E   color=basegreen
    segment sideAa A pa  color=sideorange
  text
    In the figure $AacE$, bounded by {sideorange|the line $Aa$} and {basegreen|the base $AE$}
    and by {curveblue|the curve $acE$}, take equal bases along {basegreen|the base $AE$}.

station 2
  gloss   The inscribed parallelograms standing under the curve.
  color   inscpurple #8E24AA
  color   sideorange #E8770A
  color   curveblue  #1E6FE0
  panel
    series inscribed along baseAE to curve count 4 kind inscribed_rects \
           color=inscpurple heart stabilo=#00E676
  text
    On these bases erect {inscpurple|the inscribed parallelograms}, with sides parallel to
    {sideorange|$Aa$}. {inscpurple|The inscribed figure} lies wholly under {curveblue|the curve}.

station 3
  gloss   The circumscribed parallelograms; their excess vanishes.
  color   circred    #D81B60
  color   curveblue  #1E6FE0
  color   inscpurple #8E24AA
  color   basegreen  #00A35A
  panel
    series circumscribed along baseAE to curve count 4 kind circumscribed_rects \
           color=circred heart stabilo=#FF6F00
  text
    Complete {circred|the circumscribed parallelograms} above {curveblue|the curve}. Their
    excess over {inscpurple|the inscribed figure} equals the rectangle on {basegreen|$AB$},
    which vanishes as {basegreen|$AB$} shrinks; so the figures become ultimately equal. \textit{Q.E.D.}
```

---

## PART II — THE TOOL DESIGN + CHILD BRIEF (`build/room_from_spec.py`)

This is the brief a single child chat receives to implement the one tool. Frozen contract, headless-testable pure core, file-writing shell.

### Frozen public contract

```python
# build/room_from_spec.py
from pathlib import Path
from typing import NamedTuple

class BuildResult(NamedTuple):
    node_id: str
    recipe_path: Path | None      # None for equation/text rooms with no geometry ops
    asy_path: Path
    room_source_path: Path

def build_room(spec_text: str, out_root: Path, *, write: bool = True) -> BuildResult:
    """Parse one .room spec, validate, emit recipe.json + figure.asy + room_source.json.
    Pure except for the file writes (gated by `write`). Raises SpecError(line, msg) on any
    malformed spec — never emits a half-valid file. Output JSONs are validated against the
    pydantic models in map.raw_models before writing."""

class SpecError(Exception):
    def __init__(self, line: int, msg: str): ...
```

### Architecture — four pure stages + one shell

```
parse(spec_text)            -> Spec            # line-oriented keyword parser; SpecError(line,msg)
validate(spec)              -> None            # all cross-checks; SpecError on any violation
emit_recipe(spec)           -> Recipe | None   # None when no geometry/term ops (pure text rooms)
emit_asy(spec)              -> str             # the self-contained gold-convention .asy text
emit_room_source(spec)      -> RoomSource      # scans expanded \textcolor to fill colors_used
# shell:
build_room(...)             -> writes the three artifacts, returns BuildResult
```

### Internal Spec model (parse target)

```python
# all dataclasses; pure
@dataclass
class ColorDecl:    name: str; hex: str
@dataclass
class Attr:         color: str|None; heart: bool; label: str|None; at: str; marker: str; stabilo: str|None
@dataclass
class GeoOp:        op: str; name: str; args: dict; attr: Attr; rough_xy: tuple|None; line_no: int
@dataclass
class TermOp:       color: str|None; latex: str; heart: bool; stabilo: str|None; line_no: int
@dataclass
class PhraseOp:     color: str|None; words: str; heart: bool; stabilo: str|None; line_no: int
@dataclass
class Station:
    n: int; gloss: str; colors: list[ColorDecl]
    geo_ops: list[GeoOp]; term_ops: list[TermOp]; phrase_ops: list[PhraseOp]
    layout: str|None
    text_raw: str          # prose with {name|words} spans
    line_no: int
@dataclass
class CeilingDecl:  eq_id: str; latex: str
@dataclass
class Spec:
    node_id: str; kind: str; edition: str; caption: str
    final_step: int; ceilings: list[CeilingDecl]; stations: list[Station]
```

### Stage 1 — parse

- Line-oriented. `\` at end of line = continuation. `#` starts a comment (strip to EOL, but NOT inside a `$...$` or a quoted `"..."`). Blank lines ignored.
- Header keywords (`room`/`kind`/`import`/`caption`/`final`/`ceiling`) collected until first `station`.
- `ceiling X :: Y` splits on first `::`. `final` parses to int.
- Inside a station: `gloss` (one line), repeated `color name #hex`, then `panel` block, then `text` block (everything until next `station`/EOF, trimmed).
- Panel-op dispatch on first token (`point`, `segment`, `series`, `term`, `phrase`, `layout`, …).
- Attribute parser: split trailing `key=val` / bare `heart` tokens; `label=$..$` and `stabilo=#..` kept intact. `@(x,y)` captured as `rough_xy`. Validate marker in `{dot}`, at in `{N,S,E,W,NE,NW,SE,SW,center}`, hex `^#[0-9a-fA-F]{6}$`.
- Any unknown keyword/op → `SpecError(line, "unknown keyword '<tok>'")`.

### Stage 2 — validate (math-free, all surfaced with line numbers)

- `node_id` matches `^[a-z][a-z0-9_]*$`; `kind` in `{geometry,equation,text}`.
- stations numbered 1..N contiguous, no gaps, in order.
- `final_step` in 1..N.
- ceiling `eq_ids` unique; each becomes `<node_id>.eq<i>` by ORDER (i from 0).
- per station:
    * >=1 heart (across geo_ops/term_ops/phrase_ops).
    * every color declared is USED >=1 (in an op `attr.color` OR a `{name|..}` text span OR a layout `{name|..}` span); else `SpecError "declared color 'x' never used"`.
    * every `{name|..}` span in text/layout has a matching declared color; else `SpecError`.
    * every op `attr.color` / term/phrase color refers to a declared color; else `SpecError`.
    * color names within a station are unique; same name must carry the SAME hex.
- kind/body agreement:
    * `kind=geometry` → panel has `geo_ops` (`term_ops` allowed for mixed steps); no `phrase_ops`.
    * `kind=equation` → panel has `term_ops` (and optional `layout`); no `geo_ops`/`phrase_ops`.
    * `kind=text` → panel has `phrase_ops`; no `geo_ops`/`term_ops`/`layout`.
- geometry ref integrity: every `<path>`/`<line>`/`<curve>`/point Ref used by an op was defined by an earlier op's `<Name>` in the SAME station; else `SpecError "undefined reference 'X'"`.
- NO-GLOBAL-PALETTE SMELL CHECK: there is no place in the grammar to declare a room-level palette; `color` only exists inside a station. (Structural — but validate also asserts no color decl appears before the first `station`.)
- marker only on point ops; stabilo only on heart elements (warn+ignore otherwise).

### Stage 3 — emit_recipe → Recipe

Only for rooms that have geometry ops OR term ops (i.e. anything but a pure text room; text rooms emit None — no recipe.json).

- `figure_id = f"{node_id}.f1"`. `n_steps = len(stations)`.
- `steps = [StepGloss(index=s.n, gloss=s.gloss) for s in stations]`.
- For each geo op → the matching discriminated RecipeOp:
    - `name` = the op's `<Name>`. `op` = the literal. Map fields (`a`/`b`/`center`/`through`/...).
    - `draw = Draw(step=station.n, local_color=LocalColor(name,hex) if attr.color else None, is_heart=attr.heart, marker=attr.marker, label=Label(tex,placement,offset) if label)`.
    - `rough_xy` → on `FreePoint` only.
- term ops (in equation rooms / mixed steps) → emit as `FloatLabel("label")` ops carrying the term's LaTeX in the .asy (recipe records them as label ops with the `local_color` + `step` + `is_heart` so the manifest/heart accounting is uniform). phrase ops are NOT in the recipe; they live only in the .asy.
- Validate the assembled `Recipe(**...)` through pydantic before returning.

### Stage 4 — emit_asy → str (THE gold self-contained convention)

Template (filled per room):

```
// figure.<node_id>.f1.asy — <caption first line>
// Self-contained prooffig convention. Compile: asy -u "highlight=k" figure.<node_id>.f1.asy
// highlight=-1 => OFF (all black). highlight=k => step k's matched colors + step k heart Stabilo.

import graph;
settings.outformat = "png";
unitsize(1cm);

int highlight = -1;
usersetting();

// ---- palette (LOCAL; pure black when uncolored) ----
pen BLACK = rgb(0,0,0) + linewidth(1.0pt);
// one `pen <name> = rgb(r/255,g/255,b/255) + linewidth(1.6pt);` per DISTINCT (name,hex)
// across all stations — names are station-local but identical (name,hex) dedup to one pen

// bright Stabilo markers (one per heart that declares stabilo=, else default yellow)
// pen STABILO_<STATION><IDX> = rgb(...) + opacity(0.45) + linewidth(9pt) + squarecap;

// ---- ZONE 2: construction ----
// For GEOMETRY: emit pair/path declarations from rough_xy + construction
// Free points -> pair <name>=(x,y); segments/polylines/series -> path vars + curveY helper + rects loop
// For EQUATION/TEXT: no construction; label positions auto-stacked

// ---- ZONE 4: render (highlight-driven) ----
void drawAll(int highlight) {
  // STABILO underlay (current step's heart only) — guarded by if (highlight==k)
  // ink pass — each element: on<k> ? <pen> : BLACK
  // labels — always BLACK (book lettering); equation/text term-labels colored per step
}
drawAll(highlight);
```

Emission rules:
- One `bool onK = (highlight==K);` per step at top of `drawAll`.
- Stabilo underlay: `if (onK) draw(<geom>, STABILO_<K..>);` with `opacity(0.45)+linewidth(9pt)+squarecap`.
- Ink pass drawn in REVERSE step order (step-1 base on top, matching gold).
- Labels: `label("$X$", <at>, <placement>);` always BLACK for lettering; colored for term/phrase ops.
- EQUATION/TEXT layout: terms/phrases auto-stacked on invisible grid.

### Stage 5 — emit_room_source → RoomSource

- `figures = [FigureDecl(figure_id=f"{node}.f1", asy_path="figures/{node}.f1.asy", recipe_path="recipes/{node}.f1.json", n_steps=N, caption=caption, colors_used=<union of all LocalColors across stations, deduped by (name,hex)>)]`.
- For each station → `StepPair`:
    - `pair_id = f"{node}.s{n}"`, `step_index = n`.
    - `drawing = DrawingBlock(block_id=f"{node}.s{n}.fig", figure_id=f"{node}.f1", highlight_step=n)`.
    - `text = TextBlock(block_id=f"{node}.s{n}.txt", latex=<expanded>, colors_used=<scanned>)`.
- Text expansion: convert every `{name|words}` → `\textcolor{name}{words}`. Scan with `re.compile(r"\\textcolor\{([^}]+)\}\{")` to build `colors_used`.
- `final_pair_id = f"{node}.s{final_step}"`.
- `ceiling_equations = [CeilingEq(eq_id=f"{node}.eq{i}", latex=raw) for i,(_,raw) in enumerate(ceilings)]` — eq_id auto-derived as `<node>.eq<i>`.
- Validate `RoomSource(**...)` through pydantic before returning.

### build_room shell

```python
spec = parse(spec_text)
validate(spec)
recipe = emit_recipe(spec)
asy    = emit_asy(spec)
room   = emit_room_source(spec)
if write:
    (out_root/"recipes").mkdir(...); (out_root/"figures").mkdir(...); (out_root/"room_sources").mkdir(...)
    if recipe: write recipes/<node>.f1.json
    write figures/<node>.f1.asy
    write room_sources/<node>.json
return BuildResult(node, recipe_path_or_None, asy_path, room_source_path)
```

### Golden tests (headless; no Asymptote/LaTeX executed — pure text/JSON)

```
test_lemma_2_roundtrip      : the example .room → recipe/asy/room_source DEEP-EQUAL the
                              gold JSONs; .asy string-matches gold structure. THE anchor test.
test_prop_4_equation        : equation room → recipe with FloatLabel term ops + label-only .asy;
                              colors_used = {forceorange,velblue,radgreen} scanned.
test_law_1_text             : text room → recipe_path None, label-only .asy, 4 stations, 9 colors
                              scanned; final_pair_id law_1.s4.
test_reject_missing_heart   : station with no heart → SpecError.
test_reject_undeclared_color: {ghost|x} with no `color ghost` → SpecError.
test_reject_unused_color    : declared color never used → SpecError.
test_reject_step_gap        : stations 1,2,4 → SpecError.
test_reject_global_palette  : `color` before first `station` → SpecError.
test_reject_bad_ref         : undefined ref → SpecError.
test_textcolor_scan_consistency: every \textcolor name in emitted latex ∈ colors_used and
                              vice versa (mirrors baker_text._validate) — for all three gold rooms.
test_ceiling_ids            : ceilings → <node>.eq0, .eq1 with verbatim latex.
```

### INTEGRATION NOTE FOR DEEPSEEK (honest gap — Rule 3)

The only thing not asserted from memory is the exact Asymptote function/method names in the op→snippet library inside emit_asy. Resolution path:
1. The lemma_2 gold .asy already proves: free points, pair, segment, polyline, series (rects loop + curveY helper). Locked by `test_lemma_2_roundtrip`.
2. For remaining ops (conics, tangents, intersect, arc, bisector, foot, …): child writes each snippet against pinned Asymptote docs (DeepSeek pastes), proves each by one compile via `bake/asy_compile.py` on a tiny fixture — the "compile loop confirms the externals" discipline.
3. Snippets not yet confirmed are emitted with `// TODO: confirm <op> against asy docs` and flagged — never silently faked.
4. The first 20-room level leans mostly on points/segments/polylines/series/labels; exotic conic ops grow lazily, one compile at a time.

### WHAT NIR / A CHILD NOW HOLDS

1. **ROOMSPEC.md** (Part I) — the entire format a child needs, plus its room's station map + source text. No JSON, no Asymptote, no `\textcolor`, no global palette is even expressible.
2. **`build/room_from_spec.py`** (Part II) — one tool, run 20× by DeepSeek, pure-core + thin write shell, pydantic-validated output, anchored to the gold lemma_2 triplet, honest about the one external-API gap.

The corrected color model is structurally enforced (colors live only inside stations; uncolored → black not grey; heart is per-step, never cumulative; colors_used is scanned, never authored) — so the misread that burned this project twice cannot be re-expressed in this format.
