import json

import pytest
from pydantic import ValidationError

from map.raw_models import (
    SCHEMA_VERSION,
    CitationsRaw,
    ConceptGraph,
    InferenceRaw,
    NodesRaw,
    PageMap,
    Provenance,
    SchemaVersionError,
    load_json,
)

NODES_RAW_BLOB = """{
  "schema_version": "1.0",
  "level_id": "principia_bk1_sec1",
  "edition": "Newton, Principia, trans. Andrew Motte, 1846 New York English ed.",
  "nodes": [
    {"local_label": "Law II", "proposed_id": "law_2", "kind": "law",
     "pages": ["19"], "summary": "Change of motion is proportional to the force impressed.",
     "importance_hint": 5},
    {"local_label": "Lemma I", "proposed_id": "lemma_1", "kind": "lemma",
     "pages": ["41"], "summary": "Quantities that tend to equality in a finite time become ultimately equal.",
     "importance_hint": 5},
    {"local_label": "Prop. I. Theorem I.", "proposed_id": "prop_1", "kind": "proposition",
     "pages": ["55","56"], "summary": "A body's radius to a fixed center sweeps equal areas in equal times.",
     "importance_hint": 5}
  ]
}"""

CITATIONS_RAW_BLOB = """{
  "schema_version": "1.0",
  "level_id": "principia_bk1_sec1",
  "source": "text",
  "items": [
    {"local_label": "Prop. I. Theorem I.",
     "summary": "Radii to a fixed center sweep equal areas in equal times.",
     "citations": [
        {"phrase": "by the first Law of Motion", "page_seen": "55", "vague": false},
        {"phrase": "by Cor. 1. of the Laws",     "page_seen": "55", "vague": false},
        {"phrase": "as was demonstrated above",   "page_seen": "56", "vague": true}
     ]}
  ]
}"""

INFERENCE_RAW_BLOB = """{
  "schema_version": "1.0",
  "level_id": "principia_bk1_sec1",
  "edges": [
    {"source_label": "Prop. I. Theorem I.", "target_label": "Law II",
     "reason": "The equal-area proof builds each impulse from the change-of-motion law."},
    {"source_label": "Prop. I. Theorem I.", "target_label": "Lemma I",
     "reason": "The polygon-to-curve limit uses ultimate-equality of vanishing triangles."}
  ]
}"""

PAGE_MAP_BLOB = """{
  "schema_version": "1.0",
  "pack_id": "principia",
  "pages": [
    {"page_label": "55", "leaf_index": 74, "image_path": "source/pages/leaf_0075.png"}
  ]
}"""

CONCEPT_GRAPH_BLOB = """{
  "schema_version": "1.0",
  "level_id": "principia_bk1_sec1",
  "title": "Book I, Section II",
  "edition": "Newton, Principia, trans. Motte, 1846",
  "seed": 1729001,
  "nodes": [
    {"id": "law_2", "name": "Law II", "kind": "law", "importance": 5,
     "pages": ["19"], "summary": "Change of motion is proportional to force impressed.", "tags": ["axiom"]},
    {"id": "prop_1", "name": "Prop. I, Theorem I", "kind": "proposition", "importance": 5,
     "pages": ["55","56"], "summary": "Radii sweep equal areas in equal times.", "tags": ["kepler-2"]}
  ],
  "edges": [
    {"id": "edge.prop_1.to.law_2", "source": "prop_1", "target": "law_2",
     "kind": "depends_on", "weight": 1.0, "label": "by the second Law"}
  ]
}"""

PROVENANCE_BLOB = """{
  "schema_version": "1.0",
  "level_id": "principia_bk1_sec1",
  "edges": [
    {"edge_id": "edge.prop_1.to.law_2", "provenance": "cited",
     "snippet": "…which is manifest by the second Law of Motion…",
     "page_seen": "55", "agreement": "both", "reason": "", "vague": false},
    {"edge_id": "edge.prop_1.to.lemma_1", "provenance": "inferred",
     "snippet": "", "page_seen": null, "agreement": "inference_only",
     "reason": "The polygon-to-curve limit relies on ultimate-equality of vanishing triangles.", "vague": false}
  ],
  "flags": ["ISLANDS: 1 component (ok)"]
}"""


GOLDEN = [
    (NodesRaw, NODES_RAW_BLOB),
    (CitationsRaw, CITATIONS_RAW_BLOB),
    (InferenceRaw, INFERENCE_RAW_BLOB),
    (PageMap, PAGE_MAP_BLOB),
    (ConceptGraph, CONCEPT_GRAPH_BLOB),
    (Provenance, PROVENANCE_BLOB),
]


@pytest.mark.parametrize("model_cls,blob", GOLDEN)
def test_round_trip(model_cls, blob):
    inst = model_cls.model_validate_json(blob)
    dumped = inst.model_dump()
    reparsed = model_cls.model_validate(dumped)
    assert reparsed == inst
    assert reparsed.model_dump() == dumped


@pytest.mark.parametrize("model_cls,blob", GOLDEN)
def test_extra_forbid(model_cls, blob):
    obj = json.loads(blob)
    obj["__unexpected_field__"] = "boom"
    with pytest.raises(ValidationError):
        model_cls.model_validate_json(json.dumps(obj))


def test_schema_version_error(tmp_path):
    obj = json.loads(NODES_RAW_BLOB)
    obj["schema_version"] = "0.9"
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(obj), encoding="utf-8")

    with pytest.raises(SchemaVersionError) as excinfo:
        load_json(str(p), NodesRaw)

    msg = str(excinfo.value)
    assert str(p) in msg
    assert repr(SCHEMA_VERSION) in msg
    assert repr("0.9") in msg
