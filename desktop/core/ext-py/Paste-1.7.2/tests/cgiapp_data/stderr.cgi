#!/usr/bin/env python

import sys
print 'Status: 500 Server Error'
print 'Content-type: text/html'
print
print 'There was an error'
print >> sys.stderr, 'some data on the error'
