from pathlib import Path

from telethon import events
from login import login
from message_format import format_complete_message
from pokemon_filter import is_30th_italian

from dotenv import load_dotenv
import os
load_dotenv()

chat_name = os.getenv("chat_name")  # source chat, e.g. @pokemon_alert_24_bot
target_chat = os.getenv("target_chat")  # where matching messages are sent
STATE = Path("last_id.txt")  # last processed message id, so a restart doesn't resend history

def main():
    if not chat_name or not target_chat:
        raise SystemExit("Set chat_name and target_chat in .env")
    client = login()
    last_id = int(STATE.read_text()) if STATE.exists() else 0

    async def relay(message):
        nonlocal last_id
        text = format_complete_message(message)
        if is_30th_italian(text):
            await client.send_message(target_chat, text)
        last_id = max(last_id, message.id)
        STATE.write_text(str(last_id))

    @client.on(events.NewMessage(chats=chat_name)) #To config the chats use the .env file
    async def my_event_handler(event):
        await relay(event.message)

    async def backfill():
        async for message in client.iter_messages(chat_name, min_id=last_id, reverse=True):
            await relay(message)

    client.loop.run_until_complete(backfill()) #reads all the old messages first
    client.run_until_disconnected() #allows client to run forever

main()
