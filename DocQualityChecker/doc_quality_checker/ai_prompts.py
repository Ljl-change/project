"""Prompt templates used by the AI report summarizer."""

from __future__ import annotations

import json
from typing import Any, Dict


AI_REPORT_JSON_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "overall_comment": {"type": "string"},
        "main_problems": {
            "type": "array",
            "items": {"type": "string"},
        },
        "priority_suggestions": {
            "type": "array",
            "items": {"type": "string"},
        },
        "polished_summary": {"type": "string"},
        "risk_notice": {"type": "string"},
    },
    "required": [
        "overall_comment",
        "main_problems",
        "priority_suggestions",
        "polished_summary",
        "risk_notice",
    ],
}


SYSTEM_PROMPT = """你是一个文档质量分析助手。
你只能基于 DocQualityChecker 规则引擎提供的结构化检测结果生成中文总结。
不要编造新的问题，不要声称你已经人工审阅了完整原文，不要给出“文档一定合格”这类绝对结论。
请只输出符合指定 JSON Schema 的 JSON。"""


def build_user_prompt(payload: Dict[str, Any]) -> str:
    """Build the user prompt from a sanitized structured payload."""

    return (
        "下面是 DocQualityChecker 规则引擎输出的结构化检测结果。\n"
        "请你只基于这些结果，给出总体评价、主要问题、修改优先级、优化总结和风险提示。\n"
        "不要新增不存在的问题，不要覆盖规则引擎原始结论。\n\n"
        "检测结果 JSON：\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )
