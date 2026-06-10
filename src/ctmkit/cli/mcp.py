"""`ctmkit mcp` surface: run the MCP server for AI agents."""
from __future__ import annotations

import typer

app = typer.Typer(no_args_is_help=True, help="MCP server (GitOps tools for AI agents).")


@app.command()
def serve(
    transport: str = typer.Option("stdio", "--transport", help="MCP transport (stdio)."),
) -> None:
    """Start the ctmkit MCP server so an AI agent can drive GitOps tools."""
    from ctmkit.mcp.server import build_server

    build_server().run(transport)
