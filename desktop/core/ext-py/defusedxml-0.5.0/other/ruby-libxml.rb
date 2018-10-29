#!/usr/bin/ruby -w
require 'libxml'

include LibXML

class PostCallbacks
  include XML::SaxParser::Callbacks

  def on_start_element(element, attributes)
    puts element
  end
end

parser = XML::SaxParser.file(ARGV[0])
parser.callbacks = PostCallbacks.new
parser.parse

