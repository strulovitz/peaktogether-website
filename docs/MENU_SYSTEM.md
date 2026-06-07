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
