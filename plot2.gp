set term postscript eps enhanced color "Times-Roman"

set output 'ft5.rand.maxmin.eps'
set key right bottom
set size 0.5,0.5
unset ytics
set yrange [0:]
set xrange [0:100]
plot '< cat ft5.rand.routekpath.max | ./sample.pl 7.97' w l lt 1 lc rgbcolor '#FF0000' title 'k-path', \
     '< cat ft5.rand.routeecmp.max | ./sample.pl 7.82' w l lt 2 lc rgbcolor '#0000FF' title 'ECMP'

set output 'att.rand.maxmin.eps'
set key right bottom
set size 0.5,0.5
unset ytics
set yrange [0:]
set xrange [0:100]
plot '< cat att.rand.routekpath.max | ./sample.pl 0.57' w l lt 1 lc rgbcolor '#FF0000' title 'k-path', \
     '< cat att.rand.routeecmp.max | ./sample.pl 0.36' w l lt 2 lc rgbcolor '#0000FF' title 'ECMP'
