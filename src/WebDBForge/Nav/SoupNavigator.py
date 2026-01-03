from typing import Any
import bs4
from WebDBForge.Nav.NavValidator import NavValidator

class SoupNavigator:
  @staticmethod
  def functionNav(nav: dict, references: dict, validateInternal: bool = True) -> Any:
    if isinstance(nav['data'], dict):
      if '__nav__' in nav['data']:
        soup = SoupNavigator.eval(nav['data'], references, validateInternal)
      else:
        soup = references[nav['data']['ref']]
    else:
      soup = nav['data']

    if isinstance(nav['name'], dict) and '__nav__' in nav['name']:
      name = SoupNavigator.eval(nav['name'], references, validateInternal)
    else:
      name = nav['name']

    if 'args' in nav:
      if isinstance(nav['args'], dict) and '__nav__' in nav['args']:
        args = SoupNavigator.eval(nav['args'], references, validateInternal)
      else:
        args = nav['args']
    else:
      args = []

    if 'kwargs' in nav:
      if isinstance(nav['kwargs'], dict) and '__nav__' in nav['kwargs']:
        kwargs = SoupNavigator.eval(nav['kwargs'], references, validateInternal)
      else:
        kwargs = nav['kwargs']
    else:
      kwargs = {}

    result = getattr(bs4, name)(soup, *args, **kwargs)

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
  def methodNav(nav: dict, references: dict, validateInternal: bool = True) -> Any:
    if isinstance(nav['data'], dict):
      if '__nav__' in nav['data']:
        soup = SoupNavigator.eval(nav['data'], references, validateInternal)
      else:
        soup = references[nav['data']['ref']]
    else:
      soup = nav['data']

    if isinstance(nav['name'], dict) and '__nav__' in nav['name']:
      name = SoupNavigator.eval(nav['name'], references, validateInternal)
    else:
      name = nav['name']

    if 'args' in nav:
      if isinstance(nav['args'], dict) and '__nav__' in nav['args']:
        args = SoupNavigator.eval(nav['args'], references, validateInternal)
      else:
        args = nav['args']
    else:
      args = []

    if 'kwargs' in nav:
      if isinstance(nav['kwargs'], dict) and '__nav__' in nav['kwargs']:
        kwargs = SoupNavigator.eval(nav['kwargs'], references, validateInternal)
      else:
        kwargs = nav['kwargs']
    else:
      kwargs = {}

    result = getattr(soup, name)(*args, **kwargs)

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
  def propertyNav(nav: dict, references: dict, validateInternal: bool = True) -> Any:
    if isinstance(nav['data'], dict):
      if '__nav__' in nav['data']:
        soup = SoupNavigator.eval(nav['data'], references, validateInternal)
      else:
        soup = references[nav['data']['ref']]
    else:
      soup = nav['data']

    if isinstance(nav['name'], dict) and '__nav__' in nav['name']:
      name = SoupNavigator.eval(nav['name'], references, validateInternal)
    else:
      name = nav['name']

    result = getattr(soup, name)

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
  def _evalDirect(nav: dict, references: dict, validate: bool = True):
    try:
      return NAV_FN_DATA[nav['__nav__']]['nav'](nav, references, validate)
    except Exception as e:
      print(f'Error evaluating node: {nav}\n')
      raise e

  @staticmethod
  def nav(nav: dict, references: dict, validate: bool = True) -> Any:
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
