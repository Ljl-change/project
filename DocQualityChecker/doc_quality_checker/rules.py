"""Heuristic rule implementations for document quality checks."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .models import Issue, ParagraphInfo, StructureCheckItem
from .utils import contains_cjk, detect_heading_number, normalize_text, truncate_text

STRUCTURE_RULES: Sequence[Tuple[str, Tuple[str, ...], str]] = (
    ("摘要", ("摘要",), "STRUCTURE_001"),
    ("关键词", ("关键词",), "STRUCTURE_002"),
    ("引言 / 绪论", ("引言", "绪论"), "STRUCTURE_003"),
    ("结论 / 总结", ("结论", "总结"), "STRUCTURE_004"),
    ("参考文献", ("参考文献",), "STRUCTURE_005"),
)

UNFINISHED_MARKERS: Sequence[str] = (
    "TODO",
    "todo",
    "待补充",
    "待完善",
    "这里补充",
    "XXX",
    "xxx",
    "改一下",
    "后面再写",
    "参考模板",
    "插入图片",
    "补图",
    "待修改",
    "待确认",
    "此处添加",
    "这里写",
    "暂缺",
)

FIGURE_PATTERN = re.compile(r"(图\s*(\d+(?:[-.]\d+)?))")
TABLE_PATTERN = re.compile(r"(表\s*(\d+(?:[-.]\d+)?))")
FIGURE_REFERENCE_PATTERN = re.compile(r"(如下图所示|见下图|如图所示)")
MULTI_SPACE_PATTERN = re.compile(r" {2,}")
MULTI_PUNCTUATION_PATTERN = re.compile(r"[，。、】【；：！？]{2,}")


def build_issue(
    *,
    category: str,
    severity: str,
    location: str,
    message: str,
    suggestion: str,
    rule_id: str,
    confidence: str,
    principle: str,
    excerpt: Optional[str] = None,
) -> Issue:
    """Create a rule issue with consistent metadata."""

    return Issue(
        category=category,
        severity=severity,
        location=location,
        message=message,
        suggestion=suggestion,
        excerpt=excerpt,
        rule_id=rule_id,
        confidence=confidence,
        principle=principle,
    )


def check_structure(paragraphs: Sequence[ParagraphInfo]) -> Tuple[List[Issue], List[StructureCheckItem]]:
    """Check whether required document sections exist."""

    issues: List[Issue] = []
    items: List[StructureCheckItem] = []

    normalized_paragraphs = [normalize_text(paragraph.text) for paragraph in paragraphs if paragraph.text.strip()]
    for name, keywords, rule_id in STRUCTURE_RULES:
        matched_text = next(
            (
                text
                for text in normalized_paragraphs
                if any(keyword in text for keyword in keywords)
            ),
            None,
        )
        exists = matched_text is not None
        items.append(
            StructureCheckItem(
                name=name,
                exists=exists,
                matched_text=truncate_text(matched_text, 40) if matched_text else None,
            )
        )
        if not exists:
            issues.append(
                build_issue(
                    category="structure",
                    severity="warning",
                    location="全文",
                    message=f"未检测到“{name}”部分。",
                    suggestion=f"建议补充{name}章节，或检查标题命名是否规范。",
                    rule_id=rule_id,
                    confidence="medium",
                    principle="通过标题文本和全文关键词进行启发式匹配，判断目标章节是否出现。",
                )
            )
    return issues, items


def check_paragraph_length(
    paragraphs: Sequence[ParagraphInfo],
    max_paragraph_length: int,
) -> List[Issue]:
    """Check paragraph length and excessive blank lines."""

    issues: List[Issue] = []
    consecutive_empty = 0

    for paragraph in paragraphs:
        stripped = paragraph.text.strip()
        length = len(re.sub(r"\s+", "", paragraph.text))

        if not stripped:
            consecutive_empty += 1
            if consecutive_empty == 3:
                issues.append(
                    build_issue(
                        category="paragraph",
                        severity="info",
                        location=f"第 {paragraph.index} 段附近",
                        message="检测到连续空段超过 2 个，可能存在过多空行。",
                        suggestion="建议删除多余空行，保持段落间距整洁。",
                        rule_id="PARAGRAPH_003",
                        confidence="high",
                        principle="通过统计连续空白段落数量，识别明显的空行堆叠。",
                    )
                )
            continue

        consecutive_empty = 0
        if length > max_paragraph_length:
            issues.append(
                build_issue(
                    category="paragraph",
                    severity="warning",
                    location=f"第 {paragraph.index} 段",
                    message=f"段落长度为 {length}，超过阈值 {max_paragraph_length}。",
                    suggestion="建议拆分过长段落，突出重点并提升可读性。",
                    excerpt=truncate_text(paragraph.text),
                    rule_id="PARAGRAPH_001",
                    confidence="high",
                    principle="对去除空白后的段落字符数进行统计，超过阈值即视为段落过长。",
                )
            )
        if 0 < length < 8 and not paragraph.is_heading:
            issues.append(
                build_issue(
                    category="paragraph",
                    severity="info",
                    location=f"第 {paragraph.index} 段",
                    message="段落内容较短，可能信息不足或为残留占位内容。",
                    suggestion="建议确认该段是否需要保留，或补充更完整的表达。",
                    excerpt=truncate_text(paragraph.text),
                    rule_id="PARAGRAPH_002",
                    confidence="medium",
                    principle="对非标题段落的长度做启发式判断，过短内容通常可读性或完整性不足。",
                )
            )
    return issues


def check_unfinished_markers(paragraphs: Sequence[ParagraphInfo]) -> List[Issue]:
    """Check whether paragraphs contain unfinished placeholders."""

    issues: List[Issue] = []
    for paragraph in paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue
        for marker in UNFINISHED_MARKERS:
            if marker in text:
                issues.append(
                    build_issue(
                        category="unfinished",
                        severity="warning",
                        location=f"第 {paragraph.index} 段",
                        message=f"检测到未完成标记“{marker}”。",
                        suggestion="建议删除占位内容，并补充完整、可提交的正式文本。",
                        excerpt=truncate_text(text),
                        rule_id="UNFINISHED_001",
                        confidence="high",
                        principle="对常见占位词和待补充标记进行关键词匹配，命中即提示未完成内容残留。",
                    )
                )
                break
    return issues


def _parse_decimal_number(number: str) -> Optional[List[int]]:
    if re.fullmatch(r"\d+(?:\.\d+)*", number):
        return [int(part) for part in number.split(".")]
    return None


def _detect_heading_title_without_content(number: Optional[str], text: str) -> bool:
    if not number:
        return False
    remaining = normalize_text(text)
    remaining = re.sub(r"^\s*" + re.escape(number), "", remaining).strip(" ：:.")
    return not remaining


def _check_decimal_heading_sequence(
    heading_numbers: Sequence[Tuple[ParagraphInfo, List[int]]]
) -> List[Issue]:
    """Heuristic sequence check for decimal headings."""

    issues: List[Issue] = []
    previous: Optional[List[int]] = None
    for paragraph, current in heading_numbers:
        if previous is None:
            previous = current
            continue

        if len(current) > len(previous) + 1:
            issues.append(
                build_issue(
                    category="heading",
                    severity="warning",
                    location=f"标题：{truncate_text(paragraph.text, 40)}",
                    message="标题层级可能存在跳级。",
                    suggestion="建议检查标题层级是否从上一级逐步展开，例如避免从 1 直接跳到 1.1.1。",
                    rule_id="HEADING_003",
                    confidence="medium",
                    principle="对数字型标题编号进行层级深度比较，若跨度超过一级则提示可能跳级。",
                )
            )

        if len(current) == len(previous):
            if current[:-1] == previous[:-1] and current[-1] > previous[-1] + 1:
                issues.append(
                    build_issue(
                        category="heading",
                        severity="warning",
                        location=f"标题：{truncate_text(paragraph.text, 40)}",
                        message=f"同级标题编号可能不连续：{'.'.join(map(str, previous))} 后出现 {'.'.join(map(str, current))}。",
                        suggestion="建议检查同一级标题编号是否遗漏或排序错误。",
                        rule_id="HEADING_004",
                        confidence="medium",
                        principle="对同一层级的数字标题编号进行递增检查，发现明显跳号时给出提醒。",
                    )
                )
        previous = current
    return issues


def check_heading_hierarchy(paragraphs: Sequence[ParagraphInfo]) -> List[Issue]:
    """Check heading length, numbering completeness, and heuristic sequence."""

    issues: List[Issue] = []
    decimal_headings: List[Tuple[ParagraphInfo, List[int]]] = []

    for paragraph in paragraphs:
        if not paragraph.is_heading:
            continue

        text = normalize_text(paragraph.text)
        number = paragraph.heading_number or detect_heading_number(text)
        if len(text) > 40:
            issues.append(
                build_issue(
                    category="heading",
                    severity="info",
                    location=f"标题：{truncate_text(text, 40)}",
                    message="标题较长，可能影响结构清晰度。",
                    suggestion="建议精简标题表述，尽量控制在 40 个字符以内。",
                    rule_id="HEADING_001",
                    confidence="medium",
                    principle="通过标题文本长度进行启发式判断，过长标题通常会削弱结构清晰度。",
                )
            )
        if _detect_heading_title_without_content(number, text):
            issues.append(
                build_issue(
                    category="heading",
                    severity="warning",
                    location=f"第 {paragraph.index} 段",
                    message="标题可能只有编号，未包含实际标题内容。",
                    suggestion="建议在编号后补充明确的小节名称。",
                    excerpt=truncate_text(text),
                    rule_id="HEADING_002",
                    confidence="high",
                    principle="对标题编号后的剩余文本进行检查，如果没有有效标题内容则提示空标题。",
                )
            )
        if number:
            decimal = _parse_decimal_number(number)
            if decimal:
                decimal_headings.append((paragraph, decimal))

    issues.extend(_check_decimal_heading_sequence(decimal_headings))
    return issues


def _check_caption_references(
    paragraphs: Sequence[ParagraphInfo],
    pattern: re.Pattern[str],
    label: str,
    duplicate_rule_id: str,
) -> Tuple[List[Issue], Dict[str, List[int]]]:
    occurrences: Dict[str, List[int]] = defaultdict(list)
    issues: List[Issue] = []

    for paragraph in paragraphs:
        for match in pattern.finditer(paragraph.text):
            full_label = normalize_text(match.group(1))
            number = match.group(2)
            occurrences[number].append(paragraph.index)
            if len(occurrences[number]) == 2:
                issues.append(
                    build_issue(
                        category="figure_table",
                        severity="warning",
                        location=f"第 {paragraph.index} 段",
                        message=f"{label}编号“{full_label}”重复出现。",
                        suggestion=f"建议检查{label}编号是否重复，保证全文唯一。",
                        excerpt=truncate_text(paragraph.text),
                        rule_id=duplicate_rule_id,
                        confidence="high",
                        principle="通过文本模式匹配提取图表编号，若同一编号重复出现则提示重复。",
                    )
                )
    return issues, occurrences


def _check_simple_sequence(
    occurrences: Dict[str, List[int]],
    label: str,
    rule_id: str,
) -> List[Issue]:
    issues: List[Issue] = []
    numeric_values = sorted(
        int(number)
        for number in occurrences
        if re.fullmatch(r"\d+", number)
    )
    for previous, current in zip(numeric_values, numeric_values[1:]):
        if current > previous + 1:
            issues.append(
                build_issue(
                    category="figure_table",
                    severity="warning",
                    location="全文",
                    message=f"{label}编号可能不连续：{label}{previous} 后出现 {label}{current}。",
                    suggestion=f"建议检查{label}编号是否遗漏、删除后未调整，或是否应改为章节式编号。",
                    rule_id=rule_id,
                    confidence="medium",
                    principle="对纯数字图表编号进行递增检查，发现明显跳号时给出提醒。",
                )
            )
    return issues


def check_figure_table_numbers(paragraphs: Sequence[ParagraphInfo]) -> List[Issue]:
    """Check figure/table numbering by text matching."""

    issues: List[Issue] = []
    figure_issues, figure_occurrences = _check_caption_references(
        paragraphs,
        FIGURE_PATTERN,
        "图",
        "FIGURE_TABLE_001",
    )
    table_issues, table_occurrences = _check_caption_references(
        paragraphs,
        TABLE_PATTERN,
        "表",
        "FIGURE_TABLE_002",
    )

    issues.extend(figure_issues)
    issues.extend(table_issues)
    issues.extend(_check_simple_sequence(figure_occurrences, "图", "FIGURE_TABLE_003"))
    issues.extend(_check_simple_sequence(table_occurrences, "表", "FIGURE_TABLE_004"))

    for index, paragraph in enumerate(paragraphs):
        text = paragraph.text.strip()
        if not text:
            continue
        if FIGURE_REFERENCE_PATTERN.search(text):
            window = paragraphs[max(0, index - 1) : min(len(paragraphs), index + 2)]
            has_caption_nearby = any(FIGURE_PATTERN.search(item.text) for item in window)
            if not has_caption_nearby:
                issues.append(
                    build_issue(
                        category="figure_table",
                        severity="info",
                        location=f"第 {paragraph.index} 段",
                        message="提到了“如下图所示 / 见下图 / 如图所示”，但附近未检测到明确图编号。",
                        suggestion="建议检查是否缺少图题，或在引用时补充明确的图编号。",
                        excerpt=truncate_text(text),
                        rule_id="FIGURE_TABLE_005",
                        confidence="low",
                        principle="通过引用表述与邻近段落中的图编号文本进行启发式关联，缺少编号时给出弱提示。",
                    )
                )
    return issues


def check_basic_format(paragraphs: Sequence[ParagraphInfo]) -> List[Issue]:
    """Check simple text formatting issues."""

    issues: List[Issue] = []
    for paragraph in paragraphs:
        text = paragraph.text
        stripped = text.strip()
        if not stripped:
            continue

        if MULTI_SPACE_PATTERN.search(text):
            issues.append(
                build_issue(
                    category="format",
                    severity="info",
                    location=f"第 {paragraph.index} 段",
                    message="存在连续多个空格。",
                    suggestion="建议统一段落中的空格使用，避免多余空格影响排版。",
                    excerpt=truncate_text(text),
                    rule_id="FORMAT_001",
                    confidence="high",
                    principle="通过正则表达式匹配两个及以上连续空格。",
                )
            )
        if MULTI_PUNCTUATION_PATTERN.search(text):
            issues.append(
                build_issue(
                    category="format",
                    severity="info",
                    location=f"第 {paragraph.index} 段",
                    message="存在连续多个中文标点。",
                    suggestion="建议检查重复标点，保持语句表达简洁规范。",
                    excerpt=truncate_text(text),
                    rule_id="FORMAT_002",
                    confidence="high",
                    principle="通过正则表达式匹配连续中文标点，识别明显的标点重复。",
                )
            )
        if contains_cjk(text):
            english_punctuation_count = len(re.findall(r"[,\.]", text))
            chinese_char_count = len(re.findall(r"[\u4e00-\u9fff]", text))
            if chinese_char_count >= 20 and english_punctuation_count >= 3:
                issues.append(
                    build_issue(
                        category="format",
                        severity="info",
                        location=f"第 {paragraph.index} 段",
                        message="中文段落中英文逗号或句号使用较多。",
                        suggestion="建议统一中文段落中的标点风格，优先使用中文标点。",
                        excerpt=truncate_text(text),
                        rule_id="FORMAT_003",
                        confidence="medium",
                        principle="对包含较多中文字符的段落统计英文标点数量，识别可能的标点风格混用。",
                    )
                )
        if text.count("（") != text.count("）"):
            issues.append(
                build_issue(
                    category="format",
                    severity="warning",
                    location=f"第 {paragraph.index} 段",
                    message="中文括号数量不匹配。",
                    suggestion="建议检查中文括号是否成对出现。",
                    excerpt=truncate_text(text),
                    rule_id="FORMAT_004",
                    confidence="high",
                    principle="直接统计中文左括号和右括号的数量差异，识别括号未闭合问题。",
                )
            )
        if text.count("(") != text.count(")"):
            issues.append(
                build_issue(
                    category="format",
                    severity="warning",
                    location=f"第 {paragraph.index} 段",
                    message="英文括号数量不匹配。",
                    suggestion="建议检查英文括号是否成对出现。",
                    excerpt=truncate_text(text),
                    rule_id="FORMAT_005",
                    confidence="high",
                    principle="直接统计英文左括号和右括号的数量差异，识别括号未闭合问题。",
                )
            )
    return issues


def summarize_issue_categories(issues: Iterable[Issue]) -> Counter[str]:
    """Count issues grouped by category."""

    return Counter(issue.category for issue in issues)
