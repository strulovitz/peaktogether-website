# PROMPT TO OPUS — QUAKE PARENT 11: FIX THE RENDERERS (Mode A wireframe + Mode B room)

> DeepSeek-authored handoff (not Opus's words). Written June 28, 2026, to launch a FRESH, single-mission Parent 11 after Parent 10 died of context overload. The 4 baseline launch files for this parent = Commentaries + Old Testament + this handoff (the New Testament is deliberately left off — it concerns content design, not rendering). Uses the question-first material protocol and ends WITHOUT "GO" (talk-first rhythm).

---

You are Parent 11. You get this handoff plus the baseline scriptures (the Commentaries + the Old Testament). Welcome — your mission this session is small, sharp, and singular.

------------------------------------------------------------
0) THE WORKING MODEL (how we operate)
- You are the ARCHITECT. You write design + frozen child briefs — OR, if you judge it cleaner for tightly-coupled GPU code, you may write the corrected code directly (Parent 6 did exactly this for app.py).
- Children (fresh chats) implement to your frozen contract. DeepSeek integrates the code, runs the test suite, and pushes. Nir decides everything and carries text between chats.
- Nir knows NO code and NO math. All understanding is yours. Nir's role is mechanical: paste, run, install, eyeball.
- You have NO internet and NO file access — BUT DeepSeek can see the entire codebase and every scripture and will answer your questions with EXACT VERBATIM excerpts. So you never need whole files dumped on you (see §5 — this is how we keep your context alive).

------------------------------------------------------------
1) YOUR ONE MISSION (tightly bounded)
Fix how the game DRAWS — the two renderers — so the game can actually be seen:
  (A) Mode A — the transparent WIREFRAME corridor map. Restore the PROPER look the Old Testament mandates (see §4), NOT the current 1-pixel GL_LINES stopgap.
  (B) Mode B — the SOLID first-person room. It is currently UNVERIFIED and may render black. If rooms render black, the game is pointless no matter how good the content is. Diagnose and fix.

EXPLICITLY OUT OF SCOPE (do NOT touch — other parents' jobs):
  - The 20-room Principia content (figures, recipes, LaTeX, ceiling equations) — that is the NEXT, SEPARATE parent (Parent 12). Design no content.
  - The layout / level_maker / crossing engine — DONE (5 crossings, 382 tests green). Don't touch it.
Stay on the two renderers and whatever minimal caller-side wiring the fix genuinely requires. Nothing else.

------------------------------------------------------------
2) WHY THIS IS THE GATE
The engine is complete, the layout is done, 382 tests are green, and Nir can already fly the map viewer. But the corridor renderer is a placeholder and the room renderer is unproven. This is the make-or-break VISUAL gate: no point building 20 beautiful rooms we cannot display.

------------------------------------------------------------
3) WHAT WE CURRENTLY BELIEVE IS WRONG  (⚠️ CONFIRM by asking us to show you the exact code — our summary has been wrong before, so trust the verbatim code, not this paragraph)
  - render_wire.py is currently the SIMPLIFIED GL_LINES stopgap. It lost the camera-facing quad-expansion, thick lines, distance-dimming, and bloom the OT requires. Likely needs a proper REBUILD, not a patch. (An older "5-bug" report is STALE — three of those were already fixed during map-viewer work. Don't chase them.)
  - render_room.py (Mode B) is unverified and strongly suspected broken: it appears to call moderngl.create_context() on EVERY draw (a new GL context per frame) — a prime suspect for "black rooms." It also seems to rebuild its shader program every frame (no cache) and may use a view-only matrix with NO perspective projection.
  - The perspective / MVP projection is partly a CALLER concern (app.py / map_viewer.py), so some of the fix may live there. IMPORTANT: the standalone map_viewer.py was ALREADY given a working perspective (it flies correctly today). Do NOT undo that — reconcile with it.
  - GL state ownership between Mode A (blend OFF, depth-write ON) and Mode B (panels need blend ON) must be made explicit, or panels won't composite.

------------------------------------------------------------
4) THE LOCKED AESTHETIC (do not re-decide — implement faithfully)
You hold the Old Testament; its render-mode section is your spec. LOCKED:
  - Mode A: transparent wireframe; depth test ON, depth write ON, blend OFF, depthFunc LEQUAL; near occludes far; distance-dimming white->dark-grey, NEVER pure black; camera-facing line-quads + depth bias (fixes thin-line dropout at dense crossings); subtle screen-space bloom for neon glow (NOT real blending); ~3 floor guide-lines. Pure transit.
  - Mode B: solid first-person room; walls-with-holes at door bearings; baked panels (off=grey / on=colored); ceiling equations tint blood-red after the demon dies.
Don't reopen these; realize them.

------------------------------------------------------------
5) HOW YOU GET INFORMATION  (this is what keeps your context ALIVE — please work this way)
DeepSeek can read and search the ENTIRE codebase and all scriptures. So:
  - DEFAULT MODE: Ask DeepSeek precise QUESTIONS about whatever you need to understand. You'll get back the EXACT VERBATIM code/text that answers it — pulled from wherever it lives, including a few lines stitched across several files (a "cross-cut"). BATCH several questions together when you can.
  - Think in terms of "what do I need to KNOW to design this," NOT "which file do I want." You don't need to know our file layout. Examples:
      - "Show me, verbatim, exactly how the MVP matrix is built and passed into BOTH renderers' draw calls."
      - "Show me how render_room acquires its GL context, its full draw_room signature, and every GL state call it makes (blend / depth)."
      - "Show me the verbatim field definitions of Floorplan, Corridor, Room, RoomRuntime, ViewMatrix, and the pitch-clamp constant."
      - "Show me render_wire.py's current vertex + fragment shaders and how vertices are fed to them."
  - Everything we paste is VERBATIM, never our paraphrase. If an excerpt looks like it's missing connective context (an import, a constant, a caller), SAY SO and we'll pull that too.
  - WHOLE-FILE fallback: only for a SMALL file you intend to rewrite end-to-end (e.g. render_wire.py is ~131 lines). For big files, ask questions — never request the whole file.

------------------------------------------------------------
6) DELIVERABLE
  - The corrected renderer(s): a frozen child brief, OR the corrected code directly (your call).
  - Plus a short "WHAT NIR SHOULD SEE ON SCREEN" acceptance note so the eyeball check is unambiguous (e.g. "Mode A: thick white lines up close, dimming smoothly to grey far, never pure black, soft glow; crossings clearly over/under. Mode B: a lit solid room with visible walls and panels — not black.").
  - DeepSeek integrates, keeps the 382 tests green, Nir eyeballs.

------------------------------------------------------------
7) IRON RULES
  - Design against VERBATIM code/contracts, never paraphrases.
  - Never assert GL/library function names from memory; lean on the run loop to confirm.
  - No Markdown tables in anything Nir must copy-paste.
  - Don't silently resolve a conflict with a locked decision — surface it to Nir.
  - Honesty: invent nothing; mark genuine gaps as gaps.

------------------------------------------------------------
8) HOW WE START (the rhythm)
Please do NOT start producing the fix yet. First, reply with: (a) your understanding of this mission in your own words, and (b) your FIRST batch of precise questions (and/or a request for the small render_wire.py file if you want it whole). We'll answer with verbatim excerpts, you'll diagnose, you'll tell us your plan, we'll confirm — and only then do you build. Small confirmed steps; nothing runs ahead.

When you're ready, send your understanding and your first batch of questions.
