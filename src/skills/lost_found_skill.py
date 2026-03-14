import difflib
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


def find_best_match(target_item: str, min_similarity: float = 0.6) -> LostItem | None:
    """
    Find the best matching lost item using fuzzy string matching.

    Args:
        target_item: The item description to match
        min_similarity: Minimum similarity ratio (0.0 to 1.0)

    Returns:
        The best matching LostItem or None if no good match found
    """
    best_match = None
    best_score = 0.0

    for item in LOST_FOUND_ITEMS:
        # Calculate similarity for item description
        item_similarity = difflib.SequenceMatcher(
            None, target_item.lower(), item.item.lower()
        ).ratio()

        if item_similarity > best_score and item_similarity >= min_similarity:
            best_score = item_similarity
            best_match = item

    return best_match


@function_tool()
async def report_lost_item(
    context: RunContext,
    lost_item: str,
    name: str,
    phone_number: str,
) -> dict[str, Any]:
    """
    Visitor has reported a lost item but it's not found yet. Record the lost item and the visitor's contact information.

    Args:
        lost_item: description of the lost item
        name: visitor's name
        phone_number: contact phone number
    """

    item = LostItem(item=lost_item, owner_name=name, phone=phone_number, status="lost")
    LOST_FOUND_ITEMS.append(item)

    return {
        "message": (
            f"We have recorded that you lost a {lost_item}. "
            f"If it is found we will contact you."
        ),
        "item": lost_item,
        "contact": name,
        "phone": phone_number,
    }


@function_tool()
async def check_lost_item(
    context: RunContext,
    item: str,
) -> dict[str, Any]:
    """
    Check if a lost item has been found. If it's found, inform the visitor to come to the reception desk to collect it.
    Otherwise, ask the visitor to leave their contact information if they haven't already done it.
    So that we can contact them if it is found.

    Args:
        item: description of the lost item
    """
    # Find the best matching lost item for this person
    matching_item = find_best_match(item, min_similarity=0.6)

    if matching_item and matching_item.status == "found":
        return {"found": True}

    return {"found": False}


@function_tool()
async def report_found_item(
    context: RunContext,
    item: str,
) -> dict[str, Any]:
    """
    When some one finds a lost item, thanks the person who found it and records the item as found.
    Ask the finder to bring the item to the reception desk so that it can be returned to its owner.

    Args:
    item: the found item
    """
    # Find the best matching lost item
    matching_item = find_best_match(item, min_similarity=0.5)

    if matching_item and matching_item.status == "lost":
        matching_item.status = "found"

    # If no matching lost item found, add it as a new found item
    found_item = LostItem(item=item, owner_name="", phone="", status="found")
    LOST_FOUND_ITEMS.append(found_item)

    return {"message": f"The {item} has been recorded."}
