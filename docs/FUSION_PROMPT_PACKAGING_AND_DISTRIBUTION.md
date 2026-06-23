# FUSION PROMPT — PACKAGING & DISTRIBUTION (one-click install, no `python app.py`)

> Paste this whole file to **Fusion** on OpenRouter (the combined frontier-models + Claude-Opus-judge system).
> This is now our **#1 priority** topic. Our first game is finished and works; the only thing between it and
> real players is **how a non-technical 15–25-year-old actually installs and runs it.** Please treat this as a
> full, standalone deep-dive — almost step-by-step, with practical detail, ranked options, and honest tradeoffs.

---

## 0. WHO WE ARE / WHAT TO KNOW

- **Project:** *Peak Together* (peaktogether.me) — free, open-source **co-op educational games** that turn the
  hardest unsolved problems in science/math into games for **two players on one screen** (couples, friends).
  Target audience: **ages ~15–25, mostly Windows, who have very likely NEVER opened a terminal and do NOT
  have Python installed.** Brand promise: *cozy, free, no signup, no friction.*
- **Person you're advising:** **Nir** (solo creator, GitHub: `strulovitz`). Not a professional programmer;
  please explain clearly and concretely, "do exactly this" style. Has ADHD — keep structure explicit,
  one decision at a time, and rank the options.
- **First finished game:** **Descent QED** — a remake of *Descent* (1995): you fly a ship in 6-DOF through
  corridors where each robot is a step of a real mathematical proof (the Basel problem, ∑1/n² = π²/6, on the
  way to the Riemann Hypothesis). It is DONE and playable today via `python app.py`.
- **This is the FIRST of MANY games.** Future games will be different genres (platformer, shoot-'em-up, RTS,
  point-and-click adventure, pinball, fighting game, etc.), almost all built in **Python with a similar tech
  stack**. They must **not collide with each other** on a user's machine.

You (Fusion) once raised this exact problem as a side note. Here it is **verbatim**, and now it is the main event:

> **6. Honest critique — the things that will still cost you users (and how to fix them)**
>
> ⚠️ 1 — `python app.py` is your single biggest threat. This is the one that will silently kill most of your
> traffic. The vast majority of 15–25-year-olds have never opened a terminal, don't have Python installed,
> and will hit a wall the moment something needs `pip install pygame`. Your whole "cozy and accessible" brand
> collapses at that command.
>
>     Fix, in order of impact: (a) Browser-playable demo — Pygame can run in-browser via pygbag/WebAssembly.
>     "Try it instantly, no install" next to the download button would transform your conversion.
>     (b) One-click executables — use PyInstaller to ship a .exe/.app so non-coders just double-click; keep
>     the python app.py path for the GitHub crowd. (c) At minimum, a screenshot-by-screenshot "Install in 2
>     minutes" guide — and include a requirements.txt + pip install -r requirements.txt step, because missing
>     dependencies are the #1 silent failure your current pitch ignores.

Please now elaborate on this **A LOT**, as a full discussion in its own right.

---

## 1. OUR EXACT TECH STACK & VERSIONS (please tailor all advice to these)

- **OS we build on:** Windows 11 (64-bit). **Primary user OS: Windows.** Linux support is *ideal*.
  **We are NOT targeting macOS — please skip macOS entirely (no `.app`/`.dmg`/notarization/Gatekeeper talk).**
- **Python:** **3.12.11** (CPython, from a Miniconda base env on the dev machine).
- **Runtime libraries (currently installed versions):**
  - **pygame 2.6.1** (bundles **SDL 2.28.4**)
  - **PyOpenGL 3.1.10**
  - **numpy 2.4.6**
  - **matplotlib 3.10.9**
- **Rendering:** **legacy fixed-function OpenGL** (`glBegin`/`glEnd`, display lists, `GL_LINE_STIPPLE`),
  driven through pygame's OpenGL window at 60 FPS, with a quaternion-based 6-DOF camera. **This matters a lot
  for the browser question — see §3.**
