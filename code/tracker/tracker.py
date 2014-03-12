import numpy as np
from cv2 import *

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
  imwrite("median.jpg", dst)
  # Then, define kernel and apply a morphological open
  kernel = getStructuringElement(MORPH_RECT,(3,3))
  e_dst = erode(dst,kernel)
  de_dst = dilate(e_dst,kernel)

  imwrite("result.jpg", de_dst)
  return de_dst

def contours(img):
  contours,hierarchy= findContours(img,RETR_TREE,CHAIN_APPROX_SIMPLE)
  hierarchy = hierarchy[0]      #Extra Dimension Removal!
  return(contours, hierarchy)
  
def imcenters(contours):
  for contour in contours:
    M = moments(contour)
    print "Location:",M['m10']/M['m00'],M['m01']/M['m00']

def drawbox(img,contours):
  for contour in contours:
    x,y,w,h = boundingRect(contour)
    rectangle(img,(x,y),(x+w,y+h),(255,0,0),2) 
  imshow("Result",img) 


previous = imread("0.jpg",0)
current = imread("1.jpg",0)
future = imread("2.jpg",0)

s1 = subtract(current,previous,dst="s1.jpg")
s2 = subtract(future,current,dst="s2.jpg")
thmap = threshmap(s1,s2)
result = imfilter(thmap)
contours = contours(result)[0]
imcenters(contours)
drawbox(current,contours)

c = waitKey(0)
