import copy
from WebDBForge.Node.NodeValidator import NodeValidator
from WebDBForge.Node.NodeCreate import NODE_METHODS
from typing import Any

class NodeEvaluator:
	@staticmethod
	def constNode(node: dict, references: dict = None, validateInternal: bool = True) -> Any:
		return node['value']

	@staticmethod
	def getNode(node: dict, references: dict = None, validateInternal: bool = True) -> Any:
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
	def createNode(node: dict, references: dict = None, validateInternal: bool = True) -> Any:
		if '__node__' in node['kwargs']:
			kwargs = NodeEvaluator.eval(node['kwargs'], references, validateInternal)
		else:
			kwargs = node['kwargs']

		return NODE_METHODS[node['method']](**kwargs)

	@staticmethod
	def listNode(node: dict, references: dict = None, validateInternal: bool = True) -> list | Any:
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
	def dictNode(node: dict, references: dict = None, validateInternal: bool = True) -> dict:
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
	def funNode(node: dict, references: dict = None, validateInternal: bool = True) -> Any:
		source = node.get('__source_', None)

		if '__node__' in node:
			node = { key: (source if value == '__source__' else value) for key, value in node.items() }
			node['__node__'] = node['__type__']

			return NodeEvaluator.eval(node, references, validateInternal)

		fn = references[node['fun']]

		args = node.get('args', [])

		if isinstance(node['args'], dict) and '__node__' in node['args']:
			args = NodeEvaluator.eval(node['args'], references, validateInternal)

		args = [source if arg == '__source__' else arg for arg in args]

		kwargs = node.get('kwargs', {})

		if isinstance(node['kwargs'], dict) and '__node__' in node['kwargs']:
			kwargs = NodeEvaluator.eval(node['kwargs'], references, validateInternal)

		kwargs = { key: (source if value == '__source__' else value) for key, value in kwargs.items() }

		return fn(*args, **kwargs)

	@staticmethod
	def mapNode(node: dict, references: dict = None, validateInternal: bool = True) -> list:
		if isinstance(node['sources'], dict) and '__node__' in node['sources']:
			sources = NodeEvaluator.eval(node['sources'], references, validateInternal)
		else:
			sources = node['sources']

		if isinstance(sources, dict):
			result = {}
			for key, source in sources.items():
				fun = node['fun']
				fun['__source__'] = source

				result[key] = NodeEvaluator.eval(fun, references, validateInternal)

			return result

		result = []
		for source in sources:
			fun = node['fun']
			fun['__source__'] = source

			result.append(NodeEvaluator.eval(fun, references, validateInternal))

		return result

	@staticmethod
	def zipNode(node: dict, references: dict = None, validateInternal: bool = True) -> list[dict, list]:
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

		minSourceLen = min(len(source) for source in sources.values())

		result = []

		if isinstance(build, dict):
			result = [
				{
					key: sources[src][i]
					for key, src in build.items()
				}
				for i in range(minSourceLen)
			]

			return result

		result = [
			[sources[src][i] for src in build]
			for i in range(minSourceLen)
		]

		return result

	@staticmethod
	def callNode(node: dict, references: dict = None, validateInternal: bool = True) -> Any:
		if isinstance(node.get('args', None), dict) and '__node__' in node['args']:
			args = NodeEvaluator.eval(node['args'], references, validateInternal)
		else:
			args = node.get('args', [])

		if isinstance(node.get('kwargs', None), dict) and '__node__' in node['kwargs']:
			kwargs = NodeEvaluator.eval(node['kwargs'], references, validateInternal)
		else:
			kwargs = node.get('kwargs', {})

		return references[node['func']](*args, **kwargs)

	@staticmethod
	def _evalDirect(node: dict, references: dict = None, validate: bool = True) -> Any:
		try:
			return NODE_FN_DATA[node['__node__']](node, references, validate)
		except Exception as e:
			print(f'Error evaluating node: {node}\n')
			raise e

	@staticmethod
	def eval(node: dict, references: dict = None, validate: bool = True) -> Any:
		if node['__node__'] not in NODE_FN_DATA:
			raise Exception(f'Invalid node type: {node['__node__']}')

		if not validate:
			return NodeEvaluator._evalDirect(node, references, validate)

		validationData = NodeValidator.validate(node, references)

		if not validationData['success']:
			print(f'Error evaluating node: {node}\n')
			raise validationData['error']

		return NodeEvaluator._evalDirect(node, references, validate)

NODE_FN_DATA = {
	'const': NodeEvaluator.constNode,
	'get': NodeEvaluator.getNode,
	'create': NodeEvaluator.createNode,
	'list': NodeEvaluator.listNode,
	'dict': NodeEvaluator.dictNode,
	'fun': NodeEvaluator.funNode,
	'map': NodeEvaluator.mapNode,
	'zip': NodeEvaluator.zipNode,
	'call': NodeEvaluator.callNode
}
