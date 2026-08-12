from pathlib import Path

from repoready.detector import detect_all_profiles, detect_primary_profile, detect_profile_scores
from repoready.models import ProjectProfile


def test_detect_python_project(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    assert detect_primary_profile(tmp_path) is ProjectProfile.PYTHON


def test_detect_node_project(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text("{}", encoding="utf-8")
    assert detect_primary_profile(tmp_path) is ProjectProfile.NODE


def test_detect_general_when_no_markers(tmp_path: Path) -> None:
    assert detect_all_profiles(tmp_path) == [ProjectProfile.GENERAL]


def test_detection_scores_sorted(tmp_path: Path) -> None:
    (tmp_path / "go.mod").write_text("module example.com/app", encoding="utf-8")
    scores = detect_profile_scores(tmp_path)
    assert scores[0][0] is ProjectProfile.GO
    assert scores[0][1] > 0
