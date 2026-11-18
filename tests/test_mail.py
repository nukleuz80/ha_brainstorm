"""Tests for notes by mail."""

from __future__ import annotations

from typing import Any

import pytest
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_mock_service,
)

from custom_components.brainstorm.mail import (
    MailWatcher,
    clean_body,
    clean_subject,
    format_senders,
    normalize_address,
    parse_senders,
    strip_keyword,
)

from .conftest import SetupEntry

JAN = "jan@example.com"
OPTIONS = {"mail_enabled": True, "mail_senders": {JAN: "person.jan"}}


@pytest.fixture
def persons(hass: HomeAssistant) -> None:
    """A person with a Home Assistant user."""
    hass.states.async_set(
        "person.jan", "home", {"friendly_name": "Jan", "user_id": "user-jan"}
    )


def _mail(subject: str, sender: str = JAN, **extra: Any) -> dict[str, Any]:
    """The data of imap_content as the IMAP integration fires it."""
    return {
        "entry_id": "imap-entry",
        "folder": "INBOX",
        "initial": True,
        "sender": sender,
        "subject": subject,
        "uid": "42",
        "parts": {},
        **extra,
    }


def _notes(store: Any) -> list[dict[str, Any]]:
    return [idea for idea in store.ideas if idea.get("source") == "mail"]


def test_addresses_subjects_and_bodies() -> None:
    """Addresses in lower case, no Re:, no signature or quoted mails."""
    assert normalize_address("Jan <Jan@Example.com>") == JAN
    assert normalize_address("kein-mail") == ""
    senders, bad = parse_senders("Jan@Example.com = person.jan\nkaputt = x")
    assert senders == {JAN: "person.jan"}
    assert bad == ["kaputt = x"]
    assert format_senders(senders) == f"{JAN} = person.jan"
    assert clean_subject("AW: WG: Re: Notiz: Reifen") == "Notiz: Reifen"
    body = (
        "Bitte bis Freitag.\r\n\r\n\r\n\r\nDanke\r\n> zitiert\r\n-- \r\nJan\r\nTel 123"
    )
    assert clean_body(body) == "Bitte bis Freitag.\n\nDanke"
    assert clean_body("Hi\nAm 1.1. schrieb Anna:\nalt") == "Hi"
    assert clean_body("x" * 3000).endswith(" …")


async def test_mail_becomes_a_note(
    hass: HomeAssistant, setup_entry: SetupEntry, persons: None
) -> None:
    """Subject as text, fetched body as description, marked as read."""
    seen = async_mock_service(hass, "imap", "seen")
    fetched: list[ServiceCall] = []

    async def fetch(call: ServiceCall) -> dict[str, Any]:
        fetched.append(call)
        return {"text": "Winterreifen montieren lassen.\n-- \nSignatur"}

    hass.services.async_register(
        "imap", "fetch", fetch, supports_response=SupportsResponse.ONLY
    )
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox", "Garage"]},
        options={**OPTIONS, "mail_category": "Garage", "mail_prefix": "Notiz"},
    )
    hass.bus.async_fire(
        "imap_content", _mail("Re: Notiz: Reifenwechsel", "Jan <JAN@example.com>")
    )
    # Without the keyword, from a stranger, or reported again: nothing
    hass.bus.async_fire("imap_content", _mail("Newsletter"))
    hass.bus.async_fire("imap_content", _mail("Notiz: Spam", "x@spam.com"))
    hass.bus.async_fire("imap_content", _mail("Notiz: Doppelt", initial=False))
    await hass.async_block_till_done()
    notes = _notes(entry.runtime_data)
    assert len(notes) == 1
    assert notes[0]["text"] == "Reifenwechsel"
    assert notes[0]["description"] == "Winterreifen montieren lassen."
    assert notes[0]["category"] == "Garage"
    assert notes[0]["owner"] == "user-jan"
    assert fetched[0].data == {"entry": "imap-entry", "uid": "42"}
    assert [call.data for call in seen] == [{"entry": "imap-entry", "uid": "42"}]


async def test_text_in_the_event_and_a_reply(
    hass: HomeAssistant, setup_entry: SetupEntry, persons: None
) -> None:
    """A text in the event is used, no subject takes its first line."""
    replies = async_mock_service(hass, "notify", "smtp")
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox"]},
        options={
            **OPTIONS,
            "mail_mark_seen": False,
            "mail_reply_service": "notify.smtp",
        },
    )
    watcher = MailWatcher(hass, entry.runtime_data, entry.options)
    texts = await watcher.async_handle_message(
        _mail("", text="Steuererklärung\nBelege sammeln")
    )
    assert texts == ["Steuererklärung"]
    note = _notes(entry.runtime_data)[0]
    assert note["description"] == "Belege sammeln"
    assert replies[0].data["target"] == [JAN]
    assert replies[0].data["message"].startswith("✅ Notiert in")
    # Nothing to note in an empty mail
    assert await watcher.async_handle_message(_mail("", text="")) == []


async def test_unload_stops_listening(
    hass: HomeAssistant, setup_entry: SetupEntry, persons: None
) -> None:
    """Unloading the entry removes the listener."""
    entry = await setup_entry(
        stored={"ideas": [], "categories": ["Inbox"]}, options=OPTIONS
    )
    assert hass.bus.async_listeners().get("imap_content") == 1
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert hass.bus.async_listeners().get("imap_content", 0) == 0


