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
# Traffic matrix modifier 
#   Read in a traffic matrix as provided by matrixgen.py, and multiply each
#   entry's value by a value in [0.5,1.5] so that it has a 25% variation in
#   average.
#

import sys,getopt,random

###########################################################
# Global parameters
matrixfile = 'matrix.txt'	# default topology file

#random.seed(1)		# Debug use: Uncomment this line for repeatible random numbers
optlist, userlist = getopt.getopt(sys.argv[1:], 'm:h')
for opt, optarg in optlist:
	if opt == '-m':
		matrixfile = optarg
	else:
		# getopt will fault for other options
		print "Available options"
		print " -m file : The traffic matrix file, default is matrix.txt"
		print " -h : This help message"
		sys.exit(1)

###########################################################
# Main program
#   Read in nodes, for each pair of distinct nodes, create a random value
data = open(matrixfile, "r")	# open the traffic matrix file
for line in data:
	token = line.split()
	if len(token) == 3:
		scale = 0.5 + random.random()
		print "%s %s %f" % (token[0], token[1], float(token[2])*scale)
	else:
		print line
data.close()
