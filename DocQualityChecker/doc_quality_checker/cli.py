"""Command line interface for DocQualityChecker."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from . import __version__
from .ai_reporter import generate_ai_summary
from .checker import CheckError, CheckerConfig, run_check
from .report_generator import generate_markdown_report, write_markdown_report


DEFAULT_OUTPUT = Path("outputs/check_report.md")


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""

    parser = argparse.ArgumentParser(
        prog="DocQualityChecker",
        description="检测 .docx 文档中的结构、段落、标题、图表与基础格式问题，并生成 Markdown 报告。",
    )
    parser.add_argument("--file", help="待检测的 .docx 文件路径。")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help=f"Markdown 报告输出路径，默认：{DEFAULT_OUTPUT}",
    )
    parser.add_argument(
        "--max-paragraph-length",
        type=int,
        default=300,
        help="段落长度阈值，超过该值会提示段落过长。",
    )
    parser.add_argument(
        "--enable-ai",
        action="store_true",
        help="启用 AI 报告优化。若未配置 OPENAI_API_KEY，则会自动跳过。",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entrypoint."""

    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.file:
        parser.print_help()
        return 1

    ai_message: Optional[str] = None
    try:
        result = run_check(
            Path(args.file),
            CheckerConfig(max_paragraph_length=args.max_paragraph_length),
        )
        if args.enable_ai:
            ai_summary, ai_message = generate_ai_summary(result)
            if ai_summary is not None:
                result.ai_summary = ai_summary
        report_text = generate_markdown_report(result)
        write_markdown_report(report_text, Path(args.output))
    except CheckError as exc:
        print("检测失败：")
        print(f"原因：{exc}")
        print("建议：请确认输入文件为 .docx 格式，并检查路径是否正确。")
        return 1
    except OSError as exc:
        print("检测失败：")
        print(f"原因：报告写入失败：{exc}")
        print("建议：请检查输出路径是否可写，或更换输出目录后重试。")
        return 1

    print("检测完成：")
    print(f"文件：{args.file}")
    print(f"评分：{result.score} / 100")
    print(f"等级：{result.level}")
    print(f"发现问题：{len(result.issues)} 个")
    print(f"报告路径：{args.output}")
    if args.enable_ai:
        print(f"AI 报告优化：{ai_message or '已生成 AI 优化建议。'}")
    return 0
