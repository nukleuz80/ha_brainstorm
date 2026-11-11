"""Tests for hidden brainstorm rounds."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util import dt as dt_util
import pytest
from pytest_homeassistant_custom_component.common import (
    async_capture_events,
    async_fire_time_changed,
)

from .conftest import SetupEntry

OLAF = "user-olaf"
FRIDA = "user-frida"


async def _call(
    hass: HomeAssistant, service: str, user: str | None = OLAF, **data: Any
) -> Any:
    return await hass.services.async_call(
        "brainstorm",
        service,
        data,
        blocking=True,
        return_response=True,
        context=Context(user_id=user),
    )


async def _add(hass: HomeAssistant, text: str, user: str | None, **extra: Any) -> str:
    response = await _call(hass, "add_idea", user, text=text, category="Alltag", **extra)
    return response["idea"]["id"]


def _texts(store: Any, user: str | None) -> set[str]:
    return {i["text"] for i in store.get_overview_attributes(user)["ideas"]}


async def test_round_hides_new_notes_of_others(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Each person sees only their own new notes until the round ends."""
    entry = await setup_entry()
    store = entry.runtime_data
    events = async_capture_events(hass, "brainstorm_round_ended")
    await _add(hass, "Vorher da", OLAF)

    response = await _call(hass, "start_round", category="Alltag")
    assert response["round"]["by"] == OLAF
    assert "ends_at" not in response["round"]
    olaf = await _add(hass, "Idee von Olaf", OLAF)
    frida = await _add(hass, "Idee von Frida", FRIDA)
    await _add(hass, "Frida ihr Unterpunkt", FRIDA, parent_id=frida)
    await _call(hass, "add_idea", OLAF, text="Andere Liste", category="Projekte")
    # Voice notes without a person stay visible
    await _call(hass, "add_idea", None, text="Von Alexa", category="Alltag")

    assert _texts(store, OLAF) >= {"Vorher da", "Idee von Olaf", "Andere Liste", "Von Alexa"}
    assert "Idee von Frida" not in _texts(store, OLAF)
    assert "Frida ihr Unterpunkt" not in _texts(store, OLAF)
    assert "Idee von Olaf" not in _texts(store, FRIDA)
    assert "Idee von Frida" in _texts(store, FRIDA)
    assert store.get_overview_attributes(OLAF)["rounds"]["Alltag"]["hidden_count"] == 2
    assert store.get_overview_attributes(FRIDA)["rounds"]["Alltag"]["hidden_count"] == 1
    # The system and automations see everything, the shared sensor nothing hidden
    assert "Idee von Frida" in {i["text"] for i in store.visible_ideas(None)}
    shared = hass.states.get("sensor.brainstorm_ideen_ubersicht")
    assert shared is not None
    shared_texts = {i["text"] for i in shared.attributes["ideas"]}
    assert "Von Alexa" in shared_texts
    assert not shared_texts & {"Idee von Olaf", "Idee von Frida"}
    assert "Alltag" in shared.attributes["rounds"]
    # Nobody else may change a hidden note
    with pytest.raises(ServiceValidationError):
        await _call(hass, "update_idea", FRIDA, id=olaf, text="Geändert")

    # Starting again keeps the round as it is
    again = await _call(hass, "start_round", FRIDA, category="Alltag", minutes=5)
    assert again["round"] == response["round"]

    ended = await _call(hass, "end_round", FRIDA, category="Alltag")
    assert ended["revealed"] == 3
    await hass.async_block_till_done()
    assert events[0].data == {"category": "Alltag", "revealed": 3}
    assert "Idee von Frida" in _texts(store, OLAF)
    assert "Idee von Olaf" in _texts(store, FRIDA)
    assert store.get_overview_attributes(OLAF)["rounds"] == {}
    assert all("round_by" not in idea for idea in store.ideas)

    with pytest.raises(ServiceValidationError):
        await _call(hass, "end_round", category="Alltag")
    with pytest.raises(ServiceValidationError):
        await _call(hass, "start_round", category="Gibt es nicht")


async def test_round_ends_by_itself(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """A round with minutes ends when the time is up, also after a reload."""
    entry = await setup_entry()
    response = await _call(hass, "start_round", category="Alltag", minutes=5)
    ends_at = dt_util.parse_datetime(response["round"]["ends_at"])
    assert ends_at is not None
    await _add(hass, "Geheim", FRIDA)

    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    store = entry.runtime_data
    assert "Geheim" not in _texts(store, OLAF)

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(minutes=6))
    await hass.async_block_till_done()
    assert store.rounds == {}
    assert "Geheim" in _texts(store, OLAF)


async def test_round_marker_stays_out_of_exports(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """The author's user ID of a hidden note is not exported."""
    await setup_entry()
    await _call(hass, "start_round", category="Alltag")
    await _add(hass, "Geheim", OLAF)
    exported = await _call(hass, "export_json")
    assert all("round_by" not in idea for idea in exported["ideas"])
