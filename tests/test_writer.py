from pathlib import Path

import pytest

from repoready.exceptions import UnsafePathError
from repoready.models import FileState, GeneratedFile, SetupOptions
from repoready.writer import build_plan, create_backup, list_backups, render_plan_diff, restore_backup, write_plan


def file(path: str, content: str = "content\n") -> GeneratedFile:
    return GeneratedFile(path=path, content=content, group="test", description="test")


def test_build_plan_creates_missing_file(tmp_path: Path) -> None:
    plan = build_plan([file(".editorconfig")], SetupOptions(root=tmp_path))
    assert plan[0].state is FileState.CREATE


def test_build_plan_skips_existing_without_force(tmp_path: Path) -> None:
    (tmp_path / ".editorconfig").write_text("old\n", encoding="utf-8")
    plan = build_plan([file(".editorconfig", "new\n")], SetupOptions(root=tmp_path))
    assert plan[0].state is FileState.SKIP


def test_build_plan_overwrites_with_force(tmp_path: Path) -> None:
    (tmp_path / ".editorconfig").write_text("old\n", encoding="utf-8")
    plan = build_plan([file(".editorconfig", "new\n")], SetupOptions(root=tmp_path, force=True))
    assert plan[0].state is FileState.OVERWRITE


def test_write_plan_writes_files(tmp_path: Path) -> None:
    plan = build_plan([file("nested/file.txt")], SetupOptions(root=tmp_path))
    write_plan(plan)
    assert (tmp_path / "nested/file.txt").read_text(encoding="utf-8") == "content\n"


def test_unsafe_path_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(UnsafePathError):
        build_plan([file("../outside.txt")], SetupOptions(root=tmp_path))


def test_diff_contains_file_name(tmp_path: Path) -> None:
    plan = build_plan([file("README.md", "hello\n")], SetupOptions(root=tmp_path))
    diff = render_plan_diff(plan)
    assert "README.md" in diff


def test_backup_and_restore(tmp_path: Path) -> None:
    target = tmp_path / "README.md"
    target.write_text("old\n", encoding="utf-8")
    plan = build_plan([file("README.md", "new\n")], SetupOptions(root=tmp_path, force=True))
    backup = create_backup(plan, tmp_path)
    assert backup is not None
    write_plan(plan)
    assert target.read_text(encoding="utf-8") == "new\n"
    restored = restore_backup(tmp_path, backup.backup_id)
    assert restored == ["README.md"]
    assert target.read_text(encoding="utf-8") == "old\n"
    assert backup.backup_id in list_backups(tmp_path)
