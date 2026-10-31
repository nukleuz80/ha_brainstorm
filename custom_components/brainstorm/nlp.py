"""Natural language processing and intelligent text normalization for Brainstorm Hub."""
from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime, time, timedelta
import re

# Mapping of common German Partizip II forms to clean Infinitives
PARTIZIP_TO_INFINITIVE: dict[str, str] = {
    "abgeholt": "abholen",
    "geholt": "holen",
    "gebracht": "bringen",
    "mitgebracht": "mitbringen",
    "mitgenommen": "mitnehmen",
    "gekauft": "kaufen",
    "eingekauft": "einkaufen",
    "bestellt": "bestellen",
    "repariert": "reparieren",
    "gemäht": "mähen",
    "geschnitten": "schneiden",
    "gegossen": "gießen",
    "gewässert": "wässern",
    "geputzt": "putzen",
    "gewaschen": "waschen",
    "gesaugt": "saugen",
    "aufgeräumt": "aufräumen",
    "erledigt": "erledigen",
    "gemacht": "machen",
    "vorbereitet": "vorbereiten",
    "bezahlt": "bezahlen",
    "überwiesen": "überweisen",
    "angerufen": "anrufen",
    "zurückgerufen": "zurückrufen",
    "geprüft": "prüfen",
    "überprüft": "überprüfen",
    "kontrolliert": "kontrollieren",
    "installiert": "installieren",
    "montiert": "montieren",
    "gekocht": "kochen",
    "gebacken": "backen",
    "ausgetauscht": "austauschen",
    "getauscht": "tauschen",
    "erneuert": "erneuern",
    "abgegeben": "abgeben",
    "verschickt": "verschicken",
    "abgeschickt": "abschicken",
    "ausgedruckt": "ausdrucken",
    "unterschrieben": "unterschreiben",
    "vereinbart": "vereinbaren",
    "abgesagt": "absagen",
    "zugesagt": "zusagen",
    "gesucht": "suchen",
    "gefunden": "finden",
    "geschrieben": "schreiben",
    "gelesen": "lesen",
    "gelöscht": "löschen",
    "gepackt": "packen",
    "eingepackt": "einpacken",
    "ausgepackt": "auspacken",
    "organisiert": "organisieren",
    "geplant": "planen",
    "gebucht": "buchen",
    "storniert": "stornieren",
    "gefahren": "fahren",
    "gelaufen": "laufen",
    "gegangen": "gehen",
}

# Frequent speech-to-text and typing misspellings in German
SPELL_CORRECTIONS: dict[str, str] = {
    "terasse": "Terrasse",
    "seperat": "separat",
    "standart": "Standard",
    "packet": "Paket",
    "farad": "Fahrrad",
    "fahrrad": "Fahrrad",
    "mashine": "Maschine",
    "reparatur": "Reparatur",
    "repartur": "Reparatur",
    "garantie": "Garantie",
    "quittung": "Quittung",
    "rhytmus": "Rhythmus",
    "vorraus": "Voraus",
    "wiederspiegeln": "widerspiegeln",
    "adresse": "Adresse",
    "interessant": "interessant",
    "maschine": "Maschine",
    "kompost": "Kompost",
    "flughafen": "Flughafen",
    "kinder": "Kinder",
    "rasenmäher": "Rasenmäher",
    "glühbirne": "Glühbirne",
    "staubsauger": "Staubsauger",
    "ladekabel": "Ladekabel",
}

# Common German nouns to ensure proper capitalization
KNOWN_NOUNS: set[str] = {
    "kinder", "kind", "flughafen", "bahnhof", "schule", "kita", "kindergarten",
    "arzt", "zahnarzt", "termin", "krankenhaus", "apotheke", "tierarzt",
    "garten", "rasen", "rasenmäher", "hecke", "heckenschere", "blume", "blumen",
    "baum", "bäume", "rose", "rosen", "pflanze", "beet", "hochbeet",
    "unkraut", "laub", "kompost", "dünger", "gewächshaus", "pool",
    "terrasse", "balkon", "keller", "dachboden", "garage", "haus", "wohnung",
    "küche", "bad", "badezimmer", "wohnzimmer", "schlafzimmer", "flur", "fenster", "tür",
    "auto", "reifen", "tüv", "ölwechsel", "inspektion", "werkstatt", "fahrrad",
    "rechnung", "versicherung", "steuer", "miete", "überweisung", "bank",
    "oma", "opa", "mama", "papa", "eltern", "nachbar", "hund", "katze",
    "milch", "brot", "brötchen", "eier", "butter", "käse", "fleisch", "wurst",
    "obst", "gemüse", "einkauf", "einkaufsliste", "supermarkt",
    "wäsche", "müll", "biotonne", "restmüll", "altpapier", "gelber sack", "müllabfuhr",
    "paket", "brief", "post", "medikamente", "rezept",
    "geschenk", "geburtstag", "urlaub", "koffer", "flug", "hotel", "ticket",
    "licht", "lampe", "schalter", "sensor", "kamera", "router", "wlan",
    "heizung", "thermostat", "batterie", "akku", "kabel", "ladekabel", "fernseher",
    "mittagessen", "abendessen", "frühstück", "kuchen", "torte",
}

