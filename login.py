import asyncio
import sys
from getpass import getpass

import qrcode
from telethon import TelegramClient, errors
from dotenv import load_dotenv
import os
load_dotenv()

api_id = os.getenv("api_id")
api_hash = os.getenv("api_hash")

# QR login instead of phone + code: Telegram often doesn't deliver the code to third-party apps
async def qr_login(client):
    await client.connect()
    if await client.is_user_authorized():
        return
    qr = await client.qr_login()
    while True:
        image = qrcode.QRCode()
        image.add_data(qr.url)
        image.print_ascii(tty=sys.stdout.isatty(), invert=True)  # tty: fixed colors, scannable on any terminal theme
        print("Scan it with your phone: Telegram > Settings > Devices > Link Desktop Device")
        try:
            await qr.wait()
            return
        except asyncio.TimeoutError:
            await qr.recreate()  # QR expires after ~30s, show a fresh one
        except errors.SessionPasswordNeededError:
            await client.sign_in(password=getpass("2FA password: "))
            return

def login():
    # ponytail: sleep through Telegram flood waits up to 1h (default 60s crashes the backfill); longer ones still raise
    client = TelegramClient('anon', api_id, api_hash, flood_sleep_threshold=3600)
    client.loop.run_until_complete(qr_login(client))
    return client
