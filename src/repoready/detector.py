"""Repository profile detection."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

from .models import ProjectProfile


MARKER_SCORES: Dict[ProjectProfile, Dict[str, int]] = {
    ProjectProfile.PYTHON: {
        "pyproject.toml": 10,
        "requirements.txt": 5,
        "setup.py": 6,
        "setup.cfg": 6,
        "tox.ini": 4,
        "src": 3,
        "tests": 2,
    },
    ProjectProfile.NODE: {
        "package.json": 10,
        "pnpm-lock.yaml": 5,
        "yarn.lock": 5,
        "package-lock.json": 5,
        "tsconfig.json": 4,
        "next.config.js": 3,
        "vite.config.ts": 3,
    },
    ProjectProfile.GO: {
        "go.mod": 10,
        "go.sum": 5,
        "main.go": 4,
    },
    ProjectProfile.RUST: {
        "Cargo.toml": 10,
        "Cargo.lock": 5,
        "src/main.rs": 4,
        "src/lib.rs": 4,
    },
    ProjectProfile.WEB: {
        "index.html": 5,
        "public": 3,
        "src/App.tsx": 3,
        "src/App.jsx": 3,
        "vite.config.js": 4,
        "vite.config.ts": 4,
        "astro.config.mjs": 4,
    },
    ProjectProfile.DOCKER: {
        "Dockerfile": 8,
        "docker-compose.yml": 6,
        "compose.yaml": 6,
        ".dockerignore": 3,
    },
}


def _score_profile(root: Path, profile: ProjectProfile) -> int:
    markers = MARKER_SCORES.get(profile, {})
    score = 0
    for marker, value in markers.items():
        if (root / marker).exists():
            score += value
    return score


def detect_profile_scores(root: Path) -> List[Tuple[ProjectProfile, int]]:
    """Return sorted profile scores for a repository."""

    scored = [(profile, _score_profile(root, profile)) for profile in MARKER_SCORES]
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored


def detect_all_profiles(root: Path) -> List[ProjectProfile]:
    """Return all matching profiles ordered by confidence."""

    scored = detect_profile_scores(root)
    matches = [profile for profile, score in scored if score > 0]
    if not matches:
        return [ProjectProfile.GENERAL]
    if ProjectProfile.DOCKER in matches and matches[0] is not ProjectProfile.DOCKER:
        # Docker often complements a language profile, so keep it as a secondary match.
        return matches
    return matches


def detect_primary_profile(root: Path) -> ProjectProfile:
    """Return the best detected profile."""

    return detect_all_profiles(root)[0]


def resolve_profile(root: Path, requested: ProjectProfile) -> ProjectProfile:
    """Resolve auto profile to a concrete profile."""

    if requested is ProjectProfile.AUTO:
        return detect_primary_profile(root)
    return requested
