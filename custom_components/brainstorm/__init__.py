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

from .const import (
    ATTR_CATEGORY,
    ATTR_DEVICE,
    ATTR_ID,
    ATTR_PARENT_ID,
    ATTR_PRIORITY,
    ATTR_SOURCE,
    ATTR_STATUS,
    ATTR_TAGS,
    ATTR_TEXT,
    DOMAIN,
    PLATFORMS,
)
from .store import BrainstormStore

_LOGGER = logging.getLogger(__name__)

SERVICE_ADD_IDEA = "add_idea"
SERVICE_UPDATE_IDEA = "update_idea"
SERVICE_DELETE_IDEA = "delete_idea"
SERVICE_GET_IDEAS = "get_ideas"
SERVICE_ADD_CATEGORY = "add_category"
SERVICE_REMOVE_CATEGORY = "remove_category"
SERVICE_EXPORT_MARKDOWN = "export_markdown"
SERVICE_GET_ANNOUNCEMENT = "get_announcement"

SERVICE_GET_ANNOUNCEMENT_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_CATEGORY): vol.Any(None, cv.string),
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
    },
    extra=vol.ALLOW_EXTRA,
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
    """Set up the Brainstorm component from configuration.yaml (optional)."""
    hass.data.setdefault(DOMAIN, {})

    # If domain in configuration.yaml, auto-create a config entry if none exists
    if DOMAIN in config and not hass.config_entries.async_entries(DOMAIN):
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": "import"},
                data={},
            )
        )

    return True


type BrainstormConfigEntry = ConfigEntry[BrainstormStore]


async def async_setup_entry(hass: HomeAssistant, entry: BrainstormConfigEntry) -> bool:
    """Set up Brainstorm Hub from a config entry."""
    import importlib
    import sys
    for mod in ["const", "config_flow", "nlp", "store", "sensor", "todo", "llm", "logbook"]:
        full_name = f"custom_components.brainstorm.{mod}"
        if full_name in sys.modules:
            try:
                importlib.reload(sys.modules[full_name])
                if mod == "config_flow":
                    from homeassistant import config_entries
                    if hasattr(sys.modules[full_name], "BrainstormConfigFlow"):
                        config_entries.HANDLERS[DOMAIN] = sys.modules[full_name].BrainstormConfigFlow
            except Exception as err:
                _LOGGER.debug("Could not live-reload %s: %s", full_name, err)

    from .store import BrainstormStore

    hass.data.setdefault(DOMAIN, {})

    store = BrainstormStore(hass, entry.options or entry.data)
    await store.async_load()

    entry.runtime_data = store
    hass.data[DOMAIN][entry.entry_id] = store
    hass.data[DOMAIN]["primary_store"] = store

    # Register platforms (todo, sensor)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    _register_services(hass)

    # Register LLM API for Assist & Conversation Agents
    try:
        from .llm import async_register_llm_api
        unregister_llm = async_register_llm_api(hass)
        entry.async_on_unload(unregister_llm)
    except Exception as err:
        _LOGGER.warning("Could not register Brainstorm LLM API: %s", err)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: BrainstormConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        if not hass.config_entries.async_loaded_entries(DOMAIN):
            hass.data[DOMAIN].pop("primary_store", None)
            for service in [
                SERVICE_ADD_IDEA,
                SERVICE_UPDATE_IDEA,
                SERVICE_DELETE_IDEA,
                SERVICE_GET_IDEAS,
                SERVICE_ADD_CATEGORY,
                SERVICE_REMOVE_CATEGORY,
                SERVICE_EXPORT_MARKDOWN,
                SERVICE_GET_ANNOUNCEMENT,
            ]:
                hass.services.async_remove(DOMAIN, service)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: BrainstormConfigEntry) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)


def _get_active_store(hass: HomeAssistant) -> BrainstormStore | None:
    """Get the active store instance."""
    entries = hass.config_entries.async_entries(DOMAIN)
    if entries and hasattr(entries[0], "runtime_data") and entries[0].runtime_data is not None:
        return entries[0].runtime_data
    data = hass.data.get(DOMAIN, {})
    return data.get("primary_store")


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

        idea = await store.async_add_idea(
            text=text,
            category=category,
            priority=priority,
            source=source,
            device=device,
            tags=tags,
            parent_id=parent_id,
        )
        return {"success": True, "idea": idea}

    async def handle_update_idea(call: ServiceCall) -> dict[str, Any]:
        """Handle updating an existing idea."""
        store = _get_active_store(hass)
        if not store:
            raise HomeAssistantError("Brainstorm store is not initialized")

        idea_id = call.data[ATTR_ID]
        text = call.data.get(ATTR_TEXT)
        category = call.data.get(ATTR_CATEGORY)
        priority = call.data.get(ATTR_PRIORITY)
        status = call.data.get(ATTR_STATUS)
        device = call.data.get(ATTR_DEVICE)
        update_parent = ATTR_PARENT_ID in call.data
        parent_id = call.data.get(ATTR_PARENT_ID)

        updated = await store.async_update_idea(
            idea_id=idea_id,
            text=text,
            category=category,
            priority=priority,
            status=status,
            device=device,
            parent_id=parent_id,
            update_parent=update_parent,
        )
        return {"success": updated is not None, "idea": updated}

    async def handle_delete_idea(call: ServiceCall) -> dict[str, Any]:
        """Handle deleting an idea."""
        store = _get_active_store(hass)
        if not store:
            raise HomeAssistantError("Brainstorm store is not initialized")

        idea_id = call.data[ATTR_ID]
        deleted = await store.async_delete_idea(idea_id)
        return {"success": deleted}

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
            category=category, status=status_filter, priority=priority
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
        if not name:
            raise ServiceValidationError("Der Kategoriename darf nicht leer sein.")
        success = await store.async_add_category(name)
        if not success:
            raise ServiceValidationError(f"Die Kategorie '{name}' existiert bereits.")
        return {"success": success, "categories": store.categories}

    async def handle_remove_category(call: ServiceCall) -> dict[str, Any]:
        """Handle removing a category."""
        store = _get_active_store(hass)
        if not store:
            raise HomeAssistantError("Brainstorm store is not initialized")

        name = call.data["name"]
        success = await store.async_remove_category(name)
        return {"success": success, "categories": store.categories}

    async def handle_export_markdown(call: ServiceCall) -> dict[str, Any]:
        """Handle exporting ideas to markdown files."""
        store = _get_active_store(hass)
        if not store:
            raise HomeAssistantError("Brainstorm store is not initialized")

        path = call.data.get("path")
        await store.async_export_to_markdown(path)
        return {"success": True}

    async def handle_get_announcement(call: ServiceCall) -> dict[str, Any]:
        """Handle generating spoken announcement text."""
        store = _get_active_store(hass)
        if not store:
            raise ServiceValidationError("Brainstorm store is not initialized")

        category = call.data.get(ATTR_CATEGORY)
        speech_text = store.get_announcement_text(category=category)
        active_ideas = [i for i in store.ideas if i.get(ATTR_STATUS) == "active"]
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
        SERVICE_REMOVE_CATEGORY,
        handle_remove_category,
        schema=SERVICE_REMOVE_CATEGORY_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_EXPORT_MARKDOWN,
        handle_export_markdown,
        schema=SERVICE_EXPORT_MARKDOWN_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

