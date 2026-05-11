"""Streamlit UI for DocQualityChecker."""

from __future__ import annotations

import os
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import streamlit as st

from doc_quality_checker.ai_reporter import generate_ai_summary
from doc_quality_checker.checker import CheckError, CheckerConfig, run_check
from doc_quality_checker.models import AIReportSummary, CheckResult
from doc_quality_checker.report_generator import generate_markdown_report, write_markdown_report
from doc_quality_checker.rules import summarize_issue_categories


UPLOAD_DIR = Path("outputs/uploads")
STREAMLIT_REPORT_DIR = Path("outputs/streamlit_reports")
SEVERITY_OPTIONS = ["全部", "error", "warning", "info"]
CATEGORY_OPTIONS = [
    "全部",
    "structure",
    "paragraph",
    "heading",
    "figure_table",
    "format",
    "unfinished",
]


def ensure_output_directories() -> None:
    """Create runtime directories used by the Streamlit app."""

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    STREAMLIT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_file_stem(file_name: str) -> str:
    """Convert the uploaded file name into a safe stem."""

    raw_stem = Path(file_name).stem
    safe_chars = []
    for char in raw_stem:
        if char.isalnum() or char in {"-", "_"} or ("\u4e00" <= char <= "\u9fff"):
            safe_chars.append(char)
        else:
            safe_chars.append("_")
    sanitized = "".join(safe_chars).strip("_")
    return sanitized or "document"


def build_timestamp() -> str:
    """Return a compact timestamp string."""

    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_uploaded_file(uploaded_file) -> Path:
    """Persist the uploaded file so the existing backend can read it."""

    ensure_output_directories()
    suffix = Path(uploaded_file.name).suffix.lower()
    file_name = f"{sanitize_file_stem(uploaded_file.name)}_{build_timestamp()}{suffix}"
    target_path = UPLOAD_DIR / file_name
    target_path.write_bytes(uploaded_file.getbuffer())
    return target_path


def build_report_path(file_name: str) -> Path:
    """Build the markdown report path for the current run."""

    ensure_output_directories()
    safe_stem = sanitize_file_stem(file_name)
    return STREAMLIT_REPORT_DIR / f"check_report_{safe_stem}_{build_timestamp()}.md"


def build_structure_rows(result: CheckResult) -> List[Dict[str, str]]:
    """Convert structure check items into table rows."""

    return [
        {
            "检查项": item.name,
            "状态": "通过" if item.exists else "缺失",
            "匹配内容": item.matched_text or "-",
        }
        for item in result.structure_items
    ]


def build_issue_rows(result: CheckResult, show_excerpt: bool) -> List[Dict[str, str]]:
    """Convert issues into table rows."""

    rows: List[Dict[str, str]] = []
    for issue in result.issues:
        rows.append(
            {
                "规则 ID": issue.rule_id or "-",
                "可信度": issue.confidence or "-",
                "类型": issue.category,
                "严重程度": issue.severity,
                "位置": issue.location,
                "问题": issue.message,
                "建议": issue.suggestion,
                "原文片段": (issue.excerpt or "-") if show_excerpt else "-",
            }
        )
    return rows


def filter_issue_rows(
    issue_rows: List[Dict[str, str]],
    selected_severity: str,
    selected_category: str,
) -> List[Dict[str, str]]:
    """Filter issue rows based on severity and category."""

    filtered = issue_rows
    if selected_severity != "全部":
        filtered = [row for row in filtered if row["严重程度"] == selected_severity]
    if selected_category != "全部":
        filtered = [row for row in filtered if row["类型"] == selected_category]
    return filtered


def build_issue_chart_rows(result: CheckResult) -> List[Dict[str, int | str]]:
    """Build chart data for issue category counts."""

    counts = summarize_issue_categories(result.issues)
    return [
        {"问题类型": category, "数量": count}
        for category, count in sorted(counts.items(), key=lambda item: item[0])
    ]


def render_header() -> None:
    """Render page header and usage notes."""

    st.set_page_config(
        page_title="DocQualityChecker 文档质量检测工具",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        """
        <style>
        .hero {
            padding: 1.2rem 1.4rem;
            border-radius: 18px;
            background: linear-gradient(135deg, #f4f7f2 0%, #eef5f8 100%);
            border: 1px solid #dbe7dd;
            margin-bottom: 1rem;
        }
        .hero h1 {
            margin: 0;
            color: #183a2d;
            font-size: 2rem;
        }
        .hero p {
            margin: 0.5rem 0 0;
            color: #42574a;
            line-height: 1.7;
        }
        </style>
        <div class="hero">
            <h1>DocQualityChecker 文档质量检测工具</h1>
            <p>上传 Word 文档，自动检测结构完整性、段落长度、标题编号、图表编号和未完成标记，并生成 Markdown 检测报告。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        **使用说明**

        1. 上传一个 `.docx` 文档。
        2. 在左侧设置最大段落长度阈值、报告生成和 AI 优化等参数。
        3. 点击 `开始检测`，查看评分、结构检查、问题列表、可靠性说明和 Markdown 报告。
        """,
    )


