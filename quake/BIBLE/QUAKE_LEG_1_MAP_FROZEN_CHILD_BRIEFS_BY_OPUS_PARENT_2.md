🗝️ QUAKE (Game 3) — LEG 1 (THE MAP): FROZEN CHILD BRIEFS by Parent 2

Captured June 25, 2026, at Nir's request, VERBATIM / word-for-word, AS-IS. This is Parent 2 of Quake — Claude Opus 4.8, run ALONE (not Fusion), at "normal" reasoning effort — answering the forced missions in the Parent 2 handoff (`quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_2_HANDOFF.md`). This is Parent 2's first deliverable: Mission 1 (Leg 1 — THE MAP) frozen child briefs. Nothing below is edited.

--- BEGIN VERBATIM ---

I have everything. These contracts are clean, internally consistent, and they resolve every fork I flagged. I can now freeze Leg 1.

Before the package, three reconciliations the verbatim text just settled — stated so you can see I'm designing with the frozen contracts, not around them:

    citations_raw already has source: Literal["text","image"]. Parent 1 did anticipate the text-world fork — the schema carries the producer. And §3.A.2's validation says: "if source=='text', each non-vague phrase must actually be a substring of the OCR text for page_seen." That substring-guard is only meaningful for a deterministic text extractor — it's the hallucination guard for a script, not an AI. This confirms citation_extract.py is a real, intended module. I'm adding it.

    provenance.json lives under content/levels/<level_id>/ and is build-world only (§2.5 comment + §4.9 "must NOT appear under dist/"). So merge.py writes it next to concept_graph.json; the packaging check (a later leg) enforces the dist/ exclusion. Leg 1 just produces it.

    page_map_adapter.py IS a Leg-1 module. §4.1's locked commentary makes citation_extract depend on page_map (it slices _djvu.txt form-feed chunks 1:1 by leaf_index, and page_seen = label-or-[leaf N]). So the adapter must run before the citation extractor. It's in Leg 1's build order.

    edge_id regex differs subtly between §4.9 and §4.2/§2.1. §4.9 EdgeProvenance.edge_id = ^edge\.[a-z0-9_]+\.to\.[a-z0-9_]+$; §4.2 Edge.id = same. §2.1 says node_id = ^[a-z][a-z0-9_]*$ (must start with a letter), but the edge regex uses [a-z0-9_]+ (looser). I will not "fix" this — I freeze the regexes exactly as written. The node-id-start-letter rule is enforced where node ids are validated; the edge regex is deliberately the looser composite. Iron rule respected.

MISSION 1 — LEG 1 (THE MAP): FROZEN PACKAGE
§A — Revised pipeline (text-world)

page_map source (archive hOCR json)
   │
   ▼
[0] page_map_adapter.adapt()  ─ deterministic ─► page_map.json
   │
   ├─────────────────────────────────────────────┐
   ▼                                              │
[A] STRUCTURE PASS (AI)  ─► nodes_raw.json        │ page_map feeds [B]
   │                                              ▼
[B] CITATION EXTRACT (deterministic script over _djvu.txt) ─► citations_raw.json (source="text")
   │                                              
