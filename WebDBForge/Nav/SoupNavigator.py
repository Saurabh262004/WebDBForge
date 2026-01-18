from typing import Any
import bs4
from WebDBForge.Nav.NavValidator import NavValidator

class SoupNavigator:
	@staticmethod
	def resolveData(nav: dict, references: dict, validateInternal: bool = True, logFile: str = None) -> Any:
		if not isinstance(nav['data'], dict):
			return nav['data']

		if '__nav__' in nav['data']:
			return SoupNavigator.eval(nav['data'], references, validateInternal, logFile)

		if 'ref' in nav['data']:
			return references[nav['data']['ref']]

		return nav['data']

	@staticmethod
	def resolveName(nav: dict, references: dict, validateInternal: bool = True, logFile: str = None) -> Any:
		if isinstance(nav['name'], dict) and '__nav__' in nav['name']:
			return SoupNavigator.eval(nav['name'], references, validateInternal, logFile)

		return nav['name']

	@staticmethod
	def resolveArgs(nav: dict, references: dict, validateInternal: bool = True, logFile: str = None) -> Any:
		if 'args' not in nav:
			return []

		if isinstance(nav['args'], dict) and '__nav__' in nav['args']:
			return SoupNavigator.eval(nav['args'], references, validateInternal, logFile)
		return nav['args']

	@staticmethod
	def resolveKwargs(nav: dict, references: dict, validateInternal: bool = True, logFile: str = None) -> Any:
		if 'kwargs' not in nav:
			return {}

		if isinstance(nav['kwargs'], dict) and '__nav__' in nav['kwargs']:
			return SoupNavigator.eval(nav['kwargs'], references, validateInternal, logFile)

		return nav['kwargs']

	@staticmethod
	def resolveSelect(nav: dict, references: dict, validateInternal: bool = True, logFile: str = None) -> Any:
		if 'select' not in nav:
			return None

		if isinstance(nav['select'], dict) and '__nav__' in nav['select']:
			return SoupNavigator.eval(nav['select'], references, validateInternal, logFile)

		return nav['select']

	@staticmethod
	def resolveExclude(nav: dict, references: dict, validateInternal: bool = True, logFile: str = None) -> Any:
		if 'exclude' not in nav:
			return None

		if isinstance(nav['exclude'], dict) and '__nav__' in nav['exclude']:
			return SoupNavigator.eval(nav['exclude'], references, validateInternal, logFile)

		return nav['exclude']

	@staticmethod
	def getResolved(nav: dict, references: dict, validateInternal: bool = True, logFile: str = None) -> Any:
		return {
			'data': SoupNavigator.resolveData(nav, references, validateInternal, logFile),
			'name': SoupNavigator.resolveName(nav, references, validateInternal, logFile),
			'args': SoupNavigator.resolveArgs(nav, references, validateInternal, logFile),
			'kwargs': SoupNavigator.resolveKwargs(nav, references, validateInternal, logFile),
			'select': SoupNavigator.resolveSelect(nav, references, validateInternal, logFile),
			'exclude': SoupNavigator.resolveExclude(nav, references, validateInternal, logFile),
			'unwrap': nav.get('unwrap', None)
		}

	@staticmethod
	def unwrap(result: Any, recursive: bool = False) -> Any:
		if not recursive:
			if isinstance(result, list) and len(result) == 1:
				return result[0]
			return result

		if isinstance(result, list) and len(result) == 1:
			return SoupNavigator.unwrap(result[0], True)

		return result

	@staticmethod
	def handleUnwrap(nav: dict, result: Any) -> Any:
		unwrap = nav['unwrap']

		if unwrap is None or (unwrap.lower() not in ('shallow', 'recursive')):
			return result

		unwrapRecursive = (unwrap.lower() == 'recursive')

		return SoupNavigator.unwrap(result, unwrapRecursive)

	@staticmethod
	def getSelective(result: Any, select: None | list[int], exclude: None | list[int] = None) -> Any:
		if not isinstance(result, list):
			return result

		if select is None and exclude is None:
			return result

		resultLen = len(result)

		if select is None:
			selectiveResult = result
		else:
			selectiveResult = [result[i] for i in select if i >= 0 and i < resultLen]

		if exclude is not None:
			selectiveResult = [item for i, item in enumerate(selectiveResult) if i not in exclude]

		return selectiveResult

	@staticmethod
	def functionNav(resolvedNav: dict, references: dict, validateInternal: bool = True) -> Any:
		if not isinstance(resolvedNav['data'], list):
			result = getattr(bs4, resolvedNav['name'])(resolvedNav['data'], *resolvedNav['args'], **resolvedNav['kwargs'])

			selectiveResult = SoupNavigator.getSelective(result, resolvedNav['select'], resolvedNav['exclude'])

			unwrappedResult = SoupNavigator.handleUnwrap(resolvedNav, selectiveResult)

			return unwrappedResult

		results = []
		for dataItem in resolvedNav['data']:
			newNav = dict(resolvedNav)
			newNav['data'] = dataItem

			result = SoupNavigator.functionNav(newNav, references, validateInternal)

			results.append(result)

		return results

	@staticmethod
	def methodNav(resolvedNav: dict, references: dict, validateInternal: bool = True) -> Any:
		if not isinstance(resolvedNav['data'], list):
			method = getattr(resolvedNav['data'], resolvedNav['name'], None)

			if method is None:
				return None

			result = method(*resolvedNav['args'], **resolvedNav['kwargs'])

			selectiveResult = SoupNavigator.getSelective(result, resolvedNav['select'], resolvedNav['exclude'])

			unwrappedResult = SoupNavigator.handleUnwrap(resolvedNav, selectiveResult)

			return unwrappedResult

		results = []
		for dataItem in resolvedNav['data']:
			newNav = dict(resolvedNav)
			newNav['data'] = dataItem

			result = SoupNavigator.methodNav(newNav, references, validateInternal)

			results.append(result)

		return results

	@staticmethod
	def propertyNav(resolvedNav: dict, references: dict, validateInternal: bool = True) -> Any:
		if not isinstance(resolvedNav['data'], list):
			result = getattr(resolvedNav['data'], resolvedNav['name'], None)

			selectiveResult = SoupNavigator.getSelective(result, resolvedNav['select'], resolvedNav['exclude'])

			unwrappedResult = SoupNavigator.handleUnwrap(resolvedNav, selectiveResult)

			return unwrappedResult

		results = []
		for dataItem in resolvedNav['data']:
			newNav = dict(resolvedNav)
			newNav['data'] = dataItem

			result = SoupNavigator.propertyNav(newNav, references, validateInternal)

			results.append(result)

		return results

	@staticmethod
	def dictAccessNav(resolvedNav: dict, references: dict, validateInternal: bool = True) -> Any:
		if not isinstance(resolvedNav['data'], list):
			if resolvedNav['name'] in resolvedNav['data']:
				result = resolvedNav['data'][resolvedNav['name']]
			else:
				result = None

			selectiveResult = SoupNavigator.getSelective(result, resolvedNav['select'], resolvedNav['exclude'])

			unwrappedResult = SoupNavigator.handleUnwrap(resolvedNav, selectiveResult)

			return unwrappedResult

		results = []
		for dataItem in resolvedNav['data']:
			newNav = dict(resolvedNav)
			newNav['data'] = dataItem

			result = SoupNavigator.dictAccessNav(newNav, references, validateInternal)

			results.append(result)

		return results

	@staticmethod
	def _handleThen(then: dict, result: Any, references: dict, validate: bool = True, logFile: str = None) -> Any:
		if isinstance(then, dict):
			if not isinstance(result, list):
				# 1 result - 1 then

				newThen = dict(then)
				newThen['data'] = result

				return SoupNavigator.eval(newThen, references, validate, logFile)

			# n results - 1 then

			results = []
			for dataItem in result:
				results.append(SoupNavigator._handleThen(then, dataItem, references, validate, logFile))

			return results

		if isinstance(result, list):
			# n results - n thens

			minLen = min(len(result), len(then))

			results = []
			for index in range(minLen):
				results.append(
					SoupNavigator._handleThen(then[index], result[index], references, validate, logFile)
				)

			return results

		# 1 result - n thens

		results = []
		for thenPart in then:
			results.append(SoupNavigator._handleThen(thenPart, result, references, validate, logFile))

		return results

	@staticmethod
	def _evalDirect(nav: dict, references: dict, validate: bool = True, logFile: str = None) -> Any:
		try:
			resolvedNav = SoupNavigator.getResolved(nav, references, validate)

			result = NAV_FN_DATA[nav['__nav__']](resolvedNav, references, validate)

			if ('then' not in nav) or (nav['then'] is None) or (isinstance(nav['then'], (dict, list)) and len(nav['then']) == 0):
				return result

			return SoupNavigator._handleThen(nav['then'], result, references, validate)

		except Exception as e:
			if logFile is not None:
				data = resolvedNav['data']
				del resolvedNav['data']

				with open(logFile, 'wt', encoding='utf-8') as file:
					file.write(f'Error evaluating nav: {resolvedNav}\nException: {str(e)}\n\n')
					file.write(str(data))

			raise e

	@staticmethod
	def eval(nav: dict, references: dict, validate: bool = True, logFile: str =  None) -> Any:
		if nav['__nav__'] not in NAV_FN_DATA:
			raise Exception(f'Invalid nav type: {nav["__nav__"]}')

		if not validate:
			return SoupNavigator._evalDirect(nav, references, validate, logFile)

		validationData = NavValidator.validate(nav, references)

		if validationData['success']:
			return SoupNavigator._evalDirect(nav, references, validate, logFile)

		print(f'Error evaluating nav: {nav}\n')
		raise validationData['error']

NAV_FN_DATA = {
	'function': SoupNavigator.functionNav,
	'method': SoupNavigator.methodNav,
	'property': SoupNavigator.propertyNav,
	'dictAccess': SoupNavigator.dictAccessNav
}
