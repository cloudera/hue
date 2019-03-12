"""
ldifcopy - reads LDIF from stdin, retrieve values by URL and
           write resulting LDIF to stdout

Written by Michael Stroeder <michael@stroeder.com>

This example translates the naming context of data read from
input, sanitizes some attributes, maps/removes object classes,
maps/removes attributes., etc. It's far from being complete though.
"""

import sys,ldif

infile = sys.stdin
outfile = sys.stdout

ldif_collector = ldif.LDIFCopy(
  infile,
  outfile,
  process_url_schemes=['file','ftp','http']
)
ldif_collector.parse()
