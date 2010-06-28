# -*- Mode: Python; tab-width: 4 -*-

import sys,types,time

def get_refcounts():
    d = {}
    sys.modules
    # collect all classes
    for m in sys.modules.values():
        for sym in dir(m):
            o = getattr (m, sym)
            if type(o) is types.ClassType:
                d[o] = sys.getrefcount (o)
    # sort by refcount
    pairs = map (lambda x: (x[1],x[0]), d.items())
    pairs.sort()
    pairs.reverse()
    return pairs

def print_top(max):
    for n, c in get_refcounts()[:max]:
        print '%10d %s' % (n, c.__name__)


import ldap

l = ldap.initialize('ldap://localhost:1390/')

i = 100000

while i:
  i -= 1
  res = l.search_ext_s("",ldap.SCOPE_BASE,"(objectClass=*)",timeout=40,sizelimit=10000)
#  if i % 100==0:
#    print_top(50)
#    print '---------------'
#    time.sleep(0.1)
#    l.unbind()
#    del l
#    l = ldap.initialize('ldap://localhost:1390/')

l.unbind()
