"""Brainstorm Hub custom component for Home Assistant."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse, callback
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.loader import async_get_integration
from homeassistant.util import dt as dt_util

from .alexa_skill import AlexaSkill
from .const import (
    ATTR_CATEGORY,
    ATTR_COLOR,
    ATTR_ASSIGNEE,
    ATTR_DEVICE,
    ATTR_DUE,
    ATTR_ICON,
    ATTR_ID,
    ATTR_ORDER,
    ATTR_PARENT_ID,
    ATTR_PARSE_DUE,
    ATTR_PRIORITY,
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
    SERVICE_REORDER_IDEAS,
    SERVICE_SET_CATEGORY_STYLE,
    SHARE_EDIT,
    SHARE_VIEW,
    VOICE_MODE_NATIVE,
)
from .llm import async_register_llm_api
from .reminders import ReminderManager, build_reminder_request
from .store import BrainstormStore
from .websocket import async_register_commands

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

SERVICE_ADD_IDEA = "add_idea"
SERVICE_UPDATE_IDEA = "update_idea"
SERVICE_DELETE_IDEA = "delete_idea"
SERVICE_GET_IDEAS = "get_ideas"
SERVICE_SHARE = "share"
SERVICE_ADD_CATEGORY = "add_category"
SERVICE_REMOVE_CATEGORY = "remove_category"
SERVICE_EXPORT_MARKDOWN = "export_markdown"
SERVICE_GET_ANNOUNCEMENT = "get_announcement"

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
        vol.Optional(ATTR_SOURCE, default="manual"): cv.string,
        vol.Optional(ATTR_DEVICE): vol.Any(None, cv.string),
        vol.Optional(ATTR_TAGS): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(ATTR_PARENT_ID): vol.Any(None, cv.string),
        vol.Optional(ATTR_DUE): vol.Any(None, cv.datetime),
        vol.Optional(ATTR_PARSE_DUE): cv.boolean,
        vol.Optional(ATTR_ASSIGNEE): vol.Any(None, cv.entity_id),
        vol.Optional(ATTR_ZONE): vol.Any(None, cv.entity_id),
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
    hass.data.setdefault(DOMAIN, {})

    _register_services(hass)
    async_register_commands(hass)
    return True


type BrainstormConfigEntry = ConfigEntry[BrainstormStore]


async def async_setup_entry(hass: HomeAssistant, entry: BrainstormConfigEntry) -> bool:
    """Set up Brainstorm Hub from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    store = BrainstormStore(hass, {**entry.data, **entry.options})
    integration = await async_get_integration(hass, DOMAIN)
    store.integration_version = str(integration.version)
    await store.async_load()

    entry.runtime_data = store
    hass.data[DOMAIN][entry.entry_id] = store
    hass.data[DOMAIN]["primary_store"] = store

    # Register platforms (todo, sensor)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register LLM API for Assist & Conversation Agents
    entry.async_on_unload(async_register_llm_api(hass))

    # The skill only gets an open door in the modes that use it
    skill = AlexaSkill(hass, store)
    await skill.async_load()
    store.alexa_skill = skill
    if store.voice_mode != VOICE_MODE_NATIVE:
        skill.async_start()
    entry.async_on_unload(skill.async_stop)

    reminders = ReminderManager(hass, store, {**entry.data, **entry.options})
    store.reminders = reminders
    await reminders.async_start()
    entry.async_on_unload(reminders.async_stop)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: BrainstormConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        if not hass.config_entries.async_loaded_entries(DOMAIN):
            hass.data[DOMAIN].pop("primary_store", None)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: BrainstormConfigEntry) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)


def _get_active_store(hass: HomeAssistant) -> BrainstormStore | None:
    """Get the active store instance."""
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if entries:
        return entries[0].runtime_data
    data = hass.data.get(DOMAIN, {})
    return data.get("primary_store")


def _check_idea_edit(store: BrainstormStore, idea_id: str, call: ServiceCall) -> None:
    """Refuse changes without the right to edit an idea."""
    idea = store.get_idea(idea_id)
    if idea is not None and not store.can_edit(idea, call.context.user_id):
        raise ServiceValidationError(f"Kein Zugriff auf Idee '{idea_id}'.")


def _check_idea_owner(store: BrainstormStore, idea_id: str, call: ServiceCall) -> None:
    """Refuse what only the owner of an idea may do."""
    idea = store.get_idea(idea_id)
    if idea is not None and not store.is_owner(idea, call.context.user_id):
        raise ServiceValidationError(f"Kein Zugriff auf Idee '{idea_id}'.")


async def _check_shared_setting_access(
    hass: HomeAssistant, store: BrainstormStore, call: ServiceCall
) -> None:
    """Only let admins change what affects the private ideas of others."""
    user_id = call.context.user_id
    if not store.privacy_enabled or user_id is None:
        return
    user = await hass.auth.async_get_user(user_id)
    if user is None or not user.is_admin:
        raise ServiceValidationError("Nur Administratoren dürfen das ausführen.")


