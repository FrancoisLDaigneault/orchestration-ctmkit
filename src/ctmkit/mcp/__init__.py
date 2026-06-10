"""MCP door: exposes ctmkit's GitOps-aware Control-M tools to AI agents.

Complements BMC's runtime MCP server (``mcp-remote`` → ``/automation-api/mcp/stream``,
``x-api-key``) by adding validate / deploy-plan / blackout / approval tooling. Start with
``ctmkit mcp serve``.
"""
