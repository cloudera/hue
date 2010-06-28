"""
The purpose of this script is to test thread-safety

It's called with an arbitrary number of LDAP URLs which
specifies LDAP searches each executed continously in
a separate thread with a separate LDAPObject instance.
"""

import sys,time,threading,ldap,ldapurl

ldap.LIBLDAP_R = 1

class TestThread(threading.Thread):

  def __init__(self,ldap_url):
    self.ldap_url = ldapurl.LDAPUrl(ldap_url)
    # Open the connection
    self.l = ldap.ldapobject.SimpleLDAPObject(
      self.ldap_url.initializeUrl(),trace_level=0
    )
    self.stop_event = threading.Event()
    threading.Thread.__init__(self)
    self.setName(self.__class__.__name__+self.getName()[6:])
    print 'Initialized',self.getName(),self.ldap_url.unparse()

  def run(self):
    """Thread function for cleaning up session database"""
    try:
      while not self.stop_event.isSet():
        start_time=time.time()
        ldap_result = self.l.search_s(
          self.ldap_url.dn.encode('utf-8'),
          self.ldap_url.scope,
          self.ldap_url.filterstr.encode('utf-8'),
          self.ldap_url.attrs
        )
        end_time=time.time()
        # Let us see something working
        print self.getName(),': %d search results in %0.1f s' % (len(ldap_result),end_time-start_time)
    finally:
      self.l.unbind_s()
      del self.l

thread_list = []

ldap_url_list = sys.argv[1:]

if ldap_url_list:

  for ldap_url in sys.argv[1:]:
    thread_list.append(TestThread(ldap_url))

  print 'Starting %d threads.' % (len(thread_list))

  for t in thread_list:
    t.start()
    print 'Started thread',t.getName()

  print 'Started %d threads.' % (len(thread_list))

  try:
    while 1:
      pass
  except KeyboardInterrupt:
    # Terminate all threads
    for t in thread_list:
      print 'Terminating thread',t.getName(),'...'
      t.stop_event.set()

else:
  print 'Error: You have to provide a list of LDAP URLs at command-line'
