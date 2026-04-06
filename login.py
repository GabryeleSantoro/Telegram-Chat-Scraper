from telethon import TelegramClient
import asyncio
from dotenv import load_dotenv
import os
load_dotenv()

api_id = os.getenv("api_id")
api_hash = os.getenv("api_hash")
 
def login():
    client = TelegramClient('anon', api_id, api_hash)
    client.start()
    return client