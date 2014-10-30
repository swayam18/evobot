from cv2 import * 
import urllib2
from cStringIO import StringIO
import PIL.Image as pil
import numpy

#url = "http://192.168.28.219/snapshot.cgi"
url = "http://192.168.28.102/image/jpeg.cgi" # trendnet

# username = 'admin'
# password = ''

username = 'admin'
password = 'sutd1234' # trendnet

p = urllib2.HTTPPasswordMgrWithDefaultRealm()
p.add_password(None, url, username, password)
handler = urllib2.HTTPBasicAuthHandler(p)
opener = urllib2.build_opener(handler)
urllib2.install_opener(opener)

# download image
img_file = urllib2.urlopen(url)
im = StringIO(img_file.read())
source = pil.open(im).convert("RGB")

# Convert to openCV format

image = numpy.array(source)
image = image[:,:,::-1]
imshow("hi",image)
waitKey(0)
