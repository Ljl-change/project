"""AI summary generation based on structured check results."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional, Tuple

from .ai_prompts import AI_REPORT_JSON_SCHEMA, SYSTEM_PROMPT, build_user_prompt
from .models import AIReportSummary, CheckResult
from .utils import truncate_text


DEFAULT_AI_MODEL = os.getenv("DOC_QUALITY_CHECKER_AI_MODEL", "gpt-4.1-mini")


def _build_ai_payload(result: CheckResult) -> Dict[str, Any]:
    """Build a privacy-conscious payload for the AI model."""

    issues = []
    for issue in result.issues[:30]:
        issues.append(
            {
                "rule_id": issue.rule_id,
                "category": issue.category,
                "severity": issue.severity,
                "confidence": issue.confidence,
                "location": issue.location,
                "message": issue.message,
                "suggestion": issue.suggestion,
                "principle": issue.principle,
                "excerpt": truncate_text(issue.excerpt or "", 80) if issue.excerpt else "",
            }
        )

    return {
        "stats": result.stats.to_dict(),
        "score": result.score,
        "level": result.level,
        "structure_items": [item.to_dict() for item in result.structure_items],
        "issues": issues,
        "issue_count": len(result.issues),
        "note": "仅基于规则引擎的结构化输出进行总结，不包含完整原文。",
    }


def generate_ai_summary(
    result: CheckResult,
    model: Optional[str] = None,
) -> Tuple[Optional[AIReportSummary], str]:
    """Generate an AI summary from a structured check result.

    Returns a tuple of (summary, message). When summary is None, message explains why.
    """

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None, "未配置 AI API Key，已跳过 AI 报告优化。"

    try:
        from openai import OpenAI
    except ModuleNotFoundError:
        return None, "未安装 openai 依赖，已跳过 AI 报告优化。"

    payload = _build_ai_payload(result)
    client = OpenAI(api_key=api_key)
    try:
        response = client.responses.create(
            model=model or DEFAULT_AI_MODEL,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(payload)},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "doc_quality_checker_ai_summary",
                    "schema": AI_REPORT_JSON_SCHEMA,
                    "strict": True,
                }
            },
            max_output_tokens=900,
        )
        output_text = getattr(response, "output_text", "")
        if not output_text:
            return None, "AI 返回内容为空，已保留原始规则检测报告。"
        data = json.loads(output_text)
        summary = AIReportSummary(
            overall_comment=data.get("overall_comment", ""),
            main_problems=data.get("main_problems", []),
            priority_suggestions=data.get("priority_suggestions", []),
            polished_summary=data.get("polished_summary", ""),
            risk_notice=data.get("risk_notice", ""),
        )
        return summary, "AI 优化建议已生成。"
    except Exception as exc:
        return None, f"AI 调用失败，已保留原始规则检测报告。原因：{exc}"
