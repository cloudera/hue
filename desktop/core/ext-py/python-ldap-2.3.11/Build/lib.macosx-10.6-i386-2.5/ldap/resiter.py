"""
ldap.resiter - processing LDAP results with iterators

See http://www.python-ldap.org/ for details.

\$Id: resiter.py,v 1.4 2009/07/26 11:09:58 stroeder Exp $

Python compability note:
Requires Python 2.3+
"""

import ldap

from ldap import __version__


class ResultProcessor:
  """
  Mix-in class for ldap.ldapopbject.LDAPObject which adds method allresults().
  """

  def allresults(self,msgid,timeout=-1):
    """
    Generator function which returns an iterator for processing all LDAP operation
    results of the given msgid.
    """
    result_type,result_list,result_msgid,result_serverctrls = self.result3(msgid,0,timeout)
    while result_type and result_list:
      # Loop over list of search results
      for result_item in result_list:
        yield (result_type,result_list,result_msgid,result_serverctrls)
      result_type,result_list,result_msgid,result_serverctrls = self.result3(msgid,0,timeout)
    return # allresults()
