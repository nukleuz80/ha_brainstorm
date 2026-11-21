"""Texts for an AI mind map from a web page or a PDF.

A web address is loaded by Home Assistant and turned into plain text, a PDF,
from the address, an attachment or an upload, is read page by page. Only the
start of a long text goes to the AI. Addresses inside the own network are
refused, so the card cannot be used to read devices behind the router.
"""

from __future__ import annotations

import asyncio
import io
import ipaddress
import logging
import re
import socket
from html.parser import HTMLParser
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from yarl import URL

_LOGGER = logging.getLogger(__name__)

# More than any page or PDF a mind map is made from needs
MAX_DOWNLOAD = 8 * 1024 * 1024
FETCH_TIMEOUT = 20
MAX_REDIRECTS = 4
MAX_PDF_PAGES = 40
# Enough text for the AI, the rest of a long page is left out
MAX_SOURCE_TEXT = 12_000
HTML_TYPES = ("text/html", "application/xhtml+xml")
TEXT_TYPES = ("text/plain", "text/markdown")
PDF_TYPE = "application/pdf"
USER_AGENT = "Mozilla/5.0 (compatible; HomeAssistant-Brainstorm)"

ERR_SOURCE_BLOCKED = "source_blocked"
ERR_SOURCE_UNREACHABLE = "source_unreachable"
ERR_SOURCE_UNSUPPORTED = "source_unsupported"
ERR_SOURCE_TOO_LARGE = "source_too_large"
ERR_SOURCE_EMPTY = "source_empty"

_URL = re.compile(r"^https?://\S+$", re.IGNORECASE)
# Parts of a page that are not its content
_SKIPPED = frozenset(
    {
        "script",
        "style",
        "noscript",
        "svg",
        "template",
        "nav",
        "header",
        "footer",
        "aside",
        "form",
        "button",
        "select",
        "iframe",
    }
)
_BLOCKS = frozenset(
    {
        "p",
        "div",
        "section",
        "article",
        "main",
        "br",
        "li",
        "ul",
        "ol",
        "tr",
        "table",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "blockquote",
        "pre",
        "dt",
        "dd",
    }
)
_VOID = frozenset({"br", "img", "hr", "meta", "link", "input", "wbr", "source"})


class SourceError(HomeAssistantError):
    """A web page or PDF that gives no text, with the code the card shows."""

    def __init__(self, code: str, reason: str) -> None:
        """Remember why."""
        super().__init__(reason)
        self.code = code


def is_url(text: str) -> bool:
    """Tell whether the input is one web address and nothing else."""
    return bool(_URL.match((text or "").strip()))


