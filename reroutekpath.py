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

import getopt,sys,random,heapq,re

###########################################################
# Global parameters
topofile = 'topology.txt'	# default topology file
pathfile = 'path.txt'		# default path file
flowfile = 'flow.txt'		# default flow specification file
digraph = False			# topology specification is a digraph

optlist, userlist = getopt.getopt(sys.argv[1:], 't:p:f:d')
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
		sys.exit(1)

###########################################################
# Helper functions
def ReadInput(f1, f2, f3):
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
	nodes = []	# names of nodes
	links = []	# links as an ordered pair of node IDs
	nodeDic = {}	# reverse lookup for node ID
	linkDic = {}	# reverse lookup for link ID
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
			linkDic[e] = len(links)
			links.append(e)
			length.append(1 if len(token) < 4 else token[3])
			capacity.append(1 if len(token) < 5 else token[4])
			if not digraph:
				linkDic[e[1],e[0]] = len(links)
				links.append((e[1],e[0]))
				length.append(length[-1])
				capacity.append(capacity[-1])
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
	return nodes, links, length, capacity, paths, flows, events

###########################################################
# Step 1:
#   Read in data
nodes, links, length, capacity, paths, flows, events = ReadInput(topofile, pathfile, flowfile)

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
		# Find a path for this flow
		path = random.choice(paths[flows[fid][0],flows[fid][1]])
		# Remember the path, raise load
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
