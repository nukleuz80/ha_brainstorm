"""Tests for mind maps the AI makes from a web page or a PDF."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import aiohttp
import pytest
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker
from pytest_homeassistant_custom_component.typing import (
    ClientSessionGenerator,
    WebSocketGenerator,
)

from custom_components.brainstorm import map_sources
from custom_components.brainstorm.map_sources import (
    SourceError,
    async_text_from_url,
    is_url,
    limit_text,
    text_from_html,
    text_from_pdf,
)

from .conftest import SetupEntry

AI_OPTIONS = {"ai_entity": "ai_task.test"}
PAGE = """<!doctype html><html><head><title>Sommerfest planen</title>
<style>body {color: red}</style><script>alert("x")</script></head>
<body><nav>Menü Start Kontakt</nav><header>Logo</header>
<main><h1>Sommerfest</h1><p>Essen &amp; Trinken für alle.</p>
<ul><li>Grill</li><li>Salate</li></ul></main>
<footer>Impressum</footer></body></html>"""


def make_pdf(lines: list[str], title: str | None = None) -> bytes:
    """Return a small PDF with one page of text, as an office program writes it."""
    content = "BT /F1 12 Tf 72 720 Td 14 TL " + " ".join(
        f"({line}) Tj T*" for line in lines
    )
    content += " ET"
    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        f"<< /Length {len(content)} >>\nstream\n{content}\nendstream",
    ]
    if title:
        objects.append(f"<< /Title ({title}) >>")
    out = b"%PDF-1.4\n"
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n{body}\nendobj\n".encode("latin-1")
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    info = f" /Info {len(objects)} 0 R" if title else ""
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R{info} >>\n"
        f"startxref\n{xref}\n%%EOF\n"
    ).encode()
    return out


def _register_ai(hass: HomeAssistant, answer: str) -> list[ServiceCall]:
    calls: list[ServiceCall] = []

    async def generate(call: ServiceCall) -> ServiceResponse:
        calls.append(call)
        return {"data": answer}

    hass.services.async_register(
        "ai_task", "generate_data", generate, supports_response=SupportsResponse.ONLY
    )
    return calls


@pytest.fixture
def public_dns() -> Any:
    """Every host name is a public address, without asking a real DNS."""
    with patch.object(
        map_sources, "async_resolve", return_value=["93.184.216.34"]
    ) as resolve:
        yield resolve


def test_page_text_without_menus_and_scripts() -> None:
    """Title first, content kept, navigation, styles and scripts left out."""
    text = text_from_html(PAGE)
    assert text.splitlines()[0] == "Sommerfest planen"
    assert "Essen & Trinken für alle." in text
    assert "- Grill" in text
    for gone in ("Menü", "Logo", "Impressum", "alert", "color"):
        assert gone not in text
    assert is_url(" https://example.com/a?b=1 ")
    assert not is_url("Sommerfest https://example.com")
    assert len(limit_text("wort " * 5000, 100)) <= 100


def test_pdf_text() -> None:
    """The text of the pages, the title of the document first."""
    text = text_from_pdf(make_pdf(["Umzug planen", "Kartons kaufen"], "Umzug"))
    assert text.splitlines()[0] == "Umzug"
    assert "Kartons kaufen" in text
    with pytest.raises(SourceError) as err:
        text_from_pdf(b"%PDF-1.4 kaputt")
    assert err.value.code == "source_unsupported"


async def test_page_from_the_web(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, public_dns: Any
) -> None:
    """A page is loaded, also behind a redirect, its charset respected."""
    aioclient_mock.get(
        "https://example.com/alt",
        status=301,
        headers={"Location": "/fest"},
    )
    aioclient_mock.get(
        "https://example.com/fest",
        content=PAGE.encode("iso-8859-1", "replace"),
        headers={"Content-Type": "text/html; charset=iso-8859-1"},
    )
    text = await async_text_from_url(hass, "https://example.com/alt")
    assert "Menü" not in text
    assert "Essen & Trinken für alle." in text


async def test_pdf_from_the_web(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, public_dns: Any
) -> None:
    """A PDF address is read like an uploaded PDF."""
    aioclient_mock.get(
        "https://example.com/plan.pdf",
        content=make_pdf(["Garten anlegen"]),
        headers={"Content-Type": "application/pdf"},
    )
    assert "Garten anlegen" in await async_text_from_url(
        hass, "https://example.com/plan.pdf"
    )


@pytest.mark.parametrize(
    ("address", "resolved", "code"),
    [
        ("http://192.168.0.73:8123/api/states", None, "source_blocked"),
        ("http://[::1]/", None, "source_blocked"),
        ("http://homeassistant.local/", ["10.0.0.5"], "source_blocked"),
        ("ftp://example.com/x", None, "source_blocked"),
    ],
)
async def test_own_network_is_refused(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    address: str,
    resolved: list[str] | None,
    code: str,
) -> None:
    """The card cannot read devices or Home Assistant itself."""
    with patch.object(map_sources, "async_resolve", return_value=resolved or []):
        with pytest.raises(SourceError) as err:
            await async_text_from_url(hass, address)
    assert err.value.code == code
    assert aioclient_mock.call_count == 0


async def test_redirect_into_the_own_network_is_refused(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """A public page cannot lead on to an address behind the router."""
    aioclient_mock.get(
        "https://example.com/weiter",
        status=302,
        headers={"Location": "http://intern.example/"},
    )

    async def resolve(hass: HomeAssistant, host: str) -> list[str]:
        return ["93.184.216.34"] if host == "example.com" else ["192.168.1.2"]

    with patch.object(map_sources, "async_resolve", side_effect=resolve):
        with pytest.raises(SourceError) as err:
            await async_text_from_url(hass, "https://example.com/weiter")
    assert err.value.code == "source_blocked"


@pytest.mark.parametrize(
    ("kwargs", "code"),
    [
        ({"status": 404}, "source_unreachable"),
        ({"exc": aiohttp.ClientError()}, "source_unreachable"),
        (
            {"content": b"\x89PNG", "headers": {"Content-Type": "image/png"}},
            "source_unsupported",
        ),
        (
            {
                "text": "<html><body><script>x</script></body></html>",
                "headers": {"Content-Type": "text/html"},
            },
            "source_empty",
        ),
        (
            {
                "content": b"x" * 10,
                "headers": {"Content-Length": str(20 * 1024 * 1024)},
            },
            "source_too_large",
        ),
    ],
)
async def test_pages_that_give_no_text(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    public_dns: Any,
    kwargs: dict[str, Any],
    code: str,
) -> None:
    """Each problem has its own code, which the card explains."""
    aioclient_mock.get("https://example.com/x", **kwargs)
    with pytest.raises(SourceError) as err:
        await async_text_from_url(hass, "https://example.com/x")
    assert err.value.code == code


async def test_websocket_map_from_a_page_and_an_attachment(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_ws_client: WebSocketGenerator,
    aioclient_mock: AiohttpClientMocker,
    public_dns: Any,
) -> None:
    """The page text goes into the prompt, a PDF attachment as well."""
    assert await async_setup_component(hass, "websocket_api", {})
    calls = _register_ai(hass, "Sommerfest\n  - Grill")
    entry = await setup_entry(options=AI_OPTIONS)
    store = entry.runtime_data
    aioclient_mock.get(
        "https://example.com/fest",
        text=PAGE,
        headers={"Content-Type": "text/html"},
    )
    client = await hass_ws_client(hass)
    await client.send_json_auto_id(
        {"type": "brainstorm/generate_map", "text": "https://example.com/fest"}
    )
    reply = await client.receive_json()
    assert reply["result"]["nodes"][1] == {"text": "Grill", "depth": 1}
    assert "Essen & Trinken" in calls[0].data["instructions"]

    idea = await store.async_add_idea("Umzug")
    attachment = await store.async_add_attachment(
        idea["id"], "plan.pdf", make_pdf(["Kartons packen"])
    )
    await client.send_json_auto_id(
        {
            "type": "brainstorm/generate_map",
            "idea_id": idea["id"],
            "attachment_id": attachment["id"],
        }
    )
    assert "result" in await client.receive_json()
    assert "Kartons packen" in calls[1].data["instructions"]

    await client.send_json_auto_id(
        {
            "type": "brainstorm/generate_map",
            "idea_id": idea["id"],
            "attachment_id": "gibtsnicht",
        }
    )
    assert (await client.receive_json())["error"]["code"] == "source_unreachable"
    await client.send_json_auto_id(
        {"type": "brainstorm/generate_map", "text": "http://192.168.0.1/"}
    )
    assert (await client.receive_json())["error"]["code"] == "source_blocked"
    await client.send_json_auto_id({"type": "brainstorm/generate_map", "text": " "})
    assert not (await client.receive_json())["success"]
    assert len(calls) == 2


async def test_uploaded_pdf(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client: ClientSessionGenerator,
) -> None:
    """An uploaded PDF becomes a map, a scanned one explains why not."""
    assert await async_setup_component(hass, "http", {})
    calls = _register_ai(hass, "Garten\n  - Beete")
    await setup_entry(options=AI_OPTIONS)
    client = await hass_client()

    form = aiohttp.FormData()
    form.add_field("language", "en")
    form.add_field("file", make_pdf(["Hochbeet bauen"]), filename="garten.pdf")
    response = await client.post("/api/brainstorm/map_source", data=form)
    assert response.status == 200
    assert (await response.json())["nodes"][0] == {"text": "Garten", "depth": 0}
    assert "Hochbeet bauen" in calls[0].data["instructions"]
    assert "Input:" in calls[0].data["instructions"]

    form = aiohttp.FormData()
    form.add_field("file", make_pdf([]), filename="scan.pdf")
    response = await client.post("/api/brainstorm/map_source", data=form)
    assert response.status == 400
    assert (await response.json())["code"] == "source_empty"

    form = aiohttp.FormData()
    form.add_field("file", b"kein pdf", filename="x.pdf")
    response = await client.post("/api/brainstorm/map_source", data=form)
    assert (await response.json())["code"] == "source_unsupported"


async def test_upload_without_ai(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    hass_client: ClientSessionGenerator,
) -> None:
    """Without an AI entity the card is told to pick one first."""
    assert await async_setup_component(hass, "http", {})
    await setup_entry()
    client = await hass_client()
    form = aiohttp.FormData()
    form.add_field("file", make_pdf(["x"]), filename="x.pdf")
    response = await client.post("/api/brainstorm/map_source", data=form)
    assert (await response.json())["code"] == "ai_not_configured"
