from cv2 import *
import urllib 
import numpy as np
import time
import sys
import kcluster
import copy
import time
import manager
import proxy
import socket
import freeze
import signal
import interrupt

socket.setdefaulttimeout(5.0)

TRANS_MATRIX = []
AFFLINE_MATRIX = []
ROBOTS_COUNT = 2

def signal_handler(signal, frame):
  print('Exit Detected... Setting proxy state...')
  proxy.set_state('prey',0)
  proxy.set_state('predator',0)
  sys.exit(0)

#set the transformation matrix
def setTransformationMatrix():
  pts1 = np.float32([[439,11],[491,9],[323,434],[134,429]])
  pts2 = np.float32([[0,0], [50,0] , [50,1000], [0,1000]])
  pts2 = np.float32([[pt[0] + 1804,pt[1]+922] for pt in pts2])

  global TRANS_MATRIX
  TRANS_MATRIX = getPerspectiveTransform(pts1, pts2)

def setAfflineMatrix():
  pts1 = np.float32([[1636,1353],[1805,1353],[1805,1561]])
  pts2 = np.float32([[1.300265,103.780597], [1.300249,103.780578] , [1.300257,103.780582]])

  global AFFLINE_MATRIX
  AFFLINE_MATRIX = getAffineTransform(pts1, pts2)

#Get the difference between images
def subtract(current, background,dst="result.jpg"):
  subtracted = absdiff(current, background)
  return subtracted

def fast_threshmap(im1, im2):
  r, thresh1 = threshold(im1,30,255,THRESH_BINARY)
  r, thresh2 = threshold(im2,30,255,THRESH_BINARY)

  return bitwise_or(thresh1, thresh2)
  
# Construct a threshmap
def threshmap(im1,im2,th_min = 20 , th_max = 230):
  out = []
  rows,cols = im1.shape
  for i in range(rows):
    out_row = []
    for  j in range(cols):
      p1 = im1[i][j]
      p2 = im2[i][j]
      if (p1 > th_min and p1 < th_max) and (p2 > th_min and p2 < th_max):
        out_row.append(255)
      else:
        out_row.append(0)
    out.append(out_row)
  out = np.uint8(out)
  return out

# Improve the object recognized by threshmap using filters
kernel = getStructuringElement(MORPH_RECT,(3,3))
def imfilter(thmap):
  # First, use median filter
  dst = medianBlur(thmap,3)
  #imwrite("median.jpg", dst)
  # Then, define kernel and apply a morphological open
  e_dst = erode(dst,kernel)
  de_dst = dilate(e_dst,kernel)

  #imwrite("result.jpg", de_dst)
  return de_dst

def imcontours(img):
  try:
    contours,hierarchy= findContours(img,RETR_TREE,CHAIN_APPROX_SIMPLE)
    return contours
  except TypeError:
    return None
  
#removes noise
def cluster_points(X,labels):
  clusters = {}
  for i in range(len(X)):
    x = X[i]
    c = labels[i]
    if c == -1: continue
    if c in clusters:
      clusters[c].append(x)
    else:
      clusters[c] = [x]
  return clusters

def means(contours, prev):
  X = []
  means = []
  clusters = {}
  for contour in contours:
    M = moments(contour)
    try:
      X.append((M['m10']/M['m00'],M['m01']/M['m00']))
    except ZeroDivisionError:
      print 'ZERO!'
  if len(X) >= 2:
    means, clusters = kcluster.cluster(np.asarray(X), ROBOTS_COUNT, np.asarray(prev))

  return means, clusters
  
def drawbox(img,contours):
  for contour in contours:
    x,y,w,h = boundingRect(contour)
    rectangle(img,(x,y),(x+w,y+h),(255,0,0),2) 

def map_pixel(location):
  location.append(1)
  _location = TRANS_MATRIX.dot(location)
  transformed_location = [ _location[0]/_location[2], _location[1]/_location[2], 1] 
  print transformed_location
  gps_location = AFFLINE_MATRIX.dot(transformed_location) 
  print gps_location

# looks at frames means and evaluates robot positions
def getLocation(prev,mu): 
  q = [ manager.Point(x,y) for x,y in mu]
  if prev == None: 
    q = [manager.Point(280,15), manager.Point(280,435)]
    return q
  else:
    return manager.map_points(prev,q) 

def discover():
  for i in range(100):
    try:
      url = "http://192.168.0.%d/mjpeg.cgi"%(100+i)
      stream=urllib.urlopen(url)
      print 'Camera Found!'
      return stream
    except IOError:
      print 'Not camera: '+ url
      continue

