"""Deterministic merge engine.

Consumes STRUCTURE (nodes), CITATION, and INFERENCE passes and produces a
ConceptGraph + Provenance. Pure function, deterministic, no IO/network.
"""

from map.raw_models import (
    NodesRaw,
    CitationsRaw,
    InferenceRaw,
    MergeConfig,
    ConceptGraph,
    Node,
    Edge,
    Provenance,
    EdgeProvenance,
)
from map.citation_normalize import normalize, build_index, LabelIndex


def _clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


def merge(
    nodes_raw: NodesRaw,
    citations_raw: CitationsRaw,
    inference_raw: InferenceRaw,
    cfg: MergeConfig,
) -> tuple[ConceptGraph, Provenance]:
    # ── STEP 1 — NODES ──────────────────────────────────────────────
    nodes: list[Node] = []
    seen_ids: set[str] = set()
    raw_by_id: dict = {}
    id_by_local_label: dict[str, str] = {}

    for raw in nodes_raw.nodes:
        if raw.proposed_id in seen_ids:
            raise ValueError(f"Duplicate proposed_id: {raw.proposed_id}")
        seen_ids.add(raw.proposed_id)
        raw_by_id[raw.proposed_id] = raw
        id_by_local_label[raw.local_label] = raw.proposed_id

        nodes.append(
            Node(
                id=raw.proposed_id,
                name=raw.local_label,
                kind=raw.kind,
                pages=raw.pages,
                summary=raw.summary,
                tags=[],
                importance=1,  # filled in step 5
            )
        )

    nodes.sort(key=lambda n: n.id)

    # ── STEP 2 — LABEL INDEX ────────────────────────────────────────
    label_index: LabelIndex = build_index(nodes_raw)

    # ── STEP 3 — CITATION EDGES ─────────────────────────────────────
    # Keyed by (source, target) preserving first-seen iteration order.
    edges_by_key: dict[tuple[str, str], Edge] = {}
    prov_by_key: dict[tuple[str, str], EdgeProvenance] = {}

    for item in citations_raw.items:
        owner_id = None
        for n in nodes_raw.nodes:
            if n.local_label == item.local_label:
                owner_id = n.proposed_id
                break
        if owner_id is None:
            raise ValueError(f"Unknown owner label: {item.local_label}")

        for citation in item.citations:
            target_id = normalize(citation.phrase, label_index)
            if target_id is None:
                continue
            if target_id == owner_id:
                continue
            if target_id not in seen_ids:
                continue

            key = (owner_id, target_id)
            if key in edges_by_key:
                # dedup: keep first citation's data
                continue

            edge_id = f"edge.{owner_id}.to.{target_id}"
            edges_by_key[key] = Edge(
                id=edge_id,
                source=owner_id,
                target=target_id,
                kind="depends_on",
                weight=1.0,
                label=citation.phrase,
            )
            prov_by_key[key] = EdgeProvenance(
                edge_id=edge_id,
                provenance="cited",
                snippet=citation.phrase,
                page_seen=citation.page_seen,
                agreement="citation_only",
                reason="",
                vague=citation.vague,
            )

    # ── STEP 4 — INFERENCE EDGES ────────────────────────────────────
    for ie in inference_raw.edges:
        source_id = normalize(ie.source_label, label_index)
        if source_id is None:
            raise ValueError(f"Unknown inference source label: {ie.source_label}")
        target_id = normalize(ie.target_label, label_index)
        if target_id is None:
            raise ValueError(f"Unknown inference target label: {ie.target_label}")

        if source_id == target_id:
            continue

        key = (source_id, target_id)
        if key in edges_by_key:
            # cited edge already exists → upgrade agreement to "both"
            prov_by_key[key].agreement = "both"
            continue

        edge_id = f"edge.{source_id}.to.{target_id}"
        edges_by_key[key] = Edge(
            id=edge_id,
            source=source_id,
            target=target_id,
            kind="depends_on",
            weight=1.0,
            label="",
        )
        prov_by_key[key] = EdgeProvenance(
            edge_id=edge_id,
            provenance="inferred",
            snippet="",
            page_seen=None,
            agreement="inference_only",
            reason=ie.reason,
            vague=False,
        )

    # ── STEP 5 — IMPORTANCE ─────────────────────────────────────────
    indeg: dict[str, int] = {nid: 0 for nid in seen_ids}
    for (src, tgt) in edges_by_key:
        indeg[tgt] = indeg.get(tgt, 0) + 1

    max_indeg = max(1, max(indeg.values())) if indeg else 1

    for node in nodes:
        hint = raw_by_id[node.id].importance_hint
        deg_norm = indeg.get(node.id, 0) / max_indeg
        hint_norm = (hint - 1) / 4
        score = cfg.importance_w_indeg * deg_norm + cfg.importance_w_hint * hint_norm
        node.importance = _clamp(round(1 + 4 * score), 1, 5)

    # ── STEP 6 — EMIT ───────────────────────────────────────────────
    sorted_keys = sorted(edges_by_key.keys())
    edges = [edges_by_key[k] for k in sorted_keys]
    edge_provs = [prov_by_key[k] for k in sorted_keys]

    graph = ConceptGraph(
        schema_version="1.0",
        level_id=nodes_raw.level_id,
        title=cfg.title,
        edition=nodes_raw.edition,
        seed=cfg.seed,
        nodes=nodes,
        edges=edges,
    )
    prov = Provenance(
        schema_version="1.0",
        level_id=nodes_raw.level_id,
        edges=edge_provs,
        flags=[],
    )

    return graph, prov
