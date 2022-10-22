from operator import imod
from telethon import events
from login import login
from sendmessage import sendMessage

from config import chat_name

def main():
    client = login()
    @client.on(events.NewMessage(chats=chat_name)) #To config the chat use the config.py file
    async def my_event_handler(event):
        print(event.raw_text) #prints the message. From here you'll be able to do everything with your message.
        
    client.start()
    client.run_until_disconnected() #allows client to run forever

main()  