#!/bin/bash

###############################################################################
#
# ECMP against k-path
#  objective: Show that k-path is no worse than ECMP
#  details:
#    k-path algorithm with overshoot theta=0 and k=4 on the following
#    topologies:
#    1. fattrees, XGFT(2;3,6;3,3) and XGFT(2;4,8;4,4) and XGFT(2;12,24;12,12)
#    2. att, level3
#    and with the following traffic patterns
#    1. All-to-all constant traffic
#    2. All-to-all uniform random traffic
#    3. Pareto random, i.e. 20% nodes carry 80% traffic, both sender and
#       receiver
#    4. Same as above, but with clustering
#    On traffic pattern 3, the way to generate traffic matrix is as follows
#      S = 20% sample of N
#      R = 20% sample of N, sample drawn independent of S
#      Feed to matrixgen2.py with S and R as the hot senders and receivers
#      respectively, and rho_s = rho_r = rho_c = 0.8
#    On traffic pattern 4, we set rho_c = 1.0 instead of 0.8
#

# Generate topologies
if [ ! -e ft3.topo ]; then
./topogen-ft.py -k 3 > ft3.topo
./topogen-ft.py -k 4 > ft4.topo
./topogen-ft.py -k 5 > ft5.topo
fi
# att.topo and level3.topo are obtained from Rocketfuel

# Generate traffic patterns: Constant
if [ ! -e att.const.traffic ]; then
./matrixgen.py -t att.topo -1 > att.const.traffic
./matrixgen.py -t level3.topo -1 > level3.const.traffic
./matrixgen.py -t <(grep E ft3.topo) -1 > ft3.const.traffic
./matrixgen.py -t <(grep E ft4.topo) -1 > ft4.const.traffic
./matrixgen.py -t <(grep E ft5.topo) -1 > ft5.const.traffic
fi

# Generate traffic patterns: Random
if [ ! -e att.rand.traffic ]; then
./matrixgen.py -t att.topo > att.rand.traffic
./matrixgen.py -t level3.topo > level3.rand.traffic
./matrixgen.py -t <(grep E ft3.topo) > ft3.rand.traffic
./matrixgen.py -t <(grep E ft4.topo) > ft4.rand.traffic
./matrixgen.py -t <(grep E ft5.topo) > ft5.rand.traffic
fi

# Generate traffic patterns: Pareto and clustered
if [ ! -e att.nodes ]; then
grep ^N att.topo | cut -f2 -d' ' > att.nodes
N=`wc -l < att.nodes`
M=$[N/5]
shuf att.nodes | head -n $M > att.hotsender
shuf att.nodes | head -n $M > att.hotreceiver
./matrixgen2.py -t att.topo -s att.hotsender -r att.hotreceiver > att.pareto.traffic
./matrixgen2.py -t att.topo -s att.hotsender -r att.hotreceiver -C 1 > att.cluster.traffic
fi

if [ ! -e level3.nodes ]; then
grep ^N level3.topo | cut -f2 -d' ' > level3.nodes
N=`wc -l < level3.nodes`
M=$[N/5]
shuf level3.nodes | head -n $M > level3.hotsender
shuf level3.nodes | head -n $M > level3.hotreceiver
./matrixgen2.py -t level3.topo -s level3.hotsender -r level3.hotreceiver > level3.pareto.traffic
./matrixgen2.py -t level3.topo -s level3.hotsender -r level3.hotreceiver -C 1 > level3.cluster.traffic
fi

if [ ! -e ft3.nodes ]; then
grep ^N ft3.topo | grep E | cut -f2 -d' ' > ft3.nodes
N=`wc -l < ft3.nodes`
M=$[N/5]
shuf ft3.nodes | head -n $M > ft3.hotsender
shuf ft3.nodes | head -n $M > ft3.hotreceiver
./matrixgen2.py -t <(grep E ft3.topo) -s ft3.hotsender -r ft3.hotreceiver > ft3.pareto.traffic
./matrixgen2.py -t <(grep E ft3.topo) -s ft3.hotsender -r ft3.hotreceiver -C 1 > ft3.cluster.traffic
fi

