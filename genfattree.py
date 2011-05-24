#!/usr/bin/env python

# Use of PGF/TikZ to draw the fat-tree network. The output is a
# LaTeX file.

print "\\begin{tikzpicture}[scale=0.28]"

###########################################################
# Parameter setting
swwidth=1.618	# Width of a switch
swheight=1.0	# Height of a switch
swspacing=0.2	# Spacing between agg./edge switches
podsize=2	# Number of edge switch in a pod
podspacing=0.8	# Spacing between pods
numpod=0	# Number of pods, double of podsize if zero
easpacing=1.5	# Separation between agg. and edge switches
caspacing=5.0	# Separation between agg. and core switches
ehspacing=0.8	# Separation between edge switch and host
hostsize=0.15	# Size of the host circle
numcore=0	# Number of core, auto-calculate if zero
coreoffset=1.5	# Offset between the edge of core layer and the edge of agg layer

##########################################################
# Draw the edge and aggregate switches
if numpod==0:
	numpod = podsize*2
refx = -swwidth
refy = 0
for y in range(numpod):
	for x in range(podsize):
		# Edge switches
		refx += swwidth
		print "\\draw (%f,%f) rectangle +(%f,%f);    %% Pod %d switch %d edge" % (refx,refy,swwidth,swheight,y,x)
		# Aggregation switches
		print "\\draw (%f,%f) rectangle (%f,%f);    %% Pod %d switch %d aggr" % (refx,refy+swheight+easpacing,refx+swwidth,refy+swheight*2+easpacing,y,x)
		refx += swspacing
	refx += podspacing
print "";

##########################################################
# Draw the interconnections between edge and aggregate switches
fanoutpos = swwidth/podsize/2;
refx = 0;
refy = swheight;
for y in range(numpod):
	for x in range(podsize):
		# Interconnections
		for z in range(podsize):
			print "\\draw (%f,%f) -- (%f,%f);    %% Pod %d edge %d output %d" % (refx+(swwidth+swspacing)*x+fanoutpos*(1+2*z), refy, refx+(swwidth+swspacing)*z+fanoutpos*(1+2*x), refy+easpacing, y,x,z)
	refx += (swwidth+swspacing)*podsize + podspacing
print "";

##########################################################
# Draw the core switches
if numcore==0:
	numcore=podsize*podsize;	# Number of core
# spacing between core switches
corespacing = ((podsize*numpod*(swwidth+swspacing) + (numpod-1)*podspacing - swspacing - swwidth - coreoffset*2)/(numcore-1))-swwidth
refx = coreoffset;
refy = caspacing + easpacing + 2*swheight;
for x in range(numcore):
	print "\\draw (%f,%f) rectangle +(%f,%f);    %% Core %d" % (refx,refy,swwidth,swheight,x)
	refx += swwidth + corespacing
print "";

##########################################################
# Draw the interconnections between core and aggregate switches
aggout = fanoutpos
corefanoutpos = swwidth/(podsize*podsize*numpod/numcore)/2
coreout = coreoffset+corefanoutpos
thiscore = 0
refx = 0
refy = swheight*2 + easpacing
for y in range(numpod):
	for x in range(podsize):
		# Interconnections
		for z in range(podsize):
			print "\\draw(%f,%f) -- (%f,%f);    %% Pod %d switch %d to core %d" % (refx+aggout, refy, refx+coreout, refy+caspacing, y, x, thiscore)
			aggout += fanoutpos*2
			thiscore += 1
			if (thiscore < numcore):
				coreout += corespacing + swwidth
			else:
				coreout += corefanoutpos*2 - (corespacing+swwidth)*(thiscore-1)
				thiscore = 0
		aggout += swspacing
	aggout += podspacing
print ""

##########################################################
# Draw the connection to hosts
refx = refy = 0;
edgeout=fanoutpos;
for y in range(numpod):
	for x in range(podsize):
		for z in range(podsize):
			print "\\draw (%f,0) -- (%f,-%f)    %% Pod %d switch %d host %d" % (edgeout, edgeout, ehspacing, y, x, z)
			print "(%f,-%f) circle (%f);" % (edgeout, ehspacing+hostsize, hostsize)
			edgeout += fanoutpos*2
		edgeout += swspacing
	edgeout += podspacing

print "";

print "\end{tikzpicture}"
