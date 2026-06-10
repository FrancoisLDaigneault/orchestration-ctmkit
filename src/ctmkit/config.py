"""Load the site-standard config that drives naming + environments."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Environment:
    token: str
    server: str


@dataclass(frozen=True)
class SiteStandard:
    distributed_letter: str
    app_ids: list[str]
    environments: dict[str, Environment]

    def env_token(self, env: str) -> str:
        return self.environments[env].token


def load_site_standard(path: Path) -> SiteStandard:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    envs = {
        name: Environment(token=cfg["token"], server=cfg["server"])
        for name, cfg in data["environments"].items()
    }
    return SiteStandard(
        distributed_letter=data["distributed_letter"],
        app_ids=[str(a) for a in data["app_ids"]],
        environments=envs,
    )


@dataclass(frozen=True)
class EnvEndpoint:
    """An Automation API endpoint for one environment.

    Attributes:
        endpoint: Base AAPI URL.
        timezone: IANA timezone of the Control-M environment.
    """

    endpoint: str
    timezone: str = "UTC"


def load_environments(path: Path) -> dict[str, EnvEndpoint]:
    """Load per-environment AAPI endpoints from ``environments.yaml``.

    Args:
        path: Path to ``environments.yaml``.

    Returns:
        Mapping of environment name to :class:`EnvEndpoint`.
    """
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return {
        name: EnvEndpoint(endpoint=cfg["endpoint"], timezone=cfg.get("timezone", "UTC"))
        for name, cfg in data.items()
    }


def load_deploy_order(path: Path) -> list[str]:
    """Load the ordered list of object-kind phases for deployment.

    Args:
        path: Path to ``deploy-order.yaml``.

    Returns:
        The phase names in deploy order.
    """
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return list(data["phases"])