def render_sidebar() -> Tuple[int, bool, bool, bool, bool]:
    """Render sidebar controls and return current parameter values."""

    with st.sidebar:
        st.header("参数设置")
        max_paragraph_length = st.slider(
            "最大段落长度阈值",
            min_value=100,
            max_value=1000,
            value=300,
            step=50,
            help="当单段字符数超过该阈值时，会提示段落过长。",
        )
        show_excerpt = st.checkbox("显示原文片段", value=True)
        generate_report = st.checkbox("生成 Markdown 报告", value=True)
        enable_ai = st.checkbox("启用 AI 报告优化", value=False)
        if enable_ai and not os.getenv("OPENAI_API_KEY"):
            st.warning("未检测到 OPENAI_API_KEY，无法启用 AI 优化。")
        start_check = st.button("开始检测", type="primary", use_container_width=True)
    return max_paragraph_length, show_excerpt, generate_report, enable_ai, start_check


def render_overview_metrics(result: CheckResult) -> None:
    """Render the overview metrics section."""

    severity_counts = Counter(issue.severity for issue in result.issues)
    top_cols = st.columns(5)
    top_cols[0].metric("综合评分", f"{result.score} / 100")
    top_cols[1].metric("质量等级", result.level)
    top_cols[2].metric("问题总数", len(result.issues))
    top_cols[3].metric("warning", severity_counts.get("warning", 0))
    top_cols[4].metric("info", severity_counts.get("info", 0))

    bottom_cols = st.columns(5)
    bottom_cols[0].metric("error", severity_counts.get("error", 0))
    bottom_cols[1].metric("总字数", result.stats.total_chars)
    bottom_cols[2].metric("段落数", result.stats.paragraph_count)
    bottom_cols[3].metric("标题数", result.stats.heading_count)
    bottom_cols[4].metric("表格数", result.stats.table_count)


def render_ai_section(ai_summary: Optional[AIReportSummary], ai_message: Optional[str]) -> None:
    """Render AI summary section."""

    st.subheader("AI 优化建议")
    if ai_summary is None:
        if ai_message:
            st.warning(ai_message)
        else:
            st.info("本次未启用 AI 报告优化。")
        return

    st.success(ai_message or "AI 优化建议已生成。")
    st.markdown(f"**总体评价**：{ai_summary.overall_comment}")
    st.markdown("**主要问题**")
    for item in ai_summary.main_problems or ["暂无"]:
        st.markdown(f"- {item}")
    st.markdown("**修改优先级**")
    for item in ai_summary.priority_suggestions or ["暂无"]:
        st.markdown(f"- {item}")
    st.markdown("**优化后的总结**")
    st.info(ai_summary.polished_summary or "暂无 AI 总结。")
    st.markdown("**风险提示**")
    st.caption(ai_summary.risk_notice or "以上内容由 AI 基于规则检测结果自动生成，仅供自查参考。")


def render_report_section(report_path: Optional[Path], report_text: Optional[str], source_name: str) -> None:
    """Render markdown report preview and download controls."""

    st.subheader("Markdown 报告")
    if not report_path or not report_text:
        st.info("本次未生成 Markdown 报告。")
        return

    st.success(f"报告已生成：{report_path}")
    download_name = f"check_report_{sanitize_file_stem(source_name)}.md"
    st.download_button(
        "下载 Markdown 检测报告",
        data=report_text,
        file_name=download_name,
        mime="text/markdown",
        use_container_width=True,
    )
    with st.expander("预览 Markdown 报告内容", expanded=False):
        st.code(report_text, language="markdown")


