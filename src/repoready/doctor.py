"""Repository health checks."""

from __future__ import annotations

from pathlib import Path
from typing import List

from .cleanup import find_clean_items
from .detector import resolve_profile
from .models import CheckStatus, DoctorCheck, DoctorReport, ProjectProfile
from .utils import has_any


def inspect_repository(root: Path, requested_profile: ProjectProfile = ProjectProfile.AUTO) -> DoctorReport:
    """Inspect repository setup quality."""

    profile = resolve_profile(root, requested_profile)
    checks: List[DoctorCheck] = []
    checks.extend(_common_checks(root))
    checks.extend(_github_checks(root))
    checks.extend(_profile_checks(root, profile))
    checks.extend(_cleanliness_checks(root))
    score = _score(checks)
    status = _status(score)
    return DoctorReport(root=root, detected_profile=profile, score=score, status=status, checks=checks)


def _common_checks(root: Path) -> List[DoctorCheck]:
    return [
        _exists(root, ["README.md", "readme.md"], "README", "README file found", "Add a clear README.md", 12),
        _exists(root, ["LICENSE", "LICENSE.md", "license"], "License", "License file found", "Add an open-source license", 8),
        _exists(root, [".gitignore"], "Gitignore", ".gitignore found", "Add a .gitignore file", 6),
        _exists(root, [".editorconfig"], "EditorConfig", ".editorconfig found", "Add .editorconfig for consistent editor behavior", 4),
        _exists(root, [".env.example"], "Env example", ".env.example found", "Add .env.example without real secrets", 5),
        _exists(root, ["SECURITY.md"], "Security policy", "SECURITY.md found", "Add SECURITY.md", 5),
        _exists(root, ["CONTRIBUTING.md"], "Contribution guide", "CONTRIBUTING.md found", "Add CONTRIBUTING.md", 4, warn_only=True),
    ]


def _github_checks(root: Path) -> List[DoctorCheck]:
    return [
        _exists(root, [".github/workflows/ci.yml", ".github/workflows/ci.yaml"], "CI workflow", "CI workflow found", "Add a GitHub Actions CI workflow", 8),
        _exists(root, [".github/dependabot.yml", ".github/dependabot.yaml"], "Dependabot", "Dependabot config found", "Add Dependabot for dependency updates", 4, warn_only=True),
        _exists(root, [".github/PULL_REQUEST_TEMPLATE.md"], "Pull request template", "Pull request template found", "Add a pull request template", 3, warn_only=True),
        _exists(root, [".github/ISSUE_TEMPLATE/bug_report.md", ".github/ISSUE_TEMPLATE/feature_request.md"], "Issue templates", "Issue templates found", "Add GitHub issue templates", 3, warn_only=True),
    ]


def _profile_checks(root: Path, profile: ProjectProfile) -> List[DoctorCheck]:
    if profile is ProjectProfile.PYTHON:
        return [
            _exists(root, ["pyproject.toml", "setup.py", "setup.cfg"], "Python packaging", "Python package metadata found", "Add pyproject.toml", 8),
            _exists(root, ["tests", "test"], "Tests", "Test folder found", "Add tests/", 7),
            _exists(root, ["ruff.toml", ".ruff.toml", "pyproject.toml"], "Ruff config", "Ruff configuration found", "Add Ruff configuration", 3, warn_only=True),
            _exists(root, ["mypy.ini", "pyproject.toml"], "Mypy config", "Type checking configuration found", "Add mypy configuration", 3, warn_only=True),
        ]
    if profile is ProjectProfile.NODE or profile is ProjectProfile.WEB:
        return [
            _exists(root, ["package.json"], "Package file", "package.json found", "Add package.json", 8),
            _exists(root, [".prettierrc", "prettier.config.js"], "Prettier", "Prettier configuration found", "Add Prettier configuration", 4, warn_only=True),
            _exists(root, ["src", "app", "pages"], "Source folder", "Source folder found", "Add a source folder", 4, warn_only=True),
        ]
    if profile is ProjectProfile.GO:
        return [
            _exists(root, ["go.mod"], "Go module", "go.mod found", "Run go mod init", 10),
            _exists(root, [".golangci.yml"], "Go lint config", "Go lint configuration found", "Add .golangci.yml", 4, warn_only=True),
        ]
    if profile is ProjectProfile.RUST:
        return [
            _exists(root, ["Cargo.toml"], "Cargo manifest", "Cargo.toml found", "Add Cargo.toml", 10),
            _exists(root, ["rustfmt.toml"], "Rustfmt", "Rust formatting config found", "Add rustfmt.toml", 4, warn_only=True),
        ]
    if profile is ProjectProfile.DOCKER:
        return [
            _exists(root, ["Dockerfile"], "Dockerfile", "Dockerfile found", "Add Dockerfile", 9),
            _exists(root, [".dockerignore"], "Dockerignore", ".dockerignore found", "Add .dockerignore", 5),
        ]
    return []


def _cleanliness_checks(root: Path) -> List[DoctorCheck]:
    junk = find_clean_items(root, include_dependencies=False)
    if not junk:
        return [DoctorCheck("Clean workspace", CheckStatus.PASS, "No common cache/build junk found", 5)]
    return [
        DoctorCheck(
            "Clean workspace",
            CheckStatus.WARN,
            f"Found {len(junk)} removable cache/build item(s)",
            5,
            "Run `repoready clean --dry-run` and remove unnecessary cache/build files",
        )
    ]


def _exists(
    root: Path,
    names: List[str],
    name: str,
    pass_message: str,
    suggestion: str,
    weight: int,
    warn_only: bool = False,
) -> DoctorCheck:
    if has_any(root, names):
        return DoctorCheck(name, CheckStatus.PASS, pass_message, weight)
    status = CheckStatus.WARN if warn_only else CheckStatus.FAIL
    return DoctorCheck(name, status, f"Missing {names[0]}", weight, suggestion)


def _score(checks: List[DoctorCheck]) -> int:
    total = sum(max(check.weight, 0) for check in checks)
    if total <= 0:
        return 100
    earned = 0
    for check in checks:
        if check.status is CheckStatus.PASS:
            earned += check.weight
        elif check.status is CheckStatus.WARN:
            earned += int(check.weight * 0.35)
    return max(0, min(100, round((earned / total) * 100)))


def _status(score: int) -> str:
    if score >= 90:
        return "excellent"
    if score >= 75:
        return "good"
    if score >= 60:
        return "needs work"
    return "poor"
