#!/usr/bin/ruby -w
require 'hpricot'

xml = File.read(ARGV[0])
doc = Hpricot(xml)
puts doc

