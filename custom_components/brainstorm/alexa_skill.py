"""Connection between a user's own Alexa skill and Brainstorm Hub."""
from __future__ import annotations

import json
import logging
import secrets
from typing import TYPE_CHECKING, Any

from aiohttp import hdrs, web

from homeassistant.components import webhook
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.network import get_url
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import ATTR_CATEGORY, DOMAIN, SKILL_STORAGE_KEY, SKILL_STORAGE_VERSION

if TYPE_CHECKING:
    from .store import BrainstormStore

_LOGGER = logging.getLogger(__name__)

MAX_TEXT_LENGTH = 500

INTERACTION_MODEL: dict[str, Any] = {
    "interactionModel": {
        "languageModel": {
            "invocationName": "brainstorm",
            "intents": [
                {
                    "name": "CaptureIdeaIntent",
                    "slots": [{"name": "text", "type": "AMAZON.SearchQuery"}],
                    "samples": [
                        "notiere {text}",
                        "notier {text}",
                        "idee {text}",
                        "neue idee {text}",
                        "merke dir {text}",
                        "schreib auf {text}",
                    ],
                },
                {"name": "AMAZON.CancelIntent", "samples": []},
                {"name": "AMAZON.HelpIntent", "samples": []},
                {"name": "AMAZON.StopIntent", "samples": []},
                {"name": "AMAZON.NavigateHomeIntent", "samples": []},
                {"name": "AMAZON.FallbackIntent", "samples": []},
            ],
            "types": [],
        }
    }
}

# Kept small on purpose, so that improvements reach users through the integration
SKILL_CODE_TEMPLATE = '''"""Brainstorm Hub Alexa skill. Keep this code private, it contains your secret address."""
import json
import urllib.error
import urllib.request

WEBHOOK_URL = "__WEBHOOK_URL__"
TIMEOUT_SECONDS = 6


def _response(text, end_session=True):
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {"type": "PlainText", "text": text},
            "shouldEndSession": end_session,
        },
    }


def _capture(event, text):
    payload = {
        "application_id": event["context"]["System"]["application"]["applicationId"],
        "text": text,
    }
    request = urllib.request.Request(
        WEBHOOK_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as reply:
            speech = json.loads(reply.read().decode()).get("speech")
    except (urllib.error.URLError, TimeoutError, ValueError):
        return "Home Assistant ist nicht erreichbar. Die Idee wurde nicht gespeichert."
    return speech or "Der Skill-Modus ist in Brainstorm nicht aktiv. Die Idee wurde nicht gespeichert."


def lambda_handler(event, context):
    request = event["request"]
    if request["type"] == "LaunchRequest":
        return _response("Was soll ich notieren? Sage zum Beispiel: notiere Kellerlicht dimmen.", False)
    if request["type"] == "SessionEndedRequest":
        return {"version": "1.0", "response": {}}

    intent = request.get("intent", {})
    if intent.get("name") == "CaptureIdeaIntent":
        text = intent.get("slots", {}).get("text", {}).get("value")
        if text:
            return _response(_capture(event, text))
        return _response("Ich habe keinen Text verstanden.")
    if intent.get("name") == "AMAZON.HelpIntent":
        return _response("Sage zum Beispiel: notiere Kellerlicht dimmen.", False)
    if intent.get("name") == "AMAZON.FallbackIntent":
        return _response("Das habe ich nicht verstanden. Sage zum Beispiel: notiere Kellerlicht dimmen.", False)
    return _response("Okay.")
'''


