#!/usr/bin/perl
# Crop a file according to regex matching rules.
# Copyright 2011 (c) Adrian Sai-wah Tam <adrian.sw.tam@gmail.com>
# Thu, 01 Sep 2011 11:12:32 +0800

use strict;
use warnings;

########################
# Options parsing
my $opt;
my $file;
my $fault = 0;
my $before;
my $binc = 0;
my $after;
my $ainc = 0;
while (scalar @ARGV) {
	$opt = shift @ARGV;
	if ($opt =~ /^-/) {
		if ($opt eq "-B") {
			$binc = 1;
			$before = shift @ARGV;
		} elsif ($opt eq "-b") {
			$before = shift @ARGV;
		} elsif ($opt eq "-A") {
			$ainc = 1;
			$after = shift @ARGV;
		} elsif ($opt eq "-a") {
			$after = shift @ARGV;
		} else {
			$fault = 1;
		}
	} elsif (! defined $file) {
		$file = $opt;
	} else {
		$fault = 1;
	}
}

if ($fault) { die <<END
Synopsis:
    $0 [options] [file]
Descriptions
    Crop a file according to regex matching rules. If no file is provided, input is taken from stdin.

    -a regex: Echo the file after the first occurance of a line matching this regex
    -A regex: Same as -a, but include the line of match
    -b regex: Stop echoing the file on the first occurance of a line matching this regex
    -B regex: Same as -b, but also echo the line of match
END
}

########################
# Cropping
my $echo = ! defined $after;
$file = "&STDIN" unless defined $file;
open my $f, "<$file" or die "Cannot open file $file";
while (<$f>) {
	if (! $echo) {
		if (/$after/) {
			print if $ainc;
			$echo = 1;
		};
	} else {
		if (defined $before && /$before/) {
			print if $binc;
			last;
		};
		print;
	}
}
close($f)
