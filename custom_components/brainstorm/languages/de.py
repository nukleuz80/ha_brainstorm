"""German rules and words of Brainstorm Hub."""
from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime, time, timedelta
import re

from ..const import DEFAULT_CATEGORIES, PRIORITY_HIGH, PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_URGENT
from .common import (
    CATEGORY_BRAINSTORM,
    CATEGORY_DAILY,
    CATEGORY_HOME_GARDEN,
    CATEGORY_PROJECTS,
    CATEGORY_SMARTHOME,
    LanguagePack,
    apply_glossary,
    capitalize_first,
    merge_glossary,
    validate_rewrite,
)
from .german_nouns import AMBIGUOUS_PLURALS, GERMAN_NOUNS

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
    "gefeiert": "feiern",
    "geschlossen": "schließen",
    "gehangen": "hängen",
    "gestrichen": "streichen",
    "geworfen": "werfen",
    "getragen": "tragen",
    "gezogen": "ziehen",
    "genommen": "nehmen",
    "gegeben": "geben",
    "gesehen": "sehen",
    "gesprochen": "sprechen",
    "geladen": "laden",
    "gelegen": "liegen",
    "geholfen": "helfen",
    "gestanden": "stehen",
    "geschoben": "schieben",
    "gegraben": "graben",
    "gesungen": "singen",
    "gestochen": "stechen",
    "gemessen": "messen",
    "gegessen": "essen",
    "getrunken": "trinken",
    "gebunden": "binden",
    "gerissen": "reißen",
    "beschnitten": "beschneiden",
    "beschrieben": "beschreiben",
    "besprochen": "besprechen",
    "bestiegen": "besteigen",
    "bezogen": "beziehen",
    "verschoben": "verschieben",
    "verbunden": "verbinden",
    "vergraben": "vergraben",
    "übertragen": "übertragen",
    "unterschrieben": "unterschreiben",
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
    r"^(?:äh+m?|öh+m?|hm+|mhm|also|ja|naja|na\s+ja|okay|ok|so|gut|und|ach\s+ja|übrigens)\b[,.]?\s+",
    r"^(?:ich\s+(?:glaube|denke)|mir\s+(?:ist\s+)?(?:gerade\s+)?eingefallen|mir\s+fällt\s+(?:gerade\s+)?ein|(?:ich\s+)?wollte\s+(?:noch\s+)?sagen)(?:\s*,)?\s+",
    r"^(?:(?:kannst|könntest)\s+du\s+(?:dir\s+)?(?:bitte\s+)?(?:notieren|aufschreiben|merken|eintragen)|notiere\s*(?:bitte)?|schreib\s*(?:bitte)?(?:\s*auf)?|merke?\s*(?:dir)?|trage\s+ein)\s*(?::|,|\s+dass(?:\s+(?:ich|wir)\b)?|\s+)\s*",
    r"^(?:bitte\s+notieren|bitte\s+aufschreiben|bitte\s+merken)\s*(?::|,|\s+dass(?:\s+(?:ich|wir)\b)?|\s+)\s*",
    r"^(?:neue\s+)?(?:idee|notiz)\s*(?::|,)?\s+(?!(?:von|vom|für|zu|zur|zum|an|am|über|mit|aus|im|in)\b)",
    r"^(?:dass\s+ich\s+(?:noch\s+)?|dass\s+wir\s+(?:noch\s+)?|dass\s+)",
    r"^(?:noch\s+)",
]

# Openers after which an infinitive with 'zu' is the actual task
REMINDER_OPENER = re.compile(
    r"^(?:bitte\s+)?(?:vergiss\s+nicht|nicht\s+vergessen|denke?\s+(?:dran|daran)|"
    r"erinnere\s+mich(?:\s+daran)?)(?:\s*,)?\s+",
    re.IGNORECASE,
)

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


# Prefixes of separable verbs ('raus-ge-stellt' -> 'rausstellen'), longest first
SEPARABLE_PREFIXES: tuple[str, ...] = (
    "zurück", "weiter", "heraus", "herein", "hinaus", "hinein", "runter", "rüber",
    "durch", "fest", "raus", "rein", "weg", "vor", "nach", "mit", "auf", "aus",
    "ein", "her", "hin", "los", "ab", "an", "um", "zu",
)

# Prefixes of verbs whose participle has no 'ge' ('bezahlt' -> 'bezahlen')
INSEPARABLE_PREFIXES: tuple[str, ...] = (
    "be", "ent", "er", "ver", "zer", "über", "unter", "miss", "wider", "hinter",
)

