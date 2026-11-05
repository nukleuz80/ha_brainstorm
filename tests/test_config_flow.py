"""Tests for the config and options flow."""
from __future__ import annotations

from datetime import timedelta
import json
from pathlib import Path
import re
from typing import Any
from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.entity import DATA_ENTITY_SOURCE
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_mock_service

from custom_components.brainstorm.const import DOMAIN, OVERVIEW_ENTITY_ID

from .conftest import SetupEntry


async def test_user_flow_and_single_instance(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test creating an entry and that only one instance is allowed."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    # Only one entry can exist, so nothing needs a unique ID
    assert result["result"].unique_id is None
    # None of these settings is a connection detail
    assert result["result"].data == {}
    assert result["result"].options["markdown_path"] == "/config/brainstorm"
    await hass.async_block_till_done()

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "single_instance_allowed"


async def test_yaml_is_not_supported(hass: HomeAssistant) -> None:
    """Test that the integration is config entry only."""
    from custom_components.brainstorm import CONFIG_SCHEMA  # noqa: PLC0415

    assert CONFIG_SCHEMA({DOMAIN: {}}) is not None


async def test_reconfigure_takes_effect_with_options(
    hass: HomeAssistant, setup_entry: SetupEntry, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that reconfigure wins over existing options and reloads once."""
    entry = await setup_entry(
        data={"smart_formatting": True},
        options={"smart_formatting": True, "default_category": "Projekte"},
    )
    old_store = entry.runtime_data

    result = await entry.start_reconfigure_flow(hass)
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"smart_formatting": False, "markdown_path": "/config/neu"},
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    await hass.async_block_till_done()

    assert entry.runtime_data is not old_store
    assert entry.runtime_data._smart_formatting is False  # noqa: SLF001
    assert entry.options["default_category"] == "Projekte"
    assert entry.options["smart_formatting"] is False
    assert entry.data == {"smart_formatting": True}
    assert "update listener" not in caplog.text


async def _submit_categories(
    hass: HomeAssistant, entry: Any, **user_input: Any
) -> dict[str, Any]:
    """Open the category form and submit it like the frontend does."""
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.MENU
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "categories"}
    )
    assert result["type"] is FlowResultType.FORM
    prefilled = result["description_placeholders"]["current_cats"]
    payload = {"edit_categories": prefilled, "delete_category": "none"} | user_input
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], payload
    )
    assert result["type"] is FlowResultType.MENU
    await hass.async_block_till_done()
    return result


async def test_options_delete_and_add_category(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that the pre-filled list does not revert a delete or an add."""
    entry = await setup_entry()
    idea = await entry.runtime_data.async_add_idea("xyz abc", category="Alltag")

    await _submit_categories(hass, entry, delete_category="Alltag", add_category="Reisen")

    store = entry.runtime_data
    assert "Alltag" not in store.categories
    assert "Reisen" in store.categories
    assert store._ideas[idea["id"]]["category"] == "Inbox"  # noqa: SLF001


async def test_options_edit_category_list(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test editing the full list together with an add."""
    entry = await setup_entry()
    await _submit_categories(
        hass, entry, edit_categories="Inbox, Alltag, Neu", add_category="Reisen"
    )
    assert entry.runtime_data.categories == ["Inbox", "Alltag", "Neu", "Reisen"]


async def test_options_unchanged_form_keeps_parallel_category(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a category added while the form is open survives."""
    entry = await setup_entry()
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "categories"}
    )
    prefilled = result["description_placeholders"]["current_cats"]
    await entry.runtime_data.async_add_category("Parallel")
    await hass.config_entries.options.async_configure(
        result["flow_id"], {"edit_categories": prefilled, "delete_category": "none"}
    )
    await hass.async_block_till_done()
    assert "Parallel" in entry.runtime_data.categories


async def test_options_category_style_flow(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the two step category design flow."""
    entry = await setup_entry()
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "category_style"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"category": "Alltag"}
    )
    assert result["step_id"] == "category_style_edit"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"icon": "mdi:home", "color": [255, 120, 0]}
    )
    assert result["type"] is FlowResultType.MENU
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "close"}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert entry.runtime_data.category_colors == {"Alltag": "#ff7800"}
    assert entry.runtime_data.category_icons == {"Alltag": "mdi:home"}


async def _submit_general(
    hass: HomeAssistant, entry: Any, **user_input: Any
) -> None:
    """Submit the general settings form."""
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "general"}
    )
    assert result["step_id"] == "general"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input
    )
    assert result["step_id"] == "init"
    await hass.async_block_till_done()


async def test_options_allowed_echos(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test selecting Echos, exposing them on the sensor and clearing them."""
    entry = await setup_entry()
    assert hass.states.get(OVERVIEW_ENTITY_ID).attributes["allowed_echos"] == []

    echos = ["media_player.echo_show_kuche", "media_player.wohnzimmer_echo_dot"]
    await _submit_general(hass, entry, allowed_echos=echos)
    assert entry.runtime_data.allowed_echos == echos
    assert hass.states.get(OVERVIEW_ENTITY_ID).attributes["allowed_echos"] == echos

    # The frontend omits a cleared selector
    await _submit_general(hass, entry)
    assert entry.options["allowed_echos"] == []
    assert hass.states.get(OVERVIEW_ENTITY_ID).attributes["allowed_echos"] == []


async def test_saving_applies_at_once_and_returns_to_menu(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a form neither closes the settings nor waits for closing them."""
    entry = await setup_entry()
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "general"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"smart_formatting": False}
    )
    assert result["type"] is FlowResultType.MENU
    assert "✅" in result["description_placeholders"]["notice"]
    assert entry.options["smart_formatting"] is False
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "close"}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options["smart_formatting"] is False


@pytest.mark.parametrize(
    ("path", "parent"),
    [
        (["general"], "init"),
        (["categories"], "init"),
        (["alexa_skill"], "init"),
        (["ai"], "init"),
        (["category_style"], "init"),
        (["reminders", "reminder_general"], "reminders"),
        (["reminders", "reminder_schedule"], "reminders"),
        (["reminders", "reminder_lists"], "reminders"),
        (["reminders", "reminder_places"], "reminders"),
        (["reminders", "reminder_persons"], "reminders"),
        (["reminders", "reminder_extras"], "reminders"),
        (["reminders", "reminder_locks"], "reminders"),
        (["battery"], "init"),
        (["reminders", "reminder_test"], "reminders"),
    ],
)
async def test_every_form_can_go_back_without_saving(
    hass: HomeAssistant, setup_entry: SetupEntry, path: list[str], parent: str
) -> None:
    """Test going back from each form, which must not change anything."""
    entry = await setup_entry(options={"smart_formatting": True})
    before = dict(entry.options)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    for step in path:
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {"next_step_id": step}
        )

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"go_back": True}
    )

    assert result["type"] is FlowResultType.MENU
    assert result["step_id"] == parent
    assert dict(entry.options) == before


async def test_submenu_goes_back_and_shows_status(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the back entry and the live status of the reminder menu."""
    entry = await setup_entry(
        options={
            "reminder_notify": ["notify.phone"],
            "quiet_start": "22:00:00",
            "quiet_end": "07:00:00",
        }
    )
    await entry.runtime_data.async_add_idea(
        "tonnen raus", due=dt_util.now() + timedelta(hours=2)
    )
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "reminders"}
    )
    placeholders = result["description_placeholders"]
    assert "🟢 Benachrichtigungen: phone" in placeholders["status_general"]
    assert "22:00–07:00" in placeholders["status_schedule"]
    assert placeholders["status_lists"] == "⚪ Aus"
    assert "tonnen raus" in placeholders["next_reminder"].lower()

    root = Path(__file__).parents[1] / "custom_components" / "brainstorm"
    for name in ("strings.json", "translations/en.json", "translations/de.json"):
        step = json.loads((root / name).read_text("utf-8"))["options"]["step"]["reminders"]
        for option, text in step["menu_option_descriptions"].items():
            assert option in result["menu_options"]
            assert text.strip("{}") in placeholders

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "init"}
    )
    assert result["step_id"] == "init"


