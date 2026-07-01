🌙 DEEPSEEK RESTART HANDOFF — BUILD PIPELINE PHASE — July 1, 2026 (evening)

## ⚠️ ON RESTART: READ THIS FIRST, THEN WORKFLOW, THEN COMMENTARIES ⚠️

---

## 🏆 WHAT WE ACHIEVED TODAY (July 1, 2026)

The BUILD PIPELINE is up and running! We wrote `build/build_all.py` — a master script that runs all 6 stages for all 20 Principia rooms.

### What's WORKING:

| Stage | Status |
|-------|--------|
| Stage 1 — Emit recipe/asy/room_source (20/20) | ✅ ALL |
| Stage 2 — Figure compile (16/20) | ✅ 16 |
| Stage 3 — Text baking (20/20, pdflatex) | ✅ ALL |
| Stage 4 — Ceiling equations (all) | ✅ ALL |
| Stage 5 — Manifest (219 assets, 438 PNGs) | ✅ |
| Stage 6 — Room runtimes (4/20) | 🔴 4 |

### Tests: 434/434 green 🟢

### Changes made to code:
- **`quake/app.py`** — fixed `PACK_DIR` from bare relative path to `__file__`-relative (smoke test now works from any CWD)
- **`quake/build/room_from_spec.py`** — multiple Asymptote emitter fixes:
  - `ray` → `path` type (Asymptote geometry module has no `ray()`)
  - `circle` → `path` type (Asymptote `circle()` returns `path`, not `circle`)
  - `tangent_at` — reverted to original (path conversion via `reltime` didn't work)
  - `angle` label positioning — now creates a `pair` at vertex+bisector
  - `arc` shorthand parsing — accepts `arc NAME FROM TO CENTER` without keywords
  - `foot` parser — accepts 2-token line shorthand (`foot T from Q to S P`)
  - `_safe_name()` — prefixes names that collide with Asymptote reserved words (`path`, `SE`, `N`, `S`, `E`, `W`, etc.)
  - Label emission — non-point geo ops extract midpoint via `point({nm}, 0.5)`
- **`quake/map/raw_models.py`** — relaxed `OpName` pattern to allow spaces (for multi-point `foot` line refs)
- **`quake/build/build_all.py`** — the new master build script (500 lines)

### Remaining issues (3 categories):

1. **🔴 RoomTooDense (14 rooms)** — `size_and_pack()` in `room_pack.py` can't fit panels+doors. Rooms with 2+ doors all fail. Tried: bigger rooms (room_px_per_m=800), more iterations (1000), bigger grow steps (1.5m), less slack (0.9). Nothing helped. **PARENT 17 launched to fix this.**

2. **🟡 Asymptote bugs (4 rooms)** — `tangent(path, pair)` on lemma_9/prop_7/prop_13, `foot(pair, line)` on prop_6. These rooms fall through to placeholder figures. Minor — can fix later.

3. **🟡 Door bearing mismatches (3 rooms)** — lemma_9, law_1, prop_13. ~0.05-0.20 rad off. Room validation rejects them. May be related to wall packer geometry.

### Parent 17 — ACTIVE
- Mission: fix the wall packer (`build/room_pack.py` + `build/room_geometry.py`)
- Handoff: `quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_17_HANDOFF.md`
- Launch files: Commentaries + OT + NT + handoff
- Nir will paste to a fresh Opus 4.8 chat

---

## 📋 WHAT TO DO ON RESTART

1. Read WORKFLOW.md (latest state)
2. Read Commentaries (latest)
3. Read this handoff
4. Check if Parent 17 has delivered
5. If delivered: drop in Parent 17's fix, run `python build/build_all.py`, verify room runtimes
6. If NOT delivered: ask Nir if he wants to wait for Parent 17 or continue with remaining issues
7. Fix remaining Asymptote bugs (tangent_at, foot) — low priority
8. Fix door bearing mismatches — low priority
9. Once ALL 20 room runtimes build: run room_viewer on a sample, smoke test with app.py
10. When everything passes: commit + push, update WORKFLOW + Commentaries

---

## 🛠️ QUICK COMMANDS

```powershell
# Full build (from quake directory)
cd C:\Users\nir_s\peaktogether-website\quake
python build/build_all.py

# Run tests
python -m pytest quake/tests -v

# View a room
python -m tools.room_viewer lemma_2 "levels/principia_bk1_inverse_square/pack"
```

## ⚠️ KNOWN GOTCHAS

- Pdflatex warmup is in build_all.py — exit code 0, packages auto-installed
- Asymptote binary: `C:\Program Files\Asymptote\asy.exe` (v3.12, NOT MiKTeX 2.88)
- Ghostscript: `C:\Users\nir_s\gs\bin\gswin64c.exe` (env var `ASYMPTOTE_GS`)
- `room_from_spec.py` tests (49) must stay green — many validator tests depend on exact error messages
- `raw_models.py` OpName pattern now allows spaces — don't revert
- `app.py` PACK_DIR is now `__file__`-relative — don't revert
- `tangent_at` was reverted to original `tangent(curve, at)` — the path-conversion approach broke everything

---

*Written by DeepSeek at end of July 1, 2026 build pipeline session. Parent 17 is the next gate.* 🚀