SUBJECT_PRONOUNS: set[str] = {
    "ich", "du", "er", "sie", "es", "wir", "ihr", "man", "das", "dies", "der", "die",
}

# Word endings that make a compound noun, long enough not to hit other words
_COMPOUND_PARTS: tuple[str, ...] = tuple(
    sorted(
        (
            word
            for word in GERMAN_NOUNS
            if len(word) >= 5 and not word.endswith(("en", "e"))
        ),
        key=len,
        reverse=True,
    )
) + ("haus", "liste", "lampe", "tonne", "karte", "kiste", "tasche", "farbe", "zeit", "wand", "raum")

# Words of a task that may only be reduced when they are the main verb
_MODAL_NEED = (
    r"(?:muss|musst|müssen|müsste|müssten|soll|sollen|sollte|sollten)"
)
_MODAL_FINAL = (
    r"(?:muss|müssen|müsste|müssten|soll|sollen|sollte|sollten|kann|können|"
    r"könnte|könnten)"
)
_WORD = r"[a-zA-ZäöüÄÖÜß-]+"
_STATE_WORD = r"(?:kaputt|defekt|leer|alle|undicht|verstopft|locker|lose|nass)"

# A negation, a fact about the past or a real question must keep its meaning
_RE_KEEP_SENTENCE = re.compile(
    r"\b(?:nicht|nie|niemals|nichts|kein|keine|keinen|keinem|keiner|keines|darf|"
    r"dürfen|wurde|wurden|worden|war|waren|hat|haben|hatte|hatten)\b",
    re.IGNORECASE,
)
_RE_QUESTION_START = re.compile(
    r"^(?:ob|wenn|falls|weil|warum|wieso|weshalb|wie|wann|wo|wer|was|welche[rs]?|"
    r"obwohl)\b",
    re.IGNORECASE,
)
_RE_SUBJECT_MODAL_START = re.compile(
    r"^(?:ich|wir|man)\s+(?:noch\s+)?(?:muss|müssen|müsste|müssten|soll|sollen|sollte|"
    r"sollten|will|wollen|wollte|wollten|möchte|möchten|brauche|brauchen|"
    r"würde\s+gerne?|würden\s+gerne?)\s+(?:noch\s+)?",
    re.IGNORECASE,
)
_RE_INVERTED_MODAL = re.compile(
    rf"^(.+?)\s+{_MODAL_NEED}\s+(?:wir|ich|man)\s+(.+)$", re.IGNORECASE
)
_RE_PASSIVE_MODAL = re.compile(
    rf"^(.+?)\s+{_MODAL_NEED}\s+(.*?)\b({_WORD})\s+werden$", re.IGNORECASE
)
_RE_FINAL_PASSIVE = re.compile(
    rf"^(.*?\b)?({_WORD})\s+werden(?:\s+{_MODAL_FINAL})?$",
    re.IGNORECASE,
)
_RE_FINAL_MODAL = re.compile(rf"^(.*?\b)?({_WORD})\s+{_MODAL_FINAL}$", re.IGNORECASE)
_RE_LEADING_MODAL = re.compile(rf"^{_MODAL_FINAL}\b", re.IGNORECASE)
_RE_ACTIVE_MODAL = re.compile(rf"^(.+?)\s+({_MODAL_NEED})\s+(.+)$", re.IGNORECASE)
_RE_CLAUSE_WORD = re.compile(
    r"\b(?:werden|wird|sein|ist|sind|und|oder|aber|dass|weil|wenn)\b", re.IGNORECASE
)
_RE_STATE = re.compile(
    rf"^(?P<subject>.+?)\s+(?:ist|sind)\s+(?:(?:gerade|jetzt|schon|wieder|leider)\s+)*"
    rf"(?P<state>{_STATE_WORD})$",
    re.IGNORECASE,
)
_RE_FINAL_STATE = re.compile(
    rf"^(?P<subject>.+?)\s+(?P<state>{_STATE_WORD})\s+(?:ist|sind)$", re.IGNORECASE
)
_RE_ZU_COMPOUND = re.compile(
    r"\b(zurück|weiter|raus|rein|weg|vor|nach|mit|auf|aus|ein|ab|an|um)zu"
    r"([a-zäöüß]+en)$",
    re.IGNORECASE,
)
_RE_ZU_INFINITIVE = re.compile(rf"\bzu\s+({_WORD}e?n)$", re.IGNORECASE)
_RE_NOT_FORGET_SUFFIX = re.compile(r"\s*,?\s+nicht\s+vergessen[.!]?$", re.IGNORECASE)
_RE_NOCH_MAL = re.compile(r"\bnoch\s+mal\b", re.IGNORECASE)
_RE_FILLERS = re.compile(
    r"\b(?:mal\s+wieder|auf\s+jeden\s+fall|auf\s+alle\s+fälle|mal|halt|eben|"
    r"eigentlich|irgendwie|bitte|ja|doch|wohl|noch(?!\s+(?:einmal|ein|eine|einen|mehr)\b))\b",
    re.IGNORECASE,
)
# A sentence with one of these words is still a sentence, not a short task
_RE_SENTENCE_WORD = re.compile(
    rf"\b(?:ich|du|er|es|wir|ihr|man|dass|ob|wenn|weil|ist|sind|wird|werden|braucht|"
    rf"brauchen|brauche|will|wollen|möchte|möchten|kann|können|{_MODAL_NEED}|"
    r"nicht|nie|kein|keine|keinen|wurde|wurden|war|waren|hat|haben)\b",
    re.IGNORECASE,
)


