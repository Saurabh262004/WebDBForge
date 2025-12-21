class NodeValidator:
  @staticmethod
  def constNode(node: dict, references: dict = None) -> dict[str, bool | Exception | None]:
    if 'value' not in node:
      return { 'success': False, 'error': Exception('missing \'value\' in a const node') }

    return { 'success': True, 'error': None }

  @staticmethod
  def getNode(node: dict, references: dict = None) -> dict[str, bool | Exception | None]:
    if 'from' not in node:
      return { 'success': False, 'error': Exception('missing \'from\' in a get node') }

    if node['from'] not in references:
      return { 'success': False, 'error': Exception(f'no reference with key {node['from']} found in references') }

    if 'access' not in node:
      return { 'success': False, 'error': Exception('missing \'access\' in a get node') }

    if isinstance(node['access'], str) and not node['acceses'] == 'direct':
      return { 'successs': False, 'error': Exception(f'invalid value for access in a get node') }

    # implement access points check later

    return { 'success': True, 'error': None}

  @staticmethod
  def createNode(node: dict, references: dict = None) -> dict[str, bool | Exception | None]:
    # implement check later

    return { 'success': True, 'error': None }

  @staticmethod
  def listNode(node: dict, references: dict = None) -> dict[str, bool | Exception | None]:
    if 'contents' not in node:
      return { 'success': False, 'error': Exception('missing \'contents\' in a list node') }

    return { 'success': True, 'error': None }

  @staticmethod
  def dictNode(node: dict, references: dict = None) -> dict[str, bool | Exception | None]:
    if 'keys' not in node:
      return { 'success': False, 'error': Exception('missing \'keys\' in a dict node') }

    if 'value' not in node:
      return { 'success': False, 'error': Exception('missing \'values\' in a dict node') }

    return { 'success': True, 'error': None }

  @staticmethod
  def zipNode(node: dict, references: dict = None) -> dict[str, bool | Exception | None]:
    if 'sources' not in node:
      return { 'success': False, 'error': Exception('missing \'sources\' in a zip node') }

    if not isinstance(node['sources']):
      return { 'success': False, 'error': Exception('sources in a zip node must be a dict or another node') }

    if 'build' not in node:
      return { 'success': False, 'error': Exception('missing \'build\' in a zip node') }

    if not isinstance(node['build']):
      return { 'success': False, 'error': Exception('build in a zip node must be a dict or another node') }

    return { 'success': True, 'error': None }

  @staticmethod
  def callNode(node: dict, references: dict = None) -> dict[str, bool | Exception | None]:
    if 'func' not in node:
      return { 'success': False, 'error': Exception('missing \'sources\' in a zip node') }

    if node['func'] not in references:
      return { 'success': False, 'error': Exception(f'no function with key {node['func']} found in references') }

    return { 'success': True, 'error': None }

class NodeEvaluator:
  @staticmethod
  def constNode(node: dict, validate: bool = True):
    return None

  @staticmethod
  def getNode(node: dict, references: dict = None):
    return None

  @staticmethod
  def createNode(node: dict, references: dict = None):
    return None

  @staticmethod
  def listNode(node: dict, references: dict = None):
    return None

  @staticmethod
  def dictNode(node: dict, references: dict = None):
    return None

  @staticmethod
  def zipNode(node: dict, references: dict = None):
    return None

  @staticmethod
  def callNode(node: dict, references: dict = None):
    return None

class Node:
  @staticmethod
  def eval(node: dict, references: dict = None, validate: bool = True):
    if node['__node__'] in Node.evalData:
      if validate:
        validationData = Node.evalData[node['__node__']]['validate'](node, references)

        if validationData['success']:
          return Node.evalData[node['__node__']]['eval'](node, references)

        raise validationData['error']
      
      return Node.evalData[node['__node__']]['eval'](node, references)

    raise Exception(f'Invalid node type: {node['__node__']}')

evalData = {
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
