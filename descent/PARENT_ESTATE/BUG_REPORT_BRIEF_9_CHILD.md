# BUG REPORT — BRIEF #9 CHILD (everything wrong + what should be right)

## For Claude Opus 4.8 (Parent/Architect)

The child you dispatched wrote code that CANNOT work because it hallucinated
the format and architecture of the existing engine. Below is every error,
organized by category, with the CORRECT facts alongside each one so you can
write a precise new brief.

---

## 🔴 FATAL: Corridor fixture format (Part B)

The child invented its own corridor file format instead of matching the
existing one. Here is the VERBATIM correct format from the working
corridor fixture `01_dummy.txt`:

```
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
VULNERABLE_TO { dummy_technique }
FIZZLE BAR { The technique BAR does not apply here because this is a
             placeholder and BAR is the wrong placeholder. }
FIZZLE BAZ { BAZ fizzles: it solves a different dummy problem. }
```

### Every format error the child made:

| Wrong (child) | Correct | Notes |
|---------------|---------|-------|
| No CORRIDOR/TITLE/BRIEFING_INTRO/ENTRY_TEXT/EXIT_TEXT | All 6 header blocks REQUIRED | Parser raises ParseError if any are missing |
| `ROBOT { number 1` | `ROBOT: 1` | Colon, no braces. ROBOT: is a single-value line, NOT a block |
| `LEDGER { red = electric field E` | `PRIMARY red = red` | KEYWORD key = red/yellow/blue |
| `EXPLAIN_WHAT`, `EXPLAIN_WHY`, `EXPLAIN_HOW`, `EXPLAIN_SO` | `EXPLAIN_MATHEMATICIAN`, `EXPLAIN_PHYSICIST`, `EXPLAIN_BIOLOGIST`, `EXPLAIN_ENGINEER` | These exact 4 names are REQUIRED; any other name raises ParseError |
| `\dfrac` in SEGMENTS | `\frac` only | `\dfrac` and `\tfrac` are FORBIDDEN (mathtext-only rule) |
| No `$...$` in SEGMENTS | `$\nabla \cdot \mathbf{E} = \frac{\rho}{\varepsilon_0}$` | SEGMENTS lines require $ wrappers |
| `eye_color_key: str` not mentioned | Field exists but child didn't check | The child used `eye_color_key` correctly in Part A |

### LEVEL MANIFEST — this part was correct ✅
```
title: Maxwell Test Corridor
corridors:
  ../corridors/maxwell.txt
```
Paths resolve relative to the manifest's directory (levels/).

---

## 🔴 FATAL: Parser architecture (Part A)

The child wrote a `_parse_vulnerable_to()` helper using line-by-line regex,
but the parser uses a TOKENIZER (`_tokenize()`) that pre-parses the file into
`("block", keyword, arg, body, lineno)` tuples. The VULNERABLE_TO directive
should be handled INSIDE `_parse_robot()`'s existing `if keyword == "..."` 
block-token dispatch, alongside `NAME`, `EYE`, `FIZZLE`, etc.

### Correct VULNERABLE_TO integration pattern:

1. In `_parse_robot()`, add `required_technique_id = None` alongside the other
   per-robot accumulators (name, problem, eye, fizzles, etc.)

2. In the token dispatch loop, add:
   ```python
   elif keyword == "VULNERABLE_TO":
       tok_id = _clean_body(body).strip()
       if not re.match(r'^[A-Za-z0-9_]+$', tok_id):
           raise ParseError(...)
       required_technique_id = tok_id
   ```

3. After the loop, enforce required:
   ```python
   if required_technique_id is None:
       raise ParseError(f"{fname}: robot {number} missing VULNERABLE_TO block")
   ```

4. Pass to RobotData constructor:
   ```python
   required_technique_id=required_technique_id,
   ```

---

## 🔴 FATAL: Quaternion / math duplication (Part C)

