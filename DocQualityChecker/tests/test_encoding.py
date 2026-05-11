"""Tests that guard against source-code mojibake in user-facing files."""

from pathlib import Path


MOJIBAKE_MARKERS = (
    "鎽樿",
    "鍏抽敭璇",
    "缁撹",
    "鍙傝€冩枃鐚",
    "妫€娴",
    "鏂囨。",
    "绗?",
    "锛?",
)


def test_no_known_mojibake_markers_in_source_files() -> None:
    paths = [Path("app.py")] + list(Path("doc_quality_checker").glob("*.py"))
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert not any(marker in text for marker in MOJIBAKE_MARKERS), f"Detected mojibake in {path}"
