"""Configuration loading for RepoReady."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

from .exceptions import ConfigError
from .models import RepoReadyConfig
from .utils import write_text_atomic

CONFIG_FILE_NAME = ".repoready.yaml"

DEFAULT_CONFIG = """# RepoReady configuration
profile: auto
level: standard

checks:
  github: true
  security: true
  editorconfig: true
  env: true
  dependabot: true
  docker: false
  precommit: true
  language_configs: true

score:
  warn_below: 80
  fail_below: 60

ignore:
  - .git
  - .venv
  - node_modules
  - .repoready
"""


def load_config(root: Path) -> RepoReadyConfig:
    """Load .repoready.yaml from a repository if present."""

    path = root / CONFIG_FILE_NAME
    if not path.exists():
        return RepoReadyConfig()
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML in {CONFIG_FILE_NAME}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ConfigError(f"{CONFIG_FILE_NAME} must contain a YAML mapping")
    try:
        return RepoReadyConfig.from_mapping(raw)  # type: ignore[arg-type]
    except ValueError as exc:
        raise ConfigError(f"Invalid {CONFIG_FILE_NAME}: {exc}") from exc


def write_default_config(root: Path, force: bool = False) -> Path:
    """Write a default config file."""

    path = root / CONFIG_FILE_NAME
    if path.exists() and not force:
        return path
    write_text_atomic(path, DEFAULT_CONFIG)
    return path


def config_as_dict(config: RepoReadyConfig) -> Dict[str, Any]:
    """Return a serializable config dictionary."""

    return {
        "profile": config.profile.value,
        "level": config.level.value,
        "checks": {
            "github": config.include_github,
            "security": config.include_security,
            "editorconfig": config.include_editorconfig,
            "env": config.include_env,
            "dependabot": config.include_dependabot,
            "docker": config.include_docker,
            "precommit": config.include_precommit,
            "language_configs": config.include_language_configs,
        },
        "score": {"warn_below": config.warn_below, "fail_below": config.fail_below},
        "ignore": list(config.ignore),
    }
