from pathlib import Path

from typer.testing import CliRunner

from repoready.cli import app

runner = CliRunner()


def test_cli_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "RepoReady" in result.output


def test_cli_list() -> None:
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "python" in result.output


def test_cli_preview(tmp_path: Path) -> None:
    result = runner.invoke(app, ["preview", str(tmp_path), "--profile", "python"])
    assert result.exit_code == 0
    assert "RepoReady Plan" in result.output


def test_cli_setup_dry_run_does_not_write(tmp_path: Path) -> None:
    result = runner.invoke(app, ["setup", str(tmp_path), "--profile", "python", "--dry-run"])
    assert result.exit_code == 0
    assert not (tmp_path / ".gitignore").exists()


def test_cli_setup_writes_files(tmp_path: Path) -> None:
    result = runner.invoke(app, ["setup", str(tmp_path), "--profile", "python"])
    assert result.exit_code == 0
    assert (tmp_path / ".gitignore").exists()
    assert (tmp_path / ".github/workflows/ci.yml").exists()


def test_cli_doctor_json(tmp_path: Path) -> None:
    result = runner.invoke(app, ["doctor", str(tmp_path), "--format", "json"])
    assert result.exit_code == 0
    assert '"score"' in result.output


def test_cli_init(tmp_path: Path) -> None:
    result = runner.invoke(app, ["init", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / ".repoready.yaml").exists()


def test_cli_clean_apply(tmp_path: Path) -> None:
    (tmp_path / ".pytest_cache").mkdir()
    result = runner.invoke(app, ["clean", str(tmp_path), "--apply"])
    assert result.exit_code == 0
    assert not (tmp_path / ".pytest_cache").exists()