if [ ! -e ft4.nodes ]; then
grep ^N ft4.topo | grep E | cut -f2 -d' ' > ft4.nodes
N=`wc -l < ft4.nodes`
M=$[N/5]
shuf ft4.nodes | head -n $M > ft4.hotsender
shuf ft4.nodes | head -n $M > ft4.hotreceiver
./matrixgen2.py -t <(grep E ft4.topo) -s ft4.hotsender -r ft4.hotreceiver > ft4.pareto.traffic
./matrixgen2.py -t <(grep E ft4.topo) -s ft4.hotsender -r ft4.hotreceiver -C 1 > ft4.cluster.traffic
fi

if [ ! -e ft5.nodes ]; then
grep ^N ft5.topo | grep E | cut -f2 -d' ' > ft5.nodes
N=`wc -l < ft5.nodes`
M=$[N/5]
shuf ft5.nodes | head -n $M > ft5.hotsender
shuf ft5.nodes | head -n $M > ft5.hotreceiver
./matrixgen2.py -t <(grep E ft5.topo) -s ft5.hotsender -r ft5.hotreceiver > ft5.pareto.traffic
./matrixgen2.py -t <(grep E ft5.topo) -s ft5.hotsender -r ft5.hotreceiver -C 1 > ft5.cluster.traffic
fi

# Computation: ecmp vs kpath with theta=0, k=4
if [ ! -e att.const.ecmp ]; then
./ecmp.py -t att.topo -m att.const.traffic > att.const.ecmp
./ecmp.py -t level3.topo -m level3.const.traffic > level3.const.ecmp
./ecmp.py -t ft3.topo -m ft3.const.traffic > ft3.const.ecmp
./ecmp.py -t ft4.topo -m ft4.const.traffic > ft4.const.ecmp
./ecmp.py -t ft5.topo -m ft5.const.traffic > ft5.const.ecmp
fi

if [ ! -e att.rand.ecmp ]; then
./ecmp.py -t att.topo -m att.rand.traffic > att.rand.ecmp
./ecmp.py -t level3.topo -m level3.rand.traffic > level3.rand.ecmp
./ecmp.py -t ft3.topo -m ft3.rand.traffic > ft3.rand.ecmp
./ecmp.py -t ft4.topo -m ft4.rand.traffic > ft4.rand.ecmp
./ecmp.py -t ft5.topo -m ft5.rand.traffic > ft5.rand.ecmp
fi

if [ ! -e att.pareto.ecmp ]; then
./ecmp.py -t att.topo -m att.pareto.traffic > att.pareto.ecmp
./ecmp.py -t level3.topo -m level3.pareto.traffic > level3.pareto.ecmp
./ecmp.py -t ft3.topo -m ft3.pareto.traffic > ft3.pareto.ecmp
./ecmp.py -t ft4.topo -m ft4.pareto.traffic > ft4.pareto.ecmp
./ecmp.py -t ft5.topo -m ft5.pareto.traffic > ft5.pareto.ecmp
fi

if [ ! -e att.cluster.ecmp ]; then
./ecmp.py -t att.topo -m att.cluster.traffic > att.cluster.ecmp
./ecmp.py -t level3.topo -m level3.cluster.traffic > level3.cluster.ecmp
./ecmp.py -t ft3.topo -m ft3.cluster.traffic > ft3.cluster.ecmp
./ecmp.py -t ft4.topo -m ft4.cluster.traffic > ft4.cluster.ecmp
./ecmp.py -t ft5.topo -m ft5.cluster.traffic > ft5.cluster.ecmp
fi

if [ ! -e att.const.kshortest ]; then
./kpath.py -k 4 -s -t att.topo -m att.const.traffic > att.const.kshortest
./kpath.py -k 4 -s -t level3.topo -m level3.const.traffic > level3.const.kshortest
./kpath.py -k 4 -s -t ft3.topo -m ft3.const.traffic > ft3.const.kshortest
./kpath.py -k 4 -s -t ft4.topo -m ft4.const.traffic > ft4.const.kshortest
./kpath.py -k 4 -s -t ft5.topo -m ft5.const.traffic > ft5.const.kshortest
fi

