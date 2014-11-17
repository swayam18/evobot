import numpy as np

def cluster_points(X, mu):
  clusters = {}
  for i,m in enumerate(mu):
    clusters[i] = []

  for x in X:
    distances = [np.linalg.norm(np.subtract(x,m)) for m in mu]
    best = np.argmin(distances)
    clusters[best].append(x)

  return clusters

def reevaluate_centers(mu, clusters):
  newmu = []
  keys = sorted(clusters.keys())
  for k in keys:
      if clusters[k] == []:
        newmu.append(mu[k])
      else:
        newmu.append(np.mean(clusters[k], axis = 0))
  return newmu
 
def has_converged(mu, oldmu):
    if oldmu == None: return False 
    return set([tuple(a) for a in mu]) == set([tuple(a) for a in oldmu])

def cluster(X, K, previous):
  oldmu = None
  mu = previous
  clusters = {}
  while not has_converged(mu, oldmu):
    oldmu = mu
    # Assign all points in X to clusters
    clusters = cluster_points(X, mu)
    # Reevaluate centers
    mu = reevaluate_centers(oldmu, clusters)
  return(mu, clusters)
  
