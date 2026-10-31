"""Tests for the text normalization."""
from __future__ import annotations

import pytest

from custom_components.brainstorm.nlp import clean_and_format_idea_text


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (
            "im brainstorm dass heute die kinder vom flughafen abgeholt werden müssen",
            "Heute Kinder vom Flughafen abholen",
        ),
        ("schreib bitte auf dass wir terrasse reinigen", "Terrasse reinigen"),
        ("notiere dass ich noch milch kaufen muss", "Milch kaufen"),
        ("WLAN Passwort ändern", "WLAN Passwort ändern"),
        ("ESP32 flashen", "ESP32 flashen"),
        ("iPhone laden", "iPhone laden"),
        ("Router zu reparieren", "Router zu reparieren"),
        ("Termin für morgen", "Termin für morgen"),
        ("Termin am morgen", "Termin am Morgen"),
        ("Heizung geliefert werden", "Heizung liefern"),
        ("Tür geöffnet werden", "Tür öffnen"),
        ("die Tür der Garage streichen", "Tür der Garage streichen"),
        ("kuchen für die oma backen", "Kuchen für die Oma backen"),
        ("auto in die werkstatt bringen", "Auto in die Werkstatt bringen"),
        ("Blumen pflanzen", "Blumen pflanzen"),
        ("", ""),
    ],
)
def test_clean_and_format(raw: str, expected: str) -> None:
    """Test that text is cleaned without losing meaning or spelling."""
    assert clean_and_format_idea_text(raw) == expected
