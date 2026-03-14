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


def find_best_match(
    target_item: str, target_name: str = "", min_similarity: float = 0.6
) -> LostItem | None:
    """
    Find the best matching lost item using fuzzy string matching.

    Args:
        target_item: The item description to match
        target_name: Optional owner name to match (for better accuracy)
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

        # Bonus for name match if provided
        name_similarity = 1.0
        if target_name:
            name_similarity = difflib.SequenceMatcher(
                None, target_name.lower(), item.owner_name.lower()
            ).ratio()

        # Combined score (weighted average)
        combined_score = (item_similarity * 0.7) + (name_similarity * 0.3)

        if combined_score > best_score and combined_score >= min_similarity:
            best_score = combined_score
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
    Use this tool when someone reports a lost item.

    Args:
        lost_item: description of the lost item
        name: visitor's name
        phone_number: contact phone number
    """
    # Check if this item is already reported as lost by this person
    existing_item = find_best_match(lost_item, name, min_similarity=0.8)
    if existing_item and existing_item.status == "lost":
        return {
            "message": (
                f"{name}, you have already reported losing a {lost_item}. "
                "We will continue to look for it."
            ),
            "item": lost_item,
            "contact": name,
        }

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
    # Find the best matching lost item for this person
    matching_item = find_best_match(item, name, min_similarity=0.6)

    if matching_item and matching_item.status == "found":
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
    # Find the best matching lost item
    matching_item = find_best_match(item, min_similarity=0.5)

    if matching_item and matching_item.status == "lost":
        matching_item.status = "found"

    # If no matching lost item found, add it as a new found item
    found_item = LostItem(item=item, owner_name="", phone="", status="found")
    LOST_FOUND_ITEMS.append(found_item)

    return {
        "message": f"The {item} has been recorded. Thank you for bringing it to our attention. Please bring it to the reception desk so we can return it to its owner."
    }
