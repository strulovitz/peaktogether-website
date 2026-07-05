# THE APOCRYPHA — HOMEWORLD: A GOOD BASIS
## Module Design: content, campaign, bridge, intel, guidestone — v1.0
## Peak Together — July 4, 2026

---

> ## ⚖️ OWNER AMENDMENTS (add-only, maintained by DeepSeek — READ FIRST) ⚖️
>
> **These are Nir's (the owner's) binding decisions made after this document was written.
> They OVERRIDE anything below that conflicts. Fable's original text is preserved verbatim
> underneath. New amendments are appended to this list.**
>
> **Amendment A1 — SHIPS ARE SOLID, NOT WIREframe (July 5, 2026).** Ships now render as
> **solid, opaque, lit triangle meshes** generated procedurally by `shipwright.py` (per-class
> lofted hulls + wings/fins/masts/towers + emissive nozzles, per-pixel Blinn-Phong). Wherever
> this document describes ship **meshes as "simple wireframes" (vertices + edge lists)** or the
> Mothership/ships as a "wireframe" — that is superseded for RENDERING: ships are solid. (The
> `content/meshes/*.json` wireframe data files may still exist, but the game builds ship hulls
> from `shipwright.py`.) **Only the MATH LAYER** (arrows, grids, ghosts, trails, labels) stays
> glowing holographic, over the solids, depth-tested. (Full text:
> `notes/amendment_a1_art_direction.md` + Old Testament amendments.)

---
## Requires: BIBLE.md v2.1 and NEW_TESTAMENT.md v1.0. Precedence: Bible wins over
## all; New Testament wins over this document on forge/helm/fleet questions; this
## document wins over any later chat on campaign/bridge/intel/content questions.

NOTE TO ALL READERS (human, Opus parent/child, DeepSeek): All mathematics is
written in LaTeX. Inline math is delimited by $...$ and display math by $$...$$.
Subscripts use _, superscripts use ^. Never alter the LaTeX when copying.

---------------------------------------------------------------------------------
PART 0 — SCOPE AND TWO BINDING AMENDMENTS
---------------------------------------------------------------------------------

This document specifies the remaining modules to implementation depth:

  content/    — the data layer: book excerpts, missions as data, ship classes,
                narrator lines, images (Part 1)
  campaign/   — the mission runtime: phases, objectives, event routing, mission
                visuals, progression and saves (Part 2)
  bridge/     — the Navigator's mouse-only console + the Big Picture overlay
                (Part 3)
  intel/      — the Fleet Intelligence narrator (pure text) (Part 4)
  guidestone  — a deliberately tiny subsystem inside campaign (Part 5)

AMENDMENT A — NO AUDIO, EVER (owner decision, July 2026). The game has no sound
and no music. The audio/ directory is REMOVED from the repository layout in
BIBLE.md Part 6. No module may import pyglet.media. Any design text mentioning
music or narrator voice is to be read as TEXT ON SCREEN. Consequence: intel/ is
a pure subtitle system, and all game feedback must be VISUAL (this raises the
importance of glow, color, and motion cues in every mechanic).

AMENDMENT B — THE GUIDESTONE IS A GARNISH, NOT A COURSE (owner decision, July
2026). The SVD image reveal stays in the game (it is Chapter 7 and it is
beautiful) but with a strict effort budget: one ImagePanel on the
mission-complete screen, driven by referee.svd_partial, roughly 50 lines of
code total, zero custom shaders, zero dedicated missions before Mission 15, and
Mission 15 itself simplified (Part 5). No Parent or Child may expand the
Guidestone without owner approval. Rationale: 99% of players judge the game in
the first five minutes; polish flows there first.

THE FIRST-FIVE-MINUTES DOCTRINE (binding on campaign/): from double-clicking
run.bat to a ship visibly flying under the players' command must take UNDER 60
SECONDS: no launcher, no menu tree, no unskippable text. The game boots directly
into Mission 1 (or the last save). Mission 1's opening narrator lines appear
DURING play, never blocking it. Every mission must reach interactivity within
10 seconds of loading. When any implementation choice trades polish between
"early and always seen" and "late and rarely seen", early wins.

