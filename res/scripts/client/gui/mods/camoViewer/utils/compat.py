import ResMgr

from .logger import log


def logClientVersion():
  try:
    section = ResMgr.openSection('version.xml')
    if section is None:
      log('compat check: version.xml not found via ResMgr')
      return
    version = section.readString('version', '?').strip()
    client = section.readString('meta/client', '?').strip()
    realm = section.readString('meta/realm', '?').strip()
    log('running client version=' + repr(version) + ' client_build=' + repr(client) + ' realm=' + repr(realm))
  except Exception:
    log('compat check: failed to read version.xml')
