#!/usr/bin/ruby -w
require "rexml/document"

xml = File.read(ARGV[0])
# REXML::Document.entity_expansion_limit = 1000
xmldoc = REXML::Document.new(xml)
data = xmldoc.root.text
#puts data.length
puts data
