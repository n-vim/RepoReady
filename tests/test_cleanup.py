from pathlib import Path

from repoready.cleanup import find_clean_items, remove_clean_items


def test_find_clean_items(tmp_path: Path) -> None:
    (tmp_path / ".pytest_cache").mkdir()
    items = find_clean_items(tmp_path)
    assert [item.relative_path for item in items] == [".pytest_cache"]


def test_remove_clean_items(tmp_path: Path) -> None:
    (tmp_path / "build").mkdir()
    items = find_clean_items(tmp_path)
    removed = remove_clean_items(items)
    assert removed == ["build"]
    assert not (tmp_path / "build").exists()


def test_dependency_folders_are_optional(tmp_path: Path) -> None:
    (tmp_path / "node_modules").mkdir()
    assert find_clean_items(tmp_path) == []
    assert find_clean_items(tmp_path, include_dependencies=True)
