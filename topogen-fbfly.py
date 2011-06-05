#!/usr/bin/env python

# Flattened Butterfly topology generator
#   Generate a k-ary n-flat network with concentration c
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
k = 8		# Number of switches in a dimension
n = 2		# Number of dimensions
c = 0		# Number of hosts per switch. Zero means do not include hosts in the graph.

optlist, userlist = getopt.getopt(sys.argv[1:], 'k:n:c:')
for opt, optarg in optlist:
	if opt == '-k':
		k = int(optarg)
	elif opt == '-n':
		n = int(optarg)
	elif opt == '-c':
		c = int(optarg)
	else:
		# getopt will fault for other options
		sys.exit(1)

##########################################################
# Helper function (recursive functions)
def MakeNodes(d):
	for i in range(k):
		coord[d-1] = i
		if (d == 1):
			code = "_".join("%d" % j for j in reversed(coord))
			print "N S%s" % code
		else:
			MakeNodes(d-1)

def ConnectNodes(d):
	for i in range(k):
		coord[d-1] = i
		if (d == 1):
			for j in range(len(coord)):
				for m in range(k):
					if coord[j] >= m: continue
					ccopy = coord[:]
					ccopy[j] = m
					code1 = "_".join("%d" % x for x in reversed(coord))
					code2 = "_".join("%d" % x for x in reversed(ccopy))
					print "l S%s S%s" % (code1, code2)
		else:
			ConnectNodes(d-1)

##########################################################
# Prepare coordinate system
coord = [0 for i in range(n-1)]
MakeNodes(n-1)

##########################################################
# Connect switches
coord = [0 for i in range(n-1)]
ConnectNodes(n-1)