---------------------------------------------------------------------------------
PART 1 — CONTENT: THE DATA LAYER
---------------------------------------------------------------------------------

=== 1.1 DIRECTORY LAYOUT (frozen) ===

```
content/
├── book/                    # verbatim excerpts from Strang + Solution Manual
│   ├── ch1_excerpts.json    # one file per chapter, filled as the owner pastes
│   ├── ch2_excerpts.json
│   └── ...
├── missions/
│   ├── m01_kharak_burns.json
│   ├── m02_first_contact.json
│   └── ... (m03..m16)
├── ships.json               # ship class definitions (signatures, meshes, costs)
├── meshes/                  # wireframe ship meshes: vertices + edge lists (JSON)
├── narrator/
│   ├── core.json            # always-loaded lines (rejections, generic events)
│   └── m01.json ... m16.json  # per-mission lines
├── images/
│   ├── guidestone.png       # 128x128 grayscale source image
│   └── cutscenes/           # black-and-white stills between missions (PNG)
└── fonts/
    └── mono.ttf             # the single bundled font (license-checked)
```

=== 1.2 BOOK EXCERPTS (book/chN_excerpts.json) — THE VERBATIM DOCTRINE ===

Every mathematical statement, example matrix, and exercise that the game uses
lives here, and NOWHERE else. Entry format:

```json
{
  "id": "ch2_ex_3_1",
  "kind": "exercise",              // "quote" | "example" | "exercise"
  "cite": "Strang 6e, Section 2.3, Problem 1; solution: Manual p. XX",
  "text": "<verbatim text pasted by the owner>",
  "matrices": { "A": [[2,4,-2],[4,9,-3],[-2,-3,7]], "b": [2,8,10] },
  "solution": { "x": [-1,2,2] },
  "notes": "used by mission m05 as the minefield system"
}
```

RULES: (1) The "text" field is pasted by the owner, verbatim, citation attached
— an AI may trim for length but never rewrite the mathematics. (2) The
"matrices" field is transcribed from the book's OWN example or a solved
exercise. (3) The "solution" field is used ONLY for hints and narrator text —
never as the verdict. The verdict is always recomputed by fleet/referee.py at
runtime (NumPy is the Referee, Bible Part 6): even if a transcription typo slips
into "solution", the game stays self-consistent, because it checks
$\| A x - b \| < \varepsilon$ against the stored $A$ and $b$, not against the
stored $x$. (4) Until the owner pastes a chapter, missions use clearly marked
placeholder entries with "cite": "PLACEHOLDER — replace with book example";
shipping a mission with a placeholder is forbidden.

=== 1.3 SHIP CLASSES (ships.json) ===

```json
{
  "fighter": {
    "display_name": "Fighter",
    "signature": [2, 0, 0, 1, 0, 0],
    "cost": 40, "hp": 30, "trim_speed": 3.0,
    "mesh": "meshes/fighter.json", "scale": 1.0
  },
  "elimination_corvette": {
    "display_name": "Elimination Corvette",
    "signature": [0, 0, 0, 2, 0, 1],
    "cost": 90, "hp": 60, "trim_speed": 1.5,
    "mesh": "meshes/corvette.json", "scale": 1.4,
    "special": "row_conduit"
  }
}
```

Signatures follow the Bible Part 1 roster (channel order K,B,M,S,J,U). The
"special" field names an ability handled by fleet systems: "row_conduit"
(2.5), "inverse_field" (2.6), "row_swap_tow" (2.5), "salvage" (2.4/2.13),
"collector" (2.2). Meshes are simple wireframes: {"vertices": [[x,y,z],...],
"edges": [[i,j],...]} — 20 to 60 edges per ship is the target aesthetic; a
child can author these by hand in a text editor.

=== 1.4 MISSIONS AS DATA (missions/mNN_*.json) — THE SCHEMA ===

A mission is a JSON file plus (optionally) a small Python hook file for logic
that data cannot express. The schema, version 1 (frozen):

