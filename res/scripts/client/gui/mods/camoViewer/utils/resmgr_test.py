import ResMgr

from .logger import log

TEST_PATH = 'gui/camoViewer/test_resource.xml'


def runResMgrTest():
  section = ResMgr.openSection(TEST_PATH)
  if section is None:
    log('ResMgr test FAILED: openSection(' + TEST_PATH + ') returned None')
    return
  marker = section.readString('marker')
  log('ResMgr test OK: openSection(' + TEST_PATH + ') found it, marker=' + marker)
