"""Assemble the ctmkit MCP server from the tool functions."""
from __future__ import annotations

from ctmkit.mcp import tools

TOOLS = (tools.validate_manifests, tools.deploy_plan, tools.blackout_status,
         tools.approval_check)


def build_server():
    """Build a FastMCP server exposing the ctmkit GitOps tools.

    Returns:
        A ``mcp.server.fastmcp.FastMCP`` instance with the tools registered.

    Raises:
        ImportError: If the ``mcp`` package is not installed.
    """
    from mcp.server.fastmcp import FastMCP

    server = FastMCP("ctmkit")
    for fn in TOOLS:
        server.tool()(fn)
    return server
