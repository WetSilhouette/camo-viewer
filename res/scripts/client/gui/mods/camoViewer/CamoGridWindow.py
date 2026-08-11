from frameworks.wulf.gui_constants import WindowLayer
from gui.Scaleform.framework import g_entitiesFactories, ScopeTemplates, ViewSettings
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader

from .utils.logger import log
from . import CustomizationHook
from . import Favorites

CAMO_GRID_WINDOW = 'CAMO_GRID_WINDOW'


class CamoGridWindow(AbstractWindowView):

  def __init__(self, ctx=None):
    super(CamoGridWindow, self).__init__(ctx)
    self.__items = ctx.get('items', []) if ctx else []

  def _populate(self):
    super(CamoGridWindow, self)._populate()
    log('CamoGridWindow: populated with ' + str(len(self.__items)) + ' items')
    self.flashObject.as_setItems(self.__items)
    self.flashObject.as_showSeasonFilter(CustomizationHook.isCamouflageTab())
    CustomizationHook.addTabChangeListener(self.__onTabChanged)

  def _dispose(self):
    CustomizationHook.removeTabChangeListener(self.__onTabChanged)
    super(CamoGridWindow, self)._dispose()

  def __onTabChanged(self):
    if CustomizationHook.isActive():
      self.__items = CustomizationHook.getCurrentItems()
      log('CamoGridWindow: tab changed, refreshing with ' + str(len(self.__items)) + ' items')
      self.flashObject.as_setItems(self.__items)
      self.flashObject.as_showSeasonFilter(CustomizationHook.isCamouflageTab())
    else:
      log('CamoGridWindow: tab changed to a non-grid tab, closing')
      self.onWindowClose()

  def onWindowClose(self):
    self.destroy()

  def py_selectItem(self, intCD):
    intCD = int(intCD)
    log('CamoGridWindow: item selected, intCD=' + str(intCD))
    panel = CustomizationHook.getPanel()
    if panel is None:
      log('CamoGridWindow: no active customization panel, ignoring selection')
      return
    panel.onSelectItem(-1, intCD, -1)

  def py_toggleFavorite(self, intCD):
    intCD = int(intCD)
    return Favorites.toggle(intCD)


def setup():
  settings = ViewSettings(
    CAMO_GRID_WINDOW,
    CamoGridWindow,
    'silhouette.camoViewer.CamoGridWindow.swf',
    WindowLayer.TOP_WINDOW,
    None,
    ScopeTemplates.VIEW_SCOPE,
  )
  g_entitiesFactories.addSettings(settings)
  log('CamoGridWindow: registered')


def show(items):
  appLoader = dependency.instance(IAppLoader)
  app = appLoader.getApp()
  log('CamoGridWindow: loading view with ' + str(len(items)) + ' items')
  app.loadView(SFViewLoadParams(CAMO_GRID_WINDOW), ctx={'items': items})
