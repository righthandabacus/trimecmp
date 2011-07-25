#!/usr/bin/env python
# This program takes two input files: (1) a Rocketfuel format topology file and
# (2) traffic matrix file with the format of
#     <node> <node> <load>
# where the <node> is the code correspond to the topology file and the <load>
# is a floating point number less than one. The link capacity is assume to be
# one for all links.
# 
# The program finds k paths between every pair of nodes mentioned in the
# traffic matrix, which k is a parameter to this program. The paths are found
# such that it minimizes the resultant network cost when each of the k paths
# carries 1/k of the load for the pair of node.
#

import getopt,sys,random,heapq

###########################################################
# Global parameters
topofile = 'topology.txt'	# default topology file
matrixfile = 'matrix.txt'	# default matrix file
k = 4				# default number of paths to find for a pair
shortest = False		# use only shortest path
digraph = False			# topology specification is a digraph
overshoot = 25.0		# percentage of length overshoot (w.r.t. shortest path) tolerated, effective only if shortest==False

#random.seed(1)
optlist, userlist = getopt.getopt(sys.argv[1:], 't:m:k:dso:')
for opt, optarg in optlist:
	if opt == '-t':
		topofile = optarg
	elif opt == '-m':
		matrixfile = optarg
	elif opt == '-k':
		n = int(optarg)
		if n > 0: k = n
	elif opt == '-d':
		digraph = True
	elif opt == '-s':
		shortest = True
	elif opt == '-o':
		n = float(optarg)
		if n > 0: overshoot = n
	else:
		# getopt will fault for other options
		sys.exit(1)

###########################################################
# Helper functions
def ReadInput(f1, f2):
	"""
	Read in a Rocketfuel format topology file, then a traffic matrix file.
	At this moment, we assume all link distances are 1 and capacities are 1
	as well. Changes can be made but it is not in the Rocketfuel file.
	"""
	print "Reading input file %s" % f1
	topoFile = open(f1, "r")	# Topology file
	nodeDic = {}
	nodes = []	# names of nodes
	links = []	# links as an ordered pair of node IDs
	length = []	# lengths of links
	capacity = []	# link capacities
	for line in topoFile:
		token = line.split()
		if (len(token) < 2): continue
		if token[0] == "N":	# specifying a node by its name
			nodes.append(token[1])
			nodeDic[token[1]] = len(nodes) - 1
		elif token[0] == "l":	# specifying a link as a connection between two nodes
			e = (nodeDic[token[1]], nodeDic[token[2]])
			links.append(e)
			length.append(1 if len(token) < 4 else token[3])
			capacity.append(1 if len(token) < 5 else token[4])
			if not digraph:
				links.append((e[1],e[0]))
				length.append(length[-1])
				capacity.append(capacity[-1])
	topoFile.close()

	print "Reading input file %s" % f2
	trafficFile = open(f2, "r")	# Traffic matrix file
	traffic = {}
	for line in trafficFile:
		token = line.split()
		if (len(token) < 3): continue
		traffic[nodeDic[token[0]], nodeDic[token[1]]] = float(token[2])
	trafficFile.close()
	return nodes, links, length, capacity, traffic

class memoized(object):
	""" Copied from http://wiki.python.org/moin/PythonDecoratorLibrary
	Decorator that caches a function's return value each time it is called.
	If called later with the same arguments, the cached value is returned, and
	not re-evaluated.
	"""
	def __init__(self, func):
		self.func = func
		self.cache = {}
	def __call__(self, *args):
		try:
			return self.cache[args]
		except KeyError:
			value = self.func(*args)
			self.cache[args] = value
			return value
		except TypeError:
			# uncachable -- for instance, passing a list as an argument.
			# Better to not cache than to blow up entirely.
			return self.func(*args)
	def __repr__(self):
		"""Return the function's docstring."""
		return self.func.__doc__
	def __get__(self, obj, objtype):
		"""Support instance methods."""
		return functools.partial(self.__call__, obj)

@memoized
def BellmanFord(t):
	"""
	Use Bellman-Ford to deduce the shortest path tree of any node to t
	"""

	d = [float('inf') for i in nodes]	# Shortest distance to t
	n = [-1 for i in nodes]			# Next hop toward t
	d[t] = 0
	for i in range(len(nodes)-1):
		for j,(u,v) in enumerate(links):
			if d[u] > d[v] + length[j]:
				d[u] = d[v] + length[j] 
				n[u] = v
	return n,d

def ComputeCost(pathlinks):
	c = max(linkload[l] for l in pathlinks)
	return c

