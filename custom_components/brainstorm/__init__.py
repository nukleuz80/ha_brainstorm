"""Brainstorm Hub custom component for Home Assistant."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse, callback
from homeassistant.exceptions import (
    ConfigEntryNotReady,
    HomeAssistantError,
    ServiceValidationError,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.loader import async_get_integration
from homeassistant.util import dt as dt_util

from .alexa_skill import AlexaSkill
from .attachments import AttachmentCleaner, async_register_views
from .battery import BatteryWatcher
from .bring import BRING_MESSAGES, bring_message_target
from .const import (
    ATTR_CATEGORY,
    ATTR_COLOR,
    ATTR_ASSIGNEE,
    ATTR_LANGUAGE,
    ATTR_DEVICE,
    ATTR_DUE,
    ATTR_ECHOS,
    ATTR_ICON,
    ATTR_ID,
    ATTR_ORDER,
    ATTR_PARENT_ID,
    ATTR_PARSE_DUE,
    ATTR_PRIORITY,
    ATTR_RESULT,
    ATTR_DESCRIPTION,
    ATTR_IN_PROGRESS,
    ATTR_MARKERS,
    ATTR_PROGRESS,
    ATTR_SHAPE,
    ATTR_REMINDED_AT,
    ATTR_RESET,
    ATTR_SOURCE,
    ATTR_STATUS,
    ATTR_TAGS,
    ATTR_TEXT,
    ATTR_TRIGGER,
    ATTR_ZONE,
    DOMAIN,
    PLATFORMS,
    RESULT_MAX_LENGTH,
    DESCRIPTION_MAX_LENGTH,
    MARKERS,
    NODE_SHAPES,
    PROGRESS_STEPS,
    SERVICE_REORDER_IDEAS,
    SERVICE_DELETE_DONE,
    SERVICE_SET_CATEGORY_STYLE,
    SHARE_EDIT,
    SHARE_VIEW,
    VOICE_MODE_NATIVE,
)
from .echo_locks import EchoLockManager
from .frontend import async_register_frontend
from .llm import async_register_llm_api
from .reminders import ReminderManager, build_reminder_request
from .repairs import async_check_issues, async_delete_issues
from .store import BrainstormConfigEntry, BrainstormStore, get_loaded_store
from .todo_sync import TodoSyncManager
from .websocket import async_register_commands

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

SERVICE_ADD_IDEA = "add_idea"
SERVICE_UPDATE_IDEA = "update_idea"
SERVICE_DELETE_IDEA = "delete_idea"
SERVICE_RESTORE_IDEA = "restore_idea"
SERVICE_GET_IDEAS = "get_ideas"
SERVICE_SHARE = "share"
SERVICE_ADD_CATEGORY = "add_category"
SERVICE_REMOVE_CATEGORY = "remove_category"
SERVICE_EXPORT_MARKDOWN = "export_markdown"
SERVICE_GET_ANNOUNCEMENT = "get_announcement"
SERVICE_EXPORT_JSON = "export_json"
SERVICE_IMPORT_JSON = "import_json"
SERVICE_BRING_MESSAGE = "bring_message"

SERVICE_BRING_MESSAGE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ID): cv.string,
        vol.Required("message"): vol.In(BRING_MESSAGES),
    }
)

SERVICE_EXPORT_JSON_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_CATEGORY): cv.string,
        vol.Optional("path"): cv.string,
    }
)

SERVICE_IMPORT_JSON_SCHEMA = vol.Schema(
    {
        vol.Optional("data"): dict,
        vol.Optional("path"): cv.string,
    }
)

SERVICE_GET_ANNOUNCEMENT_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_CATEGORY): vol.Any(None, cv.string),
        vol.Optional(ATTR_DEVICE): vol.Any(None, cv.string),
    }
)

SERVICE_ADD_IDEA_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TEXT): cv.string,
        vol.Optional(ATTR_CATEGORY): vol.Any(None, cv.string),
        vol.Optional(ATTR_PRIORITY): vol.Any(None, cv.string),
        vol.Optional(ATTR_SOURCE): cv.string,
        vol.Optional(ATTR_DEVICE): vol.Any(None, cv.string),
        vol.Optional(ATTR_TAGS): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_PARENT_ID): vol.Any(None, cv.string),
        vol.Optional(ATTR_DUE): vol.Any(None, cv.datetime),
        vol.Optional(ATTR_PARSE_DUE): cv.boolean,
        vol.Optional(ATTR_ASSIGNEE): vol.Any(None, cv.entity_id),
        vol.Optional(ATTR_ZONE): vol.Any(None, cv.entity_id),
        vol.Optional(ATTR_LANGUAGE): vol.Any(None, cv.string),
        vol.Optional(ATTR_DESCRIPTION): vol.Any(
            None, vol.All(cv.string, vol.Length(max=DESCRIPTION_MAX_LENGTH))
        ),
    },
    extra=vol.ALLOW_EXTRA,
)

SERVICE_UPDATE_IDEA_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ID): cv.string,
        vol.Optional(ATTR_TEXT): cv.string,
        vol.Optional(ATTR_CATEGORY): cv.string,
        vol.Optional(ATTR_PRIORITY): vol.Any(None, cv.string),
        vol.Optional(ATTR_STATUS): vol.In(["active", "completed", "archived"]),
        vol.Optional(ATTR_DEVICE): vol.Any(None, cv.string),
        vol.Optional(ATTR_PARENT_ID): vol.Any(None, cv.string),
        vol.Optional(ATTR_ORDER): vol.Coerce(int),
        vol.Optional(ATTR_DUE): vol.Any(None, cv.datetime),
        vol.Optional(ATTR_ASSIGNEE): vol.Any(None, cv.entity_id),
        vol.Optional(ATTR_ZONE): vol.Any(None, cv.entity_id),
        vol.Optional(ATTR_ECHOS): vol.Any(None, cv.entity_ids),
        vol.Optional(ATTR_RESULT): vol.Any(
            None, vol.All(cv.string, vol.Length(max=RESULT_MAX_LENGTH))
        ),
        vol.Optional(ATTR_DESCRIPTION): vol.Any(
            None, vol.All(cv.string, vol.Length(max=DESCRIPTION_MAX_LENGTH))
        ),
        vol.Optional(ATTR_IN_PROGRESS): cv.boolean,
        vol.Optional(ATTR_SHAPE): vol.Any(None, "", vol.In(NODE_SHAPES)),
        vol.Optional(ATTR_MARKERS): vol.Any(
            None, vol.All(cv.ensure_list, [vol.In(MARKERS)])
        ),
        vol.Optional(ATTR_PROGRESS): vol.Any(
            None, vol.All(vol.Coerce(int), vol.In(PROGRESS_STEPS))
        ),
    },
    extra=vol.ALLOW_EXTRA,
)

SERVICE_SHARE_SCHEMA = vol.Schema(
    {
        vol.Optional("ids"): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_CATEGORY): cv.string,
        vol.Required("shares"): {cv.string: vol.In([None, SHARE_VIEW, SHARE_EDIT])},
    }
)

SERVICE_REORDER_IDEAS_SCHEMA = vol.Schema(
    {
        vol.Required("idea_ids"): vol.All(cv.ensure_list, [cv.string]),
    }
)

SERVICE_DELETE_IDEA_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ID): cv.string,
    }
)

SERVICE_DELETE_DONE_SCHEMA = vol.Schema(
    {
        vol.Optional("older_than_days", default=0): vol.All(
            vol.Coerce(int), vol.Range(min=0, max=3650)
        ),
    }
)

SERVICE_GET_IDEAS_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_CATEGORY): cv.string,
        vol.Optional(ATTR_PRIORITY): cv.string,
        vol.Optional(ATTR_STATUS, default="active"): vol.In(
            ["active", "completed", "all", ""]
        ),
    }
)

SERVICE_ADD_CATEGORY_SCHEMA = vol.Schema(
    {
        vol.Required("name"): cv.string,
        vol.Optional(ATTR_ICON): vol.Any(None, cv.string),
        vol.Optional(ATTR_COLOR): vol.Any(None, cv.string),
    }
)

SERVICE_SET_CATEGORY_STYLE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_CATEGORY): cv.string,
        vol.Optional(ATTR_ICON): vol.Any(None, cv.string),
        vol.Optional(ATTR_COLOR): vol.Any(None, cv.string),
        vol.Optional(ATTR_RESET, default=False): cv.boolean,
    }
)

SERVICE_REMOVE_CATEGORY_SCHEMA = vol.Schema(
    {
        vol.Required("name"): cv.string,
    }
)

SERVICE_EXPORT_MARKDOWN_SCHEMA = vol.Schema(
    {
        vol.Optional("path"): cv.string,
    }
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Brainstorm component and register its services."""
    _register_services(hass)
    async_register_commands(hass)
    async_register_views(hass)
    await async_register_frontend(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: BrainstormConfigEntry) -> bool:
    """Set up Brainstorm Hub from a config entry."""
    store = BrainstormStore(hass, {**entry.data, **entry.options})
    integration = await async_get_integration(hass, DOMAIN)
    store.integration_version = str(integration.version)
    skill = AlexaSkill(hass, store)
    try:
        await store.async_load()
        await skill.async_load()
    except HomeAssistantError as err:
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN,
            translation_key="store_not_readable",
            translation_placeholders={"error": str(err)},
        ) from err
    store.alexa_skill = skill

    entry.runtime_data = store

    # Register platforms (todo, sensor)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register LLM API for Assist & Conversation Agents
    entry.async_on_unload(async_register_llm_api(hass))

    # The skill only gets an open door in the modes that use it
    if store.voice_mode != VOICE_MODE_NATIVE:
        skill.async_start()
    entry.async_on_unload(skill.async_stop)

    reminders = ReminderManager(hass, store, {**entry.data, **entry.options})
    store.reminders = reminders
    await reminders.async_start()
    entry.async_on_unload(reminders.async_stop)

    todo_sync = TodoSyncManager(hass, store, {**entry.data, **entry.options})
    store.todo_sync = todo_sync
    await todo_sync.async_start()
    entry.async_on_unload(todo_sync.async_stop)

    battery = BatteryWatcher(hass, store, {**entry.data, **entry.options})
    await battery.async_start()
    entry.async_on_unload(battery.async_stop)

    attachment_cleaner = AttachmentCleaner(hass, store)
    attachment_cleaner.async_start()
    entry.async_on_unload(attachment_cleaner.async_stop)

    echo_locks = EchoLockManager(hass, {**entry.data, **entry.options})
    await echo_locks.async_start()
    entry.async_on_unload(echo_locks.async_stop)

    # Settings are checked on every setup, and changing them reloads the entry
    async_check_issues(hass, {**entry.data, **entry.options})

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: BrainstormConfigEntry) -> bool:
    """Unload a config entry."""
    entry.runtime_data.async_cancel_ai_tasks()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: BrainstormConfigEntry) -> None:
    """Clean up the repair issues when the integration is removed."""
    async_delete_issues(hass)


