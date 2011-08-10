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
# Flattened Butterfly topology generator
#   Generate a k-ary n-flat network with concentration c. See the following for
#   more information on flattened butterfly topology:
#     D. Abts, M. R. Marty, P. M. Wells, P. Klausler and H. Liu, `Energy
#     Proportional Datacenter Networks.' In Proc. ISCA’10, pp.338-347, June
#     19-23, 2010, Saint-Malo, France.
#     J. Kim, W. J. Dally, and D. Abts, `Flattened butterfly: a cost-efficient
#     topology for high-radix networks.' In Proc. ISCA'07, pp.126-137, June
#     9-11, 2007, San Diego, CA.
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
k = 8		# Number of switches in a dimension
n = 2		# Number of dimensions
c = 0		# Number of hosts per switch. Zero means do not include hosts in the graph.

optlist, userlist = getopt.getopt(sys.argv[1:], 'k:n:c:h')
for opt, optarg in optlist:
	if opt == '-k':
		k = int(optarg)
	elif opt == '-n':
		n = int(optarg)
	elif opt == '-c':
		c = int(optarg)
	else:
		# getopt will fault for other options
		print "Available options"
		print " -k num : Number of switches in a dimension"
		print " -n num : Number of dimensions"
		print " -c num : Number of hosts per switch. Do not include hosts in the topology if zero"
		print " -h : This help message"
		sys.exit(1)

##########################################################
# Helper function: Recursive functions to make nodes and links respectively
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
