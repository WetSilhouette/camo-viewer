import json

from .utils import PlayerPrefs
from .utils.logger import log

PREFS_KEY = 'favorites.json'

_favorites = None


def _load():
  global _favorites
  if _favorites is not None:
    return
  raw = PlayerPrefs.get(PREFS_KEY, '[]')
  try:
    _favorites = set(json.loads(raw))
  except Exception:
    log('Favorites: failed to parse stored favorites, resetting')
    _favorites = set()


def _save():
  PlayerPrefs.set(PREFS_KEY, json.dumps(list(_favorites)))


def isFavorite(intCD):
  _load()
  return intCD in _favorites


def toggle(intCD):
  _load()
  if intCD in _favorites:
    _favorites.discard(intCD)
    result = False
  else:
    _favorites.add(intCD)
    result = True
  _save()
  log('Favorites: toggled intCD=' + str(intCD) + ' -> ' + str(result))
  return result
