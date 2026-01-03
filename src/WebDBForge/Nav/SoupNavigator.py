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
	def getResolved(nav: dict, references: dict, validateInternal: bool = True) -> Any:
		data = SoupNavigator.resolveData(nav, references, validateInternal)

		name = SoupNavigator.resolveName(nav, references, validateInternal)

		args = SoupNavigator.resolveArgs(nav, references, validateInternal)

		kwargs = SoupNavigator.resolveKwargs(nav, references, validateInternal)

		return {
			'data': data,
			'name': name,
			'args': args,
			'kwargs': kwargs
		}

	@staticmethod
	def getSelective(result: Any, nav: dict, references: dict, validateInternal: bool = True) -> Any:
		if (not isinstance(result, list)) or ('select' not in nav):
			return result

		if isinstance(nav['select'], list):
			select = nav['select']
		else:
			select = SoupNavigator.eval(nav['select'], references, validateInternal)

		selectiveResult = []
		for index in select:
			selectiveResult.append(result[index])

		return selectiveResult

	@staticmethod
	def functionNav(nav: dict, references: dict, validateInternal: bool = True) -> Any:
		resolved = SoupNavigator.getResolved(nav, references, validateInternal)

		result = getattr(bs4, resolved['name'])(resolved['data'], *resolved['args'], **resolved['kwargs'])

		return SoupNavigator.getSelective(result, nav, references, validateInternal)

	@staticmethod
	def methodNav(nav: dict, references: dict, validateInternal: bool = True) -> Any:
		resolved = SoupNavigator.getResolved(nav, references, validateInternal)

		result = getattr(resolved['data'], resolved['name'])(*resolved['args'], **resolved['kwargs'])

		return SoupNavigator.getSelective(result, nav, references, validateInternal)

	@staticmethod
	def propertyNav(nav: dict, references: dict, validateInternal: bool = True) -> Any:
		resolved = SoupNavigator.getResolved(nav, references, validateInternal)

		result = getattr(resolved['data'], resolved['name'])

		return SoupNavigator.getSelective(result, nav, references, validateInternal)

	@staticmethod
	def _evalDirect(nav: dict, references: dict, validate: bool = True):
		try:
			return NAV_FN_DATA[nav['__nav__']]['nav'](nav, references, validate)
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
