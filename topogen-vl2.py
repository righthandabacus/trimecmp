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
# VL2 topology generator
#  Generate a k-core VL2 network as described by the following paper as `folded
#  Clos network':
#    A. Greenberg, S. Kandula, D. A. Maltz, J. R. Hamilton, C. Kim, P. Patel,
#    N. Jain, P. Lahiri and S. Sengupta, `VL2: A Scalable and Flexible Data
#    Center Network.' In Proc. SIGCOMM’09, August 17-21, 2009, Barcelona,
#    Spain.
#  The topology has k cores in the network, and 2k aggregation switches. They form a
#  complete bipartite graph. There are 4k edge switches, each connects to two
#  aggregation switches. The edge i connects to aggregation floor(i/k) and
#  aggregation k+(i mod k).
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
k = 3		# Number of cores
n = 0		# Number of hosts per edge switch. Zero means do not include hosts in the graph.

optlist, userlist = getopt.getopt(sys.argv[1:], 'k:n:h')
for opt, optarg in optlist:
	if opt == '-k':
		k = int(optarg)
	elif opt == '-n':
		n = int(optarg)
	else:
		# getopt will fault for other options
		print "Available options"
		print " -k num : Number of cores in the network"
		print " -n num : Number of hosts per edge switch. Do not include hosts in the topology if zero"
		print " -h : This help message"
		sys.exit(1)

##########################################################
# Draw the core, aggregation, and edge
for c in range(k):
	print "N C%d" % c
for c in range(2*k):
	print "N A%d" % c
for c in range(4*k):
	print "N E%d" % c

##########################################################
# Connect core and aggregation
for c in range(k):
	for a in range(2*k):
		print "l C%d A%d" % (c, a)

##########################################################
# Connect edge to aggregation
for e in range(4*k):
	a1 = e / k
	a2 = k + (e % k)
	print "l E%d A%d" % (e, a1)
	print "l E%d A%d" % (e, a2)

##########################################################
# Draw the hosts and connect to edge switches
if n > 0:
	for e in range(4*k):
		for h in range(n):
			print "N E%dH%d" % (e, h)
			print "l E%dH%d E%d" % (e, h, e)
