def getData(structure: dict, references: dict = None):
  return None

def getObj(structure: dict, references: dict = None) -> dict:
  obj = {}

  keys = []

  for subStruct in structure:
    keys.append(getData(subStruct['keys']))

def getArr(structure: dict, references: dict = None) -> list:
  arr = []

  for subStruct in structure['contents']:
    if subStruct['type'] == 'arr':
      if len(structure['contents'] > 1) or ('flatten' in structure and structure['flatten']):
        arr.extend(getArr(subStruct, references))
        continue

      arr.append(getArr(subStruct, references))

    if subStruct['type'] == 'obj':
      arr.append(getObj(subStruct, references))
      continue

    if subStruct['type'] == 'data':
      if len(structure['contents'] > 1) or ('flatten' in structure and structure['flatten']):
        arr.extend(getData(subStruct, references))
        continue

      arr.append(getData(subStruct, references))

  return arr

def make(structure: list, references: dict = None) -> dict:
  data = {
    'DB': None,
    'metadata': None
  }

  # must only have containers as the first objects in the structure list
  for container in structure:
    if container['type'] == 'arr':
      data['DB'] = getArr(container, references)
    else:
      data['DB'] = getObj(container, references)

  return data
