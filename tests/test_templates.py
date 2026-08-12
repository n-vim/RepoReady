from pathlib import Path

from repoready.models import ProjectProfile, SetupLevel, SetupOptions
from repoready.templates import TemplateLibrary


def build(tmp_path: Path, profile: ProjectProfile, level: SetupLevel = SetupLevel.STANDARD):
    return TemplateLibrary().build(tmp_path, profile, SetupOptions(root=tmp_path, profile=profile, level=level))


def test_python_templates_include_expected_files(tmp_path: Path) -> None:
    files = build(tmp_path, ProjectProfile.PYTHON)
    paths = {file.path for file in files}
    assert ".gitignore" in paths
    assert "ruff.toml" in paths
    assert "mypy.ini" in paths
    assert ".github/workflows/ci.yml" in paths


def test_strict_level_adds_contributing(tmp_path: Path) -> None:
    files = build(tmp_path, ProjectProfile.PYTHON, SetupLevel.STRICT)
    assert "CONTRIBUTING.md" in {file.path for file in files}


def test_minimal_level_skips_security_and_dependabot(tmp_path: Path) -> None:
    files = build(tmp_path, ProjectProfile.PYTHON, SetupLevel.MINIMAL)
    paths = {file.path for file in files}
    assert "SECURITY.md" not in paths
    assert ".github/dependabot.yml" not in paths


def test_docker_option_adds_docker_files(tmp_path: Path) -> None:
    options = SetupOptions(root=tmp_path, profile=ProjectProfile.PYTHON, include_docker=True)
    files = TemplateLibrary().build(tmp_path, ProjectProfile.PYTHON, options)
    paths = {file.path for file in files}
    assert "Dockerfile" in paths
    assert "compose.yaml" in paths
    assert ".dockerignore" in paths


def test_generated_paths_are_unique(tmp_path: Path) -> None:
    files = build(tmp_path, ProjectProfile.WEB)
    paths = [file.path for file in files]
    assert len(paths) == len(set(paths))