def Sidetrack2Path(tree, sidetracks, s, t):
	"""
	Given a shortest-path tree toward destination t, and a set of
	sidetracked edges, deduce the path from s to t.
	It assumes the sidetracked edges are valid, i.e. no two sidetracked
	edges are parallel to each other.
	"""
	visited = set()		# visited nodes
	path = []		# set of edges
	sidenodes = set(links[e][0] for e in sidetracks)	# nodes that needs to be sidetracked
	current = s
	while current != t:
		# Loop detection
		if current in visited:
			return []
		else:
			visited.add(current)
		# No loop is found yet, proceed one hop
		if current in sidenodes:
			edge = [e for e in sidetracks if links[e][0] == current]
			current = links[edge[0]][1]
			path.append(edge[0])
		else:
			edge = [i for i,e in enumerate(links) if e == (current,tree[current])]
			current = links[edge[0]][1]
			path.append(edge[0])
	# Destination reached. Return the path
	return path

@memoized
def Eppstein(s,t):
	"""
	Find a number of paths joining nodes s and t. The topology is stored in
	array `links'. The nodes s and t refers to the node sequence numbers
	with respect to the array `nodes'.
	"""

	# Eppstein's algorithm for k shortest path. In below we have
	#    tree = the next hop node as in the shortest path tree
	#    dist = distance from a node (w.r.t. `nodes') to t
	#    intree = links (w.r.t. `links') that is in the shortest path tree
	#    sidetrk = links (w.r.t. `links') that can be a sidetrack
	#    delta = the "delta value" of every link (w.r.t. `links')
	#    paths = array to store the paths joining s to t, manipulated with heapq
	#    leaves = the leave nodes of the heap `paths'
	tree, dist = BellmanFord(t)
	intree = [i for i,e in enumerate(links) if tree[e[0]] == e[1]]
	sidetrk = [i for i,e in enumerate(links) if i not in intree and tree[e[1]] != e[0]]
	delta = dict([i,length[i]+dist[e[1]]-dist[e[0]]] for i,e in enumerate(links))
	paths = []
	leaves = []

	# The default shortest path
	heapq.heappush(paths,(dist[s],[]))
	heapq.heappush(leaves,paths[0])
	# In case we limit our search to only shortest path, use only delta=0 sidetracks
	if shortest:
		sidetrk = [e for e in sidetrk if delta[e]==0]
	# Find 10*k number of paths
	while len(paths) < 10*k:
		# In this while-loop, a leaf node from the heap `paths' are
		# retrieved and a sidetrack edge is added to it to form a new
		# path. Once a new path is found, add to the heap as a new
		# leaf node.
		leafdist, leafside = heapq.heappop(leaves)
		sidenode = set(links[e][0] for e in leafside)	# nodes that needs to be sidetracked
		for edge in sidetrk:
			# verify if the sidetracked edge is paralleled with another
			if links[edge][0] in sidenode: continue
			# avoid too lengthy paths w.r.t. the shortest path
			currentside = leafside[:]
			currentside.append(edge)
			if sum(delta[i] for i in currentside) > dist[s]*(overshoot/100.0): continue
			# avoid duplicated set of sidetrack edges: sort them in order
			currentside.sort()
			if [sides for d, sides in paths if sides == currentside]: continue
			# Find the path
			currentpath = Sidetrack2Path(tree, currentside, s, t)
			# Add the path to repository if it is loop-free and contains the new sidetracked edge
			visited = set(links[e][0] for e in currentpath)
			if edge in currentpath and sidenode < visited:
				newpath = (leafdist + delta[edge], currentside)
				heapq.heappush(paths, newpath)
				heapq.heappush(leaves, newpath)
		# quit if we exhausted all the paths (to avoid poping an empty heap)
		if len(leaves)==0: break
	return tree,paths

def FindKPaths(s,t):
	'''
	Find the k best paths joining s to t
	'''
	# Use Eppstein's algorithm to find a large number (10*k) of paths
	tree,paths = Eppstein(s,t)

	# Amongst the 10*k paths, find the best k
	pathcost = []
	for p in paths:
		pathlinks = Sidetrack2Path(tree, p[1], s, t)
		pathcost.append((ComputeCost(pathlinks), pathlinks))
	sortedcost = sorted(i[0] for i in pathcost)
	selectedPath = []
	while len(selectedPath) < k and len(sortedcost) > 0:
		mincost = sortedcost[0]
		indices = [i for i in range(len(paths)) if pathcost[i][0] == mincost]
		minlen = min(paths[i][0] for i in indices)
		indices = [i for i in indices if paths[i][0] == minlen]
		random.shuffle(indices)
		for i in indices:
			selectedPath.append(pathcost[i][1])
			sortedcost = sortedcost[1:]
			if len(selectedPath) == k: break
	for p in selectedPath:
		pathnode = [nodes[links[p[0]][0]]] + [nodes[links[l][1]] for l in p]
		print "Path (%s,%s) : %s" % (nodes[s], nodes[t], " ".join(pathnode))
	return selectedPath

