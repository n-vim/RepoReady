"""Profile metadata and helpers."""

from __future__ import annotations

from typing import Dict, List

from .models import ProfileInfo, ProjectProfile


PROFILE_INFOS: Dict[ProjectProfile, ProfileInfo] = {
    ProjectProfile.AUTO: ProfileInfo(
        ProjectProfile.AUTO,
        "Auto",
        "Detect the repository type from existing files and generate the best matching setup.",
        (),
        ("common",),
    ),
    ProjectProfile.GENERAL: ProfileInfo(
        ProjectProfile.GENERAL,
        "General",
        "A clean default setup for any GitHub repository.",
        ("README.md", "LICENSE", ".git"),
        ("common", "github"),
    ),
    ProjectProfile.PYTHON: ProfileInfo(
        ProjectProfile.PYTHON,
        "Python",
        "Configuration for Python packages, APIs, scripts, and CLI tools.",
        ("pyproject.toml", "requirements.txt", "setup.py", "src/", "tests/"),
        ("common", "github", "python"),
    ),
    ProjectProfile.NODE: ProfileInfo(
        ProjectProfile.NODE,
        "Node",
        "Configuration for JavaScript and TypeScript projects.",
        ("package.json", "pnpm-lock.yaml", "yarn.lock", "tsconfig.json"),
        ("common", "github", "node"),
    ),
    ProjectProfile.GO: ProfileInfo(
        ProjectProfile.GO,
        "Go",
        "Configuration for Go modules, services, and command-line tools.",
        ("go.mod", "go.sum", "main.go"),
        ("common", "github", "go"),
    ),
    ProjectProfile.RUST: ProfileInfo(
        ProjectProfile.RUST,
        "Rust",
        "Configuration for Rust crates and command-line projects.",
        ("Cargo.toml", "Cargo.lock", "src/main.rs"),
        ("common", "github", "rust"),
    ),
    ProjectProfile.WEB: ProfileInfo(
        ProjectProfile.WEB,
        "Web",
        "Configuration for frontend and static web projects.",
        ("index.html", "vite.config.ts", "next.config.js", "astro.config.mjs"),
        ("common", "github", "web"),
    ),
    ProjectProfile.DOCKER: ProfileInfo(
        ProjectProfile.DOCKER,
        "Docker",
        "Configuration for container-focused projects and services.",
        ("Dockerfile", "docker-compose.yml", "compose.yaml", ".dockerignore"),
        ("common", "github", "docker"),
    ),
}


def profile_choices() -> List[str]:
    """Return valid profile values."""

    return [profile.value for profile in ProjectProfile]


def get_profile_info(profile: ProjectProfile) -> ProfileInfo:
    """Return metadata for a profile."""

    return PROFILE_INFOS[profile]