# Spellings a sentence from speech recognition never has by itself
BUILTIN_GLOSSARY: dict[str, str] = {
    "alexa": "Alexa",
    "e-mail": "E-Mail",
    "echo show": "Echo Show",
    "email": "E-Mail",
    "grafana": "Grafana",
    "hdmi": "HDMI",
    "home assistant": "Home Assistant",
    "homeassistant": "Home Assistant",
    "ipad": "iPad",
    "iphone": "iPhone",
    "ki": "KI",
    "led": "LED",
    "nas": "NAS",
    "pdf": "PDF",
    "siri": "Siri",
    "tv": "TV",
    "usb": "USB",
    "wlan": "WLAN",
}


def _is_noun(word: str) -> bool:
    """Return whether a lowercase word is a known noun or a compound ending in one."""
    if word in KNOWN_NOUNS or word in GERMAN_NOUNS:
        return True
    if len(word) > 4 and word.endswith(NOUN_SUFFIXES):
        return True
    if (
        word.endswith("n")
        and word not in AMBIGUOUS_PLURALS
        and word[:-1].endswith("e")
        and word[:-1] in GERMAN_NOUNS
    ):
        return True
    if word.endswith("s") and word[:-1] in GERMAN_NOUNS:
        return True
    # 'sportverein' ends in 'verein'; an '-en' ending could also be a verb ('greifen')
    return not word.endswith("en") and any(
        word.endswith(word_part)
        for word_part in _COMPOUND_PARTS
        if len(word) >= len(word_part) + 3
    )


def _is_noun_after_preposition(
    preposition: str, word: str, next_word: str | None = None
) -> bool:
    """Return whether a word following a preposition should be capitalized."""
    if word in ARTICLES_AND_PRONOUNS or len(word) <= 2:
        return False
    # An adjective in front of its noun ('mit neuen batterien')
    if (
        next_word
        and word.endswith(("e", "en", "em", "er", "es"))
        and not _is_noun(word)
        and _is_noun(next_word)
    ):
        return False
    if word in TIME_ADVERBS:
        return preposition in CONTRACTED_PREPOSITIONS
    # 'zu' + infinitive ('zu reparieren')
    return not (preposition == "zu" and word.endswith("en"))


def _participle_stem_to_infinitive(stem: str) -> str:
    """Build an infinitive from a participle stem ('liefer' -> 'liefern')."""
    if stem.endswith(("iel", "eer", "eel")):
        return stem + "en"
    return stem + ("n" if stem.endswith(("e", "er", "el")) else "en")


def participle_to_infinitive(word: str) -> str | None:
    """Return the infinitive of a German participle, None if it cannot be derived."""
    lowered = word.lower()
    if lowered in PARTIZIP_TO_INFINITIVE:
        return PARTIZIP_TO_INFINITIVE[lowered]
    if lowered.endswith("iert"):
        return lowered[:-1] + "en"
    if lowered.startswith("ge") and lowered.endswith("t") and len(lowered) > 4:
        return _participle_stem_to_infinitive(lowered[2:-1])
    for prefix in SEPARABLE_PREFIXES:
        if lowered.startswith(prefix) and len(lowered) > len(prefix) + 2:
            rest = lowered[len(prefix) :]
            if rest.startswith("ge") and (core := participle_to_infinitive(rest)):
                return prefix + core
    if lowered.startswith(INSEPARABLE_PREFIXES) and lowered.endswith("t"):
        return _participle_stem_to_infinitive(lowered[:-1])
    return None


