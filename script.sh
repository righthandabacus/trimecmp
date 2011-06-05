#!/bin/bash

for TOPOFILE in *topo ; do
	TOPO=${TOPOFILE%.topo}
	./kpath.py -t $TOPO.topo -m $TOPO.full.traffic > $TOPO.all.full.kpath
	./kpath.py -t $TOPO.topo -m $TOPO.rand.traffic > $TOPO.all.rand.kpath
	./ecmp.py -t $TOPO.topo -m $TOPO.full.traffic > $TOPO.all.full.ecmp
	./ecmp.py -t $TOPO.topo -m $TOPO.rand.traffic > $TOPO.all.rand.ecmp
	./kpath.py -t $TOPO.topo -m <(cat $TOPO.full.traffic | ./trSample.pl 75) > $TOPO.part.full.kpath
	./kpath.py -t $TOPO.topo -m <(cat $TOPO.rand.traffic | ./trSample.pl 75) > $TOPO.part.rand.kpath
	./ecmp.py -t $TOPO.topo -m <(cat $TOPO.full.traffic | ./trSample.pl 75) > $TOPO.part.full.ecmp
	./ecmp.py -t $TOPO.topo -m <(cat $TOPO.rand.traffic | ./trSample.pl 75) > $TOPO.part.rand.ecmp
done
