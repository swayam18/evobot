from cv2 import *
import urllib 
import numpy as np
import time

# This code works perfectly!

TRANS_MATRIX = []
AFFLINE_MATRIX = []

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
  subtracted = np.absolute(np.subtract(current,background))
  #imwrite(dst, subtracted)
  return subtracted

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
def imfilter(thmap):
  # First, use median filter
  dst = medianBlur(thmap,3)
  #imwrite("median.jpg", dst)
  # Then, define kernel and apply a morphological open
  kernel = getStructuringElement(MORPH_RECT,(3,3))
  e_dst = erode(dst,kernel)
  de_dst = dilate(e_dst,kernel)

  #imwrite("result.jpg", de_dst)
  return de_dst

def imcontours(img):
  contours,hierarchy= findContours(img,RETR_TREE,CHAIN_APPROX_SIMPLE)
  hierarchy = hierarchy[0]      #Extra Dimension Removal!
  return(contours, hierarchy)
  
def imcenters(contours):
  for contour in contours:
    M = moments(contour)
    location =  M['m10']/M['m00'],M['m01']/M['m00']
    print "Location:", map_pixel(location)

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

def track_loop():
  stream=urllib.urlopen('http://192.168.28.102/mjpeg.cgi')
  bytes=''
  previous = None
  current = None
  future = None
  while True:
      bytes+=stream.read(1024)
      a = bytes.find('\xff\xd8')
      b = bytes.find('\xff\xd9')
      if a!=-1 and b!=-1:
        jpg = bytes[a:b+2]
        bytes= bytes[b+2:]
        i = imdecode(np.fromstring(jpg, dtype=np.uint8),0)
        print 'here'
        future = i
        if previous == None or current == None or future == None:
          pass
        else:
          s1 = subtract(current,previous)
          s2 = subtract(future,current)

          thmap = threshmap(s1,s2)
          result = imfilter(thmap)
          imshow('i',result)
          if waitKey(1) ==27:
            exit(0)

          #contours = imcontours(result)[0] #get contour
          #imcenters(contours)
          #drawbox(current,contours)
          #imwrite("tracked_new/tracked_{}.jpg".format(time.time),current)

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

