# TRAILER / LOOPING VIDEO — Claude Opus 4.8's plan

> Opus 4.8's answer to `docs/OPUS_PROMPT_TRAILER_VIDEO.md`, answered solo.
> Saved **VERBATIM, word-for-word**, at Nir's request. (Code blocks are fenced for readability;
> the words and code are unchanged.)

---

Hi Nir! Happy to take this one solo — it's well within my wheelhouse, and a single coherent voice will actually serve you better here than a fusion (the risk with multiple models on a "how to make a web video" question is they'd each suggest different tools and you'd end up with a mishmash). So I'll just be your doctor directly. 🙂

Here's the short version before the details: record with the free, built-in Windows Game Bar (Win + G), trim and loop it with the free Clipchamp that's already on Windows 11 (or ffmpeg if DeepSeek wants precision), export an MP4 (H.264) plus a small WebM, host the file on your GitHub repo / a GitHub Release (NOT Dreamhost), and embed it as a muted autoplaying looping <video> with a poster image. That's the whole thing. Now the reasoning and the copy-paste blocks.

## Question 1 — How to record the game footage on Windows, for free

Your options:

- **Windows Game Bar** (built into Windows 11). Press Win + G, hit record. Pros: already installed, zero setup, designed exactly for recording games, captures the game window cleanly, free forever, no watermark. Cons: records the active game window (which is what you want) but can occasionally miss fullscreen-exclusive OpenGL apps; records at your monitor's resolution.
- **OBS Studio** (free, open-source). Pros: the gold standard, total control, can record a specific window or region, no watermark, no time limit. Cons: more setup and a small learning curve — overkill for a 10-second clip.
- **NVIDIA ShadowPlay / AMD ReLive.** Pros: great quality, near-zero performance hit. Cons: only if you have that GPU; another thing to configure.
- **Free trials of ScreenRec / Camtasia / etc.** Avoid — watermarks, nags, or paid.

My recommendation: **Windows Game Bar first.** It's free, already on your machine, and made for this exact job. If for some reason it refuses to capture your OpenGL window (it sometimes struggles with fullscreen-exclusive rendering), fall back to **OBS Studio**, which always works.

A small but important tip that makes everything easier later: **record the game in its normal 1280×800 windowed mode, not fullscreen.** Windowed mode plays nicer with Game Bar, and a 1280×800 source is plenty for a small web clip.

Steps for Game Bar:

1. Launch Descent QED in its normal window.
2. Press Win + G to open Game Bar. (If a "Do you want to open Game Bar?" prompt appears, say yes.)
3. In the Capture widget, click the round Record button (or just press Win + Alt + R to start/stop recording without even opening the overlay).
4. Play a visually exciting ~20–30 seconds: fly through a corridor, swoop past a "proof robot," do a satisfying roll. Capture more than you need — you'll trim later.
5. Press Win + Alt + R again to stop. The MP4 lands in C:\Users\<you>\Videos\Captures\.

   Note: keep the audio — you'll strip it during editing, so it doesn't matter what's playing.

## Question 2 — How to turn the footage into a short, smoothly-looping clip, for free

Your options:

- **Clipchamp** (free, built into Windows 11; made by Microsoft). Pros: already installed, friendly visual timeline, easy trim/cut, exports MP4, mute toggle, free tier with no watermark on basic exports. Cons: it's a cloud-ish app, occasionally wants a Microsoft sign-in; not frame-perfect for loops.
- **ffmpeg** (free command-line tool). Pros: absolute precision, scriptable, perfect for trimming/muting/resizing/looping with exact control, and DeepSeek can run it for you. Cons: command-line (but that's DeepSeek's job, not yours).
- **DaVinci Resolve** (free). Pros: professional-grade. Cons: huge download, steep learning curve — massive overkill for a 10-second loop.
- **CapCut / online editors.** Often watermark the free tier or require accounts. Avoid for a brand that promises "no friction."

My recommendation: a **hybrid.** You do the rough cut visually in Clipchamp (pick the best ~8–12 seconds — humans are far better at choosing the "feel-good" moment than any tool). Then DeepSeek runs ffmpeg to do the precise, repeatable technical work: mute, resize, compress, and produce the final web files. This plays to each of your strengths.

