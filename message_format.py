"""Estrae testo messaggio + URL nascosti nel testo + URL dai pulsanti."""

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
