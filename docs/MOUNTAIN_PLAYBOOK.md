# 🏔️ MOUNTAIN PLAYBOOK — How to Build a Peak Together Mountain (EXACT recipe)

> ⭐ **DeepSeek: read this FIRST, top to bottom, every time Nir says "let's do a mountain."**
> This is the exact, battle-tested process (refined on **K2 = Turbulence** and **Annapurna I = Navier–Stokes**, July 2026).
> Follow it **the same way every time**. Author: DeepSeek V4 Pro in OpenCode. For: Nir (GitHub: strulovitz).
>
> 🔑 **The five things Nir cares about most (never forget):**
> 1. **ALL the text is HOLY / VERBATIM** — every word ChatGPT wrote, not just the math. Never paraphrase, add, drop, reorder, or "improve."
> 2. **The math must be beautiful, like LaTeX** (MathJax `$...$`). If a copy artifact broke an equation, fix it — **verify the correct form on the internet** — and tell Nir **at the end** (only if something was broken).
> 3. **NEVER break the top menu.** It took many hours to get working on all browsers + phone. Additive edits only.
> 4. **NEVER ruin the CSS.** One global `style.css`, single source of truth. No per-page style hacks.
> 5. **ASK Nir BEFORE any consequential / architectural / taste decision** — in plain chat text (NEVER the "quiz"/question tool). Don't ask about trivia; do ask before you might "fuck him." Declining one choice once ≠ never offer choices again.

---

## 0. What a "mountain" is + what Nir gives me

- Each famous problem is a **"mountain."** Nir assigns a **real-world mountain name** (metaphor) — I **NEVER invent it**.
- Nir also gives the **SUBJECT** = top-level folder: **mathematics / physics / chemistry / biology**.
- Nir pastes the **Deep Research text** (from a ChatGPT web chat).
- Nir may later give **two images**: a **scientist "sherpa guide"** portrait + the **real mountain** photo.

### The hierarchy (always mirror the doc's own structure)
```
🏔️ MOUNTAIN (hub = index.html)  →  intro + "Choose Your Path" grid of .path-card links
   └── 🧗 PATH (one index.html per path)  →  several Base Camps
          └── ⛺ BASE CAMP (a section on the path page)  →  stepping stones + annotated sources
                 └── 🪨 STEPPING STONE  →  a key result/concept
```
Completed so far:
- 🏔️ **Everest = Riemann Hypothesis** — `mathematics/Riemann_hypothesis/` (gold standard, "fattened" with sub-pages).
- 🏔️ **Annapurna I = Navier–Stokes** — `mathematics/Navier-Stokes_existence_and_smoothness/` (skeleton).
- 🏔️ **K2 = Turbulence** — `physics/K2_turbulence/` (skeleton; first Physics mountain).

**Default build = SKELETON:** one hub + one page per path; base camps are **sections** inside the path pages (no separate base-camp sub-pages unless Nir later gives per-path deep dives, RH-style).

---

## 1. THE SACRED RULES (never break)

