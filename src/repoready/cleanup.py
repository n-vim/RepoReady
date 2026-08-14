"""Workspace cleanup helpers."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import List

from .models import CleanItem
from .utils import directory_size

JUNK_DIRS = {
    "__pycache__": "Python bytecode cache",
    ".pytest_cache": "Pytest cache",
    ".mypy_cache": "Mypy cache",
    ".ruff_cache": "Ruff cache",
    "htmlcov": "Coverage HTML output",
    "dist": "Distribution build output",
    "build": "Build output",
    ".tox": "Tox environment cache",
    ".coverage": "Coverage data file",
}

DEPENDENCY_DIRS = {
    "node_modules": "Node dependency folder",
    ".venv": "Python virtual environment",
    "venv": "Python virtual environment",
}


def find_clean_items(root: Path, include_dependencies: bool = False) -> List[CleanItem]:
    """Find common cache/build items that can be cleaned."""

    names = dict(JUNK_DIRS)
    if include_dependencies:
        names.update(DEPENDENCY_DIRS)
    items: List[CleanItem] = []
    for path in root.rglob("*"):
        if ".git" in path.relative_to(root).parts:
            continue
        name = path.name
        if name in names:
            items.append(
                CleanItem(
                    path=path,
                    relative_path=path.relative_to(root).as_posix(),
                    reason=names[name],
                    size_bytes=directory_size(path),
                    is_dir=path.is_dir(),
                )
            )
    items.sort(key=lambda item: item.relative_path)
    return items


def remove_clean_items(items: List[CleanItem]) -> List[str]:
    """Remove cleanup items and return removed relative paths."""

    removed: List[str] = []
    for item in items:
        if not item.path.exists():
            continue
        if item.path.is_dir():
            shutil.rmtree(item.path)
        else:
            item.path.unlink()
        removed.append(item.relative_path)
    return removed
