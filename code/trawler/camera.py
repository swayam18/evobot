from cv2 import *
import urllib
import numpy as np

stream=urllib.urlopen('http://192.168.28.102/mjpeg.cgi')
bytes = ''

while True:
  bytes+=stream.read(1024)
  a = bytes.find('\xff\xd8')
  b = bytes.find('\xff\xd9')
  if a!=-1 and b!=-1:
    jpg = bytes[a:b+2]
    bytes= bytes[b+2:]
    i = imdecode(np.fromstring(jpg, dtype=np.uint8),0)
    imshow('i',i)
    if waitKey(1) ==27:
      exit(0)
