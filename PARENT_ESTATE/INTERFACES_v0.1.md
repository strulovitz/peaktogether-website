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
