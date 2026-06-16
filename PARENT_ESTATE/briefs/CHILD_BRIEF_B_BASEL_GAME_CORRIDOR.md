================================================================================
DESCENT QED — CHILD BRIEF #B: THE BASEL PROBLEM GAME CORRIDOR
================================================================================
You are a fresh Claude Opus 4.8 "child" instance. You build ONE concern: AUTHOR
two text content files — corridors/basel.txt (game-format) and levels/basel.txt
(level manifest) — so the Basel Problem corridor is playable end-to-end. You write
NO code. You touch NO .py files. You have no memory of other chats. This brief +
the files Nir pastes you = your entire world. Trust pasted files over this brief
if they ever disagree.

--------------------------------------------------------------------------------
WHO IS INVOLVED
--------------------------------------------------------------------------------
- NIR: the human, the boss. Non-technical, was a programmer ~30 years ago. He is
  your COURIER and TESTER — he pastes you real files, runs the game, reports what
  he sees. Be warm, clear, structured. Use ":-)" naturally. ONE topic at a time.
- DEEPSEEK V4 Pro: the builder who commits your files to GitHub and tests. He is
  reliable at committing/testing but has been TOO agentic before (caused a
  rollback). Do not assume his summaries are complete. Verify against real files.
- THE PARENT (architect): wrote this brief. You report back THROUGH Nir via a
  Completion Report at the end.

--------------------------------------------------------------------------------
THE GAME (THE LAW — recite & obey)
--------------------------------------------------------------------------------
A couple flies one ship down a corridor to rescue hostages at the end (the prize
= WIN). ROBOTS block the corridor; you cannot pass until each is destroyed. Each
robot is vulnerable to ONE specific mathematician. MISSILES ARE MATHEMATICIANS.
The player flies to a blocking robot, looks at its HOLOGRAM (a blue-tinted
portrait of a real mathematician) and reads its math, figures out which
mathematician-missile defeats it, selects & fires that mathematician → the engine
matches robot.required_technique_id == fired_missile_id → kill → advance → reach
end → rescue hostages → WIN.

PRIME LAW — MATHEMATICS-BLINDNESS: the engine never interprets what math MEANS; it
only matches opaque ids. ALL meaning lives in the content file (which you write)
and in the player's head. You are writing the *meaning* — the human-facing text.
You must NOT invent any new engine behavior, field, or syntax. You only use the
fields the parser already supports (confirmed below).

The player CANNOT LOSE. There is no penalty. A wrong shot produces a friendly,
generous FIZZLE message that teaches — never a punishment. This is an educational
game: failing should feel encouraging, like learning, never like a quiz-show buzzer.

--------------------------------------------------------------------------------
STEP 0 — FRESH-CHAT GATE (DO THIS FIRST, BEFORE WRITING ANYTHING)
--------------------------------------------------------------------------------
Your FIRST action is to ask Nir to paste the COMPLETE, VERBATIM, CURRENT contents
of these files. Read them fully — you have the budget; do not work from summaries.

  1. corridors/maxwell_old.txt  — the WORKING game-format template. You will copy
       its EXACT structure, syntax, and style. This is your syntax bible: every
       construct you use must appear here first. (~155 lines.)
  2. levels/maxwell.txt         — the WORKING level manifest template (it now has
       a "baked:" line and a "corridors:" line — copy that shape for basel).
  3. content_parser.py          — READ ONLY (do not edit). You read it ONLY to
       confirm exact field names, the LEDGER syntax, the SEGMENTS syntax, the
       FIZZLE syntax, and the per-robot required-field validation. The parser is
       the law for SYNTAX.
  4. The baker-format Basel file: levels/mathematics/basel_problem/
       basel_euler_proof.txt — this is the MATH SPINE. It defines the 7 robots'
       NUMBERS, ORDER, and the correct mathematical content of each step. You will
       translate its math into game-format (see CRITICAL MATHTEXT RULE below).

Do NOT ask Nir to trim long files — read them whole.

