# OPUS PROMPT — The best way to make a short autoplaying "trailer / looping video" for our game page

> Paste this whole file to **Claude Opus 4.8** — the same judge + integrator who gave us the excellent
> packaging & distribution plan. (If you like, you may again gather answers from other models first and
> have Opus integrate them — but Opus alone is fine.)

---

## ROLES & HOW TO GIVE YOUR ANSWER (please read this first)

You (Opus 4.8) are our **expert, judge, and integrator**. The one who will carry out your instructions is
**DeepSeek V4 Pro**, working inside **OpenCode** (an agentic coding assistant, like Claude Code, running on
my PC). **You do the design and the hard parts** (exact tools, exact settings, the HTML/CSS snippet) and hand
them to me as **copy-paste-ready blocks** — because DeepSeek "can cure a headache but damage the liver": it's
great at executing precise instructions but weak on holistic judgment. So please think holistically and
**choose for us**.

Please give your **entire answer in a format I can copy and paste easily** — plain prose plus copy-paste-ready
command/code blocks. **Please do NOT use tables.** Where there are tradeoffs, **decide for us and explain why.**

---

## 0. WHO WE ARE / CONTEXT

- **Project:** *Peak Together* (peaktogether.me) — free, open-source **co-op educational games** for two
  players on one screen (couples, friends). Audience: ~15–25, mostly Windows, non-technical, terminal-phobic.
  Brand promise: *cozy, free, no signup, no friction.*
- **Person you're advising:** **Nir** (solo creator, GitHub: `strulovitz`). **Not** a professional programmer
  — please explain clearly and concretely, and tell us exactly which tools to use.
- **The game:** **Descent QED** — a remake-spirited *Descent* (1995) game: you fly a little ship in **6-DOF**
  through corridors where each robot is a step of a real mathematical proof (the Basel problem, ∑1/n²=π²/6).
  It is DONE and, thanks to your packaging plan, now ships as a **one-click Windows download** on
  **itch.io** (https://strulovitz.itch.io/descent-qed) and **GitHub Releases**, linked from a dedicated game
  page on our site.

## 1. WHY WE'RE ASKING YOU (this is your own recommendation)

In your packaging & distribution answer, you told us that an in-browser playable demo is NOT realistic for
this game (it uses legacy fixed-function OpenGL, which WebGL can't run). Instead you recommended, verbatim:

> "put a high-quality, autoplaying, looping ~10-second MP4/GIF of the Basel-problem level at the top of your
> page. Make it so visually alive that people want the download. This gives you 90% of the 'try it instantly'
> conversion benefit with 1% of the effort."

**We now want to do exactly that.** This prompt is about HOW to make and ship that trailer/looping video well.

## 2. OUR EXACT TECH REALITY (facts so you can tailor your advice)

- **Dev machine:** Windows 11 (64-bit). We are NOT targeting macOS.
- **The game is a desktop app** (Python: pygame + PyOpenGL, legacy fixed-function OpenGL, quaternion 6-DOF
  camera, **runs at 60 FPS in a 1280×800 window**). So the only way to get footage is to **record the screen /
  game window while playing** — there is no built-in capture.
- **The website** is hand-written static HTML/CSS (no build system, no framework). A shared header/footer is
  injected by a tiny `components.js`. CSS is cache-busted with `style.css?v=N`. Images live in `/images/`.
- **The game page** that will hold the trailer is `https://www.peaktogether.me/arcade/descent-qed/`
  (file: `arcade/descent-qed/index.html`). It already has a square hero-art PNG, 4 screenshots, and a
  click-to-enlarge lightbox. We'd put the looping video **at the top**, ideally near/above the hero art.
- **Hosting = Dreamhost (shared/VPS), FileZilla only.** We can ONLY upload static files via FileZilla and edit
  `.htaccess`. No server-side processing. You earlier warned Dreamhost bandwidth isn't built for big files or
  viral spikes — so please weigh **self-hosting the video file vs. embedding from a free video host** with
  that in mind.
- **Everything must be free** (free tools, free hosting).
- **No microphone/voiceover needed** — this is a silent, muted, looping visual hook (autoplay on the web only
  works if muted anyway).

## 3. OUR GOAL (our symptoms — not a prescription)

A short, gorgeous, **autoplaying, looping, muted** clip (~6–12 seconds) at the top of the game page that makes
a non-technical visitor instantly *feel* the game and want to download it — while keeping the page fast, the
file small, and the brand cozy. We do not know the right tools, formats, or hosting choice. Please tell us.

## 4. OUR QUESTIONS FOR YOU (please decide what is best for us)

For **each** question, please lay out the realistic **alternatives**, give honest **pros and cons of each**,
then **rank them and recommend the single best one for our exact situation**, and explain **why**.

1. **Recording the gameplay on Windows, for free:** what's the best tool to capture clean 60-FPS footage of
   our game window (e.g. OBS Studio, Windows Xbox Game Bar, ShareX, ScreenToGif, NVIDIA/AMD overlays, others)?
   Alternatives, pros/cons, ranking, and your pick — plus the exact capture settings (resolution, fps,
   bitrate, codec) you'd use for our game.
2. **Editing/trimming into a tight, seamlessly-looping ~10s clip, for free:** best tool (e.g. Shotcut,
   DaVinci Resolve, Clipchamp, Kdenlive, or just `ffmpeg` commands)? How do we make the loop feel seamless
   (and is a crossfade worth it)? Alternatives, pros/cons, ranking, pick.
3. **The web format/codec for an autoplay hero loop:** MP4 (H.264/H.265) vs WebM (VP9/AV1) vs animated GIF vs
   APNG — for the best mix of small size, smoothness, and broad browser support (incl. iOS Safari autoplay
   quirks). Should we provide more than one source? Recommend.
4. **Embedding it correctly:** please give the **exact HTML/CSS** for a hero video that **autoplays, loops, is
   muted, is responsive, has a poster image (our hero art), plays inline on mobile, and respects
   `prefers-reduced-motion`** (and falls back gracefully). DeepSeek will paste this into the page.
5. **Where to host the video file, given Dreamhost-static-FileZilla-only + bandwidth worries:** self-host the
   file on Dreamhost vs. host on a free service and embed (YouTube, etc.) vs. put it on GitHub/Releases vs.
   itch.io. Pros/cons for our cozy/no-friction brand and our bandwidth limits, ranked, with your pick.
6. **Target specs / budget:** what resolution, length, fps, bitrate, and **file-size budget** should we aim
   for so the page stays fast?
7. **One concrete, ordered, step-by-step plan** for the best path end-to-end — record → trim → make it loop →
   encode → shrink the file → host → embed — tailored to a solo non-expert on Windows 11 with FileZilla +
   GitHub. Tell us exactly which tools and exact settings/commands to use; we will follow your lead.

## 5. HOW TO ANSWER

Be thorough, honest, and practical. **You are the expert; we are not** — where there are tradeoffs, **choose
for us** and explain why. **You do the design and the hard code** (capture settings, any `ffmpeg` commands,
and the final HTML/CSS), and hand it to me as **copy-paste-ready blocks**, since DeepSeek (in OpenCode) will
paste and run them. **No tables, please.** Please end with a clear, ordered **recommended plan we can act on.**
Thank you so much!!! :-)