def _rewrite_as_task(text: str, after_reminder_opener: bool) -> str:
    """Reduce a whole sentence to its task, or leave it exactly as it was."""
    if (
        _RE_KEEP_SENTENCE.search(text)
        or _RE_QUESTION_START.match(text)
        or _RE_LEADING_MODAL.match(text)
        or "?" in text
    ):
        return text
    s = text.rstrip(" .!")

    if match := _RE_SUBJECT_MODAL_START.match(s):
        s = s[match.end() :]
    elif match := _RE_INVERTED_MODAL.match(s):
        s = f"{match.group(1)} {match.group(2)}"

    if match := _RE_PASSIVE_MODAL.match(s):
        subject, rest, participle = match.group(1, 2, 3)
        infinitive = participle_to_infinitive(participle)
        if infinitive is None or _RE_CLAUSE_WORD.search(rest):
            return text
        return " ".join(part for part in (subject, rest.strip(), infinitive) if part)

    if match := _RE_FINAL_PASSIVE.match(s):
        before, participle = match.group(1, 2)
        infinitive = participle_to_infinitive(participle)
        if infinitive is None:
            return text
        return f"{before or ''}{infinitive}"

    if match := _RE_FINAL_MODAL.match(s):
        before, last_word = match.group(1, 2)
        return f"{before or ''}{participle_to_infinitive(last_word) or last_word}"

    if (match := _RE_ACTIVE_MODAL.match(s)) and not _RE_CLAUSE_WORD.search(match.group(3)):
        if match.group(1).lower() in SUBJECT_PRONOUNS:
            return text
        return f"{match.group(1)} {match.group(3)}"

    if match := _RE_STATE.match(s) or _RE_FINAL_STATE.match(s):
        return f"{match.group('subject')} {match.group('state')}"

    if after_reminder_opener:
        s = _RE_ZU_COMPOUND.sub(r"\1\2", s)
        s = _RE_ZU_INFINITIVE.sub(r"\1", s)
    return s


def _drop_fillers(text: str) -> str:
    """Remove words that carry no information in a short task."""
    s = _RE_NOCH_MAL.sub("nochmal", text)
    s = _RE_FILLERS.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip(" ,")


def _drop_articles(text: str) -> str:
    """Drop articles, keeping those of prepositional phrases and genitives.

    'heute die kinder' -> 'heute kinder', but 'in die werkstatt' and 'tür der
    garage' are preserved.
    """
    raw_words = text.split()
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
            filtered_words.append(w)
    return " ".join(filtered_words).strip()


def _format_words(text: str) -> str:
    """Correct spelling and apply German capitalization, word by word."""
    words = text.split()
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
            word_cap = capitalize_first(clean_w)
        elif _is_noun(lower_w):
            word_cap = capitalize_first(clean_w)
        elif (
            words[idx - 1].lower() in PREPOSITION_TRIGGERS
            and _is_noun_after_preposition(
                words[idx - 1].lower(),
                lower_w,
                words[idx + 1].lower().strip(".,!?:;") if idx + 1 < len(words) else None,
            )
        ):
            word_cap = capitalize_first(clean_w)
        elif (
            idx > 1
            and words[idx - 2].lower() in PREPOSITION_TRIGGERS
            and words[idx - 1].lower() in ARTICLES_AND_PRONOUNS
            and len(lower_w) > 2
        ):
            word_cap = capitalize_first(clean_w)
        else:
            word_cap = clean_w

        formatted_words.append(f"{prefix_punct}{word_cap}{suffix_punct}")

    return " ".join(formatted_words)


def format_typed_text(raw_text: str) -> str:
    """Correct typos of a typed text and otherwise keep what the person wrote."""
    words = raw_text.strip().split()
    corrected: list[str] = []
    for word in words:
        core = word.strip("\"'([<>)]>.,!?:;")
        replacement = SPELL_CORRECTIONS.get(core.lower())
        corrected.append(word.replace(core, replacement) if core and replacement else word)
    if corrected:
        corrected[0] = capitalize_first(corrected[0])
    return " ".join(corrected)


