import traceback

import Keys
from gui import InputHandler

from .utils.logger import log
from .utils.compat import logClientVersion
from .utils.browser_test import showBrowserTest
from .utils.resmgr_test import runResMgrTest
from . import CamoViewerTestWindow

VERSION = '{{VERSION}}'
DEBUG_MODE = '{{DEBUG_MODE}}'

TEST_ITEMS = [{'intCD': i, 'name': 'Test item %d' % i} for i in range(1, 19)]

CUSTOMIZATION_FEATURE_AVAILABLE = False
try:
  from . import CamoGridWindow
  from . import CustomizationHook
  CUSTOMIZATION_FEATURE_AVAILABLE = True
except Exception:
  log('COMPATIBILITY BREAK: the camo grid feature failed to import - a WoT update likely '
      'renamed/removed something this mod depends on. F6/F7/F8 debug tools still work; '
      'Space (grid) and F9 (test grid) are disabled this session. Full traceback:')
  log(traceback.format_exc())


class CamoViewer(object):

  def __init__(self):
    log('loaded, version ' + VERSION + ', debug=' + str(DEBUG_MODE))
    logClientVersion()
    InputHandler.g_instance.onKeyUp += self.handleKeyUpEvent
    CamoViewerTestWindow.setup()
    if CUSTOMIZATION_FEATURE_AVAILABLE:
      CamoGridWindow.setup()
    else:
      log('CamoGridWindow.setup() skipped - camo grid feature unavailable, see earlier log')

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
      if CUSTOMIZATION_FEATURE_AVAILABLE:
        log('F9 pressed, showing CamoGridWindow with fake test data')
        CamoGridWindow.show(TEST_ITEMS)
      else:
        log('F9 pressed, but camo grid feature is unavailable this session')
    elif event.key == Keys.KEY_SPACE:
      if CUSTOMIZATION_FEATURE_AVAILABLE and CustomizationHook.isActive():
        log('Space pressed on a customization tab, showing real grid')
        CamoGridWindow.show(CustomizationHook.getCurrentItems())
