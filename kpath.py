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
maxpaths = 100			# maximum number of paths to return from the FindPaths function

random.seed(1)
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

BellmanFordMemoize = dict()
def BellmanFord(t):
	"""
	Caching function for _BellmanFord(): The distance to destination t is
	returned from cache BellmanFordMemoize. If not in cache, call
	_BellmanFord(t).
	"""
	try:
		n,d = BellmanFordMemoize[t]
	except KeyError:
		n,d = _BellmanFord(t)
	return n,d

def _BellmanFord(t):
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
	c = sum(linkload[l] for l in pathlinks)
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

def FindKPaths(s,t):
	"""
	Find k paths joining nodes s and t. The topology is stored in array
	`links'. The nodes s and t refers to the node sequence numbers with
	respect to the array `nodes'.
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
	# Find a large number of paths
	random.shuffle(sidetrk)
	while True:
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
		# or if we enumerated too many paths
		if len(leaves)==0 or len(paths) >= maxpaths: break
	# convert paths from sidetrack-based notation to edge-based notation
	edgepaths = []
	for p in paths:
		edgepaths.append( Sidetrack2Path(tree, p[1], s, t) )
	# return
	return edgepaths

###########################################################
# Step 1:
#   Read in data
nodes, links, length, capacity, traffic = ReadInput(topofile, matrixfile)

###########################################################
# Step 2:
#   Path-finding for each pair

linkload = [0 for l in links]
pairs = traffic.keys()
allpaths = dict()
for i in range(k):
	random.shuffle(pairs)
	for pair in pairs:
		# Find a set of paths
		try:
			if len(allpaths[pair]) < i: continue
		except KeyError:
			allpaths[pair] = []
		paths = [p for p in FindKPaths(pair[0], pair[1]) if p not in allpaths[pair]]
		if len(paths) == 0: continue
		# Amongst the paths, find the best one:
		# Find the min cost according to the cost function, then use
		# path length as the tie-breaker, then randomly choose one
		pathcosts = [(ComputeCost(path), path) for path in paths]
		mincost = min(j[0] for j in pathcosts)
		pathlens = [(sum(length[l] for l in path), path) for cost,path in pathcosts if cost==mincost]
		minlen = min(j[0] for j in pathlens)
		pathpool = [j[1] for j in pathlens if j[0] == minlen]
		bestpath = random.choice(pathpool)
		# Check if we need one more path for this pair
		if len(allpaths[pair]) == 0:
			# unconditionally add the best path and increase load
			allpaths[pair].append(bestpath)
			for l in bestpath:
				linkload[l] += traffic[pair];
			pathnode = [nodes[links[bestpath[0]][0]]]
			for l in bestpath:
				pathnode.append(nodes[links[l][1]])
			print "(%s,%s) : %s" % (nodes[pair[0]], nodes[pair[1]], " ".join(pathnode))
		else:
			# compare load for with vs without the bestpath
			newload = linkload[:]
			linkset = set()
			for l in [ll for p in allpaths[pair] for ll in p]:
				newload[l] += traffic[pair] * (1.0/(len(allpaths[pair])+1)-1.0/len(allpaths[pair]))
				linkset.add(l)
			for l in bestpath:
				newload[l] += traffic[pair]/(len(allpaths[pair])+1)
				linkset.add(l)
			oldmax = max(linkload[l] for l in linkset)
			newmax = max(newload[l] for l in linkset)
			if newmax < oldmax:
				linkload = newload
				allpaths[pair].append(bestpath)
				pathnode = [nodes[links[bestpath[0]][0]]]
				for l in bestpath:
					pathnode.append(nodes[links[l][1]])
				print "(%s,%s) : %s" % (nodes[pair[0]], nodes[pair[1]], " ".join(pathnode))

###########################################################
# Step 3:
#   Output result to console
print "All the paths:"
for (pair,paths) in allpaths.iteritems():
	print "  (%s,%s): %d path(s)" % (nodes[pair[0]], nodes[pair[1]], len(paths))
	for p in paths:
		pathnode = [nodes[links[p[0]][0]]]
		for l in p:
			pathnode.append(nodes[links[l][1]])
		print "    %s" % (" ".join(pathnode))
print "Link loads"
print "\n".join([str(["(%s,%s)" % (nodes[e[0]], nodes[e[1]]),linkload[i]]) for i,e in enumerate(links)])

sys.exit(1)
