import Keys
from gui import InputHandler

from .utils.logger import log
from .utils.browser_test import showBrowserTest
from .utils.resmgr_test import runResMgrTest
from . import CamoViewerTestWindow
from . import CamoGridWindow
from . import CustomizationHook

VERSION = '{{VERSION}}'
DEBUG_MODE = '{{DEBUG_MODE}}'

TEST_ITEMS = [{'intCD': i, 'name': 'Test item %d' % i} for i in range(1, 19)]

class CamoViewer(object):

  def __init__(self):
    log('loaded, version ' + VERSION + ', debug=' + str(DEBUG_MODE))
    InputHandler.g_instance.onKeyUp += self.handleKeyUpEvent
    CamoViewerTestWindow.setup()
    CamoGridWindow.setup()

  def dispose(self):
    InputHandler.g_instance.onKeyUp -= self.handleKeyUpEvent
    log('unloaded')

  def handleKeyUpEvent(self, event):
    if event.key == Keys.KEY_F6:
      log('F6 pressed, running browser-overlay test')
      showBrowserTest()
    elif event.key == Keys.KEY_F7:
      log('F7 pressed, running ResMgr resource test')
      runResMgrTest()
    elif event.key == Keys.KEY_F8:
      log('F8 pressed, showing CamoViewerTestWindow')
      CamoViewerTestWindow.show()
    elif event.key == Keys.KEY_F9:
      log('F9 pressed, showing CamoGridWindow with fake test data')
      CamoGridWindow.show(TEST_ITEMS)
    elif event.key == Keys.KEY_SPACE:
      if CustomizationHook.isActive():
        log('Space pressed on Camo/2D Styles tab, showing real grid')
        CamoGridWindow.show(CustomizationHook.getCurrentItems())
