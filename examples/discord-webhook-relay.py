from CSGOTelnet import CommandHandler
from CSGOTelnet import Logger
import requests

# Messages will be sent to this webhook
WEBHOOK_URL = "url here"

# This lets you use Discord emojis in CS:GO chat
emojis = {
	"emoji name": "emoji ID",

	# Example emoji:
	"hey": "<:hey:1003422997706719282>"
}

# Name and prefixes don't matter, since this little program doesn't use them
COMMAND_PREFIX = "!"
ECHO_COMMAND_PREFIX = "###"
IP = "127.0.0.1"
PORT = 2121

handler = CommandHandler.CommandHandler(COMMAND_PREFIX, ECHO_COMMAND_PREFIX, Logger.LogLevel.INFO)

def on_message(message):
	content = message.get_content()

	# This prevents @everyone, @here etc.
	content = content.replace("@", "[at]")

	for emoji in emojis:
		content = content.replace(f":{emoji}:", emojis[emoji])

	data = {
		"username": "CS:GO Chat Relay",
		"content": f"{'[TEAM] ' if message.is_team_chat() else ''}**{message.get_author()}**: {content}"
	}

	response = requests.post(WEBHOOK_URL, data=data)
	if not response.ok:
		handler.logger.warn(f"Discord webhook returned {response.status_code}: {response.reason}")
	else:
		handler.logger.info(f"Relayed message from {message.get_author()}")

if __name__ == "__main__":
	handler.set_on_message(on_message)
	handler.start(IP, PORT)