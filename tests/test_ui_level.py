"""Tests for the operating levels: beginner, normal and pro."""
from __future__ import annotations

from pathlib import Path

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.brainstorm.const import DOMAIN, OVERVIEW_ENTITY_ID, PRO_MENU_STEPS

from .conftest import SetupEntry

CARDS = Path(__file__).parents[1] / "custom_components/brainstorm/cards"


async def _menu(hass: HomeAssistant, entry_id: str, step: str | None = None) -> list[str]:
    """Return the options of the main menu or of a submenu."""
    result = await hass.config_entries.options.async_init(entry_id)
    if step:
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {"next_step_id": step}
        )
    return list(result["menu_options"])


async def test_new_installations_start_normal(hass: HomeAssistant) -> None:
    """A new installation shows the normal level."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["result"].options["ui_level"] == "normal"
    await hass.async_block_till_done()
    assert hass.states.get(OVERVIEW_ENTITY_ID).attributes["ui_level"] == "normal"


async def test_existing_installations_keep_everything(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """An installation from before the levels stays at pro, with every menu entry."""
    entry = await setup_entry()
    assert entry.runtime_data.ui_level == "pro"
    assert hass.states.get(OVERVIEW_ENTITY_ID).attributes["ui_level"] == "pro"
    assert {"battery", "privacy_voice"} <= set(await _menu(hass, entry.entry_id))
    assert {"reminder_lists", "reminder_locks"} <= set(
        await _menu(hass, entry.entry_id, "reminders")
    )


async def test_lower_levels_hide_pro_settings(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Beginners and normal users do not see the settings for pros."""
    for level in ("beginner", "normal"):
        entry = await setup_entry(options={"ui_level": level})
        menus = set(await _menu(hass, entry.entry_id))
        menus |= set(await _menu(hass, entry.entry_id, "reminders"))
        assert not menus & PRO_MENU_STEPS, level
        assert {"general", "reminder_general", "ai"} <= menus
        await hass.config_entries.async_remove(entry.entry_id)
        await hass.async_block_till_done()


async def test_level_is_set_under_general(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """The general settings change the level, and the sensor tells the cards."""
    entry = await setup_entry()
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "general"}
    )
    assert "ui_level" in result["data_schema"].schema
    await hass.config_entries.options.async_configure(
        result["flow_id"], {"ui_level": "beginner"}
    )
    await hass.async_block_till_done()
    assert entry.options["ui_level"] == "beginner"
    assert hass.states.get(OVERVIEW_ENTITY_ID).attributes["ui_level"] == "beginner"
    assert "battery" not in await _menu(hass, entry.entry_id)


async def test_ai_text_cleanup_only_for_pros_and_kept(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Hiding the AI fine point keeps its value."""
    entry = await setup_entry(options={"ui_level": "normal", "ai_text_cleanup": True})
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "ai"}
    )
    assert "ai_text_cleanup" not in result["data_schema"].schema
    await hass.config_entries.options.async_configure(
        result["flow_id"], {"ai_enabled": True}
    )
    await hass.async_block_till_done()
    assert entry.options["ai_text_cleanup"] is True
    assert entry.options["ai_enabled"] is True


async def test_unknown_level_falls_back_to_pro(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """A broken value never hides anything."""
    entry = await setup_entry(options={"ui_level": "expert"})
    assert entry.runtime_data.ui_level == "pro"


def test_cards_hide_by_level() -> None:
    """Both cards set their level and offer it in the editor."""
    for card in ("brainstorm-card.js", "brainstorm-mindmap-card.js"):
        source = (CARDS / card).read_text("utf-8")
        assert "${LEVEL_CSS}" in source, card
        assert 'this.setAttribute("data-level"' in source, card
        assert 'name: "level"' in source, card
        assert "addMoreFields(body" in source, card
        assert 'data-lvl="pro"' in source and 'data-lvl="normal"' in source, card


def test_list_rows_keep_their_width() -> None:
    """The row buttons sit behind ⋯ on phones and fold subtasks in the meta row."""
    source = (CARDS / "brainstorm-card.js").read_text("utf-8")
    assert 'class="more-btn"' in source
    assert "collapse-chip" in source
    assert 'name: "row_actions"' in source
    assert "@container brainstorm-ha-card (max-width: 520px)" in source
    assert "min-width: 44px" in source
