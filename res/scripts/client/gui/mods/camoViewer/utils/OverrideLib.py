class _EventHook(object):

  def __init__(self):
    self.__handlers = []

  def __iadd__(self, handler):
    self.__handlers.append(handler)
    return self

  def __isub__(self, handler):
    if handler in self.__handlers:
      self.__handlers.remove(handler)
    return self

  def fire(self, *a, **k):
    for handler in self.__handlers:
      handler(*a, **k)


class _OverrideLib(object):

  def __init__(self):
    self.registerEvent = self.__hookDecorator(self.__registerEvent)

  def __logTrace(self, debug):
    if debug:
      import traceback
      print(traceback.format_exc())

  def __eventHandler(self, handler, debug, prepend, e, m, *a, **k):
    try:
      if prepend:
        e.fire(*a, **k)
        r = m(*a, **k)
      else:
        r = m(*a, **k)
        e.fire(*a, **k)
      return r
    except Exception:
      self.__logTrace(debug)

  def __hookDecorator(self, func):

    def Decorator1(*a, **k):

      def Decorator2(handler):
        func(handler, *a, **k)

      return Decorator2

    return Decorator1

  def __registerEvent(self, handler, cls, method, debug=True, prepend=False):
    evt = '__event_%i_%s' % (1 if prepend else 0, method)
    if hasattr(cls, evt):
      e = getattr(cls, evt)
    else:
      new_method = '__orig_%i_%s' % (1 if prepend else 0, method)
      setattr(cls, evt, _EventHook())
      setattr(cls, new_method, getattr(cls, method))
      e = getattr(cls, evt)
      m = getattr(cls, new_method)
      l = lambda *a, **k: self.__eventHandler(handler, debug, prepend, e, m, *a, **k)
      l.__name__ = method
      setattr(cls, method, l)
    e += handler


g_overrideLib = _OverrideLib()