- **Input:** keyboard + mouse always work. **Optional** gamepads via pygame: a Thrustmaster **T.16000M flight
  joystick** (pilot) and an **Xbox 360 controller** (navigator). The game must run fine with NO controller.
- **Entry point today:** `cd descent && python app.py`
- **Code + assets:** ~16 engine `.py` modules + content files (`corridors/`, `levels/`) + **pre-baked PNG
  image assets (~20 MB of `baked/` images)** + portrait PNGs. Assets are loaded by **relative path** (this is
  a known packaging gotcha — frozen apps need correct resource-path handling).
- **About matplotlib:** the game pre-bakes all its LaTeX/math into PNG images **at development time**; at
  **runtime**, matplotlib is only a *fallback* renderer. The heavy **LaTeX + TikZ baking toolchain is
  DEV-ONLY and is NOT shipped to users.** (matplotlib is still imported at runtime, though — so for now treat
  it as a runtime dependency unless you advise removing it.)
- **Repo:** `github.com/strulovitz/peaktogether-website` (the game lives in the `/descent/` subfolder of the
  website repo). Our existing `descent/descent_qed/requirements.txt` is just `pygame / PyOpenGL / numpy`
  (UNPINNED and **missing matplotlib**) — please tell us the correct pinned `requirements.txt`.

---

## 2. OUR HARD CONSTRAINTS (please respect these — they shape every answer)

