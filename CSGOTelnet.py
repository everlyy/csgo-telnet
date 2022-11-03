import telnetlib
import time
import re

class ChatCommand:
	def __init__(self, name, description, callback, is_global):
		self.name = name
		self.description = description
		self.callback = callback
		self.is_global = is_global

	def __str__(self):
		return self.name

class EchoCommand:
	def __init__(self, name, description, callback):
		self.name = name
		self.description = description
		self.callback = callback

	def __str__(self):
		return self.name

class ChatMessage:
	def __init__(self, full_message, owner_name):
		ct_team_prefix = "(Counter-Terrorist)"
		t_team_prefix = "(Terrorist)"
		dead_prefix = "*DEAD*"
		name_char_separator = " : "

		# I don't know why this appears after everyone's name, but it's making parsing messages alot easier
		char_after_name = "\u200E"

		self.full_message = full_message
		self.pre_content = self.full_message.split(name_char_separator, maxsplit=1)[0].split(char_after_name, maxsplit=1)[0].strip()
		self.message_author = self.pre_content
		self.message_content = self.full_message.split(name_char_separator, maxsplit=1)[1].strip()

		if self.__contains_one_of([ ct_team_prefix, t_team_prefix, dead_prefix ], self.full_message):
			self.message_author = self.full_message[self.full_message.index(" "):].split(char_after_name, maxsplit=1)[0].strip()

		self.is_team_chat = self.__contains_one_of([ ct_team_prefix, t_team_prefix ], self.pre_content)
		self.is_owner = self.message_author == owner_name

	def __contains_one_of(self, items, string):
		for item in items:
			if item in string:
				return True
		return False

	def __str__(self):
		return f"ChatMessage <author:\"{self.message_author}\" is_owner:{self.is_owner} content:\"{self.message_content}\" is_team_chat:{self.is_team_chat}>"


