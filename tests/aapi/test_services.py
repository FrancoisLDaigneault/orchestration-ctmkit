import json

import httpx

from ctmkit.aapi import build as build_svc
from ctmkit.aapi import deploy as deploy_svc
from ctmkit.aapi import transform as transform_svc
from ctmkit.aapi.session import Session


def _session_returning(payload, status=200, capture=None):
    def handler(request: httpx.Request) -> httpx.Response:
        if capture is not None:
            capture["path"] = request.url.path
        return httpx.Response(status, json=payload)

    return Session("https://ctm/automation-api", "K"), httpx.MockTransport(handler)


def test_build_ok(tmp_path):
    f = tmp_path / "0225_X.json"
    f.write_text("{}")
    payload = {"deploymentStatuses": [{"name": "0225_X", "isSuccessful": True, "message": "ok"}]}
    sess, tr = _session_returning(payload)
    res = build_svc.build(sess, f, transport=tr)
    assert res.ok and res.errors == []


def test_build_collects_errors(tmp_path):
    f = tmp_path / "0225_X.json"
    f.write_text("{}")
    payload = {"deploymentStatuses": [{"name": "0225_X", "isSuccessful": False, "message": "bad name"}]}
    sess, tr = _session_returning(payload)
    res = build_svc.build(sess, f, transport=tr)
    assert not res.ok and any("bad name" in e for e in res.errors)


def test_deploy_hits_deploy_endpoint(tmp_path):
    f = tmp_path / "0225_X.json"
    f.write_text("{}")
    cap = {}
    payload = {"deploymentStatuses": [{"name": "0225_X", "isSuccessful": True, "message": "deployed"}]}
    sess, tr = _session_returning(payload, capture=cap)
    res = deploy_svc.deploy(sess, f, transport=tr)
    assert res.ok and res.deployed == ["0225_X"]
    assert cap["path"].endswith("/deploy")


def test_transform_posts_both_files(tmp_path):
    defs = tmp_path / "0225_X.json"
    defs.write_text('{"a": 1}')
    desc = tmp_path / "d.json"
    desc.write_text('{"DeployDescriptor": []}')
    cap = {}
    sess, tr = _session_returning({"a": 2}, capture=cap)
    out = transform_svc.transform(sess, defs, desc, transport=tr)
    assert cap["path"].endswith("/deploy/transform")
    assert json.loads(out) == {"a": 2}