async def test_settings_page(
    hass: HomeAssistant, setup_entry: SetupEntry, persons: None
) -> None:
    """Offered with the IMAP integration, the addresses are checked and saved."""
    async_mock_service(hass, "notify", "smtp")
    MockConfigEntry(domain="imap", title="Postfach").add_to_hass(hass)
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox"]})
    hass.bus.async_fire("imap_content", _mail("Hallo", "anna@example.com"))
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "integrations"}
    )
    assert "imap" in result["menu_options"]
    assert result["description_placeholders"]["status_mail"] == "aus"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "imap"}
    )
    assert result["type"] is FlowResultType.FORM
    fields = {str(key): key for key in result["data_schema"].schema}
    assert "mail_reply_service" in fields
    flow_id = result["flow_id"]
    result = await hass.config_entries.options.async_configure(
        flow_id, {"mail_enabled": True, "mail_senders": "ohne-at = Jan"}
    )
    assert result["errors"] == {"mail_senders": "mail_senders_invalid"}
    result = await hass.config_entries.options.async_configure(
        flow_id, {"mail_enabled": True}
    )
    assert result["errors"] == {"mail_senders": "mail_senders_missing"}
    result = await hass.config_entries.options.async_configure(
        flow_id,
        {
            "mail_enabled": True,
            "mail_senders": "Jan <Jan@Example.com> = Jan",
            "mail_prefix": "Notiz",
            "mail_match": "anywhere",
            "mail_mark_seen": True,
            "mail_reply_service": "notify.smtp",
        },
    )
    assert result["step_id"] == "integrations"
    assert result["description_placeholders"]["status_mail"] == "an · 1 Adressen"
    assert entry.options["mail_senders"] == {JAN: "person.jan"}
    assert entry.options["mail_reply_service"] == "notify.smtp"
    assert entry.options["mail_match"] == "anywhere"
    hass.config_entries.options.async_abort(result["flow_id"])


def test_keywords_are_found_and_left_out() -> None:
    """At the start, anywhere, in brackets; missing gives None."""
    assert strip_keyword("Notiz: Reifen", "notiz", True) == "Reifen"
    assert strip_keyword("Reifen Notiz", "Notiz", True) is None
    assert strip_keyword("Reifen (Notiz)", "Notiz", False) == "Reifen"
    assert strip_keyword("Reifen - notiz - Winter", "Notiz", False) == "Reifen Winter"
    assert strip_keyword("Reifen", "", True) == "Reifen"


@pytest.mark.parametrize(
    ("match", "subject", "text", "expected"),
    [
        ("subject_start", "Notiz: Reifen", "", ["Reifen"]),
        ("subject_start", "Reifen Notiz", "", []),
        ("subject", "Reifen (Notiz)", "", ["Reifen"]),
        ("subject", "Reifen", "Notiz", []),
        ("anywhere", "Reifen", "Bitte als Notiz.", ["Reifen"]),
        ("anywhere", "Notiz Reifen", "", ["Reifen"]),
        ("anywhere", "Reifen", "Hallo", []),
        ("all", "Reifen", "", ["Reifen"]),
    ],
)
async def test_what_a_mail_is_recognised_by(
    hass: HomeAssistant,
    setup_entry: SetupEntry,
    persons: None,
    match: str,
    subject: str,
    text: str,
    expected: list[str],
) -> None:
    """The setting decides which mails become notes."""
    async_mock_service(hass, "imap", "seen")
    entry = await setup_entry(stored={"ideas": [], "categories": ["Inbox"]})
    watcher = MailWatcher(
        hass,
        entry.runtime_data,
        {**OPTIONS, "mail_prefix": "Notiz", "mail_match": match},
    )
    assert await watcher.async_handle_message(_mail(subject, text=text)) == expected


def test_forwarded_and_html_mails_keep_only_the_own_text() -> None:
    """Test that forwarding a mail does not copy the whole mail into the note."""
    long = "Ihre Rechnung\n" + "Zeile\n" * 500
    gmail = "Bis Freitag.\n\n---------- Weitergeleitete Nachricht ---------\nVon: Shop <a@b.de>\n\n"
    assert clean_body(gmail + long) == "Bis Freitag."
    assert clean_body("---------- Forwarded message ---------\nFrom: a@b.de\n" + long) == ""
    outlook = "Bitte prüfen\r\n\r\n*From:* Max <m@x.de>\r\n*Sent:* Monday\r\n\r\n"
    assert clean_body(outlook + long) == "Bitte prüfen"
    apple = "Siehe unten\n\nAnfang der weitergeleiteten Nachricht:\n\n> Von: X\n"
    assert clean_body(apple + long) == "Siehe unten"
    web_de = "Hallo\n\nGesendet: Montag, 17. November 2026 um 10:00 Uhr\nVon: X\n"
    assert clean_body(web_de + long) == "Hallo"
    html_mail = (
        "<html><head><style>p {color: red}</style></head><body>"
        "<p>Reifen&nbsp;wechseln</p><div>Gru&szlig;<br>Jan</div>"
        "<blockquote>alte Mail</blockquote></body></html>"
    )
    assert clean_body(html_mail) == "Reifen wechseln\nGruß\nJan"
