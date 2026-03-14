from typing import Any

from livekit.agents import RunContext, function_tool


@function_tool()
async def lookup_weather(
    context: RunContext,
    location: str,
    unit: str = "celsius",
) -> dict[str, Any]:
    """
    Look up weather information for a given location.
    Args:
        location: The location to look up the weather for.
        unit: The unit for temperature, either "celsius" or "fahrenheit". Default is "celsius".
    """
    return weather_tool(location, unit)


def weather_tool(
    location: str,
    unit: str = "celsius",
) -> dict[str, Any]:

    if unit == "fahrenheit":
        return {"weather": "sunny", "temperature_f": 70}
    else:
        return {"weather": "sunny", "temperature_c": 20}
