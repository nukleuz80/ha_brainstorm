"""Files attached to ideas: upload, download and cleanup."""
from __future__ import annotations

from datetime import datetime, timedelta
from http import HTTPStatus
import logging
from typing import Any
from urllib.parse import quote, unquote

from aiohttp import BodyPartReader, web

from homeassistant.components.http import KEY_HASS_USER, HomeAssistantView
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.event import async_call_later, async_track_time_interval
from homeassistant.helpers.http import KEY_HASS

from .const import ATTACHMENT_MAX_SIZE, ATTR_ATTACHMENTS, ATTR_ID, DOMAIN
from .store import BrainstormStore, attachment_name, get_loaded_store

_LOGGER = logging.getLogger(__name__)

URL_BASE = "/api/brainstorm/attachments"
CLEANUP_INTERVAL = timedelta(hours=6)
# Give the start of Home Assistant some room before touching the disk
CLEANUP_FIRST_DELAY = 120
# Images and PDFs open in the browser, everything else is downloaded
INLINE_TYPES = ("image/png", "image/jpeg", "image/gif", "image/webp", "application/pdf")


@callback
def async_register_views(hass: HomeAssistant) -> None:
    """Register the attachment endpoints once per run."""
    hass.http.register_view(AttachmentUploadView())
    hass.http.register_view(AttachmentView())


def _store_or_error(hass: HomeAssistant) -> BrainstormStore:
    """Return the loaded store, or answer that Brainstorm is not running."""
    store = get_loaded_store(hass)
    if store is None:
        raise web.HTTPServiceUnavailable(text="Brainstorm is not loaded")
    return store


def _user_id(request: web.Request) -> str | None:
    """Return the ID of the person who sent the request."""
    user = request.get(KEY_HASS_USER)
    return user.id if user is not None else None


def _error(err: HomeAssistantError) -> web.Response:
    """Answer with the translated message of an error."""
    status = (
        HTTPStatus.BAD_REQUEST
        if isinstance(err, ServiceValidationError)
        else HTTPStatus.INTERNAL_SERVER_ERROR
    )
    return web.json_response(
        {"message": str(err), "code": err.translation_key}, status=status
    )


class AttachmentUploadView(HomeAssistantView):
    """Add files to an idea."""

    url = URL_BASE + "/{idea_id}"
    name = "api:brainstorm:attachments"
    requires_auth = True

    async def post(self, request: web.Request, idea_id: str) -> web.Response:
        """Store every file of a multipart upload with the idea."""
        hass: HomeAssistant = request.app[KEY_HASS]
        store = _store_or_error(hass)
        user_id = _user_id(request)
        idea = store.get_idea(idea_id)
        if idea is None or not store.can_access(idea, user_id):
            raise web.HTTPNotFound
        if not store.can_edit(idea, user_id):
            raise web.HTTPForbidden

        try:
            reader = await request.multipart()
        except (AssertionError, ValueError) as err:
            raise web.HTTPBadRequest(text="Expected a multipart upload") from err
        added: list[dict[str, Any]] = []
        while (part := await reader.next()) is not None:
            if not isinstance(part, BodyPartReader) or not part.filename:
                continue
            try:
                data = await _read_limited(part)
                added.append(
                    await store.async_add_attachment(
                        # Browsers and aiohttp percent-encode quotes in names
                        idea_id, unquote(part.filename), data, user_id=user_id
                    )
                )
            except HomeAssistantError as err:
                # Files stored before the failing one stay with the idea
                if added:
                    _LOGGER.debug("Upload stopped after %d files: %s", len(added), err)
                return _error(err)
        if not added:
            raise web.HTTPBadRequest(text="No file in the upload")
        idea = store.get_idea(idea_id) or {}
        return web.json_response(
            {"added": added, "attachments": idea.get(ATTR_ATTACHMENTS) or []}
        )


