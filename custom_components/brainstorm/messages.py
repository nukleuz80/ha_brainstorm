"""Turn the messages of a messenger into notes.

A messenger such as WhatsApp or Telegram fires an event for every message it
receives. A watcher keeps only the messages of the senders it knows and adds
every line of such a message as a note of the person the sender belongs to.
A reply confirms what was noted. Each messenger only says where its events
carry the sender and the text, and how a reply is sent.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant.core import CALLBACK_TYPE, Context, Event, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .languages import get_pack

if TYPE_CHECKING:
    from .store import BrainstormStore

_LOGGER = logging.getLogger(__name__)

try:  # Newer Home Assistant checks the data of an action with probatio
    import probatio  # noqa: PLC0415

    INVALID_DATA: tuple[type[Exception], ...] = (vol.Invalid, probatio.Invalid)
except ImportError:  # pragma: no cover - older Home Assistant
    INVALID_DATA = (vol.Invalid,)

# Lines of one message become notes of their own, but not too many
MAX_NOTES = 20
# The last unknown sender of every messenger, shown on its settings page
DATA_UNKNOWN_SENDERS = f"{DOMAIN}_unknown_senders"
_SENDER_LINE = re.compile(r"^\s*(?P<sender>[^=:]+?)\s*[=:]\s*(?P<person>\S.*?)\s*$")


def field_value(data: Any, path: str) -> Any:
    """Return a field of event data, a dot leading into a nested one."""
    value = data
    for part in path.split("."):
        if not isinstance(value, Mapping) or part not in value:
            return None
        value = value[part]
    return value


def first_text(data: Mapping[str, Any], field: str, fallbacks: tuple[str, ...]) -> str:
    """Return the text of the chosen field, or of the first usual field."""
    for path in (field,) if field else fallbacks:
        value = field_value(data, path)
        if isinstance(value, (str, int)) and str(value).strip():
            return str(value).strip()
    return ""


def parse_senders(
    text: str, normalize: Callable[[Any], str], min_length: int
) -> tuple[dict[str, str], list[str]]:
    """Read lines like "+49 171 1234567 = person.jan".

    Return the senders with their person and the lines that could not be read.
    """
    senders: dict[str, str] = {}
    bad: list[str] = []
    for line in (text or "").splitlines():
        if not line.strip():
            continue
        match = _SENDER_LINE.match(line)
        sender = normalize(match.group("sender")) if match else ""
        if not match or len(sender.lstrip("-")) < min_length:
            bad.append(line.strip())
            continue
        senders[sender] = match.group("person")
    return senders, bad


def resolve_person(hass: HomeAssistant, person: str) -> str | None:
    """Return the person entity of "person.jan", "jan" or "Jan Example"."""
    wanted = person.strip()
    if hass.states.get(wanted) is not None and wanted.startswith("person."):
        return wanted
    folded = wanted.casefold()
    for state in hass.states.async_all("person"):
        if folded in (state.object_id.casefold(), str(state.name).casefold()):
            return state.entity_id
    return None


def last_unknown_sender(hass: HomeAssistant, source: str) -> str:
    """Return who last wrote without being allowed, such as "123456 (Jan)"."""
    return str(hass.data.get(DATA_UNKNOWN_SENDERS, {}).get(source) or "")


class MessageWatcher:
    """Add the messages of known senders as notes."""

    # Set by every messenger
    source = ""
    name = ""

    def __init__(
        self,
        hass: HomeAssistant,
        store: BrainstormStore,
        *,
        enabled: bool,
        senders: Mapping[str, Any],
        category: str | None,
        prefix: str,
        reply: bool,
    ) -> None:
        """Remember the settings."""
        self.hass = hass
        self.store = store
        self.enabled = enabled
        self.senders: dict[str, str] = {
            sender: str(person)
            for key, person in (senders or {}).items()
            if (sender := self.normalize(key))
        }
        self.category = (category or "").strip() or None
        self.prefix = (prefix or "").strip()
        self.reply = reply
        self._unsubs: list[CALLBACK_TYPE] = []

    # What a messenger defines

    def events(self) -> list[str]:
        """Return the events with the messages."""
        raise NotImplementedError

    def normalize(self, sender: Any) -> str:
        """Return a sender in the form it is compared in."""
        return str(sender or "").strip()

    def same_sender(self, sender: str, known: str) -> bool:
        """Tell whether a sender is a known one."""
        return sender == known

    def senders_of(self, data: Mapping[str, Any]) -> list[str]:
        """Return the ids a message may be allowed by, such as user and chat."""
        raise NotImplementedError

    def sender_label(self, data: Mapping[str, Any]) -> str:
        """Return the sender as shown on the settings page."""
        return ", ".join(self.senders_of(data))

    def text_of(self, data: Mapping[str, Any]) -> tuple[str, bool]:
        """Return the text of a message and whether it is meant as a note anyway.

        A command like "/note milk" is a note without the keyword.
        """
        raise NotImplementedError

    def is_own(self, data: Mapping[str, Any]) -> bool:
        """Tell whether a message was sent by Home Assistant itself."""
        return False

    async def async_send_reply(self, data: Mapping[str, Any], message: str) -> None:
        """Send the confirmation back."""
        raise NotImplementedError

    # What all messengers share

    async def async_start(self) -> None:
        """Listen to the messages."""
        if self.enabled and self.senders:
            self._unsubs = [
                self.hass.bus.async_listen(event, self._handle_event)
                for event in self.events()
            ]

    @callback
    def async_stop(self) -> None:
        """Stop listening."""
        while self._unsubs:
            self._unsubs.pop()()

    @callback
    def _handle_event(self, event: Event) -> None:
        """Hand a message over, as the event bus does not wait."""
        self.hass.async_create_task(
            self.async_handle_message(dict(event.data)), eager_start=True
        )

    def person_of(self, data: Mapping[str, Any]) -> str | None:
        """Return the person a message belongs to, None for an unknown sender."""
        for sender in self.senders_of(data):
            normalized = self.normalize(sender)
            for known, person in self.senders.items():
                if normalized and self.same_sender(normalized, known):
                    return person
        return None

    def note_texts(self, text: str, command: bool = False) -> list[str]:
        """Return the notes of a message, one per line, without the keyword."""
        if self.prefix and not command:
            if not text.casefold().startswith(self.prefix.casefold()):
                return []
            text = text[len(self.prefix) :].lstrip(" :,-")
        lines = [line.strip(" \t-•*") for line in text.splitlines()]
        return [line for line in lines if line][:MAX_NOTES]

    async def async_handle_message(self, data: Mapping[str, Any]) -> list[str]:
        """Add the notes of one message, returning their texts."""
        if self.is_own(data):
            return []
        person = self.person_of(data)
        if person is None:
            if label := self.sender_label(data):
                self.hass.data.setdefault(DATA_UNKNOWN_SENDERS, {})[self.source] = label
                _LOGGER.info("%s message from %s left out", self.name, label)
            return []
        text, command = self.text_of(data)
        texts = self.note_texts(text, command)
        if not texts:
            return []
        person_entity = resolve_person(self.hass, person)
        state = self.hass.states.get(person_entity) if person_entity else None
        context = Context(user_id=state.attributes.get("user_id") if state else None)
        added: list[dict[str, Any]] = []
        for line in texts:
            try:
                added.append(
                    await self.store.async_add_idea(
                        line,
                        category=self.category,
                        source=self.source,
                        device=str(state.name) if state is not None else person,
                        context=context,
                        spoken=False,
                    )
                )
            except HomeAssistantError as err:
                _LOGGER.warning("%s note %r not added: %s", self.name, line, err)
        if added and self.reply:
            pack = get_pack(self.hass.config.language)
            message = "\n".join(
                pack.msg(
                    "message_saved",
                    text=str(idea.get("text") or ""),
                    category=str(idea.get("category") or ""),
                )
                for idea in added
            )
            await self.async_send_reply(data, message)
        return [str(idea.get("text") or "") for idea in added]

    async def async_call_reply(self, action: str, service_data: dict[str, Any]) -> None:
        """Call the action of a reply, a missing or failing one only logged."""
        domain, _, service = action.partition(".")
        if not service or not self.hass.services.has_service(domain, service):
            _LOGGER.warning(
                "%s reply left out, the action %s does not exist", self.name, action
            )
            return
        try:
            await self.hass.services.async_call(
                domain, service, service_data, blocking=True
            )
        except (HomeAssistantError, ValueError, *INVALID_DATA) as err:
            _LOGGER.warning("%s reply through %s failed: %s", self.name, action, err)
