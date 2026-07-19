# 🗞️ PRESS PLAYBOOK — How We Do Press Outreach (EXACT recipe)

> ⭐ **DeepSeek: read this FIRST, top to bottom, every time Nir says "let's do press."**
> This is the exact process for pitching journalists — 5 letters × 5 subject lines,
> one outlet at a time. Author: DeepSeek V4 Pro in OpenCode. For: Nir (GitHub: strulovitz).

---

## 0. What we have

Fable wrote 5 different letters and 5 different subject lines ("arrowheads"), one for each type of journalist. Every letter and every subject line is **VERBATIM, WORD-FOR-WORD, AS-IS** — never paraphrased, never edited, never "improved."

The 5 types (in order of attack per outlet):

| # | Type | Letter file | Subject line starts with... |
|---|------|-------------|---------------------------|
| 🥇 | Technology / AI reporter | `press/letter-1-tech-ai.md` | *I can't write a line of code. I directed AI to build a "Disneyland of mathematics"...* |
| 🥈 | Internet culture / digital culture writer | `press/letter-2-internet-culture.md` | *The most wholesome strange thing on the internet...* |
| 🥉 | Science / math writer | `press/letter-3-science-math.md` | *The hardest unsolved problems in science...* |
| 4️⃣ | Features / human-interest writer | `press/letter-4-features-human-interest.md` | *He fought AI for ten years. Then he used it to build...* |
| 5️⃣ | Education / edtech reporter | `press/letter-5-education.md` | *A free "science museum" where teenagers learn university math...* |

Tracking file: `press/pitch-tracker.md` — contains ALL 5 letters verbatim, ALL 5 subject lines verbatim, and the journalist table.

---

## 1. THE SACRED RULES (never break)

1. **Letters are HOLY / VERBATIM.** Every word Fable wrote stays exactly as-is. The ONLY thing DeepSeek changes: `Dear journalist,` → `Dear [NAME],` (and NOTHING else — not punctuation, not line breaks, not a single comma).
2. **Subject lines are HOLY / VERBATIM.** Never edited.
3. **Names are EXACT.** Never invented, never guessed, never "sounds like." Extracted precisely from whatever Nir pastes from Google.
4. **Emails are EXACT.** If Google shows 3 emails for one person, save all 3. Never pick one; never drop any.
5. **VERBATIM output for Nir every time.** The full letter (with name embedded + correct subject line) ready to copy-paste and send.
6. **Track EVERYTHING.** After Nir confirms a send, mark that person DONE in `press/pitch-tracker.md`.

---

## 2. THE WORKFLOW (step by step, every outlet)

### Phase A — Nir picks an outlet

Nir says: "Let's do press for [OUTLET NAME]." (e.g. New York Times, CNN, Wired, The Guardian...)

### Phase B — One type at a time (always in order: 1 → 2 → 3 → 4 → 5)

For each type, repeat this exact loop:

1. **Nir Googles.** He searches Google for something like:
   - Type 1: *"New York Times technology reporter"*
   - Type 2: *"New York Times internet culture writer"*
   - Type 3: *"New York Times science reporter"*
   - Type 4: *"New York Times features writer"*
   - Type 5: *"New York Times education reporter"*

2. **Nir pastes.** He copy-pastes whatever Google AI Overview / search results / articles show him into our chat. This paste contains names, sometimes emails, sometimes just context. Nir does NOT need to clean it — just paste it raw.

3. **DeepSeek extracts.** From the paste, DeepSeek finds:
   - Exact name (as written — don't fix casing, don't expand initials)
   - ALL email addresses found (if none found, say so honestly)
   - Publication / outlet (the one Nir said)
   - Country (infer from outlet: NYT = USA, Guardian = UK, etc.)

