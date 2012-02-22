"""
Performes various tests for module ldapurl
"""

import ldapurl
from ldapurl import *

print '\nTesting function isLDAPUrl():'
is_ldap_url_tests = {
  # Examples from RFC2255
  'ldap:///o=University%20of%20Michigan,c=US':1,
  'ldap://ldap.itd.umich.edu/o=University%20of%20Michigan,c=US':1,
  'ldap://ldap.itd.umich.edu/o=University%20of%20Michigan,':1,
  'ldap://host.com:6666/o=University%20of%20Michigan,':1,
  'ldap://ldap.itd.umich.edu/c=GB?objectClass?one':1,
  'ldap://ldap.question.com/o=Question%3f,c=US?mail':1,
  'ldap://ldap.netscape.com/o=Babsco,c=US??(int=%5c00%5c00%5c00%5c04)':1,
  'ldap:///??sub??bindname=cn=Manager%2co=Foo':1,
  'ldap:///??sub??!bindname=cn=Manager%2co=Foo':1,
  # More examples from various sources
  'ldap://ldap.nameflow.net:1389/c%3dDE':1,
  'ldap://root.openldap.org/dc=openldap,dc=org':1,
  'ldap://root.openldap.org/dc=openldap,dc=org':1,
  'ldap://x500.mh.se/o=Mitthogskolan,c=se????1.2.752.58.10.2=T.61':1,
  'ldp://root.openldap.org/dc=openldap,dc=org':0,
  'ldap://localhost:1389/ou%3DUnstructured%20testing%20tree%2Cdc%3Dstroeder%2Cdc%3Dcom??one':1,
}
for ldap_url in is_ldap_url_tests.keys():
  result_is_ldap_url = isLDAPUrl(ldap_url)
  if result_is_ldap_url !=is_ldap_url_tests[ldap_url]:
    print 'isLDAPUrl("%s") returns %d instead of %d.' % (
      repr(ldap_url),result_is_ldap_url,is_ldap_url_tests[ldap_url]
    )

print '\nTesting class LDAPUrl:'
parse_ldap_url_tests = [
  (
    'ldap://root.openldap.org/dc=openldap,dc=org',
    LDAPUrl(
      hostport='root.openldap.org',
      dn='dc=openldap,dc=org'
    )
  ),
  (
    'ldap://root.openldap.org/dc%3dboolean%2cdc%3dnet???%28objectClass%3d%2a%29',
    LDAPUrl(
      hostport='root.openldap.org',
      dn='dc=boolean,dc=net',
      filterstr='(objectClass=*)'
    )
  ),
  (
    'ldap://root.openldap.org/dc=openldap,dc=org??sub?',
    LDAPUrl(
      hostport='root.openldap.org',
      dn='dc=openldap,dc=org',
      scope=ldapurl.LDAP_SCOPE_SUBTREE
    )
  ),
  (
    'ldap://root.openldap.org/dc=openldap,dc=org??one?',
    LDAPUrl(
      hostport='root.openldap.org',
      dn='dc=openldap,dc=org',
      scope=ldapurl.LDAP_SCOPE_ONELEVEL
    )
  ),
  (
    'ldap://root.openldap.org/dc=openldap,dc=org??base?',
    LDAPUrl(
      hostport='root.openldap.org',
      dn='dc=openldap,dc=org',
      scope=ldapurl.LDAP_SCOPE_BASE
    )
  ),
  (
    'ldap://x500.mh.se/o=Mitthogskolan,c=se????1.2.752.58.10.2=T.61',
    LDAPUrl(
      hostport='x500.mh.se',
      dn='o=Mitthogskolan,c=se',
      extensions=LDAPUrlExtensions({
        '1.2.752.58.10.2':ldapurl.LDAPUrlExtension(
          critical=0,extype='1.2.752.58.10.2',exvalue='T.61'
        )
      })
    )
  ),
  (
    'ldap://localhost:12345/dc=stroeder,dc=com????!bindname=cn=Michael%2Cdc=stroeder%2Cdc=com,!X-BINDPW=secretpassword',
    LDAPUrl(
      hostport='localhost:12345',
      dn='dc=stroeder,dc=com',
      extensions=LDAPUrlExtensions({
        'bindname':LDAPUrlExtension(
          critical=1,extype='bindname',exvalue='cn=Michael,dc=stroeder,dc=com'
        ),
        'X-BINDPW':LDAPUrlExtension(
          critical=1,extype='X-BINDPW',exvalue='secretpassword'
        ),
      }),
    )
  ),
  (
    'ldap://localhost:54321/dc=stroeder,dc=com????bindname=cn=Michael%2Cdc=stroeder%2Cdc=com,X-BINDPW=secretpassword',
    LDAPUrl(
      hostport='localhost:54321',
      dn='dc=stroeder,dc=com',
      who='cn=Michael,dc=stroeder,dc=com',
      cred='secretpassword'
    )
  ),
  (
    'ldaps://localhost:12345/dc=stroeder,dc=com',
    LDAPUrl(
      urlscheme='ldaps',
      hostport='localhost:12345',
      dn='dc=stroeder,dc=com',
    ),
  ),
  (
    'ldapi://%2ftmp%2fopenldap2-1389/dc=stroeder,dc=com',
    LDAPUrl(
      urlscheme='ldapi',
      hostport='/tmp/openldap2-1389',
      dn='dc=stroeder,dc=com',
    ),
  ),
]

for ldap_url_str,test_ldap_url_obj in parse_ldap_url_tests:
#  print '\nTesting LDAP URL:',repr(ldap_url)
  ldap_url_obj = LDAPUrl(ldapUrl=ldap_url_str)
  print '#'*72
  print test_ldap_url_obj.unparse()
  if ldap_url_obj.__ne__(test_ldap_url_obj):
    print '-'*72
    print 'Parsing error! Attributes of LDAPUrl(%s) are:\n%s\ninstead of:\n%s' % (
      repr(ldap_url_str),
      repr(ldap_url_obj),
      repr(test_ldap_url_obj)
    )
  else:
    print 'Parsing ok'
    unparsed_ldap_url_str = test_ldap_url_obj.unparse()
    unparsed_ldap_url_obj = LDAPUrl(ldapUrl=unparsed_ldap_url_str)
    if unparsed_ldap_url_obj.__ne__(test_ldap_url_obj):
      print '-'*72
      print 'Unparsing error! Attributes of LDAPUrl(%s) are:\n%s\ninstead of:\n%s' % (
        repr(unparsed_ldap_url_str),
        repr(unparsed_ldap_url_obj),
        repr(test_ldap_url_obj)
      )
    else:
      print 'Unparsing ok'
