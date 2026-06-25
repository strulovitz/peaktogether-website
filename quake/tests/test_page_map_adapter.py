import pytest

from map.page_map_adapter import adapt
from map.raw_models import PageEntry, PageMap


def test_normal_with_empties():
    hocr = {
        "format-version": "2",
        "pages": [
            {"leafNum": 1, "pageNumber": ""},
            {"leafNum": 2, "pageNumber": ""},
            {"leafNum": 3, "pageNumber": ""},
            {"leafNum": 4, "pageNumber": "41"},
            {"leafNum": 5, "pageNumber": "42"},
        ],
    }
    result = adapt(hocr, "principia", "source/pages")

    assert result.schema_version == "1.0"
    assert result.pack_id == "principia"
    assert len(result.pages) == 5

    assert [p.leaf_index for p in result.pages] == [0, 1, 2, 3, 4]
    assert [p.page_label for p in result.pages] == ["", "", "", "41", "42"]

    assert result.pages[0].image_path == "source/pages/leaf_0001.png"
    assert result.pages[3].image_path == "source/pages/leaf_0004.png"
    assert result.pages[4].image_path == "source/pages/leaf_0005.png"


def test_image_dir_none():
    hocr = {
        "format-version": "2",
        "pages": [
            {"leafNum": 1, "pageNumber": "1"},
            {"leafNum": 2, "pageNumber": "2"},
        ],
    }
    result = adapt(hocr, "testpack", None)
    assert result.pages[0].image_path is None
    assert result.pages[1].image_path is None


def test_wrong_format_version():
    hocr = {"format-version": "1", "pages": []}
    with pytest.raises(ValueError, match="format-version"):
        adapt(hocr, "testpack", None)


def test_gap_raises():
    hocr = {
        "format-version": "2",
        "pages": [
            {"leafNum": 1, "pageNumber": "1"},
            {"leafNum": 2, "pageNumber": "2"},
            {"leafNum": 4, "pageNumber": "4"},
        ],
    }
    with pytest.raises(ValueError, match="missing index 2"):
        adapt(hocr, "testpack", None)


def test_duplicate_non_empty_raises():
    hocr = {
        "format-version": "2",
        "pages": [
            {"leafNum": 1, "pageNumber": "41"},
            {"leafNum": 2, "pageNumber": "41"},
        ],
    }
    with pytest.raises(ValueError, match="41"):
        adapt(hocr, "testpack", None)


def test_duplicate_empty_passes():
    hocr = {
        "format-version": "2",
        "pages": [
            {"leafNum": 1, "pageNumber": ""},
            {"leafNum": 2, "pageNumber": ""},
            {"leafNum": 3, "pageNumber": "42"},
        ],
    }
    result = adapt(hocr, "testpack", None)
    assert len(result.pages) == 3
