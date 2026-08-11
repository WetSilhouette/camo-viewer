import sys

import BigWorld
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.customization.customization_bottom_panel import CustomizationBottomPanel
from gui.Scaleform.daapi.view.lobby.customization.customization_carousel import FilterTypes
from gui.Scaleform.daapi.view.lobby.customization.shared import CustomizationTabs, isItemUsedUp
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from skeletons.gui.shared import IItemsCache

from . import Favorites
from .utils.logger import log
from .utils.OverrideLib import g_overrideLib

GRID_TABS = CustomizationTabs.ALL
ICON_PROP_TYPES = (GUI_ITEM_TYPE.CAMOUFLAGE, GUI_ITEM_TYPE.PROJECTION_DECAL)

_panel = None
_currentTabId = None
_tabChangeListeners = []
_originalUsedUpFilterState = None


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


def _rebuildCarousel():
  dp = _panel._carouselDP
  dp.invalidateFilteredItems()
  dp.buildList()
  dp.refresh()


def _revealUsedUpItems():
  global _originalUsedUpFilterState
  if _panel is None:
    return
  try:
    dp = _panel._carouselDP
    if _originalUsedUpFilterState is None:
      _originalUsedUpFilterState = dp.isFilterApplied(FilterTypes.USED_UP)
    dp.updateCarouselFilter(FilterTypes.USED_UP, True)
    _rebuildCarousel()
    log('CustomizationHook: revealed used-up-elsewhere items')
  except Exception:
    log('CustomizationHook: failed to reveal used-up items')


def _restoreUsedUpFilter():
  global _originalUsedUpFilterState
  if _panel is None or _originalUsedUpFilterState is None:
    return
  try:
    dp = _panel._carouselDP
    dp.updateCarouselFilter(FilterTypes.USED_UP, _originalUsedUpFilterState)
    _rebuildCarousel()
    log('CustomizationHook: restored used-up filter to ' + str(_originalUsedUpFilterState))
  except Exception:
    log('CustomizationHook: failed to restore used-up filter')
  _originalUsedUpFilterState = None


def _getOtherVehicleIntCDs(item):
  currentIntCD = g_currentVehicle.item.intCD if g_currentVehicle.isPresent() else None
  return [vehicleIntCD for vehicleIntCD in item.getInstalledVehicles() if vehicleIntCD != currentIntCD]


def _getVehicleName(vehicleIntCD):
  try:
    itemsCache = dependency.instance(IItemsCache)
    vehicle = itemsCache.items.getVehicles().get(vehicleIntCD)
    return vehicle.userName if vehicle is not None else None
  except Exception:
    log('CustomizationHook: failed to resolve vehicle name for intCD=' + str(vehicleIntCD) + ': ' + repr(sys.exc_info()[1]))
    return None


def getCurrentItems():
  if _panel is None:
    return []
  appliedItems = _panel._carouselDP.getAppliedItems()
  items = []
  for intCD in _panel.carouselItems:
    name = str(intCD)
    icon = ''
    season = 0
    usedUp = False
    otherVehicleName = ''
    try:
      item = _panel.service.getItemByCD(intCD)
      name = item.userName
      icon = item.icon if item.itemTypeID in ICON_PROP_TYPES else item.iconUrl
      season = item.season
      usedUp = isItemUsedUp(item)
      if usedUp:
        vehicleNames = [name for name in
                         (_getVehicleName(vehicleIntCD) for vehicleIntCD in _getOtherVehicleIntCDs(item))
                         if name is not None]
        otherVehicleName = ', '.join(vehicleNames)
    except Exception:
      log('CustomizationHook: failed to resolve item/icon for intCD=' + str(intCD) + ': ' + repr(sys.exc_info()[1]))
    items.append({'intCD': intCD, 'name': name, 'icon': icon, 'applied': intCD in appliedItems, 'favorite': Favorites.isFavorite(intCD), 'season': season, 'usedUp': usedUp, 'otherVehicleName': otherVehicleName})
  return items


@g_overrideLib.registerEvent(CustomizationBottomPanel, '_populate')
def onPanelPopulate(self, *a, **k):
  global _panel
  _panel = self
  log('CustomizationHook: panel populated')
  BigWorld.callback(0.1, _revealUsedUpItems)


@g_overrideLib.registerEvent(CustomizationBottomPanel, '_dispose')
def onPanelDispose(self, *a, **k):
  global _panel, _currentTabId
  _restoreUsedUpFilter()
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
