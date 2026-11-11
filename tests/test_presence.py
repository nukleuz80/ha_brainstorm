"""Tests for showing who has a map open right now."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.brainstorm.const import STORAGE_KEY
from custom_components.brainstorm.presence import get_presence

from .conftest import SetupEntry


async def _present(client: Any) -> list[dict[str, Any]]:
    msg = await client.receive_json()
    assert msg["type"] == "event"
    return msg["event"]["present"]


async def test_presence_follows_open_maps(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
    hass_storage: dict[str, Any],
) -> None:
    """Joining, editing and leaving reach every open map, nothing is stored."""
    assert await async_setup_component(hass, "websocket_api", {})
    entry = await setup_entry()
    olaf = await hass_ws_client(hass)
    frida = await hass_ws_client(hass, hass_read_only_access_token)

    await olaf.send_json_auto_id(
        {"type": "brainstorm/presence/subscribe", "token": "olafmap1", "category": "Alltag"}
    )
    assert (await olaf.receive_json())["success"]
    present = await _present(olaf)
    assert [p["key"] for p in present] == ["olafmap1"]
    assert present[0]["category"] == "Alltag"
    assert present[0]["editing"] is None

    await frida.send_json_auto_id(
        {"type": "brainstorm/presence/subscribe", "token": "fridamap", "category": "Alltag"}
    )
    assert (await frida.receive_json())["success"]
    # Frida's join reaches Olaf, she gets the list after her result
    joined = await _present(olaf)
    assert {p["key"] for p in joined} == {"olafmap1", "fridamap"}
    frida_user = hass.auth.async_validate_access_token(hass_read_only_access_token).user
    assert next(p for p in joined if p["key"] == "fridamap")["user_id"] == frida_user.id
    assert len(await _present(frida)) == 2

    await frida.send_json_auto_id(
        {"type": "brainstorm/presence/update", "token": "fridamap", "category": "Alltag", "editing": "abc12345"}
    )
    assert (await frida.receive_json())["success"]
    editing = await _present(olaf)
    assert next(p for p in editing if p["key"] == "fridamap")["editing"] == "abc12345"
    await _present(frida)

    # The same again tells nobody anything
    await frida.send_json_auto_id(
        {"type": "brainstorm/presence/update", "token": "fridamap", "category": "Alltag", "editing": "abc12345"}
    )
    assert (await frida.receive_json())["success"]

    # Nobody updates another connection's map, and a bad token is refused
    await olaf.send_json_auto_id(
        {"type": "brainstorm/presence/update", "token": "fridamap", "editing": None}
    )
    assert (await olaf.receive_json())["error"]["code"] == "not_found"
    await olaf.send_json_auto_id(
        {"type": "brainstorm/presence/subscribe", "token": "<b>x</b>"}
    )
    assert not (await olaf.receive_json())["success"]

    # Closing the connection removes Frida for Olaf
    await frida.close()
    await hass.async_block_till_done()
    left = await _present(olaf)
    assert [p["key"] for p in left] == ["olafmap1"]

    # Nothing of it goes into the stored data
    assert len(get_presence(hass).entries) == 1
    await entry.runtime_data.async_save()
    stored = str(hass_storage[STORAGE_KEY])
    assert "fridamap" not in stored and "olafmap1" not in stored
