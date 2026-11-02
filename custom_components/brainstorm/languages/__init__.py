"""Everything that depends on a language, one module per language.

To add a language, create a module with a PACK and list it in PACKS. Tests run over
all listed languages and report anything that is missing.
"""
from __future__ import annotations

import re

from . import de, en, neutral
from .common import LanguagePack

PACKS: dict[str, LanguagePack] = {pack.code: pack for pack in (de.PACK, en.PACK)}

# Any language's name of a standard category leads to its neutral key, so that
# stored categories work in every language without being renamed
CATEGORY_KEYS: dict[str, str] = {
    name: key for pack in PACKS.values() for key, name in pack.category_names.items()
}


def get_pack(language: str | None) -> LanguagePack:
    """Return the rules of a language like 'de' or 'en-GB', or the neutral rules."""
    code = re.split(r"[-_]", language or "", maxsplit=1)[0].lower()
    return PACKS.get(code, neutral.PACK)
