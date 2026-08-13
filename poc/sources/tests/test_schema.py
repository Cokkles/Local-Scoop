from pathlib import Path
import json
from jsonschema import Draft202012Validator, FormatChecker
from poc.sources.registry import DEFAULT_REGISTRY

def test_source_registry_matches_schema():
    root = Path(__file__).parents[3]
    schema = json.loads((root / "schemas/v1/source-registry.json").read_text())
    record = json.loads(DEFAULT_REGISTRY.read_text())
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(record)
