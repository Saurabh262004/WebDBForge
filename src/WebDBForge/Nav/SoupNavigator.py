from typing import Any
import bs4
from WebDBForge.Nav.NavValidator import NavValidator

class SoupNavigator:
	@staticmethod
	def resolveData(nav: dict, references: dict, validateInternal: bool = True) -> Any:
		if not isinstance(nav['data'], dict):
			return nav['data']

		if '__nav__' in nav['data']:
			return SoupNavigator.eval(nav['data'], references, validateInternal)

		if 'ref' in nav['data']:
			return references[nav['data']['ref']]

		return nav['data']

	@staticmethod
	def resolveName(nav: dict, references: dict, validateInternal: bool = True) -> Any:
		if isinstance(nav['name'], dict) and '__nav__' in nav['name']:
			return SoupNavigator.eval(nav['name'], references, validateInternal)

		return nav['name']

	@staticmethod
	def resolveArgs(nav: dict, references: dict, validateInternal: bool = True) -> Any:
		if 'args' not in nav:
			return []

		if isinstance(nav['args'], dict) and '__nav__' in nav['args']:
			return SoupNavigator.eval(nav['args'], references, validateInternal)

		return nav['args']

	@staticmethod
	def resolveKwargs(nav: dict, references: dict, validateInternal: bool = True) -> Any:
		if 'kwargs' not in nav:
			return {}

		if isinstance(nav['kwargs'], dict) and '__nav__' in nav['kwargs']:
			return SoupNavigator.eval(nav['kwargs'], references, validateInternal)

		return nav['kwargs']

	@staticmethod
	def resolveSelect(nav: dict, references: dict, validateInternal: bool = True) -> Any:
		if 'select' not in nav:
			return None

		if isinstance(nav['select'], dict) and '__nav__' in nav['select']:
			return SoupNavigator.eval(nav['select'], references, validateInternal)

		return nav['select']

	@staticmethod
	def getResolved(nav: dict, references: dict, validateInternal: bool = True) -> Any:
		data = SoupNavigator.resolveData(nav, references, validateInternal)

		name = SoupNavigator.resolveName(nav, references, validateInternal)

		args = SoupNavigator.resolveArgs(nav, references, validateInternal)

		kwargs = SoupNavigator.resolveKwargs(nav, references, validateInternal)

		select = SoupNavigator.resolveSelect(nav, references, validateInternal)

		return {
			'data': data,
			'name': name,
			'args': args,
			'kwargs': kwargs,
			'select': select
		}

	@staticmethod
	def getSelective(result: Any, select: None | list[int]) -> Any:
		if select is None or not isinstance(result, list):
			return result

		resultLen = len(result)

		selectiveResult = []
		for index in select:
			if index < resultLen:
				selectiveResult.append(result[index])

		return selectiveResult

	@staticmethod
	def functionNav(resolvedNav: dict, references: dict, validateInternal: bool = True) -> Any:
		if not isinstance(resolvedNav['data'], list):
			result = getattr(bs4, resolvedNav['name'])(resolvedNav['data'], *resolvedNav['args'], **resolvedNav['kwargs'])

			selectiveResult = SoupNavigator.getSelective(result, resolvedNav['select'])

			return selectiveResult

		results = []
		for dataItem in resolvedNav['data']:
			result = SoupNavigator.functionNav(
				{
					'data': dataItem,
					'name': resolvedNav['name'],
					'args': resolvedNav['args'],
					'kwargs': resolvedNav['kwargs'],
					'select': resolvedNav['select']
				}, references, validateInternal
			)

			results.append(result)

		return results

	@staticmethod
	def methodNav(resolvedNav: dict, references: dict, validateInternal: bool = True) -> Any:
		if not isinstance(resolvedNav['data'], list):
			method = getattr(resolvedNav['data'], resolvedNav['name'], None)

			if method is None:
				return None

			result = method(*resolvedNav['args'], **resolvedNav['kwargs'])

			selectiveResult = SoupNavigator.getSelective(result, resolvedNav['select'])

			return selectiveResult

		results = []
		for dataItem in resolvedNav['data']:
			result = SoupNavigator.methodNav(
				{
					'data': dataItem,
					'name': resolvedNav['name'],
					'args': resolvedNav['args'],
					'kwargs': resolvedNav['kwargs'],
					'select': resolvedNav['select']
				}, references, validateInternal
			)

			results.append(result)

		return results

	@staticmethod
	def propertyNav(resolvedNav: dict, references: dict, validateInternal: bool = True) -> Any:
		if not isinstance(resolvedNav['data'], list):
			result = getattr(resolvedNav['data'], resolvedNav['name'], None)

			selectiveResult = SoupNavigator.getSelective(result, resolvedNav['select'])

			return selectiveResult

		results = []
		for dataItem in resolvedNav['data']:
			result = SoupNavigator.propertyNav(
				{
					'data': dataItem,
					'name': resolvedNav['name'],
					'args': resolvedNav['args'],
					'kwargs': resolvedNav['kwargs'],
					'select': resolvedNav['select']
				}, references, validateInternal
			)

			results.append(result)

		return results

	@staticmethod
	def dictAccessNav(resolvedNav: dict, references: dict, validateInternal: bool = True) -> Any:
		if not isinstance(resolvedNav['data'], list):
			if resolvedNav['name'] in resolvedNav['data']:
				result = resolvedNav['data'][resolvedNav['name']]
			else:
				result = None

			selectiveResult = SoupNavigator.getSelective(result, resolvedNav['select'])

			return selectiveResult

		results = []
		for dataItem in resolvedNav['data']:
			results.append(SoupNavigator.dictAccessNav(
				{
					'data': dataItem,
					'name': resolvedNav['name'],
					'args': resolvedNav['args'],
					'kwargs': resolvedNav['kwargs'],
					'select': resolvedNav['select']
				}, references, validateInternal
			))

		return results

	@staticmethod
	def _handleThen(then: dict, result: Any, references: dict, validate: bool = True) -> Any:
		if isinstance(then, dict):
			if not isinstance(result, list):
				newThen = dict(then)
				newThen['data'] = result

				return SoupNavigator.eval(newThen, references, validate)

			results = []
			for dataItem in result:
				results.append(SoupNavigator._handleThen(then, dataItem, references, validate))

			return results

		results = []
		for thenPart in then:
			results.append(SoupNavigator._handleThen(thenPart, result, references, validate))

		return results

	@staticmethod
	def _evalDirect(nav: dict, references: dict, validate: bool = True) -> Any:
		try:
			resolvedNav = SoupNavigator.getResolved(nav, references, validate)

			result = NAV_FN_DATA[nav['__nav__']]['nav'](resolvedNav, references, validate)

			if ('then' not in nav) or (nav['then'] is None) or (isinstance(nav['then'], (dict, list)) and len(nav['then']) == 0):
				return result

			return SoupNavigator._handleThen(nav['then'], result, references, validate)

		except Exception as e:
			print(nav['data'])
			# print(f'Error evaluating nav: {nav}\n')
			# raise e

	@staticmethod
	def eval(nav: dict, references: dict, validate: bool = True) -> Any:
		if nav['__nav__'] not in NAV_FN_DATA:
			raise Exception(f'Invalid nav type: {nav['__nav__']}')

		if not validate:
			return SoupNavigator._evalDirect(nav, references, validate)

		validationData = NAV_FN_DATA[nav['__nav__']]['validate'](nav, references)

		if not validationData['success']:
			print(f'Error evaluating nav: {nav}\n')
			raise validationData['error']

		return SoupNavigator._evalDirect(nav, references, validate)

NAV_FN_DATA = {
	'function': {
		'validate': NavValidator.functionNav,
		'nav': SoupNavigator.functionNav
	},
	'method': {
		'validate': NavValidator.methodNav,
		'nav': SoupNavigator.methodNav
	},
	'property': {
		'validate': NavValidator.propertyNav,
		'nav': SoupNavigator.propertyNav
	},
	'dictAccess': {
		'validate': NavValidator.dictAccessNav,
		'nav': SoupNavigator.dictAccessNav
	}
}
