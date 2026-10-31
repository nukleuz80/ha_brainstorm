"""Config flow for Brainstorm Hub integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.network import NoURLAvailableError

from .const import (
    CONF_AI_ENABLED,
    CONF_AI_ENTITY,
    CONF_ALLOWED_ECHOS,
    CONF_ARRIVAL_ENABLED,
    CONF_AUTO_EXPORT_MARKDOWN,
    CONF_CALENDAR_ENABLED,
    CONF_CALENDAR_ENTITY,
    CONF_DEFAULT_PERSON,
    CONF_DIGEST_ENABLED,
    CONF_DIGEST_PRESENCE,
    CONF_DIGEST_TIME,
    CONF_LIST_RULES,
    CONF_LIST_RULES_ENABLED,
    CONF_NATIVE_REMINDERS,
    CONF_NOTIFY_ENABLED,
    CONF_PERSON_RULES,
    CONF_PERSONS_ENABLED,
    CONF_PLACES_ENABLED,
    CONF_QUIET_ENABLED,
    CONF_QUIET_END,
    CONF_QUIET_START,
    CONF_REMINDER_ALEXA,
    CONF_REMINDER_DELAY,
    CONF_REMINDER_ECHOS,
    CONF_REMINDER_NOTIFY,
    CONF_REMINDERS_ENABLED,
    CONF_URGENT_DELAY,
    CONF_URGENT_ENABLED,
    CONF_URGENT_NOTIFY,
    CONF_REVIEW_DAYS,
    CONF_REVIEW_ENABLED,
    CONF_REVIEW_TIME,
    CONF_REVIEW_WEEKDAY,
    CONF_HIDE_EMPTY_CATEGORIES,
    CONF_MARKDOWN_PATH,
    CONF_SMART_FORMATTING,
    CONF_VOICE_MODE,
    DEFAULT_HIDE_EMPTY_CATEGORIES,
    DEFAULT_MARKDOWN_PATH,
    DEFAULT_REVIEW_DAYS,
    DEFAULT_URGENT_DELAY,
    DOMAIN,
    REMINDER_ALEXA_MODES,
    REMINDER_ALEXA_OFF,
    RULE_CHANNEL,
    RULE_CHANNEL_DEFAULT,
    RULE_CHANNELS,
    RULE_NOTIFY,
    RULE_SCHEDULE_ENABLED,
    RULE_SCHEDULE_TIME,
    RULE_SCHEDULE_WEEKDAYS,
    RULE_ZONE,
    RULE_ZONE_ENABLED,
    VOICE_MODE_NATIVE,
    VOICE_MODES,
)


def _suggested(options: dict[str, Any], key: str) -> dict[str, Any]:
    """Show a stored value in an optional field, which may be cleared."""
    return {"suggested_value": options.get(key)}


def _echo_field(multiple: bool) -> selector.EntitySelector:
    """Return a field to pick Echos."""
    return selector.EntitySelector(
        selector.EntitySelectorConfig(
            domain="media_player", integration="alexa_media", multiple=multiple
        )
    )


def _weekday_field(multiple: bool) -> selector.SelectSelector:
    """Return a field to pick days of the week."""
    return selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=[str(day) for day in range(7)],
            multiple=multiple,
            mode=selector.SelectSelectorMode.DROPDOWN,
            translation_key=CONF_REVIEW_WEEKDAY,
        )
    )


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
                vol.Optional(
                    CONF_HIDE_EMPTY_CATEGORIES, default=DEFAULT_HIDE_EMPTY_CATEGORIES
                ): bool,
                vol.Optional(CONF_AUTO_EXPORT_MARKDOWN, default=False): bool,
                vol.Optional(CONF_MARKDOWN_PATH, default=DEFAULT_MARKDOWN_PATH): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle reconfiguring the existing entry."""
        config_entry = self._get_reconfigure_entry()
        current_data = {**config_entry.data, **config_entry.options}

        if user_input is not None:
            # Options take precedence over data, so update both. The update listener
            # reloads the entry if something changed.
            self.hass.config_entries.async_update_entry(
                config_entry,
                data={**config_entry.data, **user_input},
                options={**config_entry.options, **user_input},
            )
            return self.async_abort(reason="reconfigure_successful")

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_HIDE_EMPTY_CATEGORIES,
                    default=current_data.get(
                        CONF_HIDE_EMPTY_CATEGORIES, DEFAULT_HIDE_EMPTY_CATEGORIES
                    ),
                ): bool,
                vol.Optional(
                    CONF_SMART_FORMATTING,
                    default=current_data.get(CONF_SMART_FORMATTING, True),
                ): bool,
                vol.Optional(
                    CONF_AUTO_EXPORT_MARKDOWN,
                    default=current_data.get(CONF_AUTO_EXPORT_MARKDOWN, False),
                ): bool,
                vol.Optional(
                    CONF_MARKDOWN_PATH,
                    default=current_data.get(CONF_MARKDOWN_PATH, DEFAULT_MARKDOWN_PATH),
                ): str,
            }
        )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=data_schema,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return BrainstormOptionsFlowHandler()


class BrainstormOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Brainstorm Hub."""

    def __init__(self) -> None:
        """Initialize options flow."""
        self._selected_style_cat: str = "Inbox"
        self._shown_categories: str = ""
        self._voice_mode: str = VOICE_MODE_NATIVE
        self._rule_enabled: bool = False
        self._rule_category: str = ""
        self._rule_person: str = ""

    def _get_localized_menu(self, step_id: str) -> dict[str, str]:
        """Return explicit localized menu options mapping to bypass frontend cache staleness."""
        is_de = getattr(self.hass.config, "language", "en").startswith("de")
        menus_de = {
            "init": {
                "categories": "Kategorien verwalten",
                "category_style": "Kategorie-Design (Farbe & Icon)",
                "general": "Allgemeine Einstellungen & Export",
                "alexa_skill": "Alexa-Spracheingabe & Skill",
                "reminders": "Erinnerungen & Benachrichtigungen",
            },
            "reminders": {
                "reminder_general": "Ein/Aus & Kanäle",
                "reminder_schedule": "Ruhezeit, Briefing & Wochenrückblick",
                "reminder_lists": "Regeln pro Liste",
                "reminder_places": "Orte & Heimkommen",
                "reminder_persons": "Personen",
                "reminder_extras": "Kalender, KI & Alexa-Erinnerungen",
            },
            "category_style_done": {
                "category_style": "Weitere Kategorie anpassen",
                "init": "Zurück zum Hauptmenü",
                "close": "Fertig & Schließen",
            },
        }
        menus_en = {
            "init": {
                "categories": "Manage Categories",
                "category_style": "Category Design (Color & Icon)",
                "general": "General Settings & Export",
                "alexa_skill": "Alexa Voice Input & Skill",
                "reminders": "Reminders & Notifications",
            },
            "reminders": {
                "reminder_general": "On/Off & Channels",
                "reminder_schedule": "Quiet Hours, Briefing & Weekly Review",
                "reminder_lists": "Rules per List",
                "reminder_places": "Places & Coming Home",
                "reminder_persons": "People",
                "reminder_extras": "Calendar, AI & Alexa Reminders",
            },
            "category_style_done": {
                "category_style": "Customize another category",
                "init": "Back to main menu",
                "close": "Done & Close",
            },
        }
        return (menus_de if is_de else menus_en).get(step_id, {})

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show options menu."""
        return self.async_show_menu(
            step_id="init",
            menu_options=self._get_localized_menu("init"),
        )

    async def async_step_category_style(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Select a category to customize its icon and color."""
        store = self.hass.data.get(DOMAIN, {}).get("primary_store")
        current_cats = (
            store.categories
            if store and store.categories
            else ["Inbox", "Smarthome", "Haus & Garten", "Projekte", "Alltag"]
        )

        if user_input is not None:
            self._selected_style_cat = user_input.get("category", current_cats[0])
            return await self.async_step_category_style_edit()

        current_icons = store.category_icons if store else {}
        current_colors = store.category_colors if store else {}

        cat_options = []
        for c in current_cats:
            details = []
            if c in current_icons and current_icons[c]:
                details.append(f"Icon: {current_icons[c]}")
            if c in current_colors and current_colors[c]:
                details.append(f"Farbe: {current_colors[c]}")
            label = f"{c} ({', '.join(details)})" if details else f"{c} (Standard)"
            cat_options.append({"value": c, "label": label})

        data_schema = vol.Schema(
            {
                vol.Required("category", default=current_cats[0]): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=cat_options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )
        return self.async_show_form(
            step_id="category_style",
            data_schema=data_schema,
            last_step=False,
        )

    async def async_step_category_style_edit(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Edit icon and color for the selected category."""
        store = self.hass.data.get(DOMAIN, {}).get("primary_store")
        cat = getattr(self, "_selected_style_cat", "Inbox")

        current_icon = (store.category_icons.get(cat) if store else None) or ""
        current_color_hex = (store.category_colors.get(cat) if store else None) or ""

        current_rgb = None
        if current_color_hex and current_color_hex.startswith("#") and len(current_color_hex) == 7:
            try:
                current_rgb = [
                    int(current_color_hex[1:3], 16),
                    int(current_color_hex[3:5], 16),
                    int(current_color_hex[5:7], 16),
                ]
            except ValueError:
                current_rgb = None

        if user_input is not None:
            if store:
                reset = user_input.get("reset_style", False)
                if reset:
                    await store.async_set_category_style(cat, reset=True)
                else:
                    icon_val = user_input.get("icon")
                    color_val = user_input.get("color")
                    hex_color = None
                    if isinstance(color_val, (list, tuple)) and len(color_val) == 3:
                        hex_color = f"#{int(color_val[0]):02x}{int(color_val[1]):02x}{int(color_val[2]):02x}"
                    elif isinstance(color_val, str) and color_val.strip():
                        hex_color = color_val.strip()

                    await store.async_set_category_style(
                        cat,
                        icon=icon_val,
                        color=hex_color,
                    )
            return await self.async_step_category_style_done()

        schema_dict: dict[Any, Any] = {}
        icon_config = selector.IconSelectorConfig()
        if current_icon:
            schema_dict[vol.Optional("icon", default=current_icon)] = selector.IconSelector(icon_config)
        else:
            schema_dict[vol.Optional("icon")] = selector.IconSelector(icon_config)

        color_config = selector.ColorRGBSelectorConfig()
        if current_rgb:
            schema_dict[vol.Optional("color", default=current_rgb)] = selector.ColorRGBSelector(color_config)
        else:
            schema_dict[vol.Optional("color")] = selector.ColorRGBSelector(color_config)

        schema_dict[vol.Optional("reset_style", default=False)] = selector.BooleanSelector()

        return self.async_show_form(
            step_id="category_style_edit",
            data_schema=vol.Schema(schema_dict),
            description_placeholders={"category": cat},
            last_step=True,
        )

    async def async_step_category_style_done(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show completion options."""
        return self.async_show_menu(
            step_id="category_style_done",
            menu_options=self._get_localized_menu("category_style_done"),
            description_placeholders={"category": getattr(self, "_selected_style_cat", "")},
        )

    async def async_step_close(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Finish and close the options flow."""
        options = dict(self.config_entry.options or self.config_entry.data)
        return self.async_create_entry(title="", data=options)

    async def async_step_categories(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage categories."""
        options = dict(self.config_entry.options or self.config_entry.data)
        store = self.hass.data.get(DOMAIN, {}).get("primary_store")
        current_cats = (
            store.categories
            if store and store.categories
            else ["Inbox", "Smarthome", "Haus & Garten", "Projekte", "Alltag"]
        )

        if user_input is not None:
            if store:
                # 1. Process manual comma list edit. The field is pre-filled, so only
                # apply it if the user changed it, and first, so it cannot revert 2/3.
                edited_list = user_input.get("edit_categories")
                if edited_list and edited_list.strip() != self._shown_categories:
                    parsed = [c.strip() for c in edited_list.split(",") if c.strip()]
                    if parsed:
                        await store.async_set_categories(parsed)

                # 2. Process delete
                cat_to_del = user_input.get("delete_category")
                if cat_to_del and cat_to_del != "none":
                    await store.async_remove_category(cat_to_del)

                # 3. Process add
                cat_to_add = user_input.get("add_category")
                if cat_to_add and cat_to_add.strip():
                    await store.async_add_category(cat_to_add.strip())

            if CONF_HIDE_EMPTY_CATEGORIES in user_input:
                options[CONF_HIDE_EMPTY_CATEGORIES] = user_input[CONF_HIDE_EMPTY_CATEGORIES]

            return self.async_create_entry(title="", data=options)

        delete_options = [{"value": "none", "label": "Keine löschen"}]
        for c in current_cats:
            if c != "Inbox":
                delete_options.append({"value": c, "label": f"{c} löschen"})

        self._shown_categories = ", ".join(current_cats)

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
                    default=self._shown_categories,
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT,
                    )
                ),
                vol.Optional(
                    CONF_HIDE_EMPTY_CATEGORIES,
                    default=options.get(
                        CONF_HIDE_EMPTY_CATEGORIES, DEFAULT_HIDE_EMPTY_CATEGORIES
                    ),
                ): selector.BooleanSelector(),
            }
        )

        return self.async_show_form(
            step_id="categories",
            data_schema=data_schema,
            description_placeholders={"current_cats": self._shown_categories},
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
            # The frontend omits a cleared selector, which has to reset the list
            options[CONF_ALLOWED_ECHOS] = user_input.get(CONF_ALLOWED_ECHOS, [])
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
                vol.Optional(
                    CONF_ALLOWED_ECHOS,
                    description={
                        "suggested_value": options.get(CONF_ALLOWED_ECHOS, [])
                    },
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="media_player",
                        integration="alexa_media",
                        multiple=True,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="general",
            data_schema=data_schema,
        )

    async def async_step_alexa_skill(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Choose how Alexa voice input reaches Brainstorm."""
        options = dict(self.config_entry.options or self.config_entry.data)

        if user_input is not None:
            self._voice_mode = user_input[CONF_VOICE_MODE]
            if self._voice_mode == VOICE_MODE_NATIVE:
                options[CONF_VOICE_MODE] = self._voice_mode
                return self.async_create_entry(title="", data=options)
            return await self.async_step_alexa_skill_setup()

        return self.async_show_form(
            step_id="alexa_skill",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_VOICE_MODE,
                        default=options.get(CONF_VOICE_MODE, VOICE_MODE_NATIVE),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=VOICE_MODES,
                            mode=selector.SelectSelectorMode.LIST,
                            translation_key=CONF_VOICE_MODE,
                        )
                    ),
                }
            ),
            last_step=False,
        )

    async def async_step_alexa_skill_setup(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show what the user needs to build their own skill."""
        options = dict(self.config_entry.options or self.config_entry.data)
        skill = self.config_entry.runtime_data.alexa_skill

        if user_input is not None:
            if user_input.get("reset_skill"):
                await skill.async_reset()
            options[CONF_VOICE_MODE] = self._voice_mode
            return self.async_create_entry(title="", data=options)

        schema: dict[Any, Any] = {}
        errors: dict[str, str] = {}
        try:
            skill_code = skill.get_skill_code()
        except NoURLAvailableError:
            errors["base"] = "no_public_url"
        else:
            copy_field = selector.TextSelector(
                selector.TextSelectorConfig(multiline=True)
            )
            schema[
                vol.Optional("skill_code", description={"suggested_value": skill_code})
            ] = copy_field
            schema[
                vol.Optional(
                    "interaction_model",
                    description={"suggested_value": skill.get_interaction_model()},
                )
            ] = copy_field
        schema[vol.Optional("reset_skill", default=False)] = selector.BooleanSelector()

        last = skill.last_request
        return self.async_show_form(
            step_id="alexa_skill_setup",
            data_schema=vol.Schema(schema),
            errors=errors,
            description_placeholders={
                "linked": "✅" if skill.is_linked else "❌",
                "last_request": (
                    f"{last['time']} ({last['device']}): {last['text']}" if last else "–"
                ),
            },
            last_step=True,
        )

    def _notify_service_options(self) -> list[str]:
        """Return every notify target this installation has set up."""
        services = {
            f"notify.{name}"
            for name in self.hass.services.async_services().get("notify", {})
            if name != "send_message" and not name.startswith("alexa_media")
        }
        services.update(self.hass.states.async_entity_ids("notify"))
        return sorted(services)

    def _notify_field(self) -> selector.SelectSelector:
        """Return a field to pick notification services."""
        return selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=self._notify_service_options(),
                multiple=True,
                custom_value=True,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        )

    @staticmethod
    def _minutes_field(maximum: int) -> selector.NumberSelector:
        """Return a field for a number of minutes."""
        return selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0,
                max=maximum,
                step=5,
                unit_of_measurement="min",
                mode=selector.NumberSelectorMode.BOX,
            )
        )

    def _save_reminder_options(
        self, clearable: tuple[str, ...], user_input: dict[str, Any]
    ) -> FlowResult:
        """Save a form, where the frontend omits fields that were cleared."""
        options = dict(self.config_entry.options or self.config_entry.data)
        for key in clearable:
            options.pop(key, None)
        options.update(user_input)
        return self.async_create_entry(title="", data=options)

    async def async_step_reminders(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show the reminder sections."""
        return self.async_show_menu(
            step_id="reminders",
            menu_options=self._get_localized_menu("reminders"),
        )

    async def async_step_reminder_general(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Choose whether and over which channels Brainstorm reminds."""
        if user_input is not None:
            return self._save_reminder_options(
                (CONF_REMINDER_ECHOS, CONF_REMINDER_NOTIFY, CONF_URGENT_NOTIFY),
                user_input,
            )
        options = dict(self.config_entry.options or self.config_entry.data)
        return self.async_show_form(
            step_id="reminder_general",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_REMINDERS_ENABLED,
                        default=options.get(CONF_REMINDERS_ENABLED, True),
                    ): selector.BooleanSelector(),
                    vol.Required(
                        CONF_REMINDER_ALEXA,
                        default=options.get(CONF_REMINDER_ALEXA, REMINDER_ALEXA_OFF),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=REMINDER_ALEXA_MODES,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            translation_key=CONF_REMINDER_ALEXA,
                        )
                    ),
                    vol.Optional(
                        CONF_REMINDER_ECHOS,
                        description=_suggested(options, CONF_REMINDER_ECHOS),
                    ): _echo_field(multiple=True),
                    vol.Required(
                        CONF_NOTIFY_ENABLED,
                        default=options.get(CONF_NOTIFY_ENABLED, True),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_REMINDER_NOTIFY,
                        description=_suggested(options, CONF_REMINDER_NOTIFY),
                    ): self._notify_field(),
                    vol.Required(
                        CONF_REMINDER_DELAY,
                        default=options.get(CONF_REMINDER_DELAY, 0),
                    ): self._minutes_field(240),
                    vol.Required(
                        CONF_URGENT_ENABLED,
                        default=options.get(CONF_URGENT_ENABLED, False),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_URGENT_NOTIFY,
                        description=_suggested(options, CONF_URGENT_NOTIFY),
                    ): self._notify_field(),
                    vol.Required(
                        CONF_URGENT_DELAY,
                        default=options.get(CONF_URGENT_DELAY, DEFAULT_URGENT_DELAY),
                    ): self._minutes_field(1440),
                }
            ),
        )

    async def async_step_reminder_schedule(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Choose quiet hours, briefing and weekly review."""
        if user_input is not None:
            return self._save_reminder_options(
                (
                    CONF_QUIET_START,
                    CONF_QUIET_END,
                    CONF_DIGEST_TIME,
                    CONF_DIGEST_PRESENCE,
                    CONF_REVIEW_TIME,
                ),
                user_input,
            )
        options = dict(self.config_entry.options or self.config_entry.data)
        time_field = selector.TimeSelector()
        return self.async_show_form(
            step_id="reminder_schedule",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_QUIET_ENABLED,
                        default=options.get(CONF_QUIET_ENABLED, True),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_QUIET_START,
                        description=_suggested(options, CONF_QUIET_START),
                    ): time_field,
                    vol.Optional(
                        CONF_QUIET_END,
                        description=_suggested(options, CONF_QUIET_END),
                    ): time_field,
                    vol.Required(
                        CONF_DIGEST_ENABLED,
                        default=options.get(CONF_DIGEST_ENABLED, False),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_DIGEST_TIME,
                        description=_suggested(options, CONF_DIGEST_TIME),
                    ): time_field,
                    vol.Optional(
                        CONF_DIGEST_PRESENCE,
                        description=_suggested(options, CONF_DIGEST_PRESENCE),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["binary_sensor", "person"], multiple=True
                        )
                    ),
                    vol.Required(
                        CONF_REVIEW_ENABLED,
                        default=options.get(CONF_REVIEW_ENABLED, False),
                    ): selector.BooleanSelector(),
                    vol.Required(
                        CONF_REVIEW_WEEKDAY,
                        default=options.get(CONF_REVIEW_WEEKDAY, "6"),
                    ): _weekday_field(multiple=False),
                    vol.Optional(
                        CONF_REVIEW_TIME,
                        description=_suggested(options, CONF_REVIEW_TIME),
                    ): time_field,
                    vol.Required(
                        CONF_REVIEW_DAYS,
                        default=options.get(CONF_REVIEW_DAYS, DEFAULT_REVIEW_DAYS),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=365,
                            step=1,
                            unit_of_measurement="d",
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                }
            ),
        )

    async def async_step_reminder_lists(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Switch list rules on and choose the list to edit."""
        options = dict(self.config_entry.options or self.config_entry.data)
        if user_input is not None:
            enabled = user_input[CONF_LIST_RULES_ENABLED]
            if enabled and user_input.get("category"):
                self._rule_enabled = enabled
                self._rule_category = user_input["category"]
                return await self.async_step_reminder_list_edit()
            options[CONF_LIST_RULES_ENABLED] = enabled
            return self.async_create_entry(title="", data=options)

        store = self.config_entry.runtime_data
        return self.async_show_form(
            step_id="reminder_lists",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_LIST_RULES_ENABLED,
                        default=options.get(CONF_LIST_RULES_ENABLED, False),
                    ): selector.BooleanSelector(),
                    vol.Optional("category"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=list(store.categories),
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    async def async_step_reminder_list_edit(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Edit the rule of one list."""
        options = dict(self.config_entry.options or self.config_entry.data)
        rules = dict(options.get(CONF_LIST_RULES) or {})
        rule = rules.get(self._rule_category, {})
        if user_input is not None:
            rules[self._rule_category] = user_input
            options[CONF_LIST_RULES] = rules
            options[CONF_LIST_RULES_ENABLED] = self._rule_enabled
            return self.async_create_entry(title="", data=options)

        return self.async_show_form(
            step_id="reminder_list_edit",
            description_placeholders={"category": self._rule_category},
            data_schema=vol.Schema(
                {
                    vol.Required(
                        RULE_CHANNEL,
                        default=rule.get(RULE_CHANNEL, RULE_CHANNEL_DEFAULT),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=RULE_CHANNELS,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            translation_key=RULE_CHANNEL,
                        )
                    ),
                    vol.Optional(
                        RULE_NOTIFY, description=_suggested(rule, RULE_NOTIFY)
                    ): self._notify_field(),
                    vol.Required(
                        RULE_SCHEDULE_ENABLED,
                        default=rule.get(RULE_SCHEDULE_ENABLED, False),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        RULE_SCHEDULE_WEEKDAYS,
                        description=_suggested(rule, RULE_SCHEDULE_WEEKDAYS),
                    ): _weekday_field(multiple=True),
                    vol.Optional(
                        RULE_SCHEDULE_TIME,
                        description=_suggested(rule, RULE_SCHEDULE_TIME),
                    ): selector.TimeSelector(),
                    vol.Required(
                        RULE_ZONE_ENABLED, default=rule.get(RULE_ZONE_ENABLED, False)
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        RULE_ZONE, description=_suggested(rule, RULE_ZONE)
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="zone")
                    ),
                }
            ),
        )

    async def async_step_reminder_places(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Switch reminders at places and when arriving home on or off."""
        if user_input is not None:
            return self._save_reminder_options((CONF_DEFAULT_PERSON,), user_input)
        options = dict(self.config_entry.options or self.config_entry.data)
        return self.async_show_form(
            step_id="reminder_places",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_ARRIVAL_ENABLED,
                        default=options.get(CONF_ARRIVAL_ENABLED, False),
                    ): selector.BooleanSelector(),
                    vol.Required(
                        CONF_PLACES_ENABLED,
                        default=options.get(CONF_PLACES_ENABLED, False),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_DEFAULT_PERSON,
                        description=_suggested(options, CONF_DEFAULT_PERSON),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="person")
                    ),
                }
            ),
        )

    async def async_step_reminder_persons(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Switch reminders for people on and choose the person to edit."""
        options = dict(self.config_entry.options or self.config_entry.data)
        if user_input is not None:
            enabled = user_input[CONF_PERSONS_ENABLED]
            if enabled and user_input.get("person"):
                self._rule_enabled = enabled
                self._rule_person = user_input["person"]
                return await self.async_step_reminder_person_edit()
            options[CONF_PERSONS_ENABLED] = enabled
            return self.async_create_entry(title="", data=options)

        return self.async_show_form(
            step_id="reminder_persons",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_PERSONS_ENABLED,
                        default=options.get(CONF_PERSONS_ENABLED, False),
                    ): selector.BooleanSelector(),
                    vol.Optional("person"): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="person")
                    ),
                }
            ),
        )

    async def async_step_reminder_person_edit(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Choose where one person gets their reminders."""
        options = dict(self.config_entry.options or self.config_entry.data)
        rules = dict(options.get(CONF_PERSON_RULES) or {})
        rule = rules.get(self._rule_person, {})
        if user_input is not None:
            rules[self._rule_person] = user_input
            options[CONF_PERSON_RULES] = rules
            options[CONF_PERSONS_ENABLED] = self._rule_enabled
            return self.async_create_entry(title="", data=options)

        return self.async_show_form(
            step_id="reminder_person_edit",
            description_placeholders={"person": self._rule_person},
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "notify", description=_suggested(rule, "notify")
                    ): self._notify_field(),
                    vol.Optional(
                        "echos", description=_suggested(rule, "echos")
                    ): _echo_field(multiple=True),
                }
            ),
        )

    async def async_step_reminder_extras(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Switch calendar, AI and real Alexa reminders on or off."""
        if user_input is not None:
            return self._save_reminder_options(
                (CONF_CALENDAR_ENTITY, CONF_AI_ENTITY), user_input
            )
        options = dict(self.config_entry.options or self.config_entry.data)
        return self.async_show_form(
            step_id="reminder_extras",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_CALENDAR_ENABLED,
                        default=options.get(CONF_CALENDAR_ENABLED, False),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_CALENDAR_ENTITY,
                        description=_suggested(options, CONF_CALENDAR_ENTITY),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="calendar")
                    ),
                    vol.Required(
                        CONF_AI_ENABLED, default=options.get(CONF_AI_ENABLED, False)
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_AI_ENTITY, description=_suggested(options, CONF_AI_ENTITY)
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="ai_task")
                    ),
                    vol.Required(
                        CONF_NATIVE_REMINDERS,
                        default=options.get(CONF_NATIVE_REMINDERS, False),
                    ): selector.BooleanSelector(),
                }
            ),
        )
