from cv2 import *
import numpy as np

# USED IN PAPER! 

img = imread("snap2.jpg")
rows,cols,ch = img.shape
pts1 = np.float32([[439,11],[491,9],[323,434],[134,429]])
pts2 = np.float32([[0,0], [50,0] , [50,1000], [0,1000]])
#pts2 = np.float32([[pt[0] + 1804,pt[1]+922] for pt in pts2])
pts2 = np.float32([[pt[0] + 902,pt[1]+461] for pt in pts2])
#print pts2

M = getPerspectiveTransform(pts1, pts2)
print M

dst = warpPerspective(img,M,(cols*5,rows*5))
#imwrite("transformed2.jpg", dst);
imshow("",dst)
waitKey(0)
