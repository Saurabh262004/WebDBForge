from typing import Any
import bs4
from WebDBForge.Nav.NavValidator import NavValidator

class SoupNavigator:
  @staticmethod
  def functionNav(nav: dict, references: dict, validateInternal: bool = True) -> Any:
    pass

  @staticmethod
  def methodNav(nav: dict, references: dict, validateInternal: bool = True) -> Any:
    pass

  @staticmethod
  def propertyNav(nav: dict, references: dict, validateInternal: bool = True) -> Any:
    pass

  @staticmethod
  def _navDirect(nav: dict, references: dict, validate: bool = True):
    try:
      return NAV_FN_DATA[nav['__nav__']]['nav'](nav, references, validate)
    except Exception as e:
      print(f'Error evaluating node: {nav}\n')
      raise e

  @staticmethod
  def nav(nav: dict, references: dict, validate: bool = True) -> Any:
    if nav['__nav__'] in NAV_FN_DATA:
      if validate:
        validationData = NAV_FN_DATA[nav['__nav__']]['validate'](nav, references)

        if validationData['success']:
          return SoupNavigator._navDirect(nav, references, validate)

        print(f'Error evaluating nav: {nav}\n')
        raise validationData['error']

      return SoupNavigator._navDirect(nav, references, validate)

    raise Exception(f'Invalid nav type: {nav['__nav__']}')

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
