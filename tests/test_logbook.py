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
    EVENT_IDEA_UNBLOCKED,
    EVENT_IDEA_UPDATED,
    OVERVIEW_ENTITY_ID,
)
from custom_components.brainstorm.logbook import async_describe_events

from .conftest import SetupEntry


@pytest.mark.parametrize(
    ("event_type", "message"),
    [
        (EVENT_IDEA_ADDED, "Idee erfasst"),
        (EVENT_IDEA_COMPLETED, "Idee erledigt"),
        (EVENT_IDEA_UPDATED, "Idee geändert"),
        (EVENT_IDEA_DELETED, "Idee gelöscht"),
        (EVENT_IDEA_UNBLOCKED, "Kann losgehen"),
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


def _describe(hass: HomeAssistant) -> dict[str, Any]:
    described: dict[str, Any] = {}
    async_describe_events(hass, lambda _, event, fn: described.update({event: fn}))
    return described


@pytest.mark.parametrize(
    ("event_type", "icon"),
    [
        (EVENT_IDEA_ADDED, "mdi:lightbulb-on"),
        (EVENT_IDEA_COMPLETED, "mdi:check-circle-outline"),
        (EVENT_IDEA_UPDATED, "mdi:pencil"),
        (EVENT_IDEA_DELETED, "mdi:delete-outline"),
        (EVENT_IDEA_UNBLOCKED, "mdi:lock-open-variant-outline"),
    ],
)
def test_every_event_has_its_icon(
    hass: HomeAssistant, event_type: str, icon: str
) -> None:
    """Each kind of event is recognisable by its icon."""
    result = _describe(hass)[event_type](
        SimpleNamespace(data={"text": "Notiz", "category": "Alltag"})
    )
    assert result["icon"] == icon
    assert result["name"] == "Brainstorm (Alltag): Notiz"


def test_urgent_ideas_get_the_alert_icon(hass: HomeAssistant) -> None:
    """An urgent idea stands out, and high priority is named."""
    added = _describe(hass)[EVENT_IDEA_ADDED]
    urgent = added(SimpleNamespace(data={"text": "Wasser!", "priority": "urgent"}))
    assert urgent["icon"] == "mdi:alert-circle"
    high = added(SimpleNamespace(data={"text": "Bald", "priority": "high"}))
    assert high["message"] == "Idee erfasst [🔴 Hoch] (Inbox)"
    assert high["icon"] == "mdi:lightbulb-on"


def test_a_long_text_is_shortened(hass: HomeAssistant) -> None:
    """The logbook shows at most 120 characters of a text."""
    long_text = "x" * 200
    for event_type in (EVENT_IDEA_ADDED, EVENT_IDEA_COMPLETED, EVENT_IDEA_DELETED):
        name = _describe(hass)[event_type](SimpleNamespace(data={"text": long_text}))[
            "name"
        ]
        shown = name.split(": ", 1)[1]
        assert len(shown) == 120
        assert shown.endswith("...")


def test_missing_data_has_defaults(hass: HomeAssistant) -> None:
    """An event without data still reads well: Inbox and an unknown note."""
    described = _describe(hass)
    added = described[EVENT_IDEA_ADDED](SimpleNamespace(data=None))
    assert added["name"] == "Brainstorm (Inbox): Unbekannte Notiz"
    assert added["message"] == "Idee erfasst (Inbox)"
    unblocked = described[EVENT_IDEA_UNBLOCKED](SimpleNamespace(data={"text": "B"}))
    assert unblocked["name"] == "Brainstorm: B"


def test_manual_source_is_not_named(hass: HomeAssistant) -> None:
    """Only another source or a device is named as the origin."""
    result = _describe(hass)[EVENT_IDEA_ADDED](
        SimpleNamespace(data={"text": "N", "category": "Alltag", "source": "manual"})
    )
    assert result["message"] == "Idee erfasst (Alltag)"


def test_unblocked_names_the_note_that_was_done(hass: HomeAssistant) -> None:
    """The message tells which note made the way free."""
    result = _describe(hass)[EVENT_IDEA_UNBLOCKED](
        SimpleNamespace(data={"text": "Streichen", "by_text": "Farbe kaufen"})
    )
    assert result["message"] == "Kann losgehen: „Farbe kaufen“ ist erledigt"


async def test_private_texts_stay_out_of_the_logbook(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_admin_user: Any
) -> None:
    """Every user can read the logbook, so with privacy on no text shows."""
    await setup_entry(
        options={"privacy_enabled": True, "privacy_owner": hass_admin_user.id}
    )
    described = _describe(hass)
    data = {"text": "Geschenk für Frida", "by_text": "Geheim", "category": "Alltag"}
    for event_type in (EVENT_IDEA_ADDED, EVENT_IDEA_UPDATED, EVENT_IDEA_UNBLOCKED):
        result = described[event_type](SimpleNamespace(data=data))
        assert "Frida" not in str(result)
        assert "Geheim" not in str(result)
        assert "Privater Eintrag" in result["name"]


def test_english_descriptions(hass: HomeAssistant) -> None:
    """An English Home Assistant gets English texts."""
    hass.config.language = "en"
    result = _describe(hass)[EVENT_IDEA_COMPLETED](SimpleNamespace(data={}))
    assert result["message"] == "Idea completed"
    assert result["name"] == "Brainstorm (Inbox): Unknown note"
