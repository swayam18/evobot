class Point:
  def __init__(self,x,y):
    self.x = x
    self.y = y

  def distance(self,point):
    return ((self.x - point.x)**2 + (self.y - point.y)**2)**0.5

  def sq_distance(self,point):
    return (self.x - point.x)**2 + (self.y - point.y)**2

  def __repr__(self):
    return self.__str__()
  
  def __str__(self):
    return "%d,%d" % (self.x, self.y)


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
    print k,l,dm[k][l]
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
