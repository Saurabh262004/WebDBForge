from WebDBForge.Node.NodeCreate import NODE_METHODS

class NodeValidator:
	@staticmethod
	def constNode(node: dict, references: dict = None) -> dict[str, bool | Exception | None]:
		if 'value' not in node:
			return { 'success': False, 'error': Exception('missing \'value\' in a const node') }

		return { 'success': True, 'error': None }

	@staticmethod
	def getNode(node: dict, references: dict = None) -> dict[str, bool | Exception | None]:
		nFrom = node.get('from', None)

		if 'from' not in node:
			return { 'success': False, 'error': Exception('missing \'from\' in a get node') }

		if isinstance(nFrom, str):
			if 'sources' in node:
				if not isinstance(node['sources'], dict):
					return { 'success': False, 'error': Exception('from in get is str, sources must be a dict or another node') }

				if (nFrom not in node['sources']):
					return { 'success': False, 'error': Exception(f'no source with key {nFrom} found in sources') }

			else:
				if not isinstance(references, dict):
					return { 'success': False, 'error': Exception('from in get is str, references must be a dict') }

				if (nFrom not in references):
					return { 'success': False, 'error': Exception(f'no reference with key {nFrom} found in references') }

		if 'access' in node:
			if (isinstance(node['access'], dict) and (not '__node__' in node['access'])) or (not isinstance(node['access'], (list, dict))):
				return { 'success': False, 'error': Exception(f'access in get node can only be a list of access points or another node which can resolve to be a list of access points') }

		# implement more access points check later

		return { 'success': True, 'error': None}

	@staticmethod
	def createNode(node: dict, references: dict = None) -> dict[str, bool | Exception | None]:
		if node['method'] not in NODE_METHODS:
			return { 'success': False, 'error': Exception(f'no method with name {node['method']} found') }

		return { 'success': True, 'error': None }

	@staticmethod
	def listNode(node: dict, references: dict = None) -> dict[str, bool | Exception | None]:
		if 'contents' not in node:
			return { 'success': False, 'error': Exception('missing \'contents\' in a list node') }

		if isinstance(node['contents'], dict):
			if '__node__' not in node['contents']:
				return { 'success': False, 'error': Exception('in a list-node, contents can only be a list of data or nodes or another node') }
		elif not isinstance(node['contents'], (list, tuple)):
			return { 'success': False, 'error': Exception('in a list-node, contents can only be a list of data or nodes or another node') }

		return { 'success': True, 'error': None }

	@staticmethod
	def dictNode(node: dict, references: dict = None) -> dict[str, bool | Exception | None]:
		if 'keys' not in node:
			return { 'success': False, 'error': Exception('missing \'keys\' in a dict node') }

		if 'values' not in node:
			return { 'success': False, 'error': Exception('missing \'values\' in a dict node') }

		return { 'success': True, 'error': None }

	@staticmethod
	def funNode(node: dict, references: dict = None) -> dict[str, bool | Exception | None]:
		if not isinstance(node, dict):
			return { 'success': False, 'error': Exception('a fun node must be a dict') }
		
		if '__node__' in node:
			nodeType = node['__node__']

			if not '__type__' in node:
				return { 'success': False, 'error': Exception('missing \'__type__\' in a fun node') }

			if nodeType not in NodeValidatorMethods:
				return { 'success': False, 'error': Exception(f'unrecognized node type {nodeType}') }

			return { 'success': True, 'error': None }

		keys = node.keys()
		for fnKey in ('fun', 'args', 'kwargs'):
			if fnKey not in keys:
				return { 'success': False, 'error': Exception(f'missing \'{fnKey}\' in a fun node') }

		if node['fun'] not in references:
			return { 'success': False, 'error': Exception(f'no function with key {node['fun']} found in references') }

		return { 'success': True, 'error': None }

	@staticmethod
	def mapNode(node: dict, references: dict = None) -> dict[str, bool | Exception | None]:
		if 'sources' not in node:
			return { 'success': False, 'error': Exception('missing \'sources\' in a map node') }

		if not isinstance(node['sources'], (list, dict)):
			return { 'success': False, 'error': Exception('sources in a map node must be a list, dict or another node') }

		if 'fun' not in node:
			return { 'success': False, 'error': Exception('missing \'fun\' in a map node') }

		if not isinstance(node['fun'], dict) or '__node__' not in node['fun']:
			return { 'success': False, 'error': Exception('fun in a map node must be another node') }

		return { 'success': True, 'error': None }

	@staticmethod
	def zipNode(node: dict, references: dict = None) -> dict[str, bool | Exception | None]:
		if 'sources' not in node:
			return { 'success': False, 'error': Exception('missing \'sources\' in a zip node') }

		if not isinstance(node['sources'], dict):
			return { 'success': False, 'error': Exception('sources in a zip node must be a dict or another node') }

		if 'build' not in node:
			return { 'success': False, 'error': Exception('missing \'build\' in a zip node') }

		if not isinstance(node['build'], (dict, list)):
			return { 'success': False, 'error': Exception('build in a zip node must be a dict, list of source-keys or another node') }

		return { 'success': True, 'error': None }

	@staticmethod
	def callNode(node: dict, references: dict = None) -> dict[str, bool | Exception | None]:
		if 'func' not in node:
			return { 'success': False, 'error': Exception('missing \'func\' in a call node') }

		if node['func'] not in references:
			return { 'success': False, 'error': Exception(f'no function with key {node['func']} found in references') }

		return { 'success': True, 'error': None }

	@staticmethod
	def validate(node: dict, references: dict = None) -> dict[str, bool | Exception | None]:
		if not isinstance(node, dict):
			return { 'success': False, 'error': Exception('a node must be a dict') }

		if '__node__' not in node:
			return { 'success': False, 'error': Exception('a node must at least contain the \'__node__\' key') }

		nodeType = node['__node__']

		if nodeType not in NodeValidatorMethods:
			return { 'success': False, 'error': Exception(f'no method with name {nodeType} found') }

		return NodeValidatorMethods[nodeType](node, references)

NodeValidatorMethods = {
	'const': NodeValidator.constNode,
	'get': NodeValidator.getNode,
	'create': NodeValidator.createNode,
	'list': NodeValidator.listNode,
	'dict': NodeValidator.dictNode,
	'map': NodeValidator.mapNode,
	'fun': NodeValidator.funNode,
	'zip': NodeValidator.zipNode,
	'call': NodeValidator.callNode
}
