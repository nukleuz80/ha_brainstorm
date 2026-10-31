"""WebSocket command that gives each user only the ideas they may see."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import CONF_SHARE_USERS, DOMAIN


@callback
def async_register_commands(hass: HomeAssistant) -> None:
    """Register the WebSocket commands."""
    websocket_api.async_register_command(hass, websocket_get_ideas)


@websocket_api.websocket_command({vol.Required("type"): "brainstorm/ideas"})
@websocket_api.async_response
async def websocket_get_ideas(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return the ideas of the connected user."""
    store = hass.data.get(DOMAIN, {}).get("primary_store")
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
    for idea in (*result["ideas"], *result["completed_ideas"]):
        idea["owner_name"] = names.get(idea.get("owner"), "")
    result["current_user"] = connection.user.id
    result["share_users"] = [
        {"id": user.id, "name": names[user.id]}
        for user in users
        if user.id != connection.user.id and (not allowed or user.id in allowed)
    ]
    connection.send_result(msg["id"], result)
