import pytest
from unittest.mock import patch, MagicMock


def make_mock_response(city="Los Angeles", region="California", temp_f=72.0, condition="Sunny"):
    mock = MagicMock()
    mock.json.return_value = {
        "location": {"name": city, "region": region},
        "current": {"temp_f": temp_f, "condition": {"text": condition}},
    }
    return mock


def test_fetch_weather_returns_one_result_per_zip():
    from weather import fetch_weather
    with patch("weather.requests.get", return_value=make_mock_response()):
        with patch("weather.time.sleep"):
            results = fetch_weather("test_key", ["90045", "10001"])
    assert len(results) == 2


def test_fetch_weather_maps_fields_correctly():
    from weather import fetch_weather
    with patch("weather.requests.get", return_value=make_mock_response(
        city="Seattle", region="Washington", temp_f=55.0, condition="Cloudy"
    )):
        with patch("weather.time.sleep"):
            results = fetch_weather("test_key", ["98101"])
    r = results[0]
    assert r["zip_code"] == "98101"
    assert r["city"] == "Seattle"
    assert r["region"] == "Washington"
    assert r["temp_f"] == 55.0
    assert r["condition"] == "Cloudy"


def test_fetch_weather_passes_api_key_in_request():
    from weather import fetch_weather, API_URL
    with patch("weather.requests.get", return_value=make_mock_response()) as mock_get:
        with patch("weather.time.sleep"):
            fetch_weather("secret_key", ["90045"])
    mock_get.assert_called_once_with(
        API_URL,
        params={"key": "secret_key", "q": "90045"},
    )


def test_main_raises_key_error_when_env_var_missing(monkeypatch):
    monkeypatch.delenv("WEATHER_API_KEY", raising=False)
    from weather import main
    with pytest.raises(KeyError, match="WEATHER_API_KEY"):
        main()