def build_glossary(custom_terms: str | None, names: list[str]) -> dict[str, str]:
    """Build the spellings to enforce from names and the person's own list."""
    return merge_glossary(BUILTIN_GLOSSARY, custom_terms, names, _RE_SENTENCE_WORD)


def clean_and_format_idea_text(
    raw_text: str, glossary: dict[str, str] | None = None
) -> str:
    """Reduce a spoken German sentence to a short task note.

    Transforms 'im brainstorm dass heute die kinder vom flughafen abgeholt werden
    müssen' into 'Heute Kinder vom Flughafen abholen'. A sentence that cannot be
    reduced completely keeps its articles and only gets its spelling corrected.
    """
    if not raw_text or not raw_text.strip():
        return ""

    s = raw_text.strip()

    # 1. Strip conversational prefixes repeatedly
    after_reminder_opener = False
    changed = True
    while changed:
        changed = False
        if match := REMINDER_OPENER.match(s):
            s = s[match.end() :].strip()
            after_reminder_opener = True
            changed = True
        for pat in CONVERSATIONAL_PREFIXES:
            new_s = re.sub(pat, "", s, flags=re.IGNORECASE).strip()
            if new_s != s:
                s = new_s
                changed = True
    s = _RE_NOT_FORGET_SUFFIX.sub("", s).strip()

    # 2. Reduce the sentence to a task, all or nothing
    s = _rewrite_as_task(s, after_reminder_opener)

    # 3. Only a real short task loses its fillers and articles
    if not (
        _RE_SENTENCE_WORD.search(s) or _RE_QUESTION_START.match(s) or "?" in s
    ):
        s = _drop_articles(_drop_fillers(s))

    # 4. Spelling and capitalization
    result = _format_words(s)
    result = apply_glossary(result, BUILTIN_GLOSSARY if glossary is None else glossary)
    # Strip any trailing punctuation that might look like conversational fragment
    if not result.endswith("?"):
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
    return due, strip_reminder_words(remaining)


def strip_reminder_words(text: str) -> str:
    """Remove the words that only connect a reminder to its content."""
    remaining = re.sub(r"\s+", " ", text).strip(" ,.")
    previous = None
    while previous != remaining:
        previous = remaining
        remaining = _RE_LEADING_WORDS.sub("", remaining)
        remaining = _RE_TRAILING_WORDS.sub("", remaining).strip(" ,.")
    return remaining


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


# A spoken date only counts when it clearly means a day; 'am morgen' or a lone
# 'abends' describes the task, and a past or recurring day is not a due date
_RE_SPOKEN_DATE = re.compile(
    r"\b(?:übermorgen|heute)\b"
    r"|(?<!am )(?<!jeden )(?<!guten )(?<!den )\bmorgen\b"
    rf"|{_RE_RELATIVE.pattern}"
    rf"|{_RE_NEXT_WEEK.pattern}"
    rf"|\b(?:{'|'.join(_WEEKDAYS)})\b"
    r"|\b\d{1,2}\.\s?\d{1,2}\.(?:\s?\d{2,4})?(?![\d.])"
    rf"|{_RE_MONTH_DATE.pattern}",
    re.IGNORECASE,
)
_RE_NO_DUE_DATE = re.compile(
    r"\b(?:seit|letzte[nrs]?|vorige[nrs]?|jede[nrs]?|gestern|vorgestern|war|waren|"
    r"wurde|wurden)\b|\?",
    re.IGNORECASE,
)
_RE_DATE_CONNECTOR = re.compile(
    r"\b(?:bis\s+(?:spätestens\s+)?|spätestens\s+|für\s+|ab\s+)"
    rf"(?=(?:übermorgen|heute|morgen|nächste|kommende|am\s|\d|{'|'.join(_WEEKDAYS)})\b)",
    re.IGNORECASE,
)

