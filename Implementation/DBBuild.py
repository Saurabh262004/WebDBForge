class NodeConstants:
  DATA_NODE_TYPE = ('get', 'create', 'direct')

  DATA_NODE_FROM = ('range',)

class NodeVerification:
  @staticmethod
  def validateDataNode(node: dict, references: dict) -> tuple[bool, Exception]:
    if (not 'type' in node) or (not isinstance(node['type'], str)):
      return (False, ValueError('"type" in data nodes must contain a valid string'))

    if not node['type'] in NodeConstants.DATA_NODE_TYPE:
      return (False, ValueError(f'Data nodes must only contain following types: {NodeConstants.DATA_NODE_TYPE}, got: {node['type']}'))

    if not 'from' in node or (not isinstance(node['from'], str)):
      return (False, ValueError(f'"from" in data nodes must contain a valid string'))

    if (node['type'] == 'get') and (node['from'] not in references):
      return (False, ValueError(f'When data node type is "get", "type" must be one of the keys in references'))

    if (node['type'] == 'create') and (node['from'] not in NodeConstants.DATA_NODE_FROM):
      return (False, ValueError(f'When data node type is "create", "type" must be one of the following: {NodeConstants.DATA_NODE_FROM}'))

    return (True,)

class DataNodeEvals:
  @staticmethod
  def create(node: dict):
    if node['from'] == 'range':
      return list(range(*node['access']))

  @staticmethod
  def get(node: dict, references: dict):
    referenceName = node['from']

    access = node['access']

    if referenceName not in references:
      return None

    if access == 'all':
      return references[referenceName]

    reference = references[referenceName]

    getData = []

    if isinstance(access, (list, tuple)):
      for accessPoint in access:
        if isinstance(accessPoint, str) and accessPoint not in reference:
          getData.append(None)
          continue

        if isinstance(accessPoint, int) and len(reference) <= accessPoint:
          getData.append(None)
          continue

        getData.append(reference[accessPoint])

    return getData

  @staticmethod
  def eval(node: dict, references: dict = None, validate: bool = True):
    if validate:
      dataNodeVerification = NodeVerification.validateDataNode(node, references)

      if not dataNodeVerification[0]:
        raise dataNodeVerification[1]

    else:
      print('Warning! evaluating data node without verification, things could break without much clarity.')

    access = node['access']

    if 'type' in access and 'from' in access and 'access' in access:
      access = node['access'] = DataNodeEvals.eval(access, references)

    if node['type'] == 'create':
      data = DataNodeEvals.create(node)
    elif node['type'] == 'get':
      data = DataNodeEvals.get(node, references)
    elif node['type'] == 'direct':
      data = access
    else:
      return None

    if isinstance(data, (list, tuple)):
      dataLen = len(data)

      if dataLen == 0:
        return None

      if dataLen == 1 and 'unwrapIfSingle' in node and node['unwrapIfSingle']:
        return data[0]

    return data
