from dataclasses import dataclass
from typing import Any

from livekit.agents import RunContext, function_tool


@dataclass
class LostItem:
    item: str
    owner_name: str
    phone: str
    status: str = "lost"  # lost | found


# Global container to store all lost and found items
LOST_FOUND_ITEMS: list[LostItem] = []


@function_tool()
async def report_lost_item(
    context: RunContext,
    lost_item: str,
    name: str,
    phone_number: str,
) -> dict[str, Any]:
    """
    Use this tool when someone reports a lost item.

    Args:
        lost_item: description of the lost item
        name: visitor's name
        phone_number: contact phone number
    """
    item = LostItem(item=lost_item, owner_name=name, phone=phone_number, status="lost")
    LOST_FOUND_ITEMS.append(item)

    return {
        "message": (
            f"Thank you {name}. "
            f"We have recorded that you lost a {lost_item}. "
            f"If it is found we will contact you at {phone_number}."
        ),
        "item": lost_item,
        "contact": name,
    }


@function_tool()
async def check_lost_item(
    context: RunContext,
    item: str,
    name: str,
) -> dict[str, Any]:
    """
    Use this tool when a visitor asks if their lost item has been found.
    """
    # Search for the item with matching owner name and item description that has status "found"
    for lost_item in LOST_FOUND_ITEMS:
        if (
            lost_item.owner_name.lower() == name.lower()
            and lost_item.item.lower() == item.lower()
            and lost_item.status == "found"
        ):
            return {
                "found": True,
                "message": (
                    f"Good news {name}. "
                    f"Your {item} has been found. "
                    "Please come to the reception desk to collect it."
                ),
            }

    return {
        "found": False,
        "message": (
            f"Sorry {name}, your {item} has not been found yet. "
            "Please check again later. Also we will contact you if it is found."
        ),
    }


@function_tool()
async def report_found_item(
    context: RunContext,
    item: str,
) -> dict[str, Any]:
    """
    Use this tool when a lost item is found.
    Thanks the person who found it and records the item as found.
    Ask the finder to bring the item to the reception desk so that it can be returned to its owner.

    Args:
    item: description of the found item
    """
    # Find the matching lost item and mark it as found
    for lost_item in LOST_FOUND_ITEMS:
        if lost_item.item.lower() == item.lower() and lost_item.status == "lost":
            lost_item.status = "found"
            return {
                "message": f"The {item} has been recorded as found. We will contact {lost_item.owner_name} at {lost_item.phone}."
            }

    # If no matching lost item found, add it as a new found item (though this is unusual)
    found_item = LostItem(item=item, owner_name="", phone="", status="found")
    LOST_FOUND_ITEMS.append(found_item)

    return {"message": f"The {item} has been recorded as found."}
