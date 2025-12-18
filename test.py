import orjson
from DBStructure import make

with open('structure.json', 'rb') as structureFile:
  structure = orjson.loads(structureFile.read(-1))

  DB = make(structure)

  print(DB)
