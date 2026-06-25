🗝️ QUAKE (Game 3) — LEG 2 (THE WALLS): FROZEN CHILD BRIEFS by Parent 2

Captured June 25, 2026, at Nir's request, VERBATIM / word-for-word, AS-IS. This is Parent 2 of Quake — Claude Opus 4.8, run ALONE (not Fusion), at "normal" reasoning effort — answering the forced missions in the Parent 2 handoff. This is Parent 2's second deliverable: Mission 2 (Leg 2 — THE WALLS) frozen child briefs. Nothing below is edited.

--- BEGIN VERBATIM ---

I have all three blocks. These are excellent, tightly-specified contracts — and they resolve every fork I pre-flagged. I can now freeze Leg 2.

First, the reconciliations the verbatim text just settled — so you see I'm designing with these contracts:

    My baker_text watch-item: CONFIRMED. §3.A.6 defines TextBlock (a model with block_id, latex, groups_used), and the \cg{group}{…} span convention. So the NT §2.8 bake(latex: str, color_groups: dict, …) signature was a sketch — the real input is the TextBlock model. I freeze baker_text to take TextBlock (consistent with Leg-1 taking models, not strings). The groups_used list is the validation hook (every \cg group must be listed and must exist in palette).

    My baker_figure watch-item: CONFIRMED but nuanced. baker_figure takes the figure.asy path (not the recipe) — because by bake time the EMITTER has already produced .asy and the compile loop has closed. The Recipe (§3.A.4) is the READER/EMITTER's concern and prooffig_check's lint target; baker_figure operates on the compiled .asy. So baker_figure(figure_asy: Path, n_steps, …) stays — but n_steps should come from the Recipe/figure, and I'll thread it explicitly. Good: the NT signature holds here.

    Draw.marker narrowing — TWO sources, ONE truth. §3.A.4's Draw class body literally shows Literal["none","dot","tick"], but the locked inline commentary immediately below amends it to ["none","dot"] ("tick" dropped, half-wired). The iron rule: I freeze ["none","dot"] (the commentary supersedes the class body). prooffig_check lints for this. The prooffig.asy drawAll only handles none/dot anyway — confirming the narrowing.

    Manifest is AssetEntry/Manifest keyed by asset_id, NOT the NT's flat block_id sketch. §4.6 gives the real shape: kind enum (figure_off/figure_on/text_off/text_on/ceiling_neutral), wall_path+master_path (two tiers — resolves the OT §7 "two DPI tiers"), dpi, and a fixed asset-id grammar. The bakers emit list[AssetEntry] (or a dict[asset_id, AssetEntry]); I'll freeze them to return AssetEntry lists and let an orchestrator assemble the Manifest.

    The asset-id grammar is the boundary that Block C confirms. §4.6: figure_off → <figure_id>.off, figure_on → <figure_id>.on.<k>, text_off → <text_block_id>.off, text_on → <text_block_id>.on. Block C's PanelPairRT references exactly drawing_off_asset/drawing_on_asset/text_off_asset/text_on_asset. So the baker's asset_ids ARE what room_maker reads. My read-only boundary check: ✅ the grammars match — baker_figure emitting prop_1.f1.off / prop_1.f1.on.3 and baker_text emitting prop_1.s3.txt.off / prop_1.s3.txt.on is precisely what PanelPairRT consumes. I freeze the bakers to emit exactly these id forms. No room redesign; the boundary is clean.

    One subtlety in the id forms — figure_id vs block_id. §3.A.4 figure_id = <node_id>.f<n> (e.g. prop_1.f1). §4.6 figure asset_id = <figure_id>.off → prop_1.f1.off. But Block C says block_id for drawing = <node_id>.s<step>.fig and "the manifest asset-id grammar uses these block_ids as prefixes: prop_1.s3.fig.on.3." This is a genuine tension — §4.6 keys figures by figure_id (prop_1.f1.on.3) while Block C's note keys them by drawing-block_id (prop_1.s3.fig.on.3). I resolve it below (it's the one thing I won't silently pick) — see §E flag. It does not block the briefs; it's a one-line id-source decision DeepSeek must confirm.

    bg_key = #FF00FF (magenta) is the flat key-out color. §3.A.7 names it; §2.4 reserves it. So baker_figure renders on magenta then keys it to transparency (Pillow), per NT §2.4 — "more robust than Asymptote's own transparency." Frozen.

    series registers as N separate elem() calls under one (group,step). §3.A.5's series realization pattern + the "elem ×N" note: the whole family lights as one step. prooffig_check must NOT require one-elem-per-op for series — it's one op → N elems. I'll account for this in the lint.

