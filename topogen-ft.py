#!/usr/bin/env python

# Fat-tree topology generator
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
k = 3		# Degree of fat tree, i.e. number of edge switch per subtree
h = False	# Include host nodes in the fat tree topology

optlist, userlist = getopt.getopt(sys.argv[1:], 'k:h')
for opt, optarg in optlist:
	if opt == '-k':
		k = int(optarg)
	elif opt == '-h':
		h = True
	else:
		# getopt will fault for other options
		sys.exit(1)

##########################################################
# Draw the core nodes
for c in range(k*k):
	print "N C%d" % c

##########################################################
# Draw the aggregation and edge nodes
for subtree in range(2*k):
	for agg in range(k):
		print "N S%dA%d" % (subtree, agg)
		print "N S%dE%d" % (subtree, agg)

##########################################################
# Connect core to aggregation
for subtree in range(2*k):
	c = 0
	for agg in range(k):
		for port in range(k):
			print "l S%dA%d C%d" % (subtree, agg, agg*k+port)
			c = c + 1

##########################################################
# Connect aggregation to edge
for subtree in range(2*k):
	for edge in range(k):
		for port in range(k):
			print "l S%dE%d S%dA%d" % (subtree, edge, subtree, port)

##########################################################
# Draw the hosts and connect to edge switches
if h:
	for subtree in range(2*k):
		for edge in range(k):
			for port in range(k):
				print "N S%dE%dH%d" % (subtree, edge, port)
				print "l S%dE%dH%d S%dE%d" % (subtree, edge, port, subtree, edge)
