import requests
import threading
import cProfile

root = "http://localhost:3000/robots/"
remote_root = "http://evobot-proxy.herokuapp.com/robots/"

def test():
  requests.get(root)

def set_state(name, state):
  data = {}
  url = root+name+'/'
  data["state"] = state
  put(url,data)
  
def prey_add_location(x,y, remote=False):
  add_location('prey', x, y, remote)

def predator_add_location(x,y, remote =False):
  add_location('predator', x, y)

def add_location(name, x, y, remote=False):
  data = {}
  data["x"] = x
  data["y"] = y
  url = root+name+'/location'
  remote_url = remote_root+name+'/location'
  thread = threading.Thread(target=post, args=(url,data,))
  thread.start()
  if remote:
    # also populate the remote server
    remote_thread = threading.Thread(target=post, args=(url,data,))
    remote_thread.start()
  return thread

def put(url,data):
  requests.put(url, json = data)

def post(url,data):
  requests.post(url, json = data)

if __name__ == '__main__':
  prey_add_location(415,12, remote = True)
  predator_add_location(11,12)
  set_state("prey", 1)
  set_state("predator", 1)
  print "done"