The one trick that makes a loop feel "smooth": a loop looks smooth when the last frame flows naturally into the first frame. The easiest way to achieve this is to pick a clip where the motion is continuous and steady — e.g., flying forward down a corridor at a constant speed, or a slow continuous roll. Avoid clips that end on a sudden stop, a menu, or a hard turn. You don't need a fancy crossfade; steady continuous motion is its own seamless loop because the eye can't tell where it restarts.

(If you ever do want a guaranteed-seamless "boomerang" loop — play forward, then reverse back to the start — I've put an optional ffmpeg recipe in Question 7. But honestly, a good steady-motion clip won't need it.)

## Question 3 — What file format the finished clip should be

This matters for browser compatibility and page speed. The options:

- **MP4 (H.264 video, no audio).** Pros: plays in every browser on Earth, including all phones (iPhone/Safari, Android/Chrome, desktop everything). The single most compatible web video format. Cons: slightly larger files than newer codecs.
- **WebM (VP9 or AV1).** Pros: smaller files at the same quality, great on Chrome/Firefox/Android. Cons: Safari/iPhone support is unreliable — so you can't ship only WebM.
- **GIF.** Pros: dead simple, autoplays/loops everywhere with zero JavaScript. Cons: terrible — a 10-second clip becomes a 10–30 MB monster with ugly, banded colors. A modern muted MP4 of the same clip is often one-tenth the size and looks vastly better. Do not use GIF for gameplay footage.

My recommendation: ship an **MP4 (H.264) as the primary, and optionally a WebM (VP9) as a smaller alternative.** The browser picks whichever it supports. MP4 guarantees it works for everyone (critical, since your audience is mostly on phones and Windows); WebM just makes it a bit lighter for the browsers that support it. If you want to keep things dead simple, MP4 alone is completely fine — the WebM is a nice-to-have, not a requirement.

## Question 4 — How to put it on the page (autoplay, loop, silent, mobile-friendly)

Here's the crucial rule that trips everyone up: **browsers will only autoplay a video if it is muted.** A video with sound is blocked from autoplaying (by design, to stop annoying ads). So your <video> must be muted. It also needs playsinline so iPhones play it inside the page instead of hijacking the screen into fullscreen.

Below is the exact code for DeepSeek. It includes a poster image (a still frame shown instantly while the video loads, so the page never looks broken or blank), graceful fallback, and is fully responsive. I've written it to drop into your existing static HTML cleanly.

> DeepSeek: paste this <video> block at the top of arcade/descent-qed/index.html, just inside the hero/top area, above the existing hero-art image (or replacing it, Nir's choice). Adjust the src URLs in Question 5/7 once the files are hosted. Keep the poster pointing at a real still frame.

```html
<!-- Peak Together: autoplaying, looping, silent gameplay clip -->
<div class="pt-clip">
  <video
    class="pt-clip__video"
    autoplay
    loop
    muted
    playsinline
    preload="metadata"
    poster="/images/descent-qed-clip-poster.jpg"
    aria-label="Gameplay footage of Descent QED, looping silently">
    <!-- Smaller, modern format first; browsers that support it use it. -->
    <source src="VIDEO_URL_HERE.webm" type="video/webm" />
    <!-- Universally-supported fallback (works on iPhone, Android, all desktops). -->
    <source src="VIDEO_URL_HERE.mp4" type="video/mp4" />
    <!-- If video can't play at all, show the still image instead. -->
    <img src="/images/descent-qed-clip-poster.jpg"
         alt="Descent QED gameplay" />
  </video>
</div>
```

And the matching CSS. DeepSeek: add this to the site's style.css, and bump the cache-buster (style.css?v=N → v=N+1) wherever it's referenced.

```css
/* Looping gameplay clip */
.pt-clip {
  width: 100%;
  max-width: 960px;      /* keeps it tidy on big screens */
  margin: 0 auto 1.5rem; /* centered, with space below */
  border-radius: 12px;   /* matches a cozy, soft look */
  overflow: hidden;
  background: #000;       /* avoids a flash before the video paints */
  aspect-ratio: 16 / 9;   /* reserves space so the page doesn't jump */
}

.pt-clip__video {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;      /* fills the box nicely on phones and desktop */
}
```

A few notes on why this is built the way it is:

- **muted + autoplay + playsinline** together are the magic combination that makes silent autoplay work on iPhone, Android, and desktop alike. Miss any one and mobile breaks.
- **poster** shows a still frame instantly, so even on a slow phone connection the page looks finished, not empty, while the video streams in.
- **preload="metadata"** means the browser doesn't download the whole video until it's needed, keeping the page fast.
- **aspect-ratio: 16/9** reserves the space up front so your layout doesn't "jump" as the video loads (good for feel and for Google's page-quality scoring).
- One honest caveat: your game window is 1280×800, which is a **16:10** shape, not 16:9. You have two clean choices — either change the CSS to `aspect-ratio: 16 / 10;` to match exactly (no cropping), or keep 16/9 and let `object-fit: cover` crop a sliver off the top/bottom (often looks more "cinematic"). I'd use **16 / 10** to show your real game honestly. Tell DeepSeek which you prefer; if unsure, go 16/10.

