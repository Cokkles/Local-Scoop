import pytest

from poc.weather.nws import NWSClient, NWSProviderError
from .conftest import POINT, T0, Router


def test_nws_requires_user_agent():
    with pytest.raises(ValueError): NWSClient(user_agent="")


def test_nws_point_discovery_sends_required_user_agent():
    router = Router(); client = NWSClient(user_agent="Local-Scoop-Test/1.0", transport=router.nws)
    metadata = client.resolve_point(POINT)
    assert metadata.hourly_url.endswith("/forecast/hourly")
    assert metadata.stations_url.endswith("/stations")
    assert router.calls[0][1]["User-Agent"] == "Local-Scoop-Test/1.0"


def test_nws_normalizes_station_observation_units():
    current = NWSClient(transport=Router().nws).fetch_forecast(POINT, T0).current
    assert current.station_id == "KRDU"
    assert current.temperature_f == pytest.approx(86.0)
    assert current.dew_point_f == pytest.approx(69.8)
    assert current.wind_speed_mph == pytest.approx(11.1847, rel=1e-3)
    assert current.pressure_hpa == pytest.approx(1013.25)
    assert current.visibility_miles == pytest.approx(10.0)


def test_nws_hourly_preserves_authoritative_forecast_fields():
    period = NWSClient(transport=Router().nws).fetch_forecast(POINT, T0).hourly[0]
    assert period.temperature_f == 87
    assert period.precipitation_probability_pct == 25
    assert period.wind_speed_mph == 8
    assert period.short_forecast == "Partly Sunny"


def test_nws_extended_forecast_preserves_day_night_periods():
    extended = NWSClient(transport=Router().nws).fetch_forecast(POINT, T0).extended
    assert len(extended) == 3
    assert extended[0].name == "This Afternoon"
    assert extended[0].temperature_f == 89
    assert extended[1].is_daytime is False
    assert extended[2].short_forecast == "Mostly Sunny"


def test_nws_alert_mapping():
    alerts, provenance = NWSClient(transport=Router().nws).fetch_alerts(POINT, T0)
    assert len(alerts) == 1 and alerts[0].event == "Heat Advisory"
    assert alerts[0].severity == "Moderate" and alerts[0].expires_at is not None
    assert provenance.source_id == "nws-alerts"


def test_nws_point_missing_link_is_rejected():
    with pytest.raises(NWSProviderError):
        NWSClient(transport=lambda *_: {"properties":{"forecastHourly":"x"}}).resolve_point(POINT)
