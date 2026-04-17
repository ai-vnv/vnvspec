"""vnvspec CLI — V&V-grade specifications for engineered systems.

Usage:
    vnvspec init              Scaffold a vnvspec.yaml + specs/ directory
    vnvspec validate <spec>   Run GtWR + structural checks on a spec file
    vnvspec registries list   List available standards registries
    vnvspec registries show   Show entries from a registry
    vnvspec export            Export a report to HTML/MD/GSN/JSON/Annex IV

Exit codes:
    0 — OK (all pass)
    1 — Assessment failures (at least one fail verdict)
    2 — Inconclusive (at least one inconclusive, zero failures)
    3 — Spec validation error
    4 — Usage error (bad arguments / config)
    5 — Internal error (uncaught exception)
"""

from __future__ import annotations

import enum
import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from vnvspec._version import __version__


class ExitCode(enum.IntEnum):
    """Structured exit codes for the vnvspec CLI."""

    OK = 0
    ASSESSMENT_FAILURES = 1
    INCONCLUSIVE = 2
    SPEC_VALIDATION_ERROR = 3
    USAGE_ERROR = 4
    INTERNAL_ERROR = 5


app = typer.Typer(
    name="vnvspec",
    help="V&V-grade specifications for engineered systems.",
    no_args_is_help=True,
)
registries_app = typer.Typer(help="Browse standards registries.")
app.add_typer(registries_app, name="registries")

catalog_app = typer.Typer(help="Browse and audit best-practices catalogs.")
app.add_typer(catalog_app, name="catalog")

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
    fmt: Annotated[
        str, typer.Option("--format", "-f", help="Spec file format: yaml, toml, or py.")
    ] = "yaml",
) -> None:
    """Scaffold a vnvspec spec file + specs/ directory."""
    spec_dir = directory / "specs"
    spec_dir.mkdir(parents=True, exist_ok=True)

    templates: dict[str, tuple[str, str]] = {
        "yaml": (
            "vnvspec.yaml",
            "# vnvspec specification\nname: my-system\nversion: 0.1.0\nrequirements: []\n",
        ),
        "toml": (
            "vnvspec.toml",
            'name = "my-system"\nversion = "0.1.0"\nrequirements = []\n',
        ),
        "py": (
            "vnvspec_spec.py",
            (
                '"""vnvspec specification."""\n\n'
                "from vnvspec import Requirement, Spec\n\n"
                'spec = Spec(name="my-system", version="0.1.0", requirements=[])\n'
            ),
        ),
    }
    if fmt not in templates:
        console.print(
            f"[red]Unknown format:[/red] {fmt}. Available: {', '.join(sorted(templates))}"
        )
        raise typer.Exit(code=ExitCode.USAGE_ERROR)

    filename, content = templates[fmt]
    spec_path = directory / filename
    if not spec_path.exists():
        spec_path.write_text(content, encoding="utf-8")
        console.print(f"[green]Created[/green] {spec_path}")
    else:
        console.print(f"[yellow]Already exists[/yellow] {spec_path}")

    console.print(f"[green]Created[/green] {spec_dir}/")
    console.print(f"Run [bold]vnvspec validate {filename}[/bold] to check.")


