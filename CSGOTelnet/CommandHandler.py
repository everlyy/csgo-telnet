from . import ChatMessage
from . import Commands
from . import Logger
import re
import telnetlib
import threading
import time

class CommandHandler:
	def __init__(self, chat_prefix, echo_prefix, log_level=Logger.LogLevel.INFO):
		self.chat_prefix = chat_prefix
		self.echo_prefix = echo_prefix
		self.commands = Commands.Commands()
		self.owner_name = None

		self.__on_incoming_data_callback = None
		self.__on_message_callback = None
		self.__on_name_change_callback = None

		self.__ip = None
		self.__port = 0
		self.__command_queue = []
		self.__queue_processor_started = False

		self.logger = Logger.Logger(log_level)

	def set_owner_name(self, owner_name):
		self.logger.dbg(f"New owner_name: \"{owner_name}\"")
		self.owner_name = owner_name

	def set_on_incoming_data(self, callback):
		self.logger.dbg(f"New __on_incoming_data_callback: {callback.__name__}()")
		self.__on_incoming_data_callback = callback

	def set_on_message(self, callback):
		self.logger.dbg(f"New __on_message_callback: {callback.__name__}()")
		self.__on_message_callback = callback

	def set_on_name_change(self, callback):
		self.logger.dbg(f"New __on_name_change_callback: {callback.__name__}()")
		self.__on_name_change_callback = callback

	def start(self, ip, port):
		if self.owner_name is None:
			self.logger.warn(f"Owner name is not set. Owner-only commands won't work.")

		self.__ip = ip
		self.__port = port

		self.logger.dbg(f"Connecting to {self.__ip}:{self.__port}...")

		try:
			listener = telnetlib.Telnet(self.__ip, self.__port)
		except Exception as e:
			self.logger.err(f"Couldn't create telnet connection to {self.__ip}:{self.__port} (did you run with `-netconport {self.__port}`?)")
			return

		self.logger.info(f"Connected to {self.__ip}:{self.__port}.")

		self.__print_info()

		self.logger.dbg("Starting queue processor...")
		self.__process_queue = threading.Thread(target=self.__process_queue_thread)
		self.__process_queue.start()
		self.__queue_processor_started = True

		while True:
			data_in = listener.read_until(b"\n")
			threading.Thread(target=self.__handle_incoming_thread, args=(data_in,)).start()

	def __print_info(self):
		self.logger.info("--- INFO ---")
		self.logger.info(f"OWNER NAME: \"{self.owner_name}\"")
		self.logger.info(f"CHAT PREFIX: \"{self.chat_prefix}\"")
		self.logger.info(f"ECHO PREFIX: \"{self.echo_prefix}\"")

		self.logger.info("")
		self.logger.info("--- COMMAND LIST ---")
		for cmd_type in Commands.CommandType:
			self.logger.info(f"COMMANDS {cmd_type.name}:")
			for command in self.commands.get_commands([cmd_type]):
				self.logger.info(f"  - {command.name}: {command.description}")
			self.logger.info("")

	def __handle_incoming_thread(self, data_in):
		self.logger.dbg(f"Received {len(data_in)} bytes from {self.__ip}:{self.__port}")

		if self.__on_incoming_data_callback:
			self.__on_incoming_data_callback(data_in)

		received = data_in.decode("utf-8").replace("\n", " ").replace("\r", "").strip()

		chat_message_pattern = re.compile(r".*[\u200E]\s(@.*|):\s+")
		name_change_pattern = re.compile(rf"\* {self.owner_name}\u200E changed name to ")

		if chat_message_pattern.match(received) is not None:
			message = ChatMessage.ChatMessage(received, self.owner_name)
			self.__handle_chat_message(message)
			return

		if received.startswith(self.echo_prefix):
			cmd = received[len(self.echo_prefix):]
			self.__handle_echo_command(cmd)
			return

		if name_change_pattern.match(received) is not None:
			self.__handle_name_change(name_change_pattern, received)
			return

	def __handle_name_change(self, name_change_pattern, received):
		old_name = self.owner_name
		self.set_owner_name(name_change_pattern.sub("", received))

		if self.__on_name_change_callback:
			self.__on_name_change_callback(old_name, self.owner_name)

	def __parse_args(self, args):
		args_list = []

		in_quotes = False
		temp = ""
		for char in args:
			if char == "\"":
				in_quotes = not in_quotes
				continue

			if char == " " and not in_quotes:
				args_list.append(temp)
				temp = ""
				continue
			temp += char

		args_list.append(temp)

		return args_list

	def __handle_chat_message(self, message):
		self.logger.dbg(message)

		if self.__on_message_callback:
			self.__on_message_callback(message)

		if not message.get_content().startswith(self.chat_prefix):
			self.logger.dbg("Message was not a command.")
			return

		for command in self.commands.get_commands([Commands.CommandType.CHAT_OWNER, Commands.CommandType.CHAT_GLOBAL]):
			command_str = message.get_content()[len(self.chat_prefix):].strip()
			if command_str.startswith(f"{command.name} ") or command_str == command.name:
				if command.cmd_type == Commands.CommandType.CHAT_OWNER and not message.is_owner():
					self.logger.warn(f"\"{message.get_author()}\" tried to run owner command \"{command.name}\"")
					return
				args = command_str[len(command.name):].strip()

				self.logger.dbg(f"Calling chat command \"{command.name}\"...")
				command.callback(message, self.__parse_args(args))
				return

		self.logger.warn(f"Coulnd't find matching chat command for \"{message.get_content()}\"")

	def __handle_echo_command(self, command_str):
		self.logger.dbg("Incoming data starts with echo command prefix!")
		for command in self.commands.get_commands([Commands.CommandType.CONSOLE_ECHO]):
			if command_str.startswith(f"{command.name} ") or command_str == command.name:
				args = command_str[len(command.name):].strip()

				self.logger.dbg(f"Calling echo command \"{command.name}\"")
				command.callback(args)
				return

		self.logger.warn(f"Coulnd't find matching echo command for \"{command_str}\"")

	def queue(self, command):
		if not self.__queue_processor_started:
			self.logger.warn("Trying to queue command before processor started.")
			return False

		if len(self.__command_queue) > 10:
			self.logger.err("Queue length is over 10. Not adding command to queue.")
			return False

		if len(self.__command_queue) > 5:
			self.logger.warn("Queue length is over 5.")

		self.__command_queue.append(command)
		self.logger.dbg(f"Queued command \"{command.split(' ')[0]}\" (Queue size: {len(self.__command_queue)})")
		return True

	def __send(self, command):
		data = f"{command}\n".encode("utf-8")
		sender = telnetlib.Telnet(self.__ip, self.__port)
		sender.write(data)
		sender.close()
		self.logger.dbg(f"Sent {len(data)} bytes to {self.__ip}:{self.__port}")

	def __process_queue_thread(self):
		self.logger.dbg("Command queue processor started.")
		while True:
			if len(self.__command_queue) < 1:
				time.sleep(.01)
				continue

			cmd = self.__command_queue.pop(0)
			if cmd.startswith("say") or cmd.startswith("say_team"):
				time.sleep(.7)

			self.logger.dbg(f"Sending command \"{cmd.split(' ')[0]}\"")
			self.__send(cmd)