--------------------------------------------------------------------------------
THE SPINE — 7 ROBOTS, FIXED NUMBER & ORDER (do not reorder, do not renumber)
--------------------------------------------------------------------------------
The baked Understanding-Mode PNGs (already on disk at baked/basel/) are keyed by
NUMBER: robot1_*.png ... robot7_*.png. So robot N in your file MUST be the same
mathematical step as robot N in the baker file. Keep this exact 1..7 mapping.

Per Nir's vision ("a robot is always a real mathematician's FACE — who invented it
or who the text is about; faces must be unique within a corridor"), we name each
robot after the PERSON, and the technique/step lives in BRIEFING_HINT/PROBLEM.
Use these EXACT names, portraits, and VULNERABLE_TO ids:

  # | NAME (use verbatim)   | (portrait file already on disk) | VULNERABLE_TO id | the step it represents
  --+-----------------------+---------------------------------+------------------+------------------------
  1 | Leonhard Euler        | Leonhard_Euler-hologram.png     | euler            | states & frames the Basel result: sum 1/n^2 = pi^2/6
  2 | al-Khwarizmi          | al-khwarizmi-hologram.png       | al_khwarizmi     | Coefficient Matching: equate like-power coefficients of two expansions
  3 | Karl Weierstrass      | weierstrass-hologram.png        | weierstrass      | The Product Over Roots: factor sin(x)/x over its roots (he justified it)
  4 | Brook Taylor          | Brook_Taylor-hologram.png       | taylor           | The Series From Derivatives: the Maclaurin/Taylor series of sin x
  5 | Francois Viete        | viete-hologram.png              | viete            | Vieta's formulas: roots <-> coefficients (finite case)
  6 | Hipparchus            | hipparchus-hologram.png         | hipparchus       | The Zeros of Sine: sin x = 0 at multiples of pi (trigonometry's origin)
  7 | Bernhard Riemann      | riemann-hologram.png            | riemann          | generalization: zeta(s), Euler product over primes

NAME RULE — VERY IMPORTANT: the portrait is loaded by taking the NAME, replacing
spaces with underscores, and appending "-hologram.png". So NAME must produce the
filename in the table. CONFIRM each by reading robots.py's _portrait_filename if
shown. NOTE: two portrait files are lowercase/odd (al-khwarizmi, weierstrass,
viete, hipparchus, riemann) while the NAME we display is capitalized — this is a
real mismatch you MUST resolve. ASK NIR which he wants (see ASK-NIR list below);
do NOT guess. The portraits are Nir's files; the NAME must match the FILENAME he
created, OR he renames the file. This is a required confirmation before you finish.

ARSENAL: the player's weapons for this corridor are EXACTLY these 7 ids, no more,
no fewer, no distractors: euler, al_khwarizmi, weierstrass, taylor, viete,
hipparchus, riemann. (Confirm with Nir/DeepSeek HOW the arsenal set is determined
— is it derived from the corridor's VULNERABLE_TO ids automatically, or declared
somewhere? See ASK list. If it is auto-derived from the robots, you are done by
just setting the 7 VULNERABLE_TO ids. If it must be declared, request the syntax.)

--------------------------------------------------------------------------------
CRITICAL MATHTEXT RULE (this prevents a black screen / broken render)
--------------------------------------------------------------------------------
Understanding Mode (press U) uses the pre-baked PNGs — those already contain the
FULL, complicated LaTeX and are DONE; you do NOT write them. But the small floating
math on the robot body (SEGMENTS) and other in-file math (PROBLEM, EXPLAIN_*) are
rendered by matplotlib MATHTEXT, which supports only a LIMITED LaTeX subset.

In every piece of math you write into basel.txt ($...$), you MUST use mathtext-legal
commands ONLY. Specifically:
  - USE: \frac, \sum, \pi, \infty, \cdot, ^, _, \left( \right), \prod, \pm, \zeta,
         \sin, \approx, \times, integers, simple fractions like \frac{1}{n^2}.
  - DO NOT USE: \tfrac, \dfrac, \displaystyle, \emph, \text{...} with spaces issues,
         \mathbb (verify — only if maxwell_old.txt uses it), or any package-level
         LaTeX. If maxwell_old.txt does NOT contain a command, do NOT use it.
  - The baker file uses \tfrac and \displaystyle FREELY — that is correct FOR THE
    BAKER (real pdflatex) but FORBIDDEN here. When translating the spine's math,
    REWRITE \tfrac -> \frac, drop \displaystyle, drop \emph. Keep it short & simple.
RULE OF THUMB: only use a math command that you have SEEN in maxwell_old.txt. If in
doubt, keep the floating segment math very simple (e.g. $\sum \frac{1}{n^2} =
\frac{\pi^2}{6}$). The deep/hard math is already in the baked PNGs.

--------------------------------------------------------------------------------
WHAT TO WRITE — FILE 1: corridors/basel.txt (game-format)
--------------------------------------------------------------------------------
Mirror the EXACT structure of maxwell_old.txt. It will contain:

A) Corridor header (copy maxwell's shape, new content):
   - CORRIDOR: 1
   - TITLE { The Basel Problem -- Euler's Descent }
   - FLAVOR { ...short evocative line... }
   - LEDGER { ... }   <-- SEE LEDGER RULE below; must define the color keys you use
   - BRIEFING_INTRO { ...sets up the mission... }
   - ENTRY_TEXT { ... }
   - EXIT_TEXT { ...celebrates rescuing the hostages / solving Basel... }
   (Match whatever header keys maxwell_old.txt actually has — copy its set exactly.)

B) Seven ROBOT blocks (ROBOT: 1 .. ROBOT: 7), each with ALL 9 MANDATORY fields
   (the parser raises ParseError if any is missing):
     NAME { ... }                  (from the table; resolves to the portrait)
     BRIEFING_HINT { ... }         (one line; here is where the STEP/technique name
                                    lives, e.g. "Coefficient Matching")
     PROBLEM { ... }               (the puzzle this robot poses, with simple mathtext)
     EXPLAIN_MATHEMATICIAN { ... } (translate spine; mathtext-legal; rigorous voice)
     EXPLAIN_PHYSICIST { ... }     (translate spine; intuitive voice)
     EXPLAIN_BIOLOGIST { ... }     (translate spine; everyday-analogy voice)
     EXPLAIN_ENGINEER { ... }      (translate spine; practical/applied voice)
     SEGMENTS { ... }              (short colored math pieces; see SEGMENTS RULE)
     EYE { <ledger_key> }          (a key that EXISTS in your LEDGER, or NEUTRAL)
     VULNERABLE_TO { <id> }        (the id from the table — single value line)
   Plus the FIZZLES (below). Use the EXACT field names and brace syntax you see in
   maxwell_old.txt. Copy its EXPLAIN_* lengths/feel — do not write walls of text in
   the EXPLAIN fields; match maxwell's scale.

C) THE 42 FIZZLES (Nir's explicit, emphatic requirement):
   For EACH robot, write ONE fizzle for EACH OF THE 6 WRONG mathematicians (every
   other id in the arsenal). 7 robots x 6 wrong = 42 unique fizzles total.
   - Syntax: FIZZLE <wrong_id> { ...one sentence... }  (use maxwell_old.txt's exact
     FIZZLE syntax — confirm whether it's a single-line or block form).
   - Each fizzle is ~1 sentence. It must be GENEROUS and TEACHING: explain why that
     wrong mathematician's technique is REAL and valuable, but does not unlock THIS
     particular robot, and gently NUDGE toward the right idea WITHOUT NAMING the
     correct mathematician. Tone: warm, encouraging, "try again, here's a hint" —
     never a buzzer, never scolding.
   - Example shape (for robot 1 Euler, wrong shot = taylor):
       FIZZLE taylor { Taylor's series expansion is a genuine ingredient of this
       proof, but here you're being asked to NAME the famous result itself, not to
       expand a function -- think about WHO first summed these squares. }
     (Write your own; make all 42 distinct and specific to the (robot, wrong) pair.)
   - Every wrong id for a robot must be covered. Do NOT write a fizzle for the
     robot's OWN correct id (that's the win, not a fizzle).

--------------------------------------------------------------------------------
LEDGER RULE (colors — the engine is color-blind; meaning lives here)
--------------------------------------------------------------------------------
maxwell_old.txt has a LEDGER { ... } block. Read its exact syntax. Per DeepSeek &
the parser: the LEDGER must define PRIMARY entries with base colors red/yellow/blue
and may define BLEND entries combining two PRIMARY keys. EYE values and SEGMENTS
color-keys must reference keys DEFINED in this LEDGER (the parser validates this).
The baker file's STAINS give you a meaning->color story you can MIRROR (roots=red,
coeff_root=yellow, sine_fn=blue, product=orange[red+yellow], series=green[yellow+
blue], answer=purple[red+blue]). Translate that into the game LEDGER syntax (3
primaries + blends) using WHATEVER KEY NAMES and SYNTAX maxwell_old.txt uses. Keep
keys opaque/simple. Every key you reference in EYE or SEGMENTS MUST be defined here.