if [ ! -e att.rand.kshortest ]; then
./kpath.py -k 4 -s -t att.topo -m att.rand.traffic > att.rand.kshortest
./kpath.py -k 4 -s -t level3.topo -m level3.rand.traffic > level3.rand.kshortest
./kpath.py -k 4 -s -t ft3.topo -m ft3.rand.traffic > ft3.rand.kshortest
./kpath.py -k 4 -s -t ft4.topo -m ft4.rand.traffic > ft4.rand.kshortest
./kpath.py -k 4 -s -t ft5.topo -m ft5.rand.traffic > ft5.rand.kshortest
fi

if [ ! -e att.pareto.kshortest ]; then
./kpath.py -k 4 -s -t att.topo -m att.pareto.traffic > att.pareto.kshortest
./kpath.py -k 4 -s -t level3.topo -m level3.pareto.traffic > level3.pareto.kshortest
./kpath.py -k 4 -s -t ft3.topo -m ft3.pareto.traffic > ft3.pareto.kshortest
./kpath.py -k 4 -s -t ft4.topo -m ft4.pareto.traffic > ft4.pareto.kshortest
./kpath.py -k 4 -s -t ft5.topo -m ft5.pareto.traffic > ft5.pareto.kshortest
fi

if [ ! -e att.cluster.kshortest ]; then
./kpath.py -k 4 -s -t att.topo -m att.cluster.traffic > att.cluster.kshortest
./kpath.py -k 4 -s -t level3.topo -m level3.cluster.traffic > level3.cluster.kshortest
./kpath.py -k 4 -s -t ft3.topo -m ft3.cluster.traffic > ft3.cluster.kshortest
./kpath.py -k 4 -s -t ft4.topo -m ft4.cluster.traffic > ft4.cluster.kshortest
./kpath.py -k 4 -s -t ft5.topo -m ft5.cluster.traffic > ft5.cluster.kshortest
fi


###############################################################################
#
# Varying overshoot theta
#   objective: Show the advantage of k-path over ECMP, namely, allowing
#   non-shortest path to be used, which can benefit certain topologies such as
#   irregular topologies
#   details:
#     k-path algorithm with overshoot theta=100% and k=4 on the same topologies
#     and traffic pattern as above. Then compare the result of this with the
#     previous ones
#     Then repeat with theta=25%, showing a combined benefit in both regular
#     and irregular topologies
#

if [ ! -e att.const.kpath ]; then
./kpath.py -k 4 -o 1000 -t att.topo -m att.const.traffic > att.const.kpath
./kpath.py -k 4 -o 1000 -t level3.topo -m level3.const.traffic > level3.const.kpath
./kpath.py -k 4 -o 1000 -t ft3.topo -m ft3.const.traffic > ft3.const.kpath
./kpath.py -k 4 -o 1000 -t ft4.topo -m ft4.const.traffic > ft4.const.kpath
./kpath.py -k 4 -o 1000 -t ft5.topo -m ft5.const.traffic > ft5.const.kpath
fi

if [ ! -e att.rand.kpath ]; then
./kpath.py -k 4 -o 1000 -t att.topo -m att.rand.traffic > att.rand.kpath
./kpath.py -k 4 -o 1000 -t level3.topo -m level3.rand.traffic > level3.rand.kpath
./kpath.py -k 4 -o 1000 -t ft3.topo -m ft3.rand.traffic > ft3.rand.kpath
./kpath.py -k 4 -o 1000 -t ft4.topo -m ft4.rand.traffic > ft4.rand.kpath
./kpath.py -k 4 -o 1000 -t ft5.topo -m ft5.rand.traffic > ft5.rand.kpath
fi

