"""Main orchestration for document checking."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

from .docx_reader import DocxReadError, read_docx
from .models import CheckResult, Issue
from .rules import (
    build_issue,
    check_basic_format,
    check_figure_table_numbers,
    check_heading_hierarchy,
    check_paragraph_length,
    check_structure,
    check_unfinished_markers,
)
from .utils import is_docx_file


class CheckError(Exception):
    """Raised when a check cannot be completed."""


@dataclass
class CheckerConfig:
    """Configuration for document checking."""

    max_paragraph_length: int = 300


def _calculate_score(issues: List[Issue]) -> int:
    score = 100
    for issue in issues:
        if issue.severity == "error":
            score -= 8
        elif issue.severity == "warning":
            score -= 3
        elif issue.severity == "info":
            score -= 1
    return max(score, 0)


def _get_level(score: int) -> str:
    if score >= 90:
        return "优秀"
    if score >= 75:
        return "良好"
    if score >= 60:
        return "一般"
    return "建议修改"


def run_check(file_path: Path, config: CheckerConfig) -> CheckResult:
    """Run the full document quality check."""

    if not file_path.exists():
        raise CheckError(f"文件不存在：{file_path}\n请检查路径是否正确。")
    if not file_path.is_file():
        raise CheckError(f"输入路径不是文件：{file_path}\n请传入一个 .docx 文档文件。")
    if not is_docx_file(file_path):
        raise CheckError(f"暂不支持该文件格式：{file_path.suffix or '无后缀'}\n请确认输入文件为 .docx 格式。")

    try:
        content = read_docx(file_path)
    except DocxReadError as exc:
        raise CheckError(str(exc)) from exc

    issues: List[Issue] = []
    structure_issues, structure_items = check_structure(content.paragraphs)
    issues.extend(structure_issues)
    issues.extend(check_paragraph_length(content.paragraphs, config.max_paragraph_length))
    issues.extend(check_unfinished_markers(content.paragraphs))
    issues.extend(check_heading_hierarchy(content.paragraphs))
    issues.extend(check_figure_table_numbers(content.paragraphs))
    issues.extend(check_basic_format(content.paragraphs))

    if content.stats.paragraph_count == 0 or content.stats.total_chars == 0:
        issues.append(
            build_issue(
                category="structure",
                severity="warning",
                location="全文",
                message="文档内容为空或几乎为空。",
                suggestion="建议确认文档是否已保存完整内容后再进行检测。",
                rule_id="STRUCTURE_999",
                confidence="high",
                principle="通过段落数和总字数判断文档是否缺少有效内容。",
            )
        )

    score = _calculate_score(issues)
    return CheckResult(
        stats=content.stats,
        issues=issues,
        structure_items=structure_items,
        score=score,
        level=_get_level(score),
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
