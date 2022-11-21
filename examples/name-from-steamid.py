from CSGOTelnet import CommandHandler
from CSGOTelnet import Logger
import time
import random

# Your Steam ID and API key are used to get your name to check if a message is from owner or not
# You can find your API key here: https://steamcommunity.com/dev/apikey
YOUR_STEAMID = "76561198446630909"
APIKEY = "API KEY HERE"

COMMAND_PREFIX = "!"
ECHO_COMMAND_PREFIX = "###"
IP = "127.0.0.1"
PORT = 2121

handler = CommandHandler.CommandHandler(COMMAND_PREFIX, ECHO_COMMAND_PREFIX, Logger.LogLevel.DEBUG)

# This will make a Steam API call and get your profile name.
handler.set_name_from_steamid(APIKEY, YOUR_STEAMID)

handler.start(IP, PORT)