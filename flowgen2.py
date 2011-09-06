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
#   Read in a set of nodes and a traffic matrix to produce a number of flows
#   according to the traffic matrix in the time interval [0:100s]. The arrival
#   is Poission and the lifetime is exponential for each pair. The size of
#   flow, i.e. bandwidth consumption, is uniformly distributed in [0:1]
#

import sys,getopt,random,math

###########################################################
# Global parameters
matrixfile = 'matrix.txt'	# default traffic matrix file
begintime = 0			# Time interval for flowgen
endtime = 100
meansize = 0.5			# Mean flow size
meanduration = 2		# Mean duration of a flow
arrivalrate = 4			# Arrival rate for a pair of nodes

#random.seed(1)		# Debug use: Uncomment this line for repeatible random numbers
optlist, userlist = getopt.getopt(sys.argv[1:], 's:m:a:d:h')
for opt, optarg in optlist:
	if opt == '-s':
		meansize = float(optarg)
	elif opt == '-m':
		matrixfile = optarg
	elif opt == '-a':
		arrivalrate = float(optarg)
	elif opt == '-d':
		meanduration = float(optarg)
	else:
		# getopt will fault for other options
		print "Available options"
		print " -m file: Traffic matrix file, default is matrix.txt"
		print " -s size : Mean flow size, default 0.5"
		print " -a rate: Arrival rate of flows for a pair of nodes, default 4 per second"
		print " -d time: Mean duration of a flow, default 2 seconds"
		print " -h : This help message"
		sys.exit(1)

###########################################################
# Helper functions
def ReadInput(f):
	"""
	Read in a traffic matrix
	"""
	trafficFile = open(f, "r")	# Traffic matrix file
	traffic = {}
	for line in trafficFile:
		token = line.split()
		if (len(token) < 3): continue
		traffic[token[0], token[1]] = meanduration/float(token[2])
	trafficFile.close()
	return traffic

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
#   Read in traffic matrix, create a series of flows
rate = ReadInput(matrixfile)
for s,t in rate.keys():
	clock = begintime
	while clock < endtime:
		size = FindSize(meansize)
		clock = FindArrival(clock,arrivalrate)
		duration = FindDuration(rate[s,t])
		print "%s %s %f %f %f" % (s, t, size, clock, clock+duration)
