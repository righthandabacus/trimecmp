#!/usr/bin/env python
# This program takes three input files: (1) a Rocketfuel format topology file,
# (2) the path data as computed by kpath.py, and (3) traffic matrix file with
# the format of
#     <node> <node> <load>
# where the <node> is the code correspond to the topology file and the <load>
# is a floating point number less than one.
# 
# This program distribute the traffic according to the traffic matrix to the
# paths as provided by kpath.py. The distribution is even across all the
# provided paths for the corresponding source-destination pair. Then this
# program output the load of each link when all the traffic are applied.
#

import getopt,sys,re

###########################################################
# Global parameters
topofile = 'topology.txt'	# default topology file
pathfile = 'path.txt'		# default path file
matrixfile = 'matrix.txt'	# default matrix file
digraph = False			# topology specification is a digraph

optlist, userlist = getopt.getopt(sys.argv[1:], 't:p:m:d')
for opt, optarg in optlist:
	if opt == '-t':
		topofile = optarg
	elif opt == '-p':
		pathfile = optarg
	elif opt == '-m':
		matrixfile = optarg
	elif opt == '-d':
		digraph = True
	else:
		# getopt will fault for other options
		sys.exit(1)

###########################################################
# Helper functions
def ReadInput(f1, f2, f3):
	"""
	Read in a Rocketfuel format topology file, then a path file, then a
	traffic matrix file.
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
		s, t, nodepath = match.group(1), match.group(2), match.group(3).split()
		linkpath = [linkDic[nodeDic[nodepath[i]],nodeDic[nodepath[i+1]]] for i in range(len(nodepath)-1)]
		try:
			paths[nodeDic[s],nodeDic[t]].append(linkpath)
		except KeyError:
			paths[nodeDic[s],nodeDic[t]] = [linkpath]
	pathFile.close()

	print "Reading input file %s" % f3
	trafficFile = open(f3, "r")	# Traffic matrix file
	traffic = {}
	for line in trafficFile:
		token = line.split()
		if (len(token) < 3): continue
		traffic[nodeDic[token[0]], nodeDic[token[1]]] = float(token[2])
	trafficFile.close()
	return nodes, links, paths, traffic

###########################################################
# Step 1:
#   Read in data
nodes, links, paths, traffic = ReadInput(topofile, pathfile, matrixfile)

###########################################################
# Step 2:
#   Distribute traffic

linkload = [0 for l in links]
for pair in traffic.keys():
	# For this traffic, distribute to all the corresponding paths evenly
	numpath = len(paths[pair])
	for path in paths[pair]:
		for link in path:
			linkload[link] += traffic[pair]/numpath

###########################################################
# Step 3:
#   Output result to console
print "Link loads"
print "\n".join(str(["(%s,%s)" % (nodes[e[0]], nodes[e[1]]),linkload[i]]) for i,e in sorted(enumerate(links),key=lambda x:linkload[x[0]]))

sys.exit(1)
