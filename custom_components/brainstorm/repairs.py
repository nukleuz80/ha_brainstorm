"""Repair issues for settings that need the person's attention."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er, issue_registry as ir
from homeassistant.helpers.network import NoURLAvailableError, get_url

from .const import (
    CONF_ALLOWED_ECHOS,
    CONF_REMINDER_ECHOS,
    CONF_VOICE_MODE,
    DOMAIN,
    VOICE_MODE_NATIVE,
)

ISSUE_SKILL_NO_PUBLIC_URL = "skill_no_public_url"
ISSUE_MISSING_ECHOS = "missing_echos"
ISSUES = (ISSUE_SKILL_NO_PUBLIC_URL, ISSUE_MISSING_ECHOS)


def _has_public_url(hass: HomeAssistant) -> bool:
    """Return whether Alexa can reach this Home Assistant over HTTPS."""
    try:
        get_url(hass, allow_internal=False, allow_ip=False, require_ssl=True)
    except NoURLAvailableError:
        return False
    return True


def _missing_echos(hass: HomeAssistant, options: dict[str, object]) -> list[str]:
    """Return the chosen Echos that no longer exist in Home Assistant."""
    registry = er.async_get(hass)
    chosen: list[str] = []
    for key in (CONF_ALLOWED_ECHOS, CONF_REMINDER_ECHOS):
        value = options.get(key)
        if isinstance(value, list):
            chosen.extend(str(item) for item in value)
    # The registry is loaded before integrations, so a slow Alexa Media start
    # does not make an Echo look gone
    return sorted(
        {
            entity_id
            for entity_id in chosen
            if registry.async_get(entity_id) is None
            and hass.states.get(entity_id) is None
        }
    )


def async_check_issues(hass: HomeAssistant, options: dict[str, object]) -> None:
    """Create or clear the repair issues for the current settings."""
    if options.get(CONF_VOICE_MODE, VOICE_MODE_NATIVE) != VOICE_MODE_NATIVE and (
        not _has_public_url(hass)
    ):
        ir.async_create_issue(
            hass,
            DOMAIN,
            ISSUE_SKILL_NO_PUBLIC_URL,
            is_fixable=False,
            severity=ir.IssueSeverity.ERROR,
            translation_key=ISSUE_SKILL_NO_PUBLIC_URL,
        )
    else:
        ir.async_delete_issue(hass, DOMAIN, ISSUE_SKILL_NO_PUBLIC_URL)

    if missing := _missing_echos(hass, options):
        ir.async_create_issue(
            hass,
            DOMAIN,
            ISSUE_MISSING_ECHOS,
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key=ISSUE_MISSING_ECHOS,
            translation_placeholders={"echos": ", ".join(missing)},
        )
    else:
        ir.async_delete_issue(hass, DOMAIN, ISSUE_MISSING_ECHOS)


def async_delete_issues(hass: HomeAssistant) -> None:
    """Remove all repair issues when the integration is removed."""
    for issue_id in ISSUES:
        ir.async_delete_issue(hass, DOMAIN, issue_id)
