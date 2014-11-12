from cv2 import *
import urllib
import numpy as np
import socket

socket.setdefaulttimeout(3.0)

def discover():
  for i in range(100):
    try:
      url = "http://192.168.0.%d/mjpeg.cgi"%(100+i)
      stream=urllib.urlopen(url)
      return stream
    except IOError:
      print 'not'+ url
      continue
  
stream = discover()
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
