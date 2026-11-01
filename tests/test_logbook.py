"""Tests for the logbook descriptions."""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from homeassistant.core import HomeAssistant

from custom_components.brainstorm.const import (
    EVENT_IDEA_ADDED,
    EVENT_IDEA_COMPLETED,
    EVENT_IDEA_DELETED,
    EVENT_IDEA_UPDATED,
    OVERVIEW_ENTITY_ID,
)
from custom_components.brainstorm.logbook import async_describe_events


@pytest.mark.parametrize(
    ("event_type", "message"),
    [
        (EVENT_IDEA_ADDED, "Idee erfasst"),
        (EVENT_IDEA_COMPLETED, "Idee erledigt"),
        (EVENT_IDEA_UPDATED, "Idee geändert"),
        (EVENT_IDEA_DELETED, "Idee gelöscht"),
    ],
)
def test_describe_events(hass: HomeAssistant, event_type: str, message: str) -> None:
    """Test that every event gets a logbook description."""
    described: dict[str, Any] = {}
    async_describe_events(hass, lambda _, event, fn: described.update({event: fn}))

    result = described[event_type](
        SimpleNamespace(data={"text": "Notiz", "category": "Inbox", "priority": "high"})
    )

    assert result["message"].startswith(message)
    assert result["entity_id"] == OVERVIEW_ENTITY_ID
    assert "Notiz" in result["name"]


@pytest.mark.parametrize(
    ("data", "tag", "origin"),
    [
        ({"priority": "urgent", "device": "Echo"}, "Dringend", "via Echo"),
        ({"priority": "low", "source": "alexa"}, "Niedrig", "via alexa"),
    ],
)
def test_describe_priority_and_origin(
    hass: HomeAssistant, data: dict[str, str], tag: str, origin: str
) -> None:
    """Test how the priority and origin of an idea are described."""
    described: dict[str, Any] = {}
    async_describe_events(hass, lambda _, event, fn: described.update({event: fn}))

    result = described[EVENT_IDEA_ADDED](
        SimpleNamespace(data={"text": "Notiz", "category": "Inbox", **data})
    )

    assert tag in str(result)
    assert origin in str(result)
