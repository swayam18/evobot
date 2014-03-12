# find homography
# author: max.grosse -at- ioctl.eu
# date: 2009.05.12
# released under zlib license 
import sys
from cv2 import *
import numpy as np

points = []
WINDOW_NAME = 'unwarp'

def closest_to(x,y):
    best_dist = 10e9
    best_i = -1
    for i in range(len(points)):
        (px,py) = points[i]
        dx = (px-x)
        dy = (py-y)
        d = dx*dx+dy*dy
        if d<best_dist:
            best_dist=d
            best_i=i
    return best_i

def mouse(evt,x,y,flags,ctx):
    """ Mouse Callback function to select the
    four points in the input image """
    if evt==CV_EVENT_LBUTTONUP:
        global points
        if len(points)>=4:
            points[closest_to(x,y)] = (x,y)
        else:
            points += [(x,y)]
       
        show = cvCloneImage(ctx)
        for (x,y) in points:
            cvCircle(show, cvPoint(x,y), 5, CV_RGB(255,0,0),3)
        cvShowImage(WINDOW_NAME,show)


def order_points(width,height):
    """ order points: (bottom-left, bottom-right, top-right, top-left) """
    global points
    new_points = []

    bl = closest_to(0,height)
    new_points += [points[bl]]
    del points[bl]

    br = closest_to(width,height)
    new_points += [points[br]]
    del points[br]
    
    tr = closest_to(width,0)
    new_points += [points[tr]]
    del points[tr]

    tl = closest_to(0,0)
    new_points += [points[tl]]
    del points[tl]

    points = new_points

def calc(real_width, real_height, width, height):
    """ calculates the homography """
    global points
    if len(points)!=4:
        raise Exception('need exactly four points')

    order_points(width,height)

    p = cvCreateMat(2,4,CV_64FC1)
    h = cvCreateMat(2,4,CV_64FC1)
    p2h = cvCreateMat(3,3,CV_64FC1)

    cvZero(p)
    cvZero(h)
    cvZero(p2h)

    for i in range(4):
        (x,y) = points[i]
        p[0,i] = (float(real_width)/float(width)) * x
        p[1,i] = (float(real_height)/float(height)) * y

    h[0,0] = 0
    h[1,0] = real_height

    h[0,1] = real_width
    h[1,1] = real_height

    h[0,2] = real_width
    h[1,2] = 0

    h[0,3] = 0
    h[1,3] = 0

    cvFindHomography(p,h,p2h)
    cvReleaseMat(p)
    cvReleaseMat(h)
    return p2h

        

im_in = imread("snap.jpg")
#out = cvLoadImage(sys.argv[1], 4)
rows,cols,ch = im_in.shape

width = cols
height = rows 
print 'working on %dx%d' % (width, height)
im = cvCreateImage(cvSize(width,height), IPL_DEPTH_8U, 3)
cvResize(im_in, im)

cvNamedWindow(WINDOW_NAME, 1)
cvShowImage(WINDOW_NAME, im)
cvSetMouseCallback(WINDOW_NAME, mouse, im)
cvWaitKey(0)

homo = calc(im_in.width, im_in.height, im.width, im.height)
cvSave('homography.cvmat', homo)


out = cvCloneImage(im_in)
cvWarpPerspective(im_in, out, homo)
out_small = cvCloneImage(im)
cvResize(out, out_small)
cvShowImage(WINDOW_NAME, out_small)
cvWaitKey(0)