class AlexaSkill:
    """Accept ideas from the Alexa skill the user built for this installation."""

    def __init__(self, hass: HomeAssistant, store: BrainstormStore) -> None:
        """Initialize the skill connection."""
        self.hass = hass
        self._ideas = store
        self._store: Store[dict[str, Any]] = Store(
            hass, SKILL_STORAGE_VERSION, SKILL_STORAGE_KEY
        )
        self._webhook_id = ""
        self._application_id: str | None = None
        self._active = False
        self.last_request: dict[str, str] | None = None

    @property
    def is_linked(self) -> bool:
        """Return whether a skill has been linked to this installation."""
        return self._application_id is not None

    async def async_load(self) -> None:
        """Load the stored secret and skill link."""
        data = await self._store.async_load() or {}
        self._webhook_id = data.get("webhook_id", "")
        self._application_id = data.get("application_id")
        if not self._webhook_id:
            await self._async_new_webhook_id()

    async def _async_save(self) -> None:
        """Persist the secret and skill link."""
        await self._store.async_save(
            {"webhook_id": self._webhook_id, "application_id": self._application_id}
        )

    async def _async_new_webhook_id(self) -> None:
        """Create a new secret, which invalidates the old skill code."""
        self._webhook_id = f"brainstorm_{secrets.token_hex(24)}"
        self._application_id = None
        await self._async_save()

    @callback
    def async_start(self) -> None:
        """Start accepting requests from the skill."""
        webhook.async_register(
            self.hass,
            DOMAIN,
            "Brainstorm Alexa Skill",
            self._webhook_id,
            self._async_handle_webhook,
            local_only=False,
            allowed_methods=[hdrs.METH_POST],
        )
        self._active = True

    @callback
    def async_stop(self) -> None:
        """Stop accepting requests from the skill."""
        if self._active:
            webhook.async_unregister(self.hass, self._webhook_id)
            self._active = False

    async def async_reset(self) -> None:
        """Replace the secret and remove the skill link."""
        was_active = self._active
        self.async_stop()
        await self._async_new_webhook_id()
        self.last_request = None
        if was_active:
            self.async_start()

    def get_skill_code(self) -> str:
        """Return the skill code with this installation's public address.

        Raises NoURLAvailableError if Home Assistant has no public address.
        """
        # webhook.async_generate_url() excludes Home Assistant Cloud addresses
        base_url = get_url(
            self.hass, allow_internal=False, allow_ip=False, require_ssl=True
        )
        url = f"{base_url}{webhook.async_generate_path(self._webhook_id)}"
        return SKILL_CODE_TEMPLATE.replace("__WEBHOOK_URL__", url)

    @staticmethod
    def get_interaction_model() -> str:
        """Return the voice model for the Alexa developer console."""
        return json.dumps(INTERACTION_MODEL, indent=2, ensure_ascii=False)

    def _speech(self, german: str, english: str) -> web.Response:
        """Return text for Alexa to speak."""
        is_german = self.hass.config.language.startswith("de")
        return web.json_response({"speech": german if is_german else english})

    async def _async_handle_webhook(
        self, hass: HomeAssistant, webhook_id: str, request: web.Request
    ) -> web.Response:
        """Store an idea sent by the skill."""
        try:
            payload = await request.json()
        except ValueError:
            return web.Response(status=400)
        if not isinstance(payload, dict):
            return web.Response(status=400)

        application_id = payload.get("application_id")
        text = payload.get("text")
        if not isinstance(application_id, str) or not application_id:
            return web.Response(status=400)
        if not isinstance(text, str):
            return web.Response(status=400)

        # The first skill to call the secret address becomes the linked one
        if self._application_id is None:
            self._application_id = application_id
            await self._async_save()
        elif application_id != self._application_id:
            _LOGGER.warning("Rejected a request from an unknown Alexa skill")
            return web.Response(status=403)

        try:
            idea = await self._ideas.async_add_idea(
                text=text.strip()[:MAX_TEXT_LENGTH], source="alexa_skill"
            )
        except HomeAssistantError as err:
            _LOGGER.warning("Could not store idea from Alexa skill: %s", err)
            return self._speech(
                "Das konnte ich nicht speichern.", "I could not save that."
            )

        self.last_request = {
            "time": dt_util.now().strftime("%d.%m.%Y %H:%M:%S"),
            "text": idea.get("text", ""),
        }
        category = idea.get(ATTR_CATEGORY)
        if category and category != "Inbox":
            return self._speech(
                f"Gespeichert unter {category}.", f"Saved under {category}."
            )
        return self._speech("Gespeichert.", "Saved.")