_SPOKEN_PRIORITIES: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"\b(?:ganz\s+|sehr\s+)?(?:dringend|eilig|sofort)\b", re.IGNORECASE),
        PRIORITY_URGENT,
    ),
    (
        re.compile(
            r"\b(?:ganz\s+|sehr\s+|total\s+|super\s+|extrem\s+)?wichtig\b|\bunbedingt\b",
            re.IGNORECASE,
        ),
        PRIORITY_HIGH,
    ),
    (
        re.compile(r"\birgendwann(?:\s+mal)?\b|\bwenn\s+zeit\s+ist\b", re.IGNORECASE),
        PRIORITY_LOW,
    ),
)
_RE_NO_SPOKEN_PRIORITY = re.compile(
    r"\b(?:nicht|kein\w*|wie|so)\s+(?:so\s+|ganz\s+|sehr\s+)?(?:dringend|eilig|wichtig)\b"
    r"|\b(?:ist|sind|wird|war)\s+(?:\w+\s+)?(?:dringend|eilig|wichtig)\b|\?",
    re.IGNORECASE,
)
# The verb directly after a category name shows that it is the subject of the sentence
_RE_VERB_AFTER_SUBJECT = re.compile(
    r"^(?:muss|müssen|müsste|müssten|soll|sollen|sollte|sollten|braucht|brauchen|ist|"
    r"sind|war|waren|hat|haben|kann|können|könnte|könnten|wird|werden|fehlt|fehlen|"
    r"läuft|laufen|geht|gehen|funktioniert|funktionieren|klemmt|spinnt|hängt)\b",
    re.IGNORECASE,
)


def starts_with_verb(text: str) -> bool:
    """Return whether a text begins with a verb, so what stood before it was the subject."""
    return bool(_RE_VERB_AFTER_SUBJECT.match(text))


def extract_spoken_due(text: str, now: datetime) -> tuple[datetime | None, str]:
    """Find a date in a spoken note, returning it and the text without it.

    The text stays as it is if nothing is left of it or the time has passed, which
    keeps 'heute' in the text in the evening instead of reminding at once.
    """
    if _RE_NO_DUE_DATE.search(text) or not _RE_SPOKEN_DATE.search(text):
        return None, text
    due, remaining = parse_due(_RE_DATE_CONNECTOR.sub("", text), now)
    if due is None or due <= now or not remaining:
        return None, text
    return due, remaining


def extract_spoken_priority(text: str) -> tuple[str, str | None]:
    """Find a priority anywhere in a spoken note, returning the text without it."""
    if _RE_NO_SPOKEN_PRIORITY.search(text):
        return text, None
    for pattern, priority in _SPOKEN_PRIORITIES:
        remaining = re.sub(r"\s+", " ", pattern.sub(" ", text, count=1)).strip(" ,.")
        if remaining != text.strip(" ,.") and remaining:
            return remaining, priority
    return text, None


_RE_NEGATION = re.compile(r"\b(?:nicht|nie|niemals|nichts|kein\w*)\b", re.IGNORECASE)
_AI_ALLOWED_WORDS: frozenset[str] = frozenset(
    {
        "der", "die", "das", "den", "dem", "des", "ein", "eine", "einen", "einem",
        "einer", "und", "für", "fürs", "von", "vom", "zum", "zur", "mit", "auf", "aufs",
        "aus", "bei", "beim", "nach", "ans", "ins", "als", "wegen",
    }
)


def validate_ai_rewrite(spoken: str, rule_text: str, candidate: str) -> str | None:
    """Return the AI's text if it only shortens what was said, otherwise None."""
    return validate_rewrite(
        spoken, rule_text, candidate, _RE_NEGATION, _AI_ALLOWED_WORDS, r"[a-zäöüß]+"
    )


def ai_cleanup_prompt(spoken_text: str, rule_text: str) -> str:
    """Return the instructions for an AI to improve a spoken note."""
    return (
            "Forme diese gesprochene Notiz in einen kurzen deutschen Stichpunkt für "
            "eine Aufgabenliste um, mit richtiger Rechtschreibung und Großschreibung. "
            "Antworte nur mit dem Stichpunkt. Erfinde keine Inhalte, Namen oder Zahlen "
            "und ändere nie eine Verneinung. Lasse Füllwörter und Wörter wie 'wichtig' "
            "oder 'dringend' weg. Eine Aufgabe endet mit dem Verb im Infinitiv.\n"
            f"Gesprochen: {spoken_text}\n"
            f"Bisheriger Stichpunkt: {rule_text}"
    )


