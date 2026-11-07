"""Serve the dashboard cards from the integration folder."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

FRONTEND_URL = f"/{DOMAIN}_frontend"
FRONTEND_DIR = Path(__file__).parent / "cards"
CARD_FILES = ("brainstorm-card.js", "brainstorm-mindmap-card.js")
DATA_FRONTEND = f"{DOMAIN}_frontend_registered"


async def async_register_frontend(hass: HomeAssistant) -> None:
    """Serve the cards and load them on every dashboard, once per run.

    HACS installs only the integration, so the cards come with it: the
    folder is served as static files and the frontend loads both cards as
    modules, in storage and YAML mode alike. The version in the address
    makes browsers fetch new cards after an update.
    """
    if hass.data.get(DATA_FRONTEND):
        return
    if getattr(hass, "http", None) is None:
        _LOGGER.debug("No HTTP server, the cards are not served")
        return
    await hass.http.async_register_static_paths(
        [StaticPathConfig(FRONTEND_URL, str(FRONTEND_DIR), True)]
    )
    hass.data[DATA_FRONTEND] = True
    if "frontend" not in hass.config.components:
        _LOGGER.debug("Frontend not loaded, the cards are served but not added")
        return
    version = (await async_get_integration(hass, DOMAIN)).version
    for card in CARD_FILES:
        add_extra_js_url(hass, f"{FRONTEND_URL}/{card}?v={version}")