[B'] INFERENCE PASS (AI) ─► inference_raw.json    
   │                                              
   ▼
[C] MERGE (deterministic) ─► concept_graph.json + provenance.json
   │
   ▼
[D] SANITY (deterministic) ─► flags + graph_preview.png
   │
   ▼
[E] YOU LOOK (eyeball + provenance audit)  ──loop B/B'–E──┐
   │                                                       │
   ▼
[F] LAYOUT (deterministic given seed) ─► floorplan.json

Four safety nets — all intact in the text world:

    Provenance — every edge carries snippet+page (EdgeProvenance).
    Numbering-continuity — sanity.check flags gaps.
    Cycle/connectivity — sanity.check + the ConceptGraph DAG validation.
    Two-method disagreement — merge diffs citations_raw (now deterministic) against inference_raw (still AI). The deterministic citation side makes net 4 stronger, not weaker — one side is now hallucination-proof by the substring guard.

The AI now does exactly two reads: STRUCTURE (nodes_raw) and INFERENCE (inference_raw). Citation transcription is deterministic. This is the win the clean text bought us.
§B — Module set (the frozen list of Leg-1 children)

map/raw_models.py        define all pydantic models (the contracts, verbatim)
map/page_map_adapter.py  hOCR json → PageMap            [NEW — locked §4.1 brief]
map/citation_extract.py  _djvu.txt + PageMap → CitationsRaw(source="text")   [NEW]
map/citation_normalize.py  phrase → NodeId|None
map/merge.py             (nodes_raw, citations_raw, inference_raw) → (ConceptGraph, Provenance)
map/sanity.py            check(graph,prov) → flags ; render_preview(graph,prov,png)
map/layout_force.py      place_nodes(graph, seed, cfg) → positions
map/layout_height.py     detect_crossings(...) ; assign_heights(...)
map/level_maker.py       build_floorplan(graph, seed, cfg) → Floorplan  (orchestrates force+height)

Nine modules. raw_models.py is the shared types file all others import (the OT §12.2 "communicate only through contracts.py" rule — here scoped as map/raw_models.py for Leg 1; DeepSeek may physically place these in the global contracts.py — that's an integration choice, the signatures are what I freeze).
§C — FROZEN CHILD BRIEFS

    Anti-regression clause (applies to every brief below): Tests must pass on these exact fixtures, byte-for-byte where the brief gives exact output. A change to any frozen signature is an Architect-gated event and bumps a contract version. extra="forbid" everywhere; schema_version asserted on load.

    Global type aliases (defined once in raw_models.py, referenced by all):
    NodeId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]
    LevelId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]
    PageLabel = str (printed label; may be "")
    Vec2 = tuple[float, float]
    Hex = Annotated[str, Field(pattern=r"^#[0-9a-fA-F]{6}$")]
    (If the Second Canon already defines these aliases elsewhere, use those verbatim — DeepSeek, confirm; do not redefine if they exist.)

C1 — map/raw_models.py

Purpose: the single source of types for Leg 1. No logic, only models + aliases + SCHEMA_VERSION = "1.0".

Frozen — define EXACTLY these classes (copy the §3.A.1, §3.A.2, §3.A.3, §4.1, §4.2, §4.4, §4.9 bodies verbatim):

    Aliases: NodeId, LevelId, PageLabel, Vec2, Hex (above).
    RawNode, NodesRaw (§3.A.1)
    RawCitation, RawCiteItem, CitationsRaw (§3.A.2)
    RawInferEdge, InferenceRaw (§3.A.3)
    PageEntry, PageMap (§4.1)
    Node, Edge, ConceptGraph (§4.2)
    FloorRoom, Corridor, Crossing, Floorplan (§4.4)
    EdgeProvenance, Provenance (§4.9)
    A loader helper: load_json(path, model) -> model that asserts obj["schema_version"] == SCHEMA_VERSION before parsing, raising SchemaVersionError(path, found, expected) on mismatch (§2.2).

Contract: pure types + one loader. No IO beyond load_json. No network.

Tests (golden round-trip): for each of the §3/§4 example JSON blobs given verbatim above, assert Model.model_validate_json(blob) succeeds and .model_dump() round-trips. Assert extra="forbid" rejects an injected unknown field. Assert load_json raises SchemaVersionError when schema_version="0.9".

Anti-regression: the verbatim example blobs (law_2/prop_1/lemma_1 for nodes_raw, the prop_1→law_2 graph, the provenance two-edge example, the page_map leaf_index:74,label:"55" example) are the frozen fixtures.
C2 — map/page_map_adapter.py

Frozen signature: def adapt(hocr_pages: dict, pack_id: str, image_dir: str | None) -> PageMap

