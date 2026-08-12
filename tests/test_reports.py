from pathlib import Path

from repoready.doctor import inspect_repository
from repoready.models import ProjectProfile
from repoready.reports import render_doctor_json, render_doctor_markdown, render_summary


def test_markdown_report_contains_score(tmp_path: Path) -> None:
    report = inspect_repository(tmp_path, ProjectProfile.GENERAL)
    md = render_doctor_markdown(report)
    assert "RepoReady Report" in md
    assert "Score" in md


def test_json_report_contains_profile(tmp_path: Path) -> None:
    report = inspect_repository(tmp_path, ProjectProfile.GENERAL)
    js = render_doctor_json(report)
    assert '"profile"' in js


def test_render_summary_skips_zero_values() -> None:
    assert render_summary({"create": 2, "skip": 0}) == "create: 2"
