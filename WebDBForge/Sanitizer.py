FORBIDDEN_CHARS = '<>:"/\\|?*\x00'

WIN_RESERVED = (
	'CON', 'PRN', 'AUX', 'NUL',
	'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
	'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
)

LINUX_RESERVED = ('.', '..')

class Sanitizer:
	@staticmethod
	def OSProofName(name: str) -> str | bool:
		for char in FORBIDDEN_CHARS:
			name = name.replace(char, '')

		# windows doesn't support these ascii control characters
		for i in range(32):
			name = name.replace(chr(i), '')

		# file names can't end with space in windows
		name = name.strip()

		# get filename without extention (if there is any)
		base = name.split('.')[0].upper()

		if base in WIN_RESERVED:
			return False

		if name in LINUX_RESERVED:
			return False

		return name