if [ ! -e att.pareto.kpath ]; then
./kpath.py -k 4 -o 1000 -t att.topo -m att.pareto.traffic > att.pareto.kpath
./kpath.py -k 4 -o 1000 -t level3.topo -m level3.pareto.traffic > level3.pareto.kpath
./kpath.py -k 4 -o 1000 -t ft3.topo -m ft3.pareto.traffic > ft3.pareto.kpath
./kpath.py -k 4 -o 1000 -t ft4.topo -m ft4.pareto.traffic > ft4.pareto.kpath
./kpath.py -k 4 -o 1000 -t ft5.topo -m ft5.pareto.traffic > ft5.pareto.kpath
fi

if [ ! -e att.cluster.kpath ]; then
./kpath.py -k 4 -o 1000 -t att.topo -m att.cluster.traffic > att.cluster.kpath
./kpath.py -k 4 -o 1000 -t level3.topo -m level3.cluster.traffic > level3.cluster.kpath
./kpath.py -k 4 -o 1000 -t ft3.topo -m ft3.cluster.traffic > ft3.cluster.kpath
./kpath.py -k 4 -o 1000 -t ft4.topo -m ft4.cluster.traffic > ft4.cluster.kpath
./kpath.py -k 4 -o 1000 -t ft5.topo -m ft5.cluster.traffic > ft5.cluster.kpath
fi

if [ ! -e att.const.kshortpath ]; then
./kpath.py -k 4 -o 25 -t att.topo -m att.const.traffic > att.const.kshortpath
./kpath.py -k 4 -o 25 -t level3.topo -m level3.const.traffic > level3.const.kshortpath
./kpath.py -k 4 -o 25 -t ft3.topo -m ft3.const.traffic > ft3.const.kshortpath
./kpath.py -k 4 -o 25 -t ft4.topo -m ft4.const.traffic > ft4.const.kshortpath
./kpath.py -k 4 -o 25 -t ft5.topo -m ft5.const.traffic > ft5.const.kshortpath
fi

if [ ! -e att.rand.kshortpath ]; then
./kpath.py -k 4 -o 25 -t att.topo -m att.rand.traffic > att.rand.kshortpath
./kpath.py -k 4 -o 25 -t level3.topo -m level3.rand.traffic > level3.rand.kshortpath
./kpath.py -k 4 -o 25 -t ft3.topo -m ft3.rand.traffic > ft3.rand.kshortpath
./kpath.py -k 4 -o 25 -t ft4.topo -m ft4.rand.traffic > ft4.rand.kshortpath
./kpath.py -k 4 -o 25 -t ft5.topo -m ft5.rand.traffic > ft5.rand.kshortpath
fi

if [ ! -e att.pareto.kshortpath ]; then
./kpath.py -k 4 -o 25 -t att.topo -m att.pareto.traffic > att.pareto.kshortpath
./kpath.py -k 4 -o 25 -t level3.topo -m level3.pareto.traffic > level3.pareto.kshortpath
./kpath.py -k 4 -o 25 -t ft3.topo -m ft3.pareto.traffic > ft3.pareto.kshortpath
./kpath.py -k 4 -o 25 -t ft4.topo -m ft4.pareto.traffic > ft4.pareto.kshortpath
./kpath.py -k 4 -o 25 -t ft5.topo -m ft5.pareto.traffic > ft5.pareto.kshortpath
fi

if [ ! -e att.cluster.kshortpath ]; then 
./kpath.py -k 4 -o 25 -t att.topo -m att.cluster.traffic > att.cluster.kshortpath
./kpath.py -k 4 -o 25 -t level3.topo -m level3.cluster.traffic > level3.cluster.kshortpath
./kpath.py -k 4 -o 25 -t ft3.topo -m ft3.cluster.traffic > ft3.cluster.kshortpath
./kpath.py -k 4 -o 25 -t ft4.topo -m ft4.cluster.traffic > ft4.cluster.kshortpath
./kpath.py -k 4 -o 25 -t ft5.topo -m ft5.cluster.traffic > ft5.cluster.kshortpath
fi


