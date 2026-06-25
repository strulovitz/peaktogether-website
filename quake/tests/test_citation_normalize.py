import pytest

from map.raw_models import NodesRaw, RawNode
from map.citation_normalize import build_index, normalize, roman_to_int


FIXTURE_NODES = NodesRaw(
    schema_version="1.0",
    level_id="test",
    edition="test",
    nodes=[
        RawNode(local_label="Law I", proposed_id="law_1", kind="law", pages=["1"], summary="", importance_hint=5),
        RawNode(local_label="Law II", proposed_id="law_2", kind="law", pages=["1"], summary="", importance_hint=5),
        RawNode(local_label="Law III", proposed_id="law_3", kind="law", pages=["1"], summary="", importance_hint=5),
        RawNode(local_label="Lemma I", proposed_id="lemma_1", kind="lemma", pages=["41"], summary="", importance_hint=5),
        RawNode(local_label="Lemma II", proposed_id="lemma_2", kind="lemma", pages=["42"], summary="", importance_hint=4),
        RawNode(local_label="Lemma VII", proposed_id="lemma_7", kind="lemma", pages=["49"], summary="", importance_hint=3),
        RawNode(local_label="Lemma XI", proposed_id="lemma_11", kind="lemma", pages=["55"], summary="", importance_hint=3),
        RawNode(local_label="Prop. I. Theorem I.", proposed_id="prop_1", kind="proposition", pages=["55"], summary="", importance_hint=5),
        RawNode(local_label="Prop. IV. Theorem IV.", proposed_id="prop_4", kind="proposition", pages=["60"], summary="", importance_hint=4),
        RawNode(local_label="Prop. XI. Problem VI.", proposed_id="prop_11", kind="proposition", pages=["75"], summary="", importance_hint=3),
        RawNode(local_label="Cor. 2. Prop. IV.", proposed_id="cor_2_prop_4", kind="corollary", pages=["61"], summary="", importance_hint=2),
        RawNode(local_label="Def. I", proposed_id="def_1", kind="definition", pages=["5"], summary="", importance_hint=5),
        RawNode(local_label="Def. III", proposed_id="def_3", kind="definition", pages=["6"], summary="", importance_hint=4),
        RawNode(local_label="Def. VIII", proposed_id="def_8", kind="definition", pages=["10"], summary="", importance_hint=2),
    ],
)

LABEL_IDX = build_index(FIXTURE_NODES)


GOLDEN_TABLE = [
    # Laws — spelled ordinals
    ("by the first Law of Motion", "law_1"),
    ("by the second Law", "law_2"),
    ("by the third Law", "law_3"),
    # Laws — roman
    ("by Law I", "law_1"),
    ("by Law II", "law_2"),
    # Lemmas
    ("by Lem. I", "lemma_1"),
    ("by Lemma I", "lemma_1"),
    ("by Lemma II", "lemma_2"),
    ("by Lemma VII", "lemma_7"),
    ("by Lem. XI", "lemma_11"),
    # Propositions
    ("by Prop. I", "prop_1"),
    ("by Prop. I. Theorem I.", "prop_1"),
    ("by Proposition IV", "prop_4"),
    ("by Prop. XI of this Book", "prop_11"),
    # Corollaries
    ("by Cor. 1. of the Laws", "law_1"),
    ("by Cor. 2. Prop. IV", "cor_2_prop_4"),
    ("by Corollary 2 of Prop. IV", "cor_2_prop_4"),
    # Definitions
    ("by Def. I", "def_1"),
    ("by Definition III", "def_3"),
    ("by Def. VIII", "def_8"),
    # Vague — return None
    ("as was demonstrated above", None),
    ("as shown above", None),
    ("by what was demonstrated", None),
    ("above", None),
    ("by the preceding", None),
    # Unmatchable — return None
    ("by Lem. CXXV", None),
    ("by Prop. C", None),
    # Edge cases
    ("by the first Law", "law_1"),
    ("per Cor. 1. of the Laws", "law_1"),
]


@pytest.mark.parametrize("phrase,expected", GOLDEN_TABLE)
def test_normalize(phrase, expected):
    result = normalize(phrase, LABEL_IDX)
    assert result == expected


def test_build_index():
    idx = build_index(FIXTURE_NODES)
    assert idx["law 1"] == "law_1"
    assert idx["law 2"] == "law_2"
    assert idx["lemma 7"] == "lemma_7"
    assert idx["prop 11"] == "prop_11"
    assert idx["cor 2 prop 4"] == "cor_2_prop_4"
    assert idx["def 8"] == "def_8"


def test_build_index_empty():
    empty = NodesRaw(schema_version="1.0", level_id="test", edition="", nodes=[])
    idx = build_index(empty)
    assert idx == {}


@pytest.mark.parametrize(
    "s,expected",
    [
        ("I", 1),
        ("II", 2),
        ("III", 3),
        ("IV", 4),
        ("V", 5),
        ("VII", 7),
        ("IX", 9),
        ("XI", 11),
        ("L", 50),
        ("C", 100),
        ("CXXV", 125),
    ],
)
def test_roman_to_int(s, expected):
    assert roman_to_int(s) == expected
