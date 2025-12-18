import orjson
from Implementation import DataNode

with open('testDSLs/structure2.json', 'rb') as structureFile:
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

  DB = DataNode.eval(structure, references)

  print(DB)
