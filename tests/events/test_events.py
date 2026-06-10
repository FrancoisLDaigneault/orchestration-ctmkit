import yaml

from ctmkit.events.models import validate_event_source
from ctmkit.events.render import render_handler_config, to_queue_entry

KAFKA = {
    "Broker": "kafka",
    "Connection": {"bootstrap.servers": "k:9093", "group.id": "g", "topic": "t"},
    "Action": "runorder",
    "Target": "DEV#D0225_BILLING",
}
SQS = {
    "Broker": "sqs",
    "Connection": {"region": "ca-central-1", "queue_url": "https://sqs/q"},
    "Action": "runorder",
    "Target": "DEV#D4007_PIPELINE",
}


def test_valid_kafka_and_sqs():
    assert validate_event_source("0225_K", KAFKA) == []
    assert validate_event_source("4007_Q", SQS) == []


def test_rejects_other_broker():
    bad = {**KAFKA, "Broker": "rabbitmq"}
    errs = validate_event_source("x", bad)
    assert any("Broker" in e for e in errs)


def test_rejects_bad_action_and_missing_connection():
    assert any("Action" in e for e in validate_event_source("x", {**KAFKA, "Action": "nope"}))
    assert any("bootstrap.servers" in e
               for e in validate_event_source("x", {**KAFKA, "Connection": {"group.id": "g", "topic": "t"}}))


def test_runorder_requires_target():
    assert any("Target" in e for e in validate_event_source("x", {**SQS, "Target": None}))


def test_render_handler_config():
    out = yaml.safe_load(render_handler_config([("0225_K", KAFKA), ("4007_Q", SQS)]))
    assert [q["type"] for q in out["queues"]] == ["kafka", "sqs"]
    assert out["queues"][0]["connection"]["topic"] == "t"
    assert to_queue_entry("0225_K", KAFKA)["action"] == "runorder"
