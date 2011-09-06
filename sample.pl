#!/usr/bin/perl
# Line sampler
#
# Given a multi-line file, this script randomly
# print some of the lines. A percentage value in (0,100]
# is required as an argument.

use strict;
use warnings;

my $percent = shift;
die "Percentage as argument required" unless ($percent > 0 && $percent <= 100);
while(<>) {
	print if (rand()*100 < $percent);
};
