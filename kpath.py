#!/usr/bin/env python
#
# Copyright (c) 2011 Polytechnic Institute of New York University
# Author: Adrian Sai-wah Tam <adrian.sw.tam@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED ''AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of New York University.

#
# This program takes two input files: (1) a Rocketfuel format topology file and
# (2) traffic matrix file with the format of
#     <node> <node> <load>
# where the <node> is the code correspond to the topology file and the <load>
# is a floating point number.
# 
# The program finds at most k paths between every pair of nodes mentioned in
# the traffic matrix, which k is a parameter to this program. The paths are
# found such that it minimizes the resultant network cost when each of the k
# paths carries 1/k of the load for the pair of node.
#

import getopt,sys,random,heapq

###########################################################
# Global parameters
topofile = 'topology.txt'	# default topology file
matrixfile = 'matrix.txt'	# default matrix file
k = 4				# maximum number of paths to find for a pair
shortest = False		# use only shortest path
digraph = False			# topology specification is a digraph
overshoot = 25.0		# percentage of length overshoot (w.r.t. shortest path) tolerated, effective only if shortest==False
maxpaths = 100			# maximum number of paths to return from the FindPaths function

#random.seed(1)		# Debug use: Uncomment this line for repeatible random numbers
optlist, userlist = getopt.getopt(sys.argv[1:], 't:m:k:dso:h')
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
		if n == 0: shortest = True
	else:
		# getopt will fault for other options
		print "Available options"
		print " -t file : The topology file in Rocketfuel format, default is topology.txt"
		print " -m file : The traffic matrix file, default is matrix.txt"
		print " -k num : Max number of paths to find for a pair"
		print " -d : Treat the topology file as digraph, i.e. each link is unidirectional"
		print " -s : Find only shortest path. The -o option is ignored when this is present."
		print " -o percent : Percentage of length overshoot w.r.t. shortest path is tolerated."
		print "              This option is honoured only if -s option is not present. Default 25."
		print " -h : This help message"
		sys.exit(1)