@callback
def _register_services(hass: HomeAssistant) -> None:
    """Register brainstorm services."""

    async def handle_add_idea(call: ServiceCall) -> dict[str, Any]:
        """Handle adding a new idea."""
        store = _get_active_store(hass)
        if not store:
            raise HomeAssistantError("Brainstorm store is not initialized")

        text = call.data[ATTR_TEXT]
        category = call.data.get(ATTR_CATEGORY)
        priority = call.data.get(ATTR_PRIORITY)
        source = call.data.get(ATTR_SOURCE, "manual")
        device = call.data.get(ATTR_DEVICE)
        tags = call.data.get(ATTR_TAGS)
        parent_id = call.data.get(ATTR_PARENT_ID)
        due = call.data.get(ATTR_DUE)
        if due is not None:
            due = dt_util.as_local(due)
        assignee = call.data.get(ATTR_ASSIGNEE)
        zone = call.data.get(ATTR_ZONE)
        trigger = {"zone": zone, "person": assignee} if zone else None
        if due is None and call.data.get(ATTR_PARSE_DUE):
            request = build_reminder_request(hass, store.options, text, dt_util.now())
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
        )
        return {"success": True, "idea": idea}

    async def handle_update_idea(call: ServiceCall) -> dict[str, Any]:
        """Handle updating an existing idea."""
        store = _get_active_store(hass)
        if not store:
            raise HomeAssistantError("Brainstorm store is not initialized")

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
        )
        if updated is not None and (
            ATTR_ASSIGNEE in call.data or ATTR_ZONE in call.data
        ):
            fields: dict[str, Any] = {}
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
            raise ServiceValidationError(f"Idee '{idea_id}' wurde nicht gefunden.")
        return {"success": True, "idea": updated}

    async def handle_share(call: ServiceCall) -> dict[str, Any]:
        """Share several ideas or a whole category with people."""
        store = _get_active_store(hass)
        if not store:
            raise HomeAssistantError("Brainstorm store is not initialized")
        if not store.privacy_enabled:
            raise ServiceValidationError(
                "Freigaben gibt es nur mit eingeschalteter Privatsphäre."
            )
        idea_ids = call.data.get("ids")
        category = call.data.get(ATTR_CATEGORY)
        if bool(idea_ids) == bool(category):
            raise ServiceValidationError("Bitte Einträge oder eine Kategorie angeben.")
        shares = call.data["shares"]
        if category:
            owner = call.context.user_id or store.voice_user_id
            await store.async_set_category_shares(owner, category, shares)
            return {"success": True, "category": category}
        changed = await store.async_set_idea_shares(
            idea_ids, shares, call.context.user_id
        )
        return {"success": True, "changed": changed}

    async def handle_reorder_ideas(call: ServiceCall) -> dict[str, Any]:
        """Handle reordering ideas."""
        store = _get_active_store(hass)
        if not store:
            raise HomeAssistantError("Brainstorm store is not initialized")

        idea_ids = call.data.get("idea_ids", [])
        for idea_id in idea_ids:
            _check_idea_edit(store, idea_id, call)
        success = await store.async_reorder_ideas(idea_ids)
        return {"success": success}

    async def handle_delete_idea(call: ServiceCall) -> dict[str, Any]:
        """Handle deleting an idea."""
        store = _get_active_store(hass)
        if not store:
            raise HomeAssistantError("Brainstorm store is not initialized")

        idea_id = call.data[ATTR_ID]
        _check_idea_owner(store, idea_id, call)
        if not await store.async_delete_idea(idea_id, context=call.context):
            raise ServiceValidationError(f"Idee '{idea_id}' wurde nicht gefunden.")
        return {"success": True}

    async def handle_get_ideas(call: ServiceCall) -> dict[str, Any]:
        """Handle fetching ideas."""
        store = _get_active_store(hass)
        if not store:
            raise HomeAssistantError("Brainstorm store is not initialized")

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
        store = _get_active_store(hass)
        if not store:
            raise ServiceValidationError("Brainstorm store is not initialized")

        name = call.data.get("name", "").strip()
        icon = call.data.get(ATTR_ICON)
        color = call.data.get(ATTR_COLOR)
        if not name:
            raise ServiceValidationError("Der Kategoriename darf nicht leer sein.")
        success = await store.async_add_category(name, icon=icon, color=color)
        if not success:
            raise ServiceValidationError(f"Die Kategorie '{name}' existiert bereits.")
        return {"success": success, "categories": store.categories}

    async def handle_set_category_style(call: ServiceCall) -> dict[str, Any]:
        """Handle setting custom icon and color for a category."""
        store = _get_active_store(hass)
        if not store:
            raise ServiceValidationError("Brainstorm store is not initialized")

        category = call.data.get(ATTR_CATEGORY, "").strip()
        icon = call.data.get(ATTR_ICON)
        color = call.data.get(ATTR_COLOR)
        reset = call.data.get(ATTR_RESET, False)

        if not category:
            raise ServiceValidationError("Kategoriename ist erforderlich.")

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
        store = _get_active_store(hass)
        if not store:
            raise HomeAssistantError("Brainstorm store is not initialized")
        await _check_shared_setting_access(hass, store, call)

        name = call.data["name"]
        success = await store.async_remove_category(name)
        return {"success": success, "categories": store.categories}

    async def handle_export_markdown(call: ServiceCall) -> dict[str, Any]:
        """Handle exporting ideas to markdown files."""
        store = _get_active_store(hass)
        if not store:
            raise HomeAssistantError("Brainstorm store is not initialized")
        await _check_shared_setting_access(hass, store, call)

        path = call.data.get("path")
        await store.async_export_to_markdown(path)
        return {"success": True}

    async def handle_get_announcement(call: ServiceCall) -> dict[str, Any]:
        """Handle generating spoken announcement text."""
        store = _get_active_store(hass)
        if not store:
            raise ServiceValidationError("Brainstorm store is not initialized")

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
        SERVICE_REORDER_IDEAS,
        handle_reorder_ideas,
        schema=SERVICE_REORDER_IDEAS_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_EXPORT_MARKDOWN,
        handle_export_markdown,
        schema=SERVICE_EXPORT_MARKDOWN_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

