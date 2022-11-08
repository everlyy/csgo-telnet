class MessageParts:
	TEAM_CT = "(Counter-Terrorist)"
	TEAM_T = "(Terrorist)"
	DEAD = "*DEAD*"
	NAME_MESSAGE_SEPARATOR = " : "
	NAME_SUFFIX = "\u200E" # This character appears after everyone's name for some reason

class ChatMessage:
	def __init__(self, full_message, owner_name):
		self.full_message = full_message
		self.owner_name = owner_name

		self.__author = None
		self.__content = None
		self.__is_team_chat = None
		self.__is_owner = None

	def get_author(self):
		if self.__author is not None:
			return self.__author

		self.__author = self.full_message.split(MessageParts.NAME_MESSAGE_SEPARATOR, maxsplit=1)[0].split(MessageParts.NAME_SUFFIX, maxsplit=1)[0].strip()

		if self.__contains_one_of([ MessageParts.TEAM_CT, MessageParts.TEAM_T, MessageParts.DEAD ], self.full_message):
			self.__author = self.full_message[self.full_message.index(" "):].split(MessageParts.NAME_SUFFIX, maxsplit=1)[0].strip()

		return self.__author
	
	def get_content(self):
		if self.__content is not None:
			return self.__content

		self.__content = self.full_message.split(MessageParts.NAME_MESSAGE_SEPARATOR, maxsplit=1)[1].strip()

		return self.__content

	def is_team_chat(self):
		if self.__is_team_chat is not None:
			return self.__is_team_chat

		pre_content = self.full_message.split(MessageParts.NAME_MESSAGE_SEPARATOR, maxsplit=1)[0].split(MessageParts.NAME_SUFFIX, maxsplit=1)[0].strip()
		self.__is_team_chat = self.__contains_one_of([ MessageParts.TEAM_CT, MessageParts.TEAM_T ], pre_content)

		return self.__is_team_chat

	def is_owner(self):
		if self.__is_owner is not None:
			return self.__is_owner

		self.__is_owner = self.get_author() == self.owner_name

		return self.__is_owner

	def __contains_one_of(self, items, string):
		for item in items:
			if item in string:
				return True
		return False

	def __str__(self):
		return f"ChatMessage <author=\"{self.get_author()}\" is_owner={self.is_owner()} content=\"{self.get_content()}\" is_team_chat={self.is_team_chat()}>"