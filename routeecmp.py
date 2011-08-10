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
# (2) a flow file in the format of 
#     <node> <node> <load> <begin> <end>
# where the <node> is the code correspond to the topology file and the <load>
# is a floating point number, <begin> and <end> are the time for this flow to
# start and finish.
# 
# The program place these flows into the network using flow-based ECMP, i.e.
# each flow will only take one path, but the path is selected at random amongst
# all equal-cost shortest paths. This program simulate the flows'
# arrival/departure as discrete events and output the change of link loads
# against time.
#

import getopt,sys,random,heapq

###########################################################
# Global parameters
topofile = 'topology.txt'	# default topology file
flowfile = 'flow.txt'		# default flow specification file
digraph = False			# topology specification is a digraph

#random.seed(1)		# Debug use: Uncomment this line for repeatible random numbers
optlist, userlist = getopt.getopt(sys.argv[1:], 't:f:dsh')
for opt, optarg in optlist:
	if opt == '-t':
		topofile = optarg
	elif opt == '-f':
		flowfile = optarg
	elif opt == '-d':
		digraph = True
	else:
		# getopt will fault for other options
		print "Available options"
		print " -t file : The topology file in Rocketfuel format, default is topology.txt"
		print " -f file : The flow file, default is flow.txt"
		print " -d : Treat the topology file as digraph, i.e. each link is unidirectional"
		print " -h : This help message"
		sys.exit(1)

###########################################################
# Helper functions
def ReadInput(f1, f3):
	"""
	Read in a Rocketfuel format topology file, and then the flow specification.
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
	nodes = []	# names of nodes
	links = []	# links as an ordered pair of node IDs
	length = []	# lengths of links
	capacity = []	# link capacities
	nodeDic = {}	# reverse lookup for node ID
	for line in topoFile:
		token = line.split()
		if (len(token) < 2): continue
		if token[0] == "N":	# specifying a node by its name
			nodeDic[token[1]] = len(nodes) - 1
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

	print "Reading input file %s" % f3
	flowFile = open(f3, "r")	# Flow history file
	flows = []	# flow specs (src,dst,size,begin,end)
	events = []	# flow arrival/departure events (time, flowID, isArrival)
	for line in flowFile:
		token = line.split()
		if (len(token) != 5): continue	# Not a flow specification
		begin, end = float(token[3]), float(token[4])
		if end == begin: continue	# Skip this malformed flow
		heapq.heappush(events, (begin, len(flows), True))
		heapq.heappush(events, (end, len(flows), False))
		spec = (nodeDic[token[0]], nodeDic[token[1]], float(token[2]), begin, end)
		flows.append(spec)
	flowFile.close()
	return nodes, links, length, capacity, flows, events

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

###########################################################
# Step 1:
#   Read in data
nodes, links, length, capacity, flows, events = ReadInput(topofile, flowfile)

###########################################################
# Step 2:
#   Exhaust the event list to establish/remove a flow on the network, and in
#   the meantime, print the link load if there is any change

clock = 0.0
linkload = [0 for l in links]
flowpaths = {}	# Dictionary for flow:->set_of_links mapping
for e,l in enumerate(linkload)
	# print initial link load
	print "%f\t%d\t%f" % (clock, e, l)
while events:
	time, fid, arrival = heapq.heappop(events)
	if arrival:
		# Find a path for this flow on the tree generated by Bellman-Ford
		tree, dist = BellmanFord(flows[fid][1])
		currentnode = flows[fid][0]
		path = []
		clock = time
		while currentnode != flows[fid][1]:
			# Find a random next hop on the shortest paths
			neighbour = list(set(e[1] for e in links if e[0]==currentnode))
			mindist = min(dist[i] for i in neighbour)
			minneighbour = [i for i in neighbour if dist[i] == mindist]
			nextnode = random.choice(minneighbour)
			# Then look up the link, and distribute traffic to it
			linkid = [i for i,e in enumerate(links) if e == (currentnode, nextnode)]
			path.append(linkid[0])
			linkload[linkid[0]] += flows[fid][2]
			# Print the upated link load
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
