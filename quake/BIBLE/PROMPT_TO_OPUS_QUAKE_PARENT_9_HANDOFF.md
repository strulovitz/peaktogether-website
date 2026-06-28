# 🔥 PROMPT TO OPUS — QUAKE PARENT 9: Non-Planar Principia Graph

> DeepSeek-authored. Self-contained. The ONE file Nir pastes after Commentaries + OT + NT.

---

## ⚠️ CRITICAL — HOW YOU GET INFORMATION

You (Parent 9, inside OpenRouter) have NO internet, NO GitHub access, NO file system. Everything you know comes from what Nir pastes into this chat.

When you need more information:

    "Nir, please ask DeepSeek to fetch [specific file / section / snippet]."

Nir copies your request → pastes to DeepSeek → DeepSeek reads the file from disk → returns the verbatim content → Nir pastes it to you.

Do NOT try to browse URLs, read files yourself, or guess external content. Just ask. The material-request protocol is:

    Parent asks Nir → Nir asks DeepSeek → DeepSeek fetches → Nir pastes to Parent

---

## §1 — THE PROBLEM (why Parent 9 exists)

Parent 7 designed a 20-node, 28-edge concept graph for Principia Book 1 Sections I–III. Engines were built (Parents 1–8, 382/382 tests green). Phase A ran: the graph is **planar** — spring_layout finds a flat 2D arrangement with **0 crossings**.

0 crossings = **Doom, not Quake.**