```json
{
  "id": "m05_minefield",
  "title": "Minefield",
  "act": 2,
  "book_ref": "ch2_ex_3_1",             // the excerpt this mission teaches
  "intro_cutscene": "images/cutscenes/m05.png",
  "guidestone_rank": 5,                  // singular values awarded on victory

  "setup": {
    "resources": 400,
    "engine_vectors": [[1,0,0],[0,1,0],[0,0,1]],
    "player_ships": [
      {"klass": "fighter", "pos": [10, 0, 5], "squad": 1},
      {"klass": "elimination_corvette", "pos": [8, 0, -3], "squad": 0}
    ],
    "build_menu": ["fighter", "elimination_corvette", "permutation_frigate"]
  },

  "context": {                           // installed into FleetSim (NT 3.2)
    "type": "rowop",                     // "shield"|"grid"|"rowop"|"gate"|
                                         // "swarm"|"relic"|"lstsq"|"none"
    "from_book": "ch2_ex_3_1",           // pulls A, b from the excerpt
    "pylon_positions": [[30,0,20],[0,0,-35],[-30,0,15]],
    "tolerance": 1e-3                    // per-mission epsilon (difficulty)
  },

  "phases": [
    {"id": "arrive",
     "objective_text": "Reach the minefield perimeter",
     "advance_when": {"event": "MISSION_FLAG", "name": "perimeter", "value": true}},
    {"id": "eliminate",
     "objective_text": "Zero the entries below each pivot",
     "advance_when": {"event": "ROWOP_APPLIED", "matrix_is_upper_triangular": true}},
    {"id": "solve",
     "objective_text": "Broadcast the disarm frequencies (back substitution)",
     "advance_when": {"event": "SOLVED", "context_id": "minefield"}}
  ],

  "narrator_file": "narrator/m05.json",
  "victory": {"when_last_phase_done": true}
}
```

The optional hook file campaign/hooks/m05.py may define on_load(api),
on_event(api, event), on_pulse(api) for anything the schema cannot say (e.g.,
"when the second zero appears, spawn two fighters at the east pylon"). Hooks
receive ONLY the MissionAPI (Part 2.3) — never raw module internals. Target:
12 of 16 missions need no hook file at all.

---------------------------------------------------------------------------------
PART 2 — CAMPAIGN: THE MISSION RUNTIME
---------------------------------------------------------------------------------

=== 2.1 FILES ===

```
campaign/
├── __init__.py     # exports Campaign
├── runner.py       # Campaign class: load/advance missions, phases, victory
├── missionapi.py   # MissionAPI: the ONLY surface hooks and schema handlers see
├── visuals.py      # mission visuals: owns VObjects for grids, nullspace lines,
│                   #   spanned boxes, ellipsoids, arrows (per context type)
├── contexts.py     # installers: shield/grid/rowop/gate/swarm/relic/lstsq
├── progress.py     # save file: progress.json (mission reached, fleet save path)
├── guidestone.py   # ~50 lines, Part 5
├── hooks/          # per-mission python hooks (optional)
└── demo.py         # python -m campaign.demo (Part 6)
```

=== 2.2 THE CAMPAIGN CLASS ===

```python
class Campaign:
    def __init__(self, content, fleet, forge, bridge, intel, settings): ...
    def start(self) -> None:
        """Loads progress.json; if absent starts m01. Applies the
        First-Five-Minutes Doctrine: no blocking screens."""
    def on_event(self, ev: "Event") -> None:
        """Wired by app.route_event. Feeds phase triggers, hooks, intel."""
    def on_pulse(self, dt: float) -> None: ...
    def on_frame(self, alpha: float) -> None:
        """Updates mission visuals from fleet.snapshot() (visuals.py)."""
```

Mission lifecycle (frozen): load JSON -> install context into FleetSim ->
build setup ships -> create mission visuals -> show intro cutscene still as a
non-blocking corner inset for 8 seconds (NOT fullscreen; doctrine) -> run
phases in order -> on victory: show mission-complete screen (cutscene still +
Guidestone panel + "press ORDER_CONFIRM to continue") -> write progress.json
and fleet save -> load next mission.

=== 2.3 THE MISSION API (missionapi.py) — the only surface hooks may touch ===

