REQUIRED_NAV_KEYS = ("__nav__", "data", "name")

class NavValidator:
	@staticmethod
	def baseValidation(nav: dict) -> dict:
		if not isinstance(nav, dict):
			return {'success': False, 'error': Exception('A nav must be a dict')}

		for key in REQUIRED_NAV_KEYS:
			if key not in nav:
				return {'success': False, 'error': Exception(f'A nav must at least contain following keys:\n {REQUIRED_NAV_KEYS}')}

		if nav['__nav__'] not in NAV_FN_DATA:
			return {'success': False, 'error': Exception(f'Invalid nav type: {nav['__nav__']}, must be one of the following:\n {list(NAV_FN_DATA.keys())}')}

		return {'success': True}

	@staticmethod
	def methodNav(nav: dict, references: dict) -> dict:
		return {'success': True}

	@staticmethod
	def propertyNav(nav: dict, references: dict) -> dict:
		return {'success': True}

	@staticmethod
	def dictAccessNav(nav: dict, references: dict) -> dict:
		return {'success': True}

	@staticmethod
	def validate(nav: dict, references: dict) -> dict:
		baseValidation = NavValidator.baseValidation(nav)

		if not baseValidation['success']:
			return baseValidation

		return NAV_FN_DATA[nav['__nav__']](nav, references)

NAV_FN_DATA = {
	'method': NavValidator.methodNav,
	'property': NavValidator.propertyNav,
	'dictAccess': NavValidator.dictAccessNav
}
