"""Tests for diagnostics, repair issues and icons of the Gold quality level."""
from __future__ import annotations

import json
from pathlib import Path

from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir

from custom_components.brainstorm.const import DOMAIN
from custom_components.brainstorm.diagnostics import async_get_config_entry_diagnostics
from custom_components.brainstorm.repairs import (
    ISSUE_MISSING_ECHOS,
    ISSUE_SKILL_NO_PUBLIC_URL,
)

from .conftest import SetupEntry

COMPONENT = Path(__file__).parent.parent / "custom_components" / "brainstorm"
SECRET_TEXT = "Geheimes Geschenk für Frida"


async def test_diagnostics_leave_out_ideas_and_people(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that diagnostics count ideas but never show their text or people."""
    entry = await setup_entry(
        stored={
            "categories": ["Inbox", "Alltag"],
            "ideas": [
                {
                    "id": "a1",
                    "text": SECRET_TEXT,
                    "category": "Alltag",
                    "status": "active",
                    "source": "alexa_skill",
                    "created_at": "2026-11-03T10:00:00+01:00",
                    "due": "2026-11-04T09:00:00+01:00",
                }
            ],
        },
        options={
            "allowed_echos": ["media_player.frida_echo_dot"],
            "glossary": "Frida",
            "voice_owners": {"Frida Echo": "user-1"},
        },
    )

    result = await async_get_config_entry_diagnostics(hass, entry)
    dumped = json.dumps(result, ensure_ascii=False)

    assert result["ideas"]["total"] == 1
    assert result["ideas"]["by_status"] == {"active": 1}
    assert result["ideas"]["with_due"] == 1
    assert result["allowed_echos"] == 1
    assert "Frida" not in dumped
    assert "frida" not in dumped
    assert "user-1" not in dumped
    assert SECRET_TEXT not in dumped


async def test_skill_without_public_address_raises_an_issue(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the repair issue for a skill that Alexa cannot reach."""
    issues = ir.async_get(hass)
    entry = await setup_entry(options={"voice_mode": "skill"})

    issue = issues.async_get_issue(DOMAIN, ISSUE_SKILL_NO_PUBLIC_URL)
    assert issue is not None
    assert issue.severity == ir.IssueSeverity.ERROR

    hass.config.external_url = "https://home.example.org"
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    assert issues.async_get_issue(DOMAIN, ISSUE_SKILL_NO_PUBLIC_URL) is None


async def test_native_voice_needs_no_public_address(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that the native voice input does not ask for a public address."""
    await setup_entry()

    assert ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_SKILL_NO_PUBLIC_URL) is None


async def test_missing_echo_raises_an_issue(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the repair issue for chosen Echos that are gone, and its removal."""
    hass.states.async_set("media_player.kueche", "idle")
    entry = await setup_entry(
        options={
            "allowed_echos": ["media_player.kueche", "media_player.alt"],
            "reminder_echos": ["media_player.weg"],
        }
    )

    issue = ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_MISSING_ECHOS)
    assert issue is not None
    assert issue.translation_placeholders == {
        "echos": "media_player.alt, media_player.weg"
    }

    await hass.config_entries.async_remove(entry.entry_id)
    await hass.async_block_till_done()

    assert ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_MISSING_ECHOS) is None


def test_every_issue_and_icon_is_translated() -> None:
    """Test that issues, icons and the setup error have their texts."""
    icons = json.loads((COMPONENT / "icons.json").read_text("utf-8"))
    services = (COMPONENT / "services.yaml").read_text("utf-8")
    for name in icons["services"]:
        assert f"\n{name}:" in f"\n{services}"
    for path in ("strings.json", "translations/en.json", "translations/de.json"):
        texts = json.loads((COMPONENT / path).read_text("utf-8"))
        assert set(texts["issues"]) == {ISSUE_SKILL_NO_PUBLIC_URL, ISSUE_MISSING_ECHOS}
        assert "{echos}" in texts["issues"][ISSUE_MISSING_ECHOS]["description"]
        assert "{error}" in texts["exceptions"]["store_not_readable"]["message"]
