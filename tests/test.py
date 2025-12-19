import orjson
from Implementation import DataNodeEvals

with open('testDSLs/structure2.json', 'rb') as structureFile:
  structure = orjson.loads(structureFile.read(-1))

  references = {
    "names": [
      "Furina",
      "Hu Tao",
      "Citlali",
      "Columbina Hyposelenia"
    ],
    "elements": [
      "Hydro",
      "Pyro",
      "Cryo",
      "Hydro"
    ]
  }

  DB = []

  for node in structure:
    DB.append(DataNodeEvals.eval(node, references))

  print(DB)
