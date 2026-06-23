# Menu System — How It Works (and Why)

This document explains the proven, cross-browser menu system used on this site.
**Do not change the approach without re-reading this.** The techniques below were
arrived at after multiple failed attempts with `visibility` tricks, JS timers,
and `transform`-based animations — all of which broke in Firefox.

---

## Desktop Dropdown (CSS-only `:hover`)

### The Problem
When you hover "Mathematics" and move the mouse down toward the dropdown,
the dropdown disappears before you can click anything. This happens in Firefox
because even a **1px gap** between the trigger element and the dropdown causes
the browser to fire `:hover` off before `:hover` on the dropdown kicks in.

### The Solution: `::after` Bridge

```css
/* The li itself has position: relative */
.nav-list > li {
    position: relative;
}

/* Bridge: an invisible pseudo-element that extends the li's
   hover area 16px downward — the mouse never "leaves" the li */
.nav-list > li.has-submenu::after {
    content: '';
    position: absolute;
    top: 100%;      /* starts at bottom of li content */
    left: 0;
    right: 0;
    height: 16px;   /* extends 16px below */
    z-index: 997;
    /* NO background = invisible but still hit-testable */
}

/* Submenu sits RIGHT BELOW the bridge — zero gap */
.submenu {
    display: none;
    position: absolute;
    top: calc(100% + 16px);  /* li bottom + bridge height */
    left: 50%;
    transform: translateX(-50%);  /* center it */
    ...
}

/* Pure CSS hover — shows dropdown when hovering li or bridge */
.has-submenu:hover > .submenu {
    display: block;
}
```

### Why This Works in Every Browser
1. The bridge is a **child** of the `li`, so hovering it = hovering the `li`
2. `display: block` is immediate — no transitions, no timing issues
3. Zero gap between bridge bottom and submenu top — seamless transition
4. No JavaScript — no event timing bugs across browsers
5. Works in Firefox, Chrome, Edge, Safari — all of them

### Key: `position: relative` on the `li`
Without this, `position: absolute` on the bridge would be relative to
a different ancestor, breaking the layout. Every `nav-list > li` must
have `position: relative`.

### Key: Bridge hidden on mobile
On mobile, the bridge is hidden with `display: none` because the mobile
menu uses click-based accordion, not hover.

---

## Mobile Menu (Click-based, `right` sliding)

### The Problem
Using `transform: translateX(100%)` to hide the slide-out menu causes
rendering bugs in Firefox on Android/iOS — text appears shifted left
and cut off, making menu items unreadable.

### Why `transform` Fails on Firefox Mobile
Firefox creates a new stacking context for `transform`-ed `position: fixed`
elements. This interacts badly with mobile viewport resizing (address bar
show/hide) and causes incorrect hit-testing and text rendering.

### The Solution: `right` + `visibility`

```css
.main-nav {
    position: fixed;
    top: 0;
    bottom: 0;
    right: -320px;          /* hidden off-screen to the right */
    width: 300px;
    max-width: 85vw;        /* fits narrow screens */
    visibility: hidden;     /* hidden from accessibility */
    transition: right 0.3s ease, visibility 0s 0.3s;
    /*                                                         ^^^^^^
        visibility delay = 0.3s on close (wait for slide-out) */
}

.main-nav.nav-open {
    right: 0;
    visibility: visible;
    transition: right 0.3s ease, visibility 0s 0s;
    /*                                                  ^^
        visibility delay = 0s on open (instant) */
}
```

### Why This Works
1. `right` animation is well-supported in all browsers, including Firefox
2. `visibility` transition delay prevents flash of content when closing
3. No `transform` means no Firefox stacking-context bugs
4. `max-width: 85vw` ensures menu fits on any screen size
5. `overflow-x: hidden` prevents text from bleeding outside the panel

### JavaScript: Click Toggle

```javascript
// Hamburger opens/closes the mobile menu
hamburger.addEventListener('click', function () {
    nav.classList.toggle('nav-open');
    body.classList.toggle('menu-open');
});

// "Mathematics" toggle expands/collapses the submenu (mobile only)
submenuToggle.addEventListener('click', function (e) {
    e.preventDefault();
    parent.classList.toggle('submenu-open');
});
```

---

## Architecture: Reusable Header/Footer

The site uses a component system so header and footer are stored in
separate files and loaded on every page:

```
header.html       ← The <header> with logo, hamburger, nav
footer.html       ← The <footer> with brand, links, social
components.js     ← Fetches and injects header/footer into pages
```

Each page includes:
```html
<div data-component="header"></div>

<!-- page content -->

<div data-component="footer"></div>
<script src="components.js"></script>
```

**Change header/footer once → updates every page.** No build step needed.

---

## Directory URLs (DreamHost)

Every folder contains an `index.html` so `/mathematics/Riemann_hypothesis/`
works without typing the filename.

`.htaccess` provides:
- `DirectoryIndex index.html` — default file for directories
- Redirect `/folder` → `/folder/` (adds trailing slash)
- Caching headers for images (30 days) and CSS/JS (7 days)

---

## Lessons Learned (Don't Repeat These)

| What was tried | Why it failed |
|---------------|---------------|
| `display: none` → `display: block` with gap | Gap breaks `:hover` chain in Firefox |
| `visibility: hidden` + `opacity` + transition delay | Firefox doesn't `:hover` hidden elements; timing still breaks |
| JS `setTimeout` 300ms unhover delay | Race conditions between `mouseleave` and `mouseenter` in Firefox |
| `transform: translateX()` for mobile slide | Firefox mobile rendering bugs — text shifts, gets cut |
| `pointer-events: none` on hidden submenu | Blocks `mouseenter` detection, creating dead zone |
| Animating `right: -320px` without `visibility` | Menu flashes visible at wrong position during page load |

