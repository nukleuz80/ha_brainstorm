"""Tests for the config and options flow."""
from __future__ import annotations

from datetime import timedelta
import json
from pathlib import Path
from typing import Any

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
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
    await hass.async_block_till_done()

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT


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
        (["category_style"], "init"),
        (["reminders", "reminder_general"], "reminders"),
        (["reminders", "reminder_schedule"], "reminders"),
        (["reminders", "reminder_lists"], "reminders"),
        (["reminders", "reminder_places"], "reminders"),
        (["reminders", "reminder_persons"], "reminders"),
        (["reminders", "reminder_extras"], "reminders"),
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
    status = result["description_placeholders"]["status"]
    assert "🟢" in status
    assert "22:00–07:00" in status
    assert "phone" in status
    assert "tonnen raus".lower() in status.lower()

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
