"""Tests for the cards that come with the integration."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any
from unittest.mock import AsyncMock, patch

from homeassistant.core import HomeAssistant

from custom_components.brainstorm.frontend import (
    CARD_FILES,
    DATA_FRONTEND,
    FRONTEND_DIR,
    FRONTEND_URL,
)

from .conftest import SetupEntry

MANIFEST_VERSION = re.search(
    r'"version": "([^"]+)"',
    (FRONTEND_DIR.parent / "manifest.json").read_text(encoding="utf-8"),
)


def test_cards_lie_in_the_integration() -> None:
    """HACS only installs the integration folder, so the cards live there."""
    for name in (*CARD_FILES, "brainstorm-i18n.js", "brainstorm-bulb.svg"):
        assert (FRONTEND_DIR / name).is_file(), name
    assert not (Path(__file__).parents[1] / "www").exists()


def test_cards_find_the_bulb_next_to_them() -> None:
    """The cards no longer expect their image under /local."""
    for name in CARD_FILES:
        assert "/local/" not in (FRONTEND_DIR / name).read_text(encoding="utf-8")


async def test_cards_are_served_and_loaded(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that the folder is served and both cards load on every dashboard."""
    registered: list[Any] = []
    urls: list[str] = []
    hass.config.components.add("frontend")
    with (
        patch(
            "homeassistant.components.http.HomeAssistantHTTP"
            ".async_register_static_paths",
            AsyncMock(side_effect=lambda configs: registered.extend(configs)),
        ),
        patch(
            "custom_components.brainstorm.frontend.add_extra_js_url",
            side_effect=lambda _hass, url: urls.append(url),
        ),
    ):
        hass.data.pop(DATA_FRONTEND, None)
        entry = await setup_entry()
        # A reload of the entry must not add the cards a second time
        await hass.config_entries.async_reload(entry.entry_id)
        await hass.async_block_till_done()

    assert [(c.url_path, c.path) for c in registered] == [
        (FRONTEND_URL, str(FRONTEND_DIR))
    ]
    assert MANIFEST_VERSION
    version = MANIFEST_VERSION.group(1)
    assert urls == [f"{FRONTEND_URL}/{card}?v={version}" for card in CARD_FILES]


async def test_without_frontend_only_the_files_are_served(
    hass: HomeAssistant, setup_entry: SetupEntry
) -> None:
    """Test that a setup without the frontend does not fail."""
    if "frontend" in hass.config.components:
        hass.config.components.remove("frontend")
    serve = AsyncMock()
    with (
        patch(
            "homeassistant.components.http.HomeAssistantHTTP"
            ".async_register_static_paths",
            serve,
        ),
        patch("custom_components.brainstorm.frontend.add_extra_js_url") as add,
    ):
        hass.data.pop(DATA_FRONTEND, None)
        await setup_entry()
    serve.assert_awaited_once()
    add.assert_not_called()