**The winning formula is the simplest one:**
- Desktop: CSS `:hover` + `::after` bridge (zero gap) + `display: block`
- Mobile: `right` slide + `visibility` toggle + JS click handlers

---

## Math Rendering (MathJax 3)

All mathematical expressions written in LaTeX (`$...$` for inline, `$$...$$` for display)
are rendered as proper math notation on every page via MathJax 3.

### How it works

`components.js` loads MathJax automatically on every page:

```javascript
// 1. Set config BEFORE the MathJax script loads (critical!)
window.MathJax = {
    tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']]
    },
    options: {
        skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
    }
};

// 2. Load MathJax from CDN
var script = document.createElement('script');
script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js';
script.async = true;
document.head.appendChild(script);

// 3. Re-typeset after header/footer components load dynamically
MathJax.typesetPromise();
```

### Critical rules

1. **`window.MathJax` MUST be set BEFORE the MathJax script loads.**  
   Do NOT inject the config as a separate `<script>` tag — set the global directly.

2. **Call `typesetPromise()` after dynamic content loads.**  
   Header/footer are loaded via `fetch`, so re-typeset in their callbacks.

3. **Use `tex-chtml.js` component** — includes AMSmath (supports `\tfrac`, `\frac`, etc.).

4. **Math renders as HTML/CSS** (not images) — scales perfectly on mobile.

5. **Cache-busting**: `components.js` is referenced as `components.js?v=3` on all pages.
   When making changes to `components.js`, bump the version number in every HTML file.

### Lessons learned

| What was tried | Why it failed |
|---------------|---------------|
| Config as injected `<script>` text | Escape issues with backslashes; config not guaranteed to load before MathJax |
| Not re-typesetting after dynamic content | Math in header/footer not rendered |
| No cache busting | Browser served old `components.js` without MathJax code |

**The winning formula:** Set `window.MathJax` directly as a JS object, then append the CDN script, then re-typeset after dynamic content loads.

---

## PLANNED NAVIGATION REDESIGN (decided June 23, 2026 — NOT YET BUILT)

Peak Together is now a multi-game arcade. The navigation is being redesigned to
match. This section is the agreed design; the implementation will follow later
(do NOT break the proven mechanics above when building it).

### New top bar (left to right)

```
Home  ·  The Arcade  ·  The Mountains ▾  ·  How It Works  ·  About      [ ▶ Play Free ]  [ GitHub ]
```

### What each item is

| Item | Type | Target |
|------|------|--------|
| **Home** | leaf link | existing home page (`/`) |
| **The Arcade** | leaf link | NEW page `/arcade/` (filterable games grid) |
| **The Mountains** | dropdown ONLY — **not a page** | see nesting below |
| **How It Works** | leaf link | NEW page `/how-it-works/` |
| **About** | leaf link | existing `/about/` |
| **▶ Play Free** | CTA button → leaf link | NEW page (e.g. `/play/`) |
| **GitHub** | CTA button → external link | `https://github.com/strulovitz/peaktogether-website` |

### The Mountains — THREE menu levels (this is new vs. the 2-level menu today)

- **Level 1 — The Mountains**: dropdown only, NOT a page. Contains sub-menus:
  - **Level 2 — Mathematics**: sub-dropdown, NOT a page. Contains leaf links:
    - **Level 3 — Riemann Hypothesis**: LEAF LINK → `https://www.peaktogether.me/mathematics/Riemann_hypothesis/`. **No further sub-menus** — this is the deepest level, and the deepest level is where the real page links live.
    - (more Mathematics topics added here later)
  - **Physics** (Level 2 sub-dropdown — leaf links added later)
  - **Chemistry** (Level 2 sub-dropdown — leaf links added later)
  - **Biology** (Level 2 sub-dropdown — leaf links added later)
  - (more subjects added later)

### Key design rules (decided by Nir)

1. **The Mountains is NOT a page.** It only opens a dropdown.
2. **Mathematics / Physics / Chemistry / Biology are NOT pages.** Each is a sub-dropdown.
3. **Only the deepest level links to real pages** (e.g. Riemann Hypothesis → its page). The deepest leaf level has NO further sub-menus.
4. The current "Mathematics → Riemann Hypothesis → 9 paths" menu nesting goes away. Riemann Hypothesis becomes a single leaf link; its 9 paths live ON the Riemann Hypothesis page, not in the menu.
5. The three grey top-bar items today (Physics/Chemistry/Biology "(soon)") move under The Mountains as Level-2 sub-dropdowns.

### Technical notes for implementation (later)

- This needs a **third nesting level** the current CSS does not have yet (today it is
  top-level `.has-submenu` → one `.submenu`). Adding Level 3 must reuse — never replace —
  the proven patterns: `::after` hover bridge on desktop, `right` + `visibility` slide on
  mobile (NEVER `transform`), `<span class="submenu-toggle">` accordions on mobile, every
  `<a>` closes the drawer, `data-component` injection, and the `components.js?v=N`
  cache-buster bump.
- The two CTA buttons (Play Free, GitHub) are the only genuinely new header elements;
  their desktop placement (right end of header) and mobile placement (inside the drawer)
  must not disturb the flex header or the drawer.