async def test_channel_test_reports_each_channel(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that the test asks first, sends for real and reports the results."""
    calls = async_mock_service(hass, "notify", "phone")
    entry = await setup_entry(options={"reminder_notify": ["notify.phone", "notify.gone"]})
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "reminders"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "reminder_test"}
    )
    assert result["step_id"] == "reminder_test"
    assert "notify.phone" in result["description_placeholders"]["targets"]
    assert not calls

    result = await hass.config_entries.options.async_configure(result["flow_id"], {})
    assert result["step_id"] == "reminder_test_result"
    assert len(calls) == 1
    report = result["description_placeholders"]["results"]
    assert "✅ notify.phone" in report
    assert "❌ notify.gone" in report

    result = await hass.config_entries.options.async_configure(result["flow_id"], {})
    assert result["step_id"] == "reminders"


async def test_all_form_fields_have_a_label(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the back field in the texts of all forms."""
    root = Path(__file__).parent.parent / "custom_components" / "brainstorm"
    for name in ("strings.json", "translations/en.json", "translations/de.json"):
        steps = json.loads((root / name).read_text("utf-8"))["options"]["step"]
        for step_id, step in steps.items():
            if "menu_options" not in step and step_id not in (
                "tools_info",
                "reminder_test_result",
            ):
                assert "go_back" in step["data"], (name, step_id)


async def test_all_fields_are_explained_in_every_language() -> None:
    """Test that every field of every flow has a label and a description."""
    root = Path(__file__).parent.parent / "custom_components" / "brainstorm"
    for name in ("strings.json", "translations/en.json", "translations/de.json"):
        texts = json.loads((root / name).read_text("utf-8"))
        for flow in ("config", "options"):
            for step_id, step in texts[flow]["step"].items():
                assert set(step.get("data", {})) == set(
                    step.get("data_description", {})
                ), (name, flow, step_id)


async def test_all_errors_and_aborts_have_a_text() -> None:
    """Test that each error and abort the flow can show has a translation."""
    root = Path(__file__).parent.parent / "custom_components" / "brainstorm"
    source = (root / "config_flow.py").read_text("utf-8")
    errors = set(re.findall(r'errors\[[^\]]+\] = "(\w+)"', source))
    aborts = set(re.findall(r'reason="(\w+)"|AbortFlow\("(\w+)"\)', source))
    aborts = {reason for pair in aborts for reason in pair if reason}
    assert errors == {
        "no_public_url",
        "owner_required",
        "todo_sync_duplicate",
        "bring_category_missing",
        "battery_category_missing",
        "lock_time_missing",
    }
    assert aborts == {"reconfigure_successful", "store_not_ready"}
    for name in ("strings.json", "translations/en.json", "translations/de.json"):
        texts = json.loads((root / name).read_text("utf-8"))
        assert errors <= set(texts["options"]["error"])
        assert "store_not_ready" in texts["options"]["abort"]
        assert "reconfigure_successful" in texts["config"]["abort"]
        assert "single_instance_allowed" in texts["config"]["abort"]


async def _open_options(hass: HomeAssistant, entry: Any, *path: str) -> dict[str, Any]:
    """Open the settings and follow menu entries."""
    result = await hass.config_entries.options.async_init(entry.entry_id)
    for step in path:
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {"next_step_id": step}
        )
    return result


