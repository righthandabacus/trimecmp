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
flowfile = 'flow.txt'		# default flow specification file
digraph = False			# topology specification is a digraph

optlist, userlist = getopt.getopt(sys.argv[1:], 't:f:ds')
for opt, optarg in optlist:
	if opt == '-t':
		topofile = optarg
	elif opt == '-f':
		flowfile = optarg
	elif opt == '-d':
		digraph = True
	else:
		# getopt will fault for other options
		sys.exit(1)

###########################################################
# Helper functions
def ReadInput(f1, f3):
	"""
	Read in a Rocketfuel format topology file, and then the traffic matrix,
	then the flow specification.
	We assumed the link specification contains at least the two endpoints
	refered by the name of nodes. Optionally, the 3rd and 4th argument in
	the link specification are the length and capacity respectively. This
	optional part is not in the Rocketfuel file.
	The flow specification is in the following format:
		<source> <destination> <load> <begin> <end>
	To mean the flow from source to destination begins and ends at certain
	time (number of seconds since start) and it is of the size of certain
	load. The flow can only be routed in one path, no spliting allowed.
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

	print "Reading input file %s" % f3
	flowFile = open(f3, "r")	# Flow history file
	flows = []
	events = []
	for line in flowFile:
		token = line.split()
		if (len(token) < 5): continue
		begin = float(token[3])
		end = float(token[4])
		if end == begin: continue	# Skip this malformed flow
		heapq.heappush(events, (begin, len(flows), True))
		heapq.heappush(events, (end, len(flows), False))
		spec = (nodeDic[token[0]], nodeDic[token[1]], float(token[2]), begin, end)
		flows.append(spec)
	flowFile.close()
	return nodes, links, length, capacity, flows, events

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

###########################################################
# Step 1:
#   Read in data
nodes, links, length, capacity, flows, events = ReadInput(topofile, flowfile)

###########################################################
# Step 2:
#   Exhaust the event list to establish/remove a flow on the network

clock = 0.0
linkload = [0 for l in links]
flowpaths = {}	# Dictionary for flow:->set of links mapping
for e in range(len(links)):
	print "%f\t%d\t%f" % (clock, e, linkload[e])
while events:
	time, fid, arrival = heapq.heappop(events)
	if arrival:
		# Find a path for this flow on the tree generated by Bellman-Ford
		tree, dist = BellmanFord(flows[fid][1])
		currentnode = flows[fid][0]
		path = []
		clock = time
		while currentnode != flows[fid][1]:
			neighbour = list(set(e[1] for e in links if e[0]==currentnode))
			mindist = min(dist[i] for i in neighbour)
			minneighbour = [i for i in neighbour if dist[i] == mindist]
			nextnode = random.choice(minneighbour)
			linkid = [i for i,e in enumerate(links) if e == (currentnode, nextnode)]
			path.append(linkid[0])
			linkload[linkid[0]] += flows[fid][2]
			print "%f\t%d\t%f" % (clock, linkid[0], linkload[linkid[0]])
			currentnode = nextnode
		# Remember the path
		flowpaths[fid] = path
	else:
		# Retrieve the path for this flow
		path = flowpaths.pop(fid)
		clock = time
		# For each link in the path, decrease the load
		for l in path:
			linkload[l] -= flows[fid][2]
			print "%f\t%d\t%f" % (clock, l, linkload[l])

sys.exit(1)
