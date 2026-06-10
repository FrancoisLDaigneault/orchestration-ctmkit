import httpx

from ctmkit.aapi.session import Session


def test_client_sets_api_key_header_and_base_url():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["key"] = request.headers.get("x-api-key")
        return httpx.Response(200, json={"ok": True})

    sess = Session(endpoint="https://ctm:8443/automation-api", api_key="K123")
    with sess.client(transport=httpx.MockTransport(handler)) as client:
        client.get("/build")
    assert captured["url"] == "https://ctm:8443/automation-api/build"
    assert captured["key"] == "K123"
