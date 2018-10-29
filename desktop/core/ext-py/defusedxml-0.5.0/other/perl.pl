#!/usr/bin/perl

use XML::Simple;
use Data::Dumper;

$parser = new XML::Simple;
$xml = $parser->XMLin("$ARGV[0]");
$data = Dumper($xml);
print $data;
