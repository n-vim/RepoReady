"""Utility helpers for RepoReady."""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path
from typing import Iterable, List, Optional

from .exceptions import UnsafePathError


def ensure_repository_root(path: Path) -> Path:
    """Return a normalized existing repository path.

    RepoReady works on local folders. The folder does not need to be a git repository,
    but it must exist and be a directory.
    """

    root = path.expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Repository path does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {root}")
    return root


def normalize_relative_path(value: str) -> Path:
    """Validate and normalize a generated relative path."""

    raw = value.replace("\\", "/").strip()
    if not raw:
        raise UnsafePathError("Generated path cannot be empty")
    path = Path(raw)
    if path.is_absolute():
        raise UnsafePathError(f"Generated path must be relative: {value}")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise UnsafePathError(f"Generated path contains unsafe segment: {value}")
    return path


def safe_join(root: Path, relative: str) -> Path:
    """Join a safe relative path under root and prevent traversal."""

    normalized = normalize_relative_path(relative)
    target = (root / normalized).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise UnsafePathError(f"Target path escapes repository root: {relative}") from exc
    return target


def read_text(path: Path) -> str:
    """Read UTF-8 text with replacement for unusual files."""

    return path.read_text(encoding="utf-8", errors="replace")


def write_text_atomic(path: Path, content: str) -> None:
    """Write a file atomically."""

    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        Path(temp_name).replace(path)
    finally:
        temp = Path(temp_name)
        if temp.exists():
            temp.unlink()


def sha256_text(content: str) -> str:
    """Hash text content."""

    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def has_any(root: Path, names: Iterable[str]) -> bool:
    """Return True if any relative path exists under root."""

    return any((root / name).exists() for name in names)


def first_existing(root: Path, names: Iterable[str]) -> Optional[Path]:
    """Return the first existing relative path."""

    for name in names:
        path = root / name
        if path.exists():
            return path
    return None


def directory_size(path: Path) -> int:
    """Return approximate total size of a file or directory."""

    if path.is_file():
        return path.stat().st_size
    total = 0
    for child in path.rglob("*"):
        if child.is_file():
            try:
                total += child.stat().st_size
            except OSError:
                continue
    return total


def format_bytes(size: int) -> str:
    """Format bytes as a short human-readable string."""

    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024


def sorted_relative_files(root: Path, limit: int = 5000) -> List[str]:
    """Return sorted relative file names for lightweight inspection."""

    results: List[str] = []
    ignored_dirs = {".git", ".venv", "venv", "node_modules", ".repoready"}
    for path in root.rglob("*"):
        if len(results) >= limit:
            break
        if any(part in ignored_dirs for part in path.relative_to(root).parts):
            continue
        if path.is_file():
            results.append(path.relative_to(root).as_posix())
    return sorted(results)