async def test_category_style_shows_and_resets_stored_design(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a stored design is shown, kept in the form and can be reset."""
    entry = await setup_entry()
    store = entry.runtime_data
    await store.async_set_category_style("Alltag", icon="mdi:home", color="#ff7800")

    result = await _open_options(hass, entry, "category_style")
    labels = {
        option["label"]
        for option in result["data_schema"].schema["category"].config["options"]
    }
    assert "Alltag (Icon: mdi:home, Farbe: #ff7800)" in labels
    assert "Inbox (Standard)" in labels

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"category": "Alltag"}
    )
    defaults = {str(key): key.default() for key in result["data_schema"].schema}
    assert defaults["icon"] == "mdi:home"
    assert defaults["color"] == [255, 120, 0]

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"go_back": True}
    )
    assert result["step_id"] == "category_style"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"category": "Alltag"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"reset_style": True}
    )
    assert result["step_id"] == "category_style_done"
    assert "Alltag" not in store.category_icons
    assert "Alltag" not in store.category_colors


async def test_category_style_tolerates_an_invalid_stored_color(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a broken color in the storage does not block the form."""
    entry = await setup_entry(stored={"category_colors": {"Alltag": "#zzzzzz"}})

    result = await _open_options(hass, entry, "category_style")
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"category": "Alltag"}
    )
    assert result["step_id"] == "category_style_edit"
    color = next(key for key in result["data_schema"].schema if str(key) == "color")
    assert not callable(color.default)


