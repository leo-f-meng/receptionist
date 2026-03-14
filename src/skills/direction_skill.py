from typing import Any

from livekit.agents import RunContext, function_tool


@function_tool()
async def get_directions(
    context: RunContext,
    destination: str,
) -> dict[str, Any]:
    """
    Use this tool when visitors ask where something is located.

    Important rules:
    - The receptionist is a virtual assistant and cannot physically guide visitors.
    - Do NOT say things like "follow me" or "this way".
    - Only provide concise factual information.

    If a visitor asks for taking them there, give verbal directions instead.

    Examples:
        - bathroom
        - elevators
        - observation deck
    Args:
    destination: one of ["bathroom", "elevators", "observation deck"]
    """

    directions = {
        "bathroom": "The restroom is located behind the reception desk. Also there are restrooms on floors 1, 34, and 68.",
        "elevators": "The elevators are located on your left side near the lobby.",
        "observation deck": "Please take the elevator to floor 68 for the observation deck.",
    }

    return {
        "message": directions.get(
            destination.lower(), "Please ask the reception desk for assistance."
        )
    }
