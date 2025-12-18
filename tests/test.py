import orjson
from Implementation.DBStructure import make

with open('testDSLs/structure.json', 'rb') as structureFile:
  structure = orjson.loads(structureFile.read(-1))

  references = {
    "a": [
      1, 2, 3
    ],
    "b": [
      '4', '5', '6'
    ],
    "c": [
      6, 7, 8
    ]
  }

  DB = make(structure, references)

  print(DB)
