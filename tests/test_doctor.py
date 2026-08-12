from pathlib import Path

from repoready.doctor import inspect_repository
from repoready.models import ProjectProfile


def test_doctor_scores_good_repo(tmp_path: Path) -> None:
    for name in ["README.md", "LICENSE", ".gitignore", ".editorconfig", ".env.example", "SECURITY.md"]:
        (tmp_path / name).write_text("ok", encoding="utf-8")
    (tmp_path / ".github/workflows").mkdir(parents=True)
    (tmp_path / ".github/workflows/ci.yml").write_text("name: CI", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    report = inspect_repository(tmp_path, ProjectProfile.PYTHON)
    assert report.score >= 80
    assert report.detected_profile is ProjectProfile.PYTHON


def test_doctor_reports_suggestions(tmp_path: Path) -> None:
    report = inspect_repository(tmp_path)
    assert report.score < 80
    assert report.suggestions


def test_doctor_detects_cache_junk(tmp_path: Path) -> None:
    (tmp_path / ".pytest_cache").mkdir()
    report = inspect_repository(tmp_path)
    assert any("cache" in check.message.lower() for check in report.checks)