## Question 5 — Where to host the video file for free

Dreamhost is out (you said so, correctly — VPS bandwidth is the wrong place for a video that might get hammered). The realistic free options:

- **Your GitHub repo (committed file) or a GitHub Release asset.** Pros: free, you already use GitHub, backed by a fast CDN, gives you a permanent direct link you can put straight in the <source src>. The video lives right next to your project. Cons: GitHub politely discourages very large binaries in the repo itself (keep repo files under ~25–50 MB — totally fine for a 1–4 MB clip). For anything bigger, attach it as a Release asset instead, which is built for binaries. For your tiny clip, committing it to the repo is simplest.
- **jsDelivr CDN** (free, sits on top of your GitHub repo). Pros: takes any file in your public GitHub repo and serves it through a very fast global CDN with proper caching — ideal for video. Free, no account, no upload step (it mirrors GitHub automatically). Cons: one extra URL pattern to learn (I give it to you below). This is the quiet pro move.
- **YouTube (unlisted) embedded.** Pros: free, infinite bandwidth. Cons: wrong tool for a silent background loop — you get the YouTube player chrome, branding, "more videos" suggestions, cookie/privacy banners, and clumsy autoplay/loop behavior. It fights your cozy, no-friction brand. Avoid for this purpose (great for a full trailer later, just not for the silent top-of-page loop).
- **Cloudinary / imgkit / other free media CDNs.** Pros: real video CDNs with free tiers. Cons: another account, free-tier limits, and overkill when GitHub+jsDelivr already does the job for free.

My recommendation: **host the file in your GitHub repo and serve it through jsDelivr.** You're already on GitHub, it costs nothing, it's fast worldwide, and it keeps your video out of Dreamhost's bandwidth entirely. No new accounts, no new platforms.

Concretely: if you commit the file to your repo at, say, arcade/descent-qed/descent-qed-clip.mp4, the jsDelivr URL is:

```
https://cdn.jsdelivr.net/gh/strulovitz/peaktogether-website@main/arcade/descent-qed/descent-qed-clip.mp4
```

