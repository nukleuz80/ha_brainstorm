"""Show the logos of the integrations Brainstorm works together with.

The settings menu shows a logo for every connected integration, in colour
while it is switched on and grey while it is off. Menu entries are plain
text, but the description above them is Markdown, so the logos are small
images served from here: the brand image a custom integration brings in
its own folder, or the one of the Home Assistant brands service.
"""

from __future__ import annotations

from io import BytesIO
import logging
from pathlib import Path

from aiohttp import ClientError, ClientTimeout, web

from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import IntegrationNotFound, async_get_integration

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

BRAND_URL = f"/api/{DOMAIN}/brand"
BRANDS_CDN = "https://brands.home-assistant.io"
# Only the logos of the integrations Brainstorm connects to are served
BRAND_DOMAINS = frozenset({"bring", "choreops"})
BRAND_SIZE = 96
DATA_BRAND_CACHE = f"{DOMAIN}_brand_cache"
FETCH_TIMEOUT = ClientTimeout(total=10)


def brand_url(domain: str, active: bool) -> str:
    """Return the address of the logo of an integration, coloured or grey."""
    return f"{BRAND_URL}/{domain}/{'on' if active else 'off'}.png"


def brand_strip(items: list[tuple[str, str, bool, str]], size: int = 32) -> str:
    """Return the logos as HTML for a Markdown description.

    Every item is the domain, the name, whether it is switched on, and the
    word for its state, which the logo shows when hovered.
    """
    return " ".join(
        f'<img src="{brand_url(domain, active)}" alt="{name}" '
        f'title="{name}: {state}" width="{size}" height="{size}">'
        for domain, name, active, state in items
    )


def _read_file(path: Path) -> bytes | None:
    try:
        return path.read_bytes()
    except OSError:
        return None


def _process(data: bytes, active: bool) -> bytes:
    """Scale a logo down and, for a switched off integration, make it grey."""
    from PIL import Image  # noqa: PLC0415 - only needed for the logos

    with Image.open(BytesIO(data)) as source:
        image = source.convert("RGBA")
    image.thumbnail((BRAND_SIZE, BRAND_SIZE))
    if not active:
        alpha = image.getchannel("A").point(lambda value: value * 45 // 100)
        image = image.convert("L").convert("RGBA")
        image.putalpha(alpha)
    out = BytesIO()
    image.save(out, format="PNG", optimize=True)
    return out.getvalue()


async def _async_source(hass: HomeAssistant, domain: str) -> bytes | None:
    """Return the brand image of an integration, from its folder or the brands service."""
    try:
        integration = await async_get_integration(hass, domain)
    except IntegrationNotFound:
        integration = None
    if integration is not None and not integration.is_built_in:
        data = await hass.async_add_executor_job(
            _read_file, Path(integration.file_path) / "brand" / "icon.png"
        )
        if data is not None:
            return data
    try:
        response = await async_get_clientsession(hass).get(
            f"{BRANDS_CDN}/{domain}/icon.png", timeout=FETCH_TIMEOUT
        )
        if response.status != 200:
            _LOGGER.debug("No logo for %s on the brands service (%s)", domain, response.status)
            return None
        return await response.read()
    except (ClientError, TimeoutError) as err:
        _LOGGER.debug("Could not fetch the logo of %s: %s", domain, err)
        return None


async def async_brand_image(hass: HomeAssistant, domain: str, active: bool) -> bytes | None:
    """Return the processed logo, kept in memory after the first time."""
    cache: dict[tuple[str, bool], bytes] = hass.data.setdefault(DATA_BRAND_CACHE, {})
    if (domain, active) in cache:
        return cache[(domain, active)]
    source = await _async_source(hass, domain)
    if source is None:
        return None
    try:
        image = await hass.async_add_executor_job(_process, source, active)
    except (OSError, ValueError) as err:
        _LOGGER.debug("The logo of %s is not a readable image: %s", domain, err)
        return None
    cache[(domain, active)] = image
    return image


class BrandView(HomeAssistantView):
    """Serve the logos of the connected integrations.

    Images in the settings menu are loaded by the browser without a token,
    so the view needs no login; it only serves the public logos of a fixed
    list of integrations.
    """

    url = BRAND_URL + "/{domain}/{variant}"
    name = f"api:{DOMAIN}:brand"
    requires_auth = False

    def __init__(self, hass: HomeAssistant) -> None:
        """Remember Home Assistant."""
        self.hass = hass

    async def get(self, request: web.Request, domain: str, variant: str) -> web.Response:
        """Return the coloured or grey logo of an integration."""
        if domain not in BRAND_DOMAINS or variant not in ("on.png", "off.png"):
            return web.Response(status=404)
        data = await async_brand_image(self.hass, domain, variant == "on.png")
        if data is None:
            return web.Response(status=404)
        return web.Response(
            body=data,
            content_type="image/png",
            headers={"Cache-Control": "public, max-age=86400"},
        )
