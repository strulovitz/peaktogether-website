INTERFACE DOCUMENT v0.1 — DESCENT QED ENGINE

(to be committed verbatim to /PARENT_ESTATE/INTERFACES_v0.1.md)
0. Prime law

The engine is mathematics-blind. No module below ever contains a mathematical fact, equation, color-to-concept mapping, or robot name. All of that enters only through corridor files parsed by content_parser. Any module found "knowing math" is a bug.
0.1 Runtime corridor discovery

On startup, app scans ./corridors/*.txt (sorted by filename). The count = N corridors. No number is hard-coded anywhere. N may be 1 or 12 or 100; geometry must cope (see Fibonacci sphere, Part 2).
0.2 Data-object vocabulary (the shared nouns)

These plain data classes are the currency passed between modules. They hold parsed content only — no geometry, no GL, no behavior.

CorridorData
  number:        int
  title:         str
  flavor:        str
  briefing_intro: str
  entry_text:    str
  exit_text:     str
  robots:        list[RobotData]      # in corridor order
  ledger:        ColorLedger           # this corridor's palette (see §Palette)

RobotData
  number:        int
  name:          str
  briefing_hint: str
  problem:       str                   # formal statement, Wikipedia register
  explain:       dict[str,str]         # keys: "mathematician","physicist",
                                        #       "biologist","engineer"
  segments:      list[Segment]         # the problem as tintable side-by-side pieces
  eye_color_key: str                   # ledger key → robots.eye color via palette
  fizzles:       dict[str,str]         # wrong-weapon-name → "why not this tool" text

Segment                               # one tintable piece of an equation
  latex:         str                   # mathtext-safe, $...$ already stripped
  ledger_key:    str | None            # None = neutral/backdropless glue symbol
  exemplify:     list[ValueArc] | None # for the engineer slide only

ValueArc                              # the laser/exemplify "sad-smiley arc"
  latex:         str                   # the sub-expression
  value:         str                   # the concrete number rendered above the arc

0.3 Module list (approved) and one-line contracts
#	Module	Owns	Public entry points (signatures stabilize in Part 2 / each brief)
1	content_parser	File grammar → data objects	parse_corridor(path) -> CorridorData; discover_corridors(dir) -> list[CorridorData]
2	palette	Color ledger + Kindergarten Mixing Law + greyscale rule	ColorLedger.tint(key) -> rgba; ColorLedger.blend(keyA,keyB) -> rgba; ColorLedger.eye(key) -> rgb
3	hub_builder	Fibonacci-sphere directions, hub sphere, N doors	build_hub(n) -> HubGeometry; HubGeometry.direction(i) -> unit_vec3; HubGeometry.door(i) -> DoorFrame
4	corridor_builder	One tube along one direction: stations, plaques, hostage room	build_corridor(corridor_data, direction, hub_radius) -> CorridorGeometry
5	robots	One non-humanoid faceted hull, eye, pods, bob/yaw, hologram, fireball	make_robot(robot_data, palette, station_pose) -> Robot; Robot.update(dt, ship_pose); Robot.draw()
6	reading_system	Fog-layer L1–L4, mouse-wheel depth, segment backdrops, exemplify	ReadingState(robot_data, palette); .scroll(delta); .laser(); .draw(screen_rect, opacity)
7	render	Translucent flat faces + wireframe edges, billboards, GL primitives	draw_wall(quad, tint, edge_rgb); draw_billboard(tex, pose); begin_2d/end_2d; draw_latex_3d
8	weapons	Face-missile/laser, correct→fireball→plaque, wrong→fizzle	WeaponSystem.fire(target, loaded_face) -> HitResult; .laser()
9	game_state	Lock-on, cleared set, loaded weapon, reading depth, progress	GameState.lock(robot); .is_cleared(robot); .load_weapon(name); progress counters
10	app	60 FPS loop, dual-player input map, window, runtime discovery	entrypoint main()
0.4 Dependency order (= child build order)

content_parser ─┐
palette ────────┼─→ (leaves, built & tested first)
                │
render ─────────┴─→ robots ─→ corridor_builder ─→ hub_builder
                          reading_system ─┐
                          weapons ────────┼─→ game_state ─→ app

Build sequence for children: content_parser → palette → render → robots → corridor_builder → hub_builder → reading_system → weapons → game_state → app → INTEGRATION child.

Rationale: the two pure leaves (content_parser, palette) have no graphics and are trivially testable from your screenshots of printed output — lowest risk, perfect for shaking down the PARENT→child→DeepSeek→report loop before any GL is involved.
0.5 Reference-only clause (goes in EVERY brief, verbatim)

    Claude Fable (a previous architect, now unavailable) wrote earlier code for corridors and robots. Ask Nir to paste that old code, and treat it as REFERENCE ONLY. It predates this interface document; it does not know these contracts and did not anticipate a parent/child workflow. Do not copy its structure. Implement the interfaces defined in this brief. You may mine the old code for reusable plumbing (quaternion Ship, TexCache, begin_2d, gamepad handling) only where it matches a contract here, and you must note any such reuse in your completion report.

0.6 DeepSeek-handoff clause (goes in EVERY brief, verbatim)

    Long mechanical/platform work (gamepad & joystick wiring, asset file loading, value tuning after Nir's test flights) is not yours to design. Mark each such spot inline as # TODO(DeepSeek): <exact recipe> | ACCEPTANCE: <check> and also list every TODO again at the end of the file under # === DEEPSEEK TODO SUMMARY ===. DeepSeek commits your verbatim file to GitHub, then works a working copy until acceptance checks pass. He is reliable on mechanical tasks and his bug reports are excellent — write for him generously.

0.7 Completion-report template (every child ends with this)

COMPLETION REPORT — module <name> — <date>
FILES CREATED: <paths>
PUBLIC INTERFACES (final signatures): <verbatim>
DEVIATIONS FROM BRIEF: <none / list with reason>
TRAPS DISCOVERED: <gotchas the next child must know>
OLD-CODE REUSE: <what was mined from Fable's code, if any>
DEEPSEEK TODOS LEFT OPEN: <list>

Nir carries this back; DeepSeek commits it to /PARENT_ESTATE/reports/.
0.8 Hard rules inherited as canon (binding on all children)

    mathtext only. SAFE: \frac \sum \int \geq \leq \cdots \cdot \left( \right) \to \infty \approx \ln \log \pi \zeta \qquad \mathrm{} \mathbf{} \Rightarrow. FORBIDDEN: \tfrac \dfrac \underbrace \color \text, any AMSmath.
    No per-part text coloring, ever — color is backdrop tint quads only (white text on dark tint; black text on light tint).
    Greyscale world / saturated-glow-only: walls dark grey, edges white/light-grey wireframe, background near-black CLEAR_COLOR=(0.045,0.055,0.10). Chroma reserved for meaning (ledger backdrops, robot eyes, holograms, hostage-blue, chevron hazard frames). Therefore any color seen through a wall = content ahead.
    Robots are NEVER humanoid (Body Simplicity Rule, §A.4): one faceted hull + one eye band (ledger color) + two stubby pods + hover-bob + slow yaw. Variation only via size/proportion/2-color paint/eye color.
    Legacy fixed-function GL only; display lists for heavy static geometry (key = rounded state tuple, rebuild on change); draw_latex_3d NEVER inside a display list (TexCache recycles ids).
    At most one new engine concept per build step.
    One voice only — the mine's signage/system voice. No HE:/SHE: speaker tags ever. The voice may ask the players questions, never answer for them.


PART 2 — FORMAT, GEOMETRY, AND DUMMY FIXTURE

(append to INTERFACES_v0.1.md)
1. CORRIDOR FILE FORMAT v0.2 (fattened from v0.1)

Grammar rules (binding on content_parser):

    A file = one corridor. Filename pattern: corridors/NN_slug.txt (e.g. 01_eulers_product.txt). Discovery sorts by filename; the leading number is for human ordering only — the authoritative corridor number is the CORRIDOR: line.
    Blocks are KEYWORD { ... }. Braces may span multiple lines. A literal brace inside text is escaped \{ \}.
    Single-value lines are KEYWORD: value (no braces): CORRIDOR:, ROBOT:.
    Lines beginning # outside any block are comments (this is where the COLOR LEDGER table is duplicated as a comment so DeepSeek sees it — per BIBLE §6).
    Math in any text uses $...$. The parser strips the dollar signs and stores raw mathtext.
    Order is fixed within the file (parser may be strict): corridor header blocks first, then robot blocks. A robot block ends where the next ROBOT: or EOF begins. The engine counts ROBOT: lines — robot count is never declared.

Corridor header blocks (once each, in this order):

CORRIDOR: <int>
TITLE { ... }
FLAVOR { ... }              # optional; default "" ; non-load-bearing
LEDGER { ... }              # NEW — see §1.1
BRIEFING_INTRO { ... }
ENTRY_TEXT { ... }
EXIT_TEXT { ... }

Robot block (repeat; engine counts them; order = corridor order):

ROBOT: <int>
NAME { ... }
BRIEFING_HINT { ... }
PROBLEM { ... }             # formal, Wikipedia register, no softening
EXPLAIN_MATHEMATICIAN { ... }   # graduate level
EXPLAIN_PHYSICIST { ... }       # undergraduate level
EXPLAIN_BIOLOGIST { ... }       # high-school level
EXPLAIN_ENGINEER { ... }        # same content, concrete numbers, value arcs
SEGMENTS { ... }            # NEW — see §1.2
EYE { <ledger_key> }        # NEW — robot eye inherits this ledger color
FIZZLE <weapon_name> { ... }    # NEW — repeatable; one per wrong weapon

1.1 The LEDGER block (encodes the Kindergarten Mixing Law)

This is how color-meaning enters the engine as content, never as code. Format inside the block, one entry per line:

LEDGER {
  PRIMARY  <key> = red
  PRIMARY  <key> = yellow
  PRIMARY  <key> = blue
  BLEND    <key> = <parentKeyA> + <parentKeyB>
}

Rules the parser validates (and reports violations of, rather than silently accepting):

    At most 3 PRIMARY entries; each color one of red | yellow | blue.
    A BLEND may only name two distinct PRIMARY keys; its color is derived by palette, never stated. (red+yellow=orange, yellow+blue=green, red+blue=purple.)
    Any ledger_key used by a SEGMENT or EYE must be defined here, or be the reserved key NEUTRAL (glue symbols: =, parens, \cdots, lone constants → backdropless).
    The parser does not know that "red means harmonic series"; it only enforces the structure of the law. Meaning lives in the author's text. ✔ engine stays math-blind.

1.2 The SEGMENTS block (tintable side-by-side pieces)

Equations are authored as ordered segments because mathtext can't tint mid-formula (BIBLE §6). One segment per line:

SEGMENTS {
  $1$            | NEUTRAL
  $+$            | NEUTRAL
  $\frac{1}{4}$  | termA
  $+$            | NEUTRAL
  $\frac{1}{9}$  | termA
  ... | ...
}

Format: <mathtext> | <ledger_key>. The reading_system lays these out left-to-right, each as its own mathtext texture on its own backdrop quad (or backdropless if NEUTRAL), baseline-aligned with forgiving padding.
1.3 The EXPLAIN_ENGINEER value-arc markup

Inside the engineer text, any expression may be wrapped:

[[ $\frac{\pi^2}{6}$ | 1.6449 ]]

The reading_system renders the expression normally, then draws a downward-opening arc ("sad-smiley mouth" / downward parabola) spanning the expression's width, just above it, with the value text centered above the arc. Exact spec in §3.3.
2. THE HUB & FIBONACCI-SPHERE GEOMETRY (the core engine novelty)

This is the design heart of hub_builder. I'm specifying it precisely so the child has zero room to improvise it badly.
2.1 Direction distribution — Fibonacci sphere

Given N corridors, produce N unit vectors spread as evenly as possible on the sphere so radiating tubes never crowd or intersect. The canonical Fibonacci-sphere placement:

For i=0,1,…,N−1:

zi​=1−N2i+1​,ri​=1−zi2​
​

θi​=i⋅π(3−5
​)

di​=(ri​cosθi​,ri​sinθi​,zi​)

where π(3−5
​)≈2.39996 rad is the golden angle. This guarantees no two directions coincide and spacing is near-uniform for any N from 1 to 12+.

Special small-N readability override (design decision, mine): pure Fibonacci for N=1 points straight along one axis, which is fine; for N=2 it gives antipodal poles, also fine. I keep Fibonacci unmodified for all N — its low-N behavior is already sensible, and a uniform rule beats special-casing. The child must not special-case small N.
2.2 Hub interior (design decision, mine)

    The hub is a faceted sphere (icosphere, ~1 subdivision — flat-shaded, greyscale, wireframe edges per the walls recipe), radius HUB_RADIUS (a tuning constant; propose HUB_RADIUS = 30.0 world units, # TODO(DeepSeek): tune after Nir flight).
    The player spawns at hub center, facing +x.
    Each corridor's door is placed on the hub surface at HUB_RADIUS * d_i, the doorway oriented so its outward normal = d_i. The corridor tube then extrudes from that door along d_i.
    Door frame = the yellow/black chevron hazard frame (BIBLE §A.3), here used at the hub as the corridor mouth, labelled with the corridor TITLE and (later) the author's face. The label billboard floats just inside the mouth, facing hub-center so the player reads it on approach.
    Breadcrumb glow: through the translucent hub wall, each door emits a faint glow in that corridor's dominant ledger color (the first PRIMARY in its LEDGER), so the hub interior reads as a constellation of colored mouths — content beckoning. ✔ greyscale-world rule.

2.3 Non-intersection guarantee

Because all directions come from one shared origin (hub center) and each tube is a straight extrusion along its own di​, two tubes can only meet at the origin, which is hollow hub interior. The Fibonacci spacing keeps angular separation ≳arccos of nearest-neighbor dot product, comfortably larger than the tube's angular half-width for N≤12 at HUB_RADIUS=30. hub_builder must assert min_pairwise_angle(N) > tube_angular_halfwidth + margin and, if it ever fails (huge N), report it rather than render overlapping tubes.
2.4 HubGeometry public interface

build_hub(n: int, hub_radius: float = 30.0) -> HubGeometry
HubGeometry.direction(i: int) -> vec3        # unit, Fibonacci
HubGeometry.door(i: int) -> DoorFrame        # pose + chevron quads + label anchor
HubGeometry.draw()                           # icosphere walls+edges, doors, glows
HubGeometry.spawn_pose() -> Pose             # center, facing +x

3. RENDERING SPECS THAT NEEDED FATTENING
3.1 Walls recipe (binds render)

Each wall quad drawn twice: (a) translucent flat-shaded fill, alpha = 1 - wall_transparency_slider (default 0.5); (b) bright edge lines (GL_LINE, light-grey/white) on top. At slider→0 the fill vanishes → pure automap wireframe; at →1 nearly solid. One slider, two parents blended. (BIBLE §6B.)
3.2 Corridor cross-section

Octagonal tube (BIBLE §A.2), with thin emissive edge-glow strips along the 8 lengthwise corners in the corridor's dominant ledger color. Robot stations are placed at even intervals down the tube centerline; the hostage room (irregular faceted cavern, blue hostage figures) caps the far end.
3.3 Value-arc rendering (the laser/exemplify mark) — exact spec

For a ValueArc over an expression of pixel width w at baseline-top ytop​:

    Draw a downward-opening parabola (sampled polyline, ~16 segments) spanning the expression width with a small horizontal inset (10%), peaking arc_rise pixels above ytop​ at the ends and dipping toward the middle — i.e. a "frown"/sad-smiley mouth. Propose arc_rise = 12 px (# TODO(DeepSeek): tune).
    Render the value text centered horizontally over the expression, its baseline arc_rise + value_gap above ytop​ (value_gap = 4 px).
    Color: the arc + value use the segment's ledger tint if it has one, else neutral light-grey. Text stays white-on-tint per the no-colored-text rule (the value is its own little backdropped segment).

3.4 Reading-system layout (binds reading_system)

Four layers L1–L4 stacked in virtual reading depth (not ship motion):

    L1 EXPLAIN_MATHEMATICIAN (nearest by default), L2 physicist, L3 biologist — read nearest clearly, see next faintly through it (alpha falls with depth). Mouse-wheel moves reading depth, fully reversible; passing a layer fades it out, rolling back restores it.
    Corner labels (tongue-in-cheek, locked): "explain like I'm a mathematician / physicist / biologist".
    Laser/CTRL = exemplify: replaces the current sign in place with the L4 engineer slide (EXPLAIN_ENGINEER + value arcs), corner label "explain like I'm an engineer — by example, with actual numbers".
    Active only while locked on a robot (game_state gates it).
    backdrop_opacity is a user slider (near-transparent ↔ opaque), default mid.

4. DUMMY CORRIDOR FIXTURE (test fixture for the parser child)

This is deliberately math-free filler — placeholder text in every field — so we test engine plumbing, never real content. Save as corridors/01_dummy.txt. It exercises every block, the ledger law, blends, neutral glue, multi-robot counting, value arcs, and fizzles.

# ===========================================================
# DUMMY CORRIDOR — engine test fixture, NO real mathematics.
# COLOR LEDGER (duplicated here for DeepSeek's eyes):
#   PRIMARY alpha = red    (stand-in concept "A")
#   PRIMARY beta  = yellow  (stand-in concept "B")
#   PRIMARY gamma = blue    (stand-in concept "C")
#   BLEND   delta = alpha + beta   -> orange
# ===========================================================
CORRIDOR: 1
TITLE { Placeholder Corridor One }
FLAVOR { A test tube where nothing means anything yet. }
LEDGER {
  PRIMARY alpha = red
  PRIMARY beta  = yellow
  PRIMARY gamma = blue
  BLEND   delta = alpha + beta
}
BRIEFING_INTRO { This briefing page is placeholder text used only to
                 verify that briefing rendering works. }
ENTRY_TEXT { You have entered the placeholder corridor. }
EXIT_TEXT { You have cleared the placeholder corridor. Well done, tester. }

ROBOT: 1
NAME { Dummy Sentinel Alpha }
BRIEFING_HINT { This robot is vulnerable to the placeholder technique FOO. }
PROBLEM { Prove that the placeholder quantity $X$ equals the placeholder
          quantity $Y$ under the stated dummy conditions. }
EXPLAIN_MATHEMATICIAN { Graduate-level placeholder. We assume the reader
          knows what $X$ and $Y$ pretend to be. }
EXPLAIN_PHYSICIST { Undergraduate placeholder. Think of $X$ as a thing and
          $Y$ as another thing. }
EXPLAIN_BIOLOGIST { High-school placeholder. Two quantities are secretly
          the same. }
EXPLAIN_ENGINEER { Plug in numbers: the quantity [[ $X$ | 3.000 ]] meets the
          quantity [[ $Y$ | 3.000 ]], so they match. }
SEGMENTS {
  $X$       | alpha
  $=$       | NEUTRAL
  $Y$       | beta
}
EYE { alpha }
FIZZLE BAR { The technique BAR does not apply here because this is a
             placeholder and BAR is the wrong placeholder. }
FIZZLE BAZ { BAZ fizzles: it solves a different dummy problem. }

ROBOT: 2
NAME { Dummy Sentinel Beta }
BRIEFING_HINT { Vulnerable to the placeholder technique QUX. }
PROBLEM { Express the placeholder $Z$ as a combination of $X$ and $Y$. }
EXPLAIN_MATHEMATICIAN { Graduate placeholder describing the combination. }
EXPLAIN_PHYSICIST { Undergraduate placeholder. }
EXPLAIN_BIOLOGIST { High-school placeholder. }
EXPLAIN_ENGINEER { Numerically, [[ $Z$ | 6.000 ]] is just the parts added. }
SEGMENTS {
  $X$       | alpha
  $+$       | NEUTRAL
  $Y$       | beta
  $=$       | NEUTRAL
  $Z$       | delta
}
EYE { delta }
FIZZLE BAR { BAR still does not apply, even to the second robot. }

What this fixture proves when the parser is done: N=1 corridor discovered; 2 robots counted (never declared); ledger with 3 primaries + 1 blend validated; delta correctly recognized as alpha+beta; NEUTRAL glue accepted; segments parsed with keys; two value arcs parsed; per-robot fizzle dictionaries (BAR,BAZ / BAR) built; EYE keys resolve to ledger entries (alpha, and the blend delta).

That completes the full Interface Document v0.1 (Parts 1 + 2).