# Prefixes that denote conversational voice introductions
CONVERSATIONAL_PREFIXES: list[str] = [
    r"^(?:in|im|für|auf|zu)\s+(?:dem\s+)?brainstorm(?:\s+hub)?\s*(?::|,|\s+dass(?:\s+(?:ich|wir)\b)?|\s+bitte|\s+)\s*",
    r"^(?:kannst\s+du\s+(?:bitte\s+)?(?:notieren|aufschreiben|merken|eintragen)|notiere\s*(?:bitte)?|schreib\s*(?:bitte)?(?:\s*auf)?|merke\s*(?:dir)?|erinnere\s+mich\s*(?:daran)?|trage\s+ein)\s*(?::|,|\s+dass(?:\s+(?:ich|wir)\b)?|\s+)\s*",
    r"^(?:bitte\s+notieren|bitte\s+aufschreiben|bitte\s+merken)\s*(?::|,|\s+dass(?:\s+(?:ich|wir)\b)?|\s+)\s*",
    r"^(?:ich\s+muss\s+(?:noch\s+)?|wir\s+müssen\s+(?:noch\s+)?|man\s+muss\s+(?:noch\s+)?|denk\s+dran\s+dass\s+|denke\s+daran\s+dass\s+)",
    r"^(?:dass\s+ich\s+(?:noch\s+)?|dass\s+wir\s+(?:noch\s+)?|dass\s+)",
    r"^(?:noch\s+)",
]

# Prepositions that strongly suggest the following word is a noun
PREPOSITION_TRIGGERS: set[str] = {
    "vom", "von", "im", "in", "am", "an", "zum", "zu", "zur", "beim", "bei",
    "auf", "unter", "über", "nach", "mit", "für", "ohne", "durch", "aus",
}

# Suffixes that identify German nouns
NOUN_SUFFIXES: tuple[str, ...] = (
    "ung", "heit", "keit", "schaft", "ion", "ment", "tät", "tum",
    "nis", "zeug", "gerät", "plan", "tag", "kabel", "pumpe", "liste",
)

ARTICLES_AND_PRONOUNS: set[str] = {
    "der", "die", "das", "dem", "den", "des",
    "ein", "eine", "einem", "einer", "einen", "eines",
    "sich", "mich", "uns", "dich", "ihm", "ihr", "ihnen",
    "mein", "meine", "dein", "deine", "sein", "seine", "unser", "unsere",
    "mir", "dir", "euch", "ihn", "sie", "alle", "allem", "allen", "alles",
    "dies", "diese", "diesem", "diesen", "dieser", "dieses",
    "jede", "jedem", "jeden", "jeder", "jedes",
}

# Time words that stay lowercase after a preposition ('für morgen')
TIME_ADVERBS: set[str] = {
    "heute", "morgen", "übermorgen", "gestern", "vorgestern",
    "jetzt", "später", "bald", "nachher", "vorher", "immer",
}

# Prepositions with a built-in article, always followed by a noun ('am Morgen')
CONTRACTED_PREPOSITIONS: set[str] = {"am", "im", "vom", "zum", "zur", "beim"}


def _capitalize(word: str) -> str:
    """Uppercase the first letter and keep spellings like 'WLAN' or 'iPhone'."""
    if any(c.isupper() for c in word):
        return word
    return word[:1].upper() + word[1:]


def _is_noun_after_preposition(preposition: str, word: str) -> bool:
    """Return whether a word following a preposition should be capitalized."""
    if word in ARTICLES_AND_PRONOUNS or len(word) <= 2:
        return False
    if word in TIME_ADVERBS:
        return preposition in CONTRACTED_PREPOSITIONS
    # 'zu' + infinitive ('zu reparieren')
    return not (preposition == "zu" and word.endswith("en"))


