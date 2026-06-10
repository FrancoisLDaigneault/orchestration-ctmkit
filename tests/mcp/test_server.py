import pytest


def test_build_server_registers_tools():
    pytest.importorskip("mcp")
    from ctmkit.mcp.server import TOOLS, build_server

    server = build_server()
    assert server is not None
    assert len(TOOLS) == 4
