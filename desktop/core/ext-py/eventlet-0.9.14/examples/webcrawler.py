#! /usr/bin/env python
"""
This is a simple web "crawler" that fetches a bunch of urls using a pool to 
control the number of outbound connections. It has as many simultaneously open
connections as coroutines in the pool.

The prints in the body of the fetch function are there to demonstrate that the
requests are truly made in parallel.
"""

urls = ["http://www.google.com/intl/en_ALL/images/logo.gif",
     "https://wiki.secondlife.com/w/images/secondlife.jpg",
     "http://us.i1.yimg.com/us.yimg.com/i/ww/beta/y3.gif"]

import eventlet
from eventlet.green import urllib2  

def fetch(url):
  print "opening", url
  body = urllib2.urlopen(url).read()
  print "done with", url
  return url, body

pool = eventlet.GreenPool(200)
for url, body in pool.imap(fetch, urls):
  print "got body from", url, "of length", len(body)