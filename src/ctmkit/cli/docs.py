"""`ctmkit docs` surface: mirror/crawl the vendor documentation."""
from __future__ import annotations

from pathlib import Path

import typer

from ctmkit.docs import crawl as crawl_mod
from ctmkit.docs import mirror as mirror_mod

app = typer.Typer(no_args_is_help=True, help="Mirror/crawl vendor docs.")


@app.command()
def crawl(
    sources: Path = typer.Option(crawl_mod.DEFAULT_SOURCES, "--sources"),
    out: Path = typer.Option(Path("docs/reference"), "--out"),
) -> None:
    """Full-site crawl of the configured doc spaces + GitHub repos + articles."""
    crawl_mod.main(["--sources", str(sources), "--out", str(out)])


@app.command()
def mirror(
    sources: Path = typer.Option(mirror_mod.DEFAULT_SOURCES, "--sources"),
    out: Path = typer.Option(Path("docs/reference/bmc"), "--out"),
) -> None:
    """Mirror the curated page set only."""
    mirror_mod.main(["--sources", str(sources), "--out", str(out)])
