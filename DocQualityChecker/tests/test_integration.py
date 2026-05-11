"""Integration tests for DOCX-based checks."""

from pathlib import Path

import pytest

pytest.importorskip("docx")

from doc_quality_checker.checker import CheckerConfig, run_check


def test_sample_docx_can_be_checked() -> None:
    """The bundled sample document should produce a non-empty check result."""

    sample_path = Path("examples/sample.docx")
    result = run_check(sample_path, CheckerConfig(max_paragraph_length=120))

    assert result.stats.file_name == "sample.docx"
    assert result.stats.paragraph_count > 0
    assert len(result.issues) > 0
    assert all(issue.rule_id for issue in result.issues)