Behavior (verbatim from the locked §4.1 commentary): assert hocr_pages["format-version"] == "2" (else ValueError naming the found value). Per page: leaf_index = leafNum - 1; page_label = pageNumber verbatim (incl. ""); image_path = f"{image_dir}/leaf_{leafNum:04d}.png" if image_dir else None. Sort by leaf_index asc; assert contiguity-from-0 (raise naming the missing index). schema_version="1.0", pack_id=pack_id. Pure function, no IO/network. (Note: the commentary says image_path "if present must exist on disk" — but adapt is pure; the disk-existence check belongs to a downstream IO validator, NOT to adapt. Freeze adapt as pure.)

Tests (the four locked cases, verbatim):

    leafNum 1..5, pageNumber ["","","","41","42"] → leaf_index 0..4, two empty labels allowed, 41/42 unique, image_path = leaf_0004.png/leaf_0005.png for the last two.
    format-version "1" → raises.
    leafNum (1,2,4) → raises naming index 2.
    duplicate non-empty pageNumber → raises; duplicate "" → passes.

C3 — map/citation_extract.py

Frozen signature:
def extract(djvu_text: str, page_map: PageMap, level_id: LevelId, node_labels: list[str]) -> CitationsRaw

where djvu_text is the raw _djvu.txt (form-feed \x0c-delimited, one chunk per leaf, 1:1 with page_map.pages by leaf_index), and node_labels is the list of RawNode.local_label strings from nodes_raw (so the extractor knows which item "owns" the citing text).

Behavior:

    Split djvu_text on \x0c into leaf chunks; assert chunk count == len(page_map.pages) (raise naming the mismatch).
    For each leaf chunk, regex-scan for cross-reference phrases. The phrase grammar is a frozen, pinned regex set (see below). Each match yields RawCitation(phrase=<verbatim matched substring>, page_seen=<label-or-"[leaf N]">, vague=<bool>).
    page_seen = the leaf's page_label if non-empty, else "[leaf {leaf_index}]" (locked §4.1 rule).
    Attribute each citation to the owning local_label: an item "owns" the text from where its label-heading appears in the chunk(s) until the next item's heading (a deterministic sectioning pass — frozen as: scan chunks in leaf order, maintain a "current owner" = the most recent node_label heading seen).
    Set source="text".
    Substring guard (the hallucination-proofing): by construction every phrase is a literal substring of its leaf chunk — assert it (a regression guard, since we matched it from that chunk).
    vague=True for the pinned vague set ("as shown above", "as was demonstrated above", "by what was demonstrated", "above").

Frozen vague + citation regex set (pinned — children must use exactly this, extend only via Architect-gated bump):

CITE_PATTERNS = [
  r"by\s+(the\s+)?(first|second|third|fourth|fifth|[IVXLC]+)\s+Law(\s+of\s+Motion)?",
  r"by\s+(Lem\.|Lemma)\s+[IVXLC]+",
  r"by\s+(Prop\.|Proposition)\s+[IVXLC]+",
  r"by\s+(Cor\.|Corollary)\s+\d+\.?\s*(Prop\.|Proposition)?\s*[IVXLC]*",
  r"by\s+(Def\.|Definition)\s+[IVXLC]+",
  r"(per|by)\s+Cor\.\s*\d+\.?\s*of\s+the\s+Laws",
]
VAGUE_PATTERNS = [
  r"as\s+(was\s+)?(shown|demonstrated)\s+above",
  r"by\s+what\s+was\s+demonstrated",
  r"\babove\b",   # only when not part of a resolved citation
]

