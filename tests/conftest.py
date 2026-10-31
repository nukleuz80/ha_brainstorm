"""Fixtures for Brainstorm Hub tests."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.brainstorm.const import DOMAIN, STORAGE_KEY

SetupEntry = Callable[..., Awaitable[MockConfigEntry]]


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Enable loading of custom integrations in all tests."""


@pytest.fixture
def setup_entry(hass: HomeAssistant, hass_storage: dict[str, Any]) -> SetupEntry:
    """Return a helper that sets up a config entry with optional stored data."""

    async def _setup(
        stored: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        options: dict[str, Any] | None = None,
    ) -> MockConfigEntry:
        if stored is not None:
            hass_storage[STORAGE_KEY] = {
                "version": 1,
                "minor_version": 1,
                "key": STORAGE_KEY,
                "data": stored,
            }
        entry = MockConfigEntry(
            domain=DOMAIN, title="Brainstorm Hub", data=data or {}, options=options or {}
        )
        entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        return entry

    return _setup
