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
# Flow generator
#   Read in a set of nodes and produce a number of flows to every pair of
#   distinct nodes in the time interval [0:100s]. The arrival is Poission and
#   the lifetime is exponential for each pair. The size of flow, i.e. bandwidth
#   consumption, is uniformly distributed in [0:1]
#

import sys,getopt,random,math

###########################################################
# Global parameters
topofile = 'topology.txt'	# default topology file
begintime = 0			# Time interval for flowgen
endtime = 100
meansize = 0.5			# Mean flow size
arrivalrate = 4			# Arrival rate for a pair of nodes
meanduration = 2		# Mean duration of a flow

#random.seed(1)		# Debug use: Uncomment this line for repeatible random numbers
optlist, userlist = getopt.getopt(sys.argv[1:], 't:s:a:d:h')
for opt, optarg in optlist:
	if opt == '-t':
		topofile = optarg
	if opt == '-s':
		meansize = float(optarg)
	if opt == '-a':
		arrivalrate = float(optarg)
	if opt == '-d':
		meanduration = float(optarg)
	else:
		# getopt will fault for other options
		print "Available options"
		print " -t file : The topology file in Rocketfuel format, default is topology.txt"
		print " -s size : Mean flow size, default 0.5"
		print " -a rate: Arrival rate of flows for a pair of nodes, default 4 per second"
		print " -d time: Mean duration of a flow, default 2 seconds"
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
#   Read in nodes, for each pair of distinct nodes, create a series of flows
nodes = ReadNodes(topofile)
for s in nodes:
	for t in nodes:
		if t == s: continue
		clock = begintime
		while clock < endtime:
			size = FindSize(meansize)
			clock = FindArrival(clock,arrivalrate)
			duration = FindDuration(meanduration)
			print "%s %s %f %f %f" % (s, t, size, clock, clock+duration)
