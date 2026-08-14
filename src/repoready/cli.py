"""Command-line interface for RepoReady."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .cleanup import find_clean_items, remove_clean_items
from .config import CONFIG_FILE_NAME, load_config, write_default_config
from .detector import detect_all_profiles, detect_profile_scores, resolve_profile
from .doctor import inspect_repository
from .exceptions import ConfigError, RepoReadyError, UnsafePathError
from .models import OutputFormat, ProjectProfile, SetupLevel, SetupOptions, config_to_options
from .profiles import PROFILE_INFOS, get_profile_info
from .reports import (
    render_clean_table,
    render_doctor_json,
    render_doctor_markdown,
    render_doctor_terminal,
    render_plan_table,
    render_profile_info,
    render_summary,
)
from .templates import TemplateLibrary
from .utils import ensure_repository_root
from .writer import (
    build_plan,
    create_backup,
    list_backups,
    render_plan_diff,
    restore_backup,
    summarize_plan,
    write_manifest,
    write_plan,
)

app = typer.Typer(
    name="repoready",
    help="Prepare repositories with clean config files, workflows, and setup essentials.",
    no_args_is_help=True,
)
console = Console()


def _version_callback(value: Optional[bool]) -> None:
    if value:
        console.print(f"RepoReady {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show RepoReady version.",
    )
) -> None:
    """RepoReady command group."""


def _build_options(
    root: Path,
    profile: ProjectProfile,
    level: SetupLevel,
    force: bool,
    backup: bool,
    include_docker: bool,
    no_github: bool,
    no_security: bool,
    no_editorconfig: bool,
    no_env: bool,
    no_dependabot: bool,
    no_precommit: bool,
) -> SetupOptions:
    config = load_config(root)
    base = config_to_options(root, config, force=force)
    return SetupOptions(
        root=root,
        profile=profile if profile is not ProjectProfile.AUTO else base.profile,
        level=level if level is not SetupLevel.STANDARD else base.level,
        force=force,
        backup=backup,
        include_github=base.include_github and not no_github,
        include_security=base.include_security and not no_security,
        include_editorconfig=base.include_editorconfig and not no_editorconfig,
        include_env=base.include_env and not no_env,
        include_dependabot=base.include_dependabot and not no_dependabot,
        include_docker=include_docker or base.include_docker,
        include_precommit=base.include_precommit and not no_precommit,
        include_language_configs=base.include_language_configs,
    )


def _plan_for_options(options: SetupOptions):
    resolved = resolve_profile(options.root, options.profile)
    files = TemplateLibrary().build(options.root, resolved, options)
    return resolved, build_plan(files, options)


@app.command()
def setup(
    path: Path = typer.Argument(Path("."), help="Repository path to prepare."),
    profile: ProjectProfile = typer.Option(ProjectProfile.AUTO, "--profile", "-p", help="Setup profile."),
    level: SetupLevel = typer.Option(SetupLevel.STANDARD, "--level", "-l", help="minimal, standard, or strict."),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show the plan without writing files."),
    backup: bool = typer.Option(True, "--backup/--no-backup", help="Back up overwritten files."),
    include_docker: bool = typer.Option(False, "--docker", help="Also generate Docker starter files."),
    no_github: bool = typer.Option(False, "--no-github", help="Do not generate GitHub files."),
    no_security: bool = typer.Option(False, "--no-security", help="Do not generate SECURITY.md."),
    no_editorconfig: bool = typer.Option(False, "--no-editorconfig", help="Do not generate .editorconfig."),
    no_env: bool = typer.Option(False, "--no-env", help="Do not generate .env.example."),
    no_dependabot: bool = typer.Option(False, "--no-dependabot", help="Do not generate Dependabot config."),
    no_precommit: bool = typer.Option(False, "--no-precommit", help="Do not generate pre-commit config."),
) -> None:
    """Generate repository setup files."""

    try:
        root = ensure_repository_root(path)
        options = _build_options(
            root,
            profile,
            level,
            force,
            backup,
            include_docker,
            no_github,
            no_security,
            no_editorconfig,
            no_env,
            no_dependabot,
            no_precommit,
        )
        resolved, plan = _plan_for_options(options)
        console.print(f"Detected profile: [bold]{resolved.value}[/bold]")
        render_plan_table(plan, console)
        console.print(f"Summary: {render_summary(summarize_plan(plan))}")
        if dry_run:
            console.print("[yellow]Dry run enabled. No files were written.[/yellow]")
            return
        backup_record = create_backup(plan, root) if backup else None
        write_plan(plan)
        write_manifest(plan, root)
        if backup_record:
            console.print(f"[green]Backup created:[/green] {backup_record.backup_id}")
        console.print("[green]Repository setup complete.[/green]")
    except (RepoReadyError, ConfigError, UnsafePathError, OSError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc


@app.command()
def preview(
    path: Path = typer.Argument(Path("."), help="Repository path to preview."),
    profile: ProjectProfile = typer.Option(ProjectProfile.AUTO, "--profile", "-p", help="Setup profile."),
    level: SetupLevel = typer.Option(SetupLevel.STANDARD, "--level", "-l", help="minimal, standard, or strict."),
    include_docker: bool = typer.Option(False, "--docker", help="Include Docker starter files."),
) -> None:
    """Preview files RepoReady would create."""

    root = ensure_repository_root(path)
    options = _build_options(root, profile, level, False, True, include_docker, False, False, False, False, False, False)
    resolved, plan = _plan_for_options(options)
    console.print(f"Detected profile: [bold]{resolved.value}[/bold]")
    render_plan_table(plan, console)
    console.print(f"Summary: {render_summary(summarize_plan(plan))}")


@app.command(name="diff")
def diff_command(
    path: Path = typer.Argument(Path("."), help="Repository path to diff."),
    profile: ProjectProfile = typer.Option(ProjectProfile.AUTO, "--profile", "-p", help="Setup profile."),
    level: SetupLevel = typer.Option(SetupLevel.STANDARD, "--level", "-l", help="minimal, standard, or strict."),
    force: bool = typer.Option(False, "--force", help="Show overwrite diffs for existing files."),
    include_skipped: bool = typer.Option(False, "--include-skipped", help="Also diff skipped files."),
) -> None:
    """Show unified diffs for generated files."""

    root = ensure_repository_root(path)
    options = _build_options(root, profile, level, force, True, False, False, False, False, False, False, False)
    _, plan = _plan_for_options(options)
    diff = render_plan_diff(plan, include_skipped=include_skipped)
    if not diff:
        console.print("[green]No diff to show.[/green]")
        return
    console.print(diff, soft_wrap=True)


@app.command()
def doctor(
    path: Path = typer.Argument(Path("."), help="Repository path to inspect."),
    profile: ProjectProfile = typer.Option(ProjectProfile.AUTO, "--profile", "-p", help="Profile to inspect."),
    format: OutputFormat = typer.Option(OutputFormat.TERMINAL, "--format", "-f", help="terminal, markdown, or json."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write report to a file."),
    fail_below: Optional[int] = typer.Option(None, "--fail-below", help="Exit with code 1 below this score."),
) -> None:
    """Check repository setup quality."""

    root = ensure_repository_root(path)
    report = inspect_repository(root, profile)
    if format is OutputFormat.TERMINAL:
        render_doctor_terminal(report, console)
    else:
        content = render_doctor_markdown(report) if format is OutputFormat.MARKDOWN else render_doctor_json(report)
        if output:
            output.write_text(content, encoding="utf-8")
            console.print(f"[green]Report written:[/green] {output}")
        else:
            console.print(content)
    if fail_below is not None and report.score < fail_below:
        raise typer.Exit(code=1)


@app.command(name="list")
def list_profiles() -> None:
    """List available profiles."""

    table = Table(title="RepoReady Profiles")
    table.add_column("Profile")
    table.add_column("Description")
    table.add_column("Markers")
    for profile, info in PROFILE_INFOS.items():
        table.add_row(profile.value, info.description, ", ".join(info.markers) or "-")
    console.print(table)


@app.command()
def info(profile: ProjectProfile = typer.Argument(..., help="Profile name.")) -> None:
    """Show profile details."""

    console.print(render_profile_info(get_profile_info(profile)))


@app.command()
def detect(path: Path = typer.Argument(Path("."), help="Repository path to detect."), scores: bool = typer.Option(False, "--scores", help="Show profile scores.")) -> None:
    """Detect the repository profile."""

    root = ensure_repository_root(path)
    matches = detect_all_profiles(root)
    console.print(f"Detected profile: [bold]{matches[0].value}[/bold]")
    if len(matches) > 1:
        console.print("Also matched: " + ", ".join(profile.value for profile in matches[1:]))
    if scores:
        table = Table(title="Detection Scores")
        table.add_column("Profile")
        table.add_column("Score")
        for profile, score in detect_profile_scores(root):
            table.add_row(profile.value, str(score))
        console.print(table)


@app.command()
def init(
    path: Path = typer.Argument(Path("."), help="Repository path."),
    force: bool = typer.Option(False, "--force", help="Overwrite existing config."),
) -> None:
    """Create a .repoready.yaml config file."""

    root = ensure_repository_root(path)
    config_path = write_default_config(root, force=force)
    console.print(f"[green]Config ready:[/green] {config_path.relative_to(root)}")


@app.command()
def backups(path: Path = typer.Argument(Path("."), help="Repository path.")) -> None:
    """List available RepoReady backups."""

    root = ensure_repository_root(path)
    items = list_backups(root)
    if not items:
        console.print("No backups found.")
        return
    for item in items:
        console.print(item)


@app.command()
def restore(
    backup_id: str = typer.Argument(..., help="Backup identifier from `repoready backups`."),
    path: Path = typer.Argument(Path("."), help="Repository path."),
) -> None:
    """Restore files from a RepoReady backup."""

    root = ensure_repository_root(path)
    restored = restore_backup(root, backup_id)
    if not restored:
        console.print("[yellow]No files restored.[/yellow]")
        return
    console.print("[green]Restored files:[/green]")
    for file in restored:
        console.print(f"- {file}")


@app.command()
def clean(
    path: Path = typer.Argument(Path("."), help="Repository path."),
    dry_run: bool = typer.Option(True, "--dry-run/--apply", help="Preview cleanup by default. Use --apply to remove."),
    dependencies: bool = typer.Option(False, "--dependencies", help="Also include dependency folders like node_modules and .venv."),
) -> None:
    """Find or remove common cache/build junk."""

    root = ensure_repository_root(path)
    items = find_clean_items(root, include_dependencies=dependencies)
    if not items:
        console.print("[green]No cleanup candidates found.[/green]")
        return
    render_clean_table(items, console)
    if dry_run:
        console.print("[yellow]Dry run enabled. Use --apply to remove these items.[/yellow]")
        return
    removed = remove_clean_items(items)
    console.print(f"[green]Removed {len(removed)} item(s).[/green]")
