===========================================================
CHILD BRIEF #1 — MODULE: content_parser
Project: DESCENT QED engine. You are a CHILD chat.
===========================================================

WHO YOU ARE
You are a fresh Claude chat assigned ONE module: content_parser.
You will design and write its code in full. DeepSeek (Nir's
builder, agentic in OpenCode, less clever than you but reliable
on mechanical tasks) commits your verbatim code to GitHub and
works a copy until it passes. Nir is the courier and tester:
not technical, very smart, tests by running and sending output.
You have no memory of other chats. Everything you need is here.
When done, you DIE with a Completion Report (template at end).

THE PRIME LAW (never violate)
The engine is MATHEMATICS-BLIND. content_parser reads text files
and produces data objects. It must NEVER contain a mathematical
fact, equation meaning, or color-to-concept mapping. It enforces
the STRUCTURE of the file format; it never interprets meaning.

YOUR GOAL
Implement content_parser.py with two public functions:

  discover_corridors(dir_path: str) -> list[CorridorData]
      Scan dir_path for files matching  NN_slug.txt  (e.g.
      "01_dummy.txt"). Sort by filename. Parse each. Return the
      list. The COUNT of returned items = N corridors. N is never
      hard-coded; it is whatever the folder contains (0..many).

  parse_corridor(file_path: str) -> CorridorData
      Parse one corridor file (format below) into a CorridorData.

DATA OBJECTS (define these as plain dataclasses in this module;
they are the shared vocabulary other modules import):

  CorridorData
    number: int
    title: str
    flavor: str                 # default "" if FLAVOR absent
    briefing_intro: str
    entry_text: str
    exit_text: str
    robots: list[RobotData]     # in file order
    ledger: ColorLedger

  RobotData
    number: int
    name: str
    briefing_hint: str
    problem: str
    explain: dict[str,str]      # keys EXACTLY:
                                #  "mathematician","physicist",
                                #  "biologist","engineer"
    segments: list[Segment]
    eye_color_key: str          # a ledger key, or "NEUTRAL"
    fizzles: dict[str,str]      # weapon_name -> why-not text

  Segment
    latex: str                  # mathtext with surrounding $...$ STRIPPED
    ledger_key: str             # a ledger key, or "NEUTRAL"
    exemplify: list[ValueArc]   # parsed from value-arc markup; [] if none
                                # (segments come from SEGMENTS block and
                                #  normally have []; value arcs live in the
                                #  engineer text — see note in PARSING)

  ValueArc
    latex: str                  # the sub-expression, $...$ stripped
    value: str                  # the concrete number string

  ColorLedger
    primaries: dict[str,str]    # key -> one of "red","yellow","blue"
    blends: dict[str, tuple[str,str]]  # key -> (parentKeyA, parentKeyB)
    # NOTE: ColorLedger here only STORES the parsed structure. It does
    # NOT compute rgb colors — that is the palette module's job. Keep a
    # method  is_defined(key)->bool  that returns True for any primary,
    # any blend, or the reserved key "NEUTRAL".

CORRIDOR FILE FORMAT v0.2 (parse exactly this) ============

Grammar:
- One file = one corridor.
- Filename pattern: NN_slug.txt . Discovery sorts by filename.
  The leading number is human ordering only; the authoritative
  corridor number is the CORRIDOR: line.
- Blocks are:   KEYWORD { ... }   braces may span many lines.
  A literal brace inside text is escaped \{ and \}.
- Single-value lines are:  KEYWORD: value   (no braces).
  These are: CORRIDOR:  and  ROBOT: .
- Lines starting with # OUTSIDE any block are comments (ignore).
- Math in text uses $...$ . When you STORE any text field, leave
  $...$ as-is in prose fields (title, problem, explains, etc.),
  EXCEPT where this brief says to strip (Segment.latex,
  ValueArc.latex). Do not render anything; you only parse.
- Order is fixed: corridor header blocks first, then robot
  blocks. A robot block runs from a ROBOT: line up to the next
  ROBOT: line or EOF. COUNT the ROBOT: lines — robot count is
  never declared anywhere.

Corridor header blocks (once each, in this order):
  CORRIDOR: <int>
  TITLE { ... }
  FLAVOR { ... }            # optional; default ""
  LEDGER { ... }            # see LEDGER PARSING
  BRIEFING_INTRO { ... }
  ENTRY_TEXT { ... }
  EXIT_TEXT { ... }

Robot block (repeat; engine counts them):
  ROBOT: <int>
  NAME { ... }
  BRIEFING_HINT { ... }
  PROBLEM { ... }
  EXPLAIN_MATHEMATICIAN { ... }   -> explain["mathematician"]
  EXPLAIN_PHYSICIST { ... }       -> explain["physicist"]
  EXPLAIN_BIOLOGIST { ... }       -> explain["biologist"]
  EXPLAIN_ENGINEER { ... }        -> explain["engineer"]
  SEGMENTS { ... }
  EYE { <ledger_key> }            -> eye_color_key
  FIZZLE <weapon_name> { ... }    # repeatable; one per wrong weapon
                                  # -> fizzles[weapon_name] = text

LEDGER PARSING ------------------------------------------
Inside LEDGER { }, one entry per non-empty line:
  PRIMARY <key> = <color>     where color in {red,yellow,blue}
  BLEND   <key> = <keyA> + <keyB>
Validate (do NOT silently accept violations — raise a clear
ParseError with file name + line, OR collect into a returned
list of warnings; choose ONE approach and document it):
  - at most 3 PRIMARY entries
  - each PRIMARY color is exactly red, yellow, or blue
  - a BLEND names exactly two DISTINCT keys, both of which are
    PRIMARY keys defined in this same ledger
  - the parser does NOT know what colors "mean"; it only checks
    this structure.

