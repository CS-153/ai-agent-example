import httpx
import logging
import json

USER_AGENT = "weather-app/1.0"
WEATHER_API_BASE = "https://api.open-meteo.com/v1/forecast?current=temperature_2m,precipitation,weather_code&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch&timezone=America%2FLos_Angeles"


logger = logging.getLogger("discord")


def _make_request(url: str):
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}

    try:
        response = httpx.Client().get(url, headers=headers, timeout=5.0)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def seven_day_forecast(latitude: str, longitude: str):
    """Get the seven day forecast for a given location with latitude and longitude."""
    logger.info(f"Getting seven day forecast for {latitude}, {longitude}")
    url = f"{WEATHER_API_BASE}&latitude={latitude}&longitude={longitude}"
    data = _make_request(url)

    if data is None:
        return "Error fetching weather data"

    res_json = {
        "current": data["current"],
        "daily": {},
    }

    for i, time in enumerate(data["daily"]["time"]):
        max_temp = data["daily"]["temperature_2m_max"][i]
        min_temp = data["daily"]["temperature_2m_min"][i]
        precipitation = data["daily"]["precipitation_probability_max"][i]
        res_json["daily"][time] = {
            "weather_code": data["daily"]["weather_code"][i],
            "temperature_max": f"{max_temp}°F",
            "temperature_min": f"{min_temp}°F",
            "precipitation": f"{precipitation}%",
        }

    return json.dumps(res_json)
