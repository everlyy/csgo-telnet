from enum import Enum

class CommandType(Enum):
	CHAT_OWNER = 1
	CHAT_GLOBAL = 2
	CONSOLE_ECHO = 3

class Command:
	def __init__(self, name, description, callback, cmd_type):
		self.name = name
		self.description = description
		self.callback = callback
		self.cmd_type = cmd_type

	def __str__(self):
		return self.name

	def init_owner_command(name, description, callback):
		return Command(name, description, callback, CommandType.CHAT_OWNER)

	def init_global_command(name, description, callback):
		return Command(name, description, callback, CommandType.CHAT_GLOBAL)

	def init_echo_command(name, description, callback):
		return Command(name, description, callback, CommandType.CONSOLE_ECHO)

class Commands:
	def __init__(self):
		self.__commands = []

	def add_owner_command(self, name, description, callback):
		self.__commands.append(Command.init_owner_command(name, description, callback))

	def add_global_command(self, name, description, callback):
		self.__commands.append(Command.init_global_command(name, description, callback))

	def add_echo_command(self, name, description, callback):
		self.__commands.append(Command.init_echo_command(name, description, callback))

	def get_commands(self, command_types):
		commands = []
		for command in self.__commands:
			if command.cmd_type in command_types:
				commands.append(command)
		return commands