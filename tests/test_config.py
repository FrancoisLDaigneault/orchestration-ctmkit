from pathlib import Path

from ctmkit.config import load_site_standard

FIX = Path(__file__).parent / "fixtures" / "site-standard.yaml"


def test_load_site_standard():
    ss = load_site_standard(FIX)
    assert ss.distributed_letter == "D"
    assert ss.app_ids == ["0225", "4007"]
    assert ss.env_token("development") == "DEV"
    assert ss.env_token("production") == "PRD"
    assert ss.environments["staging"].server == "CTMSTG"