# Given a binary image
# It returns those points that are 'white'
def point_cloud(img):
  out = []
  rows,cols = im1.shape
  for i in range(rows):
    out_row = []
    for  j in range(cols):
      if img[i][j] == 1:
        print 'white'


def track_loop(prev_locations= None):
  #stream=urllib.urlopen('http://192.168.1.1/mjpeg.cgi')
  #stream=urllib.urlopen('http://71913554.cam.trendnetcloud.com/mjpeg.cgi')
  print 'Discovering Camera...'
  stream= discover()
  codec = cv.CV_FOURCC('M','J','P','G')
  #video = VideoWriter()
  filename = "recording_%d"%int(time.time())
  #video.open(filename, codec, 24, (640,480),False)
  bytes=''
  previous = None
  current = None
  future = None
  if prev_locations == None: prev_locations = [(30,230), (620,230)]
  # test proxy
  try:
    print 'Searching for Rails server...'
    proxy.test()
  except proxy.requests.ConnectionError:
    print 'rails server not found! open a new tab in the terminal and type "rails -s"'
    return

  proxy.set_state('prey',1)
  proxy.set_state('predator',1)
  print 'rails server found... starting tracking'
  count = 0
  try: 
    while True:
      signal.alarm(3) # check for camera freeze.
      bytes+=stream.read(1024)
      if bytes == "": 
        proxy.set_state('prey',0)
        proxy.set_state('predator',0)
        break
      a = bytes.find('\xff\xd8')
      b = bytes.find('\xff\xd9')
      if a!=-1 and b!=-1:
        jpg = bytes[a:b+2]
        bytes= bytes[b+2:]
        i = imdecode(np.fromstring(jpg, dtype=np.uint8),0)
        future = i
        if previous == None or current == None or future == None:
          pass
        else:
          s1 = subtract(current,previous)
          s2 = subtract(future,current)

          thmap = fast_threshmap(s1,s2)
          result = imfilter(thmap)
          imshow('o',result)

          contours = imcontours(result) #get contour
          current_copy = copy.copy(current)
          if len(contours) != 0:
            mu, clusters = means(contours, prev_locations) 
            if len(mu):
              new_locations = mu
              prev_locations = new_locations
              robot_locations = copy.copy(prev_locations)
              for i,m in enumerate(mu):
                m = tuple(map(int, m))
                points = clusters[i]
                for p in points:
                  p = tuple(map(int, p))
                  circle(current_copy,p,2,(255))

          if prev_locations != None:
            l1 = tuple(map(int,prev_locations[0]))
            l2 = tuple(map(int,prev_locations[1]))
            circle(current_copy,l1,20,(255,0,0))
            circle(current_copy,l2,20,(0,255,0))
            if count % 24 == 0:
              send_remote = count % (24 * 3) == 0
              upload_remote = count % (24 * 300) == 0
              proxy.prey_add_location(l1[0],l1[1], remote=send_remote)
              proxy.predator_add_location(l2[0],l2[1], remote=send_remote)
              if upload_remote:
		print 'writing and uploading'
                filename= time.strftime("%Y%m%d-%H%M%S") + "-snap.jpg"
                imwrite("snaps/"+filename,current_copy)
                proxy.upload_image("snapshot.jpg")

          imshow('i',current_copy)
          #video.write(current_copy)
          if waitKey(1) ==27:
            proxy.set_state('prey',0)
            proxy.set_state('predator',0)
            exit(0)

        previous = current
        current = future
        count+=1
      else:
        print 'waiting on better data'

    proxy.set_state('prey',0)
    proxy.set_state('predator',0)
  except socket.timeout:
    print 'Camera Disappeared!'
    proxy.set_state('prey',0)
    proxy.set_state('predator',0)
  except freeze.CameraFreezeException:
    proxy.set_state('prey',0)
    proxy.set_state('predator',0)
    raise

def temp_test():
  setTransformationMatrix()
  setAfflineMatrix()
  map_pixel([87, 73])


def main_loop():
  prev_locations = [(30,230), (620,230)]
  signal.signal(signal.SIGALRM, freeze.handler)
  while True:
    try: 
      track_loop(prev_locations)
    except freeze.CameraFreezeException:
      print 'reseting camera'
      proxy.set_state('prey',0)
      proxy.set_state('predator',0)

#track()
#temp_test()
interrupt.listen()
# ctrl c
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGHUP, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
main_loop()
c = waitKey(0)