class CommandHandler:
	def __init__(self, chat_prefix, echo_prefix, name, ip, port, enable_logging):
		self.chat_prefix = chat_prefix
		self.echo_prefix = echo_prefix
		self.name = name
		self.ip = ip
		self.port = port

		self.__enable_logging = enable_logging

		self.__message_callback = None
		self.__namechange_callback = None
		self.__chat_commands = []
		self.__echo_commands = []

	def __log(self, message):
		if self.__enable_logging:
			print(f"CommandHandler: {message}")

	def add_command(self, name, description, callback):
		self.__chat_commands.append(ChatCommand(name, description, callback, False))
		self.__log(f"Added command: \"{name}\" -> {callback.__name__}()")

	def add_global_command(self, name, description, callback):
		self.__chat_commands.append(ChatCommand(name, description, callback, True))
		self.__log(f"Added global command: \"{name}\" -> {callback.__name__}()")

	def add_echo_command(self, name, description, callback):
		self.__echo_commands.append(EchoCommand(name, description, callback))
		self.__log(f"Added echo command: \"{name}\" -> {callback.__name__}()")

	def set_message_callback(self, callback):
		self.__message_callback = callback
		self.__log(f"Set __message_callback -> {callback.__name__}()")

	def set_namechange_callback(self, callback):
		self.__namechange_callback = callback
		self.__log(f"Set __namechange_callback -> {callback.__name__}()")

	def start(self):
		self.__log(f"Starting CommandHandler")

		listener = None
		self.__log(f"Connecting to {self.ip}:{self.port}...")
		try:
			listener = telnetlib.Telnet(self.ip, self.port)
			self.__log(f"Connected to {self.ip}:{self.port}")
		except Exception as e:
			self.__log(f"Couldn't create telnet connection to {self.ip}:{self.port} (did you run with `-netconport {self.port}`?)")
			return

		chat_message_pattern = re.compile(r".*[\u200E]\s(@.*|):\s+")
		
		self.__log(f"Waiting for incoming data...")
		self.send("echo CSGOTelnet started.")

		while True:
			incoming = listener.read_until(b"\n")
			self.__log(f"INC {len(incoming)} bytes from {self.ip}:{self.port}")

			decoded = incoming.decode("utf-8").replace("\n", " ").replace("\r", "").strip()

			# Check if incoming data is owner changing their name
			name_change_pattern = re.compile(rf"\* {self.name}\u200E changed name to ")
			if name_change_pattern.match(decoded) is not None:
				old_name = self.name
				self.name = name_change_pattern.sub("", decoded)
				self.__log(f"Name change: {old_name} -> {self.name}")

				# Call namechange callback if it's set
				if self.__namechange_callback:
					self.__namechange_callback(old_name, self.name)

				continue

			if decoded.startswith(self.echo_prefix):
				self.__log(f"Incoming data starts with echo prefix.")
				cmd_str = decoded[len(self.echo_prefix):]
				self.__handle_echo_command(cmd_str)
				continue

			# Check if incoming data is chat message
			if chat_message_pattern.match(decoded) is not None:
				self.__log(f"Incoming data matches chat message regex.")

				# Parse message
				message = ChatMessage(decoded, self.name)
				self.__log(f"Parsed message: {message}")

				self.__handle_chat_message(message)
				continue

	def __handle_echo_command(self, cmd_str):
		for command in self.__echo_commands:
			if cmd_str.startswith(f"{command.name} ") or cmd_str == command.name:
				args = cmd_str[len(command.name) + 1:]
				for cmd in command.callback(args):
					self.send(cmd)
				break

	def __handle_chat_message(self, message):
		if self.__message_callback:
			self.__message_callback(message)

		# Check for help command first
		check = f"{self.chat_prefix}help"
		if message.message_content.startswith(check) and message.is_owner:
			args = message.message_content[len(check):]
			time.sleep(.7)
			self.send(self.__help_command(message, args))

		command = self.__get_cmd_by_name(message, message.message_content)
		if not command:
			return

		args = message.message_content[len(check) + 1:]
		for cmd in command.callback(message, args):
			if message.is_owner and (cmd.startswith("say") or cmd.startswith("say_team")):
				time.sleep(.7)
			self.send(cmd)

	def __get_cmd_by_name(self, message, checkstr):
		for command in self.__chat_commands:
			check = f"{self.chat_prefix}{command.name}"
			if checkstr.startswith(f"{check} ") or checkstr == check:
				if not command.is_global and not message.is_owner:
					continue

				self.__log(f"checkstr matches command {command.name}")
				return command
		return None

	def send(self, cmd):
		send_start_time = time.time()

		encoded = f"{cmd}\n".encode("utf-8")
		self.__log(f"OUT {len(encoded)} bytes to {self.ip}:{self.port}")

		# You need to create a separate telnet connection because CS:GO 
		#  crashes if you send from the same connection you use for receiving  
		sender = telnetlib.Telnet(self.ip, self.port)
		sender.write(encoded)
		sender.close()

		send_time = time.time() - send_start_time
		self.__log(f"send() took {round(send_time * 1000, 2)}ms")

	def __help_command(self, message, args):
		command = self.__get_cmd_by_name(message, self.chat_prefix + args.strip())
		if command:
			return f"{'say_team' if message.is_team_chat else 'say'} {command.name}: {command.description}"

		newline = "\u2029"
		help_message = f"chat prefix: '{self.chat_prefix}' echo prefix: '{self.echo_prefix}'"

		global_cmds = []
		owner_cmds = []
		echo_cmds = []

		for command in self.__chat_commands:
			if not command.is_global:
				owner_cmds.append(command.name)
			else:
				global_cmds.append(command.name)

		for command in self.__echo_commands:
			echo_cmds.append(command.name)

		help_message += f"{newline}echo: "
		help_message += ", ".join(echo_cmds)

		help_message += f"{newline}owner only: "
		help_message += ", ".join(owner_cmds)

		help_message += f"{newline}global: "
		help_message += ", ".join(global_cmds)

		return f"{'say_team' if message.is_team_chat else 'say'} {help_message}"
