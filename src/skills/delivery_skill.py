from typing import Any

from livekit.agents import RunContext, function_tool


@function_tool()
async def delivery_dropoff(
    context: RunContext,
    courier_company: str,
) -> dict[str, Any]:
    """
    Use this tool when a delivery driver arrives.
     Important rules:
     - The receptionist is a virtual assistant and cannot physically receive deliveries.
     - Do NOT say things like "follow me" or "this way".
     - Only provide concise factual information.

     Args:
        courier_company: name of the courier company, e.g. "FedEx", "UPS
    """

    return {
        "message": (
            f"Thank you for the {courier_company} delivery. "
            "Please place the package in the designated bay area "
            "near the loading dock on the ground floor."
        )
    }