def run_detection(
    uploaded_file,
    max_paragraph_length: int,
    should_generate_report: bool,
    enable_ai: bool,
) -> Tuple[CheckResult, Optional[str], Optional[Path], Path, Optional[str]]:
    """Persist the uploaded file, run the backend check, and optionally create a report."""

    saved_file_path = save_uploaded_file(uploaded_file)
    result = run_check(
        saved_file_path,
        CheckerConfig(max_paragraph_length=max_paragraph_length),
    )

    ai_message: Optional[str] = None
    if enable_ai:
        ai_summary, ai_message = generate_ai_summary(result)
        if ai_summary is not None:
            result.ai_summary = ai_summary

    report_text: Optional[str] = None
    report_path: Optional[Path] = None
    if should_generate_report:
        report_text = generate_markdown_report(result)
        report_path = build_report_path(uploaded_file.name)
        write_markdown_report(report_text, report_path)
    return result, report_text, report_path, saved_file_path, ai_message


def main() -> None:
    """Run the Streamlit application."""

    render_header()
    max_paragraph_length, show_excerpt, generate_report, enable_ai, start_check = render_sidebar()

    uploaded_file = st.file_uploader(
        "上传待检测的 Word 文档（.docx）",
        type=["docx"],
        help="当前版本仅支持 .docx 文件。",
    )

    if uploaded_file is None:
        st.info("请先上传一个 .docx 文件开始检测。")
        return

    if Path(uploaded_file.name).suffix.lower() != ".docx":
        st.error("仅支持上传 .docx 文件，请重新选择。")
        return

    current_upload_signature = f"{uploaded_file.name}:{uploaded_file.size}"
    previous_upload_signature = st.session_state.get("upload_signature")
    if previous_upload_signature and previous_upload_signature != current_upload_signature:
        st.session_state.pop("check_result", None)
        st.session_state.pop("report_text", None)
        st.session_state.pop("report_path", None)
        st.session_state.pop("source_name", None)
        st.session_state.pop("ai_message", None)
    st.session_state["upload_signature"] = current_upload_signature

    file_size_kb = uploaded_file.size / 1024
    st.caption(f"已上传文件：`{uploaded_file.name}`  |  大小：{file_size_kb:.1f} KB")

    if start_check:
        try:
            with st.spinner("正在检测文档，请稍候..."):
                result, report_text, report_path, saved_path, ai_message = run_detection(
                    uploaded_file,
                    max_paragraph_length=max_paragraph_length,
                    should_generate_report=generate_report,
                    enable_ai=enable_ai,
                )
            st.session_state["check_result"] = result
            st.session_state["report_text"] = report_text
            st.session_state["report_path"] = str(report_path) if report_path else ""
            st.session_state["saved_upload_path"] = str(saved_path)
            st.session_state["source_name"] = uploaded_file.name
            st.session_state["ai_message"] = ai_message
            st.success("检测完成，可以向下查看详细结果。")
        except CheckError:
            st.error("检测失败，请检查文件是否为有效的 Word 文档。")
            return
        except OSError:
            st.error("检测失败，上传文件保存或报告写入时出现问题。")
            return
        except Exception:
            st.error("检测失败，请检查文件是否为有效的 Word 文档。")
            return

    result = st.session_state.get("check_result")
    if result is None:
        st.warning("文件已上传，请在左侧点击“开始检测”。")
        return

    report_text = st.session_state.get("report_text")
    report_path_raw = st.session_state.get("report_path")
    report_path = Path(report_path_raw) if report_path_raw else None
    source_name = st.session_state.get("source_name", uploaded_file.name)
    ai_message = st.session_state.get("ai_message")

    st.divider()
    st.subheader("检测结果概览")
    render_overview_metrics(result)

    st.divider()
    st.subheader("结构完整性检查")
    st.dataframe(build_structure_rows(result), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("问题列表")
    filter_cols = st.columns(2)
    selected_severity = filter_cols[0].selectbox("按严重程度筛选", SEVERITY_OPTIONS)
    selected_category = filter_cols[1].selectbox("按问题类型筛选", CATEGORY_OPTIONS)

    issue_rows = build_issue_rows(result, show_excerpt=show_excerpt)
    filtered_issue_rows = filter_issue_rows(issue_rows, selected_severity, selected_category)
    if filtered_issue_rows:
        st.dataframe(filtered_issue_rows, use_container_width=True, hide_index=True)
    else:
        st.info("当前筛选条件下没有问题记录。")

    st.divider()
    st.subheader("问题分类统计")
    chart_rows = build_issue_chart_rows(result)
    if chart_rows:
        st.bar_chart(chart_rows, x="问题类型", y="数量", use_container_width=True)
    else:
        st.info("当前未发现明显问题。")

    st.divider()
    render_ai_section(result.ai_summary, ai_message)

    st.divider()
    render_report_section(report_path, report_text, source_name)


if __name__ == "__main__":
    main()
