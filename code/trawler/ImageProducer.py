import threading
import time
import urllib2

class ImageProducer:
  'Gets and saves webcam image from the camera'

  def __init__(self):
    self.root = 'http://192.168.28.219'
    self.url = "http://192.168.28.219/snapshot.cgi"
    self.storage = "snapshots/"

  # Perfom HTTP basic auth
  def authenticate(self):
    username = 'admin'
    password = ''

    print "Authenticating..."
    p = urllib2.HTTPPasswordMgrWithDefaultRealm()
    p.add_password(None, self.root, username, password)
    handler = urllib2.HTTPBasicAuthHandler(p)
    opener = urllib2.build_opener(handler)
    urllib2.install_opener(opener)
    print "Authenticated!"

  # Download Image from the Gateway
  def get_image(self):
    print "Opening connection"
    img_file = urllib2.urlopen(self.url)
    img = img_file.read()
    print "Reading..."
    name = self.get_file_name()
    f = open(name,'wb')
    print "Saving..."
    for line in img:
      f.write(line)
    f.close()
    print "job done!"

  def get_file_name(self):
    return "{}image_{}.jpg".format(self.storage,time.time())


  # Spawn multiple threads that do parallel imgae get
  def parallel_get_image(self,n = 1):
    threads = []

    for i in range(n):
      t = threading.Thread(target=self.get_image)
      t.daemon = True;
      t.start()
      threads.append(t)

    for t in threads:
      t.join()

    threading.Timer(1,self.parallel_get_image,()).start()

p = ImageProducer()
p.authenticate()
p.parallel_get_image()