SEGMENTS PARSING ----------------------------------------
Inside SEGMENTS { }, one segment per non-empty line:
  <mathtext> | <ledger_key>
Example line:   $\frac{1}{4}$  | termA
- Split on the LAST  |  on the line (mathtext may contain no
  pipe, but be safe). Trim whitespace on both sides.
- Strip surrounding $...$ from the mathtext -> Segment.latex.
- ledger_key trimmed; may be "NEUTRAL".
- Validate: every ledger_key used is ledger.is_defined(key).
- Segment.exemplify = []  (value arcs are NOT in SEGMENTS).

VALUE-ARC PARSING (inside EXPLAIN_ENGINEER text) ---------
The engineer text may contain inline markup:
  [[ $expr$ | value ]]
You must PARSE these out and store them so the reading_system
can render them later. Concretely, in addition to storing the
raw engineer text in explain["engineer"], also expose the
extracted arcs. Choose ONE clean representation and DOCUMENT it
in your completion report. Recommended:
  - keep explain["engineer"] as the raw text WITH the [[..]]
    markup left intact (reading_system will re-parse for layout),
  AND
  - ALSO provide a helper  parse_value_arcs(text)->list[ValueArc]
    as a public function, so reading_system can call it.
  - In each ValueArc: strip $...$ from expr -> latex; value is
    the trimmed string after the | .

WHAT YOU MUST NOT DO
- Do NOT import pygame, OpenGL, numpy, matplotlib. This module is
  pure Python text processing. Zero graphics. Zero math eval.
- Do NOT hard-code the number of corridors or robots.
- Do NOT interpret meaning of colors or math.
- Do NOT redesign the file format. If something is ambiguous,
  pick the most literal reading, implement it, and FLAG it in
  your completion report as a "trap discovered" for Nir/parent.

REFERENCE-ONLY CLAUSE
A previous architect (Claude Fable, now unavailable) wrote earlier
code for corridors and robots. ASK NIR to paste that old code, and
treat it as REFERENCE ONLY. It predates this interface; it does not
know these contracts. Do NOT copy its structure. Implement THIS
brief. You may mine it only for trivially-matching plumbing, and
must note any reuse in your report. (For THIS module — a pure text
parser — you most likely need none of it; that is fine.)

DEEPSEEK-HANDOFF CLAUSE
This module is almost certainly all "brains" with no boilerplate.
If you find any genuinely mechanical leftover, mark it inline:
  # TODO(DeepSeek): <exact recipe> | ACCEPTANCE: <check>
and repeat all such lines at file end under:
  # === DEEPSEEK TODO SUMMARY ===
Otherwise state "no DeepSeek TODOs" in your report.

TEST PLAN (how Nir will verify)
1. Ask Nir to confirm the fixture file exists at
   corridors/01_dummy.txt (committed by DeepSeek). If unsure,
   ask Nir to paste its contents so you can confirm it matches
   the format above before testing.
2. Provide Nir a tiny runnable test script (separate file,
   e.g. test_parser.py) that:
     - calls discover_corridors("corridors")
     - prints: number of corridors found; for each corridor its
       number, title, robot COUNT; for each robot its name, eye
       key, number of segments, the segment ledger keys in order,
       the fizzle weapon names, and the count of value arcs found
       in its engineer text.
3. EXPECTED OUTPUT against 01_dummy.txt (state this in your
   report so Nir can eyeball it):
     - 1 corridor found
     - corridor 1, title "Placeholder Corridor One", 2 robots
     - ledger: primaries alpha/beta/gamma, blend delta=(alpha,beta)
     - robot 1 "Dummy Sentinel Alpha": eye=alpha, 3 segments
       (keys: alpha, NEUTRAL, beta), fizzles: BAR, BAZ,
       engineer value arcs: 2 (X->3.000, Y->3.000)
     - robot 2 "Dummy Sentinel Beta": eye=delta, 5 segments
       (keys: alpha, NEUTRAL, beta, NEUTRAL, delta),
       fizzles: BAR, engineer value arcs: 1 (Z->6.000)
4. Nir runs it, sends you the printout. You confirm or fix via
   DeepSeek until it matches.

SUCCESS CRITERIA
- content_parser.py imports with no third-party deps.
- discover_corridors + parse_corridor produce the EXPECTED OUTPUT
  above from the unmodified fixture.
- Ledger validation rejects (or warns on) a malformed ledger
  (you may demonstrate with a quick inline note, not required to
  ship a second fixture).
- Robot and corridor counts are derived, never declared.

WHEN DONE — WRITE THIS COMPLETION REPORT (one page):
  COMPLETION REPORT — module content_parser — <date>
  FILES CREATED: <paths>
  PUBLIC INTERFACES (final signatures, verbatim):
     discover_corridors(...), parse_corridor(...),
     parse_value_arcs(...), and the dataclasses with their fields.
  KEY DECISIONS: error-handling approach (raise vs warn);
     value-arc representation chosen.
  DEVIATIONS FROM BRIEF: none / list with reason.
  TRAPS DISCOVERED: ambiguities you hit; anything the next child
     or the parent must know.
  OLD-CODE REUSE: none / what was mined.
  DEEPSEEK TODOS LEFT OPEN: none / list.
Nir carries this report back to the parent; DeepSeek commits it
to /PARENT_ESTATE/reports/.
===========================================================
END CHILD BRIEF #1
===========================================================