```python
class MissionAPI:
    # reading
    def snapshot(self) -> "FleetSnapshot": ...
    def context(self) -> dict: ...              # the installed mission context
    def phase(self) -> str: ...
    # acting
    def spawn(self, klass: str, pos, enemy: bool = False, squad: int = 0) -> int: ...
    def set_flag(self, name: str, value) -> None:   # emits MISSION_FLAG
    def narrate(self, line_id: str) -> None: ...    # queue a specific line
    def add_visual(self, vob) -> None: ...          # forge VObject, mission-owned
    def remove_visual(self, vob) -> None: ...
    def win(self) -> None: ...
```

Import law: hooks import nothing but numpy and missionapi. Campaign owns all
mission-scoped VObjects and removes them on mission end (no leaks).

=== 2.4 CONTEXT INSTALLERS (contexts.py) — what each mission type wires up ===

For each "context.type", contexts.py installs data into FleetSim and visuals:

- "shield" (Bible 2.3): target ship id, requirement vector $b$, group; visuals:
  per-channel drain bars floating beside the target (rows!), colored
  contribution beams from firing ships (columns!).
- "grid" (Bible 2.7): sensor matrix $A$ from book excerpt rows, station
  positions; visuals: the nullspace rendered via referee.nullspace_basis —
  dimension 1 -> a glowing safe LINE (forge Line, length 400), dimension 2 ->
  a safe PLANE (forge Grid spanned by the two basis vectors); per-station
  readout numbers ($A p$ components) above each station; alarm bar.
- "rowop" (Bible 2.5/2.6): augmented matrix $[\,A \mid b\,]$; pylons at given
  positions; conduit checking (is the Elimination Corvette within distance d of
  the segment between pylon i and pylon j — a point-to-segment distance test);
  visuals: mine banks as WireSphere clusters per matrix entry, a bank powers
  down (glow -> 0.1) when its entry becomes 0.
- "gate" (Bible 2.10): the three frigate ids; per pulse computes
  spanned_volume of their position columns; visuals: SpannedBox on the three
  positions + volume Label; emits GATE_VOLUME.
- "swarm" (Bible 2.11): matrix $A$, region positions, wave state $x_k$; per
  wave x = A @ x; visuals: region markers scaled by swarm mass.
- "relic" (Bible 2.11): matrix $T$, grip radius; per pulse applies $p \mapsto
  T p$ to ships inside the grip (positions relative to relic center); visuals:
  the real eigen-axis drawn as a DashedLine through the relic once the
  Navigator has "computed" it on the console.
- "lstsq" (Bible 2.9): ping list from book excerpt; visuals: pings as small
  WireSpheres, fitted line via referee.least_squares, error vector as a
  perpendicular glowing segment; hull-scrape damage proportional to
  $\|e\|$ while traversing.

This file is where most of the game's total code lives. Estimated sizes:
shield ~120 lines, grid ~150, rowop ~200, gate ~60, swarm ~80, relic ~80,
lstsq ~80. Keep them boring and explicit; no cleverness.

=== 2.5 MISSION 1 REFERENCE FLOW (the most important 5 minutes we will ever build) ===

m01_kharak_burns.json, spelled out as the template all missions copy:

0:00 run.bat -> window opens directly into space: the Mothership wireframe at
     the origin, two Fighters beside it, the XZ reference Grid, stars (tiny
     static points, one Line batch). Subtitle appears DURING play: "Fleet
     Intelligence: Command, our engine vectors are calibrated. Squad 1 awaits a
     combination order."
0:15 The bridge console (right panel) already shows two sliders, $c_1$ and
     $c_2$, and the live preview equation $d = c_1 e_1 + c_2 e_2$. The
     Navigator drags a slider — in the 3D view the arrow $c_1 e_1$ grows, the
     parallelogram construction draws itself, a ghost marker sits at the tip.
     THE FIRST TOUCH OF THE MOUSE ALREADY MAKES SOMETHING BEAUTIFUL HAPPEN.
0:30 Pilot presses ORDER_CONFIRM: the squad flies the diagonal. First narrator
     beat: "Combination executed."
