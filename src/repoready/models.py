"""Shared models for RepoReady."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


class ProjectProfile(str, Enum):
    """Project setup profiles supported by RepoReady."""

    AUTO = "auto"
    GENERAL = "general"
    PYTHON = "python"
    NODE = "node"
    GO = "go"
    RUST = "rust"
    WEB = "web"
    DOCKER = "docker"


class SetupLevel(str, Enum):
    """How many files RepoReady should prepare."""

    MINIMAL = "minimal"
    STANDARD = "standard"
    STRICT = "strict"


class OutputFormat(str, Enum):
    """Report output formats."""

    TERMINAL = "terminal"
    MARKDOWN = "markdown"
    JSON = "json"


class FileState(str, Enum):
    """Planned write state for a generated file."""

    CREATE = "create"
    OVERWRITE = "overwrite"
    SKIP = "skip"
    SAME = "same"


class CheckStatus(str, Enum):
    """Doctor check status."""

    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    INFO = "info"


@dataclass(frozen=True)
class ProfileInfo:
    """Metadata shown in profile commands."""

    profile: ProjectProfile
    title: str
    description: str
    markers: Tuple[str, ...] = ()
    generated_groups: Tuple[str, ...] = ()


@dataclass(frozen=True)
class GeneratedFile:
    """A generated file before writing to disk."""

    path: str
    content: str
    group: str
    description: str


@dataclass(frozen=True)
class FileAction:
    """A planned file action."""

    file: GeneratedFile
    state: FileState
    target: Path
    reason: str


@dataclass
class SetupOptions:
    """Options controlling setup generation."""

    root: Path
    profile: ProjectProfile = ProjectProfile.AUTO
    level: SetupLevel = SetupLevel.STANDARD
    force: bool = False
    backup: bool = True
    include_github: bool = True
    include_security: bool = True
    include_editorconfig: bool = True
    include_env: bool = True
    include_dependabot: bool = True
    include_docker: bool = False
    include_precommit: bool = True
    include_language_configs: bool = True


@dataclass
class RepoReadyConfig:
    """Parsed .repoready.yaml configuration."""

    profile: ProjectProfile = ProjectProfile.AUTO
    level: SetupLevel = SetupLevel.STANDARD
    include_github: bool = True
    include_security: bool = True
    include_editorconfig: bool = True
    include_env: bool = True
    include_dependabot: bool = True
    include_docker: bool = False
    include_precommit: bool = True
    include_language_configs: bool = True
    ignore: List[str] = field(default_factory=list)
    fail_below: int = 60
    warn_below: int = 80

    @classmethod
    def from_mapping(cls, data: Dict[str, Any]) -> "RepoReadyConfig":
        """Create config from a YAML mapping."""

        profile = ProjectProfile(str(data.get("profile", ProjectProfile.AUTO.value)))
        level = SetupLevel(str(data.get("level", SetupLevel.STANDARD.value)))
        checks = data.get("checks", {}) or {}
        score = data.get("score", {}) or {}
        ignore = data.get("ignore", []) or []
        if not isinstance(ignore, list):
            ignore = []
        return cls(
            profile=profile,
            level=level,
            include_github=bool(checks.get("github", data.get("include_github", True))),
            include_security=bool(checks.get("security", data.get("include_security", True))),
            include_editorconfig=bool(checks.get("editorconfig", data.get("include_editorconfig", True))),
            include_env=bool(checks.get("env", data.get("include_env", True))),
            include_dependabot=bool(checks.get("dependabot", data.get("include_dependabot", True))),
            include_docker=bool(checks.get("docker", data.get("include_docker", False))),
            include_precommit=bool(checks.get("precommit", data.get("include_precommit", True))),
            include_language_configs=bool(checks.get("language_configs", data.get("include_language_configs", True))),
            ignore=[str(item) for item in ignore],
            fail_below=int(score.get("fail_below", data.get("fail_below", 60))),
            warn_below=int(score.get("warn_below", data.get("warn_below", 80))),
        )


def config_to_options(root: Path, config: RepoReadyConfig, force: bool = False) -> SetupOptions:
    """Convert config into setup options."""

    return SetupOptions(
        root=root,
        profile=config.profile,
        level=config.level,
        force=force,
        include_github=config.include_github,
        include_security=config.include_security,
        include_editorconfig=config.include_editorconfig,
        include_env=config.include_env,
        include_dependabot=config.include_dependabot,
        include_docker=config.include_docker,
        include_precommit=config.include_precommit,
        include_language_configs=config.include_language_configs,
    )


@dataclass(frozen=True)
class DoctorCheck:
    """Single repository health check."""

    name: str
    status: CheckStatus
    message: str
    weight: int = 1
    suggestion: Optional[str] = None


@dataclass(frozen=True)
class DoctorReport:
    """Repository health report."""

    root: Path
    detected_profile: ProjectProfile
    score: int
    status: str
    checks: Sequence[DoctorCheck]

    @property
    def passed(self) -> List[DoctorCheck]:
        """Passing checks."""

        return [check for check in self.checks if check.status is CheckStatus.PASS]

    @property
    def warnings(self) -> List[DoctorCheck]:
        """Warning and failing checks."""

        return [check for check in self.checks if check.status in {CheckStatus.WARN, CheckStatus.FAIL}]

    @property
    def suggestions(self) -> List[str]:
        """Unique improvement suggestions."""

        seen = set()
        items: List[str] = []
        for check in self.checks:
            if check.suggestion and check.suggestion not in seen:
                seen.add(check.suggestion)
                items.append(check.suggestion)
        return items


@dataclass(frozen=True)
class BackupRecord:
    """Metadata about a backup."""

    backup_id: str
    root: Path
    files: Sequence[str]
    manifest_path: Path


@dataclass(frozen=True)
class CleanItem:
    """A removable repository junk/cache item."""

    path: Path
    relative_path: str
    reason: str
    size_bytes: int
    is_dir: bool
