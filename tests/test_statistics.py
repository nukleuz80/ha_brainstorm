"""Tests for the statistics view."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import Context, HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.brainstorm.statistics import build_statistics

from .conftest import SetupEntry

NOW = dt_util.as_local(datetime(2026, 11, 18, 12, 0, tzinfo=dt_util.UTC))


def _idea(
    idea_id: str,
    created: datetime,
    done: datetime | None = None,
    category: str = "Inbox",
    **extra: Any,
) -> dict[str, Any]:
    return {
        "id": idea_id,
        "text": idea_id,
        "category": category,
        "status": "completed" if done else "active",
        "created_at": created.isoformat(),
        "completed_at": done.isoformat() if done else None,
        **extra,
    }


def test_weeks_lead_time_and_people() -> None:
    """Done and new per week, the lead time and who ticked off."""
    day = timedelta(days=1)
    ideas = [
        _idea("a", NOW - 2 * day, NOW - day, completed_by="u1"),
        _idea("b", NOW - 10 * day, NOW - 8 * day, category="Haus", completed_by="u1"),
        _idea(
            "c",
            NOW - 3 * day,
            NOW - 3 * day + timedelta(hours=6),
            choreops={"user": "Lenja", "done_by": "Lenja"},
        ),
        _idea("d", NOW - 30 * day, NOW - 29 * day),
        _idea("e", NOW - day, due=(NOW - timedelta(hours=1)).isoformat()),
        _idea("f", NOW - 100 * day, NOW - 99 * day),
    ]
    stats = build_statistics(ideas, NOW, {"u1": "Jan"}, weeks=4)
    assert [w["week"] for w in stats["weeks"]] == [44, 45, 46, 47]
    assert [w["completed"] for w in stats["weeks"]] == [0, 0, 2, 1]
    assert [w["added"] for w in stats["weeks"]] == [0, 1, 1, 2]
    assert stats["completed"] == 3
    assert (stats["open"], stats["overdue"]) == (1, 1)
    assert stats["lead_time"] == {
        "count": 3,
        "median_hours": 24.0,
        "average_hours": 26.0,
    }
    assert stats["people"] == [
        {"name": "Jan", "completed": 2},
        {"name": "Lenja", "completed": 1},
    ]
    assert stats["unknown"] == 0
    assert stats["categories"] == [
        {"category": "Inbox", "completed": 2, "open": 1},
        {"category": "Haus", "completed": 1, "open": 0},
    ]
    only = build_statistics(ideas, NOW, {}, weeks=4, category="Haus")
    assert only["completed"] == 1
    assert only["people"] == [] and only["unknown"] == 1
    empty = build_statistics([], NOW, {}, weeks=1)
    assert empty["lead_time"]["median_hours"] is None
    assert len(empty["weeks"]) == 1


async def test_who_ticked_off_and_websocket(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_ws_client: WebSocketGenerator,
    hass_admin_user: Any,
) -> None:
    """The user who ticks off is stored and counted; opening again forgets it."""
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox", "Haus"]})
    store = entry.runtime_data
    idea = await store.async_add_idea("Lampe", category="Haus", source="dashboard")
    other = await store.async_add_idea("Regal", source="dashboard")
    await store.async_update_idea(
        idea["id"], status="completed", context=Context(user_id=hass_admin_user.id)
    )
    await store.async_update_idea(other["id"], status="completed")
    assert store.get_idea(idea["id"])["completed_by"] == hass_admin_user.id
    assert "completed_by" not in store.get_idea(other["id"])

    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "brainstorm/statistics", "weeks": 2})
    result = (await client.receive_json())["result"]
    assert result["completed"] == 2
    assert result["people"] == [{"name": hass_admin_user.name, "completed": 1}]
    assert result["unknown"] == 1
    await client.send_json_auto_id(
        {"type": "brainstorm/statistics", "category": "Haus"}
    )
    result = (await client.receive_json())["result"]
    assert result["completed"] == 1 and len(result["weeks"]) == 8

    await store.async_update_idea(idea["id"], status="active")
    assert "completed_by" not in store.get_idea(idea["id"])
    assert "completed_by" not in store.export_json()["ideas"][0]


async def test_intercepted_commands_in_statistics(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_ws_client: WebSocketGenerator,
) -> None:
    """Caught device commands are listed, kept as a note or forgotten."""
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox", "Haus"]})
    store = entry.runtime_data
    await store.async_record_intercepted("Küche Schrank an", "Echo Küche")
    await store.async_record_intercepted("Flur aus", None)

    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "brainstorm/statistics", "weeks": 2})
    caught = (await client.receive_json())["result"]["intercepted"]
    assert [item["text"] for item in caught] == ["Flur aus", "Küche Schrank an"]
    assert caught[1]["echo"] == "Echo Küche"

    await client.send_json_auto_id(
        {"type": "brainstorm/intercepted", "entry_id": caught[1]["id"], "keep": True}
    )
    assert (await client.receive_json())["success"]
    assert [idea["text"] for idea in store.ideas] == ["Küche Schrank an"]
    assert store.ideas[0]["device"] == "Echo Küche"

    await client.send_json_auto_id(
        {"type": "brainstorm/intercepted", "entry_id": caught[0]["id"], "keep": False}
    )
    assert (await client.receive_json())["success"]
    assert store.intercepted_commands() == []
    assert len(store.ideas) == 1

    await client.send_json_auto_id(
        {"type": "brainstorm/intercepted", "entry_id": "missing", "keep": False}
    )
    assert not (await client.receive_json())["success"]

    # Persisted with the rest and capped
    for index in range(60):
        await store.async_record_intercepted(f"Licht {index} an")
    assert len(store.intercepted_commands()) == 50
    assert store.export_json() is not None


async def test_intercepted_commands_only_for_admins(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    """Sentences from the Echos belong to nobody, so other users do not see them."""
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox"]})
    await entry.runtime_data.async_record_intercepted("Flur aus")
    client = await hass_ws_client(hass, hass_read_only_access_token)
    await client.send_json_auto_id({"type": "brainstorm/statistics"})
    assert "intercepted" not in (await client.receive_json())["result"]
    await client.send_json_auto_id(
        {"type": "brainstorm/intercepted", "entry_id": "x", "keep": False}
    )
    assert not (await client.receive_json())["success"]
