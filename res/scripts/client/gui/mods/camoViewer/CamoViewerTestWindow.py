from frameworks.wulf.gui_constants import WindowLayer
from gui.Scaleform.framework import g_entitiesFactories, ScopeTemplates, ViewSettings
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.framework.application import AppEntry
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader

from .utils.logger import log

CAMO_VIEWER_TEST_WINDOW = 'CAMO_VIEWER_TEST_WINDOW'


class CamoViewerTestWindow(AbstractWindowView):

  def onWindowClose(self):
    self.destroy()

  def py_close(self):
    log('CamoViewerTestWindow: py_close called from AS3')
    self.onWindowClose()


def setup():
  settings = ViewSettings(
    CAMO_VIEWER_TEST_WINDOW,
    CamoViewerTestWindow,
    'silhouette.camoViewer.CamoViewerTestWindow.swf',
    WindowLayer.TOP_WINDOW,
    None,
    ScopeTemplates.VIEW_SCOPE,
  )
  g_entitiesFactories.addSettings(settings)
  log('CamoViewerTestWindow: registered alias ' + CAMO_VIEWER_TEST_WINDOW)


def show():
  appLoader = dependency.instance(IAppLoader)
  app = appLoader.getApp()
  log('CamoViewerTestWindow: loading view')
  app.loadView(SFViewLoadParams(CAMO_VIEWER_TEST_WINDOW))
