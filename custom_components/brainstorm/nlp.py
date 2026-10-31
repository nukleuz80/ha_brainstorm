"""Natural language processing and intelligent text normalization for Brainstorm Hub."""
from __future__ import annotations

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
