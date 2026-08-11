import os

import BigWorld
from external_strings_utils import unicode_from_utf8

from .logger import log

getPreferencesFilePath = BigWorld.wg_getPreferencesFilePath if hasattr(BigWorld, 'wg_getPreferencesFilePath') else BigWorld.getPreferencesFilePath

_preferences_path = unicode_from_utf8(getPreferencesFilePath())[1]
PREFERENCES_PATH = os.path.normpath(os.path.join(os.path.dirname(_preferences_path), 'mods', 'silhouette.camoViewer'))

_cache = {}


def _ensureDir():
  if not os.path.isdir(PREFERENCES_PATH):
    os.makedirs(PREFERENCES_PATH)


def get(key, default=None):
  if key in _cache:
    return _cache[key]
  path = os.path.join(PREFERENCES_PATH, key)
  if not os.path.exists(path):
    return default
  try:
    f = open(path, 'rb')
    try:
      text = f.read().decode('utf-8')
    finally:
      f.close()
    _cache[key] = text
    return text
  except Exception:
    log('PlayerPrefs: failed to read ' + key)
    return default


def set(key, value):
  try:
    _ensureDir()
    _cache[key] = value
    f = open(os.path.join(PREFERENCES_PATH, key), 'wb')
    try:
      f.write(value.encode('utf-8'))
    finally:
      f.close()
  except Exception:
    log('PlayerPrefs: failed to write ' + key)
