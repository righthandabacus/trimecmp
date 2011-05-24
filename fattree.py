#!/usr/bin/env python
import sys,re,math,random,copy,time

###########################################################
# Global parameters
m = int(sys.argv[1])	# Num of paths between two nodes
n = int(sys.argv[2])	# Size of fat tree


###########################################################
# Helper functions
#
def elink(i,j,k):
	'''Convert a position code SiEjUk to link sequence number'''
	return k+(j+i*n)*n

def alink(i,j,k):
	'''Convert a position code SiAjUk to link sequence number'''
	return elink(i,j,k) + 2*n*n*n

def ComputeCost(path):
	'''Return the total path cost'''
	return sum(link[i] for i in path)

def Num2Node(num):
	'''Return the host name according to the supplied seqno'''
	subtree = num / (n*n)
	edgesw = (num % (n*n)) / n
	hostnum = num % n
	return "S%dE%dH%d" % (subtree,edgesw,hostnum)

def SelectPath(path, src, dst):
	'''Update the link cost and remember this in the routers'''
	# Resolve links into router ports
	i = src / (n*n)
	j = (src % (n*n)) / n
	k = src % n
	p = dst / (n*n)
	q = (dst % (n*n)) / n
	r = dst % n
	alpha = path[0] % n
	beta = path[1] % n
	# If src & dst are in the same edge switch, no link is used. Can stop here.
	if i == p and j == q: return "in edge"
	# if the source and destination are in the same subtree, only E-A links are used.
	pathname = []
	if i == p:
		path = [path[0],path[3]]
		edge[(n*i+j)*2*n + n+alpha].append([src,dst])
		aggr[(n*p+alpha)*2*n + q].append([src,dst])
		pathname.append("S%dE%dU%d" % (i,j,alpha))
		pathname.append("S%dA%dD%d" % (p,alpha,q))
		pathname.append("S%dE%dD%d" % (p,q,r))
	# Else, use all four links
	else:
		edge[(n*i+j)*2*n + n+alpha].append([src,dst])
		aggr[(n*i+alpha)*2*n + n+beta].append([src,dst])
		aggr[(n*p+alpha)*2*n + q].append([src,dst])
		core[(n*alpha+beta)*2*n + p].append([src,dst])
		pathname.append("S%dE%dU%d" % (i,j,alpha))
		pathname.append("S%dA%dU%d" % (i,alpha,beta))
		pathname.append("C%dD%d" % (n*alpha+beta, p))
		pathname.append("S%dA%dD%d" % (p,alpha,q))
		pathname.append("S%dE%dD%d" % (p,q,r))
	# Update link cost
	for i in path:
		link[i] += 1
	return " ".join(pathname)

###########################################################
# Part 1:
#   Construct data structures 

link = [0 for i in range(2*4*n*n*n)]	# 4n^3 number of inter-router links, two directions
core = [[] for i in range(n*n*2*n)]	# List of destinations for each port in core
aggr = [[] for i in range(2*n*n*2*n)]	# List of destinations for each port in aggr
edge = [[] for i in range(2*n*n*2*n)]	# List of destinations for each port in edge

###########################################################
# Part 2:
#   Interative procedure

# prepare the 2n^3 nodes
nodes = range(2*n*n*n)
pairs = [[i,j] for i in nodes for j in nodes if j != i]
random.shuffle(pairs)

# for a pair of hosts in random order
for [a,b] in pairs:
	# Resolve node number into position code SiEjHk -> SpEqHr
	i = a / (n*n)
	j = (a % (n*n)) / n
	k = a % n
	p = b / (n*n)
	q = (b % (n*n)) / n
	r = b % n
	print "S%dE%dH%d -> S%dE%dH%d: " % (i,j,k,p,q,r)
	# Enumerate the n^2 paths and find their cost
	paths = []
	cost = []
	for alpha in range(n):
		for beta in range(n):
			path = [elink(i,j,alpha), alink(i,alpha,beta), 4*n*n*n+alink(p,alpha,beta), 4*n*n*n+elink(p,q,alpha)]
			paths.append(path)
			cost.append( ComputeCost(path) )
	# Find the best m paths with smallest cost
	costList = range(n*n)
	for c in range(m):
		mincost = min(cost[u] for u in costList)
		random.shuffle(costList)
		for d in costList:
			if cost[d] != mincost: continue
			# path[d] is the one, do something with it
			print "      (%d) " % (mincost),
			print SelectPath(paths[d], a, b)
			# remove this path from further selection
			costList = [u for u in costList if u != d]
			break

###########################################################
# Part 3:
#   Print route configuration data
print "Link costs:"
h = 0
for i in range(2*n):
	for j in range(n):
		for k in range(n):
			print "    S%dE%dU%d: %d" % (i,j,k,link[h])
			h += 1
for i in range(2*n):
	for j in range(n):
		for k in range(n):
			print "    S%dA%dU%d: %d" % (i,j,k,link[h])
			h += 1
for i in range(2*n):
	for j in range(n):
		for k in range(n):
			print "    S%dA%dD%d: %d" % (i,k,j,link[h])
			h += 1
for i in range(2*n):
	for j in range(n):
		for k in range(n):
			print "    C%dD%d: %d" % (j*n+k,i,link[h])
			h += 1

print "Routes:"
for i in range(2*n):
	for j in range(n):
		for k in range(n):
			print "    S%dE%dU%d: (%d)\n       " % (i,j,k,len(edge[(n*i+j)*2*n+n+k])),
			print "\n        ".join(sorted("(%s,%s)" % (Num2Node(pair[0]),Num2Node(pair[1])) for pair in edge[(n*i+j)*2*n+n+k]))
for i in range(2*n):
	for j in range(n):
		for k in range(n):
			print "    S%dA%dD%d: (%d)\n       " % (i,j,k,len(aggr[(n*i+j)*2*n+k])),
			print "\n        ".join(sorted("(%s,%s)" % (Num2Node(pair[0]),Num2Node(pair[1])) for pair in aggr[(n*i+j)*2*n+k]))
		for k in range(n):
			print "    S%dA%dU%d: (%d)\n       " % (i,j,k,len(aggr[(n*i+j)*2*n+n+k])),
			print "\n        ".join(sorted("(%s,%s)" % (Num2Node(pair[0]),Num2Node(pair[1])) for pair in aggr[(n*i+j)*2*n+n+k]))
for i in range(n*n):
	for k in range(2*n):
		print "    C%dD%d: (%d)\n       " % (i, k, len(core[2*n*i+k])),
		print "\n        ".join(sorted("(%s,%s)" % (Num2Node(pair[0]),Num2Node(pair[1])) for pair in core[2*n*i+k]))
exit()

'''
This program use heuristic algorithm to optimize the multipath routing in a fat
tree network. In a fat-tree network of degree n, there are n^2 paths between
any two nodes. Instead of utilizing all the n^2 paths, we use only k of them.
However, to avoid disparity in link utilization, we try to make each link
equally loaded amongst their peers. In this program, we assume every pair has
equal amount of traffic. A future extension can include a traffic matrix as an
input.

This program uses hosts as the basis for a flow.
'''
