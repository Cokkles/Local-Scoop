from __future__ import annotations
from poc.sources.audit import build_audit
from poc.sources.models import Readiness
from poc.sources.registry import by_adapter_family, enabled_sources, load_registry, sources_for_county
from poc.sources.scoring import score_source

def test_registry_loads_and_ids_are_unique():
    raw, sources = load_registry()
    assert len(sources) >= 18
    assert len({s.source_id for s in sources}) == len(sources)
    assert raw["generated_for_region"].startswith("geo1:")

def test_all_eight_counties_have_sources():
    raw, sources = load_registry()
    for county in raw["counties"]:
        assert sources_for_county(sources, county["geoid"]), county

def test_all_counties_have_primary_sources():
    raw, sources = load_registry()
    for county in raw["counties"]:
        assert any(s.authority_tier <= 2 for s in sources_for_county(sources, county["geoid"]))

def test_enabled_sources_are_ready_or_keyed():
    _, sources = load_registry()
    assert enabled_sources(sources)
    assert all(s.readiness in {Readiness.READY, Readiness.REQUIRES_KEY} for s in enabled_sources(sources))

def test_eventbrite_not_enabled_for_broad_discovery():
    _, sources = load_registry()
    source = next(s for s in sources if s.source_id == "eventbrite_platform")
    assert source.readiness is Readiness.DEFERRED
    assert not source.enabled_for_phase_0_5

def test_civicengage_family_reuses_one_adapter_family():
    _, sources = load_registry()
    family = by_adapter_family(sources)["civicengage"]
    assert {s.source_id for s in family} >= {
        "durham_city_calendar","franklin_county_calendar","granville_county_calendar","nash_county_calendar"
    }
    assert all("ical" in s.ingestion_methods for s in family)

def test_franklin_and_granville_score_high():
    _, sources = load_registry()
    lookup = {s.source_id:s for s in sources}
    assert score_source(lookup["franklin_county_calendar"]).band == "high"
    assert score_source(lookup["granville_county_calendar"]).band == "high"

def test_nash_is_structured_but_low_coverage():
    _, sources = load_registry()
    nash = next(s for s in sources if s.source_id == "nash_county_calendar")
    assert nash.structure_score == 5
    assert nash.coverage_score == 1

def test_phase_0_5_enabled_set_has_multiple_adapter_families():
    _, sources = load_registry()
    assert len({s.adapter_family for s in enabled_sources(sources)}) >= 5

def test_audit_reports_every_county():
    audit = build_audit()
    assert len(audit["county_coverage"]) == 8
    assert all(row["primary_source_count"] >= 1 for row in audit["county_coverage"])

def test_ticketmaster_is_keyed_not_public_html():
    _, sources = load_registry()
    tm = next(s for s in sources if s.source_id == "ticketmaster_discovery")
    assert tm.readiness is Readiness.REQUIRES_KEY
    assert tm.ingestion_methods == ("api",)

def test_predicthq_is_not_enabled_without_subscription():
    _, sources = load_registry()
    phq = next(s for s in sources if s.source_id == "predicthq_events")
    assert phq.readiness is Readiness.LICENSED
    assert not phq.enabled_for_phase_0_5

def test_visit_raleigh_and_johnston_advertise_rss():
    _, sources = load_registry()
    lookup = {s.source_id:s for s in sources}
    assert "rss" in lookup["visit_raleigh_events"].ingestion_methods
    assert "rss" in lookup["johnston_visitors_events"].ingestion_methods

def test_university_sources_have_feed_capability():
    _, sources = load_registry()
    lookup = {s.source_id:s for s in sources}
    assert "feed" in lookup["ncsu_calendar"].ingestion_methods
    assert "feed" in lookup["duke_calendar"].ingestion_methods