@app.command()
def validate(
    spec_path: Annotated[Path, typer.Argument(help="Path to spec YAML/JSON.")],
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
    profile: Annotated[
        str,
        typer.Option("--profile", "-p", help="Rule profile: formal, web-app, embedded."),
    ] = "formal",
) -> None:
    """Run GtWR quality checks on a spec file."""
    from vnvspec.core._internal.gtwr_rules import RuleProfile  # noqa: PLC0415
    from vnvspec.core.requirement import Requirement  # noqa: PLC0415

    try:
        rule_profile = RuleProfile(profile)
    except ValueError as exc:
        console.print(
            f"[red]Unknown profile:[/red] {profile}. "
            f"Available: {', '.join(p.value for p in RuleProfile)}"
        )
        raise typer.Exit(code=ExitCode.USAGE_ERROR) from exc

    if not spec_path.exists():
        console.print(f"[red]Error:[/red] {spec_path} not found.")
        raise typer.Exit(code=ExitCode.USAGE_ERROR)

    try:
        data = json.loads(spec_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        console.print(f"[red]Spec validation error:[/red] {exc}")
        raise typer.Exit(code=ExitCode.SPEC_VALIDATION_ERROR) from exc

    try:
        requirements = [Requirement.model_validate(r) for r in data.get("requirements", [])]
    except Exception as exc:
        console.print(f"[red]Spec validation error:[/red] {exc}")
        raise typer.Exit(code=ExitCode.SPEC_VALIDATION_ERROR) from exc

    total_violations = 0
    for req in requirements:
        violations = req.check_quality(profile=rule_profile)
        total_violations += len(violations)
        if violations:
            console.print(f"\n[bold]{req.id}[/bold]: {req.statement}")
            for v in violations:
                color = {"error": "red", "warning": "yellow", "info": "dim"}.get(
                    v.severity, "yellow"
                )
                console.print(f"  [{color}]{v.rule} {v.name}[/{color}]: {v.message}")
        elif verbose:
            console.print(f"[green]✓[/green] {req.id}: no issues")

    console.print(f"\n{len(requirements)} requirements, {total_violations} violations.")
    if total_violations > 0:
        raise typer.Exit(code=ExitCode.ASSESSMENT_FAILURES)


@app.command()
def assess(
    self_flag: Annotated[
        bool,
        typer.Option("--self", help="Run self-assessment against .vnvspec/self-spec.yaml."),
    ] = False,
) -> None:
    """Run assessment. Use --self for vnvspec self-assessment."""
    import subprocess  # noqa: PLC0415
    import sys  # noqa: PLC0415

    if not self_flag:
        console.print("[yellow]Currently only --self mode is supported.[/yellow]")
        raise typer.Exit(code=ExitCode.USAGE_ERROR)

    script = Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "self_assess.py"
    if not script.exists():
        console.print(f"[red]Self-assessment script not found:[/red] {script}")
        raise typer.Exit(code=ExitCode.INTERNAL_ERROR)

    result = subprocess.run(
        [sys.executable, str(script)], cwd=str(script.parent.parent), check=False
    )
    raise typer.Exit(code=result.returncode)


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
        raise typer.Exit(code=ExitCode.USAGE_ERROR)

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
        raise typer.Exit(code=ExitCode.USAGE_ERROR)

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
        raise typer.Exit(code=ExitCode.USAGE_ERROR) from exc

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


# ---------------------------------------------------------------------------
# catalog subcommands
# ---------------------------------------------------------------------------


@catalog_app.command("list")
def catalog_list() -> None:
    """List all discovered catalog modules."""
    from vnvspec.catalog._base import discover_catalogs  # noqa: PLC0415

    catalogs = discover_catalogs()
    if not catalogs:
        console.print("[yellow]No catalog modules found.[/yellow]")
        return

    table = Table(title="Available Catalogs")
    table.add_column("Module", style="bold")
    table.add_column("Requirements", justify="right")
    table.add_column("Compatible With")
    table.add_column("Description")

    for cat in catalogs:
        table.add_row(
            cat.module_path,
            str(cat.requirement_count),
            cat.compatible_with or "—",
            cat.doc[:60] + "…" if len(cat.doc) > 60 else cat.doc,  # noqa: PLR2004
        )

    console.print(table)


@catalog_app.command("show")
def catalog_show(
    module: Annotated[str, typer.Argument(help="Catalog module path, e.g. vnvspec.catalog.demo")],
) -> None:
    """Show requirements from a catalog module."""
    from vnvspec.catalog._base import all_requirements  # noqa: PLC0415

    try:
        import importlib  # noqa: PLC0415

        mod = importlib.import_module(module)
    except ImportError as exc:
        console.print(f"[red]Error:[/red] cannot import {module}: {exc}")
        raise typer.Exit(code=ExitCode.USAGE_ERROR) from exc

    reqs = all_requirements(mod)
    if not reqs:
        console.print(f"[yellow]No requirements found in {module}.[/yellow]")
        return

    table = Table(title=f"{module} ({len(reqs)} requirements)")
    table.add_column("ID", style="bold")
    table.add_column("Priority")
    table.add_column("Method")
    table.add_column("Statement")

    for req in reqs:
        stmt = req.statement[:70] + "…" if len(req.statement) > 70 else req.statement  # noqa: PLR2004
        table.add_row(req.id, req.priority, req.verification_method, stmt)

    console.print(table)


@catalog_app.command("audit")
def catalog_audit() -> None:
    """Audit catalog modules for compatibility with installed packages."""
    from vnvspec.catalog._base import (  # noqa: PLC0415
        check_compatibility,
        discover_catalogs,
    )

    catalogs = discover_catalogs()
    if not catalogs:
        console.print("[yellow]No catalog modules found.[/yellow]")
        return

    table = Table(title="Catalog Audit")
    table.add_column("Module", style="bold")
    table.add_column("Version Pin")
    table.add_column("Installed")
    table.add_column("Status")

    has_incompatible = False
    for cat in catalogs:
        report = check_compatibility(cat)
        status_style = {
            "compatible": "green",
            "unknown": "yellow",
            "incompatible": "red",
        }[report.level]
        if report.level == "incompatible":
            has_incompatible = True
        table.add_row(
            cat.module_path,
            cat.compatible_with or "—",
            report.installed_version or "—",
            f"[{status_style}]{report.level}[/{status_style}]",
        )

    console.print(table)

    if has_incompatible:
        raise typer.Exit(code=ExitCode.ASSESSMENT_FAILURES)


@catalog_app.command("import")
def catalog_import(
    module: Annotated[str, typer.Argument(help="Catalog module path.")],
    fmt: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: yaml, toml, or json."),
    ] = "yaml",
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output file path."),
    ] = None,
) -> None:
    """Import catalog requirements into a spec file."""
    from vnvspec.catalog._base import all_requirements  # noqa: PLC0415
    from vnvspec.core.spec import Spec  # noqa: PLC0415

    try:
        import importlib  # noqa: PLC0415

        mod = importlib.import_module(module)
    except ImportError as exc:
        console.print(f"[red]Error:[/red] cannot import {module}: {exc}")
        raise typer.Exit(code=ExitCode.USAGE_ERROR) from exc

    reqs = all_requirements(mod)
    if not reqs:
        console.print(f"[yellow]No requirements found in {module}.[/yellow]")
        raise typer.Exit(code=ExitCode.USAGE_ERROR)

    spec = Spec(name=f"catalog-{module.split('.')[-1]}", requirements=reqs)

    serializers = {"yaml": spec.to_yaml, "toml": spec.to_toml, "json": spec.to_json}
    serializer = serializers.get(fmt)
    if serializer is None:
        console.print(
            f"[red]Unknown format:[/red] {fmt}. Available: {', '.join(sorted(serializers))}"
        )
        raise typer.Exit(code=ExitCode.USAGE_ERROR)

    content = serializer()
    if output:
        Path(output).write_text(content, encoding="utf-8")
        console.print(f"[green]Exported[/green] {len(reqs)} requirements to {output}")
    else:
        console.print(content)