MISSION 2 — LEG 2 (THE WALLS): FROZEN PACKAGE
§A — The pipeline (confirming NT §2.2, with contracts bound)

page scan (Nir fetches) ──[crop]──► fig_crop.png
   │
   ▼
[R] READER AI  ─► recipe.<figure_id>.json   (§3.A.4 Recipe model — coordinate-free op-list)
   │
[Rt] TEXT AI   ─► TextBlock (§3.A.6) inside room_<node_id>.json   (\cg spans)
   │
   ▼
[validate] validate.recipe + prooffig_check.lint   (math-free static checks)
   │
[E] EMITTER AI ─► figure.<figure_id>.asy   (§3.A.5 4-zone template, against prooffig.asy + Op list + pinned asy docs)
   │
   ▼
[K] asy_compile.compile()  ──error?──► paste verbatim error to EMITTER ──► loop  (mechanical)
   │ ok
   ▼
[V] overlay_diff.run(scan, render)  ── Nir's eyes, white-shine-through ──► describe mismatch ──► EMITTER ──► [K]
   │ "more or less right"
   ▼
[B1] baker_figure.bake(figure.asy, n_steps) ─► off + on_1..on_N  AssetEntry[]  (key out bg, trim, 2 tiers)
[B2] baker_text.bake(TextBlock)             ─► text_off + text_on AssetEntry[]
   │
   ▼
manifest.json (§4.6)  ──► assets.load_pack ──► room_maker (PanelPairRT) ──► WALLS (Mode B)

Color one-source-of-truth: palette_gen.gen(palette.json) → palette.asy (hi/ink/greyInk) + palette.tex (\definecolor per group). Run once per pack, before any bake. prooffig.asy imports palette.asy; baker_text's preamble imports palette.tex.
§B — Module set (the frozen Leg-2 children)

bake/palette_gen.py      palette.json (§3.A.7) → palette.asy + palette.tex
bake/recipe_validate.py  validate a Recipe (§3.A.4) — the constructibility + type checks   [NEW vs NT]
bake/prooffig_check.py   static lint of a figure.asy (§3.A.5 template + palette + steps)
bake/asy_compile.py      run asy with -u params; capture stdout/stderr verbatim; never raise
bake/baker_figure.py     figure.asy + n_steps → off/on AssetEntry[] (key out, trim, 2 tiers, dedup off)
bake/baker_text.py       TextBlock + palette → text_off/text_on AssetEntry[]
tools/overlay_diff.py    Tkinter+Pillow+NumPy white-shine-through verifier (pure helpers testable)

