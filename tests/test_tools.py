import pytest
from unittest.mock import AsyncMock, Mock, patch

from skills.building_skill import building_tool
from skills.delivery_skill import delivery_dropoff
from skills.lost_found_skill import (
    LOST_FOUND_ITEMS,
    LostItem,
    check_lost_item,
    find_best_match,
    report_found_item,
    report_lost_item,
)
from skills.weather_skill import TempUnit, weather_tool


@pytest.fixture(autouse=True)
def clear_lost_found_items() -> None:
    # Reset shared state between tests
    LOST_FOUND_ITEMS.clear()


def test_building_tool_known_topics() -> None:
    assert building_tool("height")["answer"] == "The Shard is 1000 meters tall."
    assert building_tool("floors")["answer"] == "The Shard has 100 floors."
    assert (
        building_tool("restaurants")["answer"]
        == "There are several restaurants including Aqua Shard and Oblix."
    )


def test_building_tool_unknown_topic() -> None:
    assert building_tool("parking")["answer"] == "I don't have that information."


@pytest.mark.asyncio
async def test_weather_tool_location_not_found() -> None:
    async def fake_get(_url, params=None):
        resp = Mock()
        resp.json.return_value = {"results": []}
        return resp

    mock_client = AsyncMock()
    mock_client.get.side_effect = fake_get
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("skills.weather_skill.httpx.AsyncClient", return_value=mock_client):
        result = await weather_tool("NoSuchPlace")

    assert result == {"error": "Could not find location NoSuchPlace"}


@pytest.mark.asyncio
async def test_weather_tool_unit_conversion() -> None:
    async def fake_get(url, params=None):
        resp = Mock()
        if "geocoding-api" in url:
            resp.json.return_value = {
                "results": [{"latitude": 51.5, "longitude": -0.1}]
            }
        else:
            resp.json.return_value = {"current_weather": {"temperature": 20.0}}
        return resp

    mock_client = AsyncMock()
    mock_client.get.side_effect = fake_get
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("skills.weather_skill.httpx.AsyncClient", return_value=mock_client):
        celsius = await weather_tool("London", unit=TempUnit.celsius)
        fahrenheit = await weather_tool("London", unit=TempUnit.fahrenheit)

    assert celsius["temperature_c"] == 20.0
    assert fahrenheit["temperature_f"] == 68.0


@pytest.mark.asyncio
async def test_delivery_dropoff_message() -> None:
    result = await delivery_dropoff(Mock(), courier_company="FedEx")
    assert "FedEx" in result["message"]
    assert "designated bay area" in result["message"]


@pytest.mark.asyncio
async def test_lost_found_report_and_check() -> None:
    # Report a lost item for Alice
    resp = await report_lost_item(
        Mock(), lost_item="umbrella", name="Alice", phone_number="123"
    )
    assert "recorded" in resp["message"]
    assert len(LOST_FOUND_ITEMS) == 1

    # Reporting the same item again should not create a duplicate and should mention it was already reported
    resp2 = await report_lost_item(
        Mock(), lost_item="umbrella", name="Alice", phone_number="123"
    )
    assert "already reported" in resp2["message"]
    assert len(LOST_FOUND_ITEMS) == 1

    # The item is not yet found
    check_resp = await check_lost_item(Mock(), item="umbrella", name="Alice")
    assert check_resp["found"] is False

    # Mark the item as found
    found_resp = await report_found_item(Mock(), item="umbrella")
    assert "recorded" in found_resp["message"]

    # Check again now that it's found
    check_resp2 = await check_lost_item(Mock(), item="umbrella", name="Alice")
    assert check_resp2["found"] is True
    assert "has been found" in check_resp2["message"]


def test_find_best_match_prefers_name() -> None:
    # Ensure the matching logic takes the owner name into account
    LOST_FOUND_ITEMS.append(LostItem(item="blue wallet", owner_name="Bob", phone=""))
    match = find_best_match("blue wallet", "Bob")
    assert match is not None
    assert match.owner_name == "Bob"
