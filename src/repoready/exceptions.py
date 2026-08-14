"""Custom exceptions for RepoReady."""

from __future__ import annotations


class RepoReadyError(Exception):
    """Base exception for user-facing RepoReady errors."""


class ConfigError(RepoReadyError):
    """Raised when the RepoReady config file is invalid."""


class UnsafePathError(RepoReadyError):
    """Raised when a generated path is unsafe."""


class BackupError(RepoReadyError):
    """Raised when a backup cannot be created or restored."""


class TemplateError(RepoReadyError):
    """Raised when template generation fails."""