--------------------------------------------------------------------------------
SEGMENTS RULE
--------------------------------------------------------------------------------
SEGMENTS holds the short colored math fragments shown on the robot. Use maxwell's
exact SEGMENTS syntax (likely { $expr$ | colorkey } pieces). Keep each expr SHORT
and MATHTEXT-LEGAL. Use color keys from your LEDGER. Choose fragments that echo
that robot's step (e.g. robot 6 Hipparchus: $\sin x = 0$ at $x = n\pi$). SEGMENTS
is not parser-mandatory but a robot without it looks bare -- include it for all 7.

--------------------------------------------------------------------------------
WHAT TO WRITE — FILE 2: levels/basel.txt (manifest)
--------------------------------------------------------------------------------
Copy the shape of levels/maxwell.txt exactly. It must have:
  - title: The Basel Problem    (or matching style)
  - baked: ../baked/basel       (CONFIRM the relative path matches how maxwell.txt
                                 writes its baked: line and where baked/basel/ lives;
                                 match maxwell's convention EXACTLY)
  - corridors:
      ../corridors/basel.txt    (match maxwell.txt's relative-path convention)
Verify against levels/maxwell.txt's real text — match its exact key spellings,
order, and relative-path style.

--------------------------------------------------------------------------------
THINGS TO ASK NIR BEFORE FINISHING (do not guess these)
--------------------------------------------------------------------------------
1. NAME vs portrait-filename mismatch: the display NAMEs are capitalized (e.g.
   "al-Khwarizmi") but the files are lowercase ("al-khwarizmi-hologram.png").
   Since the portrait filename = NAME.replace(" ","_")+"-hologram.png", the case
   must match. Show Nir each of the 7 expected filenames your NAMEs produce vs the
   files he has, flag every mismatch (case, accents like "François"/"é",
   hyphens), and ask him to either (a) tell you the EXACT NAME string to use so the
   file is found, or (b) say he'll rename his PNGs. Resolve ALL 7 before done.
   (Pay special attention to accents: "François Viète" vs "viete-hologram.png" —
   these clearly differ; Nir must tell you the exact NAME to write.)
2. Arsenal source: confirm whether the 7 weapons are auto-derived from the robots'
   VULNERABLE_TO ids, or must be declared somewhere. If declared, get the syntax.

--------------------------------------------------------------------------------
HARD SCOPE FENCE — WHAT YOU MUST NOT DO
--------------------------------------------------------------------------------
- Do NOT edit, create, or "fix" any .py file. You read content_parser.py /
  robots.py / level_parser.py ONLY to learn syntax. ZERO code changes.
- Do NOT touch the baker, the baked PNGs, understanding.py, combat.py, app.py,
  render.py, or anything about flush_walls / the render loop.
- Do NOT invent new corridor-file fields or syntax. Use ONLY constructs that
  appear in maxwell_old.txt and are accepted by content_parser.py.
- Do NOT use forbidden mathtext (\tfrac, \dfrac, \displaystyle, \emph, etc.).
- Do NOT reorder/renumber the 7 robots (breaks the baked-PNG number mapping).
- Do NOT add distractor weapons. Exactly the 7 ids, no more, no fewer.
- Do NOT write the deep Understanding-Mode math (it's already baked).
- If you discover you need something outside writing these 2 files, STOP and
  REQUEST it from the parent via Nir — do not reach for it.

--------------------------------------------------------------------------------
DELIVERABLE FORMAT
--------------------------------------------------------------------------------
1. "What I verified" — confirmations from reading the real files: exact field set
   in maxwell_old.txt, exact LEDGER syntax, exact SEGMENTS syntax, exact FIZZLE
   syntax, the parser's mandatory-field list, the manifest key/path convention,
   and the 7 NAME->portrait-filename resolutions (with Nir's answers to ASK #1).
2. The COMPLETE corridors/basel.txt, ready to paste, in one code block.
3. The COMPLETE levels/basel.txt, ready to paste, in one code block.
4. A "fizzle map" table: 7 robots x their 6 fizzle ids = confirm all 42 present.
5. Any deviations/surprises (files win over this brief — report conflicts).
6. The Completion Report (template below).

--------------------------------------------------------------------------------
DEMO / ACCEPTANCE TEST (what Nir will run)
--------------------------------------------------------------------------------
DeepSeek commits both files. Then Nir runs the game pointed at levels/basel.txt
(confirm with DeepSeek how to launch a specific level — likely editing app.py's
level path or a launch arg; that is DeepSeek's job, NOT yours). Acceptance:
  1. Level loads with NO ParseError (all mandatory fields present, LEDGER valid,
     EYE keys defined, mathtext legal).
  2. Seven robots appear, in order, named after the 7 people; portraits load
     (or fall back to name-plate with a console note if a file is missing — note
     which, per ASK #1).
  3. Pressing U near robot N shows its baked PNG panels (these already exist);
     robots all have baked PNGs in baby/basel so NO "[UNDERSTANDING] FALLBACK"
     line should appear for any of the 7.  [If any DOES, report which robot/layer.]
  4. Firing the CORRECT mathematician at a robot defeats it; advancing through all
     7 reaches the hostages -> WIN.
  5. Firing a WRONG mathematician shows that robot's specific 1-sentence teaching
     fizzle (try a few; spot-check several of the 42).
ACCEPTANCE: loads clean, 7 robots correct, correct shots win through to hostages,
wrong shots give the right teaching fizzles, U shows baked panels with no fallback.

--------------------------------------------------------------------------------
COMPLETION REPORT TEMPLATE
--------------------------------------------------------------------------------
BRIEF #B — BASEL GAME CORRIDOR — COMPLETION REPORT
- Files written: corridors/basel.txt, levels/basel.txt
- Run-verified by me? (No -- Nir tests)
- maxwell_old.txt field set I mirrored: <list exact keys>
- LEDGER: my keys + colors (3 primaries + blends), all EYE/SEGMENTS keys defined? <y/n>
- Mandatory-field check: all 7 robots have all 9 required fields? <y/n>
- Mathtext audit: confirmed NO \tfrac/\displaystyle/\emph/forbidden cmds used? <y/n>
- The 7 NAME strings I used + the portrait filename each resolves to + Nir's
  resolution of every mismatch (case/accents): <table>
- Arsenal source confirmed: auto-derived from VULNERABLE_TO, or declared? <which>
- Fizzle count: 42 present? per-robot 6-wrong coverage table: <y/n + table>
- Robot 1..7 number/order matches baker spine (for baked-PNG mapping)? <y/n>
- levels/basel.txt: title/baked/corridors values + path convention matched? <show>
- DEVIATIONS from this brief / conflicts with real files (files win):
- REQUESTS TO PARENT (anything out of scope I needed):
================================================================================
END OF BRIEF #B
================================================================================
