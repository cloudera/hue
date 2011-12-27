"""
filters.py - misc stuff for handling LDAP filter strings (see RFC2254)

See http://www.python-ldap.org/ for details.

\$Id: filter.py,v 1.9 2011/07/22 07:20:53 stroeder Exp $

Compability:
- Tested with Python 2.0+
"""

from ldap import __version__


def escape_filter_chars(assertion_value,escape_mode=0):
  """
  Replace all special characters found in assertion_value
  by quoted notation.
  
  escape_mode
      If 0 only special chars mentioned in RFC 4515 are escaped.
      If 1 all NON-ASCII chars are escaped.
      If 2 all chars are escaped.
  """
  if escape_mode:
    r = []
    if escape_mode==1:
      for c in assertion_value:
        if c < '0' or c > 'z' or c in "\\*()":
          c = "\\%02x" % ord(c)
        r.append(c)
    elif escape_mode==2:
      for c in assertion_value:
        r.append("\\%02x" % ord(c))
    else:
      raise ValueError('escape_mode must be 0, 1 or 2.')
    s = ''.join(r)
  else:
    s = assertion_value.replace('\\', r'\5c')
    s = s.replace(r'*', r'\2a')
    s = s.replace(r'(', r'\28')
    s = s.replace(r')', r'\29')
    s = s.replace('\x00', r'\00')
  return s 


def filter_format(filter_template,assertion_values):
  """
  filter_template
        String containing %s as placeholder for assertion values.
  assertion_values
        List or tuple of assertion values. Length must match
        count of %s in filter_template.
  """
  return filter_template % (tuple(map(escape_filter_chars,assertion_values)))
