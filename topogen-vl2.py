#!/usr/bin/env python

# VL2 topology generator
#  There are n cores in the network, and 2n aggregation switches. They form a
#  complete bipartite graph. There are 4n edge switches, each connects to two
#  aggregation switches. The edge i connects to aggregation floor(i/n) and
#  aggregation n+(i mod n). This topology is devised in the VL2 paper.
# The format is
#    N <nodeid>
#    N <nodeid>
#    ...
#    l <nodeid> <nodeid>
#    l <nodeid> <nodeid>
#    ...

import sys,getopt

###########################################################
# Global parameters
n = 3		# Number of cores
h = 0		# Number of hosts per edge switch. Zero means do not include hosts in the graph.

optlist, userlist = getopt.getopt(sys.argv[1:], 'n:h:')
for opt, optarg in optlist:
	if opt == '-n':
		n = int(optarg)
	elif opt == '-h':
		h = int(optarg)
	else:
		# getopt will fault for other options
		sys.exit(1)

##########################################################
# Draw the core, aggregation, and edge
for c in range(n):
	print "N C%d" % c
for c in range(2*n):
	print "N A%d" % c
for c in range(4*n):
	print "N E%d" % c

##########################################################
# Connect core and aggregation
for c in range(n):
	for a in range(2*n):
		print "l C%d A%d" % (c, a)

##########################################################
# Connect edge to aggregation
for e in range(4*n):
	a1 = e / n
	a2 = n + (e % n)
	print "l E%d A%d" % (e, a1)
	print "l E%d A%d" % (e, a2)

##########################################################
# Draw the hosts and connect to edge switches
if h > 0:
	for e in range(4*n):
		for i in range(h):
			print "N E%dH%d" % (e, i)
			print "l E%dH%d E%d" % (e, i, e)
