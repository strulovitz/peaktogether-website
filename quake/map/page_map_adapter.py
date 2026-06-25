from typing import Optional

from map.raw_models import PageEntry, PageMap, SCHEMA_VERSION


def adapt(hocr_pages: dict, pack_id: str, image_dir: str | None) -> PageMap:
    ver = hocr_pages["format-version"]
    if ver != "2":
        raise ValueError(f"Unsupported format-version: {ver!r}, expected '2'")

    entries: list[PageEntry] = []
    for page in hocr_pages["pages"]:
        leaf_num = page["leafNum"]
        leaf_index = leaf_num - 1
        page_label = page["pageNumber"]
        if image_dir is not None:
            image_path: Optional[str] = f"{image_dir}/leaf_{leaf_num:04d}.png"
        else:
            image_path = None
        entries.append(
            PageEntry(
                page_label=page_label,
                leaf_index=leaf_index,
                image_path=image_path,
            )
        )

    entries.sort(key=lambda e: e.leaf_index)

    for expected, entry in enumerate(entries):
        if entry.leaf_index != expected:
            raise ValueError(f"leaf_index not contiguous: missing index {expected}")

    seen_labels: set[str] = set()
    for entry in entries:
        if entry.page_label == "":
            continue
        if entry.page_label in seen_labels:
            raise ValueError(f"Duplicate page_label: {entry.page_label!r}")
        seen_labels.add(entry.page_label)

    return PageMap(
        schema_version=SCHEMA_VERSION,
        pack_id=pack_id,
        pages=entries,
    )
