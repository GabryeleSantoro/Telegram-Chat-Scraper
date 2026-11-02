"""Matches restock alerts for the Italian Pokémon TCG 30th anniversary set."""

import re

# IT name "30° Anniversario", EN name "30th Celebration"
SET_30TH = re.compile(r"30\s*(?:°|º|th|esimo)?\s*(?:anniversario|anniversary|celebration)", re.I)
ITA_TAG = re.compile(r"\bita\b|\bitalian[aeio]?\b|🇮🇹", re.I)
OTHER_LANG = re.compile(
    r"\b(?:eng?|english|inglese|jpn?|jap|japanese|giapponese|kor|korean|coreano|chn|chinese|cinese)\b|🇬🇧|🇺🇸|🇯🇵",
    re.I,
)


def is_30th_italian(text: str) -> bool:
    # ponytail: keyword heuristic, the bot's real format is unknown; tune the regexes above if it misses
    if not SET_30TH.search(text):
        return False
    # explicit ITA tag wins; otherwise the Italian set name counts unless another language is tagged
    return bool(ITA_TAG.search(text)) or ("anniversario" in text.lower() and not OTHER_LANG.search(text))


def is_bot_promo(text: str) -> bool:
    # the bot's monthly tournament reminder ("🏆 TORNEO DI ... 🏆 ... /spacchetta") names 30° Anniversario prizes but isn't a drop
    return "/spacchetta" in text


if __name__ == "__main__":
    assert is_bot_promo("🏆 TORNEO DI NOVEMBRE 🏆\n\nvincono Mini Tin del 30° Anniversario a testa.\n\n👉 Apri ora con /spacchetta")
    assert not is_bot_promo("🚨 CARDVERSE ALERT DROP! 🚨\nPokemon 30° Anniversario Booster Box ITA")
    assert is_30th_italian("🔥 RESTOCK Pokémon 30° Anniversario Booster Box ITA - Amazon")
    assert is_30th_italian("Pokemon GCC 30° Anniversario Collezione Premium")
    assert is_30th_italian("30th Celebration Elite Trainer Box (ITA)")
    assert is_30th_italian("Carte italiane 30 anniversario 🇮🇹")
    assert not is_30th_italian("30th Celebration Elite Trainer Box ENG")
    assert not is_30th_italian("30° Anniversario Booster Bundle JAP")
    assert not is_30th_italian("30th Celebration ETB - capacita limitata EN")
    assert not is_30th_italian("Ascended Heroes Booster Box ITA")
    print("ok")