(Pattern: https://cdn.jsdelivr.net/gh/USER/REPO@BRANCH/PATH.) Put that URL into the <source src> in the page code from Question 4. Same idea for the .webm.

> If your repo's default branch is named something other than main (e.g., master), swap it in. And the file must be in a public repo for jsDelivr to serve it — yours is public, so you're set.

## Question 6 — What to aim for (length, quality, file size)

Targets tuned to "looks great, loads fast, makes them want to download":

- **Length:** 8–12 seconds. Long enough to show the feel (flying, a proof-robot moment), short enough to loop without feeling repetitive. Sweet spot ~10 seconds.
- **Resolution:** 1280×720 (or 1280×800 to match your game exactly). Your source is 1280×800; don't upscale. For a top-of-page hero clip, 720-ish is plenty crisp and keeps the file small.
- **Frame rate:** 30 fps for the web clip. Your game runs at 60, but 30 fps roughly halves the file size and looks perfectly smooth for background footage. (Keep 60 if you ever post a full trailer to YouTube, but for the silent loop, 30 is the right tradeoff.)
- **File size:** aim for 1–3 MB for the MP4 (and the WebM will come out even smaller). Under ~3 MB keeps the page genuinely fast even on phone data. The ffmpeg settings in Question 7 are tuned to hit this.
- **No audio** (you don't need it and it must be muted anyway — so we strip it entirely, which also shrinks the file).

## Question 7 — One concrete, ordered, start-to-finish plan

Here's the whole path. Steps you do are marked (Nir); steps for DeepSeek are marked (DeepSeek).

**Step 1 (Nir) — Record.** Launch Descent QED in its 1280×800 window. Press Win + Alt + R to start recording, fly through a corridor with smooth steady motion past a proof-robot for ~25–30 seconds, press Win + Alt + R to stop. Find the file in C:\Users\<you>\Videos\Captures\.

**Step 2 (Nir) — Rough-cut to the best moment.** Open Clipchamp (search "Clipchamp" in the Start menu — it's preinstalled on Windows 11). Import your capture, drag it to the timeline, and trim it down to the best ~10 seconds of continuous, smooth motion. Export as MP4 (1080p or "Auto" is fine — DeepSeek will re-compress). Save it somewhere easy, e.g. C:\Users\<you>\Videos\descent-raw.mp4. (If Clipchamp annoys you with sign-in prompts, you can skip it entirely and let DeepSeek trim with ffmpeg in Step 3 — just tell DeepSeek the start time and duration of the good part.)

**Step 3 (DeepSeek) — Process with ffmpeg.** First install ffmpeg if it isn't present, then produce the web files. Run from PowerShell:

```powershell
# Install ffmpeg (free, no admin needed) via winget:
winget install --id Gyan.FFmpeg -e

# (Open a fresh PowerShell window afterward so ffmpeg is on PATH.)

# Set these to your real input file and a working folder:
$IN  = "$env:USERPROFILE\Videos\descent-raw.mp4"
$OUT = "$env:USERPROFILE\Videos\pt-clip"
New-Item -ItemType Directory -Force $OUT | Out-Null

# Make the MP4 (H.264, muted, ~10s, 30fps, scaled to 1280 wide, web-optimized):
# If your Clipchamp clip is already ~10s, drop the -t 10 line.
ffmpeg -y -i "$IN" `
  -t 10 `
  -an `
  -vf "scale=1280:-2,fps=30" `
  -c:v libx264 -profile:v high -pix_fmt yuv420p `
  -crf 26 -preset slow -movflags +faststart `
  "$OUT\descent-qed-clip.mp4"

# Make the smaller WebM (VP9, muted) as a modern alternative:
ffmpeg -y -i "$IN" `
  -t 10 `
  -an `
  -vf "scale=1280:-2,fps=30" `
  -c:v libvpx-vp9 -b:v 0 -crf 33 `
  "$OUT\descent-qed-clip.webm"

# Make the poster still (a sharp frame grabbed ~1 second in):
ffmpeg -y -i "$IN" -ss 00:00:01 -frames:v 1 `
  -vf "scale=1280:-2" `
  "$OUT\descent-qed-clip-poster.jpg"

# Report the sizes so we can confirm they're small enough:
Get-ChildItem "$OUT" | Select-Object Name, @{n='MB';e={[math]::Round($_.Length/1MB,2)}}
```

A couple of notes for DeepSeek: -an strips audio; -crf 26 controls quality/size (lower = better/bigger; if the MP4 comes out over ~3 MB, raise to 28; if it looks soft, lower to 23). +faststart lets the video begin playing before it's fully downloaded. The scale=1280:-2 keeps the original aspect ratio (so 1280×800 stays 16:10) and guarantees even dimensions H.264 requires.

> Optional seamless "boomerang" loop (only if the plain clip's restart looks jumpy). This plays the clip forward then reversed, so the end always matches the start:

```powershell
ffmpeg -y -i "$OUT\descent-qed-clip.mp4" `
  -filter_complex "[0]reverse[r];[0][r]concat=n=2:v=1:a=0" `
  -c:v libx264 -pix_fmt yuv420p -crf 26 -preset slow -movflags +faststart `
  "$OUT\descent-qed-clip-loop.mp4"
```

> If you use this, point the page's MP4 <source> at ...-clip-loop.mp4 instead.

**Step 4 (DeepSeek) — Put the files in the repo.** Copy descent-qed-clip.mp4 and descent-qed-clip.webm into arcade/descent-qed/ in the repo, and copy descent-qed-clip-poster.jpg into /images/. Commit and push:

```powershell
# From the repo root:
Copy-Item "$env:USERPROFILE\Videos\pt-clip\descent-qed-clip.mp4"  ".\arcade\descent-qed\"
Copy-Item "$env:USERPROFILE\Videos\pt-clip\descent-qed-clip.webm" ".\arcade\descent-qed\"
Copy-Item "$env:USERPROFILE\Videos\pt-clip\descent-qed-clip-poster.jpg" ".\images\"

git add arcade/descent-qed/descent-qed-clip.mp4 arcade/descent-qed/descent-qed-clip.webm images/descent-qed-clip-poster.jpg
git commit -m "Add looping gameplay clip + poster for Descent QED page"
git push
```

**Step 5 (DeepSeek) — Add the video block to the page.** Paste the <video> HTML from Question 4 at the top of arcade/descent-qed/index.html, and add the CSS from Question 4 to style.css (and bump the ?v=N cache-buster). Set the <source> URLs to the jsDelivr links:

```html
<source src="https://cdn.jsdelivr.net/gh/strulovitz/peaktogether-website@main/arcade/descent-qed/descent-qed-clip.webm" type="video/webm" />
<source src="https://cdn.jsdelivr.net/gh/strulovitz/peaktogether-website@main/arcade/descent-qed/descent-qed-clip.mp4"  type="video/mp4" />
```

(The poster="/images/descent-qed-clip-poster.jpg" stays a local path since it's a tiny image your Dreamhost can serve fine — or point it at jsDelivr too if you prefer. And decide aspect-ratio: 16/10 vs 16/9 per Question 4 — I recommend 16/10.)

**Step 6 (Nir) — Upload the changed website files via FileZilla.** Upload the edited arcade/descent-qed/index.html and the updated style.css (the video itself is served from jsDelivr/GitHub, so it does not go on Dreamhost — only your HTML/CSS changes do). The poster image goes to /images/ if you used a local path.

**Step 7 (Nir) — Test.** Open https://www.peaktogether.me/arcade/descent-qed/ on a desktop and on your phone. Confirm: it autoplays, it's silent, it loops, it looks good, and the page still feels fast. On iPhone especially, confirm it plays inline (not fullscreen) — if it doesn't, double-check muted and playsinline are both present.

## The Ordered Plan (act on this)

1. (Nir) Record ~25–30s of smooth, continuous gameplay with Windows Game Bar (Win + Alt + R), in the 1280×800 window.
2. (Nir) Trim to the best ~10 seconds in Clipchamp (or hand the start-time + duration to DeepSeek to trim with ffmpeg).
3. (DeepSeek) Install ffmpeg (winget install Gyan.FFmpeg) and run the commands in Step 3 to produce a muted MP4 (~1–3 MB), a smaller WebM, and a poster JPG.
4. (DeepSeek) Commit the video files + poster to the GitHub repo and push (served free via jsDelivr CDN, keeping Dreamhost out of it).
5. (DeepSeek) Add the muted/autoplay/loop/playsinline <video> block to arcade/descent-qed/index.html and the CSS to style.css, bump the ?v=N, and set the jsDelivr <source> URLs (use aspect-ratio: 16/10 to match the real game).
6. (Nir) Upload only the changed HTML/CSS (and poster) via FileZilla — the video lives on GitHub/jsDelivr, not Dreamhost.
7. (Nir) Test on desktop and iPhone: silent autoplay, smooth loop, fast page, inline (not fullscreen) on mobile.

That's the whole thing, start to finish, free, and reusable for every future game — just swap the filenames and the trimmed footage. Have fun with it, Nir; a good 10-second loop of that ship threading a corridor is going to do a lot of quiet work for you. 🚀