CATEGORY_ALIASES: dict[str, list[str]] = {
    CATEGORY_HOME_GARDEN: [
        "haus & garten",
        "haus und garten",
        "haus & gartenbereich",
        "garten",
        "haus",
        "gartenarbeit",
        "gartenbereich",
        "balkon",
        "terrasse",
        "terasse",
    ],
    CATEGORY_SMARTHOME: [
        "smarthome",
        "smart home",
        "hausautomation",
        "homeautomation",
        "home assistant",
        "homeassistant",
        "iot",
    ],
    CATEGORY_PROJECTS: [
        "projekte",
        "projekt",
        "bauprojekte",
        "bauprojekt",
        "bastelprojekte",
        "bastelprojekt",
        "basteln",
        "werkstatt",
        "diy",
    ],
    CATEGORY_DAILY: [
        "alltag",
        "haushalt",
        "erledigungen",
        "erledigung",
        "einkauf",
        "einkäufe",
        "familie",
        "privat",
        "persönlich",
    ],
    CATEGORY_BRAINSTORM: [
        "brainstorm",
        "brainstorming",
        "brain storm",
        "brain-storm",
        "brainstorm hub",
        "brainstorm app",
        "mindmap",
        "mind map",
    ],
}

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    CATEGORY_BRAINSTORM: [
        "brainstorm",
        "brainstorming",
        "mindmap",
        "synapse",
        "synapsen",
        "gedanken",
        "geistesblitz",
        "ideenkarte",
        "ideensammlung",
        "kartendarstellung",
        "visualisierung",
        "radial",
        "app",
        "notiz-app",
        "logbuch",
        "funktion",
        "karten",
    ],
    CATEGORY_HOME_GARDEN: [
        "garten",
        "rasen",
        "rasenmähen",
        "rasensprengen",
        "mähen",
        "sprengen",
        "blume",
        "blumen",
        "sonnenblume",
        "sonnenblumen",
        "rose",
        "rosen",
        "pflanze",
        "pflanzen",
        "beet",
        "hochbeet",
        "hecke",
        "heckenschere",
        "unkraut",
        "gießen",
        "wässern",
        "balkon",
        "terrasse",
        "terasse",
        "baum",
        "bäume",
        "ast",
        "äste",
        "schneiden",
        "laub",
        "kompost",
        "dünger",
        "düngen",
        "gewächshaus",
        "pool",
        "poolpumpe",
        "poolroboter",
        "zaun",
        "schuppen",
        "dachrinne",
        "gartenhaus",
        "trampolin",
        "vogelhaus",
        "grill",
        "sandkasten",
        "bewässerung",
        "bewässern",
        "tomate",
        "tomaten",
    ],
    CATEGORY_SMARTHOME: [
        "smarthome",
        "smart home",
        "home assistant",
        "homeassistant",
        "automation",
        "automatisieren",
        "shelly",
        "zigbee",
        "zha",
        "z2m",
        "zigbee2mqtt",
        "esphome",
        "esp32",
        "esp8266",
        "tasmota",
        "mqtt",
        "bwm",
        "bewegungsmelder",
        "präsenzmelder",
        "präsenz",
        "sensor",
        "sensoren",
        "temperatur",
        "feuchtigkeit",
        "luftfeuchtigkeit",
        "licht",
        "lichter",
        "beleuchtung",
        "lampe",
        "lampen",
        "dimmen",
        "dimmer",
        "steckdose",
        "steckdosen",
        "schalter",
        "relais",
        "frigate",
        "kamera",
        "kameras",
        "dashboard",
        "lovelace",
        "tablet",
        "wlan",
        "wifi",
        "netzwerk",
        "router",
        "fritzbox",
        "blueprint",
        "yaml",
        "alexa",
        "echo",
        "thermostat",
        "heizkörper",
        "heizung",
        "bkw",
        "balkonkraftwerk",
        "wechselrichter",
        "inverter",
        "stromzähler",
        "powercalc",
    ],
    CATEGORY_PROJECTS: [
        "projekt",
        "projekte",
        "erweitern",
        "feature",
        "entwicklung",
        "entwickeln",
        "programmieren",
        "implementieren",
        "konzept",
        "bauen",
        "basteln",
        "umbau",
        "umbauen",
        "renovieren",
        "renovierung",
        "streichen",
        "lackieren",
        "abschleifen",
        "schleifen",
        "bohren",
        "bohrer",
        "sägen",
        "kreissäge",
        "werkstatt",
        "werkzeug",
        "3d-druck",
        "3d druck",
        "drucken",
        "filament",
        "löten",
        "lötkolben",
        "schrauben",
        "dübel",
        "holz",
        "brett",
        "bretter",
        "latte",
        "latten",
        "metall",
        "konstruieren",
        "designen",
        "reparieren",
        "reparatur",
        "werkbank",
    ],
    CATEGORY_DAILY: [
        "alltag",
        "haushalt",
        "einkaufen",
        "einkauf",
        "einkaufsliste",
        "supermarkt",
        "kaufen",
        "besorgen",
        "mitbringen",
        "apotheke",
        "medikament",
        "kinder",
        "kind",
        "flughafen",
        "bahnhof",
        "schule",
        "kita",
        "kindergarten",
        "arzt",
        "zahnarzt",
        "termin",
        "rechnung",
        "bezahlen",
        "überweisen",
        "brief",
        "post",
        "paket",
        "abholen",
        "abgeben",
        "wäsche",
        "waschen",
        "bügeln",
        "trockner",
        "spülmaschine",
        "wischen",
        "saugen",
        "staubsauger",
        "putzen",
        "fenster",
        "müll",
        "biotonne",
        "restmüll",
        "altpapier",
        "gelber sack",
        "müllabfuhr",
        "auto waschen",
        "tüv",
        "tanken",
        "ölwechsel",
        "tierarzt",
        "futter",
        "kochen",
        "rezept",
        "backen",
        "geburtstag",
        "geschenk",
        "brot",
        "milch",
        "mittagessen",
        "abendessen",
    ],
}

