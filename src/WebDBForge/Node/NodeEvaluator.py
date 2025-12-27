from Node.NodeValidator import NodeValidator
from Node.NodeCreate import NODE_METHODS

class NodeEvaluator:
  @staticmethod
  def constNode(node: dict, references: dict = None, validateInternal: bool = True):
    return node['value']

  @staticmethod
  def getNode(node: dict, references: dict = None, validateInternal: bool = True):
    result = references[node['from']]

    if 'access' not in node:
      if 'unwrapIfSingle' in node and node['unwrapIfSingle'] and isinstance(result, (list, tuple)) and len(result) == 1:
        return result[0]

      return result

    access = node['access']

    if isinstance(access, dict):
      access = NodeEvaluator.eval(access, references, validateInternal)

    for accessPoint in access:
      result = result[accessPoint]

    if 'unwrapIfSingle' in node and node['unwrapIfSingle'] and isinstance(result, (list, tuple)) and len(result) == 1:
      return result[0]

    return result

  @staticmethod
  def createNode(node: dict, references: dict = None, validateInternal: bool = True):
    if '__node__' in node['kwargs']:
      kwargs = NodeEvaluator.eval(node['kwargs'], references, validateInternal)
    else:
      kwargs = node['kwargs']

    return NODE_METHODS[node['method']](**kwargs)

  @staticmethod
  def listNode(node: dict, references: dict = None, validateInternal: bool = True):
    result = []

    contents = node['contents']

    if isinstance(contents, dict):
      contents = NodeEvaluator.eval(contents, references, validateInternal)

    for item in contents:
      if isinstance(item, dict) and '__node__' in item:
        item = NodeEvaluator.eval(item, references, validateInternal)

      if 'unwrapChildren' in node and node['unwrapChildren']:
        try:
          result.extend(item)
        except:
          print('tried to extend list node but failed, appending the data instead')
          result.append(item)
      else:
        result.append(item)

    if 'unwrapIfSingle' in node and node['unwrapIfSingle'] and len(result) == 1:
      return result[0]

    return result

  @staticmethod
  def dictNode(node: dict, references: dict = None, validateInternal: bool = True):
    result = {}

    keysListNode = {
      '__node__': 'list',
      'contents': node['keys']
    }

    valuesListNode = {
      '__node__': 'list',
      'contents': node['values']
    }

    keys = NodeEvaluator.eval(keysListNode, references, validateInternal)

    values = NodeEvaluator.eval(valuesListNode, references, validateInternal)

    minLen = min(len(keys), len(values))

    for i in range(minLen):
      result[keys[i]] = values[i]

    return result

  @staticmethod
  def zipNode(node: dict, references: dict = None, validateInternal: bool = True):
    if '__node__' in node['sources']:
      sources = NodeEvaluator.eval(node['sources'], references, validateInternal)
    else:
      sources = {}

      for key, sourceNode in node['sources'].items():
        sources[key] = NodeEvaluator.eval(sourceNode, references, validateInternal)

    if isinstance(node['build'], dict) and '__node__' in node['build']:
      build = NodeEvaluator.eval(node['build'], references, validateInternal)
    elif isinstance(node['build'], list):
      build = [
        NodeEvaluator.eval(buildNode, references, validateInternal)
        for buildNode in node['build']
      ]
    else:
      build = node['build']

    minSourceLen = min([len(source) for source in sources.values()])

    result = []

    if isinstance(build, dict):
      for i in range(minSourceLen):
        buildObj = {}

        for key, sourceReference in build.items():
          buildObj[key] = sources[sourceReference][i]

        result.append(buildObj)

      return result

    for i in range(minSourceLen):
      result.append(
        [
          sources[sourceReference][i]
          for sourceReference in build
        ]
      )

    return result

  @staticmethod
  def callNode(node: dict, references: dict = None, validateInternal: bool = True):
    if isinstance(node['args'], dict) and '__node__' in node['args']:
      args = NodeEvaluator.eval(node['args'], references, validateInternal)
    else:
      args = node['args']

    if node['argsType'] == 'kwargs':
      return references[node['func']](**args)

    return references[node['func']](*args)

  @staticmethod
  def _evalDirect(node: dict, references: dict = None, validate: bool = True):
    try:
      return NODE_FN_DATA[node['__node__']]['eval'](node, references, validate)
    except Exception as e:
      print(f'Error evaluating node: {node}\n')
      raise e

  @staticmethod
  def eval(node: dict, references: dict = None, validate: bool = True):
    if node['__node__'] in NODE_FN_DATA:
      if validate:
        validationData = NODE_FN_DATA[node['__node__']]['validate'](node, references)

        if validationData['success']:
          return NodeEvaluator._evalDirect(node, references, validate)

        print(f'Error evaluating node: {node}\n')
        raise validationData['error']

      return NodeEvaluator._evalDirect(node, references, validate)

    raise Exception(f'Invalid node type: {node['__node__']}')

NODE_FN_DATA = {
  'const': {
    'validate': NodeValidator.constNode,
    'eval': NodeEvaluator.constNode
  },
  'get': {
    'validate': NodeValidator.getNode,
    'eval': NodeEvaluator.getNode
  },
  'create': {
    'validate': NodeValidator.createNode,
    'eval': NodeEvaluator.createNode
  },
  'list': {
    'validate': NodeValidator.listNode,
    'eval': NodeEvaluator.listNode
  },
  'dict': {
    'validate': NodeValidator.dictNode,
    'eval': NodeEvaluator.dictNode
  },
  'zip': {
    'validate': NodeValidator.zipNode,
    'eval': NodeEvaluator.zipNode
  },
  'call': {
    'validate': NodeValidator.callNode,
    'eval': NodeEvaluator.callNode
  }
}