###########################################################
# Helper functions
def ReadInput(f1, f2):
	"""
	Read in a Rocketfuel format topology file, then a traffic matrix file.
	By default, we assume all link distances are 1 and capacities are 1 as
	well unless specified in the topology file. The link specification
	contains at least the two endpoints refered by the name of nodes.
	Optionally, the 3rd and 4th argument in the link specification are the
	length and capacity respectively. This optional part is not in the
	Rocketfuel's standard.
	"""
	print "Reading input file %s" % f1
	topoFile = open(f1, "r")	# Topology file
	nodes = []	# names of nodes
	links = []	# links as an ordered pair of node IDs
	length = []	# lengths of links
	capacity = []	# link capacities
	nodeDic = {}	# reverse lookup for node ID
	for line in topoFile:
		token = line.split()
		if (len(token) < 2): continue
		if token[0] == "N":	# specifying a node by its name
			nodeDic[token[1]] = len(nodes)
			nodes.append(token[1])
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
	"""
	Copied from http://wiki.python.org/moin/PythonDecoratorLibrary
	Decorator that caches a function's return value each time it is called.
	If called later with the same arguments, the cached value is returned,
	and not re-evaluated.
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
	c = max(linkload[l]/capacity[l] for l in pathlinks)
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
		if current in visited: return []
		# No loop is found yet, proceed one hop
		visited.add(current)
		if current in sidenodes:
			# proceed along a sidetrack edge
			edge = [e for e in sidetracks if links[e][0] == current]
		else:
			# proceed according to shortest path tree
			edge = [i for i,e in enumerate(links) if e == (current,tree[current])]
		current = links[edge[0]][1]
		path.append(edge[0])
	# Destination reached. Return the path
	return path

@memoized
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
	paths = [(dist[s],[])]
	leaves = [paths[0]]

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
			# no two sidetracked edges are parallel to each other
			if links[edge][0] in sidenode: continue
			# avoid too lengthy paths w.r.t. the shortest path
			currentside = leafside[:] + [edge]
			if sum(delta[i] for i in currentside) > dist[s]*(overshoot/100.0): continue
			# avoid duplicated set of sidetrack edges: sort them in order
			currentside.sort()
			if [sides for d, sides in paths if sides == currentside]: continue
			# Find the path, return empty list if a loop is found
			currentpath = Sidetrack2Path(tree, currentside, s, t)
			# Add the path to repository if it is loop-free and contains the new sidetracked edge
			if set(currentside) <= set(currentpath):
				newpath = (leafdist + delta[edge], currentside)
				heapq.heappush(paths, newpath)
				heapq.heappush(leaves, newpath)
		# quit if we exhausted all the paths (to avoid poping an empty heap)
		# or if we enumerated too many paths
		if len(leaves)==0 or len(paths) >= maxpaths: break
	# convert paths from sidetrack-based notation to edge-based notation
	edgepaths = [Sidetrack2Path(tree, p[1], s, t) for p in paths]
	return edgepaths

###########################################################
# Step 1:
#   Read in data
nodes, links, length, capacity, traffic = ReadInput(topofile, matrixfile)

###########################################################
# Step 2:
#   Path-finding for each pair in the traffic matrix
#   For the traffic between (s,t), it first find a set of short paths to t
#   using the Eppstein's algorithm (hence not necessarily all paths are
#   shortest paths). Then we put the full load at node s, and
#   recursively split this load evenly to each of the next hop toward t.

linkload = [0 for l in links]
pairs = traffic.keys()
allpaths = dict()
for i in range(k):
	random.shuffle(pairs)
	for pair in pairs:
		# Find a set of paths using Eppstein's algorithm
		try:
			if len(allpaths[pair]) < i: continue
		except KeyError:
			allpaths[pair] = []
		paths = [p for p in FindKPaths(pair[0], pair[1]) if p not in allpaths[pair]]
		if len(paths) == 0: continue
		# Amongst these paths, find the best one:
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
			# first path: unconditionally add the path and increase load
			allpaths[pair].append(bestpath)
			for l in bestpath:
				linkload[l] += traffic[pair];
			pathnode = [nodes[links[bestpath[0]][0]]] + [nodes[links[l][1]] for l in bestpath]
			print "Path (%s,%s) : %s" % (nodes[pair[0]], nodes[pair[1]], " ".join(pathnode))
		else:
			# subsequent paths: compare load between with vs without the bestpath
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
			if newmax <= oldmax:
				# add this path if we do not increase the maximum load
				linkload = newload
				allpaths[pair].append(bestpath)
				pathnode = [nodes[links[bestpath[0]][0]]] + [nodes[links[l][1]] for l in bestpath]
				print "Path (%s,%s) : %s" % (nodes[pair[0]], nodes[pair[1]], " ".join(pathnode))

###########################################################
# Step 3:
#   Fine-tuning the result.
#   Try to recursively find the hottest link(s) and get the list of traffic
#   that traverse them. Then try to find an alternative path for these traffic
#   such that we can offload part of them from these hottest links. Stop if no
#   more offloading is possible.
print "Original link loads"
print "\n".join("(%s,%s) = %r" % (nodes[e[0]], nodes[e[1]],linkload[i]) for i,e in sorted(enumerate(links),key=lambda x:linkload[x[0]]))
improved = True
while improved:
	# Find the paths that pass through bottleneck links
	maxload = max(linkload)
	hotlinks = [i for i,l in enumerate(linkload) if l==maxload]
	heavypaths = [p for pair in traffic.keys() for p in allpaths[pair] if set(p) & set(hotlinks)]
	improved = False
	# Find an alternative for each such path
	for path in heavypaths:
		# alternative path is selected from the output of FindKPaths(s,t)
		s,t = links[path[0]][0], links[path[-1]][1]
		paths = FindKPaths(s,t)
		goodpaths = []
		# the alternative path must satisfy these criteria:
		# (1) not traverse any hottest links,
		# (2) not already used for this pair,
		# (3) use of this alternative path does not create a new hottest link
		for p in paths:
			if set(p) & set(hotlinks): continue
			if p in allpaths[s,t]: continue
			headroom = maxload - max(linkload[l] for l in p)
			if len(allpaths[s,t]) < k:
				if headroom <= traffic[s,t]/(len(allpaths[s,t])+1): continue
			else:
				if headroom <= traffic[s,t]/k: continue
			goodpaths.append(p)
		if len(goodpaths)==0: continue
		# Alternative path available: Pick any one and update link costs
		newpath = random.choice(goodpaths)
		if len(allpaths[s,t]) < k:
			# add this path as we did not have k paths for this pair yet
			for l in newpath:
				linkload[l] += traffic[s,t]/(len(allpaths[s,t])+1)
			for l in (ll for p in allpaths[s,t] for ll in p):
				linkload[l] += traffic[s,t]/(len(allpaths[s,t])+1) - traffic[s,t]/len(allpaths[s,t])
			pathnode = [nodes[s]] + [nodes[links[l][1]] for l in newpath]
			print "Added (%s,%s) : %s" % (nodes[s], nodes[t], " ".join(pathnode))
		else:
			# replace path to keep only k paths for this pair
			for l in newpath:
				linkload[l] += traffic[s,t]/len(allpaths[s,t])
			for l in path:
				linkload[l] -= traffic[s,t]/len(allpaths[s,t])
			allpaths[s,t].remove(path)
			pathnode = [nodes[s]] + [nodes[links[l][1]] for l in path]
			print "Removed (%s,%s) : %s" % (nodes[s], nodes[t], " ".join(pathnode))
			pathnode = [nodes[s]] + [nodes[links[l][1]] for l in newpath]
			print "Added (%s,%s) : %s" % (nodes[s], nodes[t], " ".join(pathnode))
		allpaths[s,t].append(newpath)
		improved = True


###########################################################
# Step 3:
#   Output result to console
print "All the paths:"
for (pair,paths) in allpaths.iteritems():
	for p in paths:
		pathnode = [nodes[links[p[0]][0]]] + [nodes[links[l][1]] for l in p]
		print "(%s,%s) : %s" % (nodes[pair[0]], nodes[pair[1]], " ".join(pathnode))
print "Link loads"
print "\n".join("(%s,%s) = %r" % (nodes[e[0]], nodes[e[1]],linkload[i]) for i,e in sorted(enumerate(links),key=lambda x:linkload[x[0]]))

sys.exit(1)