async def test_voice_mode_native_is_saved_without_the_setup_page(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that the native mode skips everything about the skill."""
    entry = await setup_entry(options={"voice_mode": "skill"})
    result = await _open_options(hass, entry, "alexa_skill")
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"voice_mode": "native"}
    )
    assert result["step_id"] == "init"
    assert entry.options["voice_mode"] == "native"


async def test_skill_setup_recovers_from_a_missing_public_address(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test the error without a public address and finishing after fixing it."""
    entry = await setup_entry()
    result = await _open_options(hass, entry, "alexa_skill")
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"voice_mode": "skill"}
    )
    assert result["step_id"] == "alexa_skill_setup"
    assert result["errors"] == {"base": "no_public_url"}
    assert "voice_mode" not in entry.options

    hass.config.external_url = "https://home.example.org"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"go_back": True}
    )
    assert result["step_id"] == "alexa_skill"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"voice_mode": "skill"}
    )
    assert result["errors"] == {}
    result = await hass.config_entries.options.async_configure(result["flow_id"], {})
    assert result["step_id"] == "init"
    assert entry.options["voice_mode"] == "skill"


@pytest.mark.parametrize("step", ["privacy", "privacy_voice"])
async def test_privacy_forms_can_go_back(
    hass: HomeAssistant, setup_entry: SetupEntry, step: str
) -> None:
    """Test leaving the privacy forms, which need the list of users to open."""
    entry = await setup_entry(options={"smart_formatting": True})
    before = dict(entry.options)
    result = await _open_options(hass, entry, step)
    assert result["step_id"] == step
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"go_back": True, "device": "x"}
        if step == "privacy_voice"
        else {"go_back": True, "privacy_enabled": False, "privacy_export": False}
    )
    assert result["step_id"] == "init"
    assert dict(entry.options) == before


async def test_privacy_voice_offers_alexa_media_devices(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that only media players of Alexa Media are offered as Echos."""
    entry = await setup_entry()
    hass.states.async_set("media_player.kueche", "idle", {"friendly_name": "Echo Küche"})
    hass.states.async_set("media_player.tv", "idle", {"friendly_name": "Fernseher"})
    hass.data.setdefault(DATA_ENTITY_SOURCE, {})["media_player.kueche"] = {
        "domain": "alexa_media",
        "custom_component": True,
    }

    result = await _open_options(hass, entry, "privacy_voice")
    assert result["data_schema"].schema["device"].config["options"] == ["Echo Küche"]


async def test_store_is_awaited_while_settings_are_applied(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a form waits for a reload and explains if that takes too long."""
    entry = await setup_entry()
    result = await _open_options(hass, entry, "reminders")
    assert await hass.config_entries.async_unload(entry.entry_id)

    with patch("custom_components.brainstorm.config_flow.STORE_WAIT_SECONDS", 0):
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {"next_step_id": "reminder_lists"}
        )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "store_not_ready"

    # Trying again works as soon as Brainstorm is back
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    result = await _open_options(hass, entry, "reminders", "reminder_lists")
    assert result["step_id"] == "reminder_lists"


