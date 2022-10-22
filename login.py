from telethon import TelegramClient
import asyncio
from config import api_hash,api_id

#use the config.py file to change your personali id and hash. DO NOT SHARE WITH ANYONE

def login():
    client = TelegramClient('anon', api_id, api_hash)
    client.start()
    return client