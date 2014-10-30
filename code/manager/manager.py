import csv
import matplotlib.pyplot as plt

class Point:
  def __init__(self,x,y):
    self.x = x
    self.y = y

  def distance(self,point):
    return ((self.x - point.x)**2 + (self.y - point.y)**2)**0.5

  def sq_distance(self,point):
    return (self.x - point.x)**2 + (self.y - point.y)**2

  def __repr__(self):
    return "%f,%f" % (self.x, self.y)
  
  def __str__(self):
    return "%f,%f" % (self.x, self.y)


def construct_matrix(p,q,sq=False):
  distance_matrix = []
  for old_point in p:
    distances = []
    for new_point in q:
      if sq: distances.append(new_point.sq_distance(old_point))
      else: distances.append(new_point.distance(old_point))
    distance_matrix.append(distances)
  return distance_matrix

# Given a matrix
# It finds the indices of the minimum element
def small(matrix):
  k,l = None,None
  small = None 
  for i in range(len(matrix)):
    for j in range(len(matrix[i])):
      if matrix[i][j] == None: continue
      if small == None or matrix[i][j] < small:
        small = matrix[i][j]
        k,l = i,j
  return k,l

# Given a vector P and a vector Q
# It finds a vector P' such that
# every element in Q is in P'
# and |P-P'| is smallimized
# Greedy Search
def map_points(p,q):
  r = [point for point in p] # assume they are the same
  dm = construct_matrix(p,q)
  for i in range(len(dm)):
    k,l = small(dm) 
    r[k] = q[l]
    #print k,l,dm[k][l]
    # Remove options k and l from the matrix.
    for j in range(len(dm)):
      dm[k][j] = None
      dm[j][l] = None
  return r


# Given a vector P and a vector Q
# It constructs a distance matrix
# and chooses a vector q' such that
# every element of q is in q' and
# sum(|p-q'|**2) is minimized

# The difference is squared to penalize short and long distance.
# Notice that without the square term it is equivalent to the greedy algo
# this is because (a-c) + (b-d) == (a-d) + (b-c)
# in other words, q' is just a permutation of q. So you will always get the same sum.
# by squaring, you are penalizing distances very "unequal" to each other,
# thus operating on the assumption that in most cases, for the same duration you expect the
# robots to move roughly the same distance


def map_points_dp(p,q):
  dm = construct_matrix(p,q)
  pass
  

p = [ Point(-i+5,i+5) for i in range(0,3)]
q = [ Point(i,-i) for i in range(0,3)]

dm = construct_matrix(p,q)
r = map_points(p,q)
print p
print r

def getPositions(frames=1):
  p = []
  q = []
  fin = open('trackdata.csv')
  csvfile = csv.reader(fin)
  hits = 0
  misses = 0
  i = -1 
  for row in (csvfile):
    if row[0] !='frame': continue
    i = i + 1
    if i%frames != 0: continue
    dat =  map(float,[row[5],row[7],row[16],row[18]])
    p = [ Point(dat[0],dat[1]), Point(dat[2],dat[3]) ]
    if q!= []:
      r = map_points(p,q)
      if q[0] == r[0] and q[1] == r[1]: hits = hits + 1
      else : misses = misses + 1

      # With the points inverted
      #pb = [ p[1],p[0] ]
      #r = map_points(pb, q)
      #if q[1] == r[0] and q[0] == r[1]: hits = hits + 1
      #else : misses = misses + 1
    q = p
  #print "hits:", hits
  #print "misses:",misses
  #print "success rate:", hits*1.0/(hits+misses)*100,"%"
  return hits, misses, hits*1.0/(hits+misses)*100, hits+misses

x = []
y = []
for i in range(1,100): 
  data = getPositions(i)
  x.append(120.0/i)
  y.append(data[2])
  
plt.plot(x,y)
plt.ylabel('Tracking Accuracy')
plt.xlabel('FPS') 
plt.show()
