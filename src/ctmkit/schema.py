"""Validate a Control-M object dict against its JSON schema."""
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

# manifests folder name (plural) -> schema file stem (singular)
_SCHEMA_STEM = {
    "folders": "folder",
    "connection_profiles": "connection_profile",
    "calendars": "calendar",
    "quantitative_ressources": "quantitative_ressource",
    "secrets": "secret",
    "event_driven": "event",
    "services": "service",
}

# kinds we know how to schema-validate (others are skipped by the validator for now)
KNOWN_KINDS = frozenset(_SCHEMA_STEM)


def schema_path(kind: str, schemas_dir: Path) -> Path:
    return Path(schemas_dir) / f"{_SCHEMA_STEM[kind]}.schema.json"


def validate_object(obj: dict, kind: str, schemas_dir: Path) -> list[str]:
    schema = json.loads(schema_path(kind, schemas_dir).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    return [
        f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}"
        for e in sorted(validator.iter_errors(obj), key=lambda e: list(e.path))
    ]
