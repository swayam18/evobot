from cv2 import *
#from sklearn.cluster import KMeans
import urllib 
import numpy as np
import time
import kcluster
import copy
import time
import manager
import proxy
import socket

socket.setdefaulttimeout(5.0)

# This code works perfectly!

TRANS_MATRIX = []
AFFLINE_MATRIX = []
ROBOTS_COUNT = 2

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
  #subtracted = np.absolute(np.subtract(current,background))
  subtracted = absdiff(current, background)
  #imwrite(dst, subtracted)
  return subtracted

def fast_threshmap(im1, im2):
  r, thresh1 = threshold(im1,10,255,THRESH_BINARY)
  r, thresh2 = threshold(im2,10,255,THRESH_BINARY)

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
  #imwrite("threshmap.jpg",out)
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
      centre = (M['m10']/M['m00'],M['m01']/M['m00'])
      X.append(centre)

    except ZeroDivisionError:
      print 'ZERO!'
  if len(X) >= 2:
    means, clusters = kcluster.cluster(np.asarray(X), ROBOTS_COUNT, np.asarray(prev))
    print means
    #km = KMeans(n_clusters = ROBOTS_COUNT,n_init=1, verbose=1, init=np.asarray(prev)).fit(np.asarray(X))
    #means = km.cluster_centers_
    #labels = km.labels_
    #clusters = cluster_points(X,labels)
    
  return means, clusters
  
def imcenters(contours):
  for contour in contours:
    M = moments(contour)
    try:
      location =  M['m10']/M['m00'],M['m01']/M['m00']
      #print "Location:", map_pixel(location)
      print "Location:", location
    except ZeroDivisionError:
      print 'ZERO!'

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


def track_loop():
  previous = None
  current = None
  future = None
  prev_locations = [(23,230),(355,100)]
  cap = VideoCapture('vid2.avi')

  while cap.isOpened():
    ret,orig = cap.read()
    frame = cvtColor(orig, COLOR_BGR2GRAY)
    k = copy.copy(frame)
    if not ret: break
    i = frame
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
         for i,m in enumerate(mu):
           m = tuple(map(int, m))
           points = clusters[i]
           #circle(current_copy,m,20,(255))
           for p in points:
             p = tuple(map(int, p))
             circle(orig,p,2,(255,255,255))

       if prev_locations != None:
         colors = [(255,0,0), (0,0,255)]
         for i,p in enumerate(prev_locations):
           l = tuple(map(int, p))
           circle(orig,l,20,colors[i])

      imshow('i',orig)
      #video.write(current_copy)
      if waitKey(1) ==27:
        exit(0)

    previous = current
    current = future

def track():
  previous = imread("0.jpg",0)
  current = imread("1.jpg",0)
  future = imread("2.jpg",0)
  s1 = subtract(current,previous)
  s2 = subtract(future,current)
  thmap = threshmap(s1,s2)
  result = imfilter(thmap)
  contours = imcontours(result)[0]
  imcenters(contours)
  drawbox(current,contours)
  imwrite("tracked.jpg",current)

def temp_test():
  setTransformationMatrix()
  setAfflineMatrix()
  map_pixel([87, 73])

#track()
#temp_test()
track_loop()
c = waitKey(0)
