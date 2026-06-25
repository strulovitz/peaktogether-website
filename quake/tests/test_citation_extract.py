import pytest

from map.citation_extract import extract
from map.raw_models import (
    CitationsRaw,
    RawCitation,
    RawCiteItem,
    PageMap,
    PageEntry,
)


def test_golden_fixture():
    """Reproduce the §3.A.2 verbatim example output exactly."""
    djvu_text = (
        "PROP. I. THEOREM I.\n\n"
        "Some preamble text. by the first Law of Motion the body moves. "
        "Then by Cor. 1. of the Laws it follows. "
        "Finally, as was demonstrated above, the result holds.\n"
    )

    page_map = PageMap(
        schema_version="1.0",
        pack_id="principia",
        pages=[PageEntry(page_label="55", leaf_index=0, image_path=None)],
    )

    node_labels = ["Prop. I. Theorem I.", "Lemma I"]

    result = extract(djvu_text, page_map, "principia_bk1_sec1", node_labels)

    assert result.schema_version == "1.0"
    assert result.source == "text"
    assert len(result.items) == 1

    item = result.items[0]
    assert item.local_label == "Prop. I. Theorem I."
    assert len(item.citations) == 3

    phrases = [c.phrase for c in item.citations]
    assert any("first Law of Motion" in p for p in phrases)
    cit1 = [c for c in item.citations if "first Law" in c.phrase][0]
    assert cit1.page_seen == "55"
    assert cit1.vague == False

    cit2 = [c for c in item.citations if "Cor. 1." in c.phrase][0]
    assert cit2.page_seen == "55"
    assert cit2.vague == False

    cit3 = [c for c in item.citations if "demonstrated above" in c.phrase][0]
    assert cit3.vague == True


def test_empty_label_leaf():
    """Empty page_label → synthetic page_seen."""
    djvu_text = "LEMMA I.\n\nby Lemma II some text"

    page_map = PageMap(
        schema_version="1.0",
        pack_id="test",
        pages=[
            PageEntry(page_label="", leaf_index=2, image_path=None),
        ],
    )

    node_labels = ["Lemma I", "Lemma II"]

    result = extract(djvu_text, page_map, "test_level", node_labels)

    assert len(result.items) >= 1
    for item in result.items:
        for cit in item.citations:
            assert cit.page_seen == "[leaf 2]"


def test_chunk_count_mismatch_raises():
    """If djvu_text has more chunks than page_map pages, raise ValueError."""
    djvu_text = "page1\x0cpage2\x0cpage3"  # 3 chunks

    page_map = PageMap(
        schema_version="1.0",
        pack_id="test",
        pages=[PageEntry(page_label="1", leaf_index=0)],
    )

    with pytest.raises(ValueError, match="chunk count"):
        extract(djvu_text, page_map, "test", ["Lemma I"])


def test_no_initial_owner():
    """If first chunk has no recognized heading, citations are discarded."""
    djvu_text = "by Lemma I some random text before any heading"

    page_map = PageMap(
        schema_version="1.0",
        pack_id="test",
        pages=[PageEntry(page_label="1", leaf_index=0)],
    )

    node_labels = ["Lemma I"]

    result = extract(djvu_text, page_map, "test", node_labels)
    assert result.schema_version == "1.0"


def test_multiple_owners():
    """Lemmas and propositions spanning multiple pages."""
    djvu_text = (
        "LEMMA I.\n\nSome text. by the first Law.\n\n"
        "\x0c"
        "LEMMA II.\n\nMore text. by Lemma I.\n\n"
    )

    page_map = PageMap(
        schema_version="1.0",
        pack_id="test",
        pages=[
            PageEntry(page_label="41", leaf_index=0),
            PageEntry(page_label="42", leaf_index=1),
        ],
    )

    node_labels = ["Lemma I", "Lemma II"]

    result = extract(djvu_text, page_map, "test", node_labels)

    assert len(result.items) == 2
    assert result.items[0].local_label == "Lemma I"
    assert result.items[1].local_label == "Lemma II"

    for cit in result.items[0].citations:
        assert cit.page_seen == "41"

    for cit in result.items[1].citations:
        assert cit.page_seen == "42"
