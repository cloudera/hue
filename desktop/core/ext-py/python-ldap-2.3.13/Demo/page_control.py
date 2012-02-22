url = "ldap://localhost:1390/"
base = "dc=stroeder,dc=de"
search_flt = r'(objectClass=*)'
page_size = 10

import ldap,pprint
from ldap.controls import SimplePagedResultsControl

searchreq_attrlist=['cn','entryDN','entryUUID','mail','objectClass']

#ldap.set_option(ldap.OPT_DEBUG_LEVEL,255)
ldap.set_option(ldap.OPT_REFERRALS, 0)
l = ldap.initialize(url,trace_level=1)
l.protocol_version = 3
l.simple_bind_s("", "")

lc = SimplePagedResultsControl(
  ldap.LDAP_CONTROL_PAGE_OID,True,(page_size,'')
)

# Send search request
msgid = l.search_ext(
  base,
  ldap.SCOPE_SUBTREE,
  search_flt,
  attrlist=searchreq_attrlist,
  serverctrls=[lc]
)

pages = 0
while True:
    pages += 1
    print "Getting page %d" % (pages,)
    rtype, rdata, rmsgid, serverctrls = l.result3(msgid)
    print '%d results' % len(rdata)
#    pprint.pprint(rdata)
    pctrls = [
      c
      for c in serverctrls
      if c.controlType == ldap.LDAP_CONTROL_PAGE_OID
    ]
    if pctrls:
        est, cookie = pctrls[0].controlValue
        if cookie:
            lc.controlValue = (page_size, cookie)
            msgid = l.search_ext(
              base,
              ldap.SCOPE_SUBTREE,
              search_flt,
              attrlist=searchreq_attrlist,
              serverctrls=[lc]
            )
        else:
            break
    else:
        print "Warning:  Server ignores RFC 2696 control."
        break
