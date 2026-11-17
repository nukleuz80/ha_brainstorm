"""Turn Telegram messages into notes.

The Telegram bot integration of Home Assistant fires `telegram_text` for every
message and `telegram_command` for a command. Every line of a message from an
allowed Telegram user, or a command like "/note milk", becomes a note of the
person the user belongs to. The bot answers in the same chat.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant

from .const import (
    CONF_TELEGRAM_CATEGORY,
    CONF_TELEGRAM_ENABLED,
    CONF_TELEGRAM_PREFIX,
    CONF_TELEGRAM_REPLY,
    CONF_TELEGRAM_SENDERS,
    SOURCE_TELEGRAM,
    TELEGRAM_DOMAIN,
)
from .messages import MessageWatcher
from .messages import parse_senders as parse_sender_lines

if TYPE_CHECKING:
    from .store import BrainstormStore

EVENT_TEXT = "telegram_text"
EVENT_COMMAND = "telegram_command"
# Commands that add a note, "/note@my_bot" included
COMMANDS = frozenset({"/notiz", "/note", "/idee", "/idea"})
# Telegram ids have at least this many digits
MIN_DIGITS = 5


def telegram_available(hass: HomeAssistant) -> bool:
    """Tell whether the Telegram bot integration is set up."""
    return bool(hass.config_entries.async_entries(TELEGRAM_DOMAIN))


def normalize_id(value: Any) -> str:
    """Return a Telegram id as digits, a group keeping its minus."""
    raw = str(value or "").strip()
    digits = re.sub(r"\D", "", raw)
    return f"-{digits}" if digits and raw.startswith("-") else digits


def parse_senders(text: str) -> tuple[dict[str, str], list[str]]:
    """Read lines like "123456789 = person.jan"."""
    return parse_sender_lines(text, normalize_id, MIN_DIGITS)


def format_senders(senders: Mapping[str, str]) -> str:
    """Write the ids back as lines for the settings."""
    return "\n".join(f"{sender} = {person}" for sender, person in senders.items())


class TelegramWatcher(MessageWatcher):
    """Add the Telegram messages of known users as notes."""

    source = SOURCE_TELEGRAM
    name = "Telegram"

    def __init__(
        self, hass: HomeAssistant, store: BrainstormStore, options: dict[str, Any]
    ) -> None:
        """Remember the settings."""
        super().__init__(
            hass,
            store,
            enabled=bool(options.get(CONF_TELEGRAM_ENABLED)),
            senders=options.get(CONF_TELEGRAM_SENDERS) or {},
            category=options.get(CONF_TELEGRAM_CATEGORY),
            prefix=str(options.get(CONF_TELEGRAM_PREFIX) or ""),
            reply=bool(options.get(CONF_TELEGRAM_REPLY, True)),
        )

    def events(self) -> list[str]:
        """Return the events of messages and commands."""
        return [EVENT_TEXT, EVENT_COMMAND]

    def normalize(self, sender: Any) -> str:
        """Compare ids by their digits."""
        return normalize_id(sender)

    def senders_of(self, data: Mapping[str, Any]) -> list[str]:
        """Return the user, and the chat, as a whole group may be allowed."""
        return [
            str(data[key])
            for key in ("user_id", "chat_id")
            if data.get(key) not in (None, "")
        ]

    def sender_label(self, data: Mapping[str, Any]) -> str:
        """Return the user id with the name, such as "123456789 (Jan)"."""
        user = str(data.get("user_id") or data.get("chat_id") or "")
        name = " ".join(
            str(data[key]) for key in ("from_first", "from_last") if data.get(key)
        )
        return f"{user} ({name})" if user and name else user

    def text_of(self, data: Mapping[str, Any]) -> tuple[str, bool]:
        """Return the text, or the words after a note command."""
        command = str(data.get("command") or "")
        if not command:
            return str(data.get("text") or ""), False
        if command.split("@", 1)[0].casefold() not in COMMANDS:
            return "", False
        return " ".join(str(arg) for arg in data.get("args") or []), True

    async def async_send_reply(self, data: Mapping[str, Any], message: str) -> None:
        """Answer in the chat the message came from, through the same bot."""
        service_data: dict[str, Any] = {"message": message}
        if (chat := data.get("chat_id")) is not None:
            service_data["chat_id"] = chat
        if (message_id := data.get("id")) is not None:
            service_data["reply_to_message_id"] = message_id
        bot = data.get("bot")
        if isinstance(bot, Mapping) and bot.get("config_entry_id"):
            service_data["config_entry_id"] = bot["config_entry_id"]
        await self.async_call_reply(f"{TELEGRAM_DOMAIN}.send_message", service_data)
