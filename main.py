import asyncio
from urllib.parse import urlencode
from urllib.request import urlopen

from telethon import events
from telethon.utils import split_text
from login import login
from message_format import clean_links, format_complete_message
from pokemon_filter import is_30th_italian, is_bot_promo
from store import open_db, save

from dotenv import load_dotenv
import os
load_dotenv()

chat_name = os.getenv("chat_name")  # source chat, e.g. @pokemon_alert_24_bot
target_chat = os.getenv("target_chat")  # where matching messages are sent
bot_token = os.getenv("bot_token")  # matches are sent by this bot: Telegram never notifies you of your own messages

def bot_send(chat_id, text):
    urlopen(f"https://api.telegram.org/bot{bot_token}/sendMessage",
            urlencode({"chat_id": chat_id, "text": text}).encode(), timeout=30)

def main():
    if not chat_name or not target_chat or not bot_token:
        raise SystemExit("Set chat_name, target_chat and bot_token in .env")
    client = login()
    target_id = client.loop.run_until_complete(client.get_peer_id(target_chat))  # "me"/@user/@channel -> Bot API chat_id
    db = open_db()

    @client.on(events.NewMessage(chats=chat_name)) #To config the chats use the .env file
    async def my_event_handler(event):
        text = format_complete_message(event.message)
        if is_bot_promo(text):  # not a drop: don't save or forward
            return
        matched = is_30th_italian(text)
        print(f"[{event.message.date:%Y-%m-%d %H:%M:%S}] {'MATCH ' if matched else ''}{text}\n")
        save(db, event.message, text, matched)  # before sending, so a failed send doesn't lose the message
        if matched:
            # appended link/button URLs can push the text past Telegram's 4096-char limit
            for chunk, _ in split_text(clean_links(text), []):
                await asyncio.to_thread(bot_send, target_id, chunk)

    print(f"Listening for new messages in {chat_name}...")
    client.run_until_disconnected() #allows client to run forever

main()
