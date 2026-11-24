"""Tests for the text normalization."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from custom_components.brainstorm.languages.de import (
    extract_spoken_due,
    build_glossary,
    clean_and_format_idea_text,
    extract_spoken_due,
    extract_spoken_priority,
    format_typed_text,
    parse_due,
    participle_to_infinitive,
    validate_ai_rewrite,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (
            "im brainstorm dass heute die kinder vom flughafen abgeholt werden müssen",
            "Heute Kinder vom Flughafen abholen",
        ),
        ("schreib bitte auf dass wir terrasse reinigen", "Terrasse reinigen"),
        ("notiere dass ich noch milch kaufen muss", "Milch kaufen"),
        # The voice command took "notiere" already
        ("bitte dass der Rasen gemäht werden muss", "Rasen mähen"),
        ("Bitte, Milch kaufen", "Milch kaufen"),
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


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        # A modal verb in the middle of the sentence
        ("der rasen muss gemäht werden", "Rasen mähen"),
        ("die hecke sollte geschnitten werden", "Hecke schneiden"),
        ("die terrasse muss abgehangen werden", "Terrasse abhängen"),
        ("die mülltonne muss rausgestellt werden", "Mülltonne rausstellen"),
        ("die garage muss mal aufgeräumt werden", "Garage aufräumen"),
        ("die waschmaschine muss repariert werden", "Waschmaschine reparieren"),
        ("der fernseher muss an die wand gehängt werden", "Fernseher an die Wand hängen"),
        ("das licht im keller muss ausgetauscht werden", "Licht im Keller austauschen"),
        ("die tür der garage muss gestrichen werden", "Tür der Garage streichen"),
        ("die kinder müssen heute vom flughafen abgeholt werden", "Kinder heute vom Flughafen abholen"),
        ("das auto muss in die werkstatt", "Auto in die Werkstatt"),
        ("der hund muss zum tierarzt", "Hund zum Tierarzt"),
        ("das paket abgeholt werden muss", "Paket abholen"),
        ("kürbisse müssen wir heute schnitzen", "Kürbisse heute schnitzen"),
        # Subject and modal verb at the start
        ("ich sollte mal die heizung entlüften", "Heizung entlüften"),
        ("wir sollten die garage aufräumen", "Garage aufräumen"),
        ("ich will die reifen wechseln", "Reifen wechseln"),
        ("ich müsste mal wieder oma anrufen", "Oma anrufen"),
        ("ich möchte den keller aufräumen", "Keller aufräumen"),
        ("wir brauchen neue batterien", "Neue Batterien"),
        # Openers
        ("äh ich wollte noch sagen dass die lampe in der küche kaputt ist", "Lampe in der Küche kaputt"),
        ("also ich glaube wir müssen mal die fenster putzen", "Fenster putzen"),
        ("könntest du dir merken dass ich die rechnung bezahlen muss", "Rechnung bezahlen"),
        ("mir ist eingefallen dass wir das dach prüfen sollten", "Dach prüfen"),
        ("idee eine app für die kinder bauen", "Eine App für die Kinder bauen"),
        ("vergiss nicht die milch zu kaufen", "Milch kaufen"),
        ("nicht vergessen den müll rauszubringen", "Müll rausbringen"),
        ("rechnung bezahlen nicht vergessen", "Rechnung bezahlen"),
        ("die heizung ist kaputt", "Heizung kaputt"),
        # Fillers stay away only from a real short task
        ("die hecke muss noch geschnitten werden", "Hecke schneiden"),
        ("rasen noch mal mähen", "Rasen nochmal mähen"),
        ("rasenmäher muss noch einmal laufen", "Rasenmäher noch einmal laufen"),
    ],
)
def test_spoken_sentences_become_tasks(raw: str, expected: str) -> None:
    """Test that a whole spoken sentence is reduced to its task."""
    assert clean_and_format_idea_text(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        # Negations and facts must not turn into a task
        ("die rechnung wurde noch nicht bezahlt", "Die Rechnung wurde noch nicht bezahlt"),
        ("die kinder dürfen nicht vergessen werden", "Die Kinder dürfen nicht vergessen werden"),
        ("ich muss nicht zum arzt", "Ich muss nicht zum Arzt"),
        ("wir brauchen keine neue heizung", "Wir brauchen keine neue Heizung"),
        # Questions and subordinate clauses stay as they are
        ("ob schlaue antworten auch einen skill braucht", "Ob schlaue antworten auch einen Skill braucht"),
        ("was macht die heizung?", "Was macht die Heizung?"),
        # Sentences that cannot be reduced completely keep their articles
        ("die spülmaschine muss repariert werden und die pumpe auch", "Die Spülmaschine muss repariert werden und die Pumpe auch"),
        ("das muss weg", "Das muss weg"),
        ("sie muss zum arzt", "Sie muss zum Arzt"),
        ("der hund braucht futter", "Der Hund braucht Futter"),
        ("muss auf jeden fall überarbeitet werden", "Muss auf jeden Fall überarbeitet werden"),
        ("das wetter sollte besser werden", "Das Wetter sollte besser werden"),
        ("die lieferung muss gefxzbarn werden", "Die Lieferung muss gefxzbarn werden"),
    ],
)
def test_sentences_stay_whole_when_they_cannot_be_reduced(raw: str, expected: str) -> None:
    """Test that a sentence is reduced completely or not at all."""
    assert clean_and_format_idea_text(raw) == expected


@pytest.mark.parametrize(
    ("participle", "infinitive"),
    [
        ("gemäht", "mähen"),
        ("rausgestellt", "rausstellen"),
        ("weggeworfen", "wegwerfen"),
        ("angeschlossen", "anschließen"),
        ("zurückgeschnitten", "zurückschneiden"),
        ("ausprobiert", "ausprobieren"),
        ("überarbeitet", "überarbeiten"),
        ("besorgt", "besorgen"),
        ("entlüftet", "entlüften"),
        ("gefeiert", "feiern"),
        ("geleert", "leeren"),
        ("gespielt", "spielen"),
        ("gebügelt", "bügeln"),
        ("geöffnet", "öffnen"),
        ("besser", None),
        ("groß", None),
        ("vergessen", None),
    ],
)
def test_participle_to_infinitive(participle: str, infinitive: str | None) -> None:
    """Test deriving an infinitive, and refusing to guess one."""
    assert participle_to_infinitive(participle) == infinitive


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Die Hecke muss geschnitten werden", "Die Hecke muss geschnitten werden"),
        ("die Tür der Garage", "Die Tür der Garage"),
        ("Was macht Sinn?", "Was macht Sinn?"),
        ("seperat prüfen.", "Separat prüfen."),
        ("packet holen", "Paket holen"),
        ("iPhone laden", "iPhone laden"),
    ],
)
def test_typed_text_is_kept(raw: str, expected: str) -> None:
    """Test that a typed text only loses its typos."""
    assert format_typed_text(raw) == expected


# A Sunday evening
NOW = datetime(2026, 11, 1, 20, 0, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    ("raw", "expected_due", "expected_text"),
    [
        ("morgen arzt anrufen", (2026, 11, 2, 9, 0), "arzt anrufen"),
        ("ich muss morgen früh den arzt anrufen", (2026, 11, 2, 8, 0), "ich muss den arzt anrufen"),
        ("am 25.11. elternsprechtag", (2026, 11, 25, 9, 0), "elternsprechtag"),
        ("wäsche bis freitag waschen", (2026, 11, 6, 9, 0), "wäsche waschen"),
        ("termin für übermorgen um 14 uhr machen", (2026, 11, 3, 14, 0), "termin machen"),
        ("hecke schneiden in zwei wochen", (2026, 11, 15, 9, 0), "hecke schneiden"),
        ("heute abend um 22 uhr müll raus", (2026, 11, 1, 22, 0), "müll raus"),
    ],
)
def test_spoken_due_is_found(
    raw: str, expected_due: tuple[int, ...], expected_text: str
) -> None:
    """Test that a spoken date moves out of the text."""
    due, text = extract_spoken_due(raw, NOW)
    assert due == datetime(*expected_due, tzinfo=timezone.utc)
    assert text == expected_text


@pytest.mark.parametrize(
    "raw",
    [
        # Already over, it would remind at once
        "heute arzt anrufen",
        # Describe the task and not the day
        "am morgen brötchen holen",
        "früh aufstehen",
        "um 5 kisten bestellen",
        "abends licht aus",
        # In the past, recurring or a question
        "seit montag kaputt",
        "letzten freitag war der arzt da",
        "jeden montag müll raus",
        "kommt der arzt morgen?",
        # A version number is not a date
        "brainstorm 1.5.8 testen",
        # Nothing would be left of the note
        "morgen",
    ],
)
def test_spoken_due_stays_in_the_text(raw: str) -> None:
    """Test that the text is kept when no clear date in the future is meant."""
    assert extract_spoken_due(raw, NOW) == (None, raw)


@pytest.mark.parametrize(
    ("raw", "priority", "text"),
    [
        ("elternsprechtag ganz wichtig frei nehmen", "high", "elternsprechtag frei nehmen"),
        ("arzt unbedingt anrufen", "high", "arzt anrufen"),
        ("rechnung dringend bezahlen", "urgent", "rechnung bezahlen"),
        ("irgendwann mal garage streichen", "low", "garage streichen"),
        ("wichtige unterlagen holen", None, "wichtige unterlagen holen"),
        ("nicht so wichtig garage streichen", None, "nicht so wichtig garage streichen"),
        ("das ist wichtig", None, "das ist wichtig"),
        ("ist das dringend?", None, "ist das dringend?"),
        ("wichtig", None, "wichtig"),
    ],
)
def test_spoken_priority(raw: str, priority: str | None, text: str) -> None:
    """Test that a priority is found anywhere, but not in a different meaning."""
    assert extract_spoken_priority(raw) == (text, priority)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("für die kinder einen sportverein finden", "Für die Kinder einen Sportverein finden"),
        ("hund braucht futter", "Hund braucht Futter"),
        ("ich brauche kaffee", "Kaffee"),
        ("wir brauchen multilinguale möglichkeiten im skill", "Multilinguale möglichkeiten im Skill"),
        ("grafana muss pdf report erhalten", "Grafana PDF Report erhalten"),
        ("automationen müssen in home assistant überarbeitet werden", "Automationen in Home Assistant überarbeiten"),
        ("mit neuen batterien testen", "Mit neuen Batterien testen"),
        # Verbs and adjectives stay lowercase
        ("blumen pflanzen", "Blumen pflanzen"),
        ("reifen wechseln", "Reifen wechseln"),
        ("wand streichen", "Wand streichen"),
        ("akku begreifen", "Akku begreifen"),
    ],
)
def test_nouns_and_spellings(raw: str, expected: str) -> None:
    """Test capitalizing from the word list, compounds and built-in spellings."""
    assert clean_and_format_idea_text(raw) == expected


def test_glossary_from_names_and_own_terms() -> None:
    """Test that names and own terms are spelled right and own terms win."""
    glossary = build_glossary(
        "Hape Kerkeling\nkürbissen = Kürbisse\npdf = Pdf",
        ["Lenia Müller", "Schlaue Antworten", "ist", "Al"],
    )
    text = clean_and_format_idea_text(
        "ein buch von hape kerkeling für lenia und lenia müller zu schlaue antworten als pdf",
        glossary,
    )
    assert "Hape Kerkeling" in text
    assert "für Lenia und Lenia Müller" in text
    assert "Schlaue Antworten" in text
    assert text.endswith("Pdf")
    assert glossary["kürbissen"] == "Kürbisse"
    assert "ist" not in glossary
    assert "al" not in glossary


def test_glossary_only_replaces_whole_words() -> None:
    """Test that a term inside a longer word stays alone."""
    assert clean_and_format_idea_text("ki kiste holen") == "KI Kiste holen"
    assert clean_and_format_idea_text("kiwi holen") == "Kiwi holen"


@pytest.mark.parametrize(
    ("spoken", "rule_text", "candidate", "expected"),
    [
        # Accepted: only shorter, better spelling, also a joined compound
        ("ein buch auf die bücher liste", "Ein Buch auf die Bücher Liste", "Buch auf Bücherliste", "Buch auf Bücherliste"),
        ("die hecke muss geschnitten werden", "Hecke schneiden", "Hecke schneiden.", "Hecke schneiden"),
        ("die hecke muss geschnitten werden", "Hecke schneiden", '"Die Hecke schneiden"', "Die Hecke schneiden"),
        # An invented word, number or person
        ("arzt anrufen", "Arzt anrufen", "Zahnarzt anrufen", None),
        ("milch kaufen", "Milch kaufen", "2 Milch kaufen", None),
        ("milch kaufen", "Milch kaufen", "Milch und Eier kaufen", None),
        # A changed negation in either direction
        ("rechnung wurde nicht bezahlt", "Rechnung wurde nicht bezahlt", "Rechnung bezahlen", None),
        ("rechnung bezahlen", "Rechnung bezahlen", "Rechnung nicht bezahlen", None),
        # Too long, several lines, or most of the note gone
        ("hecke schneiden", "Hecke schneiden", "Die Hecke schneiden sollte man heute", None),
        ("hecke schneiden", "Hecke schneiden", "Hecke\nschneiden", None),
        ("garage aufräumen und keller putzen", "Garage aufräumen und Keller putzen", "Garage", None),
        ("hecke schneiden", "Hecke schneiden", "", None),
    ],
)
def test_validate_ai_rewrite(
    spoken: str, rule_text: str, candidate: str, expected: str | None
) -> None:
    """Test that an AI text is only accepted if it adds and changes nothing."""
    assert validate_ai_rewrite(spoken, rule_text, candidate) == expected


_APPOINTMENT_NOW = datetime(2026, 11, 3, 7, 0, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    ("spoken", "due", "text"),
    [
        (
            "ein termin lenia essen bringen heute um zwölf uhr dreißig",
            datetime(2026, 11, 3, 12, 30, tzinfo=timezone.utc),
            "lenia essen bringen",
        ),
        (
            "termin zahnarzt um neun",
            datetime(2026, 11, 3, 9, 0, tzinfo=timezone.utc),
            "zahnarzt",
        ),
        (
            "ein termin für acht uhr fünf",
            datetime(2026, 11, 3, 8, 5, tzinfo=timezone.utc),
            "ein termin",
        ),
    ],
)
def test_appointment_with_time_only(spoken: str, due: datetime, text: str) -> None:
    """Test that an appointment needs no day, only a time of day."""
    assert extract_spoken_due(spoken, _APPOINTMENT_NOW) == (due, text)


@pytest.mark.parametrize("spoken", ["lichter um 22 uhr aus", "ein termin"])
def test_time_without_appointment_stays_text(spoken: str) -> None:
    """Test that a time in an ordinary note does not become a reminder."""
    assert extract_spoken_due(spoken, _APPOINTMENT_NOW) == (None, spoken)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        # What is left of 'notiere, dass …' stands in clause order
        ("wir ein regelwerk für zuhause brauchen", "Ein Regelwerk für Zuhause"),
        ("dass wir ein regelwerk für zuhause brauchen", "Ein Regelwerk für Zuhause"),
        ("notiere, dass ich neue schuhe brauche", "Neue Schuhe"),
        ("ich den keller aufräumen muss", "Keller aufräumen"),
        ("wir die garage streichen sollten", "Garage streichen"),
        ("wir am samstag oma besuchen wollen", "Am Samstag Oma besuchen"),
        ("ich morgen den arzt anrufen muss", "Morgen Arzt anrufen"),
        (
            "wir die kinder vom flughafen abgeholt werden müssen",
            "Kinder vom Flughafen abholen",
        ),
        # 'dass' misheard as 'das'
        (
            "das das regelwerk für die kinder einen skill bekommen muss",
            "Regelwerk für die Kinder einen Skill bekommen",
        ),
        ("das das auto in die werkstatt muss", "Auto in die Werkstatt"),
        # Who needs it stays, and so does a sentence with its own meaning
        ("die kinder neue schuhe brauchen", "Die Kinder neue Schuhe brauchen"),
        ("die kinder brauchen neue schuhe", "Die Kinder brauchen neue Schuhe"),
        ("das ist ein test", "Das ist ein Test"),
    ],
)
def test_clauses_become_tasks(raw: str, expected: str) -> None:
    """A subordinate clause turns into a short task."""
    assert clean_and_format_idea_text(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        # An adjective ending in "-tisch" is no table (v1.28.1)
        (
            "Meeting-Protokolle automatisch verschicken",
            "Meeting-Protokolle automatisch verschicken",
        ),
        ("Regal praktisch einräumen", "Regal praktisch einräumen"),
        ("Rechnung kritisch prüfen", "Rechnung kritisch prüfen"),
        ("Ablauf spezifisch beschreiben", "Ablauf spezifisch beschreiben"),
        # A real table or fish stays a noun
        ("neuen schreibtisch kaufen", "Neuen Schreibtisch kaufen"),
        ("gartentisch streichen", "Gartentisch streichen"),
        ("goldfisch füttern", "Goldfisch füttern"),
        ("klapptisch aufbauen", "Klapptisch aufbauen"),
        ("werktisch aufräumen", "Werktisch aufräumen"),
        ("esstisch abwischen", "Esstisch abwischen"),
        ("neuen glastisch kaufen", "Neuen Glastisch kaufen"),
        ("kaffeetisch abräumen", "Kaffeetisch abräumen"),
        ("geburtstagstisch aufbauen", "Geburtstagstisch aufbauen"),
        ("haifisch malen", "Haifisch malen"),
    ],
)
def test_adjectives_ending_like_nouns_stay_lowercase(raw: str, expected: str) -> None:
    """Test that "automatisch" is not capitalized as a compound of "Tisch"."""
    assert clean_and_format_idea_text(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("tisch decken", "Tisch decken"),
        ("geburtstagstisch decken", "Geburtstagstisch decken"),
        ("oma will tisch decken", "Oma will Tisch decken"),
        ("auto tanken", "Auto tanken"),
        ("wohnung mieten", "Wohnung mieten"),
        ("app updaten", "App updaten"),
        ("teig rollen", "Teig rollen"),
        ("sie wollen grillen", "Sie wollen grillen"),
        ("bitte auto tanken", "Auto tanken"),
        ("morgen tanken", "Morgen tanken"),
        # The noun after an adjective, a determiner or a number
        ("neue decken kaufen", "Neue Decken kaufen"),
        ("kuscheldecke und warme decken kaufen", "Kuscheldecke und warme Decken kaufen"),
        ("meine decken waschen", "Meine Decken waschen"),
        ("zwei rollen kaufen", "Zwei Rollen kaufen"),
        ("2 rollen kaufen", "2 Rollen kaufen"),
        ("alle fragen klären", "Alle Fragen klären"),
        ("mieten zahlen", "Mieten zahlen"),
    ],
)
def test_verbs_like_plurals_stay_lowercase(raw: str, expected: str) -> None:
    """Test that "decken" sets the table and is only "Decken" after an adjective."""
    assert clean_and_format_idea_text(raw) == expected


def _at(day: int, hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 11, day, hour, minute, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    ("spoken", "due"),
    [
        # 1 to 5 o'clock without a part of the day is the afternoon
        ("am freitag um halb drei elternabend", _at(6, 14, 30)),
        ("am freitag um 3 uhr elternabend", _at(6, 15)),
        ("am freitag viertel nach zwei elternabend", _at(6, 14, 15)),
        ("am freitag um eins elternabend", _at(6, 13)),
        # A part of the day, a 24 hour time and 6 o'clock and later stay
        ("am freitag um 3 uhr nachts elternabend", _at(6, 3)),
        ("am freitag um 11 uhr nachts elternabend", _at(6, 23)),
        ("am freitag früh um 5 elternabend", _at(6, 5)),
        ("am freitag morgens um 4 uhr elternabend", _at(6, 4)),
        ("am freitag halb eins mittags elternabend", _at(6, 12, 30)),
        ("am freitag um 03:00 elternabend", _at(6, 3)),
        ("am freitag um 0 uhr elternabend", _at(6, 0)),
        ("am freitag um 6 uhr elternabend", _at(6, 6)),
        ("am freitag um halb zehn elternabend", _at(6, 9, 30)),
        ("am freitag um 4:45 elternabend", _at(6, 4, 45)),
        ("am freitag um 12 uhr nachts elternabend", _at(6, 0)),
    ],
)
def test_early_hours_mean_the_afternoon(spoken: str, due: datetime) -> None:
    """Test that nobody means 1 to 5 o'clock at night without saying so."""
    assert extract_spoken_due(spoken, _APPOINTMENT_NOW) == (due, "elternabend")


@pytest.mark.parametrize(
    ("spoken", "due", "text"),
    [
        ("termin friseur um viertel nach zehn", _at(3, 10, 15), "friseur"),
        ("termin friseur um halb drei", _at(3, 14, 30), "friseur"),
        ("termin friseur viertel vor vier", _at(3, 15, 45), "friseur"),
        ("termin friseur für viertel nach zehn", _at(3, 10, 15), "friseur"),
        ("termin friseur ab halb drei", _at(3, 14, 30), "friseur"),
    ],
)
def test_appointment_with_half_or_quarter(
    spoken: str, due: datetime, text: str
) -> None:
    """Test that half and quarter also work for an appointment without a day."""
    assert extract_spoken_due(spoken, _APPOINTMENT_NOW) == (due, text)


def test_reminder_at_three_means_the_afternoon() -> None:
    """Test that a reminder "um 3 Uhr" also lands in the afternoon (v1.28.2)."""
    due, text = parse_due("erinnere mich um 3 uhr an den müll", _APPOINTMENT_NOW)
    assert due == _at(3, 15)
    assert text == "erinnere mich an den müll"
