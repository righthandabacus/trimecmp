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
digraph = False

optlist, userlist = getopt.getopt(sys.argv[1:], 't:m:k:d')
for opt, optarg in optlist:
	if opt == '-t':
		topofile = optarg
	elif opt == '-m':
		matrixfile = optarg
	elif opt == '-k':
		k = int(optarg)
	elif opt == '-d':
		digraph = True
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
	nodes = []
	links = []
	for line in topoFile:
		token = line.split()
		if (len(token) < 2): continue
		if token[0] == "N":	# specifying a node by its name
			nodes.append(token[1])
			nodeDic[token[1]] = len(nodes) - 1
		elif token[0] == "l":	# specifying a link as a connection between two nodes
			e = (nodeDic[token[1]], nodeDic[token[2]])
			links.append(e)
			if not digraph: links.append((e[1],e[0]))
	topoFile.close()

	print "Reading input file %s" % f2
	trafficFile = open(f2, "r")	# Traffic matrix file
	traffic = {}
	for line in trafficFile:
		token = line.split()
		if (len(token) < 3): continue
		traffic[nodeDic[token[0]], nodeDic[token[1]]] = float(token[2])
	trafficFile.close()
	return nodes, links, traffic

def BellmanFord(t):
	"""
	Use Bellman-Ford to deduce the shortest path tree of any node to t
	"""

	d = [float('inf') for i in nodes]	# Shortest distance to t
	n = [-1 for i in nodes]			# Next hop toward t
	d[t] = 0
	for i in range(len(nodes)-1):
		changed = False
		for (u,v) in links:
			if d[u] > d[v] + 1:
				d[u] = d[v] + 1
				n[u] = v
	return n,d

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
	#    deltaSorted = list version of `delta' sorted in ascending delta value
	#    paths = array to store the paths joining s to t, manipulated with heapq
	tree, dist = BellmanFord(t)
	intree = [e for e in range(len(links)) if tree[links[e][0]]==links[e][1]]
	sidetrk = [e for e in range(len(links)) if e not in intree and tree[links[e][1]]!=links[e][0]]
	delta = dict([e,1+dist[links[e][1]]-dist[links[e][0]]] for e in range(len(links)))
	deltaSorted = [(k,delta[k]) for k in delta.keys()].sort(lambda x,y: cmp(x[1],y[1]))
	paths = []

	# The default shortest path
	heapq.heappush(paths,(dist[s],[]))
	print nodes
	print links
	print tree
	print dist
	print [links[e] for e in intree]
	print [links[e] for e in sidetrk]
	print [[links[i],delta[i]] for i in range(len(delta))]

###########################################################
# Step 1:
#   Read in data
nodes, links, traffic = ReadInput(topofile, matrixfile)

###########################################################
# Step 2:
#   Path-finding for each pair

pairs = traffic.keys()
random.shuffle(pairs)
for pair in pairs:
	paths = FindKPaths(pair[0], pair[1])

sys.exit(1)

###########################################################
# Helper functions

def FindPath(u,v,w):
	"""Find the shortest path from u to v using weight w, according to Dijkstra's algorithm"""
	d = [0 if n == u else float('inf') for n in range(len(nodes))]	# distance to n from u
	p = [None for n in nodes]	# previous node to reach n
	n = range(len(nodes))		# candidate nodes

	while (len(n)):
		# find the node with shortest distance
		t = min(n, key=lambda x: d[x])
		# if the node isaccessible, remove it from n
		if d[t] == float('inf'): break
		n = [x for x in n if x != t]
		# list all incident links
		inlink = [x for x in range(len(links)) if t in links[x]]
		# update all neighbour nodes
		for e in inlink:
			# if neighbour node s is still in n
			s = links[e][0] if links[e][1] == t else links[e][1]
			if s not in n: continue
			# compute the distance from u to s if via t
			dist = d[t] + w[e]
			# if we have a shorter distance, update d and p
			if dist < d[s]:
				d[s] = dist
				p[s] = t
	# construct the path by backtracking on p
	path = [v]
	t = v
	while p[t] != None:
		t = p[t]
		path.append(t)
	return path[-1::-1]

def N2E(n):
	"""Convert a node-based path into link-based path"""
	path = []
	for i in range(len(n)-1):
		e = [l for l in range(len(links)) if links[l] == sorted([n[i], n[i+1]])][0]
		path.append(e)
	return path

def ComputeCost(multipath, controller):
	allLinks = list(set([link for mpath in controller for path in mpath for link in path]))
	countOld = len(allLinks)
	allLinks.extend([link for path in multipath for link in path])
	countNew = len(list(set(allLinks)))
	return (countNew - countOld)*4 + countOld * 1