1:00-4:00 Three waypoint targets, each teaching one thing: (a) a target on the
     $e_1$ axis (one slider), (b) a target needing both sliders, (c) a target
     needing a NEGATIVE coefficient (subtitle: "Negative scalars reverse the
     vector, Command."). A wrong order is never punished: the ghost marker
     shows where the combination WOULD land; the fleet only commits on CONFIRM.
4:30 A damaged freighter limps in at position exactly $2 e_1 + 3 e_2$;
     spawning the phase objective "bring the squad alongside" — the couple
     must read a position AS a combination for the first time (inverse
     thinking: given $d$, find $c_1, c_2$ — the console shows an empty
     $c_1 \cdot (1,0,0) + c_2 \cdot (0,1,0) = (2,?,3)$ hint card).
5:30 Victory; mission-complete screen; the Guidestone panel shows its first
     faint rank-1 shimmer with one quiet subtitle line. Total code beyond the
     schema: hook file of ~40 lines.

=== 2.6 PROGRESSION AND SAVES (progress.py) ===

progress.json: {"mission": "m05_minefield", "fleet_save": "saves/fleet_m05.json",
"guidestone_rank": 4, "settings_version": 1}. Written on every victory. run.bat
resumes it. "New campaign" = deleting the file via a single console button on
the mission-complete screen (no menu system exists; doctrine).

---------------------------------------------------------------------------------
PART 3 — BRIDGE: THE NAVIGATOR'S CONSOLE AND THE BIG PICTURE
---------------------------------------------------------------------------------

=== 3.1 THE 2D OVERLAY — INTERFACES AMENDMENT v1.1 (owner-approved by accepting
        this document) ===

forge gains a minimal screen-space layer, drawn after bloom (crisp, no glow
bleed), coordinates in window pixels, origin bottom-left (matching
PointerState):

```python
Rect2D(x, y, w, h, color, filled=False)
Line2D(x0, y0, x1, y1, color)
Label2D(text, x, y, px=16, color=(1,1,1,1))   # reuses the glyph atlas
Image2D(image, x, y, w, h)                     # reuses ImagePanel texture path
```

These four are the ENTIRE UI vocabulary. INTERFACES.md gains them as v1.1.
No other UI additions without a new amendment.

=== 3.2 FILES ===

```
bridge/
├── __init__.py    # exports Bridge
├── widgets.py     # Button, Slider, MatrixGrid, ValueReadout, HintCard
├── console.py     # Bridge class: layout, panel switching per context type
├── bigpicture.py  # the four-subspaces overlay
└── demo.py        # python -m bridge.demo (Part 6)
```

=== 3.3 THE WIDGET KIT (widgets.py) — mouse-only, deliberately tiny ===

```python
class Widget:
    rect: tuple[float, float, float, float]      # x, y, w, h in pixels
    def draw(self, overlay) -> None: ...
    def on_pointer(self, ps: "PointerState") -> None: ...

Button(label, on_click)
Slider(label, lo, hi, step, on_change)           # drag knob; wheel = fine step
MatrixGrid(rows, cols, editable_mask, on_edit)   # displays a numpy array;
    # editable cells cycle value by wheel / click-drag; used for the augmented
    # matrix, throttle vectors, coefficient entry, probe matrices (2.13)
ValueReadout(label, fmt)                          # e.g. "RANK 3/6", "det 5.98"
HintCard(text_lines)                              # boxed multi-line text; used
    # for book-quote hints, with citation line rendered small underneath
```

Interaction model: Bridge.on_pulse receives PointerState from helm (via app),
performs rectangle hit-testing top-down, routes to the active widget; a drag
captures the pointer until release. There is no focus system, no keyboard input
to widgets EVER (Iron Rule: keyboard belongs to the Pilot), no scrolling
layouts. If a panel doesn't fit, the panel has too many widgets — redesign it.

=== 3.4 CONSOLE LAYOUT (console.py) ===

The right 30% of the window, three stacked zones (top to bottom):

1. FLEET ZONE (always visible): MatrixGrid showing the fleet matrix $A$ —
   columns are ships (column header = tiny ship glyph + squad number), the 6
   rows are labeled K,B,M,S,J,U; ValueReadouts: "RANK r/6", resources; the
   selected ship's column highlighted (selection follows the Pilot's TAB —
   shared state, one more forced conversation).