def _participle_stem_to_infinitive(stem: str) -> str:
    """Build an infinitive from a participle stem ('liefer' -> 'liefern')."""
    return stem + ("n" if stem.endswith(("e", "er", "el")) else "en")


def clean_and_format_idea_text(raw_text: str) -> str:
    """Intelligently clean conversational fillers and format German task notes.
    
    Transforms sentences like:
    'im brainstorm dass heute die kinder vom flughafen abgeholt werden müssen'
    into:
    'Heute Kinder vom Flughafen abholen'
    """
    if not raw_text or not raw_text.strip():
        return ""

    s = raw_text.strip()

    # 1. Strip conversational prefixes repeatedly
    changed = True
    while changed:
        changed = False
        for pat in CONVERSATIONAL_PREFIXES:
            new_s = re.sub(pat, "", s, flags=re.IGNORECASE).strip()
            if new_s != s:
                s = new_s
                changed = True

    # 2. Passive modal verb transformation to infinitive
    # e.g., '... abgeholt werden müssen' -> '... abholen'
    passive_pat = (
        r"\b([a-zA-ZäöüÄÖÜß]+)\s+"
        r"(?:werden\s+(?:müssen|muss|soll|sollen|kann|können)|"
        r"werden|müssen|muss|soll|sollen)\.?$"
    )
    m = re.search(passive_pat, s, flags=re.IGNORECASE)
    if m:
        partizip = m.group(1).lower()
        if partizip in PARTIZIP_TO_INFINITIVE:
            inf = PARTIZIP_TO_INFINITIVE[partizip]
            s = s[:m.start(1)] + inf
        elif partizip.endswith("iert"):
            inf = partizip[:-1] + "en"
            s = s[:m.start(1)] + inf
        elif partizip.startswith("ge") and partizip.endswith("t") and len(partizip) > 4:
            stem = partizip[2:-1]
            inf = _participle_stem_to_infinitive(stem)
            s = s[:m.start(1)] + inf

    # Strip stray leftover modal verbs at the end
    s = re.sub(r"\s+(?:muss|müssen|soll|sollen)\.?$", "", s, flags=re.IGNORECASE).strip()

    # 3. Strip conversational definite articles, keeping those of prepositional phrases
    # and the genitive markers 'der'/'des' inside a sentence.
    # e.g. 'heute die kinder' -> 'heute kinder'
    # but 'in die werkstatt', 'tür der garage' are preserved.
    raw_words = s.split()
    filtered_words: list[str] = []
    articles = {"der", "die", "das", "den", "dem", "des"}
    for idx, w in enumerate(raw_words):
        w_lower = w.lower().strip("\"'([<.,!?:;)]>")
        if w_lower in articles:
            if idx == 0:
                continue
            prev_word = raw_words[idx - 1].lower().strip("\"'([<.,!?:;)]>")
            if prev_word in PREPOSITION_TRIGGERS or w_lower in ("der", "des"):
                filtered_words.append(w)
            else:
                continue
        else:
            filtered_words.append(w)

    s = " ".join(filtered_words).strip()

    # 4. Token-by-token spell checking and German capitalization
    words = s.split()
    formatted_words: list[str] = []

    for idx, w in enumerate(words):
        prefix_punct = w[:len(w) - len(w.lstrip("\"'([<"))]
        suffix_punct = w[len(w.rstrip("\"')]>.,!?:;")):]
        clean_w = w[len(prefix_punct):len(w) - len(suffix_punct)] if suffix_punct else w[len(prefix_punct):]
        lower_w = clean_w.lower()

        # Spell correction check
        if lower_w in SPELL_CORRECTIONS:
            clean_w = SPELL_CORRECTIONS[lower_w]
            lower_w = clean_w.lower()

        # Capitalization rules
        if idx == 0:
            word_cap = _capitalize(clean_w)
        elif lower_w in KNOWN_NOUNS:
            word_cap = _capitalize(clean_w)
        elif lower_w.endswith(NOUN_SUFFIXES) and len(lower_w) > 4:
            word_cap = _capitalize(clean_w)
        elif (
            idx > 0
            and words[idx - 1].lower() in PREPOSITION_TRIGGERS
            and _is_noun_after_preposition(words[idx - 1].lower(), lower_w)
        ):
            word_cap = _capitalize(clean_w)
        elif (
            idx > 1
            and words[idx - 2].lower() in PREPOSITION_TRIGGERS
            and words[idx - 1].lower() in ARTICLES_AND_PRONOUNS
            and len(lower_w) > 2
        ):
            word_cap = _capitalize(clean_w)
        else:
            word_cap = clean_w

        formatted_words.append(f"{prefix_punct}{word_cap}{suffix_punct}")

    result = " ".join(formatted_words)
    # Strip any trailing punctuation that might look like conversational fragment
    result = re.sub(r"[\.,;:!\?]+$", "", result).strip()
    return result


