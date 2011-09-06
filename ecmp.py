#!/usr/bin/python -u
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
# The program forward the traffic between any two nodes mentioned in the
# traffic matrix in the "equal-cost multipath" forwarding manner, and account
# the load on each link.
#

import getopt,sys,random,heapq

###########################################################
# Global parameters
topofile = 'topology.txt'	# default topology file
matrixfile = 'matrix.txt'	# default matrix file
digraph = False			# topology specification is a digraph

optlist, userlist = getopt.getopt(sys.argv[1:], 't:m:dh')
for opt, optarg in optlist:
	if opt == '-t':
		topofile = optarg
	elif opt == '-m':
		matrixfile = optarg
	elif opt == '-d':
		digraph = True
	else:
		# getopt will fault for other options
		print "Available options"
		print " -t file : The topology file in Rocketfuel format, default is topology.txt"
		print " -m file : The traffic matrix file, default is matrix.txt"
		print " -d : Treat the topology file as digraph, i.e. each link is unidirectional"
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
		nochange = True
		for j,(u,v) in enumerate(links):
			if d[u] > d[v] + length[j]:
				nochange = False
				d[u] = d[v] + length[j] 
				n[u] = v
		if nochange: break
	return n,d

###########################################################
# Step 1:
#   Read in data
nodes, links, length, capacity, traffic = ReadInput(topofile, matrixfile)

###########################################################
# Step 2:
#   Path-finding for each pair in the traffic matrix
#   For the traffic between (s,t), it first find the shortest-path tree to t
#   using Bellman-Ford algorithm. Then we put the full load at node s, and
#   recursively split this load evenly to each of the next hop toward t.

linkload = [0 for l in links]
pairs = traffic.keys()
random.shuffle(pairs)
for pair in pairs:
	print "Filling " + str(pair)
	# Find shortest paths tree by Bellman-Ford
	#   dist[n] = the distance to destination from node n
	#   load[n] = traffic arriving node n
	tree, dist = BellmanFord(pair[1])
	load = [0 for i in nodes]
	load[pair[0]] = traffic[pair]
	# Breath-first search from the source node until the destination node
	#   visited: The visited nodes, initialized to be t as we can stop once
	#            we reach t
	#   tovisit: The nodes to be visited, in a priority queue with the
	#            priority as the distance to t. We deplete this priority
	#            queue in descending order of distance to t. Initialized to
	#            hold node s only.
	visited = set([pair[1]])
	tovisit = [(-dist[pair[0]], pair[0])]
	while len(tovisit):
		# Pick the farthest node to t and look for all its
		# shortest-path neighbours
		d, n = heapq.heappop(tovisit)
		if n in visited: continue
		neighbour = list(set(e[1] for e in links if e[0]==n))
		mindist = min(dist[i] for i in neighbour)
		minneighbour = [i for i in neighbour if dist[i]==mindist]
		# Distribute load evenly to the neighbours
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
print "\n".join("(%s,%s) = %r" % (nodes[e[0]], nodes[e[1]],linkload[i]) for i,e in sorted(enumerate(links),key=lambda x:linkload[x[0]]))

sys.exit(1)

##################################