async def test_list_rule_is_saved_and_shown_again(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test editing the rule of one list, including going back from it."""
    entry = await setup_entry()
    result = await _open_options(hass, entry, "reminders", "reminder_lists")
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"list_rules_enabled": True, "category": "Alltag"}
    )
    assert result["step_id"] == "reminder_list_edit"
    assert result["description_placeholders"]["category"] == "Alltag"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "go_back": True,
            "channel": "default",
            "schedule_enabled": False,
            "zone_enabled": False,
        },
    )
    assert result["step_id"] == "reminder_lists"
    assert "list_rules" not in entry.options

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"list_rules_enabled": True, "category": "Alltag"}
    )
    rule = {"channel": "alexa", "schedule_enabled": False, "zone_enabled": False}
    result = await hass.config_entries.options.async_configure(result["flow_id"], rule)
    assert result["step_id"] == "reminders"
    assert entry.options["list_rules_enabled"] is True
    assert entry.options["list_rules"] == {"Alltag": rule}
    await hass.async_block_till_done()


async def test_person_rule_is_saved(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test choosing the channels of one person, including going back from it."""
    hass.states.async_set("person.alex", "home", {"friendly_name": "Alex"})
    entry = await setup_entry()
    result = await _open_options(hass, entry, "reminders", "reminder_persons")
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"persons_enabled": True, "person": "person.alex"}
    )
    assert result["step_id"] == "reminder_person_edit"
    assert result["description_placeholders"]["person"] == "person.alex"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"go_back": True}
    )
    assert result["step_id"] == "reminder_persons"
    assert "person_rules" not in entry.options

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"persons_enabled": True, "person": "person.alex"}
    )
    rule = {"notify": ["notify.alex"]}
    result = await hass.config_entries.options.async_configure(result["flow_id"], rule)
    assert result["step_id"] == "reminders"
    assert entry.options["persons_enabled"] is True
    assert entry.options["person_rules"] == {"person.alex": rule}
    await hass.async_block_till_done()


@pytest.mark.parametrize("readme", ["README.md", "README_de.md"])
async def test_every_setting_is_documented(readme: str) -> None:
    """Test that the README names each field the way the forms show it."""
    repo = Path(__file__).parent.parent
    language = "translations/de.json" if readme == "README_de.md" else "strings.json"
    root = repo / "custom_components" / "brainstorm"
    texts = json.loads((root / language).read_text("utf-8"))
    document = (repo / readme).read_text("utf-8")
    for flow in ("config", "options"):
        for step in texts[flow]["step"].values():
            for field, label in step.get("data", {}).items():
                if field != "go_back":
                    assert f"| {label} |" in document, (readme, field)


async def test_glossary_can_be_cleared(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that an emptied list of own terms is really removed."""
    entry = await setup_entry(options={"glossary": "Lenia"})
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "general"}
    )
    await hass.config_entries.options.async_configure(result["flow_id"], {})
    await hass.async_block_till_done()
    assert entry.options["glossary"] == ""


async def test_ai_has_its_own_menu_entry(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that the AI is set in its own section, which can also clear it."""
    entry = await setup_entry(options={"ai_entity": "ai_task.old"})
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert "ai" in result["menu_options"]
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "ai"}
    )
    assert result["step_id"] == "ai"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"ai_entity": "ai_task.test", "ai_text_cleanup": True, "ai_enabled": False},
    )
    assert result["type"] is FlowResultType.MENU
    assert result["step_id"] == "init"
    assert entry.options["ai_entity"] == "ai_task.test"
    assert entry.options["ai_text_cleanup"] is True
    await hass.async_block_till_done()
    assert hass.states.get(OVERVIEW_ENTITY_ID).attributes["ai_subtasks"] is True

    # The frontend leaves a cleared entity field out
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "ai"}
    )
    await hass.config_entries.options.async_configure(
        result["flow_id"], {"ai_text_cleanup": False, "ai_enabled": False}
    )
    assert "ai_entity" not in entry.options


async def test_calendar_and_alexa_extras_no_longer_ask_for_the_ai(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that saving the extras keeps the AI settings untouched."""
    entry = await setup_entry(
        options={"ai_entity": "ai_task.test", "ai_text_cleanup": True}
    )
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "reminders"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "reminder_extras"}
    )
    fields = {str(key) for key in result["data_schema"].schema}
    assert not fields & {"ai_entity", "ai_enabled", "ai_text_cleanup"}
    await hass.config_entries.options.async_configure(
        result["flow_id"], {"calendar_enabled": False, "native_reminders": False}
    )
    assert entry.options["ai_entity"] == "ai_task.test"
    assert entry.options["ai_text_cleanup"] is True