The child wrote ~80 lines of quaternion math (`_q_slerp`, `_look_quaternion`,
`_q_normalize`) that DUPLICATE functions already in `render.py`:

| Child wrote | Already in render.py | Verbatim signature |
|-------------|---------------------|-------------------|
| `_look_quaternion(eye, target, up_hint)` | `render.quat_look_along(direction, up)` | Takes a DIRECTION vector (target-eye), NOT eye+target |
| `_q_slerp(q0, q1, t)` | NOT in render, but `render.quat_mul(a, b)` and `render.quat_normalize(q)` exist | Child can build slerp from these |
| `_q_normalize(q)` | `render.quat_normalize(q)` | Identical |

**Tell children to use `render.quat_look_along(direction)`** — it's verified
and existing. They should NOT reinvent quaternion math.

---

## 🟡 MEDIUM: Robot data access (Part C)

The child tries to access `robot.fizzles` directly, but:

- `fizzles` is a field on `RobotData` (the data object)
- `Robot` objects do NOT store `fizzles` or `RobotData` directly
- After Part A changes, `Robot` stores `self._robot_data` (the full RobotData)
- So `robot._robot_data.fizzles` is the correct access, OR expose it via a
  new `@property` on Robot

The child also tried `getattr(robot, "_robot_data", None) or getattr(robot, "robot_data", None)` — this is fragile. Give the child the exact access path.

### Correct data layout after Part A:

```
RobotData (parsed from file)
  .number, .name, .problem, .explain, .segments, .eye_color_key,
  .fizzles (dict: technique_id -> "why not" text),
  .required_technique_id (NEW)

Robot (runtime object, built by corridor_builder)
  .name, .position, .base_pos, .size, .eye_color
  .number (@property -> robot_data.number)              [NEW in Part A]
  .required_technique_id (@property -> robot_data.required_technique_id) [NEW]
  ._robot_data  (private, stores full RobotData)         [NEW in Part A]
  .is_defeated(), .play_defeat(), .update(...), .draw(...)
```

---

## 🟡 MEDIUM: Hologram filename uncertainty

The child's README lists two naming schemes:
1. Manifest: `holograms/gauss.png`, `holograms/faraday.png`, etc.
2. NAME-derived: `Gauss's Law (Electric)-hologram.png` (with spaces/apostrophes/parens!)

**How robots.py actually loads holograms** (verbatim from code):
```python
def _portrait_filename(name):
    return name.strip().replace(" ", "_") + "-hologram.png"
```
So `NAME { Gauss's Law (Electric) }` becomes:
`Gauss's_Law_(Electric)-hologram.png` — apostrophes and parens are NOT escaped!

**The child must either:**
- Use clean NAME fields without special characters (e.g. "Gauss Electric", "Gauss Magnetic")
- OR the parent must tell the child the exact hologram filename and the child must
  name robots accordingly

---

## 🟢 OK: Parts that were actually fine

- Part A dataclass change (adding required_technique_id) ✅
- Part A Robot properties (.number, .required_technique_id) ✅
- Part A dummy fixture additions (VULNERABLE_TO line) ✅
- Part D wiring instructions (conceptually correct) ✅
- The manifest format (levels/maxwell.txt) ✅
- Combat logic (fire/mismatch/autoface/slerp algorithm) ✅
- Key-binding choices (SPACE, [, ]) don't collide ✅

---

## 📋 SUMMARY FOR THE PARENT

When writing the new child brief, you MUST paste verbatim:
1. A working corridor fixture example (01_dummy.txt robot block shown above)
2. The RobotData dataclass definition
3. The 2D HUD signatures from render.py
4. The quaternion helpers from render.py (quat_look_along, quat_mul, etc.)
5. The exact hologram filename formula: `name.replace(" ", "_") + "-hologram.png"`
6. The Robot public members (position, is_defeated, play_defeat, etc.)

Without these verbatim pastes, another child will hallucinate the format again.
