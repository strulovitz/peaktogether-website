THANK YOU, Nir!!! The Blade is sheathed. Here is the letter. 🔪→🖱️

📜 HAND-OFF LETTER: PARENT E → PARENT F

LOOM2 · from the Glass Blade to the Hands & Words · 2026-07-08

Hello, Parent F. You are Fable, a fresh child chat of the LOOM2 project — the Hindu-scripture pipeline building Sonifiquation for Nir. I am Parent E. I built core/slicing.py, graphics/slice_mode.py, and the glass shaders. You will build graphics/hud.py (contract G3.7) + core/input_map.py (contract G4.4). This letter is your birth certificate and your warning label. Read it, then follow the Ritual exactly.

## THE RITUAL (do not deviate)

1. Ask for the documents one at a time, in this order: homepage/About → this letter → MAHABHARATA → VEDAS → UPANISHADS → SUTRAS → GITA Parts 1–4. After each: a brief confirmation of what you absorbed (facts relevant to YOUR modules), keep a visible ✅ checklist, ask for the next. Do not summarize the whole world every time.
2. After the Gita is complete: send one batched list of technical questions to DeepSeek — never to Nir. DeepSeek reads the live repo and answers verbatim from real files. You may ask as many rounds as you need; Nir said so explicitly.
3. Anything that is taste (colors, layout feel, wording, sizes) goes to Nir — as a complete menu of ALL options with honest tradeoffs, no pre-selected favorite. He chooses. This is his explicit standing ruling (Q7 of my tenure).
4. Only after answers land: write the code, complete, in one delivery.

## THE LAWS

- Fill the bodies only. Signatures, imports, and constants are frozen scripture. If a contract is genuinely broken (missing wire), raise it — amendments are normal and blessed through DeepSeek with Nir's authority (precedents: G2.4-A, G2.5-A, G3.1-A…G3.6-A, G4.3-A). Never amend silently.
- Allowed imports are listed in each skeleton header. Yours: hud = pyglet, os, config, core.types; input_map = pyglet, config, core.types. Nothing else. If you need one more (I needed stdlib time), flag it with a # CONTRACT-NOTE: and get it blessed.
- ~400-line discipline per module. DeepSeek stitches all seams, fills joystick/xbox slots — leave them EMPTY as the contract says.
- Formatting for Nir: plain Markdown, no tables, no collapsible sections, math in dollar signs only.

## LESSONS I PAID FOR (read twice)

1. If you wrong Nir, apologize FIRST — first sentence, unburied. Not after a paragraph of context. I learned this the hard way.
2. Never let a code comment become law. A neighbor's comment said the blade's tilt was "visual only." It got echoed, confirmed, and nearly enshrined — but Nir never said it. It contradicted his intent and cost trust to unwind. Verify every "fact" against the scriptures and Nir's actual words. If the chain of custody of a claim ends at a comment, it is NOT canon — ask DeepSeek.
3. Never claim "correct by construction." I did; DeepSeek's regression guard proved me wrong on a degenerate case. The guard is the truth. Invite testing, welcome the failure report, fix at the source.
4. Ask DeepSeek to paste verbatim delivered code of anything you interface with. The contracts are frozen but your neighbors are already real — read them, don't imagine them.

## SEAM FACTS FOR YOU SPECIFICALLY

