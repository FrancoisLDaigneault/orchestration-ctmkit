"""Render event-source objects into a Control-M Event Handler queue-config (YAML)."""
from __future__ import annotations

import yaml


def to_queue_entry(name: str, obj: dict) -> dict:
    """Convert one event-source object into an Event Handler queue entry.

    Args:
        name: Event-source name.
        obj: Event-source body.

    Returns:
        A dict matching the Event Handler queue-configuration schema.
    """
    entry = {
        "name": name,
        "type": obj.get("Broker"),
        "format": "yaml",
        "connection": obj.get("Connection", {}),
        "action": obj.get("Action"),
    }
    if obj.get("Target"):
        entry["target"] = obj["Target"]
    return entry


def render_handler_config(sources: list[tuple[str, dict]]) -> str:
    """Render the full Event Handler queue-configuration YAML for a set of sources.

    Args:
        sources: ``(name, body)`` pairs.

    Returns:
        The YAML document a Control-M Event Handler consumes.
    """
    queues = [to_queue_entry(name, body) for name, body in sources]
    return yaml.safe_dump({"queues": queues}, sort_keys=False)
