# -*- coding: utf-8 -*-
from __future__ import print_function

url = "ldap://localhost:1390"
base = "dc=stroeder,dc=de"
search_flt = r'(objectClass=*)'
page_size = 10
binddn = ''
bindpw = ''
trace_level = 0

import ldap,pprint

try:
  from ldap.controls.pagedresults import SimplePagedResultsControl
except ImportError:
  from ldap.controls.libldap import SimplePagedResultsControl

searchreq_attrlist=['cn','entryDN','entryUUID','mail','objectClass']

#ldap.set_option(ldap.OPT_DEBUG_LEVEL,255)
ldap.set_option(ldap.OPT_REFERRALS, 0)
l = ldap.initialize(url,trace_level=trace_level)
l.protocol_version = 3
l.simple_bind_s(binddn,bindpw)

req_ctrl = SimplePagedResultsControl(True,size=page_size,cookie='')

known_ldap_resp_ctrls = {
  SimplePagedResultsControl.controlType:SimplePagedResultsControl,
}

# Send search request
msgid = l.search_ext(
  base,
  ldap.SCOPE_SUBTREE,
  search_flt,
  attrlist=searchreq_attrlist,
  serverctrls=[req_ctrl]
)

pages = 0
while True:
    pages += 1
    print('-'*60)
    print("Getting page %d" % (pages))
    rtype, rdata, rmsgid, serverctrls = l.result3(msgid,resp_ctrl_classes=known_ldap_resp_ctrls)
    print('%d results' % len(rdata))
    print('serverctrls=',pprint.pprint(serverctrls))
    print('rdata=',pprint.pprint(rdata))
    pctrls = [
      c
      for c in serverctrls
      if c.controlType == SimplePagedResultsControl.controlType
    ]
    if pctrls:
        print('pctrls[0].size',repr(pctrls[0].size))
        print('pctrls[0].cookie',repr(pctrls[0].cookie))
        if pctrls[0].cookie:
            # Copy cookie from response control to request control
            req_ctrl.cookie = pctrls[0].cookie
            msgid = l.search_ext(
              base,
              ldap.SCOPE_SUBTREE,
              search_flt,
              attrlist=searchreq_attrlist,
              serverctrls=[req_ctrl]
            )
        else:
            break
    else:
        print("Warning:  Server ignores RFC 2696 control.")
        break

l.unbind_s()
