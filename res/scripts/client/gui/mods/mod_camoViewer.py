from .camoViewer.CamoViewer import CamoViewer

def init():
  global camoViewer
  camoViewer = CamoViewer()

def fini():
  camoViewer.dispose()
