import os
import sys
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Optional

from ....adapters.inbound.parsers.sql_parser import RegexSqlParser
from ....adapters.inbound.detectors.sql_detector import SqlPatternDetector
from ....adapters.outbound.exporters.html_hud_exporter import HtmlHudExporter
from ....adapters.outbound.exporters.json_exporter import JsonExporter
from ....adapters.outbound.exporters.markdown_exporter import MarkdownExporter
from ....adapters.outbound.exporters.sarif_exporter import SarifExporter
from ....application.scan_service import ScanService
from ....domain.pattern import PATTERN_CATALOG

app = typer.Typer(
    name="dpx-sql",
    help="Architectural pattern detector and static analysis engine for SQL schemas, queries, and stored procedures.",
    add_completion=False,
)
console = Console()


@app.command()
def scan(
    path: str = typer.Argument(".", help="Target SQL file or directory to scan"),
    html: Optional[str] = typer.Option(None, "-H", "--html", help="Path to export interactive HTML HUD report"),
    json_out: Optional[str] = typer.Option(None, "-J", "--json", help="Path to export JSON findings report"),
    markdown: Optional[str] = typer.Option(None, "-M", "--markdown", help="Path to export Markdown report"),
    sarif: Optional[str] = typer.Option(None, "-S", "--sarif", help="Path to export SARIF v2.1.0 report"),
    min_confidence: float = typer.Option(0.50, "-c", "--min-confidence", help="Minimum confidence threshold (0.0 to 1.0)"),
):
    """
    Scan SQL files for architectural patterns, idiomatic constructs, procedural logic, and security hazards.
    """
    if not os.path.exists(path):
        console.print(f"[bold red]Error:[/bold red] Path '{path}' does not exist.")
        raise typer.Exit(code=1)

    parser = RegexSqlParser()
    detector = SqlPatternDetector()
    html_exporter = HtmlHudExporter()
    json_exporter = JsonExporter()
    markdown_exporter = MarkdownExporter()
    sarif_exporter = SarifExporter()

    service = ScanService(
        parser=parser,
        detector=detector,
        html_exporter=html_exporter,
        json_exporter=json_exporter,
        markdown_exporter=markdown_exporter,
        sarif_exporter=sarif_exporter,
    )

    with console.status("[bold cyan]Scanning SQL schemas, stored procedures, and queries...[/bold cyan]"):
        report = service.scan_path(
            target_path=path,
            html_output=html,
            json_output=json_out,
            markdown_output=markdown,
            sarif_output=sarif,
        )

    # Filter by confidence
    detections = [d for d in report.detections if d.confidence.value >= min_confidence]

    # Console Output
    console.print()
    console.print(
        Panel.fit(
            f"[bold cyan]🐘 DPX-SQL Analysis Complete[/bold cyan]\n"
            f"[bold white]Files Scanned:[/bold white] {report.scanned_files_count} | "
            f"[bold white]Execution Time:[/bold white] {report.execution_time_seconds:.4f}s | "
            f"[bold white]Total Patterns:[/bold white] {len(detections)}",
            border_style="cyan",
        )
    )

    if detections:
        table = Table(title="🔍 Detected SQL Architectural Patterns & Hazards", border_style="dim")
        table.add_column("#", justify="right", style="cyan", no_wrap=True)
        table.add_column("Category", style="magenta")
        table.add_column("Pattern Type", style="bold white")
        table.add_column("Target Symbol", style="green")
        table.add_column("Confidence", justify="center")
        table.add_column("Location", style="blue")

        for idx, d in enumerate(detections, start=1):
            conf_color = "green" if d.confidence.value >= 0.85 else "yellow" if d.confidence.value >= 0.70 else "white"
            conf_str = f"[{conf_color}]{d.confidence.percentage}% [{d.confidence.level.value}][/{conf_color}]"
            loc_str = f"{os.path.basename(d.location.file_path)}:{d.location.line_number}"
            table.add_row(str(idx), d.category.value, d.pattern_type.value, d.target_name, conf_str, loc_str)

        console.print(table)
    else:
        console.print("[yellow]No architectural patterns or hazards detected matching criteria.[/yellow]")

    console.print()
    if html:
        console.print(f"[bold green]✔[/bold green] Interactive HTML HUD exported to: [cyan]{html}[/cyan]")
    if json_out:
        console.print(f"[bold green]✔[/bold green] JSON findings exported to: [cyan]{json_out}[/cyan]")
    if markdown:
        console.print(f"[bold green]✔[/bold green] Markdown report exported to: [cyan]{markdown}[/cyan]")
    if sarif:
        console.print(f"[bold green]✔[/bold green] SARIF file exported to: [cyan]{sarif}[/cyan]")


@app.command()
def catalog():
    """
    List all supported SQL architectural patterns, GoF relational mappings, and security hazards.
    """
    table = Table(title="📚 DPX-SQL Supported Pattern Catalog (43 Patterns)", border_style="cyan")
    table.add_column("Pattern Type", style="bold green")
    table.add_column("Category", style="magenta")
    table.add_column("Default Weight", justify="center", style="yellow")
    table.add_column("Description", style="white")

    for p_type, meta in PATTERN_CATALOG.items():
        table.add_row(p_type.value, meta.category.value, f"{int(meta.default_weight*100)}%", meta.description)

    console.print(table)


@app.command()
def version():
    """
    Show DPX-SQL version.
    """
    console.print("[bold cyan]DPX-SQL[/bold cyan] v0.1.0 (Bivex Static Analysis Suite)")


if __name__ == "__main__":
    app()
