set term postscript eps enhanced color "Times-Roman"
set output "att.pareto.k.eps"
set key left
set size 0.5,0.5
unset ytics
set yrange [3900:4200]
plot "att.pareto.k" w lp lt 1 lc rgbcolor "#FF0000" notitle

set output "att.rand.k.eps"
set key left
set size 0.5,0.5
unset ytics
set yrange [188:189]
plot "att.rand.k" w lp lt 1 lc rgbcolor "#FF0000" notitle

set output "ft5.rand.k.eps"
set key left
set size 0.5,0.5
unset ytics
set yrange [5.5:6]
plot "ft5.rand.k" w lp lt 1 lc rgbcolor "#FF0000" notitle

set output "ft5.pareto.k.eps"
set key left
set size 0.5,0.5
unset ytics
set yrange [300:500]
plot "ft5.pareto.k" w lp lt 1 lc rgbcolor "#FF0000" notitle
