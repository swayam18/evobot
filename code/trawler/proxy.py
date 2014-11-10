import requests
import threading
import cProfile

#root = "http://localhost:3000/robots/"
root = "http://evobot-proxy.herokuapp.com/robots/"

def set_state(name, state):
  data = {}
  url = root+name+'/'
  data["state"] = state
  put(url,data)
  
def prey_add_location(x,y):
  add_location('prey', x, y)

def predator_add_location(x,y):
  add_location('predator', x, y)

def add_location(name, x, y):
  data = {}
  data["x"] = x
  data["y"] = y
  url = root+name+'/location'
  thread = threading.Thread(target=post, args=(url,data,))
  thread.start()
  return thread

def put(url,data):
  requests.put(url, json = data)

def post(url,data):
  requests.post(url, json = data)

predator_add_location(415,12)
predator_add_location(11,12)
set_state("prey", 2)
set_state("predator", 5)
print "done"
