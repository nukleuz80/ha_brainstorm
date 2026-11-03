"""WebSocket commands for the ideas each user may see and change."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
import homeassistant.helpers.config_validation as cv

from .const import CONF_SHARE_USERS
from .store import get_loaded_store


@callback
def async_register_commands(hass: HomeAssistant) -> None:
    """Register the WebSocket commands."""
    websocket_api.async_register_command(hass, websocket_get_ideas)
    websocket_api.async_register_command(hass, websocket_set_map_positions)


@websocket_api.websocket_command({vol.Required("type"): "brainstorm/ideas"})
@websocket_api.async_response
async def websocket_get_ideas(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return the ideas of the connected user."""
    store = get_loaded_store(hass)
    if store is None:
        connection.send_error(
            msg["id"], websocket_api.ERR_NOT_FOUND, "Brainstorm is not loaded"
        )
        return
    allowed = store.options.get(CONF_SHARE_USERS) or []
    users = [
        user
        for user in await hass.auth.async_get_users()
        if user.is_active and not user.system_generated
    ]
    names = {user.id: user.name or user.id for user in users}
    result = store.get_overview_attributes(connection.user.id)
    pictures = {
        state.attributes["user_id"]: state.attributes.get("entity_picture")
        for state in hass.states.async_all("person")
        if state.attributes.get("user_id")
    }
    for idea in (*result["ideas"], *result["completed_ideas"]):
        idea["owner_name"] = names.get(idea.get("owner"), "")
        if author := idea.get("created_by"):
            idea["author_name"] = names.get(author, "")
            idea["author_picture"] = pictures.get(author)
    result["current_user"] = connection.user.id
    result["share_users"] = [
        {"id": user.id, "name": names[user.id]}
        for user in users
        if user.id != connection.user.id and (not allowed or user.id in allowed)
    ]
    connection.send_result(msg["id"], result)


MAP_POSITION = vol.Any(
    None,
    vol.Schema(
        {
            vol.Required("x"): vol.All(vol.Coerce(float), vol.Range(-1e5, 1e5)),
            vol.Required("y"): vol.All(vol.Coerce(float), vol.Range(-1e5, 1e5)),
        }
    ),
)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "brainstorm/map_positions",
        vol.Required("positions"): vol.All(
            vol.Schema({cv.string: MAP_POSITION}), vol.Length(max=500)
        ),
    }
)
@websocket_api.async_response
async def websocket_set_map_positions(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Keep where the connected user placed ideas on the mind map."""
    store = get_loaded_store(hass)
    if store is None:
        connection.send_error(
            msg["id"], websocket_api.ERR_NOT_FOUND, "Brainstorm is not loaded"
        )
        return
    changed = await store.async_set_map_positions(
        msg["positions"], connection.user.id
    )
    connection.send_result(msg["id"], {"changed": changed})