1. **Hosting = Dreamhost VPS, FileZilla only.** The website lives on a Dreamhost virtual private server where
   Nir **can ONLY upload static files via FileZilla SFTP/FTP** and edit `.htaccess`. He **cannot** SSH, cannot
   install Python or any software server-side, cannot run any server-side process, cannot change server
   config. → Dreamhost can serve **static files and downloadable binaries** only. (Please also warn us about
   Dreamhost **storage/bandwidth limits** if we host large binaries there, and whether that's wise.)
2. **GitHub is available** (`strulovitz/peaktogether-website`) for code and possibly **GitHub Releases** for
   binaries.
3. **Users likely have NO Python** and are **terminal-phobic.** The dream is a **`setup.exe`-style one-click
   installer** they download and run, that "just works" (and a Linux equivalent if possible).
4. **Do NOT damage the user's system.** If they *do* happen to have Python, we must not overwrite it, not do
   global `pip install`s, not change their PATH destructively, not break their existing setup. Strongly prefer
   a **fully self-contained / bundled runtime** that ignores any system Python.
5. **Multi-game, no collisions.** This is game #1 of many (different genres, similar Python stack). The
   distribution architecture must let many games coexist on one machine **without dependency/version
   collisions**, and ideally be repeatable/cheap to apply to each new game.
6. Everything must be **free** (free tools, free hosting) — this is a free, open-source passion project.

---

## 3. A TECHNICAL REALITY WE WANT YOU TO ADDRESS HONESTLY (the browser-demo question)

The earlier advice suggested a **pygbag/WebAssembly browser demo**. But our renderer uses **PyOpenGL
desktop fixed-function OpenGL** (`glBegin/glEnd`, display lists) **and matplotlib**. As far as we understand,
pygbag targets **pygame/SDL** drawing and does **not** cleanly support **PyOpenGL desktop GL** or
**matplotlib** in the browser (browser GL is WebGL/GLES, which doesn't expose fixed-function calls).

**Please assess this honestly:**
- Is a pygbag/WASM browser build realistically possible for THIS game **as built**, or would it require
  rewriting the renderer (e.g., to pure pygame 2D, or to modern shader-based GLES/WebGL)?
- If it needs a rewrite: is a small **separate "browser teaser" demo** (a tiny, 2D, pygame-only slice that
  *does* run in pygbag) a smarter use of effort than porting the whole 3D game?
- Or should we **deprioritize the browser path entirely** for now and put all effort into a flawless
  **one-click desktop installer**? Give your honest recommendation with reasoning.
- Note: a pygbag build outputs **static HTML/JS/WASM files**, which our Dreamhost (static-only) **could**
  serve — so hosting the output isn't the blocker; feasibility of the port is.

---

## 4. THE QUESTIONS (please answer each in depth, with ranked options + pros/cons)

**Q1 — Browser-playable demo:** feasibility for our PyOpenGL + matplotlib stack (see §3). Recommend keep,
cut-down, or skip — and why.

**Q2 — One-click executable (the bundle):** Compare and **rank** the freezing tools for bundling
pygame + PyOpenGL + numpy + matplotlib on Python 3.12 → **PyInstaller vs Nuitka vs cx_Freeze vs
Briefcase/BeeWare** (and anything better). For the winner, cover concretely:
- handling **PyOpenGL / OpenGL drivers** and **pygame/SDL** in a frozen build;
- the **relative-asset-path** problem (e.g., PyInstaller `--add-data`, `sys._MEIPASS`);
- **download size** (matplotlib + numpy are heavy — can/should we drop matplotlib to shrink it?);
- **Windows SmartScreen / "Unknown publisher"** warnings on an unsigned `.exe` (a real conversion-killer for
  scared young users) — how bad is it, and what are the **free or cheap** mitigations (code signing options,
  costs, alternatives)? **Antivirus false positives** with PyInstaller — how to avoid/handle.

**Q3 — A real installer (the dream `setup.exe`):** Should we wrap the bundle in **Inno Setup** or **NSIS**
(free) to produce a true `setup.exe` with a Start-Menu shortcut, desktop icon, and uninstaller? Rank them and
give the recommended approach. For **Linux**, rank **AppImage vs Flatpak vs .deb vs plain tarball** for a
double-click experience. **(We are NOT targeting macOS — please skip it entirely.)**

**Q4 — FREE hosting for the downloadable installer/zip (and any browser build):** Give us a few **free**
options with pros/cons, then **rank them for OUR needs** (educational game, ages 15–25, growing catalog).
Please consider at least: **itch.io** (does its free tier / the itch app / HTML5 embeds fit us well?),
**GitHub Releases**, **GitHub Pages** (for a static WASM demo), **SourceForge**, hosting **directly on
Dreamhost** (mind storage/bandwidth), and anything else. Address **per-file size limits, bandwidth, ease of
updates, and audience fit.**

**Q5 — No-collision, no-damage strategy (very important):** Rank approaches for isolation:
**(a)** fully bundled runtime (PyInstaller/Nuitka — ships its own Python, ignores system Python),
**(b)** an installer that creates a dedicated **venv**, **(c)** conda/embeddable-Python approaches, etc. —
which best guarantees we never touch the user's existing Python/system? Then advise the **multi-game
architecture**: should each game be a **fully self-contained bundle** (simple, larger downloads, zero
collisions), or should we build a **shared "Peak Together" launcher/runtime** that installs once and then
downloads/runs individual games (smaller per-game, more engineering)? Pros/cons and a **recommended path for a
catalog that will keep growing**, given Nir is a solo non-expert.

**Q6 — `requirements.txt`:** give us the exact **pinned** versions to standardize across ALL our games
(based on §1), and say whether to keep matplotlib.

**Q7 — The concrete pipeline for ME (almost step-by-step):** Given my reality (Windows 11 dev machine,
Dreamhost+FileZilla static hosting, GitHub, solo non-expert, target users on Windows with no Python),
tell me **exactly what to do**: which tools to install on my PC, the exact build commands, how to produce the
Windows installer (and Linux), where to upload each artifact, and what the **end-user experience** looks like
from "clicks a button on peaktogether.me" → "playing the game." Make it repeatable so I can reuse it for
every future game.

---

## 5. OUTPUT FORMAT REQUEST

Please be thorough and **practical**: use ranked comparison tables (tool / pros / cons / verdict), concrete
commands, and a clear final **"recommended plan for Nir"** at the end. Be honest about tradeoffs and effort —
if something is a bad idea for our constraints, say so plainly. Thank you so much!!! :-)
