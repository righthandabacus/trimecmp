#!/usr/bin/env python
# This program takes two input files: (1) a Rocketfuel format topology file and
# (2) traffic matrix file with the format of
#     <node> <node> <load>
# where the <node> is the code correspond to the topology file and the <load>
# is a floating point number less than one. The link capacity is assume to be
# one for all links.
# 
# The program finds all the shortest paths between every pair of nodes
# mentioned in the traffic matrix and distribute the load evenly to them.
#

import getopt,sys,random,heapq

###########################################################
# Global parameters
topofile = 'topology.txt'	# default topology file
matrixfile = 'matrix.txt'	# default matrix file
digraph = False

optlist, userlist = getopt.getopt(sys.argv[1:], 't:m:d')
for opt, optarg in optlist:
	if opt == '-t':
		topofile = optarg
	elif opt == '-m':
		matrixfile = optarg
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
	length = []
	capacity = []
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
for pair in pairs:
	# Find shortest paths tree by Bellman-Ford
	#   dist = the distance to destination at any node
	#   load = traffic arriving any node
	tree, dist = BellmanFord(pair[1])
	load = [0 for i in nodes]
	load[pair[0]] = traffic[pair]
	# Breath-first search from the source node until the destination node
	visited = set()
	visited.add(pair[1])
	tovisit = []
	heapq.heappush(tovisit,(-dist[pair[0]],pair[0]))
	while len(tovisit):
		# Pick the farthest node and look for all its min-distance neighbours
		d, n = heapq.heappop(tovisit)
		if n in visited: continue
		neighbour = list(set(e[1] for e in links if e[0]==n))
		mindist = min(dist[i] for i in neighbour)
		minneighbour = [i for i in neighbour if dist[i]==mindist]
		# Distribute load to the neighbours
		visited.add(n)
		for i in minneighbour:
			load[i] += load[n]/len(minneighbour)
			linkid = links.index((n,i))
			linkload[linkid] += load[n]/len(minneighbour)
			heapq.heappush(tovisit,(-dist[i],i))

###########################################################
# Step 3:
#   Output result to console
print "Link loads"
print "\n".join([str(["(%s,%s)" % (nodes[e[0]], nodes[e[1]]),linkload[i]]) for i,e in enumerate(links)])

sys.exit(1)

##################################
