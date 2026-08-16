"""Report rendering for terminal, Markdown, and JSON."""

from __future__ import annotations

import json
from typing import Dict, List, Sequence

from rich.console import Console
from rich.table import Table

from .models import CheckStatus, CleanItem, DoctorReport, FileAction, FileState, ProfileInfo
from .utils import format_bytes


def render_plan_table(plan: Sequence[FileAction], console: Console) -> None:
    """Render a setup plan table."""

    table = Table(title="RepoReady Plan")
    table.add_column("State")
    table.add_column("File")
    table.add_column("Group")
    table.add_column("Reason")
    for action in plan:
        style = {
            FileState.CREATE: "green",
            FileState.OVERWRITE: "yellow",
            FileState.SKIP: "red",
            FileState.SAME: "cyan",
        }[action.state]
        table.add_row(f"[{style}]{action.state.value}[/{style}]", action.file.path, action.file.group, action.reason)
    console.print(table)


def render_summary(summary: Dict[str, int]) -> str:
    """Render compact plan summary."""

    return ", ".join(f"{key}: {value}" for key, value in summary.items() if value)


def render_doctor_terminal(report: DoctorReport, console: Console) -> None:
    """Render a doctor report in the terminal."""

    console.print(f"[bold]RepoReady Doctor[/bold]")
    console.print(f"Repository: {report.root}")
    console.print(f"Profile: [bold]{report.detected_profile.value}[/bold]")
    console.print(f"Score: [bold]{report.score}/100[/bold] ({report.status})")
    table = Table(title="Checks")
    table.add_column("Status")
    table.add_column("Check")
    table.add_column("Message")
    for check in report.checks:
        status_style = {
            CheckStatus.PASS: "green",
            CheckStatus.WARN: "yellow",
            CheckStatus.FAIL: "red",
            CheckStatus.INFO: "cyan",
        }[check.status]
        table.add_row(f"[{status_style}]{check.status.value}[/{status_style}]", check.name, check.message)
    console.print(table)
    if report.suggestions:
        console.print("[bold]Suggestions[/bold]")
        for suggestion in report.suggestions:
            console.print(f"- {suggestion}")


def render_doctor_markdown(report: DoctorReport) -> str:
    """Render a doctor report as Markdown."""

    lines = [
        "# RepoReady Report",
        "",
        f"- Repository: `{report.root.name}`",
        f"- Detected profile: `{report.detected_profile.value}`",
        f"- Score: **{report.score}/100**",
        f"- Status: **{report.status}**",
        "",
        "## Checks",
        "",
        "| Status | Check | Message |",
        "| --- | --- | --- |",
    ]
    for check in report.checks:
        lines.append(f"| `{check.status.value}` | {check.name} | {check.message} |")
    if report.suggestions:
        lines.extend(["", "## Suggestions", ""])
        for suggestion in report.suggestions:
            lines.append(f"- {suggestion}")
    return "\n".join(lines) + "\n"


def render_doctor_json(report: DoctorReport) -> str:
    """Render a doctor report as JSON."""

    payload = {
        "repository": str(report.root),
        "profile": report.detected_profile.value,
        "score": report.score,
        "status": report.status,
        "checks": [
            {
                "name": check.name,
                "status": check.status.value,
                "message": check.message,
                "weight": check.weight,
                "suggestion": check.suggestion,
            }
            for check in report.checks
        ],
        "suggestions": report.suggestions,
    }
    return json.dumps(payload, indent=2) + "\n"


def render_clean_table(items: Sequence[CleanItem], console: Console) -> None:
    """Render cleanup candidates."""

    table = Table(title="RepoReady Cleanup")
    table.add_column("Path")
    table.add_column("Reason")
    table.add_column("Size")
    for item in items:
        table.add_row(item.relative_path, item.reason, format_bytes(item.size_bytes))
    console.print(table)


def render_profile_info(info: ProfileInfo) -> str:
    """Render profile details as text."""

    markers = ", ".join(info.markers) if info.markers else "none"
    groups = ", ".join(info.generated_groups) if info.generated_groups else "none"
    return f"{info.title}\n\n{info.description}\n\nMarkers: {markers}\nGenerated groups: {groups}"
