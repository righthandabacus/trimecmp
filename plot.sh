#!/usr/bin/env bash

perl -ne 'print if $x;$x=1 if /^L/;' $1 | perl -pe 's/^.*, //;s/]//' | sort -n | nl > _data1
perl -ne 'print if $x;$x=1 if /^L/;' $2 | perl -pe 's/^.*, //;s/]//' | sort -n | nl > _data2
perl -ne 'print if $x;$x=1 if /^L/;' $3 | perl -pe 's/^.*, //;s/]//' | sort -n | nl > _data3

echo 'set term postscript eps enhanced color'
echo 'set output "graph.eps"'
echo 'set key left'
echo 'plot "_data1" w l title "k-short", "_data2" w l title "k-free", "_data3" w l title "ecmp"'

