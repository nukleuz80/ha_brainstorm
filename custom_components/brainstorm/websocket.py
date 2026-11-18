"""WebSocket commands for the ideas each user may see and change."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
import homeassistant.helpers.config_validation as cv

from homeassistant.util import dt as dt_util

from .ai import MAP_INPUT_MAX_LENGTH, SPEECH_INPUT_MAX_LENGTH, AIUnavailableError
from .choreops import POINT_KINDS, SUGGEST_MAX_ITEMS
from .const import (
    CONF_SHARE_USERS,
    DRAW_COLORS,
    DRAW_KINDS,
    DRAW_MAX_POINTS,
    MAP_TAB_DETAILS,
    MAP_TAB_LAYOUTS,
    MAP_TAB_NAME_MAX,
    PIN_COLORS,
)
from .map_sources import SourceError
from .presence import get_presence
from .statistics import DEFAULT_WEEKS, MAX_WEEKS, build_statistics
from .store import TRASH_DAYS, BrainstormStore, get_loaded_store, habit_summary

# Error codes the cards translate for the person
ERR_AI_NOT_CONFIGURED = "ai_not_configured"
ERR_AI_FAILED = "ai_failed"
ERR_AI_UNAVAILABLE = "ai_unavailable"
ERR_TOO_FEW_NOTES = "too_few_notes"


@callback
def async_register_commands(hass: HomeAssistant) -> None:
    """Register the WebSocket commands."""
    websocket_api.async_register_command(hass, websocket_get_ideas)
    websocket_api.async_register_command(hass, websocket_set_map_positions)
    websocket_api.async_register_command(hass, websocket_set_pins)
    websocket_api.async_register_command(hass, websocket_get_drawing)
    websocket_api.async_register_command(hass, websocket_presence_subscribe)
    websocket_api.async_register_command(hass, websocket_presence_update)
    websocket_api.async_register_command(hass, websocket_add_stroke)
    websocket_api.async_register_command(hass, websocket_delete_strokes)
    websocket_api.async_register_command(hass, websocket_suggest_subtasks)
    websocket_api.async_register_command(hass, websocket_split_speech)
    websocket_api.async_register_command(hass, websocket_summarize_branch)
    websocket_api.async_register_command(hass, websocket_suggest_parents)
    websocket_api.async_register_command(hass, websocket_cluster_ideas)
    websocket_api.async_register_command(hass, websocket_suggest_points)
    websocket_api.async_register_command(hass, websocket_generate_map)
    websocket_api.async_register_command(hass, websocket_get_comments)
    websocket_api.async_register_command(hass, websocket_get_trash)
    websocket_api.async_register_command(hass, websocket_get_statistics)
    websocket_api.async_register_command(hass, websocket_get_habit)
    websocket_api.async_register_command(hass, websocket_restore_trash)
    websocket_api.async_register_command(hass, websocket_purge_trash)
    websocket_api.async_register_command(hass, websocket_get_map_tabs)
    websocket_api.async_register_command(hass, websocket_save_map_tab)
    websocket_api.async_register_command(hass, websocket_delete_map_tab)
    websocket_api.async_register_command(hass, websocket_order_map_tabs)


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
        if timer_by := (idea.get("timer") or {}).get("by"):
            idea["timer"]["name"] = names.get(timer_by, "")
        people = set(idea.get("votes") or {})
        for users in (idea.get("reactions") or {}).values():
            people.update(users)
        if people:
            idea["people"] = {user: names.get(user, "") for user in people}
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


PIN = vol.Any(
    None,
    vol.Schema(
        {
            vol.Required("x"): vol.All(vol.Coerce(float), vol.Range(-1e5, 1e5)),
            vol.Required("y"): vol.All(vol.Coerce(float), vol.Range(-1e5, 1e5)),
            vol.Optional("color"): vol.In([*PIN_COLORS, ""]),
        }
    ),
)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "brainstorm/pins",
        vol.Required("pins"): vol.All(vol.Schema({cv.string: PIN}), vol.Length(max=500)),
    }
)
@websocket_api.async_response
async def websocket_set_pins(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Keep where the connected user placed notes on the pinboard."""
    store = get_loaded_store(hass)
    if store is None:
        connection.send_error(
            msg["id"], websocket_api.ERR_NOT_FOUND, "Brainstorm is not loaded"
        )
        return
    changed = await store.async_set_pins(msg["pins"], connection.user.id)
    connection.send_result(msg["id"], {"changed": changed})


