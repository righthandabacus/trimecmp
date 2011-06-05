#!/usr/bin/env python

# Traffic matrix generator
#   Read in a set of nodes and give uniform random [0:1] load to every pair

import sys,getopt,random

###########################################################
# Global parameters
topofile = 'topology.txt'	# default topology file
fullload = False

optlist, userlist = getopt.getopt(sys.argv[1:], 'f:1')
for opt, optarg in optlist:
	if opt == '-f':
		topofile = optarg
	elif opt == '-1':
		fullload = True
	else:
		# getopt will fault for other options
		sys.exit(1)

###########################################################
# Helper functions
def ReadNodes(f):
	"""
	Read in a Rocketfuel format topology file for the list of nodes
	"""
	topoFile = open(f, "r")	# Topology file
	nodes = []
	for line in topoFile:
		token = line.split()
		if (len(token) < 2): continue
		if token[0] == "N":	# specifying a node by its name
			nodes.append(token[1])
	topoFile.close()

	return nodes

###########################################################
# Main program
#   Read in nodes, for each pair, create a random value
nodes = ReadNodes(topofile)
#random.seed()
for s in nodes:
	for t in nodes:
		if t == s: continue
		value = 1 if fullload else random.random()
		print "%s %s %f" % (s, t, value)
