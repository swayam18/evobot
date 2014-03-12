from cv2 import *
import numpy as np

img = imread("snap2.jpg")
rows,cols,ch = img.shape
pts1 = np.float32([[130,205], [337,30] , [639,194], [599,5]])
pts2 = np.float32([[130,205], [337,30] , [639,194], [599,5]])

pts1 = np.float32([[401,243], [521,239], [385,279], [518,279]])
pts2 = np.float32([[385,243-133],[518,239- 133], [385,279], [518,279]])
pts2 = np.float32([[pt[0] + 1804,pt[1]+922] for pt in pts2])
print pts2

M = getPerspectiveTransform(pts1, pts2)
print M

dst = warpPerspective(img,M,(cols*5,rows*5))
imwrite("trasnfomred.jpg", dst);
waitKey(0)
