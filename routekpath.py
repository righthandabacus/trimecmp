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
# This program takes two input files: (1) a Rocketfuel format topology file,
# (2) the path data as computed by kpath.py, and (3) a flow file in the format
# of
#     <node> <node> <load> <begin> <end>
# where the <node> is the code correspond to the topology file and the <load>
# is a floating point number, <begin> and <end> are the time for this flow to
# start and finish.
# 
# The program place these flows into the network on one of the paths provided
# by kpath.py; if there are multiple paths available, a random one is selected.
# This program simulate the flows' arrival/departure as discrete events and
# output the change of link loads against time.
#

import getopt,sys,random,heapq,re

###########################################################
# Global parameters
topofile = 'topology.txt'	# default topology file
pathfile = 'path.txt'		# default path file
flowfile = 'flow.txt'		# default flow specification file
digraph = False			# topology specification is a digraph

optlist, userlist = getopt.getopt(sys.argv[1:], 't:p:f:dh')
for opt, optarg in optlist:
	if opt == '-t':
		topofile = optarg
	elif opt == '-p':
		pathfile = optarg
	elif opt == '-f':
		flowfile = optarg
	elif opt == '-d':
		digraph = True
	else:
		# getopt will fault for other options
		print "Available options"
		print " -t file : The topology file in Rocketfuel format, default is topology.txt"
		print " -p file : The path file, default is path.txt"
		print " -f file : The flow file, default is flow.txt"
		print " -d : Treat the topology file as digraph, i.e. each link is unidirectional"
		print " -h : This help message"
		sys.exit(1)

###########################################################
# Helper functions
def ReadInput(f1, f2, f3):
	"""
	Read in a Rocketfuel format topology file, then a path file, then the
	flow specification.  We assumed the link specification contains at
	least the two endpoints refered by the name of nodes. The flow
	specification is in the following format:
		<source> <destination> <load> <begin> <end>
	To mean the flow from source to destination begins and ends at certain
	time (number of seconds since start) and it is of the size of certain
	load. The flow can only be routed in one path, no spliting allowed.
	"""
	print "Reading input file %s" % f1
	topoFile = open(f1, "r")	# Topology file
	nodes = []	# names of nodes
	links = []	# links as an ordered pair of node IDs
	nodeDic = {}	# reverse lookup for node ID
	linkDic = {}	# reverse lookup for link ID
	for line in topoFile:
		token = line.split()
		if (len(token) < 2): continue
		if token[0] == "N":	# specifying a node by its name
			nodeDic[token[1]] = len(nodes)
			nodes.append(token[1])
		elif token[0] == "l":	# specifying a link as a connection between two nodes
			e = (nodeDic[token[1]], nodeDic[token[2]])
			linkDic[e] = len(links)
			links.append(e)
			if not digraph:
				linkDic[e[1],e[0]] = len(links)
				links.append((e[1],e[0]))
	topoFile.close()

	print "Reading input file %s" % f2
	pathFile = open(f2, "r")	# Path file
	paths = {}	# lookup table for a pair to paths
	pathregex = re.compile(r'\((.*),(.*)\) : (.*)')
	for line in pathFile:
		match = pathregex.match(line)
		if not match: continue
		s, t, nodepath = nodeDic[match.group(1)], nodeDic[match.group(2)], match.group(3).split()
		linkpath = [linkDic[nodeDic[nodepath[i]],nodeDic[nodepath[i+1]]] for i in range(len(nodepath)-1)]
		try:
			paths[s,t].append(linkpath)
		except KeyError:
			paths[s,t] = [linkpath]
	pathFile.close()

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
	return nodes, links, paths, flows, events

###########################################################
# Step 1:
#   Read in data
nodes, links, paths, flows, events = ReadInput(topofile, pathfile, flowfile)

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
		# Find a path for this flow from the known paths
		path = random.choice(paths[flows[fid][0],flows[fid][1]])
		# Remember the path, raise load, print updated link load
		flowpaths[fid] = path
		clock = time
		for l in path:
			linkload[l] += flows[fid][2]
			print "%f\t%d\t%f" % (clock, l, linkload[l])
	else:
		# Retrieve the path for this flow
		path = flowpaths.pop(fid)
		clock = time
		# For each link in the path, decrease the load
		for l in path:
			linkload[l] -= flows[fid][2]
			print "%f\t%d\t%f" % (clock, l, linkload[l])

sys.exit(1)
