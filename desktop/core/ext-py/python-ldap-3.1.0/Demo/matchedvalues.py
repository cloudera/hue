#!/usr/bin/env python
#
# demo for matched values control (RFC 3876)
#
# suppose the uid=jsmith LDAP entry has two mail attributes:
#
# dn: uid=jsmith,ou=People,dc=example,dc=com
# (...)
# mail: jsmith@example.com
# mail: jsmith@example.org
#
# Let's say you want to fetch only the example.org email. Without MV,
# you would first fetch all mail attributes and then filter them further
# on the client. With the MV control, the result can be given to the
# client already filtered.
#
# Sample output:
# $ ./matchedvalues.py
# LDAP filter used: (&(objectClass=inetOrgPerson)(mail=*@example.org))
# Requesting 'mail' attribute back
#
# No matched values control:
# dn: uid=jsmith,ou=People,dc=example,dc=com
# mail: jsmith@example.org
# mail: john@example.com
#
# Matched values control: (mail=*@example.org)
# dn: uid=jsmith,ou=People,dc=example,dc=com
# mail: jsmith@example.org
from __future__ import print_function

import ldap
from ldap.controls import MatchedValuesControl

def print_result(search_result):
    for n in range(len(search_result)):
        print("dn: %s" % search_result[n][0])
        for attr in search_result[n][1].keys():
            for i in range(len(search_result[n][1][attr])):
                print("%s: %s" % (attr, search_result[n][1][attr][i]))
        print


uri = "ldap://ldap.example.com"
base = "dc=example,dc=com"
scope = ldap.SCOPE_SUBTREE
filter = "(&(objectClass=inetOrgPerson)(mail=*@example.org))"
control_filter = "(mail=*@example.org)"

ld = ldap.initialize(uri)

mv = MatchedValuesControl(criticality=True, controlValue=control_filter)

res = ld.search_ext_s(base, scope, filter, attrlist = ['mail'])
print("LDAP filter used: %s" % filter)
print("Requesting 'mail' attribute back")
print
print("No matched values control:")
print_result(res)

res = ld.search_ext_s(base, scope, filter, attrlist = ['mail'], serverctrls = [mv])
print("Matched values control: %s" % control_filter)
print_result(res)
