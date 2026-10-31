# Telegram-Chat-Scraper
This tool allows to scrape through all messages send in a chat or in a channel on Telegram, regardless the chat is set to private.

## How to install
The first thing to do is to install all the libraries.
First you have to install ```pip3 install asyncio``` to run the asynchronous tasks.
Then the next library to install is telethon with ```pip3 install telethon```

## How to use
To start using this tool copy `.env.example` to `.env` (`cp .env.example .env`) and fill in the values. The filter lives in `pokemon_filter.py`; run `python3 pokemon_filter.py` to check it.

On start the tool reads all the old messages, then keeps listening for new ones. The last processed id is saved in `last_id.txt`: delete it to process the whole history again.

To get your api_id and api_hash you have to log in in this website https://my.telegram.org/auth, that will give all the api key to use.
Filled all the fields go to the folder where the files are located and run ``` main.py ```. Then follow the instruction et voilà, you are officially scraping a telegram chat.

### Responsability
I don't get any responsability for what this tool is used for. I assume is used for legal stuff.