def CountNewLinks(multipath, controller):
	allLinks = list(set([link for mpath in controller for path in mpath for link in path]))
	countOld = len(allLinks)
	allLinks.extend([link for path in multipath for link in path])
	countNew = len(list(set(allLinks)))
	return (countNew - countOld)

###########################################################
# Part 1:
#   Read in the topology file
topoFile = open(sys.argv[1],"r")
nodes = []
nodeDic = {}
links = []
for line in topoFile:
	token = line.split()
	if (len(token) < 2): continue
	if token[0] == "N":
		nodes.append(int(token[1]))
		nodeDic[token[1]] = len(nodes) - 1;
	elif token[0] == "l":
		e = sorted([nodeDic[token[1]], nodeDic[token[2]]])
		links.append(e)
topoFile.close()
print "The %d links between %d nodes:" % (len(links), len(nodes))
#print "\n".join(["%d - %d" % (e[0], e[1]) for e in links]);

###########################################################
# Part 2:
#   Find k redundant paths between any two nodes
mpaths = []
for u in range(len(nodes)-1):
	for v in range(u+1,len(nodes)):
		#print "The %d best paths from %d to %d: (in terms of links)" % (k, u, v)
		weight = [1 for e in links]	# initial weight
		uv = []				# holds the multipath from u to v
		for i in range(k):
			# find the path
			nodepath = FindPath(u, v, weight)
			linkpath = N2E(nodepath)
			uv.append(linkpath)
			# update weight
			for e in linkpath: weight[e] += len(links)
			#print "%s (%s)" % ("-".join([str(n) for n in nodepath]), "".join(["%4d" % (e) for e in linkpath]))
		mpaths.append(uv)

# Print all paths
print "All paths:"
print "\n".join(", ".join("".join("%4d" % (link) for link in path) for path in mpath) for mpath in mpaths)

###########################################################
# Part 3:
#   Consolidate paths into controllers by stochastic optimization technique.
sostart = time.clock()
ctrl = map(lambda x: [], range(sigma))
ctrlList = range(sigma)
random.shuffle(mpaths)
for mpath in mpaths:
	#print "Multipath: %s" % (" and ".join(["-".join([str(node) for node in path]) for path in mpath]))
	cost = map(lambda s: ComputeCost(mpath, ctrl[s]), range(sigma))

	# put the multipath into the controller that costs least
	mincost = min(cost)
	random.shuffle(ctrlList)
	for i in ctrlList:
		if cost[i] != mincost: continue
		ctrl[i].append(mpath)
		#print "Cost vector (%s); multipath added to server %d" % (",".join([str(c) for c in cost]), i)
		break
sotime = time.clock() - sostart

###########################################################
# Part 4:
#   Print the configuration
ctrlLinkCnt = [0] * sigma
for i in range(sigma):
	print "Controller %d:" % (i)
	#print "\n".join("  "+"".join("%4d" % (link) for link in path) for mpath in ctrl[i] for path in mpath)
	print "".join("%3d" % (k) for k in sorted(set(link for mpath in ctrl[i] for path in mpath for link in path)))
	ctrlLinkCnt[i] = len(set(link for mpath in ctrl[i] for path in mpath for link in path))
	print "Totally %d links" % (ctrlLinkCnt[i])
print "Link count vector (%s)" % (",".join(str(i) for i in ctrlLinkCnt))
pathlen = [len(path) for mpath in mpaths for path in mpath]
print "Average path length %f hops, max %d, min %d" % (float(sum(pathlen))/len(pathlen), max(pathlen), min(pathlen))
print "Total links used: %d out of %d" % (len(set(link for c in ctrl for mpath in c for path in mpath for link in path)), len(links))
print "Time elapsed: %f" % (sotime)

###########################################################
# Part 5:
#   Refinement using simulated annealing
refstart = time.clock()
ctrlBest = copy.deepcopy(ctrl)
ctrlLinkCntBest = ctrlLinkCnt[:]
thermo = 100.0	# thermal energy
while thermo > 0:
	# Get a neighbouring solution from ctrl by moving one multipath away from the maxset
	maxset = max(range(sigma), key=lambda x: ctrlLinkCnt[x])
	# Pick a random multipath from the maxset and compute the cost if moved to another controller
	m = random.choice(range(len(ctrl[maxset])))
	newlinks = [CountNewLinks(ctrl[maxset][m], ctrl[i]) for i in range(sigma)]
	newlinks[maxset] = float('inf')
	# The one with least new link is the candidate (minset)
	minset = min(range(sigma), key=lambda x: newlinks[x])
	ctrlTemp = copy.deepcopy(ctrl)
	ctrlTemp[minset].append(ctrlTemp[maxset][m])
	ctrlTemp[maxset] = [ctrlTemp[maxset][i] for i in range(len(ctrlTemp[maxset])) if i != m]
	ctrlTempLinkCnt = [len(list(set([link for mpath in ctrlTemp[i] for path in mpath for link in path]))) for i in range(sigma)]
	# Move definitely if it yields a better solution, otherwise move with a probability
	delta = max(ctrlTempLinkCnt) - max(ctrlLinkCnt)
	if delta < 0 or random.random() < math.exp(-delta/thermo):
		ctrl = ctrlTemp
		ctrlLinkCnt = ctrlTempLinkCnt
	# Update best if necessary
	if max(ctrlTempLinkCnt) < max(ctrlLinkCntBest):
		ctrlBest = copy.deepcopy(ctrl)
		ctrlLinkCntBest = ctrlLinkCnt[:]
	# Update temperature
	thermo -= 0.01
