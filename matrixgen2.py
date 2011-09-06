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
# Traffic matrix generator with hot senders/receivers
#   This script reads in (1) a set of nodes from a Rocketfuel topology file,
#   (2) a set of `hot senders', and (3) a set of `hot receivers'. The program
#   takes 3 additional parameters, namely, rho_s, the fraction of traffic (of
#   all traffic in the network) originated from the `hot senders'; rho_r, the
#   fraction of traffic towards the `hot receivers; rho_c, the fraction of
#   traffic that send from the hot senders are targetting the hot receivers.
#   
#   Denote the set of all nodes in concern with N, and the hot senders as
#   N_s \in N, hot receivers as N_r \in N, the traffic from node i to node j as
#   m_ij. Then the total traffic in the network is
#      \omega' = \sum_{i,j} m_ij
#   Assume m_ij is a random value drawn from [0,x], where
#      m_ij \in [0,\alpha]    if i \in N_s,    j \in N_r
#      m_ij \in [0,\beta]     if i \in N_s,    j \notin N_r
#      m_ij \in [0,\gamma]    if i \notin N_s, j \in N_r
#      m_ij \in [0,1]         if i \notin N_s, j \notin N_r
#   and the expected value of \omega' denoted as \omega. We further denote the
#   number of nodes in N by n, number of nodes in N_s by s, number of nodes in
#   N_r by r, and denote S = n-s, R = n-r, then we have the following equations
#   fulfilled to fit the parameters rho_s, rho_r, and rho_c:
#     2 \omega = sr\alpha + sR\beta + Sr\gamma + SR
#     (sr\alpha + sR\beta) / (2\omega) = \rho_s
#     (sr\alpha + Sr\gamma) / (2\omega) = \rho_r
#     sr\alpha / (sr\alpha + sR\beta) = \rho_c
#   Rearranging, we have the following system of three linear equations in
#   three unknowns:
#     [ sr(1-\rho_s)    sR(1-\rho_s)  -Sr\rho_s     ][\alpha]   [ SR\rho_s ]
#     [ sr(1-\rho_r)   -sR\rho_r       Sr(1-\rho_r) ][\beta ] = [ SR\rho_r ]
#     [ sr(1-\rho_c)   -sR\rho_c       0            ][\gamma]   [ 0        ]
#   by solving this system, we obtain the value for \alpha, \beta, and \gamma,
#   and generate the traffic values m_ij for all i,j accordingly.
#

import sys,getopt,random,numpy

###########################################################
# Global parameters
topofile = 'topology.txt'	# default topology file
hottx = 'sender.txt'		# hot senders
hotrx = 'receiver.txt'		# hot receivers
constant = False		# if false, the traffic is constant, or random otherwise
rho_s = 0.8			# fraction of traffic from hot senders 
rho_r = 0.8			# fraction of traffic towards hot receivers
rho_c = 0.8			# fraction of traffic that from hot senders towards hot receivers

#random.seed(1)		# Debug use: Uncomment this line for repeatible random numbers
optlist, userlist = getopt.getopt(sys.argv[1:], 't:r:s:R:S:C:1h')
for opt, optarg in optlist:
	if opt == '-t':
		topofile = optarg
	elif opt == '-r':
		hotrx = optarg
	elif opt == '-s':
		hottx = optarg
	elif opt == '-R':
		rho_r = float(optarg)
	elif opt == '-S':
		rho_s = float(optarg)
	elif opt == '-C':
		rho_c = float(optarg)
	elif opt == '-1':
		constant = True
	else:
		# getopt will fault for other options
		print "Available options"
		print " -t file : The topology file in Rocketfuel format, default is topology.txt"
		print " -s file : Hot sender nodes, default is sender.txt"
		print " -r file : Hot receiver nodes, default is receiver.txt"
		print " -S fraction: Fraction of traffic from hot senders, default is 0.8"
		print " -R fraction: Fraction of traffic towards hot receivers, default is 0.8"
		print " -C fraction: Fraction of traffic that from hot senders towards hot receivers, default is 0.8"
		print " -1 : Generate constant load for each pair of nodes"
		print " -h : This help message"
		sys.exit(1)

###########################################################
# Helper functions
def ReadNodes(f,s,r):
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

	senderFile = open(s, "r")	# Hot senders file
	tx = []	# names of nodes
	for line in senderFile:
		token = line.split()
		if (len(token) != 1): continue
		tx.append(token[0])
	senderFile.close()

	receiverFile = open(r, "r")	# Hot receivers file
	rx = []	# names of nodes
	for line in receiverFile:
		token = line.split()
		if (len(token) != 1): continue
		rx.append(token[0])
	receiverFile.close()

	return nodes,tx,rx

###########################################################
# Main program

# Read in nodes
nodes,tx,rx = ReadNodes(topofile,hottx,hotrx)

# Computation of \alpha, \beta, and \gamma
n,s,r = len(nodes),len(tx), len(rx)
S,R = n-s, n-r
A = numpy.array([[s*r*(1-rho_s),   s*R*(1-rho_s),  -S*r*rho_s],
                 [s*r*(1-rho_r),  -s*R*rho_r,       S*r*(1-rho_r)],
		 [s*r*(1-rho_c),  -s*R*rho_c,       0]])
b = numpy.array([S*R*rho_s, S*R*rho_r, 0])
[alpha,beta,gamma] = numpy.linalg.solve(A,b)

# Generate random values
for u in nodes:
	for v in nodes:
		if u == v: continue
		if u in tx and v in rx:
			scale = alpha
		elif u in tx:
			scale = beta
		elif v in rx:
			scale = gamma
		else:
			scale = 1
		value = scale * (1 if constant else random.random())
		print "%s %s %f" % (u, v, value)
