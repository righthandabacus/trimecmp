#!/usr/bin/env python

# Flow generator
#   At this moment, read in a set of nodes and produce a number of flows to
#   each pair. Later on, read the traffic matrix as well to make the flows'
#   size in time-average agree with the traffic matrix.

import sys,getopt,random,math

###########################################################
# Global parameters
topofile = 'topology.txt'	# default topology file
fullload = False
begintime = 0			# Time interval for flowgen
endtime = 100

optlist, userlist = getopt.getopt(sys.argv[1:], 't:1')
for opt, optarg in optlist:
	if opt == '-t':
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

def FindSize(mean):
	"""
	Return a mean flow size, following a uniform distribution in [0:2*mean]
	"""
	return 2*mean*random.random()

def FindArrival(previous, rate):
	"""
	Assume Poisson arrival, the next arrival is previous+interarrival time
	"""
	inter = - math.log(1-random.random()) / rate
	return previous + inter

def FindDuration(mean):
	"""
	Assume exponential holding time, return the duration
	"""
	return - math.log(1-random.random()) * mean

###########################################################
# Main program
#   Read in nodes, for each pair, create a random value
nodes = ReadNodes(topofile)
#random.seed()
for s in nodes:
	for t in nodes:
		if t == s: continue
		clock = begintime
		while clock < endtime:
			size = FindSize(0.5)
			clock = FindArrival(clock,4)
			duration = FindDuration(2)
			print "%s %s %f %f %f" % (s, t, size, clock, clock+duration)
