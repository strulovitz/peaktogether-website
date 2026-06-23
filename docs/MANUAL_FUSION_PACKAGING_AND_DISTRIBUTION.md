# MANUAL FUSION — Packaging & Distribution (Claude Opus 4.8, final combined answer)

> This is the **manual fusion**. Nir gave the same question (`docs/FUSION_PROMPT_PACKAGING_AND_DISTRIBUTION.md`)
> to several AI models in separate OpenRouter chats — **GPT-5.5** and **Google Gemini 3.1 Pro Preview** — and
> then handed both answers to **Claude Opus 4.8**, who acted as the judge + integrator and produced this final
> combined answer below.
>
> Saved **VERBATIM, word-for-word, as-is** at Nir's request. (Code blocks have been fenced for readability;
> the words and code are unchanged.)

---

Perfect — I now have both answers (GPT-5.5 and Gemini 3.1 Pro Preview). I have everything I need, so let me do the fusion right here. No need to ask me in another chat — I'm the integrator, and I've read both carefully.

Before the answer itself, one quick note on what I'm actually doing, because it matters for your trust in the result: the two models agree on the big architecture (PyInstaller one-folder → zip → download), which is reassuring — that's almost certainly the right path. But they disagree on hosting (GPT says itch.io primary, Gemini says GitHub Releases primary), and more importantly, both of them have at least one bug or risky instruction in their code/commands that would actually bite you or DeepSeek. A naive "average" would inherit those bugs. So my job here is to keep what's right, fix what's wrong, and give you one clean, correct plan. I'll flag the corrections honestly as I go.

Here's the fusion.

## Peak Together — The Complete Plan to Let Anyone Install & Play Your Games (No Terminal, No Python)

Hi Nir. Good news first: both expert models and I agree on the core answer, which means you can act on it with confidence. The disagreements are at the edges (where to host, a few code details), and I'll settle those for you. I'll also fix two genuine bugs in their instructions that would have wasted DeepSeek's time or produced a broken build.

The one-sentence version:

> Ship each game as a portable Windows folder built with PyInstaller in "one-folder" mode, zipped, hosted on BOTH itch.io (friendly front door) and GitHub Releases (reliable mirror + dev source), linked from a beautiful download page on peaktogether.me. Never make players install Python. Never use one-file mode. Never use an installer (yet). Each game is its own isolated folder that shares nothing with the others.

## Question 1 — How should a non-technical user install and run the game?

Both models independently reached the same conclusion, and they're right. Here are the real alternatives:

- Tell users to install Python + pip install + python app.py — this is your current state. It is the single biggest threat to your traffic, exactly as your critique said. Last place. Keep it only for the GitHub/developer crowd.
- PyInstaller one-file .exe (a single file) — looks elegant, but it secretly unzips itself to a temp folder on every launch, which means slow startup, higher antivirus false-positive rate, and more fragility with OpenGL + assets. Both models warned against this, and they're correct. Avoid.
- Traditional installer (Inno Setup / NSIS) — feels "official," but adds friction (clicking Next five times), can write to the registry, and contradicts your "we won't touch your computer" promise. Good maybe-later, not now.
- PyInstaller one-folder portable .zip — a self-contained folder with the .exe + a private Python + all DLLs + your assets. User unzips, double-clicks, plays. No Python, no terminal, no admin, no system changes. To uninstall, they delete the folder. This is the winner, unanimously.

My recommendation: PyInstaller one-folder mode, shipped as a .zip. It's the only option that fully honors all your constraints at once (no Python, no terminal, no system risk, games don't collide, free).

The player-facing flow you want is exactly four steps, and you should print these inside the zip and on the website:

1. Download the Windows zip.
2. Right-click it → "Extract All…"
3. Open the extracted folder.
4. Double-click "Descent QED.exe".

No Python needed. No terminal. No install. To uninstall, just delete the folder.

That last sentence is worth a lot — say it everywhere.

## Question 2 — Is "try instantly in the browser" realistic for this game?

Both models say no, and they are correct — but let me make sure you understand why, because it determines what your future games can do.

