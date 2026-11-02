"""Estrae testo messaggio + URL nascosti nel testo + URL dai pulsanti."""

import re
from urllib.parse import urlsplit, urlunsplit

from telethon.tl.types import (
    KeyboardButtonSimpleWebView,
    KeyboardButtonUrl,
    KeyboardButtonUrlAuth,
    KeyboardButtonWebView,
    MessageEntityTextUrl,
)


def format_complete_message(message) -> str:
    """
    Testo del messaggio, più:
    - link ipertestuali con testo visibile (MessageEntityTextUrl) con relativo href;
    - etichetta e URL dei pulsanti che espongono un link (inline o tastiera).
    """
    parts: list[str] = []
    if message.message:
        parts.append(message.message)

    text_url_pairs = message.get_entities_text(MessageEntityTextUrl)
    if text_url_pairs:
        parts.append("")
        parts.append("--- Link nel testo (URL non mostrati nel testo) ---")
        for ent, inner in text_url_pairs:
            parts.append(f"{inner} → {ent.url}")

    rm = message.reply_markup
    rows = getattr(rm, "rows", None) if rm else None
    if rows:
        btn_lines: list[str] = []
        for row in rows:
            for btn in row.buttons:
                line = _format_url_button(btn)
                if line:
                    btn_lines.append(line)
        if btn_lines:
            parts.append("")
            parts.append("--- Pulsanti (etichetta → URL) ---")
            parts.extend(btn_lines)

    return "\n".join(parts) if parts else ""


URL = re.compile(r"https?://\S+")
# parametri di tracciamento tolti da qualsiasi URL
TRACKING = re.compile(r"(?:utm_\w+|fbclid|gclid|igshid|mc_[ce]id|srsltid|ref_?)$", re.I)


def clean_links(text: str) -> str:
    """Toglie affiliazioni e tracking dagli URL, e le righe dei pulsanti "Condividi" (t.me/share)."""
    text = "\n".join(line for line in text.splitlines() if "t.me/share/" not in line)
    return URL.sub(lambda m: _clean_url(m.group()), text)


def _clean_url(url: str) -> str:
    try:
        u = urlsplit(url)
    except ValueError:  # URL malformato nel testo: lascialo com'è
        return url
    if "amazon." in u.netloc:  # basta /dp/ASIN: tag affiliato, linkCode, th, psc e /ref=... sono rumore
        return urlunsplit((u.scheme, u.netloc, re.sub(r"/ref=.*", "", u.path), "", ""))
    query = "&".join(p for p in u.query.split("&") if p and not TRACKING.match(p.split("=")[0]))
    return urlunsplit((u.scheme, u.netloc, u.path, query, u.fragment))


def _format_url_button(btn) -> str | None:
    if isinstance(
        btn,
        (
            KeyboardButtonUrl,
            KeyboardButtonUrlAuth,
            KeyboardButtonWebView,
            KeyboardButtonSimpleWebView,
        ),
    ):
        extra = f" (fwd: {btn.fwd_text})" if getattr(btn, "fwd_text", None) else ""
        return f"{btn.text} → {btn.url}{extra}"
    return None


if __name__ == "__main__":
    msg = """Bundle 30º anniversario → https://shop.it/p/x?variant=5707&utm_source=tg&fbclid=abc

--- Pulsanti (etichetta → URL) ---
🛒 Acquista → https://www.amazon.it/dp/B0HKNXM4YL?tag=pokemondrop04-21&linkCode=ogi&th=1&psc=1
🛒 Vai sul Sito → https://agapopvault.com/catalogo?categoria=pokemon
👋 Condividi → https://t.me/share/url?url=https%3A//t.me/pokemon_alert_24_bot&text=Attiva"""
    assert clean_links(msg) == """Bundle 30º anniversario → https://shop.it/p/x?variant=5707

--- Pulsanti (etichetta → URL) ---
🛒 Acquista → https://www.amazon.it/dp/B0HKNXM4YL
🛒 Vai sul Sito → https://agapopvault.com/catalogo?categoria=pokemon"""
    assert _clean_url("https://www.amazon.it/Pokemon-Box/dp/B0HKNXM4YL/ref=sr_1_1?keywords=x") == "https://www.amazon.it/Pokemon-Box/dp/B0HKNXM4YL"
    assert _clean_url("http://[bad") == "http://[bad"
    print("ok")
