class CameraFreezeException(Exception):
  pass

def handler(signum, frame):
  print 'camera froooze'
  raise CameraFreezeException("Camera Froze!")
