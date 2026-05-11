"""Shared helper functions."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional


HEADING_NUMBER_PATTERN = re.compile(
    r"^\s*("
    r"\d+(?:\.\d+)*"
    r"|[一二三四五六七八九十]+、"
    r"|[（(][一二三四五六七八九十]+[)）]"
    r"|第\s*\d+\s*章"
    r")\s*"
)


def normalize_text(text: str) -> str:
    """Normalize text for rule matching."""

    return re.sub(r"\s+", " ", text).strip()


def count_non_whitespace_chars(text: str) -> int:
    """Count non-whitespace characters."""

    return len(re.sub(r"\s+", "", text))


def is_docx_file(path: Path) -> bool:
    """Return whether the path points to a .docx file."""

    return path.suffix.lower() == ".docx"


def truncate_text(text: str, limit: int = 80) -> str:
    """Safely truncate long text for console or report output."""

    cleaned = normalize_text(text)
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: max(0, limit - 3)]}..."


def escape_markdown_table(text: Optional[str]) -> str:
    """Escape content used inside markdown tables."""

    if text is None:
        return "-"
    return text.replace("|", r"\|").replace("\n", "<br>")


def detect_heading_number(text: str) -> Optional[str]:
    """Extract a heading numbering prefix when present."""

    match = HEADING_NUMBER_PATTERN.match(text)
    if not match:
        return None
    return normalize_text(match.group(1))


def looks_like_heading_text(text: str) -> bool:
    """Heuristic heading detection based on common heading patterns."""

    normalized = normalize_text(text)
    if not normalized:
        return False
    if detect_heading_number(normalized):
        return True
    return bool(
        re.match(
            r"^(摘要|关键词|引言|绪论|结论|总结|参考文献)([:：]?\s*.*)?$",
            normalized,
        )
    )


def contains_cjk(text: str) -> bool:
    """Return whether text contains Chinese characters."""

    return bool(re.search(r"[\u4e00-\u9fff]", text))