Your game renders with PyOpenGL using legacy fixed-function OpenGL (glBegin/glEnd, display lists). The browser's graphics layer is WebGL, which is shader-based only and physically cannot run fixed-function calls. Tools like pygbag can put simple 2D Pygame games in the browser beautifully — but a Pygame window driving legacy PyOpenGL is exactly the case pygbag struggles with. Forcing it would be a multi-week rewrite of your renderer, and it would block your launch for no good reason.

So, the honest verdict:

- Now: Don't try to make Descent QED playable in-browser. Instead, put a high-quality, autoplaying, looping ~10-second MP4/GIF of the Basel-problem level at the top of your page. Make it so visually alive that people want the download. This gives you 90% of the "try it instantly" conversion benefit with 1% of the effort.
- Cheap experiment, later: Time-box one afternoon to throw the game at pygbag just to see. If it works, great surprise. If not (likely), you lost an afternoon, not a launch.
- Future games: If a game is pure 2D Pygame with no PyOpenGL, design it for pygbag from day one and you can offer real instant browser play for those. Use OpenGL only when a game truly needs 3D, and accept that those are download-only.

Recommendation: Trailer/looping video now; download is the real "play" button; revisit browser only for future 2D-only games.

## Question 3 — Where to host the free download? (The models disagreed — I'll settle it)

This is the one real conflict. GPT said itch.io primary; Gemini said GitHub Releases primary. Both made good points, and both made one wrong claim:

