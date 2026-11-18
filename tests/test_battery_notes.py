"""Tests for working together with Battery Notes."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import device_registry as dr, entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.brainstorm.battery_notes import battery_type, needed_batteries
from custom_components.brainstorm.const import DOMAIN
from custom_components.brainstorm.store import BrainstormStore

from .conftest import SetupEntry
from .test_bring import HOME, FakeBringList, bring  # noqa: F401

OPTIONS = {
    "battery_enabled": True,
    "battery_threshold": 20,
    "battery_category": "Smarthome",
}


@pytest.fixture(autouse=True)
def _no_confirm_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    """Create battery tasks at once, unless a test checks the wait."""
    monkeypatch.setattr(
        "custom_components.brainstorm.battery.CONFIRM_DELAY", timedelta(0)
    )


def _device(hass: HomeAssistant, name: str, kind: str | None, quantity: Any = 2) -> str:
    """A device with a battery sensor and, with a type, Battery Notes."""
    entry = MockConfigEntry(domain="test")
    entry.add_to_hass(hass)
    device = (
        dr.async_get(hass)
        .async_get_or_create(
            config_entry_id=entry.entry_id, identifiers={("test", name)}, name=name
        )
        .id
    )
    slug = name.lower().replace(" ", "_")
    registry = er.async_get(hass)
    registry.async_get_or_create(
        "sensor", "zha", slug, suggested_object_id=f"{slug}_batterie", device_id=device
    )
    if kind is not None:
        registry.async_get_or_create(
            "sensor",
            "battery_notes",
            f"{slug}_type",
            suggested_object_id=f"{slug}_battery_type",
            device_id=device,
        )
        hass.states.async_set(
            f"sensor.{slug}_battery_type",
            f"{quantity}× {kind}",
            {"battery_type": kind, "battery_quantity": quantity},
        )
    return device


def _level(hass: HomeAssistant, name: str, level: int) -> None:
    slug = name.lower().replace(" ", "_")
    hass.states.async_set(
        f"sensor.{slug}_batterie",
        str(level),
        {"device_class": "battery", "unit_of_measurement": "%"},
    )


def _replaced(hass: HomeAssistant) -> list[dict[str, Any]]:
    """Battery Notes with its service, returning what it was told."""
    calls: list[dict[str, Any]] = []

    async def replaced(call: ServiceCall) -> None:
        calls.append(dict(call.data))

    hass.services.async_register("battery_notes", "set_battery_replaced", replaced)
    return calls


def _task(store: BrainstormStore, device: str) -> dict[str, Any]:
    return next(i for i in store.ideas if i.get("battery") == f"device:{device}")


async def test_types_in_tasks_and_new_batteries_reported(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """A task names the type, and only ticking it off by hand reports it."""
    calls = _replaced(hass)
    hall = _device(hass, "Bewegungsmelder Flur", "AA")
    bath = _device(hass, "Thermometer Bad", "CR2032", "1")
    plain = _device(hass, "Fenster Bad", None)
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Smarthome"]}, options=OPTIONS
    )
    store = entry.runtime_data
    for name in ("Bewegungsmelder Flur", "Thermometer Bad", "Fenster Bad"):
        _level(hass, name, 10)
    await hass.async_block_till_done()
    assert _task(store, hall)["text"] == (
        "Batterie wechseln: Bewegungsmelder Flur (10 %) · 2× AA"
    )
    assert (
        _task(store, bath)["text"]
        == "Batterie wechseln: Thermometer Bad (10 %) · 1× CR2032"
    )
    assert _task(store, plain)["text"] == "Batterie wechseln: Fenster Bad (10 %)"
    assert battery_type(hass, "sensor.irgendwas") is None
    assert needed_batteries(hass, store) == {"AA": 2, "CR2032": 1}

    # Ticked off by hand: Battery Notes learns about the new battery
    await store.async_update_idea(_task(store, hall)["id"], status="completed")
    await hass.async_block_till_done()
    assert calls == [{"device_id": hall}]
    # A device unknown to Battery Notes is not reported
    await store.async_update_idea(_task(store, plain)["id"], status="completed")
    await hass.async_block_till_done()
    assert len(calls) == 1
    # Closed by the new level, Battery Notes sees the battery itself
    _level(hass, "Thermometer Bad", 100)
    await hass.async_block_till_done()
    assert _task(store, bath)["status"] == "completed"
    assert len(calls) == 1


async def test_switched_off(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """Without the switches, tasks name no type and report nothing."""
    calls = _replaced(hass)
    hall = _device(hass, "Bewegungsmelder Flur", "AA")
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Smarthome"]},
        options={**OPTIONS, "battery_notes_enabled": False},
    )
    store = entry.runtime_data
    _level(hass, "Bewegungsmelder Flur", 10)
    await hass.async_block_till_done()
    assert (
        _task(store, hall)["text"] == "Batterie wechseln: Bewegungsmelder Flur (10 %)"
    )
    await store.async_update_idea(_task(store, hall)["id"], status="completed")
    await hass.async_block_till_done()
    assert calls == []


async def test_batteries_to_bring(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    bring: dict[str, FakeBringList],  # noqa: F811
) -> None:
    """The batteries of the open tasks go on Bring, each type once."""
    _replaced(hass)
    _device(hass, "Bewegungsmelder Flur", "AA")
    _device(hass, "Fernbedienung", "AA")
    _device(hass, "Thermometer Bad", "CR2032", 1)
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Smarthome", "Einkauf"]},
        options={
            **OPTIONS,
            "bring_enabled": True,
            "bring_category": "Einkauf",
            "bring_default_list": HOME,
        },
    )
    store = entry.runtime_data

    async def send() -> dict[str, Any]:
        return await hass.services.async_call(
            DOMAIN, "batteries_to_bring", {}, blocking=True, return_response=True
        )

    with pytest.raises(ServiceValidationError) as err:
        await send()
    assert err.value.translation_key == "battery_bring_nothing"
    assert store.get_overview_attributes()["battery_notes"] is None

    for name in ("Bewegungsmelder Flur", "Fernbedienung", "Thermometer Bad"):
        _level(hass, name, 5)
    await hass.async_block_till_done()
    assert store.get_overview_attributes()["battery_notes"] == {
        "categories": ["Smarthome"],
        "needed": {"AA": 4, "CR2032": 1},
    }
    bring[HOME].put("batterien cr2032")
    assert await send() == {
        "entity_id": HOME,
        "added": ["Batterien AA"],
        "skipped": ["Batterien CR2032"],
    }
    item = next(i for i in bring[HOME].items if i.summary == "Batterien AA")
    assert item.description == "4×"

    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(
            DOMAIN, "batteries_to_bring", {"list": "todo.nix"}, blocking=True
        )
    assert err.value.translation_key == "bring_list_unknown"


async def test_settings_page(hass: HomeAssistant, setup_entry: SetupEntry) -> None:
    """The page is offered with Battery Notes and saves its switches."""
    _replaced(hass)
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Smarthome"]}, options=OPTIONS
    )
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "integrations"}
    )
    assert "battery_notes" in result["menu_options"]
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "battery_notes"}
    )
    assert result["type"] is FlowResultType.FORM
    fields = {str(key) for key in result["data_schema"].schema}
    assert fields == {"battery_notes_enabled", "battery_notes_replaced", "go_back"}
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"battery_notes_enabled": True, "battery_notes_replaced": False},
    )
    assert result["step_id"] == "integrations"
    assert entry.options["battery_notes_replaced"] is False
    hass.config_entries.options.async_abort(result["flow_id"])