PRESENCE_TOKEN = vol.All(cv.string, vol.Match(r"^[A-Za-z0-9]{6,40}$"))
PRESENCE_CATEGORY = vol.Any(None, vol.All(cv.string, vol.Length(max=100)))
PRESENCE_EDITING = vol.Any(None, vol.All(cv.string, vol.Length(max=40)))


@websocket_api.websocket_command(
    {
        vol.Required("type"): "brainstorm/presence/subscribe",
        vol.Required("token"): PRESENCE_TOKEN,
        vol.Optional("category"): PRESENCE_CATEGORY,
    }
)
@callback
def websocket_presence_subscribe(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Show this open map to the others and tell it who else is there.

    Nothing is stored: closing the map or losing the connection ends the
    subscription and removes the person.
    """
    presence = get_presence(hass)
    key = (id(connection), msg["token"])
    msg_id = msg["id"]

    @callback
    def forward(present: list[dict[str, Any]]) -> None:
        connection.send_message(
            websocket_api.event_message(msg_id, {"present": present})
        )

    user = connection.user
    if not presence.join(key, user.id, user.name or "", msg.get("category"), forward):
        connection.send_error(msg_id, "too_many", "Too many open maps")
        return
    connection.subscriptions[msg_id] = lambda: presence.leave(key)
    connection.send_result(msg_id)
    forward(presence.entries)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "brainstorm/presence/update",
        vol.Required("token"): PRESENCE_TOKEN,
        vol.Optional("category"): PRESENCE_CATEGORY,
        vol.Optional("editing"): PRESENCE_EDITING,
    }
)
@callback
def websocket_presence_update(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Tell the others which list this map shows and which note it edits."""
    presence = get_presence(hass)
    key = (id(connection), msg["token"])
    if not presence.knows(key):
        connection.send_error(msg["id"], websocket_api.ERR_NOT_FOUND, "Not subscribed")
        return
    # The answer comes before the news it causes
    connection.send_result(msg["id"])
    presence.update(key, msg.get("category"), msg.get("editing"))


def _drawing_store(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg_id: int) -> Any:
    store = get_loaded_store(hass)
    if store is None:
        connection.send_error(msg_id, websocket_api.ERR_NOT_FOUND, "Brainstorm is not loaded")
    return store


@websocket_api.websocket_command(
    {
        vol.Required("type"): "brainstorm/drawing",
        vol.Required("category"): cv.string,
    }
)
@callback
def websocket_get_drawing(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Send the strokes drawn on the map of a category."""
    if (store := _drawing_store(hass, connection, msg["id"])) is None:
        return
    try:
        strokes = store.drawing(msg["category"])
    except ServiceValidationError as err:
        connection.send_error(msg["id"], websocket_api.ERR_NOT_FOUND, str(err))
        return
    connection.send_result(msg["id"], {"strokes": strokes})


POINT = vol.All(
    vol.ExactSequence(
        [
            vol.All(vol.Coerce(float), vol.Range(-1e5, 1e5)),
            vol.All(vol.Coerce(float), vol.Range(-1e5, 1e5)),
        ]
    )
)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "brainstorm/add_stroke",
        vol.Required("category"): cv.string,
        vol.Required("kind"): vol.In(DRAW_KINDS),
        vol.Required("points"): vol.All(
            [POINT], vol.Length(min=2, max=DRAW_MAX_POINTS)
        ),
        vol.Required("color"): vol.In(DRAW_COLORS),
        vol.Required("width"): vol.All(vol.Coerce(int), vol.Range(1, 16)),
    }
)
@websocket_api.async_response
async def websocket_add_stroke(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Draw a stroke, an arrow or an ellipse on the map of a category."""
    if (store := _drawing_store(hass, connection, msg["id"])) is None:
        return
    try:
        stroke = await store.async_add_stroke(
            msg["category"],
            msg["kind"],
            [list(point) for point in msg["points"]],
            msg["color"],
            msg["width"],
        )
    except ServiceValidationError as err:
        # The card explains a full map or an unknown list in its own words
        connection.send_error(
            msg["id"], err.translation_key or websocket_api.ERR_INVALID_FORMAT, str(err)
        )
        return
    connection.send_result(msg["id"], {"stroke": stroke})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "brainstorm/delete_strokes",
        vol.Required("category"): cv.string,
        vol.Optional("ids"): vol.All([cv.string], vol.Length(max=500)),
    }
)
@websocket_api.async_response
async def websocket_delete_strokes(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Remove strokes from a map, all of them without IDs."""
    if (store := _drawing_store(hass, connection, msg["id"])) is None:
        return
    try:
        removed = await store.async_delete_strokes(msg["category"], msg.get("ids"))
    except ServiceValidationError as err:
        connection.send_error(msg["id"], websocket_api.ERR_NOT_FOUND, str(err))
        return
    connection.send_result(msg["id"], {"removed": removed})


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
        vol.Required("type"): "brainstorm/split_speech",
        vol.Required("text"): vol.All(cv.string, vol.Length(max=SPEECH_INPUT_MAX_LENGTH)),
        vol.Optional("language"): vol.All(cv.string, vol.Length(max=10)),
    }
)
@websocket_api.async_response
async def websocket_split_speech(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Split freely spoken text into tasks to check first; nothing is stored."""
    store = get_loaded_store(hass)
    if store is None:
        connection.send_error(
            msg["id"], websocket_api.ERR_NOT_FOUND, "Brainstorm is not loaded"
        )
        return
    result = await store.async_split_speech(msg["text"], msg.get("language"))
    connection.send_result(msg["id"], result)


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


@websocket_api.websocket_command(
    {
        vol.Required("type"): "brainstorm/cluster_ideas",
        vol.Required("category"): vol.All(cv.string, vol.Length(max=100)),
        vol.Optional("language"): vol.All(cv.string, vol.Length(max=10)),
    }
)
@websocket_api.async_response
async def websocket_cluster_ideas(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Let the AI group loose notes of a category into themes; nothing is stored."""
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
        themes = await store.async_cluster_ideas(
            msg["category"], connection.user.id, msg.get("language")
        )
    except AIUnavailableError:
        connection.send_error(
            msg["id"], ERR_AI_UNAVAILABLE, "The AI did not answer, try again later"
        )
        return
    if themes is None:
        connection.send_error(
            msg["id"], ERR_TOO_FEW_NOTES, "There are too few loose notes to group"
        )
        return
    connection.send_result(msg["id"], {"themes": themes})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "brainstorm/choreops/suggest_points",
        vol.Required("ids"): vol.All(
            cv.ensure_list, [cv.string], vol.Length(min=1, max=SUGGEST_MAX_ITEMS)
        ),
        vol.Optional("kind", default="chore"): vol.In(POINT_KINDS),
        vol.Optional("language"): vol.All(cv.string, vol.Length(max=10)),
    }
)
@websocket_api.async_response
async def websocket_suggest_points(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Suggest ChoreOps points for tasks or costs for wishes; nothing is stored."""
    store = get_loaded_store(hass)
    if store is None:
        connection.send_error(
            msg["id"], websocket_api.ERR_NOT_FOUND, "Brainstorm is not loaded"
        )
        return
    visible = [
        idea_id
        for idea_id in msg["ids"]
        if (idea := store.get_idea(idea_id)) is not None
        and store.can_access(idea, connection.user.id)
    ]
    result = await store.async_suggest_points(visible, msg["kind"], msg.get("language"))
    connection.send_result(msg["id"], result)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "brainstorm/generate_map",
        vol.Optional("text", default=""): vol.All(
            cv.string, vol.Length(max=MAP_INPUT_MAX_LENGTH * 2)
        ),
        vol.Inclusive("idea_id", "attachment"): cv.string,
        vol.Inclusive("attachment_id", "attachment"): cv.string,
        vol.Optional("language"): vol.All(cv.string, vol.Length(max=10)),
    }
)
@websocket_api.async_response
async def websocket_generate_map(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Let the AI turn a topic, a text, a web page or a PDF into a mind map.

    Nothing is stored, the person picks what to keep.
    """
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
    if not msg["text"].strip() and "attachment_id" not in msg:
        connection.send_error(
            msg["id"], websocket_api.ERR_INVALID_FORMAT, "Nothing to make a map from"
        )
        return
    try:
        nodes = await store.async_generate_map_from_source(
            text=msg["text"],
            idea_id=msg.get("idea_id"),
            attachment_id=msg.get("attachment_id"),
            user_id=connection.user.id,
            language=msg.get("language"),
        )
    except SourceError as err:
        connection.send_error(msg["id"], err.code, str(err))
        return
    except AIUnavailableError:
        connection.send_error(
            msg["id"], ERR_AI_UNAVAILABLE, "The AI did not answer, try again later"
        )
        return
    if nodes is None:
        connection.send_error(msg["id"], ERR_AI_FAILED, "The AI gave no mind map")
        return
    connection.send_result(msg["id"], {"nodes": nodes})


@websocket_api.websocket_command(
    {vol.Required("type"): "brainstorm/comments", vol.Required("idea_id"): cv.string}
)
@websocket_api.async_response
async def websocket_get_comments(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return the comments of a note with the names and pictures of their authors."""
    store = get_loaded_store(hass)
    if store is None:
        connection.send_error(
            msg["id"], websocket_api.ERR_NOT_FOUND, "Brainstorm is not loaded"
        )
        return
    user_id = connection.user.id
    try:
        comments = store.get_comments(msg["idea_id"], user_id)
    except ServiceValidationError:
        connection.send_error(msg["id"], websocket_api.ERR_NOT_FOUND, "Unknown idea")
        return
    names = {user.id: user.name or "" for user in await hass.auth.async_get_users()}
    pictures = {
        state.attributes["user_id"]: state.attributes.get("entity_picture")
        for state in hass.states.async_all("person")
        if state.attributes.get("user_id")
    }
    idea = store.get_idea(msg["idea_id"]) or {}
    can_edit = store.can_edit(idea, user_id)
    for comment in comments:
        author = comment.get("by")
        comment["name"] = names.get(author, "")
        comment["picture"] = pictures.get(author)
        comment["mine"] = author == user_id
        comment["can_delete"] = author == user_id or can_edit
    connection.send_result(msg["id"], {"comments": comments, "can_edit": can_edit})


def _trash_store(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg_id: int
) -> BrainstormStore | None:
    """Return the store, or answer that Brainstorm is not loaded."""
    store = get_loaded_store(hass)
    if store is None:
        connection.send_error(msg_id, websocket_api.ERR_NOT_FOUND, "Brainstorm is not loaded")
    return store


@websocket_api.websocket_command(
    {vol.Required("type"): "brainstorm/habit", vol.Required("idea_id"): cv.string}
)
@callback
def websocket_get_habit(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return the streak and recent days of a habit, for its calendar."""
    if (store := _trash_store(hass, connection, msg["id"])) is None:
        return
    idea = store.get_idea(msg["idea_id"])
    summary = habit_summary(idea) if idea is not None else None
    if summary is None or not store.can_access(idea, connection.user.id):
        connection.send_error(msg["id"], websocket_api.ERR_NOT_FOUND, "No such habit")
        return
    connection.send_result(msg["id"], summary)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "brainstorm/statistics",
        vol.Optional("weeks", default=DEFAULT_WEEKS): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=MAX_WEEKS)
        ),
        vol.Optional("category"): vol.Any(None, cv.string),
    }
)
@websocket_api.async_response
async def websocket_get_statistics(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return done per week, lead time and who ticked off, of the visible notes."""
    if (store := _trash_store(hass, connection, msg["id"])) is None:
        return
    names = {user.id: user.name or "" for user in await hass.auth.async_get_users()}
    connection.send_result(
        msg["id"],
        build_statistics(
            store.visible_ideas(connection.user.id),
            dt_util.now(),
            names,
            msg["weeks"],
            msg.get("category"),
        ),
    )


@websocket_api.websocket_command({vol.Required("type"): "brainstorm/trash"})
@callback
def websocket_get_trash(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return the deleted notes this user may bring back, newest first."""
    if (store := _trash_store(hass, connection, msg["id"])) is None:
        return
    connection.send_result(
        msg["id"],
        {"items": store.trash_items(connection.user.id), "days": TRASH_DAYS},
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "brainstorm/trash/restore",
        vol.Required("ids"): vol.All(cv.ensure_list, [cv.string]),
    }
)
@websocket_api.async_response
async def websocket_restore_trash(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Bring notes back from the trash."""
    if (store := _trash_store(hass, connection, msg["id"])) is None:
        return
    restored = [
        idea_id
        for idea_id in msg["ids"]
        if await store.async_restore_idea(idea_id, connection.user.id) is not None
    ]
    connection.send_result(msg["id"], {"restored": restored})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "brainstorm/trash/delete",
        vol.Required("ids"): vol.All(cv.ensure_list, [cv.string]),
    }
)
@websocket_api.async_response
async def websocket_purge_trash(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Delete notes from the trash for good."""
    if (store := _trash_store(hass, connection, msg["id"])) is None:
        return
    removed = await store.async_purge_trash(msg["ids"], connection.user.id)
    if removed:
        await store.async_cleanup_attachments()
    connection.send_result(msg["id"], {"deleted": removed})


@websocket_api.websocket_command({vol.Required("type"): "brainstorm/map_tabs"})
@callback
def websocket_get_map_tabs(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return the shared map tabs and the user's own."""
    if (store := _trash_store(hass, connection, msg["id"])) is None:
        return
    connection.send_result(msg["id"], {"tabs": store.map_tabs(connection.user.id)})


_TAB_FILTER = vol.Schema(
    {
        vol.Optional("query"): vol.All(cv.string, vol.Length(max=100)),
        vol.Optional("prios"): [cv.string],
        vol.Optional("tags"): [cv.string],
        vol.Optional("markers"): [cv.string],
        vol.Optional("overdue"): cv.boolean,
        vol.Optional("soon"): cv.boolean,
        vol.Optional("working"): cv.boolean,
        vol.Optional("myDay"): cv.boolean,
    }
)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "brainstorm/map_tabs/save",
        vol.Optional("tab_id"): cv.string,
        vol.Optional("name"): vol.All(cv.string, vol.Length(min=1, max=MAP_TAB_NAME_MAX)),
        vol.Optional("icon"): vol.All(cv.string, vol.Length(max=8)),
        vol.Optional("category"): vol.All(cv.string, vol.Length(min=1, max=100)),
        vol.Optional("focus"): vol.Any(None, cv.string),
        vol.Optional("branch"): cv.boolean,
        vol.Optional("layout"): vol.Any(None, vol.In(MAP_TAB_LAYOUTS)),
        vol.Optional("detail"): vol.Any(None, vol.In(MAP_TAB_DETAILS)),
        vol.Optional("filter"): _TAB_FILTER,
        vol.Optional("view"): vol.Any(
            None,
            vol.Schema(
                {
                    vol.Required("x"): vol.Coerce(float),
                    vol.Required("y"): vol.Coerce(float),
                    vol.Required("scale"): vol.Coerce(float),
                }
            ),
        ),
        vol.Optional("private"): cv.boolean,
    }
)
@websocket_api.async_response
async def websocket_save_map_tab(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Save the current view as a tab, or change a tab."""
    if (store := _trash_store(hass, connection, msg["id"])) is None:
        return
    # "id" is the message number, the tab comes as tab_id
    data = {k: v for k, v in msg.items() if k not in ("type", "id", "tab_id")}
    if "tab_id" in msg:
        data["id"] = msg["tab_id"]
    try:
        tab = await store.async_save_map_tab(data, connection.user.id)
    except ServiceValidationError as err:
        connection.send_error(
            msg["id"], err.translation_key or "invalid_tab", str(err)
        )
        return
    connection.send_result(msg["id"], {"tab": tab})


@websocket_api.websocket_command(
    {vol.Required("type"): "brainstorm/map_tabs/delete", vol.Required("tab_id"): cv.string}
)
@websocket_api.async_response
async def websocket_delete_map_tab(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Remove a map tab."""
    if (store := _trash_store(hass, connection, msg["id"])) is None:
        return
    if not await store.async_delete_map_tab(msg["tab_id"], connection.user.id):
        connection.send_error(msg["id"], websocket_api.ERR_NOT_FOUND, "No such tab")
        return
    connection.send_result(msg["id"], {"deleted": msg["tab_id"]})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "brainstorm/map_tabs/order",
        vol.Required("ids"): vol.All(cv.ensure_list, [cv.string]),
    }
)
@websocket_api.async_response
async def websocket_order_map_tabs(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Put the map tabs in a new order."""
    if (store := _trash_store(hass, connection, msg["id"])) is None:
        return
    await store.async_order_map_tabs(msg["ids"], connection.user.id)
    connection.send_result(msg["id"], {"tabs": store.map_tabs(connection.user.id)})
