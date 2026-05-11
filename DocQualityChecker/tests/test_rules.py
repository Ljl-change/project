"""Tests for rule functions and markdown report generation."""

from doc_quality_checker.ai_reporter import generate_ai_summary
from doc_quality_checker.models import CheckResult, DocumentStats, ParagraphInfo
from doc_quality_checker.report_generator import generate_markdown_report
from doc_quality_checker.rules import (
    check_basic_format,
    check_figure_table_numbers,
    check_heading_hierarchy,
    check_paragraph_length,
    check_structure,
    check_unfinished_markers,
)


def build_paragraph(
    index: int,
    text: str,
    is_heading: bool = False,
    heading_number: str = None,
) -> ParagraphInfo:
    """Create a paragraph object for testing."""

    return ParagraphInfo(
        index=index,
        text=text,
        style_name="Heading 1" if is_heading else "Normal",
        is_heading=is_heading,
        heading_number=heading_number,
    )


def test_long_paragraph_should_be_detected() -> None:
    paragraphs = [build_paragraph(1, "这是很长的正文。" + "示例文本" * 80)]
    issues = check_paragraph_length(paragraphs, max_paragraph_length=300)

    assert any(issue.rule_id == "PARAGRAPH_001" for issue in issues)
    assert any(issue.confidence == "high" for issue in issues)


def test_todo_should_be_detected() -> None:
    paragraphs = [build_paragraph(1, "这里后面还要补充 TODO 内容")]
    issues = check_unfinished_markers(paragraphs)

    assert any(issue.rule_id == "UNFINISHED_001" for issue in issues)


def test_heading_jump_should_be_detected() -> None:
    paragraphs = [
        build_paragraph(1, "1 绪论", is_heading=True, heading_number="1"),
        build_paragraph(2, "1.1.1 研究背景", is_heading=True, heading_number="1.1.1"),
    ]
    issues = check_heading_hierarchy(paragraphs)

    assert any(issue.rule_id == "HEADING_003" for issue in issues)


def test_figure_sequence_gap_should_be_detected() -> None:
    paragraphs = [
        build_paragraph(1, "图1 系统流程图"),
        build_paragraph(2, "图2 模块结构图"),
        build_paragraph(3, "图4 实验结果图"),
    ]
    issues = check_figure_table_numbers(paragraphs)

    assert any(issue.rule_id == "FIGURE_TABLE_003" for issue in issues)


def test_unmatched_chinese_brackets_should_be_detected() -> None:
    paragraphs = [build_paragraph(1, "（这里有一个括号没有闭合。")]
    issues = check_basic_format(paragraphs)

    assert any(issue.rule_id == "FORMAT_004" for issue in issues)


def test_markdown_report_should_include_reliability_and_rule_fields() -> None:
    stats = DocumentStats(
        file_name="sample.docx",
        file_path="examples/sample.docx",
        total_chars=1234,
        paragraph_count=12,
        empty_paragraph_count=2,
        heading_count=4,
        table_count=1,
    )
    structure_issues, structure_items = check_structure([build_paragraph(1, "摘要", is_heading=True)])
    result = CheckResult(
        stats=stats,
        issues=structure_issues,
        structure_items=structure_items,
        score=88,
        level="良好",
        created_at="2026-05-11 10:00:00",
    )

    report = generate_markdown_report(result)

    assert "# 文档质量检测报告" in report
    assert "## 检测可靠性说明" in report
    assert "规则 ID" in report


def test_ai_reporter_should_skip_without_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    stats = DocumentStats(
        file_name="sample.docx",
        file_path="examples/sample.docx",
        total_chars=1234,
        paragraph_count=12,
        empty_paragraph_count=2,
        heading_count=4,
        table_count=1,
    )
    result = CheckResult(
        stats=stats,
        issues=[],
        structure_items=[],
        score=100,
        level="优秀",
        created_at="2026-05-11 10:00:00",
    )

    ai_summary, message = generate_ai_summary(result)

    assert ai_summary is None
    assert "未配置 AI API Key" in message