The whole reason Quake is true-3D is the §1 invariant: "corridors cross at different heights as bridges/underpasses — that's WHY it must be true 3D." A planar graph defeats the entire premise. The engine is NOT the problem (it's robust, scale-free, all tests green). The graph topology is the problem.

### Why it's planar

Parent 7 selected 20 nodes from Sections I–III. The graph has 28 edges. Average degree = 2.8. A graph this sparse is almost always planar. Spring_layout, by design, finds planar embeddings when they exist. And they exist here because the topology doesn't contain a K5 or K3,3 subgraph (the two minimal non-planar patterns).

### What DeepSeek found in the actual Principia text

DeepSeek searched the full Principia text for real citations between the 20 nodes. Result: **24 real, verifiable citations** exist in the text. But several key edges Parent 7 included are NOT real citations, and several real citations were excluded. Furthermore, **lemma_1** — the most-cited lemma in Section I (cited by lemma_2, lemma_11, and others) — was not even included as a node by Parent 7.

The 24 real citation edges found in the text are:

```
(lemma_2  → lemma_1)    ← lemma_1 NOT in graph!
(lemma_4  → lemma_3)
(lemma_6  → lemma_5)
(lemma_7  → lemma_6)
(lemma_9  → lemma_5)
(lemma_10 → lemma_9)
(lemma_11 → lemma_1)    ← lemma_1 NOT in graph!
(prop_1   → law_1)
(prop_1   → lemma_5)    ← Parent 7 missed this
(prop_2   → law_1)
(prop_2   → law_2)      ← Parent 7 missed this
(prop_4   → lemma_7)
(prop_4   → prop_2)     ← Parent 7 missed this
(prop_4   → prop_1)     ← Parent 7 missed this
(prop_6   → lemma_2)    ← Parent 7 missed this
(prop_6   → lemma_10)
(prop_6   → prop_1)
(prop_7   → prop_6)
(prop_11  → lemma_7)
(prop_11  → lemma_12)
(prop_11  → prop_6)
(prop_11  → prop_7)     ← Parent 7 missed this
(prop_13  → lemma_7)
(prop_13  → prop_6)
```

### Cross-reference: what Parent 7 had vs. what's real

Parent 7 edges NOT supported by explicit text citations (may be logical/implicit dependencies):
- `edge.lemma_3.to.lemma_2` (no text citation found)
- `edge.lemma_4.to.lemma_2` (no text citation found)
- `edge.lemma_9.to.lemma_7` (no text citation found)
- `edge.lemma_11.to.lemma_6` (no text citation found)
- `edge.lemma_10.to.law_2` (no text citation found)
- `edge.prop_1.to.law_2` (no text citation found)
- `edge.prop_1.to.lemma_3` (no text citation found)
- `edge.prop_4.to.lemma_11` (no text citation found)
- `edge.prop_6.to.lemma_11` (no text citation found)
- `edge.prop_15.to.prop_11` (no text citation found)
- `edge.prop_15.to.prop_4` (no text citation found)

Real citations Parent 7 MISSED:
- `lemma_2 → lemma_1` (lemma_1 not in graph)
- `lemma_11 → lemma_1` (lemma_1 not in graph)
- `prop_1 → lemma_5`
- `prop_2 → law_2`
- `prop_4 → prop_2`
- `prop_4 → prop_1`
- `prop_6 → lemma_2`
- `prop_11 → prop_7`

---

## §2 — YOUR MISSION (Parent 9)

Redesign the Principia Book 1 Sections I–III concept graph so it is **non-planar**: mathematically impossible to draw flat, forcing NATURAL bridges and underpasses. Every edge must be a REAL citation from the actual Principia text.

### Hard constraints

1. **Every edge = a real citation from the text.** No invented edges, no "logical" edges, no "probably depends on." If Newton cites it, include it. If he doesn't, don't. This is a GAME about Newton's actual reasoning, not a math textbook reconstruction.

2. **Include lemma_1.** Lemma I is the most-cited lemma in Section I. Lemma II cites it. Lemma XI cites it twice. Excluding it was a mistake.

3. **The graph must be non-planar.** A non-planar graph is one that CANNOT be drawn on a 2D plane without edge crossings. The two minimal non-planar subgraphs are:
   - **K5** — 5 nodes, all connected to each other (10 edges)
   - **K3,3** — two groups of 3 nodes, every node in group A connected to every node in group B (9 edges)
   If your graph contains either as a subgraph, it is non-planar and WILL have unavoidable crossings. Target one of these patterns using real citations.

4. **NO hardcoded node/edge/crossing counts.** The graph size is whatever the real citations demand. If the genuine dense subgraph needs 15 nodes, use 15. If it needs 25, use 25. Don't target "about 20" — target non-planarity.

5. **All nodes must be from Book 1 Sections I, II, or III** of Newton's Principia (1729 Motte translation). These sections cover: the method of first and last ratios (Lemmas I–XI), centripetal forces (Props I–X including Lemma XII), and eccentric conic sections / inverse-square law (Props XI–XVII including Lemmas XIII–XIV).

6. **Use the EXACT node IDs** from Parent 7 where they exist (lemma_2, law_1, prop_1, etc.), and follow the same pattern for new ones (lemma_1, prop_3, etc.).

7. **Emil a valid DAG** — no cycles. Newton's citations are always forward (a lemma cites earlier lemmas, a proposition cites lemmas and earlier propositions).

8. **Keep the importance hints (1–5)** meaningful. The inverse-square law (prop_11) should be importance 5. The basic lemmas maybe 2–3. This affects room size and map color.

9. **Output format = valid `concept_graph.json`** conforming to the Second Canon §4.2. The schema is:
   - Node: id (pattern ^[a-z][a-z0-9_]*$), name, kind (lemma/law/proposition/corollary), importance (1–5), pages, summary, tags
   - Edge: id (pattern ^edge\.[a-z0-9_]+\.to\.[a-z0-9_]+$), source, target (both NodeId), kind ("depends_on"), weight (1.0), label (the citation phrase from the text)
   - `schema_version: "1.0"`, `extra: "forbid"`

### Deliverable

A single `concept_graph.json` — complete, valid per §4.2, non-planar, with every edge backed by a real Principia citation. Plus a brief explanation of:
- Which subgraph forces non-planarity (identify the K5 or K3,3)
- Which nodes are the "hubs" (degree 4+) that naturally create crossing congestion
- Any nodes you considered but excluded (and why)

---

## §3 — HOW TO GET MORE INFORMATION

You have three baseline items from Nir's initial paste:
- **The Commentaries** (BIBLE index + locked decisions)
- **The Old Testament** (Fusion's master doctrine)
- **The New Testament** (Opus's two-legs design)

### Additional materials you can request

You have this handoff already. You ALSO have the **DIGESTED PRINCIPIA** embedded in the combined Parent 7 handoff — it summarizes all 148 lemmas/props in one sentence each. If you haven't been pasted it yet, ask for: `quake/principia/DIGESTED_PRINCIPIA.md`

For the FULL text of specific sections (to verify citations):

```
quake/principia/book_1/section_01.txt  — Lemmas I–XI (first & last ratios)
quake/principia/book_1/section_02.txt  — Propositions I–X (centripetal forces)
quake/principia/book_1/section_03.txt  — Propositions XI–XVII (conic sections, inverse-square)
quake/principia/axioms/axioms_and_laws.txt  — Laws I–III + Corollaries
```

For the current (broken) graph to see what to fix: `quake/levels/principia_bk1_inverse_square/concept_graph.json`

For the exact data format contract: request the Second Canon §4.2 (ConceptGraph schema) from `quake/BIBLE/QUAKE_SECOND_CANON_FORMATS_AND_INTERFACES_BY_OPUS.md`

### Suggested workflow

1. Read the DIGEST to understand all available nodes in Sections I–III (~30 total lemmas + propositions + laws)
2. Ask for the full text of sections 01, 02, and 03 (ONE at a time to protect your context)
3. Extract EVERY citation from the text — build a complete dependency map
4. Identify the densest subgraph that contains a K5 or K3,3 pattern
5. Output the final `concept_graph.json`

### One gotcha to know

The text uses older citation language: "by Lem. I", "by Lemma 2.", "by the preceding lemma", "by prop. 2.", "by cor. 4. prop. 1." — you'll find these scattered through the proof paragraphs. "The preceding lemma" refers to the immediately prior lemma in the text order, NOT in our graph order. Be careful to resolve these to explicit IDs.

---

## §4 — ACCEPTANCE GATES

After you deliver, DeepSeek will:

**Gate 1:** Validate `concept_graph.json` against the frozen §4.2 schema (pydantic, NodeId patterns, Edge.id patterns, importance 1–5, no extra fields).

**Gate 2:** Verify every edge has a corresponding citation in the Principia text (DeepSeek will grep the text files).

**Gate 3:** Verify the graph is a valid DAG, weakly connected, no self-loops, no duplicate edges.

**Gate 4:** Prove non-planarity — DeepSeek will run a planarity test (networkx's `check_planarity`) and confirm it returns False. If it returns True, the graph is planar and the mission failed — we push back.

**Gate 5:** Run `build_floorplan` on the new graph with seed 1729001 and the default LayoutConfig (k_factor=1.0). The crossing count should be NATURALLY positive — at least 8–12 genuine crossings, emerging from the topology, not from seed-hunting or k_factor tricks.

**Gate 6:** Run the full 382-test suite — zero regressions (the new graph is just data; no engine should need changing).

---

## §5 — THE BIG PICTURE

Parent 7 gave us a good first draft — 20 real Newton propositions, valid DAG, genuine citations. But it was TOO SPARSE. A planar graph in a 3D Quake game is a category error. The entire OT §1 invariant — "crossings are a feature, corridors cross at different heights as bridges/underpasses" — depends on the graph being non-planar.

Your job is to fix that. Use Newton's own words. Make the graph dense enough that the topology itself demands bridges. No seed-hunting. No invented edges. Just real mathematical dependencies, faithfully represented, unavoidably tangled — because Newton's reasoning IS tangled, and a graph that captures it honestly will force crossings naturally.

The densest natural subgraph will likely center on:
- **Lemma I** (cited by lemma_2, lemma_11, and others)
- **Lemma VII** (cited by lemma_9? check the text; cited by prop_4, prop_11, prop_13)
- **Prop VI** (cited by prop_7, prop_11, prop_13 — it's the key formula for computing force laws)
- **Prop I** (cited by prop_4, prop_6 — the geometric proof of Kepler's Second Law)

These are the natural hubs. When you add ALL their real citations (incoming AND outgoing), you'll likely find a K3,3 or K5 lurking in the genuine dependency structure.

Go read the text. Find the real connections. Make it unavoidably 3D. 🗝️🔥
