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
# Fat-tree topology generator
#   It generates a 3-level fat tree with each node of 2K degrees, i.e.
#   XGFT(3;k,k,2k;1,k,k) if hosts are generated, or XGFT(2;k,2k;k,k) if hosts
#   are not generated. See the following for the XGFT() notation:
#     S. R. Ohring, M. Ibel, S. K. Das, and M. J. Kumar, "On Generalized Fat
#     Trees," in Proc. 9th International Parallel Processing Symposium, Santa
#     Barbara, CA, 1995, pp. 37-44.
# The output is in Rocketfuel format, i.e.
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
n = False	# Include host nodes in the fat tree topology

optlist, userlist = getopt.getopt(sys.argv[1:], 'k:nh')
for opt, optarg in optlist:
	if opt == '-k':
		k = int(optarg)
	elif opt == '-n':
		h = True
	else:
		# getopt will fault for other options
		print "Available options"
		print " -k num : Degree of fat tree, i.e. number of edge switch per subtree"
		print " -n : Include hosts in the topology"
		print " -h : This help message"
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
if n:
	for subtree in range(2*k):
		for edge in range(k):
			for port in range(k):
				print "N S%dE%dH%d" % (subtree, edge, port)
				print "l S%dE%dH%d S%dE%d" % (subtree, edge, port, subtree, edge)