async def async_reload_entry(hass: HomeAssistant, entry: BrainstormConfigEntry) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)


def _require_store(hass: HomeAssistant) -> BrainstormStore:
    """Return the store, or explain that the action cannot run without it."""
    store = get_loaded_store(hass)
    if store is None:
        raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="not_loaded"
        )
    return store


def _check_idea_edit(store: BrainstormStore, idea_id: str, call: ServiceCall) -> None:
    """Refuse changes without the right to edit an idea."""
    idea = store.get_idea(idea_id)
    if idea is not None and not store.can_edit(idea, call.context.user_id):
        raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="no_access_idea", translation_placeholders={"id": idea_id}
        )


def _check_idea_owner(store: BrainstormStore, idea_id: str, call: ServiceCall) -> None:
    """Refuse what only the owner of an idea may do."""
    idea = store.get_idea(idea_id)
    if idea is not None and not store.is_owner(idea, call.context.user_id):
        raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="no_access_idea", translation_placeholders={"id": idea_id}
        )


async def _check_shared_setting_access(
    hass: HomeAssistant, store: BrainstormStore, call: ServiceCall
) -> None:
    """Only let admins change what affects the private ideas of others."""
    user_id = call.context.user_id
    if not store.privacy_enabled or user_id is None:
        return
    user = await hass.auth.async_get_user(user_id)
    if user is None or not user.is_admin:
        raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="admin_only"
        )