(DeepSeek: these are seed patterns derived from the §3.A.2 examples and Newton's house style. Treat them as v1.0 frozen; real _djvu.txt will surface more — each addition is an Architect-gated bump, NOT a silent edit. The substring guard makes false positives auditable, and citation_normalize returning None makes unmatched phrases harmless.)

Contract: pure function, deterministic, no IO/network.

Tests (golden):

    Fixture chunk: "...PROP. I. THEOREM I. ... by the first Law of Motion ... by Cor. 1. of the Laws ... as was demonstrated above ..." with a 1-leaf page_map (page_label="55") → produces a CitationsRaw whose single RawCiteItem(local_label="Prop. I. Theorem I.") has exactly the three citations from the §3.A.2 example, with the third vague=True. This reproduces the §3.A.2 verbatim example output.
    Empty-label leaf (page_label="", leaf_index=2) with a citation → page_seen="[leaf 2]".
    Chunk-count mismatch → raises.

C4 — map/citation_normalize.py

Frozen signature: def normalize(phrase: str, label_index: "LabelIndex") -> NodeId | None
where LabelIndex is a frozen lookup built from nodes_raw:
LabelIndex = dict[str, NodeId] mapping a normalized lookup key (e.g. "lemma 1", "prop 11", "law 2", "cor 2 prop 4") → the node's proposed_id. Provide def build_index(nodes_raw: NodesRaw) -> LabelIndex.

Behavior: parse the verbatim phrase, handle: Roman numerals (I..C), abbreviations (Lem./Lemma, Prop./Proposition, Cor./Corollary, Def./Definition, Law), spelled-out ordinals for laws (first/second/third → 1/2/3), compound refs (Cor. 2. Prop. IV → target prop_4, with the corollary recorded as a returned tag/side-channel — see note), and "of this Book" (ignored — same book). Return the target NodeId or None (for vague/unresolvable). Vague phrases → None.

Note on compound Cor. N. Prop. M: the §1.7 original said "return the target node id (and records the corollary as a tag)." Since the frozen signature returns NodeId | None, the corollary-tag is not a return value here — the edge target is the proposition (prop_4). If corollaries are themselves nodes (e.g. cor_2_prop_4 per §2.1's example), then normalize returns cor_2_prop_4 iff that id exists in label_index, else falls back to prop_4. Frozen rule: prefer the most-specific id present in label_index; else the parent.

Contract: pure, deterministic, no IO.

Tests (the ~40-phrase table — frozen fixture): a table of Principia-style phrases → expected ids, including at minimum:

"by the first Law of Motion"     -> "law_1"
"by the second Law"              -> "law_2"
"by Lem. I"                      -> "lemma_1"
"by Lemma VII"                   -> "lemma_7"
"by Prop. XI of this Book"       -> "prop_11"
"by Cor. 2. Prop. IV"            -> "prop_4"   (or "cor_2_prop_4" if present)
"by Cor. 1. of the Laws"         -> "law_1"    (frozen: "of the Laws" → law_<n>)
"by Def. III"                    -> "def_3"
"as was demonstrated above"      -> None
"above"                          -> None
<...assembled to ~40 against a fixed label_index...>

DeepSeek: build the full 40-row table from the patterns above; each row is a frozen assertion. The label_index for the test fixture is pinned (laws 1–3, lemmas 1–11, props 1–11, defs 1–8, plus cor_2_prop_4).
C5 — map/merge.py

Frozen signature:
def merge(nodes_raw: NodesRaw, citations_raw: CitationsRaw, inference_raw: InferenceRaw, cfg: "MergeConfig") -> tuple[ConceptGraph, Provenance]

where MergeConfig carries the locked importance weights:

class MergeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    importance_w_indeg: float = 0.6
    importance_w_hint: float = 0.4

(These two fields are the BuildConfig importance fields per the §1.4 lock. DeepSeek: if a global BuildConfig already declares them, MergeConfig is a view onto those — do not duplicate-decide the values.)

Behavior (deterministic, fully golden-testable):

    Nodes: from nodes_raw.nodes, build Nodes. Enforce global proposed_id uniqueness (raise on dup, naming it). Carry name=local_label, kind, pages, summary, tags=[] initially, importance filled in step 5.
    Build LabelIndex via citation_normalize.build_index(nodes_raw).
    Citation edges: for each RawCiteItem → owner node (resolve local_label→id via LabelIndex; raise if owner unknown). For each RawCitation, normalize(phrase) → target id or None. On a real target ≠ owner: create/merge an Edge(id=f"edge.{src}.to.{tgt}", source=src, target=tgt, label=phrase). Self-loops forbidden (skip + flag). Record an EdgeProvenance(provenance="cited", snippet=<the phrase in context — frozen as the verbatim phrase>, page_seen=<citation.page_seen>, vague=<citation.vague>, reason="").
    3a. snippet rule (frozen): in the text world the verbatim phrase is the snippet (we have no wider window guaranteed). snippet = phrase. (If a future text-window extractor supplies context, the snippet may widen — Architect-gated.)
    Inference edges: for each RawInferEdge, resolve both labels → ids (raise if unknown), forbid self-edges. If an edge already exists from citation → set its provenance agreement="both" (keep provenance="cited"). If it does not exist → add a new Edge AND an EdgeProvenance(provenance="inferred", snippet="", page_seen=None, reason=<RawInferEdge.reason>, agreement="inference_only"). For citation edges with no inference match → agreement="citation_only".
    Importance (LOCKED formula — NOT quantiles):
    deg_norm=max(1, max_indeg)indeg​,hint_norm=4hint−1​
    score=windeg​⋅deg_norm+whint​⋅hint_norm,importance=clamp(round(1+4⋅score), 1, 5)
    indeg = number of edges targeting this node (in-degree). hint = RawNode.importance_hint. Apply per node.
    Emit: ConceptGraph(schema_version="1.0", level_id, title=?, edition=nodes_raw.edition, seed=?, nodes, edges) and Provenance(schema_version="1.0", level_id, edges=<all EdgeProvenance>, flags=[]) (flags filled by sanity, not here — merge leaves flags=[]).
        title and seed: these are NOT in nodes_raw. Frozen rule: merge takes them from cfg (add title: str and seed: int to MergeConfig), OR seed defaults and title from nodes_raw? — Resolution: add title: str and seed: int to MergeConfig. They originate in the level's build config, not the AI passes. (DeepSeek: confirm BuildConfig/level config supplies these.)

Edge ordering (determinism): emit nodes sorted by id; emit edges sorted by (source, target); emit EdgeProvenance in the same order as edges, 1:1. This makes output byte-stable.

Contract: pure, deterministic, no IO/network.

Tests (exact golden):

    Fixture: nodes_raw = the §3.A.1 verbatim example (law_2, lemma_1, prop_1). citations_raw = the §3.A.2 verbatim example (prop_1 cites "by the first Law of Motion"→law_1 — but law_1 not in nodes! see note). inference_raw = the §3.A.3 verbatim example (prop_1→Law II, prop_1→Lemma I).
    Note (a deliberate teaching fixture): the §3.A.2 example cites law_1 which is absent from the §3.A.1 example nodes. Frozen behavior: an unresolved/absent target → normalize returns the id, but merge finds no such node → edge is dropped + a flag-worthy event (but merge leaves flags to sanity; merge instead simply does not emit the edge, and this is caught by sanity's connectivity check). (This is realistic: it's exactly the "missing item" the safety nets exist for.) The reliable golden assertion: prop_1→law_2 appears as agreement="both" (citation "by the second Law" + inference "Law II"), prop_1→lemma_1 appears as inferred / inference_only (matching the §4.9 verbatim example's two edges exactly).
    Therefore the frozen expected output IS the §4.9 verbatim example (the two-edge provenance) plus the matching concept_graph (the §4.2 verbatim prop_1→law_2 edge + the inferred prop_1→lemma_1 edge). Assert importance: with these in-degrees, compute via the locked formula and pin the integer results.
    Self-loop in inference → skipped.
    Unknown owner label → raises.

C6 — map/sanity.py

Frozen signatures:
def check(graph: ConceptGraph, provenance: Provenance, expected_runs: dict[str, list[int]] | None = None) -> list[str]
def render_preview(graph: ConceptGraph, provenance: Provenance, out_png: Path) -> None

check behavior (returns plain-English flag strings; these get written into Provenance.flags by the orchestrator):

    Numbering-continuity: group nodes by kind, parse the numeric index from each id (e.g. lemma_7→7). For each kind, expect contiguous 1..max; report gaps: "MISSING_ITEM: lemma_7 expected (have lemma_1..lemma_6, lemma_8), check the page". expected_runs optionally pins the expected max per kind (e.g. {"lemma":[1..11]}); if None, infer from observed max.
    Cycle detection: the graph must be a DAG. Report each cycle: "CYCLE: lemma_3 -> prop_2 -> lemma_3 — likely a misread citation; check these pages".
    Orphans: nodes with degree 0: "ORPHAN: def_5 has no edges".
    Connectivity/islands: count weakly-connected components: "ISLANDS: 2 components — a section-bridging citation may be missing" (or "ISLANDS: 1 component (ok)" per the §4.9 example flag).
    Provenance scrutiny: count agreement buckets; "SCRUTINY: 3 inference_only edges (shown dashed) — confirm against the page".

render_preview behavior: draw with networkx + matplotlib (build-only deps, OT §11). Node size & color ∝ importance (use palette.map_importance[1..5] if a palette is passed; else a fixed dev ramp). Inferred / inference_only edges dashed; cited solid. Label nodes by name. Write a labelled PNG. No assertion on pixel output (rendering is not byte-stable) — this function is smoke-tested only.

Contract: check is pure & deterministic (golden-testable). render_preview does IO (writes PNG) and is display-free (Agg backend) — tested only for "produces a non-empty file without raising."

Tests (exact golden for check):

    A graph with a planted cycle lemma_3→prop_2→lemma_3 → flags contain the exact CYCLE: string.
    A graph missing lemma_7 (have 1–6, 8) → exact MISSING_ITEM: string.
    A graph with a disconnected def_5 (degree 0) → ORPHAN: string.
    Two components → ISLANDS: 2 components....
    The §4.9 example graph (1 component) → "ISLANDS: 1 component (ok)".
    render_preview on the small fixture → file exists, size > 0, no exception (skip gracefully if matplotlib Agg unavailable).

C7 — map/layout_force.py

Frozen signature: def place_nodes(graph: ConceptGraph, seed: int, cfg: "LayoutConfig") -> dict[NodeId, Vec2]

class LayoutConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scale_m: float = 40.0     # world half-extent in meters
    iterations: int = 200     # spring_layout iterations

Behavior: (1) canonicalize: sort node ids and edges before building the networkx graph (OT §8.1 — order-independent). (2) networkx.spring_layout(G, seed=seed, iterations=cfg.iterations) → unit positions. (3) scale to world XZ by cfg.scale_m. Return {node_id: (x, z)}.

THE DETERMINISM CAVEAT (OT R10, §8.1, §16 — LOCKED DOCTRINE): spring_layout is NOT guaranteed bit-identical across NumPy/BLAS/platforms. We lay out once on the build machine and ship floorplan.json. Therefore:

Tests — INVARIANT-based, NOT exact-coordinate (this is the deliberate exception to "exact golden"):

    Determinism on this machine: place_nodes(g, 1729001, cfg) called twice → identical dict (same-process determinism IS guaranteed by the fixed seed).
    Completeness: every node id present exactly once; no extras.
    Finiteness/bounds: all coords finite, within [-scale_m, +scale_m].
    Order-independence: shuffling graph.nodes/graph.edges input order → identical output (proves the canonicalization works). This is the strong, portable golden test — it doesn't depend on BLAS, only on our canonical-sort correctness.
    DO NOT assert exact float coordinates against a cross-machine golden.

C8 — map/layout_height.py

Frozen signatures:
def detect_crossings(positions: dict[NodeId, Vec2], graph: ConceptGraph, cfg: "HeightConfig") -> list[tuple[str, str, Vec2]] (corridor_id pairs + intersection point)
def assign_heights(crossings: list[tuple[str,str,Vec2]], graph: ConceptGraph, cfg: "HeightConfig") -> dict[str, int] (corridor_id → height_level)

class HeightConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    socket_clearance_m: float = 2.0   # ignore intersections nearer than this to a node
    layer_warn: int = 7
    layer_fail: int = 12
    base_y: float = 0.0
    delta_y: float = 3.0

detect_crossings (deterministic): for every pair of edges (in canonical (source,target) order), 2D segment-intersection test on their endpoint positions. Ignore shared endpoints; ignore intersections within socket_clearance_m of any node. On a too-close-to-socket intersection, first attempt a deterministic local dogleg (frozen: not auto-resolved here — return it flagged); if unresolvable, the orchestrator fails loud naming the offending corridor ids. Return crossings sorted canonically.

assign_heights (deterministic greedy coloring — OT §8.1 verbatim algorithm): build conflict graph H (vertex per corridor, edge per crossing). Process corridors in fixed order: weight desc, then source id, then target id. Assign each the lowest layer not used by an already-assigned crossing-neighbor. Layer→y = base_y + layer*delta_y. Warn if max_layer > layer_warn; raise if > layer_fail (message: "re-seed N or widen scale").

Contract: both pure & fully deterministic (integer/id-ordered) — exact golden tests.

Tests (exact golden):

    The canonical 4-node-one-crossing fixture: nodes a,b,c,d at positions making edges edge.a.to.c and edge.b.to.d cross at the center. detect_crossings → exactly one crossing of those two corridors. assign_heights → the two crossing corridors get different height_level (one 0, one 1, by the fixed order). Assert exact {corridor_id: level} dict.
    A no-crossing graph → empty crossings, all heights 0.
    A 3-mutually-crossing set → 3 distinct layers (or per greedy: assert exact dict).
    A fixture forcing >12 layers → raises with the re-seed message.
    Intersection within socket_clearance_m of a node → returned flagged (not silently dropped).

C9 — map/level_maker.py

Frozen signature: def build_floorplan(graph: ConceptGraph, seed: int, cfg: "LevelMakerConfig") -> Floorplan

class LevelMakerConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    layout: LayoutConfig = LayoutConfig()
    height: HeightConfig = HeightConfig()
    map_radius_base_m: float = 2.0
    map_radius_per_importance_m: float = 1.0   # radius = base + (importance-1)*per
    corridor_width_m: float = 3.0
    palette_map_importance: dict[int, Hex]     # {1:..,5:..} → FloorRoom.map_color

Behavior (orchestration — calls C7, C8):

    positions = place_nodes(graph, seed, cfg.layout).
    crossings = detect_crossings(positions, graph, cfg.height); on a socket-conflict flagged crossing → fail loud naming the corridor ids (OT §8.1 "else fail loudly with the offending ids").
    heights = assign_heights(crossings, graph, cfg.height).
    Build FloorRoom per node: room_id=node.id, map_xz=positions[id], importance=node.importance, map_radius_m = base + (importance-1)*per, map_color = cfg.palette_map_importance[importance], socket_y=0.0.
    Build Corridor per edge: corridor_id=edge.id, endpoints, height_level=heights[edge.id], cruise_y=base_y+level*delta_y, path_xz=[src_xz, ...ramp knees..., tgt_xz] (frozen: straight [src, tgt] if level==0; insert two ramp-knee points near each crossing if level>0 — exact knee rule pinned: knee at socket_clearance_m before/after the crossing point, raised to cruise_y), width_m=cfg.corridor_width_m.
    Build Crossing per detected crossing: crossing_id=f"x.{over}.{under}", over_corridor/under_corridor = the higher-level corridor over the lower (tie broken by the same fixed order), at_xz=intersection, over_y/under_y from their levels (assert over_y > under_y, §4.4 validation).
    Emit Floorplan(schema_version="1.0", level_id=graph.level_id, seed=seed, rooms, corridors, crossings).

Validation built in (§4.4): room_ids == graph node ids (spine); corridor endpoints exist; every crossing over_y > under_y; height_level ≤ layer_fail.

Contract: deterministic given positions (so the height/room/corridor/crossing assembly is exact-golden-testable by feeding fixed positions); the full build_floorplan inherits place_nodes's machine-dependence, so its end-to-end test is invariant-based.

Tests:

    Exact-golden (fixed positions path): factor the assembly so steps 2–7 are testable with injected fixed positions (the 4-node-one-crossing fixture from C8). Assert the exact Floorplan: 4 rooms with computed radii/colors, 2 corridors at levels {0,1}, 1 crossing with over_y>under_y, the over/under chosen by fixed order. This is the headline anti-regression fixture (it proves "crossings become bridges").
    Invariant (full path): build_floorplan(graph, seed, cfg) twice → identical (same-process); spine equality holds; all §4.4 validations pass.
    A graph that overflows layers → raises with the re-seed message.

§D — LEG-1 BUILD ORDER + TEST PLAN

1. map/raw_models.py        ← everything imports this. Build & test FIRST.
2. map/page_map_adapter.py  ← depends only on raw_models. (parallel-ok with 3,4)
3. map/citation_normalize.py← depends only on raw_models. (the 40-phrase table)
4. map/citation_extract.py  ← depends on raw_models + page_map (from 2).
5. map/merge.py             ← depends on raw_models + citation_normalize (3).
6. map/sanity.py            ← depends on raw_models. (check is pure; preview smoke)
7. map/layout_height.py     ← depends on raw_models. (exact-golden core)
8. map/layout_force.py      ← depends on raw_models + networkx. (invariant-tested)
9. map/level_maker.py       ← depends on 7,8. The orchestrator. Build LAST.

Why this order: types first (1); the three leaf-pure modules (2,3) unblock the two consumers (4,5); the safety net (6) and the deterministic height core (7) are independent; the fragile force module (8) before the orchestrator (9) that needs both layout pieces.

Per-module (unit, the frozen fixtures above): each module's golden tests pass byte-for-byte (exact) except layout_force + the full build_floorplan path (invariant + same-process determinism only).

Integration (the Leg-1 golden mini-level): wire a tiny end-to-end fixture (no AI, no network):

    A pinned page_map (3 leaves), a pinned _djvu.txt (3 form-feed chunks) → citation_extract → citations_raw.
    A pinned nodes_raw (e.g. law_1, law_2, lemma_1, prop_1) + pinned inference_raw.
    merge → concept_graph + provenance; assert: DAG, spine, importance integers (locked formula), the agreement buckets match expectation.
    sanity.check → assert the expected flags (clean: ISLANDS: 1 component (ok)).
    level_maker.build_floorplan (same-process) → a valid Floorplan passing all §4.4 validations, with ≥1 crossing → ≥1 bridge.

The acceptance gate (maps to OT M2 "Deterministic floorplan"): the integration fixture produces a floorplan.json that the (future) M2 viewer can render with crossings as over/under. Leg 1 is DONE when: all unit goldens pass, the integration fixture is green, and floorplan.json validates against Floorplan with the spine intact.
§E — Open items I'm flagging (NOT blockers — for your awareness)

    title + seed origin for merge/level_maker. I routed them through config. Confirm the level's BuildConfig (Second Canon §4.8) is their home — if §4.8 already defines level_id/title/seed, wire from there rather than MergeConfig. (I did not request §4.8 — it's not a Leg-1 contract I write to, only read. If it conflicts, tell me and I'll align.)
    Type-alias home. I defined NodeId/LevelId/PageLabel/Vec2/Hex in raw_models.py. If the Second Canon §2 already declares these globally (it references PageLabel, Vec2, Hex, LevelId, NodeId in the verbatim text), use the global ones — raw_models.py imports, not redefines. This is an integration placement, not a contract change.
    The CITE_PATTERNS seed set will grow when real _djvu.txt is processed. I've frozen v1.0 + the Architect-gated-bump rule. The substring guard + normalize→None make over/under-matching safe and auditable, so growth is low-risk.

Mission 1 / Leg 1 is frozen. Nine child briefs, exact signatures against the verbatim §3/§4 contracts, golden fixtures with the determinism caveat handled exactly per OT doctrine, a dependency-sorted build order, and an acceptance gate mapped to M2.

When you're ready, send the Leg-2 (WALLS) verbatim sections I'll need — but per your forced order, only after you confirm Leg 1 is in DeepSeek's hands. I'll hold here. 🗝️

--- END VERBATIM ---
