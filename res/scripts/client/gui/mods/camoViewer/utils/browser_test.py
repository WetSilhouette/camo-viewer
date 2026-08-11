import threading
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from socket import error as SocketError

from .logger import log

TEST_HTML = u"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {
    margin: 0;
    background: #1b1f24;
    color: #e8e8e8;
    font-family: Arial, sans-serif;
  }
  h1 {
    padding: 12px 16px;
    margin: 0;
    font-size: 18px;
    border-bottom: 1px solid #333;
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 8px;
    padding: 16px;
  }
  .tile {
    aspect-ratio: 1;
    background: #2a2f36;
    border: 1px solid #3d4451;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    color: #9aa5b1;
  }
</style>
</head>
<body>
  <h1>camo-viewer Phase 1 browser-overlay test (local HTTP)</h1>
  <div class="grid">
    %s
  </div>
</body>
</html>
""" % u''.join(u'<div class="tile">%d</div>' % i for i in range(1, 25))

_PORTS_POOL = (50100, 50101, 50102, 50103, 50104)
_server = None
_serverThread = None


class _Handler(BaseHTTPRequestHandler):

  def do_GET(self):
    body = TEST_HTML.encode('utf-8')
    self.send_response(200)
    self.send_header('Content-Type', 'text/html; charset=utf-8')
    self.send_header('Content-Length', str(len(body)))
    self.end_headers()
    self.wfile.write(body)

  def log_message(self, fmt, *args):
    log('[http] ' + (fmt % args))


def _ensureServer():
  global _server, _serverThread
  if _server is not None:
    return _server.server_port
  for port in _PORTS_POOL:
    try:
      _server = HTTPServer(('127.0.0.1', port), _Handler)
      break
    except SocketError:
      continue

  if _server is None:
    log('failed to bind local http server on any port in ' + str(_PORTS_POOL))
    return None
  _serverThread = threading.Thread(target=_server.serve_forever)
  _serverThread.daemon = True
  _serverThread.start()
  log('local http server listening on 127.0.0.1:' + str(_server.server_port))
  return _server.server_port


def showBrowserTest():
  from gui.shared.event_dispatcher import showBrowserOverlayView
  port = _ensureServer()
  if port is None:
    return
  url = 'http://127.0.0.1:' + str(port) + '/'
  log('opening browser overlay at ' + url)
  showBrowserOverlayView(url)
