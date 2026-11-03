"""Diagnostics for Brainstorm Hub, without the content of any idea."""
from __future__ import annotations

from collections import Counter
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .const import (
    CONF_ALLOWED_ECHOS,
    CONF_CALENDAR_ENTITY,
    CONF_DEFAULT_PERSON,
    CONF_GLOSSARY,
    CONF_MARKDOWN_PATH,
    CONF_PERSON_RULES,
    CONF_PRIVACY_OWNER,
    CONF_REMINDER_ECHOS,
    CONF_REMINDER_NOTIFY,
    CONF_SHARE_USERS,
    CONF_URGENT_NOTIFY,
    CONF_VOICE_OWNERS,
)
from .store import BrainstormConfigEntry

# Settings that name people, rooms or private words
TO_REDACT = {
    CONF_ALLOWED_ECHOS,
    CONF_CALENDAR_ENTITY,
    CONF_DEFAULT_PERSON,
    CONF_GLOSSARY,
    CONF_MARKDOWN_PATH,
    CONF_PERSON_RULES,
    CONF_PRIVACY_OWNER,
    CONF_REMINDER_ECHOS,
    CONF_REMINDER_NOTIFY,
    CONF_SHARE_USERS,
    CONF_URGENT_NOTIFY,
    CONF_VOICE_OWNERS,
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: BrainstormConfigEntry
) -> dict[str, Any]:
    """Return what helps to find a problem, leaving out what people wrote."""
    store = entry.runtime_data
    ideas = store.ideas
    skill = store.alexa_skill
    reminders = store.reminders
    return {
        "entry": {
            "version": entry.version,
            "data": async_redact_data(dict(entry.data), TO_REDACT),
            "options": async_redact_data(dict(entry.options), TO_REDACT),
        },
        "integration_version": store.integration_version,
        "categories": len(store.categories),
        "ideas": {
            "total": len(ideas),
            "by_status": dict(Counter(str(i.get("status")) for i in ideas)),
            "by_source": dict(Counter(str(i.get("source")) for i in ideas)),
            "with_due": sum(1 for i in ideas if i.get("due")),
            "with_parent": sum(1 for i in ideas if i.get("parent_id")),
        },
        "voice_mode": store.voice_mode,
        "allowed_echos": len(store.allowed_echos),
        "privacy_enabled": store.privacy_enabled,
        "skill": {
            "linked": skill.is_linked if skill else None,
            "last_request_time": (
                skill.last_request.get("time")
                if skill and skill.last_request
                else None
            ),
        },
        "reminders_enabled": reminders.enabled if reminders else None,
    }
