"""Tests for the logos of the connected integrations in the settings."""

from __future__ import annotations

from io import BytesIO

from PIL import Image

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from custom_components.brainstorm.brand import BRANDS_CDN, _process, brand_strip

from .conftest import SetupEntry


def _png(colour: tuple[int, int, int, int] = (255, 0, 0, 255), size: int = 256) -> bytes:
    out = BytesIO()
    Image.new("RGBA", (size, size), colour).save(out, format="PNG")
    return out.getvalue()


def test_strip() -> None:
    """Test that every logo links to its coloured or grey image."""
    html = brand_strip([("bring", "Bring!", True, "an"), ("choreops", "ChoreOps", False, "aus")])
    assert 'src="/api/brainstorm/brand/bring/on.png"' in html
    assert 'src="/api/brainstorm/brand/choreops/off.png"' in html
    assert 'title="ChoreOps: aus"' in html
    assert brand_strip([]) == ""


def test_grey_logo() -> None:
    """Test that a switched off logo is small, grey and paler."""
    with Image.open(BytesIO(_process(_png(), active=False))) as image:
        assert image.size == (96, 96)
        red, green, blue, alpha = image.convert("RGBA").getpixel((10, 10))
    assert red == green == blue
    assert alpha < 128
    with Image.open(BytesIO(_process(_png(), active=True))) as image:
        assert image.convert("RGBA").getpixel((10, 10)) == (255, 0, 0, 255)


async def test_view(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client_no_auth: ClientSessionGenerator,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test serving the logos without a login, only for the known integrations."""
    aioclient_mock.get(f"{BRANDS_CDN}/bring/icon.png", content=_png())
    aioclient_mock.get(f"{BRANDS_CDN}/choreops/icon.png", status=404)
    await setup_entry(stored={"ideas": [], "categories": ["Inbox"]})
    client = await hass_client_no_auth()

    response = await client.get("/api/brainstorm/brand/bring/off.png")
    assert response.status == 200
    assert response.content_type == "image/png"
    with Image.open(BytesIO(await response.read())) as image:
        red, green, blue, _alpha = image.convert("RGBA").getpixel((5, 5))
    assert red == green == blue
    assert (await client.get("/api/brainstorm/brand/bring/on.png")).status == 200
    assert (await client.get("/api/brainstorm/brand/bring/off.png")).status == 200
    # The logo is fetched once and kept for both variants after that
    assert aioclient_mock.call_count == 2

    assert (await client.get("/api/brainstorm/brand/choreops/on.png")).status == 404
    assert (await client.get("/api/brainstorm/brand/hue/on.png")).status == 404
    assert (await client.get("/api/brainstorm/brand/bring/x.png")).status == 404
