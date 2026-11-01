"""Tests for the LLM tools."""
from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest
from homeassistant.core import Context, Event, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import llm
from voluptuous_openapi import convert

from custom_components.brainstorm.const import EVENT_IDEA_DELETED
from custom_components.brainstorm.llm import (
    BRAINSTORM_LLM_API_ID,
    async_register_llm_api,
)

from .conftest import SetupEntry


@pytest.fixture
async def call_tool(hass: HomeAssistant, setup_entry: SetupEntry) -> Any:
    """Set up the integration with test ideas and return a tool caller."""
    entry = await setup_entry()
    store = entry.runtime_data
    await store.async_add_idea("Rasen mähen vorne", category="Haus & Garten")
    await store.async_add_idea("Rasen mähen hinten", category="Haus & Garten")
    await store.async_add_idea("Milch kaufen", category="Alltag")
    context = Context()
    api = await llm.async_get_api(
        hass,
        BRAINSTORM_LLM_API_ID,
        llm.LLMContext(
            platform="test",
            context=context,
            language="de",
            assistant=None,
            device_id=None,
        ),
    )

    async def _call(tool_name: str, **args: Any) -> dict[str, Any]:
        result = await api.async_call_tool(
            llm.ToolInput(tool_name=tool_name, tool_args=args)
        )
        _call.last = result
        return result.data

    _call.store = store
    _call.context = context
    _call.api = api
    return _call


async def test_list_categories(call_tool: Any) -> None:
    """Test that the category overview works."""
    result = await call_tool("brainstorm_list_categories")
    assert result["total_active"] == 3
    assert result["category_counts"]["Alltag"] == 1


@pytest.mark.parametrize(
    ("category", "count"),
    [("all", 3), ("alle", 3), ("haus & garten", 2), ("Alltag", 1), ("Gibtsnicht", 0)],
)
async def test_get_ideas_category_filter(
    call_tool: Any, category: str, count: int
) -> None:
    """Test the category filter of the query tool."""
    result = await call_tool("brainstorm_get_ideas", category=category)
    assert result["count"] == count


@pytest.mark.parametrize(
    "tool", ["brainstorm_delete_idea", "brainstorm_complete_idea"]
)
async def test_ambiguous_query_changes_nothing(call_tool: Any, tool: str) -> None:
    """Test that several matches return candidates instead of acting."""
    result = await call_tool(tool, query="rasen")
    assert len(result["matches"]) == 2
    assert call_tool.last.error is True
    assert len(call_tool.store.ideas) == 3
    assert all(i["status"] == "active" for i in call_tool.store.ideas)


async def test_exact_match_wins(call_tool: Any) -> None:
    """Test that an exact text match is preferred."""
    result = await call_tool("brainstorm_complete_idea", query="rasen mähen vorne")
    assert result["success"] is True
    assert result["text"] == "Rasen mähen vorne"


@pytest.mark.parametrize("query", ["   ", "gibtsnicht"])
async def test_no_match_deletes_nothing(call_tool: Any, query: str) -> None:
    """Test that blank or unknown queries do not delete anything."""
    result = await call_tool("brainstorm_delete_idea", query=query)
    assert "error" in result
    assert len(call_tool.store.ideas) == 3


async def test_delete_passes_context(hass: HomeAssistant, call_tool: Any) -> None:
    """Test that the context of the LLM request reaches the event."""
    events: list[Event] = []

    @callback
    def _record(event: Event) -> None:
        events.append(event)

    hass.bus.async_listen(EVENT_IDEA_DELETED, _record)
    result = await call_tool("brainstorm_delete_idea", query="milch")
    await hass.async_block_till_done()

    assert result["success"] is True
    assert events[0].context is call_tool.context


async def test_tools_meet_core_requirements(
    call_tool: Any, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that core reports no deprecated tool usage and parameters convert."""
    tools = {tool.name: tool for tool in call_tool.api.tools}
    assert len(tools) == 5
    assert all(tool.integration == "brainstorm" for tool in tools.values())
    assert tools["brainstorm_delete_idea"].annotations.destructive is True
    assert tools["brainstorm_get_ideas"].annotations.read_only is True

    for tool in tools.values():
        convert(tool.parameters)
    await call_tool("brainstorm_list_categories")

    assert "without an integration" not in caplog.text
    assert "deprecated" not in caplog.text


async def test_add_idea_tool(call_tool: Any) -> None:
    """Test adding an idea, and that empty text is refused."""
    result = await call_tool(
        "brainstorm_add_idea", text="Regal bauen", category="Projekte", priority="low"
    )
    assert result["success"] is True
    stored = next(i for i in call_tool.store.ideas if "egal" in i["text"])
    assert stored["category"] == "Projekte"
    assert stored["priority"] == "low"

    assert "error" in await call_tool("brainstorm_add_idea", text="  ")


async def test_get_ideas_tool_searches_and_shows_all_statuses(call_tool: Any) -> None:
    """Test the text search and the status all."""
    result = await call_tool("brainstorm_get_ideas", search="milch")
    assert result["count"] == 1
    idea = next(i for i in call_tool.store.ideas if "ilch" in i["text"])
    await call_tool.store.async_update_idea(idea["id"], status="completed")
    assert (await call_tool("brainstorm_get_ideas", status="active"))["count"] == 2
    assert (await call_tool("brainstorm_get_ideas", status="all"))["count"] == 3


@pytest.mark.parametrize(
    ("tool", "args"),
    [
        ("brainstorm_add_idea", {"text": "Regal bauen"}),
        ("brainstorm_get_ideas", {}),
        ("brainstorm_complete_idea", {"id": "x"}),
        ("brainstorm_delete_idea", {"id": "x"}),
        ("brainstorm_list_categories", {}),
    ],
)
async def test_tools_report_that_the_entry_is_not_loaded(
    hass: HomeAssistant, call_tool: Any, tool: str, args: dict[str, Any]
) -> None:
    """Test each tool without a loaded entry."""
    entry = hass.config_entries.async_entries("brainstorm")[0]
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert "error" in await call_tool(tool, **args)


async def test_failed_registration_does_not_block_setup(hass: HomeAssistant) -> None:
    """Test that a failing LLM registration is not fatal."""
    with patch(
        "custom_components.brainstorm.llm.llm.async_register_api",
        side_effect=HomeAssistantError("schon da"),
    ):
        unregister = async_register_llm_api(hass)
    unregister()