4. **DeepSeek outputs** in this exact format for Nir to copy-paste and send:

   **Name:** [exact name from Google]
   **Email(s):** [email1, email2, ...] or "No email found in search results"
   **Type:** [# - e.g. 1 - Technology / AI]
   ```
   Subject: [VERBATIM subject line for this type]

   Dear [NAME],

   [VERBATIM letter for this type — nothing else changed]
   ```

5. **Nir sends the email** (from his Gmail, manually).

6. **Nir says "done"** — then DeepSeek updates `press/pitch-tracker.md`:
   - Adds the row: Name | Email(s) | Publication | Country | Status: ✅ Sent
   - Commits + pushes

7. **Repeat** for the next person of the SAME type in the SAME outlet, until all people of that type are done.

8. **Then move to the next type** (Type 2, then 3, then 4, then 5) for the SAME outlet.

9. **When all 5 types are done for an outlet** → Nir picks the next outlet.

---

## 3. DEEPSEEK'S JOB PER PASTE

When Nir pastes Google results, DeepSeek:

1. Reads the paste carefully.
2. Finds all journalist names and their emails.
3. For EACH person found, outputs the copy-paste block (see §2 step 4).
4. If multiple people are in one paste, outputs one block per person.
5. If no email is found for a person, says: "Email(s): No email found in search results" but STILL gives the copy-paste block (Nir may find the email another way).
6. Never skips a person. Never batches unrelated people together.

---

## 4. THE TRACKER FORMAT

`press/pitch-tracker.md` has a table:

| # | Name | Email(s) | Publication | Type | Country | Status |
|---|------|----------|-------------|------|---------|--------|
| 1 | Jane Doe | jane@nyt.com | New York Times | 1-Tech | USA | ✅ Sent |

Status values:
- `✅ Sent` — Nir confirmed it was sent
- `⏳ Pending` — extracted but not yet sent
- `❌ No email` — name found but no email

---

## 5. WHAT DEEPSEEK NEVER DOES

- ❌ Never edits the letter (except `Dear [NAME],`).
- ❌ Never edits the subject line.
- ❌ Never invents a name.
- ❌ Never invents or guesses an email.
- ❌ Never changes the type order (always 1→2→3→4→5).
- ❌ Never skips a person found in the paste.
- ❌ Never sends the email — Nir sends it himself manually.
- ❌ Never uses the "quiz"/question tool. All communication is plain chat text.

---

## 6. FILES

| File | Purpose |
|------|---------|
| `press/pitch-tracker.md` | Master tracker — letters, subject lines, journalist table |
| `press/letter-1-tech-ai.md` | Letter #1 — Technology / AI reporter |
| `press/letter-2-internet-culture.md` | Letter #2 — Internet culture / digital culture |
| `press/letter-3-science-math.md` | Letter #3 — Science / math writer |
| `press/letter-4-features-human-interest.md` | Letter #4 — Features / human-interest |
| `press/letter-5-education.md` | Letter #5 — Education / edtech |

---

## 7. COMMIT + PUSH

After EVERY change to the tracker (marking someone sent, adding rows), DeepSeek commits and pushes with a clear message like:
- `press: NYT — Tech/AI — Jane Doe sent`

---

## 8. RESTART PROTOCOL

On restart, read:
1. This playbook first.
2. `press/pitch-tracker.md` to see where we stopped.
3. Ask Nir: "Continue with [CURRENT OUTLET], Type [N]?"

---

## 9. PRACTICAL RULES FROM THE TRENCHES (locked July 16, 2026)

### 9a. ONE JOURNALIST AT A TIME

DeepSeek works through journalists **ONE BY ONE** — never all at once. The loop:
1. DeepSeek reads the tracker → finds the next unsent journalist name.
2. DeepSeek tries to find their email from the internet (author pages, etc.).
3. If found → DeepSeek outputs the full copy-paste block (subject + letter with name).
4. If NOT found → DeepSeek tells Nir honestly: "Email not found. Nir, can you Google '[NAME] [OUTLET] email' and paste the results?"
5. Nir pastes Google results → DeepSeek extracts the email → outputs the block.
6. Nir sends from Gmail, says "done" → DeepSeek updates tracker + commits + pushes.
7. Move to the NEXT journalist of the SAME type.

### 9b. HOW DEEPSEEK SEARCHES FOR EMAILS

- DeepSeek checks the journalist's author page on the publication's website (e.g. `technologyreview.com/author/niall-firth/`).
- DeepSeek checks the publication's "Our Team" or masthead page.
- If still no email → DeepSeek asks Nir to Google it. DeepSeek does NOT:
  - ❌ Use Muck Rack (Nir forbids it — July 16, 2026)
  - ❌ Use RocketReach, Hunter.io, or any paid email-finding service
  - ❌ Invent or guess an email pattern (e.g. firstname.lastname@outlet.com)
  - ❌ Scrape LinkedIn or Twitter/X

### 9c. JOURNALIST NAMES COME FROM THE TRACKER

The tracker already lists which journalists to send to (Nir named them earlier in the process). DeepSeek reads the tracker's status marker to find who's next. DeepSeek does NOT invent new names or search for additional journalists — those are Nir's picks.

### 9d. MOUNTAINS ARE PAUSED DURING PRESS PHASE

While we are in press outreach, mountain building is **PAUSED**. Do NOT mention mountains, do NOT ask about next mountains, do NOT read the mountain playbook — unless Nir explicitly says "let's do a mountain." The AGENTS.md CURRENT PHASE marker reflects this.

### 9e. COMMIT + PUSH AFTER EVERY SEND

After Nir confirms a journalist was sent, DeepSeek:
1. Updates `press/pitch-tracker.md` (adds the row, updates the status marker comment).
2. Commits with message: `press: [OUTLET] — [Type] — [Name] sent`
3. Pushes to GitHub.

This is NOT optional. Every send = one commit + push.

---

## 10. OPENCLAW AUTOMATION (established July 16-17, 2026)

We attempted to automate the entire press outreach pipeline with OpenClaw —
an open-source personal AI agent that runs locally, connects to Telegram,
and can call APIs. The goal: Nir says "start press: CNN" and the agent finds
journalists, searches emails, sends verbatim letters.

### 10a. OPENCLAW SETUP (completed)

- **Installed:** Windows, Node.js, `npm i -g openclaw@latest`
- **Model:** DeepSeek V4 Pro (Nir's API key from platform.deepseek.com)
- **Telegram:** Bot created via @BotFather, connected (pairing approved)
- **DeepSeek plugin:** `@openclaw/deepseek-provider` installed
- **Google plugin:** Bundled (`stock:google/index.js`), enabled
- **Config:** `~/.openclaw/openclaw.json`
- **Press skill:** Written at `~/.openclaw/skills/press-outreach/SKILL.md`
  Contains all 5 verbatim letters, grouping rules, workflow instructions.
  Agent discovers skills on session restart.

### 10b. GEMINI API KEY (for Google web search)

- **Created:** Google AI Studio → https://aistudio.google.com/apikey
- **Key format:** Newer format starting with `AQ.` (NOT the old `AIza` format).
  Both formats are valid — Google changed the prefix in 2026.
- **Set as:** Windows user env var `GEMINI_API_KEY` (permanent, survives reboot).
  Also in `openclaw.json` under `plugins.entries.google.config.webSearch.apiKey`.
- **Cost:** FREE tier — limited quota, resets daily at 10:00 AM Israel time.

### 10c. KNOWN BUG — OpenClaw Gemini web_search FAILS

OpenClaw's built-in `web_search` with `provider: "gemini"` is BROKEN.
GitHub PR #104672 "fix(gemini): resolve search env secret refs" — STILL OPEN
as of July 16, 2026. The Google plugin loads but credential resolution for
the web_search provider flow fails.

**Workaround:** Call Gemini API directly via `exec` tool using Fable's script.

### 10d. FABLE'S GEMINI SCRIPT (the working solution)

File: `C:\Users\nir_s\gemini_websearch.py`

- Stdlib-only Python (no pip install)
- Calls `generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`
- Uses `x-goog-api-key` header for auth (not URL query param)
- `tools: [{"google_search": {}}]` for Google Search grounding
- Handles 429 with exponential backoff (honors Google's RetryInfo)
- Falls through multiple models on 400/404
- Reads API key from env var first, then from openclaw.json
- Never prints the key

**Critical gotcha:** `-lite` models do NOT support `google_search`.
Only full models (e.g. gemini-2.0-flash, gemini-3.5-flash, gemini-flash-latest)
work with search grounding.

### 10e. GEMINI QUOTA & RATE LIMITS

- Free tier has separate quotas for plain generateContent vs grounded search.
- Grounded search quota is SMALL — easy to exhaust with testing.
- `gemini-2.5-flash` returns 404 on v1beta (may need v1alpha endpoint or
  doesn't support grounding on this tier).
- `gemini-2.0-flash` works but also has quota.
- Daily reset: midnight Pacific = **10:00 AM Israel time**.
- **Rule:** ONE test per session. Do NOT hammer the API.

### 10f. LESSONS LEARNED (DON'T REPEAT)

1. ❌ OpenClaw's Gemini `web_search` tool has a KNOWN BUG. Don't waste time debugging it.
2. ❌ Don't hammer the Gemini API with test queries — exhausts grounded search quota.
3. ✅ Call Gemini directly via Python + exec (Fable's script pattern).
4. ✅ Always use `x-goog-api-key` header, not `?key=` query param.
5. ✅ Non-lite models only for `google_search` grounding.
6. ✅ `gemini_websearch.py` has built-in backoff + model fallback.
7. ✅ Daily quota reset = 10:00 AM Israel time.

### 10g. GOOGLE-SEARCH KEY FORMAT (2026)

Google changed their API key format in 2026. New keys from aistudio.google.com
start with `AQ.` (not `AIza`). Both are valid. Don't tell Nir his key is
"wrong format" — it's the new format.

---

## 11. CURRENT STATUS — July 17, 2026 (end of session)

### 11a. WHAT'S SET UP AND WORKING

| Component | Status | Details |
|-----------|--------|---------|
| OpenClaw agent | ✅ | Windows, Node.js, DeepSeek V4 Pro model |
| Telegram | ✅ | Bot connected, Nir can message from phone |
| Web search | ✅ | DuckDuckGo (free, no key, native OpenClaw support) |
| Press skill | ✅ | `~/.openclaw/skills/press-outreach/SKILL.md` — all 5 letters |
| Email sending | ✅ | `C:\Users\nir_s\gmail-send.py` — SMTP via Gmail App Password |
| GitHub access | ✅ | Git credentials work, can commit + push tracker |
| Gemini API key | ⚠️ | AQ format key created but NOT usable (zero quota, Vertex billing wall) |
| DeepSeek API key | ✅ | Working as main model |

### 11b. GMAIL SENDING SCRIPT

File: `C:\Users\nir_s\gmail-send.py`

Usage: `python C:\Users\nir_s\gmail-send.py "to@email.com" "Subject" "Body text"`

Reads `OPENCLAW_GMAIL_APP_PASSWORD` env var (set as permanent Windows user var).
Sends via `smtp.gmail.com:587` using `nir.strulovitz@gmail.com`.
Strips spaces from the app password automatically (Google displays with spaces).

OpenClaw calls this via `exec` tool. Must be instructed:
```
python C:\Users\nir_s\gmail-send.py "recipient@email.com" "Subject" "Body"
```

### 11c. WHY GEMINI/GOOGLE FAILED (lesson learned)

- `AQ.` format keys are Vertex AI express mode, NOT Developer API keys
- New Google Cloud projects only get AQ keys — no more `AIza` keys
- AQ keys on Developer API = zero entitlement (not rate-limited — permanently zero)
- AQ keys on Vertex AI = requires billing setup (403)
- Google Custom Search JSON API = CLOSED to new customers (2026)
- Google Programmable Search "entire web" = DEPRECATED (2026)
- **Bottom line:** Google has killed ALL free web search APIs for new users in 2026
- **Solution:** DuckDuckGo (free, works, no key, native OpenClaw plugin)

### 11d. PRESS OUTREACH STATUS

| Outlet | Sent | Status |
|--------|------|--------|
| WIRED | 39 | Complete |
| MIT Tech Review | 27 | Complete |
| CNN | 20 | Complete |
| NYT | 35 | Complete |
| WaPo | 21 | Complete |
| BBC | 20 | Complete |
| Guardian | 301 | Complete |
| Observer | 15 | Complete |
| The Verge | 13 | Complete |

**Grand total: 491 journalists across 9 outlets.**

ALL OUTLETS COMPLETE. Next: Nir picks the next outlet or decides what's next.

### 11e. WHAT STILL NEEDS TO BE DONE

1. **Await Nir's decision** — All 9 outlets are complete. Nir picks what's next: more outlets, mountains, or something else.

### 11f. AGENT INSTRUCTIONS (verbatim — give to OpenClaw on fresh session)

```
You have the press-outreach skill. Read it. Use DuckDuckGo for search.
Space searches 30 seconds apart. Prefer web_fetch on profile pages.
Send emails with: python C:\Users\nir_s\gmail-send.py "email" "subject" "body"
After each send, update C:\Users\nir_s\peaktogether-website\press\pitch-tracker.md
then git add + git commit + git push from C:\Users\nir_s\peaktogether-website
Never invent emails. Never edit letters. One journalist at a time.
Start: WIRED + MIT TR + CNN are COMPLETE (86 sent). Ask Nir which outlet is next.
```

---

(End of file — total 11 sections)