reftime = time.clock() - refstart

###########################################################
# Part 6:
#   Print refined configuration
for i in range(sigma):
	print "Refined Controller %d:" % (i)
	#print "\n".join(["  "+"".join(["%4d" % (link) for link in path]) for mpath in ctrlCopy[i] for path in mpath])
	print "".join(["%3d" % (k) for k in sorted(list(set([link for mpath in ctrlBest[i] for path in mpath for link in path])))])
	print "Totally %d links" % (ctrlLinkCntBest[i])
print "Refined link count vector (%s)" % (",".join([str(i) for i in ctrlLinkCntBest]))
print "Time elapsed: %f" % (reftime)
###########################################################
# Part 7:
#   Solution using simulated annealing with random starter
sastart = time.clock()
ctrl = [[] for i in range(sigma)]
for mpath in mpaths:
	ctrl[int(random.random()*sigma)].append(mpath)
ctrlLinkCnt = [len(set(link for mpath in ctrl[i] for path in mpath for link in path)) for i in range(sigma)]
ctrlBest = copy.deepcopy(ctrl)
ctrlLinkCntBest = ctrlLinkCnt[:]
thermo = 100.0	# thermal energy
for i in range(sigma):
	print "Sim Ann Controller %d (starting point):" % (i)
	#print "\n".join(["  "+"".join(["%4d" % (link) for link in path]) for mpath in ctrlCopy[i] for path in mpath])
	print "".join(["%3d" % (k) for k in sorted(list(set([link for mpath in ctrlBest[i] for path in mpath for link in path])))])
	print "Totally %d links" % (ctrlLinkCntBest[i])
print "Sim ann link count vector (%s)" % (",".join([str(i) for i in ctrlLinkCntBest]))
while thermo > 0:
	# Get a neighbouring solution from ctrl by moving one multipath away from the maxset
	maxset = max(range(sigma), key=lambda x: ctrlLinkCnt[x])
	# Pick a random multipath from the maxset and compute the cost if moved to another controller
	m = random.choice(range(len(ctrl[maxset])))
	newlinks = [CountNewLinks(ctrl[maxset][m], ctrl[i]) for i in range(sigma)]
	newlinks[maxset] = float('inf')
	# The one with least new link is the candidate (minset)
	minset = min(range(sigma), key=lambda x: newlinks[x])
	ctrlTemp = copy.deepcopy(ctrl)
	ctrlTemp[minset].append(ctrlTemp[maxset][m])
	ctrlTemp[maxset] = [ctrlTemp[maxset][i] for i in range(len(ctrlTemp[maxset])) if i != m]
	ctrlTempLinkCnt = [len(list(set([link for mpath in ctrlTemp[i] for path in mpath for link in path]))) for i in range(sigma)]
	# Move definitely if it yields a better solution, otherwise move with a probability
	delta = max(ctrlTempLinkCnt) - max(ctrlLinkCnt)
	if delta < 0 or random.random() < math.exp(-delta/thermo):
		ctrl = ctrlTemp
		ctrlLinkCnt = ctrlTempLinkCnt
	# Update best if necessary
	if max(ctrlTempLinkCnt) < max(ctrlLinkCntBest):
		ctrlBest = copy.deepcopy(ctrl)
		ctrlLinkCntBest = ctrlLinkCnt[:]
	# Update temperature
	thermo -= 0.01
satime = time.clock() - sastart

###########################################################
# Part 8:
#   Print refined configuration
for i in range(sigma):
	print "Sim Ann Controller %d:" % (i)
	#print "\n".join(["  "+"".join(["%4d" % (link) for link in path]) for mpath in ctrlCopy[i] for path in mpath])
	print "".join(["%3d" % (k) for k in sorted(list(set([link for mpath in ctrlBest[i] for path in mpath for link in path])))])
	print "Totally %d links" % (ctrlLinkCntBest[i])
print "Sim ann link count vector (%s)" % (",".join([str(i) for i in ctrlLinkCntBest]))
print "Time elapsed: %f" % (satime)
