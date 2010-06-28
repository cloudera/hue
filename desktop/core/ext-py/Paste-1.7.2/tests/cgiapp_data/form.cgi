#!/usr/bin/env python

import cgi

print 'Content-type: text/plain'
print

form = cgi.FieldStorage()

print 'Filename:', form['up'].filename
print 'Name:', form['name'].value
print 'Content:', form['up'].file.read()
