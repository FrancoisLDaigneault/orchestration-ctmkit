import httpx

from ctmkit.aapi.session import Session
from ctmkit.policy.health import server_healthy


def _session(status):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status)

    return Session("https://ctm/automation-api", "K"), httpx.MockTransport(handler)


def test_healthy_when_2xx():
    s, t = _session(200)
    assert server_healthy(s, transport=t) is True


def test_unhealthy_when_5xx():
    s, t = _session(503)
    assert server_healthy(s, transport=t) is False


def test_unhealthy_on_transport_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down")

    s = Session("https://ctm/automation-api", "K")
    assert server_healthy(s, transport=httpx.MockTransport(handler)) is False
