import CSGOTelnet
import random

YOUR_NAME = "everly"
COMMAND_PREFIX = "!"
ECHO_COMMAND_PREFIX = "ECHOCMD#"
ENABLE_LOGGING = True

IP = "127.0.0.1"
PORT = 2121

def on_message(message):
	print(f"Incoming message: {message}")

def gettime(message, args):
	current_time = time.strftime("%H:%M", time.localtime())
	yield f"{'say_team' if message.is_team_chat else 'say'} It's currently {current_time} for {message.message_author}"

def ping(message, args):
	yield f"say pong! {message.message_author}"

def crosshair_color(args):
	yield f"cl_crosshaircolor 5"
	yield f"cl_crosshaircolor_r {random.randint(0, 255)}"
	yield f"cl_crosshaircolor_g {random.randint(0, 255)}"
	yield f"cl_crosshaircolor_b {random.randint(0, 255)}"

if __name__ == "__main__":
	handler = CSGOTelnet.CommandHandler(COMMAND_PREFIX, ECHO_COMMAND_PREFIX, YOUR_NAME, IP, PORT, ENABLE_LOGGING)
	
	handler.set_message_callback(on_message)

	handler.add_command("time", "shows the current time", gettime)
	handler.add_global_command("ping", "pong", ping)
	handler.add_echo_command("crosshair", "random crosshair color", crosshair_color)

	handler.start()