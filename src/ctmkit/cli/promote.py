"""`ctmkit promote` surface: descriptor-based promotion across environments."""
from __future__ import annotations

from pathlib import Path

import typer

from ctmkit.aapi.deploy import deploy
from ctmkit.aapi.transform import transform
from ctmkit.cli._console import success
from ctmkit.cli._context import resolve_session
from ctmkit.promote.promoter import promote as run_promote

app = typer.Typer(no_args_is_help=True, help="Promote config across environments.")


@app.command()
def run(
    app_id: str = typer.Option(..., "--app"),
    from_env: str = typer.Option(..., "--from-env"),
    to_env: str = typer.Option(..., "--to-env"),
    path: Path = typer.Option(Path("."), "--path", help="Repo root."),
    endpoint: str = typer.Option(None, "--endpoint", help="Override the resolved endpoint."),
    api_key: str = typer.Option(..., "--api-key", envvar="CTM_API_KEY"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Promote ``--app`` folders from ``--from-env`` into ``--to-env`` via the descriptor."""
    base = Path(path) / "control-m" / app_id
    src = base / from_env / "folders"
    descriptor = base / to_env / "deploy_descriptor" / f"from-{from_env}.json"
    session = resolve_session(path, to_env, endpoint, api_key)

    def _transform(p: Path, desc: Path) -> str:
        return transform(session, p, desc)

    def _deploy_text(text: str, name: str) -> None:
        if not dry_run:
            tmp = Path("/tmp") / name
            tmp.write_text(text, encoding="utf-8")
            deploy(session, tmp)

    report = run_promote(src, descriptor=descriptor,
                         transform_fn=_transform, deploy_text_fn=_deploy_text)
    success(f"promoted {len(report.promoted)} file(s) {from_env} -> {to_env}"
            + (" (dry-run)" if dry_run else ""))
