"""Turn e-mails into notes.

The IMAP integration of Home Assistant fires `imap_content` for every new mail
in the watched folder. A mail from an allowed address becomes one note: its
subject is the text, its body the description, without quoted replies and the
signature. The mail can be marked as read afterwards, and a reply can be sent
through a notify action such as the one of SMTP.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_MAIL_CATEGORY,
    CONF_MAIL_ENABLED,
    CONF_MAIL_MARK_SEEN,
    CONF_MAIL_MATCH,
    CONF_MAIL_PREFIX,
    CONF_MAIL_REPLY_SERVICE,
    CONF_MAIL_SENDERS,
    IMAP_DOMAIN,
    MAIL_MATCH_ALL,
    MAIL_MATCH_ANYWHERE,
    MAIL_MATCH_SUBJECT,
    MAIL_MATCH_SUBJECT_START,
    SOURCE_MAIL,
)
from .messages import INVALID_DATA, MessageWatcher
from .messages import parse_senders as parse_sender_lines

if TYPE_CHECKING:
    from .store import BrainstormStore

_LOGGER = logging.getLogger(__name__)

EVENT_IMAP = "imap_content"
# The description keeps the start of a long mail
MAX_DESCRIPTION = 2000
# "Re:", "AW:", "Fwd:" and the like in front of a subject
_SUBJECT_TAGS = re.compile(r"^\s*((re|aw|fw|fwd|wg|sv|antw)\s*:\s*)+", re.IGNORECASE)
# Where the own text of a mail ends: the signature or a quoted earlier mail
_END_LINES = (
    re.compile(r"^--\s*$"),
    re.compile(r"^_{5,}\s*$"),
    re.compile(r"^-{3,}\s*(original|urspr\w{1,2}ngliche)", re.IGNORECASE),
    re.compile(r"^(am|on)\s.+(schrieb|wrote).*:\s*$", re.IGNORECASE),
    re.compile(r"^(von|from):\s", re.IGNORECASE),
    re.compile(r"^(gesendet von|sent from)\s", re.IGNORECASE),
)


def imap_available(hass: HomeAssistant) -> bool:
    """Tell whether the IMAP integration is set up."""
    return bool(hass.config_entries.async_entries(IMAP_DOMAIN))


def normalize_address(value: Any) -> str:
    """Return an e-mail address in lower case, "Jan <jan@x.de>" as "jan@x.de"."""
    raw = str(value or "").strip()
    if match := re.search(r"<([^>]+)>", raw):
        raw = match.group(1)
    return raw.strip().lower() if "@" in raw else ""


def parse_senders(text: str) -> tuple[dict[str, str], list[str]]:
    """Read lines like "jan@example.com = person.jan"."""
    return parse_sender_lines(text, normalize_address, 3)


def format_senders(senders: Mapping[str, str]) -> str:
    """Write the addresses back as lines for the settings."""
    return "\n".join(f"{address} = {person}" for address, person in senders.items())


def strip_keyword(text: str, keyword: str, start_only: bool) -> str | None:
    """Return a text without its keyword, None when the keyword is missing.

    "Notiz: Reifen" becomes "Reifen", "Reifen (Notiz)" with the keyword
    anywhere becomes "Reifen".
    """
    if not keyword:
        return text
    # Separators and brackets around the keyword go with it
    around = r"\s*[:\-,]?\s*"
    word = rf"[(\[]?{re.escape(keyword)}[)\]]?"
    start = "^" if start_only else ""
    pattern = re.compile(f"{start}{around}{word}{around}", re.IGNORECASE)
    if not pattern.search(text):
        return None
    return pattern.sub(" ", text, count=1).strip(" :,-")


def clean_subject(subject: str) -> str:
    """Return a subject without "Re:" or "Fwd:" in front."""
    return _SUBJECT_TAGS.sub("", subject or "").strip()


def clean_body(text: str) -> str:
    """Return the own text of a mail, without signature and quoted mails."""
    lines: list[str] = []
    for line in (text or "").replace("\r\n", "\n").split("\n"):
        stripped = line.strip()
        if any(pattern.match(stripped) for pattern in _END_LINES):
            break
        if stripped.startswith(">"):
            continue
        lines.append(line.rstrip())
    body = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    if len(body) > MAX_DESCRIPTION:
        body = body[:MAX_DESCRIPTION].rstrip() + " …"
    return body


class MailWatcher(MessageWatcher):
    """Add the mails of known addresses as notes."""

    source = SOURCE_MAIL
    name = "Mail"

    def __init__(
        self, hass: HomeAssistant, store: BrainstormStore, options: dict[str, Any]
    ) -> None:
        """Remember the settings."""
        super().__init__(
            hass,
            store,
            enabled=bool(options.get(CONF_MAIL_ENABLED)),
            senders=options.get(CONF_MAIL_SENDERS) or {},
            category=options.get(CONF_MAIL_CATEGORY),
            prefix=str(options.get(CONF_MAIL_PREFIX) or ""),
            reply=bool(str(options.get(CONF_MAIL_REPLY_SERVICE) or "").strip()),
        )
        self.mark_seen = bool(options.get(CONF_MAIL_MARK_SEEN, True))
        self.match = str(options.get(CONF_MAIL_MATCH) or MAIL_MATCH_SUBJECT_START)
        self.reply_service = str(options.get(CONF_MAIL_REPLY_SERVICE) or "").strip()

    def events(self) -> list[str]:
        """Return the event of new mails."""
        return [EVENT_IMAP]

    def normalize(self, sender: Any) -> str:
        """Compare addresses in lower case."""
        return normalize_address(sender)

    def senders_of(self, data: Mapping[str, Any]) -> list[str]:
        """Return the address of the sender."""
        sender = str(data.get("sender") or "")
        return [sender] if sender else []

    def text_of(self, data: Mapping[str, Any]) -> tuple[str, bool]:
        """Return the subject, the body is read on its own."""
        return clean_subject(str(data.get("subject") or "")), False

    def is_own(self, data: Mapping[str, Any]) -> bool:
        """Leave out a mail seen before, which IMAP reports again."""
        return data.get("initial") is False

    async def async_notes(
        self, data: Mapping[str, Any]
    ) -> list[tuple[str, str | None]]:
        """Return one note: the subject with the body as description.

        Which mails count is chosen in the settings: the keyword at the start
        of the subject, anywhere in the subject, anywhere in the mail, or every
        mail of the allowed addresses.
        """
        subject, _ = self.text_of(data)
        keyword = "" if self.match == MAIL_MATCH_ALL else self.prefix
        found = True
        if self.match in (MAIL_MATCH_SUBJECT_START, MAIL_MATCH_SUBJECT):
            stripped = strip_keyword(
                subject, keyword, self.match == MAIL_MATCH_SUBJECT_START
            )
            if stripped is None:
                # The body is not even read for a mail that does not count
                return []
            subject = stripped
        raw_body = await self._async_body(data)
        body = clean_body(raw_body)
        if self.match == MAIL_MATCH_ANYWHERE and keyword:
            stripped = strip_keyword(subject, keyword, False)
            if stripped is not None:
                subject = stripped
            else:
                found = keyword.casefold() in raw_body.casefold()
        if not found:
            return []
        if not subject and body:
            # Without a subject the first line of the body is the note
            subject, _, body = body.partition("\n")
            subject, body = subject.strip(), body.strip()
        texts = self.note_texts(subject, command=True)
        if not texts:
            return []
        return [(" ".join(texts), body or None)]

    async def _async_body(self, data: Mapping[str, Any]) -> str:
        """Return the text of the mail, fetched when the event has none."""
        if isinstance(data.get("text"), str):
            return str(data["text"])
        entry, uid = data.get("entry_id"), data.get("uid")
        if (
            not entry
            or not uid
            or not self.hass.services.has_service(IMAP_DOMAIN, "fetch")
        ):
            return ""
        try:
            response = await self.hass.services.async_call(
                IMAP_DOMAIN,
                "fetch",
                {"entry": entry, "uid": str(uid)},
                blocking=True,
                return_response=True,
            )
        except (HomeAssistantError, ValueError, *INVALID_DATA) as err:
            _LOGGER.warning("Text of the mail %s not read: %s", uid, err)
            return ""
        return str((response or {}).get("text") or "")

    async def async_after_notes(self, data: Mapping[str, Any]) -> None:
        """Mark the mail as read, so it is not left as a new one."""
        entry, uid = data.get("entry_id"), data.get("uid")
        if self.mark_seen and entry and uid:
            await self.async_call_reply(
                f"{IMAP_DOMAIN}.seen", {"entry": entry, "uid": str(uid)}
            )

    async def async_send_reply(self, data: Mapping[str, Any], message: str) -> None:
        """Answer through a notify action, such as the one of SMTP."""
        service_data: dict[str, Any] = {"message": message, "title": "Brainstorm"}
        if sender := normalize_address(data.get("sender")):
            service_data["target"] = [sender]
        await self.async_call_reply(self.reply_service, service_data)
