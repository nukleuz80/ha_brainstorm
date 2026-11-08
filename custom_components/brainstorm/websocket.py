"""WebSocket commands for the ideas each user may see and change."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
import homeassistant.helpers.config_validation as cv

from .ai import AIUnavailableError
from .const import CONF_SHARE_USERS
from .store import get_loaded_store

# Error codes the cards translate for the person
ERR_AI_NOT_CONFIGURED = "ai_not_configured"
ERR_AI_FAILED = "ai_failed"
ERR_AI_UNAVAILABLE = "ai_unavailable"


@callback
def async_register_commands(hass: HomeAssistant) -> None:
    """Register the WebSocket commands."""
    websocket_api.async_register_command(hass, websocket_get_ideas)
    websocket_api.async_register_command(hass, websocket_set_map_positions)
    websocket_api.async_register_command(hass, websocket_suggest_subtasks)
    websocket_api.async_register_command(hass, websocket_summarize_branch)
    websocket_api.async_register_command(hass, websocket_suggest_parents)


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
        if worker := (idea.get("in_progress") or {}).get("by"):
            idea["in_progress"]["name"] = names.get(worker, "")
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


@websocket_api.websocket_command(
    {
        vol.Required("type"): "brainstorm/suggest_subtasks",
        vol.Required("idea_id"): cv.string,
        vol.Optional("language"): vol.All(cv.string, vol.Length(max=10)),
    }
)
@websocket_api.async_response
async def websocket_suggest_subtasks(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Let the AI suggest subtasks for an idea the user may change."""
    store = get_loaded_store(hass)
    if store is None:
        connection.send_error(
            msg["id"], websocket_api.ERR_NOT_FOUND, "Brainstorm is not loaded"
        )
        return
    idea = store.get_idea(msg["idea_id"])
    if idea is None or not store.can_access(idea, connection.user.id):
        connection.send_error(msg["id"], websocket_api.ERR_NOT_FOUND, "Unknown idea")
        return
    if not store.can_edit(idea, connection.user.id):
        connection.send_error(
            msg["id"], websocket_api.ERR_UNAUTHORIZED, "No right to change this idea"
        )
        return
    if not store.ai_subtasks_available:
        connection.send_error(
            msg["id"], ERR_AI_NOT_CONFIGURED, "No AI task entity is set up"
        )
        return
    try:
        suggestions = await store.async_suggest_subtasks(idea, msg.get("language"))
    except AIUnavailableError:
        connection.send_error(
            msg["id"], ERR_AI_UNAVAILABLE, "The AI did not answer, try again later"
        )
        return
    if suggestions is None:
        connection.send_error(msg["id"], ERR_AI_FAILED, "The AI gave no subtasks")
        return
    connection.send_result(msg["id"], {"suggestions": suggestions})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "brainstorm/summarize_branch",
        vol.Required("idea_id"): cv.string,
        vol.Optional("language"): vol.All(cv.string, vol.Length(max=10)),
    }
)
@websocket_api.async_response
async def websocket_summarize_branch(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Let the AI sum up a note and its subtasks; nothing is stored."""
    store = get_loaded_store(hass)
    if store is None:
        connection.send_error(
            msg["id"], websocket_api.ERR_NOT_FOUND, "Brainstorm is not loaded"
        )
        return
    idea = store.get_idea(msg["idea_id"])
    user_id = connection.user.id
    if idea is None or not store.can_access(idea, user_id):
        connection.send_error(msg["id"], websocket_api.ERR_NOT_FOUND, "Unknown idea")
        return
    if not store.ai_subtasks_available:
        connection.send_error(
            msg["id"], ERR_AI_NOT_CONFIGURED, "No AI task entity is set up"
        )
        return
    try:
        summary = await store.async_summarize_branch(idea, user_id, msg.get("language"))
    except AIUnavailableError:
        connection.send_error(
            msg["id"], ERR_AI_UNAVAILABLE, "The AI did not answer, try again later"
        )
        return
    if summary is None:
        connection.send_error(msg["id"], ERR_AI_FAILED, "The AI gave no summary")
        return
    connection.send_result(
        msg["id"], {"summary": summary, "can_edit": store.can_edit(idea, user_id)}
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "brainstorm/suggest_parents",
        vol.Required("category"): vol.All(cv.string, vol.Length(max=100)),
        vol.Optional("language"): vol.All(cv.string, vol.Length(max=10)),
    }
)
@websocket_api.async_response
async def websocket_suggest_parents(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Let the AI suggest where loose notes of a category belong; nothing is stored."""
    store = get_loaded_store(hass)
    if store is None:
        connection.send_error(
            msg["id"], websocket_api.ERR_NOT_FOUND, "Brainstorm is not loaded"
        )
        return
    if not store.ai_subtasks_available:
        connection.send_error(
            msg["id"], ERR_AI_NOT_CONFIGURED, "No AI task entity is set up"
        )
        return
    try:
        suggestions = await store.async_suggest_parents(
            msg["category"], connection.user.id, msg.get("language")
        )
    except AIUnavailableError:
        connection.send_error(
            msg["id"], ERR_AI_UNAVAILABLE, "The AI did not answer, try again later"
        )
        return
    if suggestions is None:
        connection.send_error(
            msg["id"], ERR_AI_FAILED, "There are no loose notes to sort in"
        )
        return
    connection.send_result(msg["id"], {"suggestions": suggestions})