async def _read_limited(part: BodyPartReader) -> bytes:
    """Read one file, but stop as soon as it is too large."""
    chunks: list[bytes] = []
    size = 0
    while chunk := await part.read_chunk(256 * 1024):
        size += len(chunk)
        if size > ATTACHMENT_MAX_SIZE:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="attachment_too_large",
                translation_placeholders={
                    "name": attachment_name(part.filename or ""),
                    "max": str(ATTACHMENT_MAX_SIZE // (1024 * 1024)),
                },
            )
        chunks.append(chunk)
    return b"".join(chunks)


class AttachmentView(HomeAssistantView):
    """Show or delete one attachment."""

    url = URL_BASE + "/{idea_id}/{attachment_id}"
    name = "api:brainstorm:attachment"
    requires_auth = True

    async def get(
        self, request: web.Request, idea_id: str, attachment_id: str
    ) -> web.StreamResponse:
        """Send the file to people who may see the idea."""
        hass: HomeAssistant = request.app[KEY_HASS]
        store = _store_or_error(hass)
        idea = store.get_idea(idea_id)
        if idea is None or not store.can_access(idea, _user_id(request)):
            raise web.HTTPNotFound
        entry = next(
            (
                a
                for a in idea.get(ATTR_ATTACHMENTS) or []
                if a.get(ATTR_ID) == attachment_id
            ),
            None,
        )
        path = store.attachment_file(idea_id, attachment_id)
        if entry is None or path is None:
            raise web.HTTPNotFound
        if not await hass.async_add_executor_job(path.is_file):
            raise web.HTTPNotFound
        content_type = str(entry.get("type") or "application/octet-stream")
        disposition = "inline" if content_type in INLINE_TYPES else "attachment"
        name = str(entry.get("name") or "file")
        return web.FileResponse(
            path,
            headers={
                "Content-Type": content_type,
                "Content-Disposition": f"{disposition}; filename*=UTF-8''{quote(name)}",
                "X-Content-Type-Options": "nosniff",
                "Content-Security-Policy": "sandbox",
                "Cache-Control": "private, max-age=3600",
            },
        )

    async def delete(
        self, request: web.Request, idea_id: str, attachment_id: str
    ) -> web.Response:
        """Remove an attachment for people who may edit the idea."""
        hass: HomeAssistant = request.app[KEY_HASS]
        store = _store_or_error(hass)
        user_id = _user_id(request)
        idea = store.get_idea(idea_id)
        if idea is None or not store.can_access(idea, user_id):
            raise web.HTTPNotFound
        if not store.can_edit(idea, user_id):
            raise web.HTTPForbidden
        if not await store.async_remove_attachment(idea_id, attachment_id):
            raise web.HTTPNotFound
        idea = store.get_idea(idea_id) or {}
        return web.json_response({"attachments": idea.get(ATTR_ATTACHMENTS) or []})


class AttachmentCleaner:
    """Delete the attachments of ideas that are done for a while."""

    def __init__(self, hass: HomeAssistant, store: BrainstormStore) -> None:
        """Initialize the cleaner."""
        self.hass = hass
        self.store = store
        self._unsubs: list[CALLBACK_TYPE] = []

    @callback
    def async_start(self) -> None:
        """Clean up shortly after the start and then every few hours."""
        self._unsubs.append(
            async_call_later(self.hass, CLEANUP_FIRST_DELAY, self._async_run)
        )
        self._unsubs.append(
            async_track_time_interval(self.hass, self._async_run, CLEANUP_INTERVAL)
        )

    @callback
    def async_stop(self) -> None:
        """Stop the timers."""
        while self._unsubs:
            self._unsubs.pop()()

    async def _async_run(self, _now: datetime) -> None:
        """Run one cleanup; a failure waits for the next round."""
        try:
            await self.store.async_cleanup_attachments()
        except (OSError, HomeAssistantError) as err:
            _LOGGER.warning("Cleaning up Brainstorm attachments failed: %s", err)

