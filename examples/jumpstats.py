from CSGOTelnet import CommandHandler
from CSGOTelnet import Logger
from datetime import datetime
import csv
import re
import time

# Name and prefixes don't matter, since this little program doesn't use them
COMMAND_PREFIX = "!"
ECHO_COMMAND_PREFIX = "###"
IP = "127.0.0.1"
PORT = 2121

# Filename to write jumpstats to.
# Will look something like stats_18_11_2022_22_19_11.csv
date = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
statsfile_name = f"stats_{date}.csv"

handler = CommandHandler.CommandHandler(COMMAND_PREFIX, ECHO_COMMAND_PREFIX, Logger.LogLevel.INFO)

def on_incoming_data(data):
	# Regex to match jumpstats.
	# I only tested them on brutalcs servers, so I don't know if this will work on other servers (probably not).

	#                         distance             strafes    pre                 max        height              sync       crouch    -forward
	lj_pattern = re.compile(r"([0-9]*[.][0-9]+).*\[([0-9]+).* ([0-9]*[.][0-9]+).* ([0-9]+).* ([0-9]*[.][0-9]+).* ([0-9]+)%.*(yes|no).*(yes|no)")
	matches = lj_pattern.findall(data.decode("utf-8"))
	if len(matches) > 0:
		with open(statsfile_name, "a", newline='', encoding='utf-8') as file:
			writer = csv.writer(file)
			to_write = [int(time.time())] + list(matches[0])
			writer.writerow(to_write)
		handler.logger.info(f"Saved jump: {matches[0][0]} units ({matches[0][1]} strafes @ {matches[0][5]}% sync)")

if __name__ == "__main__":
	fields = ["time", "distance", "strafes", "pre", "max", "height", "sync", "crouchjump", "-forward"]
	with open(statsfile_name, "w", newline='', encoding='utf-8') as file:
		writer = csv.writer(file)
		writer.writerow(fields)

	handler.set_on_incoming_data(on_incoming_data)
	handler.start(IP, PORT)