2. CONTEXT ZONE (swaps per mission context type — this is where each Bible
   mechanic gets its controls):
   - shield: throttle Sliders per group ship + residual ValueReadout + "LEAST
     SQUARES" Button (regime 2) — the button is DISABLED (greyed, with hint
     card "target in column space — exact solution exists") when
     referee.is_solvable is true.
   - grid: per-station readouts of $A p$ components + "JAM" Buttons + nullspace
     dimension readout "$\dim N(A) = 3 - r$".
   - rowop: the augmented MatrixGrid + multiplier Slider + "SUBTRACT" /
     "SWAP" / "SCALE" Buttons + back-substitution entry row.
   - gate: volume ValueReadout + per-frigate distance readouts.
   - swarm/relic: the matrix on display + "COMPUTE EIGENVECTORS" Button
     (fills readouts + tells campaign to draw the axis DashedLine).
   - lstsq: ping list with per-ping "EXCLUDE" toggles + $(C, D)$ readout +
     $\|e\|$ readout.
3. BUILD ZONE: Buttons for build_menu klasses with costs; research Buttons
   when the mission grants them; each build Button shows a one-line
   consequence preview: "+column (INDEPENDENT — rank 4 -> 5)" or "+column
   (dependent — throughput only)", computed live by referee on the candidate
   signature. THIS PREVIEW IS THE $A = CR$ ECONOMY MADE VISIBLE (Bible 2.4).

Bridge translates widget actions into fleet orders (NT 3.3) and submits them
through the same queue as the Pilot. Bridge never mutates fleet state directly.

=== 3.5 THE BIG PICTURE OVERLAY (bigpicture.py) ===

Toggled by a console Button (mouse — it belongs to the Navigator). A
translucent full-screen diagram of Strang's "Big Picture" for the ACTIVE
mission matrix (grid/rowop/lstsq contexts; button disabled otherwise):

- Left half: $\mathbb{R}^n$ (input space) — two boxes: ROW SPACE (dimension
  $r$) and NULLSPACE (dimension $n - r$).
- Right half: $\mathbb{R}^m$ (output space) — two boxes: COLUMN SPACE
  (dimension $r$) and LEFT NULLSPACE (dimension $m - r$).
- Arrows: row space -> column space (labeled "$x_r \mapsto A x_r$"), nullspace
  -> the zero point of the right half (labeled "$A x_n = 0$").
- All four dimension labels are LIVE (they update when the Navigator jams a
  station and $r$ drops — the nullspace box visibly grows; ~10 lines of code,
  enormous payoff).
- Rendering: Rect2D + Line2D + Label2D only. Estimated total: ~120 lines.
- Unlocks in Mission 9 (Bible campaign) and stays available thereafter.

---------------------------------------------------------------------------------
PART 4 — INTEL: THE NARRATOR (PURE TEXT)
---------------------------------------------------------------------------------

=== 4.1 FILES: intel/__init__.py (exports Intel), intel/lines.py, intel/demo.py ===