###############################################################################
#
# Spectrum of k
#    objective: Show the law of diminishing return on k, i.e. we do not need a
#    large k for the benefits
#    details:
#      Use theta=25%, and k=1,2,4,6,8,10,12,14,16
#      Topology on XGFT(2;12,24;12,12) and att
#      Traffic pattern of (2) and (3)
#

for k in 1 2 4 6 8 10 12 14 16; do
if [ ! -e att.pareto.kpath$k ]; then
./kpath.py -k $k -o 25 -t att.topo -m att.pareto.traffic > att.pareto.kpath$k
./kpath.py -k $k -o 25 -t att.topo -m att.rand.traffic > att.rand.kpath$k
./kpath.py -k $k -o 25 -t ft5.topo -m ft5.pareto.traffic > ft5.pareto.kpath$k
./kpath.py -k $k -o 25 -t ft5.topo -m ft5.rand.traffic > ft5.rand.kpath$k
fi
done


###############################################################################
#
# Varied traffic matrix
#    objective: Show the k-path is robust to varied traffic matrix
#    details:
#      with the old k-path data, feed in the traffic matrix with 25% variation
#      in average (uniformly random scale factor [0.5,1.5]) to each element and
#      check the effect
#

if [ ! -e att.pareto.modtraffic ]; then
./matrixmod.py att.pareto.traffic > att.pareto.modtraffic
./matrixmod.py ft5.pareto.traffic > ft5.pareto.modtraffic
./matrixmod.py att.rand.traffic > att.rand.modtraffic
./matrixmod.py ft5.rand.traffic > ft5.rand.modtraffic
./kpathload.py -t att.topo -p att.pareto.kshortpath -m att.pareto.modtraffic > att.pareto.varied
./kpathload.py -t ft5.topo -p ft5.pareto.kshortpath -m ft5.pareto.modtraffic > ft5.pareto.varied
./kpathload.py -t att.topo -p att.rand.kshortpath -m att.rand.modtraffic > att.rand.varied
./kpathload.py -t ft5.topo -p ft5.rand.kshortpath -m ft5.rand.modtraffic > ft5.rand.varied
fi


###############################################################################
#
# Dynamic flow
#     objective: Instead of traffic matrix, we use a event-driven model of flow
#     placement to see the time axis of link loads
#     details:
#       first with traffic matrix model, then generate flows and feed into the
#       network

if [ ! -e att.rand.flows ]; then
./flowgen2.py -m att.rand.traffic > att.rand.flows
./flowgen2.py -m att.pareto.traffic > att.pareto.flows
./flowgen2.py -m ft5.rand.traffic > ft5.rand.flows
./flowgen2.py -m ft5.pareto.traffic > ft5.pareto.flows
fi

if [ ! -e att.rand.routeecmp ]; then
./routeecmp.py -t att.topo -f att.rand.flows > att.rand.routeecmp
fi

if [ ! -e att.pareto.routeecmp ]; then
./routeecmp.py -t att.topo -f att.pareto.flows > att.pareto.routeecmp
fi

if [ ! -e ft5.rand.routeecmp ]; then
./routeecmp.py -t ft5.topo -f ft5.rand.flows > ft5.rand.routeecmp
fi

if [ ! -e ft5.pareto.routeecmp ]; then
./routeecmp.py -t ft5.topo -f ft5.pareto.flows > ft5.pareto.routeecmp
fi

if [ ! -e att.rand.routekpath ]; then
./routekpath.py -t att.topo -p att.rand.kshortpath -f att.rand.flows > att.rand.routekpath
fi

if [ ! -e att.pareto.routekpath ]; then
./routekpath.py -t att.topo -p att.pareto.kshortpath -f att.pareto.flows > att.pareto.routekpath
fi

if [ ! -e ft5.rand.routekpath ]; then
./routekpath.py -t ft5.topo -p ft5.rand.kshortpath -f ft5.rand.flows > ft5.rand.routekpath
fi

if [ ! -e ft5.pareto.routekpath ]; then
./routekpath.py -t ft5.topo -p ft5.pareto.kshortpath -f ft5.pareto.flows > ft5.pareto.routekpath
fi
