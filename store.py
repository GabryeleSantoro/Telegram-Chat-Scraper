"""Saves every message from the source chat, and every shop seen in its alerts, in a local SQLite db (messages.db)."""

import re
import sqlite3

# alert header: "🚨 POPSPLANET ALERT DROP! 🚨", "🔥 AMAZON DROP 🔥"
HEADER = re.compile(r"^\W*(.+?)\s+(?:ALERT\s+)?DROP\b")


def open_db(path="messages.db"):
    db = sqlite3.connect(path)
    db.execute("PRAGMA journal_mode=WAL")  # fast writes, and you can query the db while the listener runs
    db.execute("PRAGMA synchronous=NORMAL")
    db.execute("""CREATE TABLE IF NOT EXISTS messages (
        chat_id INTEGER, id INTEGER, date TEXT, sender_id INTEGER, text TEXT, matched INTEGER,
        PRIMARY KEY (chat_id, id))""")
    db.execute("CREATE TABLE IF NOT EXISTS stores (name TEXT PRIMARY KEY, url TEXT)")
    if not db.execute("SELECT 1 FROM stores").fetchone():  # fill from messages saved before the table existed
        with db:
            for (text,) in db.execute("SELECT text FROM messages").fetchall():
                _save_store(db, text)
    return db


def save(db, message, text, matched):
    with db:  # commits
        db.execute("INSERT OR REPLACE INTO messages VALUES (?, ?, ?, ?, ?, ?)",
                   (message.chat_id, message.id, message.date.isoformat(), message.sender_id, text, int(matched)))
        _save_store(db, text)


def store_of(text):
    """(name, url) of the shop a drop alert comes from, None if the text isn't one."""
    header = HEADER.match(text)
    if not header:
        return None
    # the "Vai sul Sito" button, else the domain of the first link (Amazon only has a product "Acquista" link)
    site = re.search(r"Vai sul Sito → (\S+)", text) or re.search(r"→ (https?://[^/\s]+)", text)
    return header[1].title(), site and site[1]


def _save_store(db, text):
    if store := store_of(text):
        db.execute("INSERT OR IGNORE INTO stores VALUES (?, ?)", store)


if __name__ == "__main__":
    from datetime import datetime, timezone
    from types import SimpleNamespace

    db = open_db(":memory:")
    msg = SimpleNamespace(chat_id=1, id=7, date=datetime(2026, 10, 31, tzinfo=timezone.utc), sender_id=42)
    save(db, msg, "30° Anniversario ITA", True)
    save(db, msg, "edited", False)  # same message again replaces, no duplicate
    assert db.execute("SELECT id, date, text, matched FROM messages").fetchall() == [(7, "2026-10-31T00:00:00+00:00", "edited", 0)]
    assert db.execute("SELECT * FROM stores").fetchall() == []  # not an alert

    assert store_of("🚨 POPSPLANET ALERT DROP! 🚨\n• Mazzo → https://www.popsplanet.it/products/x\n"
                    "🛒 Vai sul Sito → https://www.popsplanet.it/collections/pokemon-card-game") \
        == ("Popsplanet", "https://www.popsplanet.it/collections/pokemon-card-game")
    assert store_of("🔥 AMAZON DROP 🔥\n🛒 Acquista → https://www.amazon.it/dp/B0G1XB2STM?tag=x") == ("Amazon", "https://www.amazon.it")
    assert store_of("🏆 TORNEO DI NOVEMBRE 🏆\n👉 Apri ora con /spacchetta") is None
    save(db, SimpleNamespace(chat_id=1, id=8, date=msg.date, sender_id=42), "🔥 AMAZON DROP 🔥\n🛒 Acquista → https://www.amazon.it/dp/B0", False)
    assert db.execute("SELECT * FROM stores").fetchall() == [("Amazon", "https://www.amazon.it")]
    print("ok")
