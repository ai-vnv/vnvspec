"""vnvspec CLI — V&V-grade specifications for engineered systems.

Usage:
    vnvspec init              Scaffold a vnvspec.yaml + specs/ directory
    vnvspec validate <spec>   Run GtWR + structural checks on a spec file
    vnvspec registries list   List available standards registries
    vnvspec registries show   Show entries from a registry
    vnvspec export            Export a report to HTML/MD/GSN/JSON/Annex IV
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from vnvspec._version import __version__

app = typer.Typer(
    name="vnvspec",
    help="V&V-grade specifications for engineered systems.",
    no_args_is_help=True,
)
registries_app = typer.Typer(help="Browse standards registries.")
app.add_typer(registries_app, name="registries")

console = Console()


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"vnvspec {__version__}")
        raise typer.Exit


@app.callback()
def main(
    _version: Annotated[
        bool | None,
        typer.Option("--version", "-V", callback=_version_callback, is_eager=True),
    ] = None,
) -> None:
    """vnvspec — V&V-grade specifications for engineered systems."""


@app.command()
def init(
    directory: Annotated[Path, typer.Argument(help="Target directory.")] = Path("."),
) -> None:
    """Scaffold a vnvspec.yaml + specs/ directory."""
    spec_dir = directory / "specs"
    spec_dir.mkdir(parents=True, exist_ok=True)

    yaml_path = directory / "vnvspec.yaml"
    if not yaml_path.exists():
        yaml_path.write_text(
            "# vnvspec specification\nname: my-system\nversion: 0.1.0\nrequirements: []\n",
            encoding="utf-8",
        )
        console.print(f"[green]Created[/green] {yaml_path}")
    else:
        console.print(f"[yellow]Already exists[/yellow] {yaml_path}")

    console.print(f"[green]Created[/green] {spec_dir}/")
    console.print("Run [bold]vnvspec validate vnvspec.yaml[/bold] to check.")


@app.command()
def validate(
    spec_path: Annotated[Path, typer.Argument(help="Path to spec YAML/JSON.")],
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
) -> None:
    """Run GtWR quality checks on a spec file."""
    from vnvspec.core.requirement import Requirement  # noqa: PLC0415

    if not spec_path.exists():
        console.print(f"[red]Error:[/red] {spec_path} not found.")
        raise typer.Exit(code=1)

    data = json.loads(spec_path.read_text(encoding="utf-8"))
    requirements = [Requirement.model_validate(r) for r in data.get("requirements", [])]

    total_violations = 0
    for req in requirements:
        violations = req.check_quality()
        total_violations += len(violations)
        if violations:
            console.print(f"\n[bold]{req.id}[/bold]: {req.statement}")
            for v in violations:
                color = "red" if v.severity == "error" else "yellow"
                console.print(f"  [{color}]{v.rule} {v.name}[/{color}]: {v.message}")
        elif verbose:
            console.print(f"[green]✓[/green] {req.id}: no issues")

    console.print(f"\n{len(requirements)} requirements, {total_violations} violations.")
    if total_violations > 0:
        raise typer.Exit(code=1)


@app.command()
def export(
    report_path: Annotated[Path, typer.Argument(help="Path to report JSON.")],
    fmt: Annotated[str, typer.Option("--format", "-f", help="Output format.")] = "html",
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output file path."),
    ] = None,
) -> None:
    """Export a report to HTML, Markdown, GSN Mermaid, JSON, or Annex IV."""
    from vnvspec.core.assessment import Report  # noqa: PLC0415
    from vnvspec.exporters import (  # noqa: PLC0415
        export_annex_iv,
        export_gsn_mermaid,
        export_html,
        export_json,
        export_markdown,
    )

    if not report_path.exists():
        console.print(f"[red]Error:[/red] {report_path} not found.")
        raise typer.Exit(code=1)

    data = json.loads(report_path.read_text(encoding="utf-8"))
    report = Report.model_validate(data)

    formatters: dict[str, object] = {
        "html": export_html,
        "md": export_markdown,
        "markdown": export_markdown,
        "gsn": export_gsn_mermaid,
        "mermaid": export_gsn_mermaid,
        "json": export_json,
        "annex-iv": export_annex_iv,
    }

    fn = formatters.get(fmt)
    if fn is None:
        console.print(
            f"[red]Unknown format:[/red] {fmt}. Available: {', '.join(sorted(formatters))}"
        )
        raise typer.Exit(code=1)

    if fmt in ("gsn", "mermaid", "annex-iv"):
        result: str = fn(report)  # type: ignore[operator]
    elif output is not None:
        result = fn(report, path=output)  # type: ignore[operator]
    else:
        result = fn(report)  # type: ignore[operator]

    if output is not None and fmt not in ("gsn", "mermaid", "annex-iv"):
        console.print(f"[green]Exported[/green] {output}")
    else:
        console.print(result)


@registries_app.command("list")
def registries_list() -> None:
    """List available standards registries."""
    from vnvspec.registries import list_available  # noqa: PLC0415

    table = Table(title="Available Registries")
    table.add_column("Name", style="bold")

    for name in list_available():
        table.add_row(name)

    console.print(table)


@registries_app.command("show")
def registries_show(
    name: Annotated[str, typer.Argument(help="Registry name.")],
    limit: Annotated[int, typer.Option("--limit", "-n")] = 20,
) -> None:
    """Show entries from a standards registry."""
    from vnvspec.registries import load  # noqa: PLC0415

    try:
        registry = load(name)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    table = Table(title=f"{registry.name} ({len(registry.entries)} entries)")
    table.add_column("Clause", style="bold")
    table.add_column("Title")
    table.add_column("Level", style="dim")

    for entry in registry.entries[:limit]:
        table.add_row(entry.clause, entry.title, entry.normative_level)

    console.print(table)
    if len(registry.entries) > limit:
        console.print(
            f"[dim]Showing {limit} of {len(registry.entries)}. Use --limit to see more.[/dim]"
        )
