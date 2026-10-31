"""Tests for the config and options flow."""
from __future__ import annotations

from typing import Any

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.brainstorm.const import DOMAIN

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
    assert result["type"] is FlowResultType.CREATE_ENTRY
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