_NUMBER_WORDS: dict[str, int] = {
    "null": 0,
    "ein": 1,
    "eins": 1,
    "eine": 1,
    "einem": 1,
    "einer": 1,
    "zwei": 2,
    "drei": 3,
    "vier": 4,
    "fünf": 5,
    "sechs": 6,
    "sieben": 7,
    "acht": 8,
    "neun": 9,
    "zehn": 10,
    "elf": 11,
    "zwölf": 12,
    "dreizehn": 13,
    "vierzehn": 14,
    "fünfzehn": 15,
    "sechzehn": 16,
    "siebzehn": 17,
    "achtzehn": 18,
    "neunzehn": 19,
    "zwanzig": 20,
    "einundzwanzig": 21,
    "zweiundzwanzig": 22,
    "dreiundzwanzig": 23,
    "vierundzwanzig": 24,
    "dreißig": 30,
    "fünfundvierzig": 45,
}
_NUMBER = r"\d{1,2}|" + "|".join(
    sorted(_NUMBER_WORDS, key=len, reverse=True)
)
_WEEKDAYS = (
    "montag",
    "dienstag",
    "mittwoch",
    "donnerstag",
    "freitag",
    "samstag",
    "sonntag",
)
_MONTHS = (
    "januar",
    "februar",
    "märz",
    "april",
    "mai",
    "juni",
    "juli",
    "august",
    "september",
    "oktober",
    "november",
    "dezember",
)
_DAY_PARTS: dict[str, tuple[int, bool]] = {
    "früh": (8, False),
    "morgens": (8, False),
    "vormittag": (10, False),
    "vormittags": (10, False),
    "mittag": (12, False),
    "mittags": (12, False),
    "nachmittag": (15, True),
    "nachmittags": (15, True),
    "abend": (19, True),
    "abends": (19, True),
    "nacht": (22, True),
    "nachts": (22, True),
}
_DEFAULT_DUE_TIME = time(9, 0)
_DAY_PART = "|".join(sorted(_DAY_PARTS, key=len, reverse=True))

_RE_RELATIVE = re.compile(
    rf"\bin\s+({_NUMBER}|ner)\s+(minuten?|stunden?|tag(?:en)?|wochen?)\b", re.I
)
_RE_DAY = re.compile(r"\b(übermorgen|morgen|heute)\b", re.I)
_RE_NEXT_WEEK = re.compile(r"\b(?:nächste|kommende)\s+woche\b", re.I)
_RE_WEEKDAY = re.compile(
    r"\b(?:am\s+|nächsten\s+|kommenden\s+)?(" + "|".join(_WEEKDAYS) + r")\b", re.I
)
_RE_DATE = re.compile(r"\b(?:am\s+)?(\d{1,2})\.\s?(\d{1,2})\.(?:\s?(\d{2,4}))?", re.I)
_RE_MONTH_DATE = re.compile(
    r"\b(?:am\s+)?(\d{1,2})\.?\s+(" + "|".join(_MONTHS) + r")\b", re.I
)
_RE_HALF = re.compile(rf"\b(?:um\s+)?halb\s+({_NUMBER})\b", re.I)
_RE_QUARTER = re.compile(rf"\b(?:um\s+)?viertel\s+(vor|nach)\s+({_NUMBER})\b", re.I)
_RE_CLOCK = re.compile(
    rf"\bum\s+({_NUMBER})(?:[:.](\d{{2}}))?(?:\s*uhr)?(?:\s+({_NUMBER}))?(?=\s|$|[,.])"
    rf"|\b({_NUMBER})(?:[:.](\d{{2}}))?\s*uhr(?:\s+({_NUMBER}))?(?=\s|$|[,.])",
    re.I,
)
_RE_DAY_PART = re.compile(rf"\b(?:am\s+|in\s+der\s+)?({_DAY_PART})\b", re.I)
_RE_LEADING_WORDS = re.compile(r"^(?:an|am|um|dass|daran|zu|bitte|mich|ans?)\b\s*", re.I)
_RE_TRAILING_WORDS = re.compile(r"\s*\b(?:an|erinnern|bitte)$", re.I)


