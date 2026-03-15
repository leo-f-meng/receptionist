from typing import Any
from enum import Enum
import httpx

from livekit.agents import RunContext, function_tool


class TempUnit(str, Enum):
    celsius = "celsius"
    fahrenheit = "fahrenheit"


@function_tool()
async def lookup_weather(
    context: RunContext,
    location: str,
    unit: TempUnit = TempUnit.celsius,
) -> dict[str, Any]:
    """
    Look up real weather information for a location.
    The default unit is Celsius, but Fahrenheit can be used by setting unit="fahrenheit".

    Args:
        location: City name (example: London)
        unit: Temperature unit ("celsius" or "fahrenheit")
    """

    return await weather_tool(location, unit)


async def weather_tool(
    location: str,
    unit: TempUnit = TempUnit.celsius,
) -> dict[str, Any]:

    async with httpx.AsyncClient() as client:

        # Convert city → coordinates
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"

        geo_resp = await client.get(
            geo_url,
            params={"name": location, "count": 1},
        )

        geo_data = geo_resp.json()

        if not geo_data.get("results"):
            return {"error": f"Could not find location {location}"}

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]

        # Get weather
        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_resp = await client.get(
            weather_url,
            params={
                "latitude": lat,
                "longitude": lon,
                "current_weather": True,
            },
        )

        weather_data = weather_resp.json()
        temp_c = weather_data["current_weather"]["temperature"]

        if unit == TempUnit.fahrenheit:
            temp = temp_c * 9 / 5 + 32
            return {
                "location": location,
                "weather": "current conditions",
                "temperature_f": round(temp, 1),
            }

        return {
            "location": location,
            "weather": "current conditions",
            "temperature_c": temp_c,
        }
