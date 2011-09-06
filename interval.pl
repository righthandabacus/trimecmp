#!/usr/bin/perl
# Line sampler
#
# Given a multi-line file, this script regularly print a line every n lines.

use strict;
use warnings;

my $interval = shift;
die "Interval as argument required" unless ($interval > 0);
while(<>) {
	print unless ($. % $interval);
};

