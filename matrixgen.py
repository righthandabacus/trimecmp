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
# Traffic matrix generator
#   Read in a set of nodes and give uniform random [0:1] load to every pair of
#   distinct nodes. The output is suitable for use in kpath.py, ecmp.py and
#   other related scripts.
#

import sys,getopt,random

###########################################################
# Global parameters
topofile = 'topology.txt'	# default topology file
fullload = False		# if true, the load is constantly 1

#random.seed(1)		# Debug use: Uncomment this line for repeatible random numbers
optlist, userlist = getopt.getopt(sys.argv[1:], 't:1h')
for opt, optarg in optlist:
	if opt == '-t':
		topofile = optarg
	elif opt == '-1':
		fullload = True
	else:
		# getopt will fault for other options
		print "Available options"
		print " -t file : The topology file in Rocketfuel format, default is topology.txt"
		print " -1 : Generate constant load of 1 for each pair of nodes"
		print " -h : This help message"
		sys.exit(1)

###########################################################
# Helper functions
def ReadNodes(f):
	"""
	Read in a Rocketfuel format topology file for the list of nodes
	"""
	topoFile = open(f, "r")	# Topology file
	nodes = []	# names of nodes
	for line in topoFile:
		token = line.split()
		if (len(token) < 2): continue
		if token[0] == "N":	# specifying a node by its name
			nodes.append(token[1])
	topoFile.close()

	return nodes

###########################################################
# Main program
#   Read in nodes, for each pair of distinct nodes, create a random value
nodes = ReadNodes(topofile)
for s in nodes:
	for t in nodes:
		if t == s: continue
		value = 1 if fullload else random.random()
		print "%s %s %f" % (s, t, value)
