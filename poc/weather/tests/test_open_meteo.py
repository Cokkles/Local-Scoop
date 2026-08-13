from urllib.parse import parse_qs, urlparse
import pytest

from poc.weather.open_meteo import OpenMeteoClient, OpenMeteoProviderError
from .conftest import POINT, T0, Router, load


def test_open_meteo_request_is_explicit_about_units_timezone_and_horizon():
    url = OpenMeteoClient(transport=lambda *_: load("open_meteo.json")).build_url(POINT, "America/New_York", 7)
    query = parse_qs(urlparse(url).query)
    assert query["temperature_unit"] == ["fahrenheit"]
    assert query["wind_speed_unit"] == ["mph"]
    assert query["precipitation_unit"] == ["inch"]
    assert query["timezone"] == ["America/New_York"]
    assert "uv_index" in query["hourly"][0]


def test_open_meteo_normalizes_detail_fields():
    bundle = OpenMeteoClient(transport=Router().open_meteo).fetch(POINT, "America/New_York", T0)
    assert bundle.current.apparent_temperature_f == 96
    assert bundle.hourly[0].dew_point_f == 72
    assert bundle.hourly[0].visibility_miles == pytest.approx(10.0)
    assert bundle.hourly[0].uv_index == 6.5


def test_open_meteo_horizon_is_bounded():
    with pytest.raises(ValueError): OpenMeteoClient(transport=lambda *_:{}).build_url(POINT, "America/New_York", 17)


def test_open_meteo_missing_hourly_times_is_rejected():
    with pytest.raises(OpenMeteoProviderError):
        OpenMeteoClient(transport=lambda *_:{"current":{},"hourly":{}}).fetch(POINT,"America/New_York",T0)
