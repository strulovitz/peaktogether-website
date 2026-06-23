# FUSION PROMPT — How to let anyone install & play our game (no terminal, no `python app.py`)

> Paste this whole file to **Fusion** on OpenRouter (the combined frontier-models + Claude-Opus-judge system).
> This is now our **#1 priority**, and it deserves a full, deep discussion in its own right — almost
> step-by-step, with practical detail. **You are the expert here; we are not. Please diagnose and prescribe.**

---

## 0. WHO WE ARE / CONTEXT

- **Project:** *Peak Together* (peaktogether.me) — free, open-source **co-op educational games** that turn the
  hardest unsolved problems in science/math into games for **two players on one screen** (couples, friends).
  Audience: **ages ~15–25, mostly Windows, who have very likely NEVER opened a terminal and do NOT have
  Python installed.** Brand promise: *cozy, free, no signup, no friction.*
- **Person you're advising:** **Nir** (solo creator, GitHub: `strulovitz`). Not a professional programmer —
  please explain clearly and concretely. We come to you like a patient bringing symptoms: **we don't know the
  right answer, and we are not qualified to choose — please tell us what is best for us.**
- **First finished game:** **Descent QED** — a remake of *Descent* (1995): you fly a ship in 6-DOF through
  corridors where each robot is a step of a real mathematical proof (the Basel problem, ∑1/n² = π²/6). It is
  DONE and playable today — but only by running `python app.py`.
- **This is the FIRST of MANY games.** Future games will be different genres (platformer, shoot-'em-up, RTS,
  point-and-click adventure, pinball, fighting game, etc.), almost all built in **Python with a similar tech
  stack**. They must **coexist on a user's machine without breaking it or colliding with each other.**

You once raised this exact problem in passing. Here it is **verbatim**, and now it is the main event:

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

Please now treat this as a full, standalone deep-dive. We will do whatever you recommend.

---

## 1. OUR EXACT TECH STACK & VERSIONS (facts — so you can tailor your advice)

- **Build machine:** Windows 11 (64-bit). **Primary user OS: Windows.** Linux support would be great.
  **We are NOT targeting macOS — please skip it entirely.**
- **Python:** **3.12.11** (CPython, on the dev machine).
- **Runtime libraries currently installed:**
  - **pygame 2.6.1** (bundles **SDL 2.28.4**)
  - **PyOpenGL 3.1.10**
  - **numpy 2.4.6**
  - **matplotlib 3.10.9**
- **Rendering:** **legacy fixed-function OpenGL** (`glBegin`/`glEnd`, display lists), driven through pygame's
  OpenGL window at 60 FPS, with a quaternion 6-DOF camera.
- **Input:** keyboard + mouse always work. **Optionally**, gamepads via pygame (a Thrustmaster T.16000M
  flight joystick and an Xbox 360 controller). The game runs fine with no controller.
- **Entry point today:** `cd descent && python app.py`
- **Code + assets:** ~16 engine `.py` modules + content files + **pre-baked PNG image assets (~20 MB)** +
  portrait PNGs. Assets are loaded by **relative path**.
- **matplotlib** is only a *runtime fallback* (the math is pre-baked into PNGs at development time); the LaTeX
  baking toolchain is **dev-only and is NOT shipped** to users.
- **Repo:** `github.com/strulovitz/peaktogether-website` (the game lives in the `/descent/` subfolder). Our
  current `requirements.txt` lists only `pygame / PyOpenGL / numpy` (unpinned, and missing matplotlib).

---

## 2. OUR HARD CONSTRAINTS (facts)

1. **Hosting = Dreamhost VPS, FileZilla only.** We can **ONLY upload static files via FileZilla SFTP/FTP** and
   edit `.htaccess`. We **cannot** SSH, install Python or any software server-side, run any server-side
   process, or change server config. So it can serve **static files and downloadable files** only. (Please
   also tell us if Dreamhost's storage/bandwidth makes it a bad place to host large downloads.)
2. **We have GitHub** (`strulovitz/peaktogether-website`).
3. **Users very likely have NO Python** and are **terminal-phobic.**
4. **We must not damage or change the user's existing system or Python** in any way.
5. **Many games are coming**; they must coexist on a user's machine **without colliding** with each other.
6. **Everything must be free** (free tools, free hosting).

---

## 3. OUR GOAL (our symptoms — not a prescription)

A non-technical 15–25-year-old should be able to go from *"saw it on peaktogether.me"* to *"playing the game"*
as effortlessly as possible — ideally without installing Python, without touching a terminal, and without any
risk to their computer. We do not know the right way to achieve this. We also do not know whether letting them
"try it instantly" in a browser is even realistic given our tech above. And we need somewhere free to host the
download. And we'd love a repeatable approach we can reuse for every future game.

---

## 4. OUR QUESTIONS FOR YOU (please decide what is best for us)

1. Given everything above, **how should a non-technical user (no Python, no terminal) install and run our
   game as easily as possible?** Please give your recommended approach, step by step.
2. Is letting users **"try it instantly" in a web browser** realistic for our game **as it is built**? If yes,
   how? If not, why — and what would you do instead?
3. **Where should we host the downloadable game** (and anything else) **for free**, given our
   Dreamhost-is-FileZilla-only-static + GitHub situation? What's best for our 15–25 audience, and why?
4. **How do we make sure that installing our games never harms or changes the user's existing system or
   Python**, and never conflicts between our own multiple games as the catalog grows?
5. We're worried users might see scary "unknown publisher" / security warnings when they download or run
   something — **is that a real problem for us, and what should we do about it?**
6. **What requirements / version setup should we standardize on** across all our games?
7. Please give us **one concrete, step-by-step plan tailored to our exact reality** (Windows dev machine,
   FileZilla static hosting, GitHub, a solo non-expert), so we can follow it for this game and reuse it for
   every future game. Tell us exactly which tools to use and what to do — **we will follow your lead.**

---

## 5. HOW TO ANSWER

Please be thorough, honest, and practical. **You are the expert; we are not** — where there are tradeoffs,
**choose for us** and explain why. Please end with a clear, ordered **recommended plan we can act on.**
Thank you so much!!! :-)