@callback
def _register_services(hass: HomeAssistant) -> None:
    """Register brainstorm services."""

    async def handle_add_idea(call: ServiceCall) -> dict[str, Any]:
        """Handle adding a new idea."""
        store = _require_store(hass)

        text = call.data[ATTR_TEXT]
        category = call.data.get(ATTR_CATEGORY)
        priority = call.data.get(ATTR_PRIORITY)
        # Without a source, someone typed the text into the action directly
        # (developer tools, a script, an AI agent), so its wording is kept
        source = call.data.get(ATTR_SOURCE)
        spoken = None if source else False
        if source is None:
            source = "manual"
        device = call.data.get(ATTR_DEVICE)
        tags = call.data.get(ATTR_TAGS)
        parent_id = call.data.get(ATTR_PARENT_ID)
        due = call.data.get(ATTR_DUE)
        if due is not None:
            due = dt_util.as_local(due)
        assignee = call.data.get(ATTR_ASSIGNEE)
        zone = call.data.get(ATTR_ZONE)
        language = call.data.get(ATTR_LANGUAGE)
        trigger = {"zone": zone, "person": assignee} if zone else None
        if due is None and call.data.get(ATTR_PARSE_DUE):
            request = build_reminder_request(
                hass, store.options, text, dt_util.now(), language
            )
            if request.text and (request.due or request.trigger):
                due, trigger, text = request.due, request.trigger, request.text
                assignee = request.assignee or assignee

        idea = await store.async_add_idea(
            text=text,
            category=category,
            priority=priority,
            source=source,
            device=device,
            tags=tags,
            parent_id=parent_id,
            context=call.context,
            due=due,
            assignee=assignee,
            trigger=trigger,
            owner=call.context.user_id or store.voice_user_for(device),
            language=language,
            spoken=spoken,
            description=call.data.get(ATTR_DESCRIPTION),
        )
        return {"success": True, "idea": idea}

    async def handle_update_idea(call: ServiceCall) -> dict[str, Any]:
        """Handle updating an existing idea."""
        store = _require_store(hass)

        idea_id = call.data[ATTR_ID]
        _check_idea_edit(store, idea_id, call)
        text = call.data.get(ATTR_TEXT)
        category = call.data.get(ATTR_CATEGORY)
        priority = call.data.get(ATTR_PRIORITY)
        status = call.data.get(ATTR_STATUS)
        device = call.data.get(ATTR_DEVICE)
        update_parent = ATTR_PARENT_ID in call.data
        parent_id = call.data.get(ATTR_PARENT_ID)
        order = call.data.get(ATTR_ORDER)

        updated = await store.async_update_idea(
            idea_id=idea_id,
            text=text,
            category=category,
            priority=priority,
            status=status,
            device=device,
            parent_id=parent_id,
            update_parent=update_parent,
            order=order,
            context=call.context,
            due=dt_util.as_local(call.data[ATTR_DUE]) if call.data.get(ATTR_DUE) else None,
            update_due=ATTR_DUE in call.data,
            result=call.data.get(ATTR_RESULT),
            update_result=ATTR_RESULT in call.data,
            description=call.data.get(ATTR_DESCRIPTION),
            update_description=ATTR_DESCRIPTION in call.data,
            in_progress=call.data.get(ATTR_IN_PROGRESS),
            shape=call.data.get(ATTR_SHAPE),
            update_shape=ATTR_SHAPE in call.data,
            markers=call.data.get(ATTR_MARKERS),
            update_markers=ATTR_MARKERS in call.data,
            progress=call.data.get(ATTR_PROGRESS),
            update_progress=ATTR_PROGRESS in call.data,
        )
        if updated is not None and (
            ATTR_ASSIGNEE in call.data
            or ATTR_ZONE in call.data
            or ATTR_ECHOS in call.data
        ):
            fields: dict[str, Any] = {}
            if ATTR_ECHOS in call.data:
                fields[ATTR_ECHOS] = call.data[ATTR_ECHOS] or None
            if ATTR_ASSIGNEE in call.data:
                fields[ATTR_ASSIGNEE] = call.data[ATTR_ASSIGNEE]
                state = hass.states.get(call.data[ATTR_ASSIGNEE] or "")
                if state is not None and state.attributes.get("user_id"):
                    await store.async_set_idea_shares(
                        [idea_id], {state.attributes["user_id"]: SHARE_EDIT}, None
                    )
            if ATTR_ZONE in call.data:
                person = fields.get(ATTR_ASSIGNEE, updated.get(ATTR_ASSIGNEE))
                zone = call.data[ATTR_ZONE]
                fields[ATTR_TRIGGER] = {"zone": zone, "person": person} if zone else None
                fields[ATTR_REMINDED_AT] = None
            await store.async_mark_fields(idea_id, fields)
        if updated is None:
            raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="idea_not_found", translation_placeholders={"id": idea_id}
        )
        return {"success": True, "idea": updated}

    async def handle_share(call: ServiceCall) -> dict[str, Any]:
        """Share several ideas or a whole category with people."""
        store = _require_store(hass)
        if not store.privacy_enabled:
            raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="sharing_needs_privacy"
        )
        idea_ids = call.data.get("ids")
        category = call.data.get(ATTR_CATEGORY)
        if bool(idea_ids) == bool(category):
            raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="share_target_missing"
        )
        shares = call.data["shares"]
        if category:
            owner = call.context.user_id or store.voice_user_id
            await store.async_set_category_shares(owner, category, shares)
            return {"success": True, "category": category}
        changed = await store.async_set_idea_shares(
            idea_ids, shares, call.context.user_id
        )
        if not changed:
            raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="no_idea_found"
        )
        return {"success": True, "changed": changed}

    async def handle_reorder_ideas(call: ServiceCall) -> dict[str, Any]:
        """Handle reordering ideas."""
        store = _require_store(hass)

        idea_ids = call.data.get("idea_ids", [])
        for idea_id in idea_ids:
            if store.get_idea(idea_id) is None:
                raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="idea_not_found", translation_placeholders={"id": idea_id}
        )
            _check_idea_edit(store, idea_id, call)
        success = await store.async_reorder_ideas(idea_ids)
        return {"success": success}

    async def handle_delete_idea(call: ServiceCall) -> dict[str, Any]:
        """Handle deleting an idea."""
        store = _require_store(hass)

        idea_id = call.data[ATTR_ID]
        _check_idea_owner(store, idea_id, call)
        if not await store.async_delete_idea(idea_id, context=call.context):
            raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="idea_not_found", translation_placeholders={"id": idea_id}
        )
        return {"success": True}

    async def handle_delete_done(call: ServiceCall) -> dict[str, Any]:
        """Delete ideas that are done, everything or those done long enough."""
        store = _require_store(hass)
        deleted = await store.async_delete_done(
            call.data["older_than_days"],
            user_id=call.context.user_id,
            context=call.context,
        )
        return {"deleted": deleted}

    async def handle_bring_message(call: ServiceCall) -> dict[str, Any]:
        """Tell the others on a Bring list, for example who goes shopping."""
        store = _require_store(hass)
        idea_id = call.data[ATTR_ID]
        idea = store.get_idea(idea_id)
        if idea is None or store.access_level(idea, call.context.user_id) is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="idea_not_found",
                translation_placeholders={"id": idea_id},
            )
        target = bring_message_target(hass, store, idea)
        if target is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="bring_not_linked"
            )
        entity_id, item = target
        message = call.data["message"]
        data: dict[str, Any] = {"message": message}
        if message == "urgent_message":
            if item is None:
                raise ServiceValidationError(
                    translation_domain=DOMAIN, translation_key="bring_urgent_needs_item"
                )
            data["item"] = item
        await hass.services.async_call(
            "bring",
            "send_message",
            data,
            target={"entity_id": entity_id},
            blocking=True,
            context=call.context,
        )
        return {"entity_id": entity_id, "message": message}

    async def handle_restore_idea(call: ServiceCall) -> dict[str, Any]:
        """Handle bringing back a deleted idea."""
        store = _require_store(hass)

        idea_id = call.data[ATTR_ID]
        idea = await store.async_restore_idea(idea_id, call.context.user_id)
        if idea is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="idea_not_restorable",
                translation_placeholders={"id": idea_id},
            )
        return {"success": True, "idea": idea}

    async def handle_get_ideas(call: ServiceCall) -> dict[str, Any]:
        """Handle fetching ideas."""
        store = _require_store(hass)

        category = call.data.get(ATTR_CATEGORY)
        priority = call.data.get(ATTR_PRIORITY)
        status_filter = call.data.get(ATTR_STATUS, "active")
        if status_filter == "all" or not status_filter:
            status_filter = None

        ideas = store.get_ideas_by_category(
            category=category,
            status=status_filter,
            priority=priority,
            user_id=call.context.user_id,
        )
        return {
            "count": len(ideas),
            "ideas": ideas,
            "categories": store.categories,
        }

    async def handle_add_category(call: ServiceCall) -> dict[str, Any]:
        """Handle adding a category."""
        store = _require_store(hass)

        name = call.data.get("name", "").strip()
        icon = call.data.get(ATTR_ICON)
        color = call.data.get(ATTR_COLOR)
        if not name:
            raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="category_name_empty"
        )
        success = await store.async_add_category(name, icon=icon, color=color)
        if not success:
            raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="category_exists", translation_placeholders={"name": name}
        )
        return {"success": success, "categories": store.categories}

    async def handle_set_category_style(call: ServiceCall) -> dict[str, Any]:
        """Handle setting custom icon and color for a category."""
        store = _require_store(hass)

        category = call.data.get(ATTR_CATEGORY, "").strip()
        icon = call.data.get(ATTR_ICON)
        color = call.data.get(ATTR_COLOR)
        reset = call.data.get(ATTR_RESET, False)

        if not category:
            raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="category_name_required"
        )

        success = await store.async_set_category_style(
            category,
            icon=icon,
            color=color,
            reset=reset,
        )
        return {
            "success": success,
            "category": category,
            "category_icons": store.category_icons,
            "category_colors": store.category_colors,
        }

    async def handle_remove_category(call: ServiceCall) -> dict[str, Any]:
        """Handle removing a category."""
        store = _require_store(hass)
        await _check_shared_setting_access(hass, store, call)

        name = call.data["name"]
        if not await store.async_remove_category(name):
            raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="category_not_removable", translation_placeholders={"name": name}
        )
        return {"success": True, "categories": store.categories}

    async def handle_export_markdown(call: ServiceCall) -> dict[str, Any]:
        """Handle exporting ideas to markdown files."""
        store = _require_store(hass)
        await _check_shared_setting_access(hass, store, call)

        path = call.data.get("path")
        try:
            await store.async_export_to_markdown(path)
        except OSError as err:
            raise HomeAssistantError(
            translation_domain=DOMAIN, translation_key="export_failed", translation_placeholders={"error": str(err)}
        ) from err
        return {"success": True}

    async def handle_export_json(call: ServiceCall) -> dict[str, Any]:
        """Return the ideas the caller may see as JSON, optionally into a file."""
        store = _require_store(hass)
        path = call.data.get("path")
        data = store.export_json(call.context.user_id, call.data.get(ATTR_CATEGORY))
        if not path:
            return data
        # A file can be read by everyone with access to the config folder
        await _check_shared_setting_access(hass, store, call)
        try:
            written = await store.async_write_json(path, data)
        except OSError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="json_write_failed",
                translation_placeholders={"error": str(err)},
            ) from err
        return {**data, "path": written}

    async def handle_import_json(call: ServiceCall) -> dict[str, Any]:
        """Add the ideas of a JSON export that are not here yet."""
        store = _require_store(hass)
        data = call.data.get("data")
        path = call.data.get("path")
        if (data is None) == (path is None):
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="json_source_missing"
            )
        user_id = call.context.user_id
        user = await hass.auth.async_get_user(user_id) if user_id else None
        is_admin = user_id is None or (user is not None and user.is_admin)
        if path is not None:
            await _check_shared_setting_access(hass, store, call)
            try:
                data = await store.async_read_json(path)
            except OSError as err:
                raise HomeAssistantError(
                    translation_domain=DOMAIN,
                    translation_key="import_failed",
                    translation_placeholders={"error": str(err)},
                ) from err
        known_users = {u.id for u in await hass.auth.async_get_users()}
        return await store.async_import_json(
            data, user_id, known_users, keep_owners=is_admin
        )

    async def handle_get_announcement(call: ServiceCall) -> dict[str, Any]:
        """Handle generating spoken announcement text."""
        store = _require_store(hass)

        category = call.data.get(ATTR_CATEGORY)
        # Automations have no user, and what they speak can be heard in the room
        user_id = call.context.user_id or store.voice_user_for(call.data.get(ATTR_DEVICE))
        speech_text = store.get_announcement_text(category=category, user_id=user_id)
        active_ideas = [
            i for i in store.visible_ideas(user_id) if i.get(ATTR_STATUS) == "active"
        ]
        if category and str(category).strip().lower() not in ["all", "alle"]:
            active_ideas = [
                i
                for i in active_ideas
                if (i.get(ATTR_CATEGORY) or "").lower() == str(category).strip().lower()
            ]
        return {
            "speech": speech_text,
            "count": len(active_ideas),
            "category": category,
        }

    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_ANNOUNCEMENT,
        handle_get_announcement,
        schema=SERVICE_GET_ANNOUNCEMENT_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SHARE,
        handle_share,
        schema=SERVICE_SHARE_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_IDEA,
        handle_add_idea,
        schema=SERVICE_ADD_IDEA_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_IDEA,
        handle_update_idea,
        schema=SERVICE_UPDATE_IDEA_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_DELETE_IDEA,
        handle_delete_idea,
        schema=SERVICE_DELETE_IDEA_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_DELETE_DONE,
        handle_delete_done,
        schema=SERVICE_DELETE_DONE_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_RESTORE_IDEA,
        handle_restore_idea,
        schema=SERVICE_DELETE_IDEA_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_IDEAS,
        handle_get_ideas,
        schema=SERVICE_GET_IDEAS_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_CATEGORY,
        handle_add_category,
        schema=SERVICE_ADD_CATEGORY_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_CATEGORY_STYLE,
        handle_set_category_style,
        schema=SERVICE_SET_CATEGORY_STYLE_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_REMOVE_CATEGORY,
        handle_remove_category,
        schema=SERVICE_REMOVE_CATEGORY_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_BRING_MESSAGE,
        handle_bring_message,
        schema=SERVICE_BRING_MESSAGE_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_REORDER_IDEAS,
        handle_reorder_ideas,
        schema=SERVICE_REORDER_IDEAS_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_EXPORT_JSON,
        handle_export_json,
        schema=SERVICE_EXPORT_JSON_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_IMPORT_JSON,
        handle_import_json,
        schema=SERVICE_IMPORT_JSON_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_EXPORT_MARKDOWN,
        handle_export_markdown,
        schema=SERVICE_EXPORT_MARKDOWN_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

