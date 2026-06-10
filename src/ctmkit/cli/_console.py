"""Shared Rich console and small render helpers for the CLI."""
from __future__ import annotations

from rich.console import Console
from rich.table import Table

console = Console()
err_console = Console(stderr=True)


def success(message: str) -> None:
    """Print a green success line.

    Args:
        message: Text to display.
    """
    console.print(f"[bold green]✓[/] {message}")


def failure(message: str) -> None:
    """Print a red failure line to stderr.

    Args:
        message: Text to display.
    """
    err_console.print(f"[bold red]✗[/] {message}")


def errors_table(title: str, rows: list[str]) -> None:
    """Render a list of error strings as a single-column table.

    Args:
        title: Table title.
        rows: Error strings to list.
    """
    table = Table(title=title, show_header=False, expand=True)
    for row in rows:
        table.add_row(f"[red]{row}[/]")
    console.print(table)