###########################################################
# Step 1:
#   Read in data
nodes, links, length, capacity, traffic = ReadInput(topofile, matrixfile)

###########################################################
# Step 2:
#   Path-finding for each pair

linkload = [0 for l in links]
pairs = traffic.keys()
random.shuffle(pairs)
allpaths = []
for pair in pairs:
	# Find k paths
	paths = FindKPaths(pair[0], pair[1])
	# For each link in the path, increase the load by rho/k
	for l in [ll for p in paths for ll in p]:
		linkload[l] += traffic[pair]/len(paths)
	# Keep the paths
	allpaths.extend(paths)

###########################################################
# Step 3:
#   Fine-tuning result
print "Link loads"
print "\n".join(str(["(%s,%s)" % (nodes[e[0]], nodes[e[1]]),linkload[i]]) for i,e in sorted(enumerate(links),key=lambda x:linkload[x[0]]))
improved = True
while improved:
	# Find the paths that pass through bottleneck links
	maxload = max(linkload)
	hotlinks = [l for l in range(len(links)) if linkload[l]==maxload]
	heavypaths = [p for p in allpaths if set(p) & set(hotlinks)]
	improved = False
	for path in heavypaths:
		s,t = links[path[0]][0], links[path[-1]][1]
		parallelpaths = [p for p in allpaths if links[p[0]][0]==s and links[p[-1]][1]==t]
		# Try to find an alternative path to this path
		tree,paths = Eppstein(s,t)
		pathcost = []
		for p in paths:
			pathlinks = Sidetrack2Path(tree, p[1], s, t)
			if set(pathlinks) & set(hotlinks): continue
			if pathlinks in parallelpaths: continue
			headroom = maxload - max(linkload[l] for l in pathlinks)
			if len(parallelpaths) < k:
				if headroom <= traffic[s,t]/(len(parallelpaths)+1): continue
			else:
				if headroom <= traffic[s,t]/k: continue
			pathcost.append((ComputeCost(pathlinks), pathlinks))
		if len(pathcost)==0: continue
		# Alternative path available: Update link costs
		mincost,minpath = min(pathcost)
		allpaths.append(minpath)
		if len(parallelpaths) < k:
			# add this path as we did not have k paths for this pair yet
			for l in minpath:
				linkload[l] += traffic[s,t]/(len(parallelpaths)+1)
			for l in (ll for p in parallelpaths for ll in p):
				linkload[l] += traffic[s,t]/(len(parallelpaths)+1) - traffic[s,t]/len(parallelpaths)
			pathnode = [nodes[s]] + [nodes[links[l][1]] for l in minpath]
			print "Added (%s,%s) : %s" % (nodes[s], nodes[t], " ".join(pathnode))
		else:
			# replace path to keep only k paths for this pair
			allpaths.remove(path)
			for l in minpath:
				linkload[l] += traffic[s,t]/len(parallelpaths)
			for l in path:
				linkload[l] -= traffic[s,t]/len(parallelpaths)
			pathnode = [nodes[s]] + [nodes[links[l][1]] for l in path]
			print "Removed (%s,%s) : %s" % (nodes[s], nodes[t], " ".join(pathnode))
			pathnode = [nodes[s]] + [nodes[links[l][1]] for l in minpath]
			print "Added (%s,%s) : %s" % (nodes[s], nodes[t], " ".join(pathnode))
		improved = True

###########################################################
# Step 4:
#   Output result to console
print "All the paths:"
for p in allpaths:
	pathnode = [nodes[links[p[0]][0]]] + [nodes[links[l][1]] for l in p]
	print "(%s,%s) : %s" % (nodes[s], nodes[t], " ".join(pathnode))
print "Link loads"
print "\n".join(str(["(%s,%s)" % (nodes[e[0]], nodes[e[1]]),linkload[i]]) for i,e in sorted(enumerate(links),key=lambda x:linkload[x[0]]))

sys.exit(1)
