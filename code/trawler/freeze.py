class CameraFreezeException(Exception):
  pass

def handler(signum, frame):
  raise CameraFreezeException("Camera Froze!")