- GPT was slightly too negative on GitHub Releases (it's not just a "decent" host — its CDN is excellent and bandwidth is effectively free).
- Gemini was slightly too negative on itch.io ("takes the user away from your cozy ecosystem") — in reality, itch.io is where your 15–25 audience already expects to find indie games, and it raises trust, not lowers it.

Here's the honest landscape:

- Dreamhost VPS (FileZilla static): Fine for the website, images, CSS, the trailer video. Bad as the primary host for large .zip downloads — VPS bandwidth isn't built for a viral spike, manual FileZilla re-uploads are clunky, and there's no versioning. Use for the site, not the game binaries.
- GitHub Releases: Free, backed by a massive CDN, effectively unlimited bandwidth, built-in versioning, perfect for open-source, and you can hotlink the .zip straight into a button on your site. Slightly "techy" feel if a user lands on the raw page, but if they click your website button they barely notice. Excellent.
- itch.io: The cozy, friendly, indie-native front door your exact audience already trusts. Free, great CDN, screenshots/trailer/devlog built in, "free / pay-what-you-want" supported. Excellent, and best for first-time non-technical players.
- Google Drive / Dropbox / OneDrive: Avoid. Looks amateur, quota/link breakage, inconsistent download warnings.
- Internet Archive: Fine as a long-term archival mirror later; not a front door.

My ruling (better than either model alone): do BOTH, with clear roles.

- itch.io = the primary "Play on Windows" destination for normal players (warm, trusted, indie-native).
- GitHub Releases = the mirror + the canonical versioned source (great CDN, perfect for the dev crowd, and a reliable backup link).
- peaktogether.me on Dreamhost = the official home with the trailer and the buttons. Your main button → itch.io; a smaller "Mirror (GitHub)" link → the GitHub release.

This costs you nothing extra (you upload the same zip to both) and removes the single-point-of-failure that either model's solo choice would have created.

## Question 4 — How to guarantee we never harm the user's system or collide between our games

This is the part that protects your brand, and PyInstaller one-folder already solves it almost entirely, because the bundled game carries its own private Python and its own copy of pygame/PyOpenGL/numpy inside the folder. The player's machine never gets Python, never runs pip, never gets global packages, never needs admin, and nothing is shared between games. Game #2 is just another independent folder.

The one thing to get right (both models touched it, GPT specified it well): where the game writes save files, settings, and crash logs. A packaged game should not write next to its .exe (that folder may be read-only depending on where the user extracted it). It should write to a per-game folder under the user's AppData:

```
%LOCALAPPDATA%\PeakTogether\DescentQED\
```

That's normal, safe Windows behavior, and it keeps each game's data cleanly separated.

Rules to enforce across all games: no global pip install for players, no writing to C:\Python312\, no shared "PeakTogetherPython" environment, no registry writes, no PATH changes, no admin prompts, no drivers. Each game self-contained; per-game AppData folder; uninstall = delete folder.

## Question 5 — The scary "Unknown Publisher" / SmartScreen warning

Both models agree it's a real problem, and both are right. Because your .exe isn't code-signed, Windows SmartScreen may show "Windows protected your PC / Unknown publisher." You cannot fully eliminate this for free (an EV code-signing cert is ~$300+/year and is overkill for you right now). PyInstaller apps also occasionally trip antivirus heuristics.

What you can do for free, all of which I'm baking into the plan:

- Use one-folder mode, not one-file (lower false-positive rate). ✅
- Do NOT use UPX compression (upx=False) — UPX-packed exes look more suspicious to antivirus. ✅
- Never request admin rights. ✅
- Host only from trusted places (itch.io, GitHub, your site). ✅
- Publish a SHA-256 checksum next to each download (technical users verify; everyone else gains trust). ✅
- Pre-empt the warning on your download page with friendly text (below).
- If Defender ever flags you, submit a false-positive report at https://www.microsoft.com/en-us/wdsi/filesubmission.

Reassurance text to place right under the download button:

```
Heads-up: Peak Together is a brand-new, free, open-source project, so Windows may say
"Unknown publisher." That's expected for small free games. Click "More info" → "Run anyway."
The game needs no admin permission, installs nothing, and doesn't touch your Python or system.
To remove it, just delete the folder. Source code: github.com/strulovitz/peaktogether-website
```

## Question 6 — What requirements / version setup to standardize on

Both models agree on the key principle (pin versions; separate dev from production; don't ship matplotlib). I'm adopting GPT's cleaner three-file split. Here's the standard for every game:

- requirements-runtime.txt — only what the game needs to run (this is what gets bundled):

```
pygame==2.6.1
PyOpenGL==3.1.10
numpy==2.4.6
```

- requirements-build.txt — only the build tool:

```
pyinstaller>=6.11,<7
```

- requirements-dev.txt — runtime plus your dev-only tools (the LaTeX/PNG baking toolchain):

```
-r requirements-runtime.txt
matplotlib==3.10.9
```

One important correction to GPT's matplotlib advice. GPT recommended deleting the runtime matplotlib fallback. That's good for build size, but it's a code change to a finished, working game, and it risks introducing a crash if some code path still imports matplotlib. Since DeepSeek "can cure a headache but damage the liver," I do not want it surgically removing matplotlib from your game logic right now. Instead, we do the safe thing: tell PyInstaller to exclude matplotlib from the bundle (one line in the spec), and guard the import so that if matplotlib isn't present, the game degrades gracefully instead of crashing. This gets you the small/clean build without risky surgery on working gameplay code. I'll show this below.

## Question 7 — The one concrete, step-by-step plan (copy-paste-ready for DeepSeek)

I've merged the best of both plans and fixed two real bugs that would have hurt you:

- Bug fix #1 (from GPT's plan): GPT told you to put from pt_runtime import bootstrap at the top of app.py, with the file at descent/pt_runtime.py. That works only because cwd happens to be right — but it's fragile in a packaged build and during import ordering. I'm making the import robust so DeepSeek can't break it.
- Bug fix #2 (from Gemini's plan): Gemini's PyInstaller command bundles assets with --add-data "assets;assets" but only names the assets folder — your portraits/ PNGs and any other content files would be missing from the build, and the game would crash on a clean machine looking for them. My spec file below sweeps in all non-Python files automatically, so nothing is left out. Gemini's quick command is great for a first smoke-test, but the spec file is what you ship.

Hand everything below to DeepSeek in OpenCode. It's ordered. Each block is copy-paste-ready.

### Step 1 — Create the three requirements files (in the repo root)

requirements-runtime.txt:

```
pygame==2.6.1
PyOpenGL==3.1.10
numpy==2.4.6
```

requirements-build.txt:

```
pyinstaller>=6.11,<7
```

requirements-dev.txt:

```
-r requirements-runtime.txt
matplotlib==3.10.9
```

### Step 2 — Add the runtime bootstrap helper

Create descent/pt_runtime.py (handles base paths, per-game AppData, and a crash logger that shows a message box in the windowed build instead of failing silently):

```python
from __future__ import annotations

import ctypes
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

_GAME_SLUG = "DescentQED"
_APPDATA_DIR: Path | None = None
_BASE_DIR: Path | None = None


def bootstrap(game_slug: str = "DescentQED") -> None:
    """Call once at the very start of app.py, before loading assets."""
    global _GAME_SLUG, _APPDATA_DIR, _BASE_DIR
    _GAME_SLUG = game_slug
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

    if getattr(sys, "frozen", False):
        _BASE_DIR = Path(sys.executable).resolve().parent
    else:
        _BASE_DIR = Path(__file__).resolve().parent

    os.chdir(_BASE_DIR)

    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        _APPDATA_DIR = Path(local_appdata) / "PeakTogether" / _GAME_SLUG
    else:
        _APPDATA_DIR = Path.home() / ".peaktogether" / _GAME_SLUG
    _APPDATA_DIR.mkdir(parents=True, exist_ok=True)

    sys.excepthook = _handle_uncaught_exception


def base_dir() -> Path:
    if _BASE_DIR is None:
        bootstrap(_GAME_SLUG)
    assert _BASE_DIR is not None
    return _BASE_DIR


def appdata_dir() -> Path:
    if _APPDATA_DIR is None:
        bootstrap(_GAME_SLUG)
    assert _APPDATA_DIR is not None
    return _APPDATA_DIR


def asset_path(*parts: str) -> str:
    """Prefer this for asset loading in new/future code."""
    return str(base_dir().joinpath(*parts))


def user_path(*parts: str) -> str:
    """Use for settings, saves, logs, controller bindings."""
    return str(appdata_dir().joinpath(*parts))


def _handle_uncaught_exception(exc_type, exc_value, exc_tb) -> None:
    text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    log_path = None
    try:
        log_path = appdata_dir() / "crash-log.txt"
        with log_path.open("a", encoding="utf-8") as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write(datetime.now().isoformat(timespec="seconds") + "\n")
            f.write(text + "\n")
    except Exception:
        log_path = None

    message = "Descent QED crashed."
    if log_path is not None:
        message += f"\n\nA crash log was written here:\n{log_path}"
    message += "\n\nIf you'd like to help, please send this file to Peak Together."

    if getattr(sys, "frozen", False) and os.name == "nt":
        try:
            ctypes.windll.user32.MessageBoxW(None, message, "Descent QED", 0x00000010)
        except Exception:
            pass

    sys.__excepthook__(exc_type, exc_value, exc_tb)
```

### Step 3 — Wire it into app.py (robustly)

> DeepSeek: do this exactly. Find the very top of descent/app.py. If the file's first line is from __future__ import ..., that line MUST stay first. Insert the bootstrap call immediately after any from __future__ line(s) and before any other import (especially before pygame, OpenGL, numpy, and before any code that loads assets). Use this robust form so it works whether run from source or as a frozen exe:

```python
# --- Peak Together bootstrap (must run before pygame / asset loading) ---
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pt_runtime import bootstrap
bootstrap("DescentQED")
# --- end bootstrap ---
```

(The sys.path.insert line is the fix for GPT's fragile import — it guarantees pt_runtime is found regardless of how the game is launched.)

### Step 4 — Make matplotlib safe to be absent (no risky surgery)

> DeepSeek: do NOT delete matplotlib usage. Just find where it's imported and wrap it so a missing matplotlib never crashes the player build. Run this to locate it:

```powershell
Select-String -Path .\descent\*.py -Pattern "matplotlib" -CaseSensitive:$false
```

Then wherever you see import matplotlib..., convert it to a guarded import, e.g.:

```python
try:
    import matplotlib
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except Exception:
    matplotlib = None
    plt = None
    HAS_MATPLOTLIB = False
```

…and guard any code that uses it with if HAS_MATPLOTLIB:. We exclude matplotlib from the shipped bundle (Step 5), so this guard is what keeps the game stable. The pre-baked PNGs are already shipped, so players never need matplotlib.

### Step 5 — Add the PyInstaller spec (sweeps in ALL assets — this is the fix for Gemini's missing-files bug)

Create packaging/descent_qed_windows.spec:

```python
# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

ROOT = Path(SPECPATH).resolve().parent
GAME_DIR = ROOT / "descent"
if not GAME_DIR.exists():
    raise SystemExit(f"Could not find game directory: {GAME_DIR}")

excluded_dir_names = {"__pycache__", ".pytest_cache", ".mypy_cache",
                      ".ruff_cache", "build", "dist", ".venv-build", "build_env"}
excluded_suffixes = {".pyc", ".pyo"}

datas = []
for path in GAME_DIR.rglob("*"):
    if not path.is_file():
        continue
    if any(part in excluded_dir_names for part in path.parts):
        continue
    if path.suffix.lower() in excluded_suffixes:
        continue
    if path.suffix.lower() == ".py":
        continue  # python is analyzed from imports; here we add only data/assets
    relative_parent = path.parent.relative_to(GAME_DIR)
    datas.append((str(path), str(relative_parent)))

icon_path = GAME_DIR / "icon.ico"
icon = str(icon_path) if icon_path.exists() else None

a = Analysis(
    [str(GAME_DIR / "app.py")],
    pathex=[str(GAME_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "OpenGL", "OpenGL.GL", "OpenGL.GLU",
        "OpenGL.arrays.numpymodule", "OpenGL.platform.win32",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "tkinter", "pytest", "IPython", "jupyter"],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="Descent QED",
    debug=False,
    strip=False,
    upx=False,        # IMPORTANT: no UPX -> fewer antivirus false positives
    console=False,    # no terminal window for players
    icon=icon,
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=False, upx_exclude=[],
    name="Descent QED",
    contents_directory=".",
)
```

### Step 6 — Add the one-click build script

Create build_windows_release.ps1 in the repo root:

```powershell
$ErrorActionPreference = "Stop"
$Version = if ($env:PT_VERSION) { $env:PT_VERSION } else { Get-Date -Format "yyyy.MM.dd" }
$ZipName = "PeakTogether-DescentQED-Windows-$Version.zip"

if (!(Test-Path ".\descent\app.py")) { throw "Run from repo root (\.descent\app.py not found)." }

Write-Host "Cleaning..."
Remove-Item -Recurse -Force ".\build", ".\dist", ".\release" -ErrorAction SilentlyContinue

Write-Host "Creating build venv..."
if (!(Test-Path ".\.venv-build")) { py -3.12 -m venv .venv-build }
$Python = ".\.venv-build\Scripts\python.exe"

& $Python -m pip install --upgrade pip setuptools wheel
& $Python -m pip install -r requirements-runtime.txt -r requirements-build.txt

Write-Host "Building..."
& $Python -m PyInstaller ".\packaging\descent_qed_windows.spec" --noconfirm --clean

if (!(Test-Path ".\dist\Descent QED\Descent QED.exe")) { throw "Build failed: exe missing." }

New-Item -ItemType Directory -Force ".\release" | Out-Null

@"
Descent QED  -  Peak Together

How to play:
1. If you're reading this inside the zip, extract the zip first.
2. Open the extracted folder.
3. Double-click "Descent QED.exe".

No Python. No terminal. No installer. No admin needed.
To uninstall: delete this folder.

If it crashes, a log may appear at:
%LOCALAPPDATA%\PeakTogether\DescentQED\crash-log.txt

Website: https://peaktogether.me
Source:  https://github.com/strulovitz/peaktogether-website
"@ | Set-Content -Path ".\dist\Descent QED\README - How to Play.txt" -Encoding UTF8

Write-Host "Zipping..."
Compress-Archive -Path ".\dist\Descent QED\*" -DestinationPath ".\release\$ZipName" -Force

$Hash = Get-FileHash ".\release\$ZipName" -Algorithm SHA256
"$($Hash.Hash)  $ZipName" | Set-Content -Path ".\release\$ZipName.sha256.txt" -Encoding ASCII

Write-Host "`nDONE."
Write-Host "  .\release\$ZipName"
Write-Host "  SHA-256: $($Hash.Hash)"
Write-Host "Test this zip on a Windows PC WITHOUT Python before uploading.`n"
```

### Step 7 — Build it (you run this, Nir)

In PowerShell, from the repo root:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\build_windows_release.ps1
```

### Step 8 — Test it the right way (this is the step people skip and regret)

- Copy the .zip to your Desktop, right-click → Extract All, open the folder, double-click Descent QED.exe.
- Confirm: game launches, all images AND portraits load, sound works, keyboard/mouse work, no terminal window appears.
- Then test on a Windows machine that has NO Python installed (a friend's laptop, a relative's PC). That machine is your real audience. If it runs there, you're done.

### Step 9 — Publish on itch.io (primary, friendly front door)

Create a free itch.io account for Peak Together → New project → Kind: Downloadable, Pricing: No payment (free), Platform: Windows. Upload the .zip. Add screenshots + your trailer. Description:

```
Descent QED — a free two-player educational 6-DOF game from Peak Together.
No Python. No terminal. No installer. Just unzip and double-click "Descent QED.exe".
To uninstall, delete the folder.
Source code: https://github.com/strulovitz/peaktogether-website
```

### Step 10 — Publish on GitHub Releases (mirror + source of truth)

On strulovitz/peaktogether-website → Releases → Draft a new release → tag descent-qed-v1.0.0. Attach both the .zip and the .sha256.txt. Release notes: the same 4-step "how to play" + a line saying the SHA-256 is attached.

### Step 11 — Update peaktogether.me (Dreamhost, FileZilla)

Put the trailer/looping video at the top, then the download section:

```
▶ Download Descent QED for Windows
   No Python. No terminal. No installer. Unzip and double-click.

   [ Play on Windows ]   → links to your itch.io page
   Mirror (GitHub)       → links to your GitHub release

Heads-up: We're a brand-new free, open-source project, so Windows may say
"Unknown publisher." Click "More info" → "Run anyway." The game installs nothing,
needs no admin, and doesn't touch your Python or system. To remove it, delete the folder.
```

## Reusing this for every future game

You now have a repeatable template. For game #2, copy the structure: newgame/app.py + newgame/pt_runtime.py (with its own slug), a packaging/newgame_windows.spec, the same three requirements files, and the build script (point it at the new folder). Each game ships as its own independent zip, writes to %LOCALAPPDATA%\PeakTogether\<GameSlug>\, and shares nothing with the others. Pure-2D future games can also try pygbag for real browser play; OpenGL games stay download-only.

Linux note: PyInstaller can't cross-build Linux from Windows. When you want Linux, the free path is GitHub Actions (a Windows runner + a Linux runner build both for you automatically). Don't add this until the manual Windows release is working — Windows first.

## The Ordered Plan (do this, in this order)

1. Add requirements-runtime.txt, requirements-build.txt, requirements-dev.txt.
2. Add descent/pt_runtime.py.
3. Insert the robust bootstrap block at the top of descent/app.py.
4. Guard the matplotlib import (do not delete it); rely on the bundle excluding it.
5. Add packaging/descent_qed_windows.spec (sweeps in all assets + portraits).
6. Add build_windows_release.ps1.
7. Run the build (Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass, then .\build_windows_release.ps1).
8. Test the zip outside the repo and on a Python-free Windows PC.
9. Upload to itch.io (primary).
10. Upload the same zip + checksum to GitHub Releases (mirror).
11. Update peaktogether.me: trailer on top, "Play on Windows" → itch.io, "Mirror" → GitHub, plus the friendly SmartScreen note.
12. Reuse this exact template for every future game.

Summary of what the fusion changed vs. the individual models: I kept the architecture both agreed on (one-folder PyInstaller → zip), settled the hosting disagreement by using itch.io + GitHub together (best of both, no single point of failure), fixed Gemini's asset bug (its command would have shipped a game missing your portraits/ and content files), fixed GPT's fragile import and softened its risky "delete matplotlib" advice into a safe guard-and-exclude, and standardized the safety/version practices both recommended. The result is one plan that's safer and more complete than either model produced alone. Good luck with the launch, Nir — this is a genuinely lovely project. 🚀
