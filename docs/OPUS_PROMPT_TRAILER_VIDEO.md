# OPUS PROMPT — How should we make a short autoplaying "trailer / looping video" for our game page?

> Paste this whole file to **Claude Opus 4.8** — the same judge + integrator who gave us the excellent
> packaging & distribution plan. (As before, you may gather answers from other models first and integrate
> them, or answer alone — your call.)

---

## ROLES & HOW TO GIVE YOUR ANSWER (please read this first)

You (Opus 4.8) are our **expert and decision-maker**. The one who will carry out your instructions is
**DeepSeek V4 Pro**, working inside **OpenCode** (an agentic coding assistant, like Claude Code, running on
my PC). **You do the thinking, the choosing, and the hard parts** and hand them to me as **copy-paste-ready
blocks**, because DeepSeek "can cure a headache but damage the liver": it executes precise instructions well
but is weak on holistic judgment.

We come to you like a **patient bringing symptoms**: **we do not know the options, and we are not qualified to
choose. Please diagnose and prescribe.** Tell us the alternatives, their honest pros and cons, rank them, pick
the best for us, explain why, and give step-by-step instructions for the best one.

Please give your **entire answer in a format I can copy and paste easily** — plain prose plus copy-paste-ready
command/code blocks. **Please do NOT use tables.**

---

## 0. WHO WE ARE / CONTEXT

- **Project:** *Peak Together* (peaktogether.me) — free, open-source **co-op educational games** for two
  players on one screen (couples, friends). Audience: ~15–25, mostly Windows, non-technical, terminal-phobic.
  Brand promise: *cozy, free, no signup, no friction.*
- **Person you're advising:** **Nir** (solo creator, GitHub: `strulovitz`). **Not** a professional programmer
  — please explain clearly and concretely.
- **The game:** **Descent QED** — a *Descent* (1995)-spirited game: you fly a little ship in **6-DOF** through
  corridors where each robot is a step of a real mathematical proof (the Basel problem, ∑1/n²=π²/6). It is
  DONE and, thanks to your packaging plan, now ships as a **one-click Windows download** on **itch.io**
  (https://strulovitz.itch.io/descent-qed) and **GitHub Releases**, linked from a dedicated game page on our
  site.

## 1. WHY WE'RE ASKING YOU

In your packaging answer you told us an in-browser playable demo is not realistic for this game, and instead
recommended putting a short, autoplaying, looping clip of the gameplay at the top of the game page as a
"try it instantly" hook. **We now want to do exactly that, and we need you to tell us how.**

## 2. OUR EXACT REALITY (facts so you can tailor your advice)

- **Our machine:** Windows 11 (64-bit). We are NOT targeting macOS.
- **The game is a desktop app** (Python: pygame + PyOpenGL, legacy fixed-function OpenGL, quaternion 6-DOF
  camera, runs at 60 FPS in a 1280×800 window). It has **no built-in way to record itself**, so any footage
  has to be captured from the screen while we play.
- **The website** is hand-written static HTML/CSS (no build system, no framework). A shared header/footer is
  injected by a tiny `components.js`. CSS is cache-busted with `style.css?v=N`. Images live in `/images/`.
- **The game page** that will hold the clip is `https://www.peaktogether.me/arcade/descent-qed/` (file:
  `arcade/descent-qed/index.html`). It already has a square hero-art image, four screenshots, and a
  click-to-enlarge lightbox. We'd put the looping clip at the **top** of the page.
- **Hosting:** our website is on **Dreamhost**, and we can only upload static files via **FileZilla** and edit
  `.htaccess` (no server-side processing). **⚠️ Hosting the video file itself on our Dreamhost is NOT an
  option** (bandwidth/limits) — so please tell us where else the video should live.
- **Everything must be free** (free tools, free hosting).
- It should be **silent** — no voiceover or music needed.

## 3. OUR GOAL (our symptoms — not a prescription)

A short looping clip at the top of the game page that starts playing by itself, quietly, loops smoothly, looks
good on both phones and computers, keeps the page fast, and makes a non-technical visitor instantly want to
download the game. We do not know how to record it, what to turn it into, where to host it, or how to put it
on the page. **Please tell us what is best.**

## 4. OUR QUESTIONS FOR YOU (please decide what is best for us)

For **each** question below, please tell us the realistic **alternatives**, give the honest **pros and cons of
each**, then **rank them and recommend the single best one for our exact situation**, explain **why**, and
give **step-by-step instructions for the best one**. (We don't know the alternatives — listing them and their
tradeoffs is exactly what we're asking you for.)

1. How should we **record footage of our game** on Windows, for free?
2. How should we **turn that footage into a short, smoothly-looping clip**, for free?
3. **What kind of file** should the finished clip be, so it plays well on a webpage across all browsers
   (including phones) while staying small and smooth?
4. **How do we put it on the page** so it starts by itself, loops, and is silent and looks good on phones and
   computers? Please give us the exact code for DeepSeek to paste in.
5. **Where should we host the video file for free?** (Reminder: our Dreamhost is **not** an option.) Please
   give the options with pros and cons, rank them for our cozy/no-friction brand, and recommend the best.
6. **What should we aim for** (length, quality, file size) so the page stays fast and the clip still looks
   great?
7. Please give us **one concrete, ordered, step-by-step plan** for the best path from start to finish, tailored
   to a solo non-expert on Windows 11 with FileZilla + GitHub. Tell us exactly what to use and what to do — we
   will follow your lead.

## 5. HOW TO ANSWER

Be thorough, honest, and practical. **You are the expert; we are not** — where there are tradeoffs, **choose
for us** and explain why. Hand the hard parts (any settings, any commands, and the final page code) to me as
**copy-paste-ready blocks**, since DeepSeek (in OpenCode) will paste and run them. **No tables, please.**
Please end with a clear, ordered **recommended plan we can act on.** Thank you so much!!! :-)
