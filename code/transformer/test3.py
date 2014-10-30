from cv2 import *
import numpy as np

img = imread("snap2.jpg")
rows,cols,ch = img.shape
pts1 = np.float32([[130,205], [337,30] , [639,194], [599,5]])
pts2 = np.float32([[130,205], [337,30] , [639,194], [599,5]])

pts1 = np.float32([[401,243], [521,239], [518,279], [385,279]])
pts2 = np.float32([[385,243-133],[518,239- 133], [385,279], [518,279]])
pts2 = np.float32([[400,250],[450,250],[450,300],[400,300]])

pts1 = np.float32([[386,13],[545,6],[500,431],[0,421]])
pts2 = np.float32([[0,0], [100,0] , [100,500], [0,500]])

pts2 = np.float32([[pt[0] + 1804,pt[1]+922] for pt in pts2])
print pts2

M = getPerspectiveTransform(pts1, pts2)
print M

dst = warpPerspective(img,M,(cols*5,rows*5))
imwrite("transformed3.jpg", dst);
#imshow("",img)
waitKey(0)