def _number(value: str) -> int:
    """Convert a spoken or written number."""
    lowered = value.lower()
    if lowered == "ner":
        return 1
    return int(lowered) if lowered.isdigit() else _NUMBER_WORDS[lowered]


def parse_due(text: str, now: datetime) -> tuple[datetime | None, str]:
    """Find a spoken German date and time, returning it and the remaining text.

    Without a date, a time in the past means tomorrow. Without a time, a day
    means 09:00. The result carries the time zone of now.
    """
    spans: list[tuple[int, int]] = []

    def take(pattern: re.Pattern[str]) -> re.Match[str] | None:
        """Search outside of what was already found and remember the match."""
        for match in pattern.finditer(text):
            if not any(s < match.end() and match.start() < e for s, e in spans):
                spans.append(match.span())
                return match
        return None

    due: datetime | None = None
    if match := take(_RE_RELATIVE):
        amount = _number(match.group(1))
        unit = match.group(2).lower()
        if unit.startswith("minute"):
            due = now + timedelta(minutes=amount)
        elif unit.startswith("stunde"):
            due = now + timedelta(hours=amount)
        else:
            days = amount * 7 if unit.startswith("woche") else amount
            day = now.date() + timedelta(days=days)
            due = _combine(now, day, take)
    else:
        day = None
        if match := take(_RE_DATE):
            day = _date_in_future(now, int(match.group(1)), int(match.group(2)), match.group(3))
        elif match := take(_RE_MONTH_DATE):
            month = _MONTHS.index(match.group(2).lower()) + 1
            day = _date_in_future(now, int(match.group(1)), month, None)
        elif match := take(_RE_DAY):
            offset = {"heute": 0, "morgen": 1, "übermorgen": 2}[match.group(1).lower()]
            day = now.date() + timedelta(days=offset)
        elif take(_RE_NEXT_WEEK):
            day = now.date() + timedelta(days=7 - now.weekday())
        elif match := take(_RE_WEEKDAY):
            ahead = (_WEEKDAYS.index(match.group(1).lower()) - now.weekday()) % 7
            day = now.date() + timedelta(days=ahead or 7)
        due = _combine(now, day, take)

    if due is None:
        return None, text.strip()

    remaining = text
    for start, end in sorted(spans, reverse=True):
        remaining = f"{remaining[:start]} {remaining[end:]}"
    remaining = re.sub(r"\s+", " ", remaining).strip(" ,.")
    previous = None
    while previous != remaining:
        previous = remaining
        remaining = _RE_LEADING_WORDS.sub("", remaining)
        remaining = _RE_TRAILING_WORDS.sub("", remaining).strip(" ,.")
    return due, remaining


def _date_in_future(
    now: datetime, day: int, month: int, year: str | None
) -> date | None:
    """Build a date, moving to next year if it has passed and no year was given."""
    try:
        if year:
            full_year = int(year) + 2000 if len(year) == 2 else int(year)
            return now.date().replace(year=full_year, month=month, day=day)
        result = now.date().replace(month=month, day=day)
        if result < now.date():
            result = result.replace(year=result.year + 1)
    except ValueError:
        return None
    return result


def _combine(
    now: datetime,
    day: date | None,
    take: Callable[[re.Pattern[str]], re.Match[str] | None],
) -> datetime | None:
    """Add the spoken time of day to a date, which may not be known yet."""
    hour: int | None = None
    minute = 0
    if match := take(_RE_HALF):
        hour = (_number(match.group(1)) - 1) % 24
        minute = 30
    elif match := take(_RE_QUARTER):
        base = _number(match.group(2))
        hour, minute = ((base - 1) % 24, 45) if match.group(1).lower() == "vor" else (base, 15)
    elif match := take(_RE_CLOCK):
        hour = _number(match.group(1) or match.group(4))
        minute_text = match.group(2) or match.group(5) or match.group(3) or match.group(6)
        if minute_text:
            minute = _number(minute_text)
    if hour is not None and (hour > 24 or minute > 59):
        return None

    part = take(_RE_DAY_PART)
    if part:
        default_hour, afternoon = _DAY_PARTS[part.group(1).lower()]
        if hour is None:
            hour = default_hour
        elif afternoon and hour < 12:
            hour += 12

    if day is None and hour is None:
        return None
    if hour is None:
        clock = _DEFAULT_DUE_TIME
    else:
        clock = time(hour % 24, minute)
    if day is None:
        day = now.date()
        if datetime.combine(day, clock, now.tzinfo) <= now:
            day = day + timedelta(days=1)
    return datetime.combine(day, clock, now.tzinfo)
