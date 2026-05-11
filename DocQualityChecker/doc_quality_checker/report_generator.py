"""Markdown report generator."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import List, Optional

from .models import AIReportSummary, CheckResult, Issue
from .rules import summarize_issue_categories
from .utils import escape_markdown_table, truncate_text


SUGGESTION_SUMMARY = {
    "structure": "文档结构方面：建议补充摘要、关键词、引言/绪论、结论和参考文献等必要章节。",
    "paragraph": "段落组织方面：建议拆分过长段落，删除多余空行，并补足过短段落的信息。",
    "unfinished": "未完成内容方面：建议清理 TODO、待补充、占位文本等提交前残留内容。",
    "heading": "标题结构方面：建议检查标题命名、层级顺序和编号连续性，避免跳级或空标题。",
    "figure_table": "图表编号方面：建议检查图表编号是否重复、是否连续，并补充清晰的图表标题。",
    "format": "格式细节方面：建议统一中英文标点、空格和括号使用，减少基础排版问题。",
}


def _build_issue_message(issue: Issue) -> str:
    message = issue.message
    if issue.excerpt:
        message = f"{message}<br>片段：{escape_markdown_table(truncate_text(issue.excerpt, 60))}"
    return escape_markdown_table(message)


def _render_ai_summary(lines: List[str], ai_summary: AIReportSummary) -> None:
    """Append AI summary section to the markdown report."""

    lines.extend(
        [
            "",
            "## 七、AI 优化建议",
            "",
            f"- 总体评价：{ai_summary.overall_comment or '-'}",
            "",
            "### 主要问题",
        ]
    )
    if ai_summary.main_problems:
        for item in ai_summary.main_problems:
            lines.append(f"- {item}")
    else:
        lines.append("- 暂无")

    lines.extend(["", "### 修改优先级"])
    if ai_summary.priority_suggestions:
        for item in ai_summary.priority_suggestions:
            lines.append(f"- {item}")
    else:
        lines.append("- 暂无")

    lines.extend(
        [
            "",
            "### 优化总结",
            "",
            ai_summary.polished_summary or "暂无 AI 总结。",
            "",
            "### 风险提示",
            "",
            ai_summary.risk_notice or "以上内容由 AI 基于规则检测结果自动生成，仅供自查参考。",
        ]
    )


def generate_markdown_report(
    result: CheckResult,
    ai_summary: Optional[AIReportSummary] = None,
) -> str:
    """Generate a markdown report from the check result."""

    effective_ai_summary = ai_summary or result.ai_summary
    severity_counts = Counter(issue.severity for issue in result.issues)
    category_counts = summarize_issue_categories(result.issues)

    lines: List[str] = [
        "# 文档质量检测报告",
        "",
        "## 一、基本信息",
        "",
        f"- 文件名：{result.stats.file_name}",
        f"- 文件路径：{result.stats.file_path}",
        f"- 检测时间：{result.created_at}",
        f"- 总字数：{result.stats.total_chars}",
        f"- 段落数：{result.stats.paragraph_count}",
        f"- 空段落数：{result.stats.empty_paragraph_count}",
        f"- 标题数：{result.stats.heading_count}",
        f"- 表格数：{result.stats.table_count}",
        f"- 问题总数：{len(result.issues)}",
        f"- error 数量：{severity_counts.get('error', 0)}",
        f"- warning 数量：{severity_counts.get('warning', 0)}",
        f"- info 数量：{severity_counts.get('info', 0)}",
        "",
        "## 二、总体评分",
        "",
        f"- 综合评分：{result.score} / 100",
        f"- 质量等级：{result.level}",
        "- 说明：该评分基于启发式规则自动生成，仅用于文档提交前的自检参考。",
        "",
        "## 三、结构完整性检查",
        "",
        "| 检查项 | 是否存在 | 匹配内容 |",
        "|---|---|---|",
    ]

    for item in result.structure_items:
        lines.append(
            f"| {escape_markdown_table(item.name)} | {'是' if item.exists else '否'} | {escape_markdown_table(item.matched_text)} |"
        )

    lines.extend(
        [
            "",
            "## 四、问题列表",
            "",
        ]
    )

    if not result.issues:
        lines.append("未发现明显问题。")
    else:
        lines.extend(
            [
                "| 序号 | 类型 | 严重程度 | 规则 ID | 可信度 | 位置 | 问题 | 建议 |",
                "|---|---|---|---|---|---|---|---|",
            ]
        )
        for index, issue in enumerate(result.issues, start=1):
            lines.append(
                f"| {index} | {escape_markdown_table(issue.category)} | {escape_markdown_table(issue.severity)} | "
                f"{escape_markdown_table(issue.rule_id or '-')} | {escape_markdown_table(issue.confidence or '-')} | "
                f"{escape_markdown_table(issue.location)} | {_build_issue_message(issue)} | "
                f"{escape_markdown_table(truncate_text(issue.suggestion, 60))} |"
            )

    lines.extend(
        [
            "",
            "## 五、修改建议总结",
            "",
        ]
    )

    if not category_counts:
        lines.append("- 当前未发现明显问题，可结合人工复核后再提交。")
    else:
        for category in category_counts:
            lines.append(f"- {SUGGESTION_SUMMARY.get(category, '建议结合具体问题逐项修订文档内容和排版。')}")

    lines.extend(
        [
            "",
            "## 六、检测规则说明",
            "",
            "当前工具采用启发式规则进行自动检测，适用于论文、课程报告、比赛文档、软著说明书、项目报告等材料的提交前自查。",
            "",
            "它可以帮助你快速发现结构缺失、标题层级异常、未完成标记、基础排版问题等常见风险，但不能替代正式审稿、查重、排版软件或人工校对。",
            "",
            "## 检测可靠性说明",
            "",
            "1. 高可信度问题：通常由明确规则触发，例如 TODO、括号不匹配、明显段落过长。",
            "2. 中可信度问题：通常由关键词或编号规则触发，例如章节缺失、图表编号不连续。",
            "3. 低可信度问题：通常需要人工判断，例如标题命名特殊、文档类型特殊。",
            "",
            "DocQualityChecker 当前采用启发式规则检测，适合用于提交前自查和格式初筛。检测结果具有参考价值，但不能替代人工审阅、正式查重、排版软件或专业审稿流程。",
            "",
        ]
    )

    if effective_ai_summary:
        _render_ai_summary(lines, effective_ai_summary)

    return "\n".join(lines)


def write_markdown_report(report_text: str, output_path: Path) -> None:
    """Write the markdown report to disk, creating parent directories when needed."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_text, encoding="utf-8")