=== 4.2 LINE FORMAT (content/narrator/*.json) ===

```json
{
  "id": "m05_pivot_zero",
  "on": {"event": "PIVOT_ZERO"},
  "text": "A dead pylon in the pivot position, Command. We must exchange rows — Permutation Frigate standing by.",
  "cite": "",              // REQUIRED non-empty when text states mathematics
  "tags": ["teach"],       // "teach" | "story" | "reject" | "flavor"
  "cooldown_s": 30,
  "once": false
}
```

=== 4.3 THE INTEL CLASS ===

```python
class Intel:
    def __init__(self, content) -> None: ...
    def on_event(self, ev: "Event", mission_id: str) -> None:
        """Finds candidate lines (core.json + current mission file) matching
        ev.kind and optional data filters; drops lines on cooldown or already
        shown (once); picks the least-recently-shown; enqueues it."""
    def queue_line(self, line_id: str) -> None: ...    # MissionAPI.narrate
    def on_frame(self) -> None:
        """Draws the subtitle bar: bottom 10% of the 3D viewport, Label2D,
        max 2 lines visible, each fades after 7 seconds. Queue cap 3;
        overflow drops 'flavor' first, then oldest."""
```

=== 4.4 TONE RULES (binding on everyone writing lines) ===

(1) NEVER punishing: every ORDER_REJECTED line explains and suggests — the
canonical example remains: "Admiral, that combination lies outside our column
space. Suggest adding an independent vessel." (2) Mathematical sentences are
sourced/adapted from content/book excerpts with the cite field filled; flavor
and story lines are free-written but contain no mathematics. (3) Short: max
140 characters per line, because there is no voice — with Amendment A the
subtitle IS the narrator, so it must be glanceable during play. (4) Teach
lines fire on the FIRST occurrence of a phenomenon, then respect cooldowns —
the couple should explain things to each other; the narrator only opens doors.

---------------------------------------------------------------------------------
PART 5 — THE GUIDESTONE (DESCOPED PER AMENDMENT B)
---------------------------------------------------------------------------------

campaign/guidestone.py, complete specification:

```python
class Guidestone:
    def __init__(self, content) -> None:
        """Loads images/guidestone.png as (128,128) float64 in [0,1]."""
    def panel(self, rank: int) -> "np.ndarray":
        """Returns referee.svd_partial(G, rank)[0], clipped to [0,1]."""
    def energy(self, rank: int) -> float: ...
```

Usage (the WHOLE feature): on the mission-complete screen, an Image2D shows
panel(rank_reached) with the caption "GUIDESTONE — rank {k} of 16 — signal
energy {energy:.0%}", plus ONE narrator story line. That is all. Budget: ~50
lines, one afternoon, zero maintenance. Mission 15 simplification: the
"transmit" mission keeps its defense gameplay and the rank-$k$ choice Slider
(cost readout $k(m+n+1)$ numbers vs $m \cdot n$ — two Label2Ds), but drops any
custom transmission visualization: the existing panel image + a progress bar
suffice. If players love the Guidestone, expansion can be APPROVED LATER — the
cheap version ships first.

---------------------------------------------------------------------------------
PART 6 — ACCEPTANCE DEMOS (HUMAN-EYES DEFINITIONS OF DONE)
---------------------------------------------------------------------------------

python -m bridge.demo — EXPECTED: game window with only the console panel
active on a dark background. A fake 6x4 fleet matrix is displayed; clicking a
build button prints the order to the console log area and the rank readout
updates ("RANK 3/6" -> "4/6" for the independent ship, unchanged for the
dependent one, whose button preview says "dependent — throughput only");
dragging the multiplier slider and pressing SUBTRACT updates the augmented
MatrixGrid and a zero entry visibly appears; the BIG PICTURE button overlays
the four-subspace diagram with dimensions matching the readout ($r = 2$,
$n - r = 1$, $m - r = 0$ for the demo matrix). Mouse only; pressing keyboard
keys does nothing in the panel.

python -m campaign.demo — EXPECTED: boots straight into Mission 1 exactly as
the reference flow in Part 2.5 describes, with fleet+forge+helm+bridge+intel
all live. This demo IS the game's vertical slice; when it matches Part 2.5,
the project has its first shippable artifact.

python -m intel.demo — EXPECTED: console prints the chosen line for a stream
of synthetic events; demonstrates cooldown (the same event twice within 30 s
prints only once), the "once" flag, and queue overflow dropping flavor lines
first.

---------------------------------------------------------------------------------
BUILD SEQUENCE FOR THESE MODULES (child-sized packages, after NT step 9)
---------------------------------------------------------------------------------

1. content loader (ContentDB: read/validate all JSON, fail loudly on schema
   errors) + ships.json + two hand-authored wireframe meshes.
2. forge 2D overlay (INTERFACES v1.1) + widgets.py + console FLEET ZONE.
3. campaign runner + progress + "none" context + Mission 1 (schema, hook,
   narrator file) -> the vertical slice (campaign.demo passes Part 2.5).
4. intel + narrator core.json.
5. contexts: rowop (hardest, do first) -> shield -> grid -> gate.
6. Missions 2-8 as data files against finished contexts.
7. Big Picture overlay + Mission 9.
8. contexts lstsq/swarm/relic + Missions 10-14.
9. guidestone.py (one afternoon) + Missions 15-16.

END OF THE APOCRYPHA. The scriptures are now complete: BIBLE.md (vision and
mechanics), NEW_TESTAMENT.md (forge/fleet/helm), APOCRYPHA.md (content/
campaign/bridge/intel/guidestone). A new Parent reading all three in order
knows everything this project is, why, and how to build it.