def limit_text(text: str, limit: int = MAX_SOURCE_TEXT) -> str:
    """Return the text with tidy lines, shortened at a line or word."""
    lines = [" ".join(line.split()) for line in text.splitlines()]
    cleaned = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    if len(cleaned) <= limit:
        return cleaned
    cut = cleaned[:limit]
    end = max(cut.rfind("\n"), cut.rfind(" "))
    return cut[: end if end > limit // 2 else limit].rstrip()


class _PageText(HTMLParser):
    """Collect the visible text of a page, its title first."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.parts: list[str] = []
        self._skip: list[str] = []
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _VOID:
            if tag == "br":
                self.parts.append("\n")
            return
        if tag in _SKIPPED or self._skip:
            self._skip.append(tag)
            return
        if tag == "title":
            self._in_title = True
        if tag in _BLOCKS:
            self.parts.append("\n")
        if tag == "li":
            self.parts.append("- ")

    def handle_endtag(self, tag: str) -> None:
        if self._skip:
            if tag in self._skip:
                # Close up to the tag, as pages do not always close everything
                while self._skip and self._skip.pop() != tag:
                    pass
            return
        if tag == "title":
            self._in_title = False
        if tag in _BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip:
            return
        if self._in_title:
            self.title += data
            return
        self.parts.append(data)


def _first_line(text: str) -> str:
    """Return the first line, to leave out a title the text starts with."""
    return text.split("\n", 1)[0].strip()


def text_from_html(html: str) -> str:
    """Return the title and the readable text of a web page."""
    parser = _PageText()
    try:
        parser.feed(html)
        parser.close()
    except AssertionError:
        # A badly broken page still gives what was read so far
        pass
    title = " ".join(parser.title.split())
    body = limit_text("".join(parser.parts))
    if title and _first_line(body) != title:
        return f"{title}\n\n{body}".strip()
    return body


def text_from_pdf(data: bytes) -> str:
    """Return the text of a PDF; blocking, so it runs in the executor."""
    from pypdf import PdfReader  # noqa: PLC0415  # imported only when needed
    from pypdf.errors import PdfReadError  # noqa: PLC0415

    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted and not reader.decrypt(""):
            raise SourceError(ERR_SOURCE_UNSUPPORTED, "The PDF is locked")
        texts: list[str] = []
        title = ""
        if reader.metadata and reader.metadata.title:
            title = str(reader.metadata.title).strip()
        length = 0
        for page in reader.pages[:MAX_PDF_PAGES]:
            text = page.extract_text() or ""
            texts.append(text)
            length += len(text)
            if length > MAX_SOURCE_TEXT:
                break
    except SourceError:
        raise
    except (PdfReadError, ValueError, KeyError, TypeError, OSError) as err:
        raise SourceError(ERR_SOURCE_UNSUPPORTED, f"PDF not readable: {err}") from err
    body = limit_text("\n\n".join(texts))
    if title and body and _first_line(body) != title:
        body = f"{title}\n\n{body}"
    return body


async def async_text_from_pdf(hass: HomeAssistant, data: bytes) -> str:
    """Return the text of a PDF, read without blocking Home Assistant."""
    if len(data) > MAX_DOWNLOAD:
        raise SourceError(ERR_SOURCE_TOO_LARGE, "The PDF is too large")
    if not data.startswith(b"%PDF"):
        raise SourceError(ERR_SOURCE_UNSUPPORTED, "Not a PDF")
    text = await hass.async_add_executor_job(text_from_pdf, data)
    if not text.strip():
        # A scanned PDF has pictures of its pages but no text
        raise SourceError(ERR_SOURCE_EMPTY, "The PDF has no text")
    return text


async def async_resolve(hass: HomeAssistant, host: str) -> list[str]:
    """Return the addresses of a host name."""
    infos = await hass.loop.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    return [str(info[4][0]) for info in infos]


async def _async_check_host(hass: HomeAssistant, url: URL) -> None:
    """Refuse addresses that are not on the public internet."""
    host = url.raw_host or ""
    if not host or url.scheme not in ("http", "https"):
        raise SourceError(ERR_SOURCE_BLOCKED, "Only web addresses can be read")
    try:
        addresses = [str(ipaddress.ip_address(host.strip("[]")))]
    except ValueError:
        try:
            addresses = await async_resolve(hass, host)
        except (OSError, UnicodeError) as err:
            raise SourceError(ERR_SOURCE_UNREACHABLE, f"Unknown host {host}") from err
    if not addresses:
        raise SourceError(ERR_SOURCE_UNREACHABLE, f"Unknown host {host}")
    for address in addresses:
        if not ipaddress.ip_address(address.split("%", 1)[0]).is_global:
            raise SourceError(ERR_SOURCE_BLOCKED, f"{host} is inside the own network")


async def _async_read(response: Any) -> bytes:
    """Read a body, stopping once it is larger than allowed."""
    length = response.headers.get("Content-Length")
    if length and length.isdigit() and int(length) > MAX_DOWNLOAD:
        raise SourceError(ERR_SOURCE_TOO_LARGE, "The file is too large")
    data = bytearray()
    async for chunk in response.content.iter_chunked(64 * 1024):
        data.extend(chunk)
        if len(data) > MAX_DOWNLOAD:
            raise SourceError(ERR_SOURCE_TOO_LARGE, "The file is too large")
    return bytes(data)


def decode_page(data: bytes, content_type: str) -> str:
    """Return the text of a page in the charset it names."""
    charset = "utf-8"
    if match := re.search(r"charset=([\w.-]+)", content_type, re.IGNORECASE):
        charset = match.group(1)
    elif match := re.search(rb"<meta[^>]+charset=[\"']?([\w.-]+)", data[:4096], re.I):
        charset = match.group(1).decode("ascii", "ignore")
    try:
        return data.decode(charset, errors="replace")
    except LookupError:
        return data.decode("utf-8", errors="replace")


async def async_fetch(
    hass: HomeAssistant, address: str, accept: str = "text/html,application/pdf,*/*"
) -> tuple[str, bytes, str]:
    """Load a public web address, return its media type, body and Content-Type."""
    url = URL(address.strip())
    session = async_get_clientsession(hass)
    timeout = aiohttp.ClientTimeout(total=FETCH_TIMEOUT)
    headers = {"User-Agent": USER_AGENT, "Accept": accept}
    for _ in range(MAX_REDIRECTS + 1):
        # Every hop is checked, a public page must not lead into the own network
        await _async_check_host(hass, url)
        try:
            async with session.get(
                url, headers=headers, timeout=timeout, allow_redirects=False
            ) as response:
                if response.status in (301, 302, 303, 307, 308):
                    location = response.headers.get("Location")
                    if not location:
                        break
                    url = url.join(URL(location))
                    continue
                if response.status >= 400:
                    raise SourceError(
                        ERR_SOURCE_UNREACHABLE, f"The page answered {response.status}"
                    )
                content_type = str(response.headers.get("Content-Type") or "")
                kind = content_type.split(";", 1)[0].strip().lower()
                data = await _async_read(response)
        except (aiohttp.ClientError, TimeoutError, asyncio.TimeoutError) as err:
            raise SourceError(ERR_SOURCE_UNREACHABLE, f"Not loaded: {err}") from err
        return kind, data, content_type
    raise SourceError(ERR_SOURCE_UNREACHABLE, "Too many redirects")


def is_html(kind: str, data: bytes) -> bool:
    """Tell whether a loaded body is a web page."""
    return kind in HTML_TYPES or (not kind and b"<html" in data[:2048].lower())


async def async_text_from_url(hass: HomeAssistant, address: str) -> str:
    """Load a web page or PDF and return its text for the AI."""
    kind, data, content_type = await async_fetch(hass, address)
    if kind == PDF_TYPE or data.startswith(b"%PDF"):
        return await async_text_from_pdf(hass, data)
    if is_html(kind, data):
        text = text_from_html(decode_page(data, content_type))
    elif kind in TEXT_TYPES:
        text = limit_text(decode_page(data, content_type))
    else:
        raise SourceError(ERR_SOURCE_UNSUPPORTED, f"Cannot read {kind or 'this file'}")
    if not text.strip():
        raise SourceError(ERR_SOURCE_EMPTY, "The page has no text")
    return text
