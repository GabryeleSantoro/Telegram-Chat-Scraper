from telethon import events
from login import login
from message_format import format_complete_message

from dotenv import load_dotenv
import os
load_dotenv()

chat_name = os.getenv("chat_name")

def main():
    client = login()
    @client.on(events.NewMessage(chats=chat_name)) #To config the chat use the config.py file 
    async def my_event_handler(event):
        print(format_complete_message(event.message))
        
    client.start()
    client.run_until_disconnected() #allows client to run forever

main()  