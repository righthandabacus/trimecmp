#!/usr/bin/env bash

./crop.pl -a '^L' $1.ecmp | perl -pe 's/^.*= //' | nl > _data1
./crop.pl -a '^L' $1.kshortest | perl -pe 's/^.*= //' | nl > _data2
./crop.pl -a '^L' $1.kshortpath | perl -pe 's/^.*= //' | nl > _data3
./crop.pl -a '^L' $1.kpath | perl -pe 's/^.*= //' | nl > _data4

(
echo 'set term postscript eps enhanced color "Times-Roman"'
echo 'set output "graph.eps"'
echo 'set key left'
echo 'set size 0.5,0.5'
echo 'unset ytics'
echo 'set yrange [0:]'
echo 'plot "_data1" w l lt 1 lc rgbcolor "#000000" title "ECMP", \'
echo '     "_data2" w l lt 1 lc rgbcolor "#FF0000" title "{/Symbol q}=0", \'
echo '     "_data3" w l lt 4 lc rgbcolor "#FF00FF" title "{/Symbol q}=25%", \'
echo '     "_data4" w l lt 4 lc rgbcolor "#0000FF" title "{/Symbol q}={/Symbol \245}", \'
echo '     "<cat _data2|./interval.pl 10" w p lc rgbcolor "#FF0000" pt 1 notitle, \'
echo '     "<cat _data3|./interval.pl 10" w p lc rgbcolor "#FF00FF" pt 2 notitle, \'
echo '     "<cat _data4|./interval.pl 10" w p lc rgbcolor "#0000FF" pt 6 notitle'
) | gnuplot

mv graph.eps $1.eps
