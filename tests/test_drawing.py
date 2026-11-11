"""Tests for freehand drawing on the map of a category."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.setup import async_setup_component
import pytest
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.brainstorm.const import DRAW_MAX_STROKES

from .conftest import SetupEntry


async def _ws(client: Any, **msg: Any) -> dict[str, Any]:
    await client.send_json_auto_id(msg)
    return await client.receive_json()


async def test_strokes_by_websocket(
    hass: HomeAssistant, setup_entry: SetupEntry, hass_ws_client: WebSocketGenerator
) -> None:
    """Strokes are added, read and removed per category; the sensor counts changes."""
    assert await async_setup_component(hass, "websocket_api", {})
    entry = await setup_entry()
    store = entry.runtime_data
    client = await hass_ws_client(hass)

    assert (await _ws(client, type="brainstorm/drawing", category="Alltag"))["result"] == {"strokes": []}
    reply = await _ws(
        client,
        type="brainstorm/add_stroke",
        category="alltag",
        kind="pen",
        points=[[0, 0], [10.04, 5], [20, -3]],
        color="red",
        width=4,
    )
    stroke = reply["result"]["stroke"]
    assert stroke["points"] == [[0.0, 0.0], [10.0, 5.0], [20.0, -3.0]]
    assert stroke["kind"] == "pen"
    arrow = (
        await _ws(
            client,
            type="brainstorm/add_stroke",
            category="Alltag",
            kind="arrow",
            points=[[0, 0], [50, 50], [90, 90]],
            color="blue",
            width=3,
        )
    )["result"]["stroke"]
    assert arrow["points"] == [[0.0, 0.0], [50.0, 50.0]]
    revs = store.get_overview_attributes(None)["drawing_revs"]
    assert revs == {"Alltag": 2}

    strokes = (await _ws(client, type="brainstorm/drawing", category="Alltag"))["result"]["strokes"]
    assert [s["id"] for s in strokes] == [stroke["id"], arrow["id"]]
    # Another list stays empty
    assert (await _ws(client, type="brainstorm/drawing", category="Projekte"))["result"]["strokes"] == []

    # Bad input is refused
    for bad in (
        {"kind": "laser", "color": "red"},
        {"kind": "pen", "color": "url(x)"},
        {"kind": "pen", "color": "red", "points": [[1, 1]]},
    ):
        msg = {"type": "brainstorm/add_stroke", "category": "Alltag", "points": [[0, 0], [1, 1]], "width": 2, **bad}
        assert not (await _ws(client, **msg))["success"]
    unknown = await _ws(
        client, type="brainstorm/add_stroke", category="Gibt es nicht",
        kind="pen", points=[[0, 0], [1, 1]], color="red", width=2,
    )
    assert unknown["error"]["code"] == "category_not_found"

    reply = await _ws(client, type="brainstorm/delete_strokes", category="Alltag", ids=[stroke["id"], "missing"])
    assert reply["result"] == {"removed": 1}
    reply = await _ws(client, type="brainstorm/delete_strokes", category="Alltag")
    assert reply["result"] == {"removed": 1}
    assert store.drawing("Alltag") == []
    # Nothing left: the category drops out of the counters
    assert store.get_overview_attributes(None)["drawing_revs"] == {}


async def test_drawing_limit_and_category_removal(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """A map holds a limited number of strokes; removing a list drops them."""
    entry = await setup_entry()
    store = entry.runtime_data
    for _ in range(DRAW_MAX_STROKES):
        await store.async_add_stroke("Projekte", "ellipse", [[0, 0], [5, 5]], "green", 2)
    with pytest.raises(ServiceValidationError) as err:
        await store.async_add_stroke("Projekte", "pen", [[0, 0], [5, 5]], "green", 2)
    assert err.value.translation_key == "drawing_full"

    # Strokes survive a reload
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    store = entry.runtime_data
    assert len(store.drawing("Projekte")) == DRAW_MAX_STROKES

    await store.async_remove_category("Projekte")
    await store.async_add_category("Projekte")
    assert store.drawing("Projekte") == []


async def test_drawing_in_json_export(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """The export carries the strokes, the import adds clean new ones once."""
    entry = await setup_entry()
    store = entry.runtime_data
    kept = await store.async_add_stroke("Alltag", "pen", [[0, 0], [5, 5]], "red", 3)
    exported = await hass.services.async_call(
        "brainstorm", "export_json", {}, blocking=True, return_response=True
    )
    assert exported["drawings"] == {"Alltag": [kept]}
    only = await hass.services.async_call(
        "brainstorm", "export_json", {"category": "Projekte"}, blocking=True, return_response=True
    )
    assert only["drawings"] == {}

    await store.async_delete_strokes("Alltag")
    exported["drawings"]["Alltag"].extend(
        [
            {"id": "bad00001", "kind": "pen", "color": "red;x", "width": 3, "points": [[0, 0], [1, 1]]},
            {"id": "bad00002", "kind": "pen", "color": "red", "width": 3, "points": [[0, "x"], [1, 1]]},
            {"id": "<script>", "kind": "pen", "color": "red", "width": 3, "points": [[0, 0], [1, 1]]},
        ]
    )
    exported["drawings"]["Gibt es nicht"] = [kept]
    for _ in range(2):
        await hass.services.async_call(
            "brainstorm", "import_json", {"data": exported}, blocking=True, return_response=True
        )
    assert store.drawing("Alltag") == [kept]
    assert "Gibt es nicht" not in store.categories
