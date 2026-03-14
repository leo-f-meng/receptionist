from typing import Any

from livekit.agents import RunContext, function_tool


@function_tool()
async def get_building_info(context: RunContext, topic: str) -> dict[str, Any]:
    """
    Use this tool when visitors ask factual questions about The Shard building.
    Args:
        topic: one of ["height", "floors", "restaurants"]
    """
    return building_tool(topic)


def building_tool(topic: str) -> dict[str, Any]:
    knowledge = {
        "height": "The Shard is 1000 meters tall.",
        "floors": "The Shard has 100 floors.",
        "restaurants": "There are several restaurants including Aqua Shard and Oblix.",
    }

    return {"answer": knowledge.get(topic.lower(), "I don't have that information.")}
