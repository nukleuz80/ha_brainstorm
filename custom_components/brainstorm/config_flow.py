"""Config flow for Brainstorm Hub integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_AUTO_EXPORT_MARKDOWN,
    CONF_MARKDOWN_PATH,
    CONF_SMART_FORMATTING,
    DEFAULT_MARKDOWN_PATH,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class BrainstormConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Brainstorm Hub."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title="Brainstorm Hub", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Optional(CONF_AUTO_EXPORT_MARKDOWN, default=False): bool,
                vol.Optional(CONF_MARKDOWN_PATH, default=DEFAULT_MARKDOWN_PATH): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return BrainstormOptionsFlowHandler()


class BrainstormOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Brainstorm Hub."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show options menu."""
        return self.async_show_menu(
            step_id="init",
            menu_options=["categories", "general"],
        )

    async def async_step_categories(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage categories."""
        store = self.hass.data.get(DOMAIN, {}).get("primary_store")
        current_cats = (
            store.categories
            if store and store.categories
            else ["Inbox", "Smarthome", "Haus & Garten", "Projekte", "Alltag"]
        )

        if user_input is not None:
            if store:
                # 1. Process delete
                cat_to_del = user_input.get("delete_category")
                if cat_to_del and cat_to_del != "none":
                    await store.async_remove_category(cat_to_del)

                # 2. Process add
                cat_to_add = user_input.get("add_category")
                if cat_to_add and cat_to_add.strip():
                    await store.async_add_category(cat_to_add.strip())

                # 3. Process manual comma list edit (if changed)
                edited_list = user_input.get("edit_categories")
                if edited_list:
                    parsed = [c.strip() for c in edited_list.split(",") if c.strip()]
                    if parsed and parsed != store.categories:
                        await store.async_set_categories(parsed)

            return self.async_create_entry(title="", data={})

        delete_options = [{"value": "none", "label": "Keine löschen"}]
        for c in current_cats:
            if c != "Inbox":
                delete_options.append({"value": c, "label": f"{c} löschen"})

        data_schema = vol.Schema(
            {
                vol.Optional("add_category"): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT,
                        autocomplete="off",
                    )
                ),
                vol.Optional("delete_category", default="none"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=delete_options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(
                    "edit_categories",
                    default=", ".join(current_cats),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="categories",
            data_schema=data_schema,
            description_placeholders={"current_cats": ", ".join(current_cats)},
        )

    async def async_step_general(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage general settings and export."""
        options = dict(self.config_entry.options or self.config_entry.data)
        store = self.hass.data.get(DOMAIN, {}).get("primary_store")
        current_cats = (
            store.categories
            if store and store.categories
            else ["Inbox", "Smarthome", "Haus & Garten", "Projekte", "Alltag"]
        )

        if user_input is not None:
            options.update(user_input)
            return self.async_create_entry(title="", data=options)

        cat_options = [{"value": c, "label": c} for c in current_cats]

        data_schema = vol.Schema(
            {
                vol.Optional(
                    "default_category",
                    default=options.get("default_category", "Inbox"),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=cat_options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(
                    CONF_SMART_FORMATTING,
                    default=options.get(CONF_SMART_FORMATTING, True),
                ): selector.BooleanSelector(),
                vol.Optional(
                    CONF_AUTO_EXPORT_MARKDOWN,
                    default=options.get(CONF_AUTO_EXPORT_MARKDOWN, False),
                ): selector.BooleanSelector(),
                vol.Optional(
                    CONF_MARKDOWN_PATH,
                    default=options.get(CONF_MARKDOWN_PATH, DEFAULT_MARKDOWN_PATH),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="general",
            data_schema=data_schema,
        )

