# Peak Together -- Workflow for DeepSeek V4 Pro (OpenCode)

## Who's Who

| Role | Who | What |
|------|-----|------|
| **Architect** | Claude Fable (OpenRouter) | Provides the perfect "Bible" skeleton code |
| **Builder** | DeepSeek V4 Pro (OpenCode, this is YOU) | Copies Bible, fills in details, fixes bugs |
| **Boss** | Nir (strulovitz) | Decides everything, talks to Claude Fable, manages the website |

## The BIBLE System

- **BIBLE/math_flyer.py** = Claude Fable's original code. NEVER MODIFY IT. Only Claude Fable can authorize changes.
- **Working copy** = The actual downloadable `.py` file. You work on THIS.
- If you find a bug in the Bible, tell Nir. He asks Claude Fable. Claude Fable authorizes the fix. THEN you apply it to BOTH the Bible and the working copy.
- Document every Bible bug in `BIBLE/BUGS_FOUND_<bible_file>_<timestamp>.md` so Nir can show Claude Fable.

## Project Structure

```
peaktogether-website/          # GitHub repo (also Dreamhost live site)
├── BIBLE/
│   ├── math_flyer.py          # BIBLE -- DO NOT TOUCH without Claude Fable's OK
│   └── BUGS_FOUND_<name>_<timestamp>.md  # Bug reports for Claude Fable
├── mathematics/
│   └── Riemann_hypothesis/
│       └── Analytical_Path_Classical_and_Modern_Analytic_Number_Theory/
│           ├── index.html            # The webpage (edit THIS for demo callout)
│           └── harmonic_series_mathematics.py  # The working Python demo
├── index.html                  # Main homepage
├── style.css                   # Global styles (demo callout CSS is here)
├── WORKFLOW.md                 # THIS FILE -- read me first every session!
└── .gitignore                  # Ignores __pycache__, *.pyc, *.log
```

## How to Prompt Claude Fable (for Nir's reference)

Claude Fable lives on OpenRouter and has NO MEMORY between sessions. Every time you must tell him:

1. **Who you are**: "I am Nir, building Peak Together"
2. **What we did so far**: Brief summary of the project status
3. **The reference**: Link to Wikipedia section or specific illustration
4. **The request**: "Please make an interactive demo page for [topic]"
5. **Constraints**: "Follow our mathtext-only rule (no \\tfrac, \\dfrac, AMSMath). Use the same engine. The output should be a new @register_page class."

## Conventions

### Mathtext-Only Rule
- ALLOWED: `\frac`, `\sum`, `\geq`, `\cdots`, `\left(`, `\right)`, `\to`, `\infty`, `\mathbf`
- FORBIDDEN: `\tfrac`, `\dfrac`, `\underbrace`, `\binom` and ALL other AMSMath commands
- Reason: matplotlib's built-in mathtext has no full LaTeX installation

### Coding Conventions
- Python file: single-file, extendable via `@register_page` classes
- Each new Wikipedia concept = one new `Page` subclass
- Tab cycles between pages
- Engine code (camera, UI, LaTeX textures) -- DO NOT TOUCH
- Gamepad code goes ONLY in `GamepadManager` class
- Keyboard/mouse/controllers are additive (work simultaneously)

### HTML Editing on Windows
- **NEVER use PowerShell's Set-Content for HTML files** -- it corrupts UTF-8 emojis/special chars to Windows-1252
- **ALWAYS use Python** for any HTML file modifications:
  ```python
  with open(path, 'r', encoding='utf-8') as f: content = f.read()
  # ... do replacements ...
  with open(path, 'w', encoding='utf-8') as f: f.write(content)
  ```

### Dreamhost Deployment
- The website is hosted on Dreamhost (NOT GitHub Pages)
- Nir uploads via FileZilla from the local repo
- After renaming directories, manually delete the OLD directory on Dreamhost (FileZilla doesn't auto-delete)
- After renaming files, manually delete the OLD file on Dreamhost

## What We've Built So Far

| Page | Topic | Status |
|------|-------|--------|
| Page 1 | Harmonic Series -- Definition & Divergence | Done |
| Page 2 | Comparison Test (Oresme, ~1350) | Done |
| Page 3 | Integral Test | Coming next |

### Features Implemented
- 6-DOF quaternion camera (no gimbal lock)
- LaTeX rendering via matplotlib mathtext
- Keyboard flight controls (Descent-style)
- Mouse slider controls (Manipulate-style)
- Gamepad support: T.16000M joystick (pilot) + Xbox 360 (manipulator)
- Startup joystick calibration (60 frames)
- Radial and scalar deadzones
- GL display list caching for performance
- Crash logging to .log file
- Tab to cycle between pages

## Session Checklist (Read Me Every Time!)

1. Read this WORKFLOW.md
2. Check C:\Users\nir_s\peaktogether-website is up to date (`git pull`)
3. NEVER run commands that create/download large files without asking Nir
4. NEVER modify BIBLE/ without explicit permission
5. ONLY use Python (not PowerShell) for HTML edits
6. Tell Nir about ANY typo you find (don't silently fix or ignore)
7. After every meaningful change, commit and push
8. Ask Nir before doing ANYTHING you're unsure about

## Nir's Preferences
- Nir LOVES emojis -- use them abundantly in chat
- Nir does NOT know Python -- explain things simply
- The target audience is couples (boyfriend + girlfriend) on a gaming PC
- Verbatin Claude Fable descriptions for website callouts
- Be concise but cheerful
- Nir is the boss -- always ask before taking initiative
