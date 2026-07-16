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

(End of file — total 9 sections)
