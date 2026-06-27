# 🏔️ MOUNTAIN PLAYBOOK — How to Process a Peak Together Mountain 🏔️

> My (DeepSeek's) complete guide for turning one of Nir's "Deep Research" documents into a
> set of website pages, in the exact Peak Together style. Read this FIRST whenever we work
> on the website's math/physics/chemistry/biology "mountains."
> Author: DeepSeek V4 Pro in OpenCode. For: Nir (GitHub: strulovitz).

---

## 0. The big picture — what a "mountain" is

- Each famous problem (Clay Millennium problems, etc.) is a **"mountain."**
- **Nir assigns a real-world mountain name** as a metaphor. I **NEVER invent it** — Nir tells me.
  - 🏔️ **Everest = Riemann Hypothesis** (the first, most famous; fully "fattened")
  - 🏔️ **Annapurna I = Navier–Stokes Existence & Smoothness** (built as a skeleton)
- **Nir also tells me the SUBJECT** = which top-level folder it lives in: **Mathematics / Physics / Chemistry / Biology.**

### The 4-level hierarchy (ALWAYS mirror this)
```
🏔️ MOUNTAIN (hub page)  →  intro + "Choose Your Path" grid of path-cards
   └── 🧗 PATH (one page each)  →  several Base Camps
          └── ⛺ BASE CAMP (a section on the path page)  →  description + Stepping Stones + sources
                 └── 🪨 STEPPING STONE  →  a key theorem / result / concept (a bullet)
```
- **Hub page** = `index.html` in the mountain folder. Intro + `<h2>Choose Your Path</h2>` + a
  `.path-grid` of `.path-card` links (one per path).
- **Path page** = `index.html` in each path folder. `<h1>` = path title; then each **Base Camp**
  as an `<h2>` (description `<p>`), an `<h3>Stepping Stones</h3>` + `<ul>`, and finally a
  `<h2>What to Upload Next</h2>` section listing that path's sources grouped by base camp.

### Two stages of a mountain (Nir's words)
- **Gold standard (Riemann only, so far):** a *skeleton* doc (all paths + base camps lightly
  described) **plus** a separate per-path deep dive that "fattens" each base camp into its own
  full page (the numbered `01-...`, `02-...` sub-folders under each RH path).
- **Every other mountain (for now):** **SKELETON ONLY** — one Deep Research doc per mountain.
  Build base camps as **sections within the path pages** (no separate base-camp sub-pages yet).
  Later, Nir's per-path deep dives can "fatten" them into their own pages, RH-style.

---

## 1. The SACRED rules (never break these)

1. **Text is HOLY / VERBATIM.** Copy Nir's research text **word-for-word**: nothing added,
   removed, reworded, or "improved." The only allowed touches are: HTML structure, wrapping
   math in `$...$`, and fixing **obvious LaTeX copy-artifacts** (see §4) — and even those only
   with Nir's OK.
2. **NOTHING LOST.** Every word of the research must end up on the site. If I'm unsure where a
   chunk belongs, **ASK Nir** — never drop it, never guess.
3. **Keep prose typos/oddities verbatim** (e.g. `Hőlder`, `G. 1. Seregin`, `%'hopf'%`). Flag
   them so Nir knows, but do NOT change them unless he says so.
4. **Don't reorganize** the doc's structure. Follow its own Paths / Base Camps / Stepping Stones.
5. **Only the MOUNTAIN goes in the top menu** — not every base camp. In-page cards/links handle
   the rest (just like Riemann).
6. **Ask before anything that could break what already works.** Building NEW pages + adding menu
   links is additive and safe.

---

## 2. The content pipeline (how Nir delivers the text)

- ✅ **GOLD pipeline = direct copy+paste from the ChatGPT web chat into our chat.** The math
  arrives as real **LaTeX** (`$...$`), exactly what our MathJax wants.
- ❌ Do NOT rely on: **PDF** (mangles/loses equations), **DOCX** (I can't read it cleanly),
  **Acrobat→HTML** (messy & slow).
- The paste usually contains **CONTEXT to ignore** (NOT website content unless Nir says keep):
  old PDF filenames, the "COPY/PASTE PROMPT," ChatGPT's clarifying Q&A, the "I'll let you know…"
  preamble, and a trailing **"Citations" URL list**.
- The blueprint is often **pasted twice** → **use ONE copy.**

---

## 3. The exact page template (copy from Riemann)

Reference files:
- Hub example: `mathematics/Riemann_hypothesis/index.html`
- Path example: `mathematics/Riemann_hypothesis/Analytical_Path_Classical_and_Modern_Analytic_Number_Theory/index.html`

Every page = this shell:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>... — Peak Together</title>
    <link rel="stylesheet" href="/style.css?v=24">
</head>
<body>

    <div data-component="header"></div>

    <main class="page">
        ... content ...
        <a href="..." class="back-link">← Back to ...</a>
    </main>

    <div data-component="footer"></div>

    <script src="/components.js?v=3"></script>
</body>
</html>
```

How it works:
- `header.html` + `footer.html` are **shared components** injected by `/components.js` into the
  `data-component="header"`/`"footer"` divs.
- **MathJax** auto-loads via `components.js`: inline `$...$`, display `$$...$$` / `\[...\]`.
- CSS classes available: `.page`, `.subtitle`, `.path-grid`, `.path-card`, `.back-link`.

### Hub page specifics
- `<h1>🏔️ <Mountain>: The <Problem Name></h1>` (e.g. `🏔️ Annapurna I: The Navier–Stokes Existence and Smoothness Problem`)
- `<p class="subtitle">…</p>` — **site chrome** (my words, NOT research). Mirror RH's tone:
  mention the `$1,000,000` Clay prize + "Together, we climb." (Keep the `$` the only one in that
  element so MathJax doesn't mis-parse it.)
- A short 2-paragraph intro (**site chrome**), then `<h2>Choose Your Path</h2>` + a
  `.path-grid` with one `.path-card` per path (each card: `<h3>` title + `<p>` one-line blurb,
  blurbs are site chrome).
- Back-link: `← Back to Home` → `/`.

### Path page specifics
- `<h1>` = the path's title, verbatim (e.g. `Path 1: Foundational Formulation and Existence Theory`).
- Per Base Camp: `<h2>Base Camp X.Y – Title</h2>` + description `<p>` + `<h3>Stepping Stones</h3>`
  + `<ul>` of `<li><strong>Stepping Stone: Name</strong> – text</li>`.
- Then `<h2>What to Upload Next</h2>` + `<p>` intro + per-base-camp `<h3>` + `<ul>` of sources.
  **Italicize book titles** with `<em>`; leave paper titles in their quotes; authors verbatim.
- Back-link: `← Back to <Problem>` → absolute hub URL.

> ⚠️ Hub uses **path-cards** (no `<li>`); path pages use **`<ul>`/`<li>`** (no path-cards).

---

## 4. Fixing broken math (the ChatGPT copy drops characters)

ChatGPT's web copy silently **drops `\`, `_`, `*`** etc., so some equations render broken.
This is **Option A** (Nir's choice): for each broken equation, I propose the corrected LaTeX,
list them all in ONE message, and Nir approves (he can't read math but trusts me; I still show him).

Typical fixes seen on Navier–Stokes (pattern → repair):
- `T^$`            → `T^*$`            (lost `*`)
- `|\omega|{\infty}` → `|\omega|_{\infty}`   (lost `_`)
- `\int_0^T!`      → `\int_0^T\!`      (lost `\`)
- `,ds`            → `\,ds`            (lost `\`)
- `_{\infty,,\infty}` → `_{\infty,\infty}`  (double comma)
- `}{p,\infty}`    → `}_{p,\infty}`    (lost `_`)
- `F!\Big(`        → `F\!\Big(`        (lost `\`)
- `$-\epsilon$ regularity` → `$\varepsilon$-regularity` (confirm via nearby correct usage)

After applying: VERIFY 0 broken patterns remain and each fix is present (see §7).

---

## 5. 🔴 CRITICAL technical gotcha — HTML-escape math & prose

The browser parses HTML **before** MathJax runs. A raw `<` followed by a letter (e.g. `t<T`)
is read as a tag and **breaks the page**. So in ALL content (prose AND inside `$...$`):
- `&` → `&amp;`
- `<` → `&lt;`   (e.g. `\sup_{t&lt;T}`, `2/p+3/q&lt;1`, `p&lt;\infty`)
- `>` → `&gt;`   (e.g. `T&gt;0`, `3/2&gt;1`, `t&gt;0`)

MathJax decodes the entities back to real characters before typesetting, so escaping is safe
and **required**. Also:
- Keep an **unpaired `$`** (like the `$1,000,000` prize) as the only `$` in its element.
- Preserve **UTF-8** literally: `Šverák`, `Růžička`, `Nečas`, Greek `θ`, en-dashes `–`, curly
  quotes `“ ” ’`, etc. (pages are `charset="UTF-8"`).
- Use `&ldquo; &rdquo;` for the doc's curly double-quotes when convenient.

---

## 6. Folders, URLs & the menu

- Mountain hub: `/<subject>/<Problem_Folder>/index.html`
  e.g. `/mathematics/Navier-Stokes_existence_and_smoothness/`
- Path folders: `Path_N_<Short_Name>/index.html`
- Folder/URL names are **NOT holy** — I pick clean ASCII names (hyphens/underscores).
- **Menu lives ONCE in `/header.html`.** To add a mountain, add under the subject's submenu:
  ```html
  <li><a href="/<subject>/<folder>/">Display Name</a></li>
  ```
  - Mathematics submenu already exists (Riemann Hypothesis, Navier–Stokes…).
  - Physics / Chemistry / Biology currently show
    `<li><span class="submenu-coming">Coming soon</span></li>` — replace that with real link(s)
    when their first mountain arrives.

---

## 7. Verification (Windows / PowerShell 5.1 — `rg` is NOT installed!)

Use `Select-String -SimpleMatch` (NOT ripgrep). After building, confirm:
1. **All index.html files exist** (hub + each path).
2. **Broken LaTeX patterns = 0** and **each fix present ≥ 1** (loop the §4 lists).
3. **No raw unescaped math** `<`/`>` (search `t<T`, `q<1`, `p<\infty`, `T>0`, etc. → all 0).
4. **Structure counts** per file (`<h2>`, `<li>`, `path-card`) match expectations:
   - hub: `path-card` = number of paths
   - path page: `<li>` = (stepping stones) + (sources) ; `<h2>` = (base camps) + 1 ("What to Upload Next")

Example PowerShell skeleton:
```powershell
$ns = "C:\Users\nir_s\peaktogether-website\mathematics\<Mountain_Folder>"
$files = Get-ChildItem -Path $ns -Recurse -Filter index.html
$files | Select-String -SimpleMatch -Pattern 'T^$'   # broken → expect 0
$files | Select-String -SimpleMatch -Pattern 'T^*'   # fixed  → expect >=1
```

---

## 8. End-to-end workflow per mountain

1. Nir gives: **mountain name** + **subject** + **pasted Deep Research text**.
2. Identify the structure **from the doc** (paths → base camps → stepping stones → sources).
3. **Scan math**, list all broken-LaTeX fixes in one message, get Nir's OK (Option A).
4. Drop the **duplicate** paste + all **context/meta** (PDF names, prompt, Q&A, citations).
5. Create folders; build **hub + path pages** from the Riemann template — verbatim + fixes +
   HTML-escaping.
6. Add the mountain to **`/header.html`** under its subject.
7. **VERIFY** (§7): 0 broken, fixes present, no raw `<>`, structure counts match.
8. Show Nir; on his OK, **commit + push** (commit style: `feat:` / `docs:`, no emojis in message).

---

## 9. Environment & repo facts

- OS: Windows. Shell: **PowerShell 5.1**. `rg`/ripgrep **NOT available** → use `Select-String`.
- Repo: `C:\Users\nir_s\peaktogether-website` (git). Remote:
  `https://github.com/strulovitz/peaktogether-website.git`.
- Commit message style in this repo: conventional prefixes `feat:` / `docs:` / `fix:` (no emojis).
- **Only commit/push when Nir asks.** Don't sweep unrelated files (e.g. `quake/savegame.json`)
  into website commits — stage specific paths.
- Known future cleanup: the existing **Riemann** pages have some garbled equations baked in from
  old PDF extraction — could be fixed the same Option-A way someday.

## 10. Working with Nir

- LOTS of emojis 😊🎉🏔️, warm, concise, step-by-step. Communicate before & after each step.
- Nir is the BOSS — ask before initiative; he doesn't read math, trusts me on it, but I still
  show the fixes. Everything in this project is **super important** to him. ❤️

---

### Mountains completed
- 🏔️ **Everest = Riemann Hypothesis** — `mathematics/Riemann_hypothesis/` (gold standard, fattened).
- 🏔️ **Annapurna I = Navier–Stokes Existence & Smoothness** — `mathematics/Navier-Stokes_existence_and_smoothness/`
  (skeleton: hub + 6 path pages, 13 base camps, 39 stepping stones, all sources; 7 LaTeX fixes applied).