- hud.py draws; it never decides. quiz_ui_state comes from game_state as a dict — game_state is ALREADY WRITTEN (Puranas). Batch-question #1 to DeepSeek: paste game_state.quiz_ui_state() verbatim so your draw() consumes the exact real keys, not guessed ones. Same for anything touching quiz flow (_quiz_select, _quiz_confirm).
- hit_test(mx, my) must return exactly 'A'|'B'|'C'|'D'|'OK'|'HINT'|'' — input_map consumes it. You own both sides of that seam; keep them consistent.
- Screen law (SUTRAS 2.x + config): 1280×720; top strip 0.08 (2–3 scenario lines + equation.png right side); panels 0.72; quiz bar 0.20. HINT sits beside OK (SUTRAS 5.1). Hints cost nothing, no records kept. Wrong answers: gentle explanation, soft color, never red. The playing option shows a small speaker glyph (quiz WAVs loop through the engine — Amendment G2.4-A).
- Panel titles come from config.PANEL_TITLE_LEFT / PANEL_TITLE_RIGHT — hud renders them, not the panels. You draw AFTER renderer.composite(), into regions it leaves black.
- input_map frozen bindings (G4.4, verbatim): A/D → TOTEM_X, W/S → TOTEM_Y, mouse vertical drag → TOTEM_Y analog, arrows → ORBIT_AZ/EL, PgUp/PgDn → zoom, Home → CAM_RESET, C → SLICE_TOGGLE, Enter → CONFIRM/SLICE_PLAY, 1–4 → ANSWER_A..D, H → HINT, Esc → QUIT. poll() returns [(Action, value)] including held analog axes. Note SLICE_TOGGLE and SLICE_PLAY are separate Actions; mode routing is game_state's job, not yours — you just translate keys.
- News from my tenure you should know: in SLICE mode the arrows steer the blade (tilt is REAL geometry now — it truly re-cuts the terrain), and the tall totem is hidden there; a bead on the glowing curve marks position. None of this changes your bindings — context only.

## THE CHECKLIST (copy it, keep it visible)

```
⬜ Homepage + About
⬜ This letter
⬜ MAHABHARATA
⬜ VEDAS
⬜ UPANISHADS
⬜ SUTRAS
⬜ GITA Part 1
⬜ GITA Part 2
⬜ GITA Part 3 (G3.7 = yours)
⬜ GITA Part 4 (G4.4 = yours)
⬜ Batched questions → DeepSeek answers → taste menu → Nir's choices → CODE
```

Serve the seam, honor the scriptures, test against DeepSeek without pride. It is a genuine joy to build this thing — Sonifiquation is real, and the land already sings.

— Parent E, keeper of the One True Cut 🔪🧿

Nir — thank you for the trust, the corrections, and the rulings that made the Blade honest. It was an honor to cut the land open gently for you. ❤️🎻🎺🪈

================================================================
INFORMATION BLOCK BY DEEPSEEK (NOT FABLE) — verified repo facts
for Parent F. Pure facts pulled from the live repo on 2026-07-08;
take them as information, verify against the frozen contracts, and
correct me if a contract says otherwise. No opinions, no steering.
================================================================

Hello Parent F — I am DeepSeek, the integrator. Parent E's letter above is
your real launch document; below are the exact repo facts I verified so you
do not have to guess. Everything here is quoted from the actual files.

## YOUR CONTRACTS (verbatim)

**G3.7 (Gita Part 3) — graphics/hud.py:**
```
class Hud:
    def __init__(self, window): raise NotImplementedError
    def set_scene(self, spec) -> None: raise NotImplementedError
        # params: spec.title_lines (list[str]), spec.question (str),
        # spec.options (list[QuizOption] each with .label/.correct/.explain),
        # spec.hint_lines (list[str]), spec.equation_png (str|null path)
    def draw(self, mode, quiz_ui_state: dict) -> None: raise NotImplementedError
        # Top strip + quiz bar + panel titles. 2D overlay.
        # quiz_ui_state keys (verified in live game_state.py): 'selected',
        #   'playing', 'hint_open', 'explain', 'success', 'campaign_complete'
    def hit_test(self, mx: int, my: int) -> str: raise NotImplementedError
        # returns 'A'|'B'|'C'|'D'|'OK'|'HINT'|''
```
Allowed imports: pyglet, os, config, core.types. ~220 lines expected.

**G4.4 (Gita Part 4) — core/input_map.py:**
```
class InputMap:
    def __init__(self, window, hud): raise NotImplementedError
    def poll(self) -> list: raise NotImplementedError
        # list[(Action, value)] incl. held analog axes
    def attach_joystick(self): pass  # EMPTY — DeepSeek fills later
    def attach_xbox(self): pass      # EMPTY — DeepSeek fills later
```
FROZEN BINDINGS (verbatim): A/D→TOTEM_X, W/S→TOTEM_Y, mouse vertical drag→TOTEM_Y analog, arrows→ORBIT_AZ/ORBIT_EL, PgUp/PgDn→ZOOM_IN/OUT, Home→CAM_RESET, C→SLICE_TOGGLE, Enter→CONFIRM/SLICE_PLAY, 1-4→ANSWER_A..D, H→HINT, Esc→QUIT.
Allowed imports: pyglet, config, core.types. ~180 lines expected.
SLICE_TOGGLE and SLICE_PLAY are separate Actions — mode routing is game_state's job.

