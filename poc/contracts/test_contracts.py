from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

ROOT = Path(__file__).parents[2]
SCHEMAS = ROOT / "schemas" / "v1"


def validate(schema_name: str, record: dict) -> None:
    schema = json.loads((SCHEMAS / schema_name).read_text())
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(record)


@pytest.mark.parametrize(
    ("schema_name", "record"),
    [
        ("geography.json", {"schema_version":"1.0","region_id":"geo1:test","home":{},"coverage_mode":"county","included_regions":[],"excluded_regions":[]}),
        ("source.json", {"schema_version":"1.0","source_id":"src-1","name":"City","source_type":"government","authority_tier":1,"ingestion_method":"api","url":"https://example.test","enabled":True}),
        ("event.json", {"schema_version":"1.0","event_id":"evt-1","title":"Event","start_time":"2026-08-15T12:00:00-04:00","geography":{},"category":"community","status":"scheduled","provenance":[{"source_id":"src-1"}]}),
        ("story.json", {"schema_version":"1.0","story_id":"story-1","headline":"Headline","published_at":"2026-08-13T08:00:00-04:00","geography":{},"category":"local","provenance":[{"source_id":"src-1"}]}),
        ("weather.json", {"schema_version":"1.0","weather_id":"wx-1","location":{},"retrieved_at":"2026-08-13T08:00:00-04:00","current":{},"hourly":[],"alerts":[],"provenance":[{"source_id":"nws"}]}),
        ("daily-scoop.json", {"schema_version":"1.0","scoop_id":"scoop-1","region_id":"geo1:test","local_date":"2026-08-13","scoop_version":1,"generated_at":"2026-08-13T00:05:00-04:00","model":"test-model","prompt_version":"p1","sections":[{"heading":"Around Town","body":"A supported statement.","record_ids":["evt-1"]}]})
    ],
)
def test_valid_contract_examples(schema_name: str, record: dict) -> None:
    validate(schema_name, record)


def test_event_without_provenance_is_rejected() -> None:
    with pytest.raises(ValidationError):
        validate("event.json", {"schema_version":"1.0","event_id":"evt-1","title":"Event","start_time":"2026-08-15T12:00:00-04:00","geography":{},"category":"community","status":"scheduled","provenance":[]})


def test_daily_scoop_section_without_record_ids_is_rejected() -> None:
    with pytest.raises(ValidationError):
        validate("daily-scoop.json", {"schema_version":"1.0","scoop_id":"scoop-1","region_id":"geo1:test","local_date":"2026-08-13","scoop_version":1,"generated_at":"2026-08-13T00:05:00-04:00","model":"test-model","prompt_version":"p1","sections":[{"heading":"Around Town","body":"Unsupported.","record_ids":[]}]})
