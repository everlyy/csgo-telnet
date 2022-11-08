from enum import Enum
import inspect
import datetime

class LogLevel(Enum):
	DEBUG = 1
	INFO = 2
	WARNING = 3
	ERROR = 4

class Logger:
	def __init__(self, log_level):
		self.log_level = log_level

	def __color_for_level(self, log_level):
		return ["\033[37m", "\033[34m", "\033[33m", "\033[31m"][log_level.value - 1]

	def __log(self, log_level, message):
		if log_level.value < self.log_level.value:
			return
		caller = inspect.stack()[2].function
		time = datetime.datetime.now().strftime("%H:%M:%S.%f")
		print(f"{time} \033[35m{caller}()\033[m {self.__color_for_level(log_level)}{log_level.name}: {message}\033[m")

	def dbg(self, message):
		self.__log(LogLevel.DEBUG, message)

	def info(self, message):
		self.__log(LogLevel.INFO, message)

	def warn(self, message):
		self.__log(LogLevel.WARNING, message)

	def err(self, message):
		self.__log(LogLevel.ERROR, message)