"""Tests for the command line interface."""

from doc_quality_checker.cli import main


def test_cli_reports_missing_file(capsys) -> None:
    """CLI should show a friendly message when the input file is missing."""

    exit_code = main(["--file", "examples/does_not_exist.docx"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "检测失败：" in captured.out
    assert "文件不存在" in captured.out
