"""Event-source model + validation (Kafka / SQS only)."""
from __future__ import annotations

BROKERS = ("kafka", "sqs")
ACTIONS = ("setevent", "runorder", "ondemand")

# minimal connection keys required per broker (matches the Event Handler config)
_REQUIRED_CONNECTION = {
    "kafka": ("bootstrap.servers", "group.id", "topic"),
    "sqs": ("region", "queue_url"),
}


def validate_event_source(name: str, obj: dict) -> list[str]:
    """Validate one event-source object; return a list of problems (empty = valid).

    Args:
        name: The object name (for messages).
        obj: The event-source body (``Broker``, ``Connection``, ``Action``, ``Target``).

    Returns:
        Human-readable error strings.
    """
    errors: list[str] = []
    broker = obj.get("Broker")
    if broker not in BROKERS:
        errors.append(f"{name}: Broker must be one of {list(BROKERS)} (got {broker!r})")
    action = obj.get("Action")
    if action not in ACTIONS:
        errors.append(f"{name}: Action must be one of {list(ACTIONS)} (got {action!r})")
    connection = obj.get("Connection", {})
    for key in _REQUIRED_CONNECTION.get(broker, ()):
        if key not in connection:
            errors.append(f"{name}: {broker} connection missing required key {key!r}")
    if action in ("runorder", "ondemand") and not obj.get("Target"):
        errors.append(f"{name}: action {action!r} requires a Target folder")
    return errors