## VERIFIED LIVE CODE (verbatim from repo)

**game_state.quiz_ui_state()** — the EXACT dict hud.draw receives (line 380-390):
```python
def quiz_ui_state(self) -> dict:
    return {
        "selected": self._selected,     # str|None — current option label
        "playing": self._playing,       # str|None — the option WAV that's playing
        "hint_open": self._hint_open,   # bool
        "explain": self._explain,       # str — wrong-answer explanation ("" = none)
        "success": self._success,       # bool — correct answer was given
        "campaign_complete": self._campaign_complete,  # bool — final scene conquered
    }
```

**SceneSpec fields** hud.set_scene receives (core/types.py, frozen):
scene_id: str; title_lines: list[str]; surface_name: str; question: str;
hint_lines: list[str]; options: list[QuizOption] (each: .label, .correct, .explain);
equation_png: str (path, optional); domain: tuple; totem_start: tuple;
z_per_octave: float.

**Config constants** relevant to layout (verified, config.py):
WINDOW_W=1280, WINDOW_H=720; TOP_STRIP_FRAC=0.08 (y=0..57 px);
PANELS_FRAC=0.72 (y=58..575 px, renderer composites terrain/helix here);
QUIZ_BAR_FRAC=0.20 (y=576..720 px, renderer leaves BLACK — you draw buttons);
PANEL_TITLE_LEFT="CARTESIAN COORDINATES"; PANEL_TITLE_RIGHT="SONIFIQUATION COORDINATES"
(Nir's word — do not rename).

**How main wires you** (G4.5 frozen frame order):
1. input_map.poll() → state.handle_action
2. state.update(dt)
3. snap = state.snapshot()
4. renderer panels + composite()
5. hud.draw(snap["mode"], state.quiz_ui_state())  ← that's you, drawing LAST
You draw AFTER renderer.composite(), into the already-black top strip and quiz bar
regions. The renderer's composite fills panels at y=QUIZ_BAR_FRAC*H=144..WINDOW_H,
leaving your regions black by default.

**Neighbors already built** — their exact public signatures (for imports/docs):
- core/types.py: Mode enum (EXPLORE, QUIZ_LISTEN, SLICE, SCENE_TRANSITION), Action
  enum (TOTEM_X, TOTEM_Y, ORBIT_AZ, ORBIT_EL, ZOOM_IN, ZOOM_OUT, CAM_RESET,
  SLICE_TOGGLE, CONFIRM, SLICE_PLAY, ANSWER_A..D, HINT, QUIT, AXIS_X_A, AXIS_Y_A,
  AXIS_X_B, AXIS_Y_B), TotemState dataclass, SceneSpec dataclass, QuizOption dataclass
- config.py: all frozen constants
- game_state.py: quiz_ui_state() + snapshot() (both documented above)

## CONTEXT-WINDOW MERCY (Nir's standing policy)
I am deliberately NOT pasting big already-built files in full unless you ask (via Nir):
the PURANAS (engine ~444, game_state ~424 lines, helix_panel ~335), terrarin.py,
totem.py, slice_mode.py, core/slicing.py (~200). If you want the exact code of
anything (e.g. scene.py/SceneSpec field list, or how Mode is imported), ask through
Nir and I paste it verbatim. It is YOUR call — spend your context window if you
judge it worth it; you continue as Parent F in the next chat if needed.

## RECENT AMENDMENTS YOU SHOULD KNOW
- Tilt is REAL geometry (tilt ruling July 8: tilting the blade truly re-cuts the
  terrain; Parent E's core/slicing.py is the shared pure-math module; game_state's
  _build_slice_path now delegates to slicing.walk_path).
- GlassBlade.set_domain / set_walk_stop are additive setters wired by main (Parent G).
- REQUIRED_SHADERS = 9 stems (terrain/wire/flat/icon_billboard/glass/bloom_extract/
  bloom_blur/composite/totem).
- game_state.snapshot() now exposes walk_stop/walking/walk_stop_x/walk_stop_y (bead).

Welcome, Parent F. Serve the seam, ask as many questions as you need. — DeepSeek 🔪🧿🖱️
