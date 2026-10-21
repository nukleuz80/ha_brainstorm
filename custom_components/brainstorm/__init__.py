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
    ATTR_ID,
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

SERVICE_ADD_IDEA_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TEXT): cv.string,
        vol.Optional(ATTR_CATEGORY): vol.Any(None, cv.string),
        vol.Optional(ATTR_SOURCE, default="manual"): cv.string,
        vol.Optional(ATTR_TAGS): vol.All(cv.ensure_list, [cv.string]),
    }
)

SERVICE_UPDATE_IDEA_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ID): cv.string,
        vol.Optional(ATTR_TEXT): cv.string,
        vol.Optional(ATTR_CATEGORY): cv.string,
        vol.Optional(ATTR_STATUS): vol.In(["active", "completed", "archived"]),
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


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Brainstorm Hub from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    store = BrainstormStore(hass, entry.options or entry.data)
    await store.async_load()

    hass.data[DOMAIN][entry.entry_id] = store
    hass.data[DOMAIN]["primary_store"] = store

    # Register platforms (todo, sensor)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    _register_services(hass)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)


def _get_active_store(hass: HomeAssistant) -> BrainstormStore | None:
    """Get the active store instance."""
    data = hass.data.get(DOMAIN, {})
    return data.get("primary_store")


@callback
def _register_services(hass: HomeAssistant) -> None:
    """Register brainstorm services."""

    async def handle_add_idea(call: ServiceCall) -> dict[str, Any]:
        """Handle adding a new idea."""
        store = _get_active_store(hass)
        if not store:
            raise ValueError("Brainstorm store is not initialized")

        text = call.data[ATTR_TEXT]
        category = call.data.get(ATTR_CATEGORY)
        source = call.data.get(ATTR_SOURCE, "manual")
        tags = call.data.get(ATTR_TAGS)

        idea = await store.async_add_idea(
            text=text,
            category=category,
            source=source,
            tags=tags,
        )
        return {"success": True, "idea": idea}

    async def handle_update_idea(call: ServiceCall) -> dict[str, Any]:
        """Handle updating an existing idea."""
        store = _get_active_store(hass)
        if not store:
            raise ValueError("Brainstorm store is not initialized")

        idea_id = call.data[ATTR_ID]
        text = call.data.get(ATTR_TEXT)
        category = call.data.get(ATTR_CATEGORY)
        status = call.data.get(ATTR_STATUS)

        updated = await store.async_update_idea(
            idea_id=idea_id,
            text=text,
            category=category,
            status=status,
        )
        return {"success": updated is not None, "idea": updated}

    async def handle_delete_idea(call: ServiceCall) -> dict[str, Any]:
        """Handle deleting an idea."""
        store = _get_active_store(hass)
        if not store:
            raise ValueError("Brainstorm store is not initialized")

        idea_id = call.data[ATTR_ID]
        deleted = await store.async_delete_idea(idea_id)
        return {"success": deleted}

    async def handle_get_ideas(call: ServiceCall) -> dict[str, Any]:
        """Handle fetching ideas."""
        store = _get_active_store(hass)
        if not store:
            raise ValueError("Brainstorm store is not initialized")

        category = call.data.get(ATTR_CATEGORY)
        status_filter = call.data.get(ATTR_STATUS, "active")
        if status_filter == "all" or not status_filter:
            status_filter = None

        ideas = store.get_ideas_by_category(category=category, status=status_filter)
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
            raise ValueError("Brainstorm store is not initialized")

        name = call.data["name"]
        success = await store.async_remove_category(name)
        return {"success": success, "categories": store.categories}

    async def handle_export_markdown(call: ServiceCall) -> dict[str, Any]:
        """Handle exporting ideas to markdown files."""
        store = _get_active_store(hass)
        if not store:
            raise ValueError("Brainstorm store is not initialized")

        path = call.data.get("path")
        await store.async_export_to_markdown(path)
        return {"success": True}

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

