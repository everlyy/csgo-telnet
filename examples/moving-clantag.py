from CSGOTelnet import CommandHandler
from CSGOTelnet import Logger
import time
import threading

YOUR_NAME = "everly"
IP = "127.0.0.1"
PORT = 2121

# The program will cycle through these clantags
clanids = [
	43162082, # katbot 
	43162083, # atbot k
	43162084, # tbot ka
	43162085, # bot kat
	43162088, # ot katb
	43162091  # t katbo
]

handler = CommandHandler.CommandHandler("!", "###", Logger.LogLevel.INFO)

do_clantag = False
def clan_thread_func(handler):
	global do_clantag
	index = 0
	set_normal = False

	while True:
		if do_clantag:
			set_normal = False
			handler.queue(f"cl_clanid {clanids[index % len(clanids)]}")
			index += 1
		else:
			if not set_normal:
				handler.queue("cl_clanid 0")
				set_normal = True
		time.sleep(.5)

def clan(message, args):
	global do_clantag, handler
	do_clantag = not do_clantag
	handler.queue(f"{'say_team' if message.is_team_chat() else 'say'} moving clantag: {'yes' if do_clantag else 'no'}")

if __name__ == "__main__":
	handler.set_owner_name(YOUR_NAME)
	handler.commands.add_owner_command("clan", "moving clantag", clan)

	thread = threading.Thread(target=clan_thread_func, args=(handler, ))
	thread.start()

	handler.start(IP, PORT)
