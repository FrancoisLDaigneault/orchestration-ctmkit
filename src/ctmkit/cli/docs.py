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


@app.command()
def refresh(
    out: Path = typer.Option(Path("docs/reference"), "--out"),
) -> None:
    """Re-fetch only pages the server reports as modified (conditional, incremental).

    Sends ``If-Modified-Since`` per page; 304 → skipped, 200 → rewritten. Run a full
    ``crawl`` occasionally to discover brand-new pages.
    """
    from curl_cffi import requests as cr

    from ctmkit.docs.clean import clean_markdown
    from ctmkit.docs.index import diff_and_update, write_changelog
    from ctmkit.docs.mirror import html_to_markdown
    from ctmkit.docs.refresh import refresh as do_refresh

    session = cr.Session(impersonate="chrome124")
    result = do_refresh(out, session,
                        clean_fn=lambda html: clean_markdown(html_to_markdown(html)))
    changes = diff_and_update(out)
    write_changelog(out, changes)
    typer.echo(f"refreshed: {result.updated} updated, {result.unchanged} unchanged (304), "
               f"{result.errors} error(s); changelog +{len(changes.added)} "
               f"~{len(changes.changed)} -{len(changes.removed)}")