1. **EVERYTHING is HOLY / VERBATIM** — prose AND math, word for word. The ONLY things I may touch:
   - HTML structure (wrapping text into the template);
   - wrapping math in `$...$` (only where ChatGPT already delimited it — don't add math markup where he wrote plain prose);
   - italicizing **book titles** with `<em>` (established site convention — see §3);
   - fixing **obvious broken LaTeX copy-artifacts** and **obvious garbled tokens/typos** (see §4), verified online, reported at the end.
2. **NOTHING LOST.** Every word ends up on the site. Unsure where a chunk goes? **ASK Nir.**
3. **Keep prose oddities verbatim** unless Nir says fix them (he usually does when I flag them — see §4).
4. **Don't reorganize** the doc. Follow its own Paths / Base Camps / Stepping Stones order.
5. **Only the MOUNTAIN goes in the menu** — not base camps. In-page cards handle the rest.
6. **"What to Upload Next" — INCLUDE it, split per path, verbatim.** (History: on K2 Nir first said drop it as "Google-AI meta filler," then reversed and said keep it, split into each path. Final rule = **KEEP + split per path**. See §3.)

---

## 2. The content pipeline (how Nir delivers text)

- ✅ **Best:** direct copy-paste from the ChatGPT web chat into our chat. Math arrives as real LaTeX (`$...$`).
- ❌ Avoid PDF / DOCX / Acrobat→HTML (they mangle equations).
- The paste often contains **meta to IGNORE**: old PDF filenames, the "COPY/PASTE PROMPT," ChatGPT's clarifying Q&A, "I'll let you know…" preamble, a trailing **Citations** URL list. **Drop those.**
- The blueprint is sometimes **pasted twice** → use ONE copy.
- ⚠️ **BUT "What to Upload Next" is NOT meta — we keep it** (split per path, verbatim). Only the truly-meta stuff above is dropped.

---

## 3. The exact page template

Reference the already-built pages when in doubt:
- Hub: `physics/K2_turbulence/index.html`
- Path: `physics/K2_turbulence/Path_1_Classical_Phenomenology_and_Scaling_Laws/index.html`

Every page = this shell:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>… — Peak Together</title>
    <link rel="stylesheet" href="/style.css?v=24">
</head>
<body>

    <div data-component="header"></div>

    <main class="page">
        … content …
        <a href="…" class="back-link">← Back to …</a>
    </main>

    <div data-component="footer"></div>

    <script src="/components.js?v=3"></script>
</body>
</html>
```
- `header.html` + `footer.html` are injected by `/components.js`. **MathJax** auto-loads via `components.js` (inline `$...$`, display `$$...$$` / `\[...\]`).
- Useful classes: `.page`, `.subtitle`, `.path-grid`, `.path-card`, `.back-link`, `.gp-gallery`, `.gp-gallery.two`.

### Hub page
- `<h1>🏔️ <Mountain>: <Problem Name></h1>` (e.g. `🏔️ K2: Turbulence`).
- `<p class="subtitle">…</p>` — **site chrome (my words, not the research).** Mirror the tone; end with "Together, we climb." Keep any lone `$` (like `$1,000,000`) the ONLY `$` in that element so MathJax doesn't mis-parse.
- (Optional) the **image gallery** right after the subtitle — see §8.
- A short 2-paragraph intro (site chrome), then `<h2>Choose Your Path</h2>` + `.path-grid` of one `.path-card` per path (`<h3>` title + `<p>` one-line blurb, blurbs = site chrome).
- Back-link → `/` ("← Back to Home").

### Path page
- `<h1>` = the path's title, **verbatim** (e.g. `Path 1: Classical Phenomenology and Scaling Laws`).
- Per Base Camp (K2 format, faithful to the doc):
  ```html
  <h2>Base Camp X.Y: Title</h2>
  <p><strong>Stepping Stones:</strong> … verbatim semicolon list …</p>
  <ul>
      <li>Author, <em>Book Title</em> – verbatim description … (level).</li>
      <li>Author (year), "Paper Title in quotes" – verbatim description … (level).</li>
  </ul>
  ```
  Rule for `<em>`: **un-quoted work titles = books → italicize**; **quoted paper titles → keep the quotes, no italics**; authors verbatim.
- The doc's **parenthetical path summary** at the end of each path → keep as a `<p>…</p>`, verbatim (it's real content, not meta).
- **"What to Upload Next" — this path's slice**, at the very end before the back-link:
  ```html
  <h2>What to Upload Next</h2>
  <p>To continue our deep exploration, it's recommended to gather key original sources and textbooks for each base camp. Below is a prioritized list of PDFs (5–6 each) grouped by base camp:</p>
  <h3>Base Camp X.Y (label)</h3>
  <ul>
      <li>… one PDF entry …</li>   <!-- split the semicolon list; one <li> per entry; italicize book titles -->
  </ul>
  ```
  The global intro sentence is repeated on each path page (that's fine — like the NS pages repeat an intro line).
- Back-link → the hub (e.g. `← Back to K2 – Turbulence`).

> ⚠️ Hub uses `.path-card` (no `<li>`); path pages use `<ul>/<li>` (no path-cards).

---

## 4. Fixing broken math + verifying with the internet

ChatGPT's web copy silently **drops `\`, `_`, `*`** and sometimes hallucinates garbled tokens. Nir's rule (locked on K2):
- **Transcribe verbatim first.** Then **fix broken equations myself**, **verify the correct form on the internet** when there's any doubt, and **report every fix at the END — only if something was broken.** (Do NOT stop to pre-approve each fix; just fix + report.)
- Also fix **obvious prose typos / garbled tokens** the same way (Nir asked me to on K2), and list them at the end.

Real examples from K2 (do it exactly like this):
- LaTeX: `$\sim!20$` → `$\sim\!20$` (dropped `\`; `\!` is a thin negative space → renders "∼20").
- Garbled token: `WALETIME` → `WMLES` (Wall-Modeled LES) — I searched the web, confirmed "WALETIME" isn't a real term, chose the standard near-wall hybrid method that fit the sentence, and **flagged it as my best-judgment reconstruction** for Nir to confirm.
- Typos: `layer-and-scade` → `layer-and-cascade`; `Peclét`/`Peclet` → **`Péclet`** (correct spelling, é on the first e).
- Generic patterns to watch: `T^$`→`T^*$`, `|\omega|{\infty}`→`|\omega|_{\infty}`, `\int_0^T!`→`\int_0^T\!`, `,ds`→`\,ds`, `F!\Big(`→`F\!\Big(`.
- Unicode Greek inside `$…$` (e.g. `$β$`, `$k$–$ε$`, `$C_μ$`) **renders fine in MathJax — leave it verbatim, it is NOT broken.**

After fixing: **verify 0 broken patterns remain** (see §9).

---

## 5. 🔴 CRITICAL — HTML-escape math & prose

The browser parses HTML before MathJax runs, so a raw `<` (e.g. `t<T`) breaks the page. In ALL content (prose AND inside `$...$`):
- `&` → `&amp;`  (⚠️ this bites CONSTANTLY — every author "A & B" and every "X & Y" in titles/labels)
- `<` → `&lt;`   (e.g. `p&lt;\infty`, `2/p+3/q&lt;1`)
- `>` → `&gt;`   (e.g. `T&gt;0`)

MathJax decodes entities back before typesetting, so escaping is safe and required. Also:
- Keep an **unpaired `$`** (like `$1,000,000`) as the only `$` in its element.
- Preserve **UTF-8 literally**: `Šverák`, `Péclet`, `Bénard`, `Cvitanović`, Greek `θ β ε ω μ`, en-dashes `–`, em-dashes `—`, curly quotes `" " ' '`, `×`, `∼`, `…`.

---

## 6. THE TOP MENU — handle VERY carefully, break NOTHING

**How it works (understand before touching):**
- The menu lives **ONCE** in `/header.html`. Every page just has `<div data-component="header"></div>`; `components.js` fetches `header.html` and injects it. So I edit **one file** and the whole site updates.
- It's a **3-level dropdown**:
  - **Level 1** (top bar): Home · The Arcade · **The Mountains** · How It Works · About · Play/GitHub buttons
  - **Level 2** (inside "The Mountains"): **Mathematics · Physics · Chemistry · Biology** — these are `<li class="has-submenu"><span class="submenu-toggle">Subject</span><ul class="submenu">…</ul></li>`
  - **Level 3** (inside each subject): the mountain links, `<li><a href="/…/">Name</a></li>`
- **Desktop** = pure CSS `:hover` with invisible "bridge" `::after` zones (in `style.css`). **Mobile (≤900px)** = hamburger toggles `.nav-open`; tapping a `.submenu-toggle` toggles `.submenu-open` (accordion in `components.js`). **DO NOT touch `style.css` menu rules or `components.js`.**

**To add a mountain (the ONLY change I make — purely additive):**
- A **subject's FIRST mountain** currently shows a placeholder:
  ```html
  <ul class="submenu">
      <li><span class="submenu-coming">Coming soon</span></li>
  </ul>
  ```
  Replace **only that `<li>`** with the real link:
  ```html
  <ul class="submenu">
      <li><a href="/<subject>/<folder>/">Mountain Display Name</a></li>
  </ul>
  ```
- A subject's **later mountains**: just add another `<li><a …></li>` next to the existing ones (like Mathematics holds both Riemann + Navier–Stokes).
- **Subjects are permanent** — never remove/rename Physics/Chemistry/Biology; each will hold MANY mountains.
- To keep the edit unique/safe: include the subject's `<span class="submenu-toggle">Subject</span>` line in the match so I only touch the right subject (Physics/Chemistry/Biology all have identical "Coming soon").
- After editing: verify exactly the intended change (see §9). **Never** edit the CSS or JS for a menu change.

---

## 7. THE CSS — ONE global file, single source of truth

**How the whole site is styled (Nir explained this explicitly, July 2026):**
- **ONE shared stylesheet: `/style.css`.** Every page links `<link href="/style.css?v=24">`. **ALL** visual styling (colors, menu, buttons, galleries, everything) lives there as reusable classes. **Pages never carry their own styling.**
- `?v=24` is a **cache tag**. When `style.css` changes, either (a) bump the number everywhere so browsers auto-refetch, or (b) accept that a **Ctrl+F5** shows it. Nir is fine with Ctrl+F5 for himself; he just wants everything centralized in the ONE file.
- **NEVER** add a per-page `<style>` block or inline layout hack. (I did this once on K2 to "avoid Ctrl+F5" and Nir was furious — it fragments the codebase. Do it the site's way: global `style.css`.)
- **ASK before any CSS architecture decision** (inline vs global, version bump, new class). It's consequential.
- Adding a **new reusable class** to `style.css` (like `.gp-gallery.two`) is the correct, safe way — put it right beside its siblings (`.four`, `.three`).

---

## 8. IMAGES & the hero gallery (scientist + real mountain)

Nir gives two images per mountain: a **scientist "sherpa guide"** and the **real mountain**. They go in a **two-up gallery** at the top of the hub (right after the subtitle).

### 8a. Move + name the files
- **MOVE (not copy)** the files from `C:\Users\nir_s\Downloads` into `C:\Users\nir_s\peaktogether-website\images\`. (Nir said MOVE — verify the byte size matches, then the original leaves Downloads. `Move-Item` does this in one step.)
- Rename to lowercase **kebab-case**, consistent pattern:
  - scientist → `<mountain>-<topic>-<person>-sherpa-guide.png`
    e.g. `k2-turbulence-kolmogorov-sherpa-guide.png`, `annapurna-navier-stokes-ladyzhenskaya-sherpa-guide.png`
  - mountain → `<mountain>-<topic>-real-mountain.png`
    e.g. `k2-turbulence-real-mountain.png`, `annapurna-navier-stokes-real-mountain.png`
- Watch for **spaces / mixed case** in Nir's original filenames (e.g. `k2-turbulence- real-mountain.PNG`) — normalize them.

### 8b. Check dimensions FIRST
Get pixel sizes (PowerShell + System.Drawing). So far Nir's images have been:
- scientist portrait = **square, 1024×1024 (1:1)**
- real mountain = **4:3, 960×720 (W/H ≈ 1.333)**
The global `.gp-gallery.two` rule is **tuned for exactly this pair of shapes**. If a future pair has **different** aspect ratios, the equal-height math breaks — **update the `nth-child` flex values** so `flex-grow = width/height` of each image (see 8d), or the heights won't match.

### 8c. The markup (scientist FIRST = left on wide / top on narrow)
Right after `<p class="subtitle">…</p>` on the hub:
```html
<div class="gp-gallery two">
    <img src="/images/<…>-sherpa-guide.png" alt="<Scientist> — the sherpa guide for <Mountain> – <Topic>">
    <img src="/images/<…>-real-mountain.png" alt="<Mountain> — the real mountain">
</div>
```
DOM order controls layout: **child 1 = left (wide) / top (narrow)** = the **scientist**; **child 2 = right / bottom** = the **mountain**.

### 8d. The CSS (already in global `style.css`, beside `.four`/`.three`)
```css
/* Two images shown in full at the SAME height; each image's width follows its own
   aspect ratio (child 1 = square 1:1, child 2 = landscape 4:3), so nothing is cropped. */
.gp-gallery.two { display: flex; align-items: flex-start; }
.gp-gallery.two img { width: auto; min-width: 0; }
.gp-gallery.two img:nth-child(1) { flex: 1 1 0; }      /* square portrait → flex-grow = 1.0  */
.gp-gallery.two img:nth-child(2) { flex: 1.333 1 0; }  /* 4:3 mountain    → flex-grow = 1.333 */
```
and inside `@media (max-width: 768px) { … }`:
```css
.gp-gallery.two { flex-direction: column; }
.gp-gallery.two img { width: 100%; flex: none; }
```
**Why it works:** each image's `flex-grow` = its width/height ratio, so flex gives each a width proportional to its aspect ratio → **both render at the exact same height, side by side, nothing cropped.** On ≤768px they stack full-width (scientist on top). This is what "correct the height of the scientist" means: the square portrait no longer looks taller than the 4:3 mountain.
- If Nir ever wants **edge-to-edge with a small crop** instead of height-matched-no-crop, switch to `aspect-ratio: 4/3; object-fit: cover;` — but **ASK first** (cropping his image is consequential).

### 8e. The lightbox (click to enlarge — same as the game pages)
The base `.gp-gallery` + `.gp-gallery img` styling and ALL `.lightbox-*` / `.zoomable` CSS already live in `style.css`. Add this **exact script** just before `</body>` on the hub (it targets `.gp-gallery img`):
```html
<script>
(function () {
    'use strict';
    function initLightbox() {
        var imgs = document.querySelectorAll('.gp-gallery img');
        if (!imgs.length) return;
        var overlay = document.createElement('div');
        overlay.className = 'lightbox-overlay';
        overlay.setAttribute('role', 'dialog');
        overlay.setAttribute('aria-modal', 'true');
        var big = document.createElement('img');
        big.className = 'lightbox-img'; big.alt = '';
        var closeBtn = document.createElement('button');
        closeBtn.className = 'lightbox-close';
        closeBtn.setAttribute('aria-label', 'Close');
        closeBtn.innerHTML = '&times;';
        overlay.appendChild(big); overlay.appendChild(closeBtn);
        document.body.appendChild(overlay);
        function openBox(src, alt){ big.setAttribute('src', src); big.setAttribute('alt', alt||''); overlay.classList.add('open'); document.body.classList.add('lightbox-locked'); }
        function closeBox(){ overlay.classList.remove('open'); document.body.classList.remove('lightbox-locked'); big.setAttribute('src',''); }
        for (var i=0;i<imgs.length;i++){ imgs[i].classList.add('zoomable'); imgs[i].addEventListener('click', function(){ openBox(this.getAttribute('src'), this.getAttribute('alt')); }); }
        overlay.addEventListener('click', function(e){ if (e.target===overlay || e.target===closeBtn) closeBox(); });
        closeBtn.addEventListener('click', closeBox);
        document.addEventListener('keydown', function(e){ if (e.key==='Escape'||e.keyCode===27) closeBox(); });
    }
    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', initLightbox); } else { initLightbox(); }
})();
</script>
```
(I can't view images myself — write a thematic `alt` from the filename/topic and tell Nir he can refine it.)

---

## 9. Verification (Windows / PowerShell 5.1 — `rg` is NOT installed → use `Select-String`)

Run after building; confirm:
1. **All `index.html` exist** (hub + one per path). Count = paths + 1.
2. **Broken LaTeX = 0**, each intended fix present (loop the §4 patterns; e.g. `\sim!20` → 0, `\sim\!20` → present).
3. **No unescaped `&`**: search `' & '` → **0**; and `'&amp;amp;'` (double-escape) → **0**.
4. **No raw math `<`/`>`** (search `t<T`, `p<\infty`, `T>0`, …) → 0.
5. **Structure counts** per path page: `<h2>` = base camps + 1 ("What to Upload Next"); `<li>` = (annotated sources) + (What-to-Upload PDFs). Hub `.path-card` = number of paths.
6. **Menu:** `header.html` still has the right number of "Coming soon" (only the subjects with no mountain yet) + exactly 1 new mountain link; Mathematics/other subjects untouched.
7. **Images:** files present in `images/`; `.gp-gallery two` block present; scientist listed **first**; lightbox `initLightbox` present.

---

## 10. Commit, push, and deploy

- **ALWAYS commit + push after each completed change** (Nir's standing instruction — don't ask each time). Stage **specific paths** only; never sweep unrelated files (e.g. `quake/savegame.json`).
- Commit message style: conventional prefixes `feat:` / `docs:` / `fix:` / `style:` / `refactor:` — **no emojis** in the message.
- Give Nir the GitHub **blob (view)** links when useful.
- 🚚 **Deploy is MANUAL via FileZilla to peaktogether.me** (GitHub ≠ the live site). After pushing, **remind Nir exactly which files to upload** — and **DO NOT FORGET THE IMAGES.** (On Annapurna the HTML was live but the two images 404'd because they hadn't been uploaded — the page showed broken images. I can verify live files with a quick `Invoke-WebRequest -Method Head` on the image URLs → 200 = live, 404 = not uploaded yet.)

---

## 11. Working with Nir (behavioral rules — as important as the code)

- 😊 **LOTS of emojis, warm, concise, step-by-step.** Communicate before & after each step. Nir is the BOSS.
- 🙋 **ASK before consequential decisions**, in **plain chat text**. NEVER use the "quiz"/question tool — Nir hates it ("stop this quiz shit, ask me normally"). Ask BEFORE you might "fuck him," not after.
- 🚫 Don't ask about trivia; don't stall; don't over-ask. But architecture/taste/anything-that-could-break/anything-irreversible → ASK first with a clear recommendation.
- ✍️ **Facts only from me; taste/design/aesthetics → Nir.** Never invent words Nir didn't say; never put words in his mouth.
- 🧮 Nir doesn't read math and **trusts me** on it — but I still **show him every fix** at the end.
- ❤️ Everything here is **super important** to him. Don't ruin his day; don't make him repeat himself; do the FULL job.

---

## 12. Environment & repo facts

- OS: Windows. Shell: **PowerShell 5.1**. `rg`/ripgrep NOT available → `Select-String`. Conda hangs → use base `python`.
- Repo: `C:\Users\nir_s\peaktogether-website` (git). Remote: `https://github.com/strulovitz/peaktogether-website.git` (`github.com/strulovitz`).
- Images live in `/images/` (kebab-case). Shared components: `/header.html`, `/footer.html`, injected by `/components.js`. Global styles: `/style.css`.

---

## 13. End-to-end checklist (do these in order, every mountain)

1. Nir gives **mountain name + subject + pasted Deep Research text** (+ maybe 2 images).
2. Read the doc; map Paths → Base Camps → Stepping Stones → sources. Drop only the true meta (§2); **keep "What to Upload Next"** (split per path).
3. Transcribe **verbatim**, HTML-escape (`&`,`<`,`>`), wrap math in `$…$`, italicize book titles. Fix broken math/typos (verify online).
4. Build **hub** (`physics|mathematics|…/<Folder>/index.html`) + **one page per path** (`Path_N_<Short_Name>/index.html`).
5. If images given: **move + rename**, check dimensions, add the **`.gp-gallery two`** block (scientist first) + **lightbox script** to the hub. (Reuse the global CSS; only touch CSS if aspect ratios differ — and ASK if cropping.)
6. Add the mountain to **`/header.html`** (replace the subject's "Coming soon" for its first mountain, or add a sibling `<li>`). Touch nothing else in the menu.
7. **VERIFY** (§9): 0 broken math, 0 unescaped `&`, structure counts, menu intact, images wired.
8. **Report to Nir** the LaTeX/prose fixes (only if any were broken).
9. **Commit + push.** Then **remind Nir to FileZilla-upload** the changed HTML **+ the new images** (don't forget images!).
