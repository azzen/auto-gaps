class AnsiSequence:
	INFO = '\033[94m'
	SUCCESS = '\033[92m'
	WARNING = '\033[93m'
	ERROR = '\033[91m'
	RESET = '\033[0m'

class Log:

	@staticmethod
	def info(*args):
		print(AnsiSequence.INFO, "[*]", AnsiSequence.RESET, *args)

	@staticmethod
	def err(*args):
		print(AnsiSequence.ERROR, "[-]", AnsiSequence.RESET, *args)

	@staticmethod
	def warn(*args):
		print(AnsiSequence.WARNING, "[!]", AnsiSequence.RESET, *args)

	@staticmethod
	def success(*args):
		print(AnsiSequence.SUCCESS, "[+]", AnsiSequence.RESET, *args)
