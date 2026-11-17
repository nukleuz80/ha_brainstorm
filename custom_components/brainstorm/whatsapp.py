"""Turn WhatsApp messages into notes.

A WhatsApp bridge, such as the integration ha-whatsapp, fires an event for
every message it receives. The event and its fields can be set, so other
bridges work as well: the text and the sender are looked for in the usual
fields when none are given.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant

from .const import (
    CONF_WHATSAPP_CATEGORY,
    CONF_WHATSAPP_ENABLED,
    CONF_WHATSAPP_EVENT,
    CONF_WHATSAPP_PREFIX,
    CONF_WHATSAPP_REPLY,
    CONF_WHATSAPP_REPLY_SERVICE,
    CONF_WHATSAPP_SENDER_FIELD,
    CONF_WHATSAPP_SENDERS,
    CONF_WHATSAPP_TEXT_FIELD,
    DEFAULT_WHATSAPP_EVENT,
    DEFAULT_WHATSAPP_REPLY_SERVICE,
    SOURCE_WHATSAPP,
)
from .messages import (
    MessageWatcher,
    field_value,
    first_text,
    resolve_person,
)
from .messages import (
    parse_senders as parse_sender_lines,
)

if TYPE_CHECKING:
    from .store import BrainstormStore

__all__ = [
    "WhatsAppWatcher",
    "field_value",
    "format_senders",
    "normalize_number",
    "parse_senders",
    "resolve_person",
    "same_number",
]

# Where the bridges put the text and the sender, the first one found is used
TEXT_FIELDS = (
    "content",
    "body",
    "text",
    "message",
    "message.text",
    "message.body",
    "data.body",
    "data.text",
)
SENDER_FIELDS = (
    "from",
    "sender",
    "phone",
    "number",
    "chat_id",
    "chatId",
    "jid",
    "message.from",
    "data.from",
)
# Set by the bridges for a message sent from the own number, such as a reply
OWN_FIELDS = ("fromMe", "from_me", "is_from_me", "self")
# A number needs this many digits to be compared by its end
MIN_DIGITS = 6


def normalize_number(value: Any) -> str:
    """Return the digits of a phone number, without "@c.us", "+" or "00"."""
    raw = str(value or "").split("@", 1)[0]
    digits = re.sub(r"\D", "", raw)
    return digits.removeprefix("00")


def same_number(first: str, second: str) -> bool:
    """Tell whether two numbers are the same, one perhaps without country code.

    "01711234567" and "491711234567" match, as the national form only lacks
    the country code in front of the leading zero.
    """
    if not first or not second:
        return False
    if first == second:
        return True
    short, long_ = sorted((first.lstrip("0"), second.lstrip("0")), key=len)
    return len(short) >= MIN_DIGITS and long_.endswith(short)


def parse_senders(text: str) -> tuple[dict[str, str], list[str]]:
    """Read lines like "+49 171 1234567 = person.jan"."""
    return parse_sender_lines(text, normalize_number, MIN_DIGITS)


def format_senders(senders: Mapping[str, str]) -> str:
    """Write the numbers back as lines for the settings."""
    return "\n".join(f"+{number} = {person}" for number, person in senders.items())


class WhatsAppWatcher(MessageWatcher):
    """Add the WhatsApp messages of known numbers as notes."""

    source = SOURCE_WHATSAPP
    name = "WhatsApp"

    def __init__(
        self, hass: HomeAssistant, store: BrainstormStore, options: dict[str, Any]
    ) -> None:
        """Remember the settings."""
        super().__init__(
            hass,
            store,
            enabled=bool(options.get(CONF_WHATSAPP_ENABLED)),
            senders=options.get(CONF_WHATSAPP_SENDERS) or {},
            category=options.get(CONF_WHATSAPP_CATEGORY),
            prefix=str(options.get(CONF_WHATSAPP_PREFIX) or ""),
            reply=bool(options.get(CONF_WHATSAPP_REPLY, True)),
        )
        self.event = (
            str(options.get(CONF_WHATSAPP_EVENT) or "").strip()
            or DEFAULT_WHATSAPP_EVENT
        )
        self.text_field = str(options.get(CONF_WHATSAPP_TEXT_FIELD) or "").strip()
        self.sender_field = str(options.get(CONF_WHATSAPP_SENDER_FIELD) or "").strip()
        self.reply_service = (
            str(options.get(CONF_WHATSAPP_REPLY_SERVICE) or "").strip()
            or DEFAULT_WHATSAPP_REPLY_SERVICE
        )

    def events(self) -> list[str]:
        """Return the event of the bridge."""
        return [self.event]

    def normalize(self, sender: Any) -> str:
        """Compare numbers by their digits."""
        return normalize_number(sender)

    def same_sender(self, sender: str, known: str) -> bool:
        """Match a number also without its country code."""
        return same_number(sender, known)

    def senders_of(self, data: Mapping[str, Any]) -> list[str]:
        """Return the number of the sender."""
        sender = first_text(data, self.sender_field, SENDER_FIELDS)
        return [sender] if sender else []

    def text_of(self, data: Mapping[str, Any]) -> tuple[str, bool]:
        """Return the text of the message."""
        return first_text(data, self.text_field, TEXT_FIELDS), False

    def is_own(self, data: Mapping[str, Any]) -> bool:
        """Leave out what the own number sent, such as the reply."""
        return any(data.get(field) is True for field in OWN_FIELDS)

    async def async_send_reply(self, data: Mapping[str, Any], message: str) -> None:
        """Answer through the action of the bridge."""
        target = first_text(data, self.sender_field, SENDER_FIELDS)
        await self.async_call_reply(
            self.reply_service, {"target": target, "message": message}
        )