PACK = LanguagePack(
    code="de",
    default_categories=tuple(DEFAULT_CATEGORIES),
    category_names={
        CATEGORY_HOME_GARDEN: "Haus & Garten",
        CATEGORY_SMARTHOME: "Smarthome",
        CATEGORY_PROJECTS: "Projekte",
        CATEGORY_DAILY: "Alltag",
        CATEGORY_BRAINSTORM: "Brainstorm",
    },
    category_aliases=CATEGORY_ALIASES,
    category_keywords=CATEGORY_KEYWORDS,
    and_word="und",
    category_stop_words=frozenset({"und", "der", "die", "das"}),
    alias_lead=(
        r"^(?:(?:für|fürs|im|in\s+der|in\s+dem|auf\s+der|auf\s+dem|am|beim|zum|zur)\s+"
        r"(?:den\s+|das\s+|die\s+|dem\s+)?)?"
    ),
    alias_tail=r"(:|\s+dass\s+|\s+ich\s+|\s+wir\s+|\s*,\s*|\s+)(.+)$",
    topic_pattern=re.compile(
        r"^(?:im\s+|in\s+|für\s+|beim\s+)?(?:projekt|thema|bereich)\s+"
        r"([a-zA-Z0-9äöüÄÖÜß\-_&]{2,30})(?::|\s+dass\s+|\s+ich\s+|\s+wir\s+|\s*,\s*|\s+)(.+)$",
        re.IGNORECASE,
    ),
    priority_prefixes=(
        (
            re.compile(
                r"^(?:dringend|sofort|eilig|asap|notfall|höchste\s+priorität|"
                r"prio\s+dringend|prio\s+sofort)(?::|\s+|,)\s*(.+)$",
                re.IGNORECASE,
            ),
            PRIORITY_URGENT,
        ),
        (
            re.compile(
                r"^(?:wichtig|hohe\s+priorität|priorität\s+hoch|prio\s+1|prio\s+hoch)"
                r"(?::|\s+|,)\s*(.+)$",
                re.IGNORECASE,
            ),
            PRIORITY_HIGH,
        ),
        (
            re.compile(
                r"^(?:niedrige\s+priorität|priorität\s+niedrig|prio\s+3|prio\s+niedrig|"
                r"wenn\s+zeit(?:\s+ist)?|später\s+mal|irgendwann|optional)"
                r"(?::|\s+|,)\s*(.+)$",
                re.IGNORECASE,
            ),
            PRIORITY_LOW,
        ),
        (
            re.compile(
                r"^(?:normale\s+priorität|mittlere\s+priorität|priorität\s+normal|"
                r"priorität\s+mittel|prio\s+2|prio\s+mittel)(?::|\s+|,)\s*(.+)$",
                re.IGNORECASE,
            ),
            PRIORITY_MEDIUM,
        ),
    ),
    clean_text=clean_and_format_idea_text,
    format_typed=format_typed_text,
    extract_due=extract_spoken_due,
    parse_due=parse_due,
    strip_reminder_words=strip_reminder_words,
    extract_priority=extract_spoken_priority,
    starts_with_verb=starts_with_verb,
    build_glossary=build_glossary,
    validate_ai_rewrite=validate_ai_rewrite,
    ai_cleanup_prompt=ai_cleanup_prompt,
)