Seven modules. I'm adding recipe_validate.py (the NT folded recipe-validation into "validate.recipe + prooffig_check"; §3.A.4's validation rules are substantial and pure — they deserve their own testable module, exactly as Leg 1 separated citation_normalize from merge). prooffig_check stays a separate, text-level lint of the .asy; recipe_validate checks the JSON recipe (constructibility, ref resolution, type compatibility). Two different artifacts, two checkers.
§C — FROZEN CHILD BRIEFS

    Anti-regression clause (every brief): Tests must pass on these exact fixtures, byte-for-byte where exact output is given. Frozen signatures are Architect-gated; extra="forbid", schema_version asserted on load. The §3.A.4 example recipe (prop_1.f1), the §3.A.6 TextBlock (prop_1.s3.txt), the §3.A.7 palette, and the §4.6 manifest examples are the canonical fixtures.

    External-API honesty (NT §2.5 + Iron Rule #3): No brief asserts Asymptote function signatures from memory. Asymptote names live only inside the .asy files the EMITTER writes against the pinned asy_geometry_reference.txt; the ⟨…⟩ placeholders in §3.A.5 are confirmed by the compile loop. Our Python modules never name an Asymptote function — they only invoke the asy binary and parse its text output.

C1 — bake/palette_gen.py

Frozen signature: def gen(palette: Palette, out_asy: Path, out_tex: Path) -> None
(Takes the parsed Palette model, §3.A.7 — not a raw path — so it's pure-logic-testable via a separate IO-thin wrapper. DeepSeek may add gen_from_file(palette_json: Path, …) that loads + calls gen.)

Behavior:

    Emit palette.asy defining: pen hi(string g), pen ink(string g), pen greyInk — exactly the three symbols prooffig.asy accesses via access "palette.asy" as pal. hi(g) returns the group's hi hex as an Asymptote rgb(...) pen; ink(g) the ink hex; greyInk = grey_ink. Unknown group → an Asymptote-level error (frozen: emit a hi/ink that aborts on an unknown key, so a bad group fails the compile loudly).
    Emit palette.tex defining \definecolor{<group>}{HTML}{<hex-without-#>} for every group's ink (the \cg{group}{…} text color), plus \definecolor{grey_text}{HTML}{…}. Also define the \cg macro itself (frozen: \newcommand{\cg}[2]{{\color{#1}#2}}) so text blocks compile.
    Hex → component conversion: #RRGGBB → Asymptote rgb(r/255,g/255,b/255) and → LaTeX HTML 6-digit.

Contract: pure given Palette (writes two text files; deterministic byte output).

Tests (exact golden):

    The §3.A.7 example palette → palette.asy contains hi/ink/greyInk and a branch for each of path/radius/construction/tangent/swept_area; palette.tex contains \definecolor{radius}{HTML}{1E6FE0} (the ink of radius), \definecolor{grey_text}{HTML}{8A8A8A}, and the \cg macro. Byte-stable.
    A group whose ink="#E8A200" → palette.tex has {HTML}{E8A200}; palette.asy has rgb(0xE8/255, ...) form (exact emitted string pinned).
    Missing reserved key (grey_ink) in input → Palette validation already rejects it (model-level); gen never sees it. (Reserved-key presence is enforced by the Palette model, not gen.)

C2 — bake/recipe_validate.py [NEW]

Frozen signature: def validate_recipe(recipe: Recipe, palette: Palette) -> list[str]
returns plain-English violation strings (empty list = valid). (Returns rather than raises, like Leg-1 sanity.check — the orchestrator decides to fail.)

Behavior — enforce EXACTLY the §3.A.4(c) rules:

    figure_id startswith node_id + ".f".
    len(steps) == n_steps; step indices exactly 1..n_steps, unique.
    All op.name unique; every Ref resolves to an earlier op (forward refs forbidden → constructibility order). (A Ref is an op.name string.)
    Type compatibility (frozen table — derived from the op vocabulary): point-args (a/b/center/through/point/vertex/frm/to/p1..p5/f1/f2/major_end/minor_end/focus/at-as-point) must reference point-producing ops (free_point, point_on, intersect, midpoint, foot, reflect_point); line-args (to in parallel/perpendicular, over in reflect_point, line in foot, directrix in parabola_fd) must reference line-producing ops (line, parallel, perpendicular, tangent_at, tangent_from, bisector, ray); curve-args (curve in tangent_*, path in point_on, a/b in intersect when a curve, to_curve/along in series) must reference curve/path producers (circle_*, circle_3, arc, ellipse_*, parabola_fd, hyperbola_foci, conic_5, segment, line, ray, polygon, polyline); series.along must be segment or arc.
    Every drawn op's draw.step ∈ 1..n_steps.
    Every step 1..n_steps has ≥1 drawn op (else on_k == off).
    circle_cr has exactly one of radius_points/radius_value.
    FloatLabel (op="label") must have draw set with a label.
    Every draw.group exists in palette.groups.
    marker ∈ ["none","dot"] (the locked narrowing — reject "tick" even though the model once allowed it; belt-and-suspenders since the frozen model is now narrowed).
    Coordinate fields (rough_xy, near, offset, t) never affect validity — only the EMITTER's starting guess. The validator must ignore them for pass/fail.

Contract: pure, deterministic, no IO.

Tests (exact golden):

    The §3.A.4(b) verbatim example recipe (prop_1.f1) → [] (valid). This is the headline fixture.
    Planted: a Ref to a later op → "FORWARD_REF: 'Cc' references 'c' which is defined later" (exact string).
    Planted: step 2 has no drawn op → "EMPTY_STEP: step 2 has no drawn element (on_2 would equal off)".
    Planted: circle_cr with both radius_points and radius_value → exact violation.
    Planted: intersect.a references a free_point (a point, not a curve/line) → type-compat violation.
    Planted: draw.group="ghost" not in palette → group violation.
    Planted: marker="tick" → marker violation.

C3 — bake/prooffig_check.py

Frozen signature: def lint(figure_asy: Path, palette: Palette, n_steps: int) -> list[str]
returns plain-English violations (empty = clean). Text-level only; no Asymptote execution (that's asy_compile's job).

Behavior — enforce the §3.A.5 template invariants by text scan:

    File import prooffig; present.
    Declares int highlight=-1;.
    Ends (last non-comment statement) with drawAll(highlight);.
    The 4 zones present in order (recognize by the ZONE 1..4 comment markers OR structurally: settings → construction → registration → render). Frozen: require the four ZONE comment markers (the template mandates them).
    Parse every elem(...)/lbl(...) call: extract its group (2nd-or-group-position string arg) and step (int arg). Every group exists in palette.groups (or is a reserved key). Steps used are a subset of 1..n_steps, and contiguous from 1 (every step in 1..n_steps appears in ≥1 elem/lbl). (This is the .asy-side mirror of recipe_validate's "every step has a drawn op" — catches an EMITTER that dropped a step.)
    series awareness: multiple elem(...) with the same (group,step) are allowed (one recipe op → N elems). Do NOT flag duplicate (group,step).
    marker arg, if present, ∈ ["none","dot"].

Contract: pure, deterministic, no IO beyond reading the text file. (Robust to whitespace; regex-based extraction — flagged as best-effort text parsing, with the compile loop as the real gate.)

Tests (exact golden):

    The §3.A.5 verbatim figure.prop_1.f1.asy with n_steps=3, the §3.A.7 palette → [].
    Planted: missing import prooffig; → exact violation.
    Planted: no drawAll(highlight); → exact violation.
    Planted: an elem(..., "ghost", 1) group not in palette → group violation.
    Planted: n_steps=3 but no step-2 elem/lbl → "STEP_GAP: step 2 never registered".
    Two elem with (swept_area, 3) (series) → NOT flagged.

C4 — bake/asy_compile.py

Frozen signature:
def compile(src: Path, out_stem: Path, params: dict[str, str], cfg: "AsyConfig") -> AsyResult

class AsyResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ok: bool
    outputs: list[Path]
    stderr: str
    stdout: str

class AsyConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    asy_binary: str = "asy"
    out_format: str = "png"          # confirm exact -f flag value from asy docs file
    dpi: int = 220
    extra_flags: list[str] = []

Behavior:

    Invoke the asy binary with: each params item as a -u "k=v" flag (e.g. highlight=2), the output format/DPI flags (exact flag spellings confirmed from asy_geometry_reference.txt / asy --help, NOT hardcoded from memory — the brief says "confirm exact flags from the docs file, do not hardcode guesses"; the child documents the flags it used), src, and out_stem.
    Capture stdout + stderr verbatim. Never raise on an Asymptote/LaTeX error — return ok=False with the full text (this is the copy-paste-to-EMITTER payload). ok=True only on zero exit AND expected output file(s) present.
    outputs = the produced file paths.

Contract: the only module that runs an external process. All other modules are pure. Subprocess invocation is isolated here.

Tests (monkeypatch the subprocess — no real asy in CI):

    Monkeypatch to a fake that records argv: assert each params entry appears as a -u "k=v" token, in sorted-key order (frozen: params emitted in sorted key order for determinism), and the format/dpi flags appear.
    Fake returns non-zero exit + stderr text → ok=False, stderr preserved verbatim, no exception.
    Fake returns zero exit + creates the expected output file → ok=True, outputs lists it.
    Fake returns zero exit but no output file → ok=False (frozen: missing-output is a failure).

C5 — bake/baker_figure.py

Frozen signature:
def bake(figure_asy: Path, figure_id: FigureId, n_steps: int, out_dir: Path, palette: Palette, cfg: "BakerFigureConfig", *, compile_fn=asy_compile.compile) -> list[AssetEntry]

class BakerFigureConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    wall_dpi: int = 220
    master_dpi: int = 440
    alpha_threshold: int = 16        # bg-key tolerance for transparency
    trim_padding_px: int = 8

(compile_fn injected → testable with a fake compiler returning canned PNGs, per NT §2.8.)

Behavior (NT §2.4 + §4.6 grammar):

    Render off once: compile_fn(figure_asy, out, {"highlight":"-1"}, …) at wall_dpi and master_dpi.
    For each k ∈ 1..n_steps: compile_fn(…, {"highlight":str(k)}, …) at both tiers.
    Key out palette.bg_key (the flat magenta) to transparency via Pillow (NumPy mask within alpha_threshold). Trim transparent margins; add trim_padding_px; record content_bbox (§2.3 pixel convention: top-left origin, half-open) + px_w/px_h.
    Dedup off: emit ONE figure_off AssetEntry (asset_id = f"{figure_id}.off"), shared across all steps. Emit one figure_on per step (asset_id = f"{figure_id}.on.{k}", kind="figure_on").
    Each AssetEntry: wall_path (wall-dpi PNG), master_path (…@master.png), px_w/px_h (of the wall tier), content_bbox, dpi=wall_dpi.
    Return list[AssetEntry] of length 1 + n_steps (one off + N on).

Contract: orchestrates compile (injected) + pure Pillow/NumPy image ops. The image helpers (key_out, trim, bbox) are separate pure functions (NumPy-array in/out) tested headless.

Tests (fake compile_fn returns canned PNGs):

    n_steps=3 → exactly 1 + 3 = 4 AssetEntries; off deduped (one prop_1.f1.off); on ids prop_1.f1.on.1/2/3. Asserts compile_fn was asked for off (once per tier) + 3 ons (per tier) → frozen call count.
    A canned PNG with a magenta border + black ink → key_out makes magenta transparent; trim yields the exact content_bbox; px_w/px_h correct.
    kind fields correct (figure_off/figure_on); asset_id grammar matches §4.6 exactly.
    Boundary assert: the emitted asset_ids (prop_1.f1.off, prop_1.f1.on.3) are exactly what PanelPairRT.drawing_off_asset/drawing_on_asset would reference (§E flag #1 governs whether the key is figure_id or block_id — test pins whichever DeepSeek confirms).

C6 — bake/baker_text.py

Frozen signature:
def bake(text_block: TextBlock, palette: Palette, out_dir: Path, cfg: "BakerTextConfig", *, compile_fn) -> list[AssetEntry]

class BakerTextConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    wall_dpi: int = 220
    master_dpi: int = 440
    alpha_threshold: int = 16
    trim_padding_px: int = 8
    preamble: str = ""    # standalone+amsmath+amssymb+mathtools+xcolor+varwidth; injected, not hardcoded-from-memory

(compile_fn here invokes Tectonic — the LaTeX engine, OT §11/§12.6 — injected for testability. The \cg macro + \definecolors come from palette.tex, included in the preamble.)

Behavior (§3.A.6 + NT §2.4 + §2.6):

    Validate (frozen, before baking): every group in a \cg{group}{…} span appears in text_block.groups_used; every groups_used entry exists in palette.groups. Violations → raise (this is a build-time content error). (The "LaTeX compiles" gate is the compile_fn result.)
    Wrap text_block.latex in the standalone template + palette.tex:
        off (grey): redefine \cg{g}{x} → render x in grey_text (frozen: off-preamble overrides \cg to ignore the group color and use grey_text). All text grey.
        on (colored): \cg{g}{x} → x in group's ink color (the normal \cg from palette.tex).
    Compile both via compile_fn (Tectonic) at wall_dpi + master_dpi. Key out / trim transparent (same pixel rules as baker_figure); record bbox.
    Emit two AssetEntries: text_off (asset_id = f"{block_id}.off", kind="text_off") and text_on (asset_id = f"{block_id}.on", kind="text_on").
    Return [off_entry, on_entry].

Contract: orchestrates Tectonic (injected) + pure image ops (shared with baker_figure — factor key_out/trim into a shared bake/_imageops.py helper, both bakers import it; the helper is the pure-tested unit).

Tests (fake compile_fn):

    The §3.A.6 verbatim TextBlock (prop_1.s3.txt) → 2 AssetEntries, ids prop_1.s3.txt.off / prop_1.s3.txt.on, kinds correct. Matches the §4.6 example asset prop_1.s3.txt.off.
    A \cg{ghost}{…} where ghost ∉ groups_used → raises (validation).
    A groups_used entry not in palette → raises.
    The off-bake preamble overrides \cg to grey_text; the on-bake uses ink — assert the two generated .tex sources differ in exactly the \cg definition (text-level assert on the wrapped source).

C7 — tools/overlay_diff.py

Frozen entry: def run(back_png: Path, front_png: Path) -> None (Tkinter GUI; never ships; build-tool only).

Pure helpers (frozen, NumPy-array in/out — these are the tested units):

def binarize(img: np.ndarray, threshold: int) -> np.ndarray        # dark<threshold → ink (True)
def transform(img: np.ndarray, tx: float, ty: float, scale: float, rot_deg: float) -> np.ndarray   # Pillow affine
def dilate(mask: np.ndarray, px: int) -> np.ndarray                # MaxFilter / morphology
def compose(back_ink: np.ndarray, front_ink: np.ndarray) -> np.ndarray
    # mid-grey field; paint back-ink WHITE; paint front-ink BLACK over it.
    # white-remaining = back has ink the front lacks = MISMATCH.

GUI behavior (NT §2.3): load back (scan) + front (render); per-layer pan/scale/rotate sliders + mouse drag; global thicken slider (0–12 px, dilates the front mask before compose); binarize threshold slider; Flip button (swap front/back to catch both-direction mismatches); save-composite button. Per redraw: binarize each → affine each → dilate front → compose → show. Tkinter wiring is the only display-needing part; skipped in CI.

The reliability principle (NT §2.3, restated for the child): the EMITTER only needs relative construction correct; the overlay tool absorbs all global placement (the per-layer transforms align a warped/rotated/rescaled scan to the clean render). Nir describes mismatches with the figure's own letters ("the arc above A doesn't reach B") — zero math, zero coordinates.

Contract: the four helpers are pure (NumPy in/out, deterministic). run is the only display-dependent function.

Tests (headless, on the pure helpers — NT §2.3 verbatim test spec):

    A synthetic back with a line the front lacks → compose has white pixels exactly along that line.
    With thicken ≥ the gap (dilate the front to cover near-misses) → those white pixels vanish.
    binarize: a known grey ramp at threshold t → exact ink mask.
    transform: a 90° rotation of an asymmetric mask → expected orientation.
    run is not tested in CI (no display); the brief notes "skip gracefully without a context."

§D — LEG-2 BUILD ORDER + TEST PLAN

1. bake/palette_gen.py     ← needs only the Palette model. Build FIRST (everything color flows from it).
2. bake/recipe_validate.py ← needs Recipe + Palette models. (parallel-ok with 3,4,7)
3. bake/prooffig_check.py  ← needs Palette + n_steps. (text-level lint)
4. bake/asy_compile.py     ← needs only AsyResult/AsyConfig. The subprocess isolate.
5. bake/_imageops.py       ← (shared pure helpers: key_out, trim, bbox) — build before the bakers.
6. bake/baker_figure.py    ← needs asy_compile (injected) + _imageops + AssetEntry.
7. bake/baker_text.py      ← needs Tectonic (injected) + _imageops + AssetEntry.
8. tools/overlay_diff.py   ← standalone; needs only its 4 pure helpers + Tkinter.

Why: color source first (1); the two static validators (2,3) and the subprocess isolate (4) are independent; the shared image helpers (5) precede both bakers (6,7); the overlay tool (8) is fully standalone. raw_models.py (Leg 1) is extended with the Leg-2 models (Recipe + ops, TextBlock, Palette/GroupColor, AssetEntry/Manifest, plus aliases FigureId, GroupName, OpName, Ref, Vec3, TextBlockId, PairId) — DeepSeek adds these to the same shared contracts file; same extra="forbid"/schema_version discipline.

Per-module unit (the frozen fixtures above): all exact-golden except overlay_diff.run (no-display, skipped) and any flag explicitly best-effort (the prooffig_check text parse — backed by the compile gate).

Integration (the Leg-2 golden mini-figure, no AI, no network, no real asy/Tectonic):

    Take the §3.A.4 verbatim recipe (prop_1.f1) + §3.A.7 palette → recipe_validate returns [].
    palette_gen.gen → palette.asy + palette.tex (byte-stable).
    Feed the §3.A.5 verbatim figure.prop_1.f1.asy + n_steps=3 → prooffig_check.lint returns [].
    baker_figure.bake with a fake compile_fn (canned magenta-bordered PNGs) → 4 AssetEntries (off + on_1..3), off deduped, ids matching §4.6.
    baker_text.bake with the §3.A.6 TextBlock + fake Tectonic → 2 AssetEntries (…txt.off/…txt.on).
    Assemble a Manifest from the AssetEntries → validates against §4.6; every asset_id is referenceable by a PanelPairRT (boundary check: build a dummy PanelPairRT pointing at prop_1.f1.off/.on.3/prop_1.s3.txt.off/.on and assert all four resolve in the manifest).

Acceptance gate (maps to OT M5 "Baker + one real figure"): Leg 2 is DONE when all unit goldens pass, the integration fixture is green, and the assembled Manifest validates with asset_ids that a PanelPairRT can consume. (The first REAL asy/Tectonic compile of a genuine Principia figure is the M5 human-in-the-loop milestone — out of scope for the frozen contracts, which are proven with injected compilers in CI.)
§E — Open items I'm flagging (NOT blockers — DeepSeek confirms at integration)

    ⚠️ The figure asset-id key: figure_id vs drawing-block_id (the one real tension). §4.6's grammar says figure assets key on figure_id: figure_off → <figure_id>.off → prop_1.f1.off, figure_on → <figure_id>.on.<k> → prop_1.f1.on.3. But Block C's closing note says "the manifest asset-id grammar uses these block_ids as prefixes: prop_1.s3.fig.on.3." These disagree: prop_1.f1.on.3 (figure_id-keyed) vs prop_1.s3.fig.on.3 (block_id-keyed). I froze baker_figure to the §4.6 grammar (<figure_id>.off / <figure_id>.on.<k>) because §4.6 is the actual Manifest schema with a worked example (prop_1.f1.on.3), and the iron rule says trust the frozen format. But PanelPairRT.drawing_on_asset must then reference prop_1.f1.on.3, not prop_1.s3.fig.on.3. This requires room_maker to map a step s<k> → its figure's figure_id + step k. DeepSeek: confirm which key room_maker/PanelPairRT actually emits. If the room side is already built to block_id-prefixed ids, tell me and I'll re-freeze the baker grammar to match — this is a contract reconciliation I must not guess. (It does not block building the bakers; it's a one-line asset_id format that the integration boundary-test pins either way.)

    Vec3 and the Leg-2 aliases' home. Block C uses Vec3; §3.A.4 uses Vec2/GroupName/OpName/Ref/FigureId. If the Second Canon §2 already declares these globally, the extended contracts file imports them. DeepSeek: confirm; don't redefine.

    The series count comes from the READER ("the count the book draws"). recipe_validate does NOT police whether count matches the engraving — that's the overlay tool's (Nir's eyes) job per §2.6. recipe_validate only checks 1 ≤ count ≤ 64 (the model bound). Flagging so no one adds a "wrong count" check that would require understanding the figure.

Mission 2 / Leg 2 is frozen. Seven child briefs with exact signatures bound to the verbatim §3.A.4–§3.A.7 + §4.6 contracts, the asset-id boundary to PanelPairRT checked (with the one real id-grammar tension flagged for DeepSeek's confirmation, not silently decided), golden fixtures drawn from the verbatim examples, injected compilers for headless CI, a dependency-sorted build order, and an acceptance gate mapped to M5.

Both legs are now in DeepSeek's hands. Per your handoff, once the build has started THEN I can propose holistically — so I'll hold here and await DeepSeek's Leg-2 build report (or your word on the §E #1 id-grammar confirmation, which is the single thing I'd want settled before baker_figure and room_maker meet). 🗝️

--- END VERBATIM ---
