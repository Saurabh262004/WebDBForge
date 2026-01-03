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

		selectiveResult = []
		for index in select:
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
			results.append(SoupNavigator.functionNav(
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
	def methodNav(resolvedNav: dict, references: dict, validateInternal: bool = True) -> Any:
		if not isinstance(resolvedNav['data'], list):
			result = getattr(resolvedNav['data'], resolvedNav['name'])(*resolvedNav['args'], **resolvedNav['kwargs'])

			selectiveResult = SoupNavigator.getSelective(result, resolvedNav['select'])

			return selectiveResult

		results = []
		for dataItem in resolvedNav['data']:
			results.append(SoupNavigator.methodNav(
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
	def propertyNav(resolvedNav: dict, references: dict, validateInternal: bool = True) -> Any:
		if not isinstance(resolvedNav['data'], list):
			result = getattr(resolvedNav['data'], resolvedNav['name'])

			selectiveResult = SoupNavigator.getSelective(result, resolvedNav['select'])

			return selectiveResult

		results = []
		for dataItem in resolvedNav['data']:
			results.append(SoupNavigator.propertyNav(
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
	def _evalDirect(nav: dict, references: dict, validate: bool = True):
		try:
			resolvedNav = SoupNavigator.getResolved(nav, references, validate)
			return NAV_FN_DATA[nav['__nav__']]['nav'](resolvedNav, references, validate)
		except Exception as e:
			print(f'Error evaluating node: {nav}\n')
			raise e

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
	}
}
