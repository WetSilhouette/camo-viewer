from gui.Scaleform.daapi.view.lobby.customization.customization_bottom_panel import CustomizationBottomPanel
from gui.Scaleform.daapi.view.lobby.customization.shared import CustomizationTabs
from gui.shared.gui_items import GUI_ITEM_TYPE

from . import Favorites
from .utils.logger import log
from .utils.OverrideLib import g_overrideLib

GRID_TABS = (CustomizationTabs.CAMOUFLAGES, CustomizationTabs.STYLES_2D)
ICON_PROP_TYPES = (GUI_ITEM_TYPE.CAMOUFLAGE, GUI_ITEM_TYPE.PROJECTION_DECAL)

_panel = None
_currentTabId = None
_tabChangeListeners = []


def isActive():
  return _panel is not None and _currentTabId in GRID_TABS


def isCamouflageTab():
  return _currentTabId == CustomizationTabs.CAMOUFLAGES


def getPanel():
  return _panel


def addTabChangeListener(callback):
  if callback not in _tabChangeListeners:
    _tabChangeListeners.append(callback)


def removeTabChangeListener(callback):
  if callback in _tabChangeListeners:
    _tabChangeListeners.remove(callback)


def getCurrentItems():
  if _panel is None:
    return []
  appliedItems = _panel._carouselDP.getAppliedItems()
  items = []
  for intCD in _panel.carouselItems:
    name = str(intCD)
    icon = ''
    season = 0
    try:
      item = _panel.service.getItemByCD(intCD)
      name = item.userName
      icon = item.icon if item.itemTypeID in ICON_PROP_TYPES else item.iconUrl
      season = item.season
    except Exception:
      log('CustomizationHook: failed to resolve item/icon for intCD=' + str(intCD))
    items.append({'intCD': intCD, 'name': name, 'icon': icon, 'applied': intCD in appliedItems, 'favorite': Favorites.isFavorite(intCD), 'season': season})
  return items


@g_overrideLib.registerEvent(CustomizationBottomPanel, '_populate')
def onPanelPopulate(self, *a, **k):
  global _panel
  _panel = self
  log('CustomizationHook: panel populated')


@g_overrideLib.registerEvent(CustomizationBottomPanel, '_dispose')
def onPanelDispose(self, *a, **k):
  global _panel, _currentTabId
  _panel = None
  _currentTabId = None
  log('CustomizationHook: panel disposed')
  for callback in list(_tabChangeListeners):
    callback()


@g_overrideLib.registerEvent(CustomizationBottomPanel, '_CustomizationBottomPanel__onTabChanged')
def onTabChanged(self, tabIndex, itemCD=None, *a, **k):
  global _currentTabId
  _currentTabId = tabIndex
  log('CustomizationHook: tab changed to ' + str(tabIndex) + ', active=' + str(isActive()))
  for callback in list(_tabChangeListeners):
    callback()
