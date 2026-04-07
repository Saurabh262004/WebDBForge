import orjson
from WebDBForge import MakeDB

with open('tests/mkdbManifest.json', 'rb') as manFile:
	mkdbManifest = orjson.loads(manFile.read())

	mkdbManifest['extraRef'] = {
		'checkLimited': lambda char, lst: 'limited' if char[1] in lst else 'standard'
	}

	MakeDB(**mkdbManifest)
