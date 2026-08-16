"""Planning, writing, diffing, and backup operations."""

from __future__ import annotations

import difflib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from .exceptions import BackupError
from .models import BackupRecord, FileAction, FileState, GeneratedFile, SetupOptions
from .utils import read_text, safe_join, sha256_text, write_text_atomic

BACKUP_ROOT = ".repoready/backups"
MANIFEST_PATH = ".repoready/manifest.json"


def build_plan(files: Sequence[GeneratedFile], options: SetupOptions) -> List[FileAction]:
    """Build a safe write plan for generated files."""

    actions: List[FileAction] = []
    for file in files:
        target = safe_join(options.root, file.path)
        if not target.exists():
            actions.append(FileAction(file=file, state=FileState.CREATE, target=target, reason="missing"))
            continue
        current = read_text(target)
        if current == file.content:
            actions.append(FileAction(file=file, state=FileState.SAME, target=target, reason="unchanged"))
        elif options.force:
            actions.append(FileAction(file=file, state=FileState.OVERWRITE, target=target, reason="force enabled"))
        else:
            actions.append(FileAction(file=file, state=FileState.SKIP, target=target, reason="already exists"))
    return actions


def write_plan(plan: Sequence[FileAction]) -> List[Path]:
    """Write create and overwrite actions."""

    written: List[Path] = []
    for action in plan:
        if action.state in {FileState.CREATE, FileState.OVERWRITE}:
            write_text_atomic(action.target, action.file.content)
            written.append(action.target)
    return written


def render_plan_diff(plan: Sequence[FileAction], include_skipped: bool = False) -> str:
    """Render unified diffs for planned file changes."""

    chunks: List[str] = []
    for action in plan:
        if action.state is FileState.SAME:
            continue
        if action.state is FileState.SKIP and not include_skipped:
            continue
        old = read_text(action.target).splitlines() if action.target.exists() else []
        new = action.file.content.splitlines()
        fromfile = f"a/{action.file.path}" if old else "/dev/null"
        tofile = f"b/{action.file.path}"
        diff = difflib.unified_diff(old, new, fromfile=fromfile, tofile=tofile, lineterm="")
        text = "\n".join(diff)
        if text:
            chunks.append(text)
    return "\n\n".join(chunks)


def create_backup(plan: Sequence[FileAction], root: Path) -> Optional[BackupRecord]:
    """Create a backup for files that will be overwritten."""

    overwrite_actions = [action for action in plan if action.state is FileState.OVERWRITE]
    if not overwrite_actions:
        return None
    backup_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_root = root / BACKUP_ROOT / backup_id
    backup_root.mkdir(parents=True, exist_ok=True)
    files: List[str] = []
    for action in overwrite_actions:
        rel = action.file.path
        destination = backup_root / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(action.target, destination)
        files.append(rel)
    manifest = {
        "backup_id": backup_id,
        "created_at": backup_id,
        "files": files,
    }
    manifest_path = backup_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return BackupRecord(backup_id=backup_id, root=backup_root, files=files, manifest_path=manifest_path)


def list_backups(root: Path) -> List[str]:
    """List backup identifiers."""

    backup_root = root / BACKUP_ROOT
    if not backup_root.exists():
        return []
    return sorted([path.name for path in backup_root.iterdir() if path.is_dir()], reverse=True)


def restore_backup(root: Path, backup_id: str) -> List[str]:
    """Restore files from a backup."""

    backup_root = root / BACKUP_ROOT / backup_id
    manifest_path = backup_root / "manifest.json"
    if not manifest_path.exists():
        raise BackupError(f"Backup not found: {backup_id}")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    restored: List[str] = []
    for rel in data.get("files", []):
        source = backup_root / rel
        target = safe_join(root, rel)
        if not source.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        restored.append(str(rel))
    return restored


def write_manifest(plan: Sequence[FileAction], root: Path) -> Path:
    """Write a RepoReady manifest describing generated files."""

    items: List[Dict[str, str]] = []
    for action in plan:
        if action.state in {FileState.CREATE, FileState.OVERWRITE, FileState.SAME}:
            items.append(
                {
                    "path": action.file.path,
                    "group": action.file.group,
                    "state": action.state.value,
                    "sha256": sha256_text(action.file.content),
                }
            )
    manifest = {
        "tool": "RepoReady",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "files": items,
    }
    path = root / MANIFEST_PATH
    write_text_atomic(path, json.dumps(manifest, indent=2) + "\n")
    return path


def summarize_plan(plan: Sequence[FileAction]) -> Dict[str, int]:
    """Count actions by state."""

    summary = {state.value: 0 for state in FileState}
    for action in plan:
        summary[action.state.value] += 1
    return summary
