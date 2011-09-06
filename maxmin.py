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
# This program takes the output of routeecmp.py as input, which it is in the format of
#    <time> <linkid> <load>
# This program analyze the time-ordered link load data and outputs the maximum and minimum link load at any time.
#

import getopt,sys

###########################################################
# Global parameters
routefile = 'route.txt'		# default input file
maxfile = 'max.txt'
minfile = 'min.txt'

#random.seed(1)		# Debug use: Uncomment this line for repeatible random numbers
optlist, userlist = getopt.getopt(sys.argv[1:], 'i:M:m:h')
for opt, optarg in optlist:
	if opt == '-i':
		routefile = optarg
	elif opt == '-M':
		maxfile = optarg
	elif opt == '-m':
		minfile = optarg
	else:
		# getopt will fault for other options
		print "Available options"
		print " -i file : Input file, default is route.txt"
		print " -M file : Output of maximum link load, default is max.txt"
		print " -m file : Output of minimum link load, default is min.txt"
		print " -h : This help message"
		sys.exit(1)

###########################################################
infile = open(routefile, "r")
outmax = open(maxfile, "w")
outmin = open(minfile, "w")
loads = []
oldmax = None
oldmin = None
clock = 0
for line in infile:
	token = line.split()
	if len(token) != 3: continue
	time, link, load = float(token[0]), int(token[1]), float(token[2])
	if len(loads) == link:
		loads.append(load)
	else:
		loads[link] = load
	if clock < time:
		clock = time
		maxload = max(loads)
		minload = min(loads)
		if oldmax != maxload:
			#if oldmax != None:
			#	print >>outmax, "%f %f" % (time,oldmax)
			print >>outmax, "%f %f" % (time,maxload)
			oldmax = maxload
		if oldmin != minload:
			#if oldmin != None:
			#	print >>outmin, "%f %f" % (time,oldmin)
			print >>outmin, "%f %f" % (time,minload)
			oldmin = minload
infile.close()
outmax.close()
outmin.close()
