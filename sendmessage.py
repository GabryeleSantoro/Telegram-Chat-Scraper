import requests
from config import TOKEN,chat_id

#This sections is about sending the message to another channel. To fill the fields use the config.py file 
def sendMessage(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    print(requests.get(url).json()) # this sends the message and prints it on command line