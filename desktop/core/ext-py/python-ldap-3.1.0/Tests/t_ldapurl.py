# -*- coding: utf-8 -*-
"""
Automatic tests for python-ldap's module ldapurl

See https://www.python-ldap.org/ for details.
"""

from __future__ import unicode_literals

import os
import unittest

# Switch off processing .ldaprc or ldap.conf before importing _ldap
os.environ['LDAPNOINIT'] = '1'

from ldap.compat import quote

import ldapurl
from ldapurl import LDAPUrl


class MyLDAPUrl(LDAPUrl):
    attr2extype = {
        'who':'bindname',
        'cred':'X-BINDPW',
        'start_tls':'startTLS',
        'trace_level':'trace',
    }


class TestIsLDAPUrl(unittest.TestCase):

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
        'ldaps://ldap.example.com/c%3dDE':1,
        'ldapi:///dc=stroeder,dc=de????x-saslmech=EXTERNAL':1,
    }

    def test_isLDAPUrl(self):
        for ldap_url, expected in self.is_ldap_url_tests.items():
            result = ldapurl.isLDAPUrl(ldap_url)
            self.assertEqual(
                result, expected,
                'isLDAPUrl("%s") returns %d instead of %d.' % (
                    ldap_url, result, expected,
                )
            )


class TestParseLDAPUrl(unittest.TestCase):

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
            extensions=ldapurl.LDAPUrlExtensions({
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
            extensions=ldapurl.LDAPUrlExtensions({
                'bindname':ldapurl.LDAPUrlExtension(
                critical=1,extype='bindname',exvalue='cn=Michael,dc=stroeder,dc=com'
                ),
                'X-BINDPW':ldapurl.LDAPUrlExtension(
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

    def test_ldapurl(self):
        for ldap_url_str,test_ldap_url_obj in self.parse_ldap_url_tests:
            ldap_url_obj = LDAPUrl(ldapUrl=ldap_url_str)
            self.assertEqual(
                ldap_url_obj, test_ldap_url_obj,
                'Attributes of LDAPUrl(%s) are:\n%s\ninstead of:\n%s' % (
                    repr(ldap_url_str),
                    repr(ldap_url_obj),
                    repr(test_ldap_url_obj),
                )
            )
            unparsed_ldap_url_str = test_ldap_url_obj.unparse()
            unparsed_ldap_url_obj = LDAPUrl(ldapUrl=unparsed_ldap_url_str)
            self.assertEqual(
                unparsed_ldap_url_obj, test_ldap_url_obj,
                'Attributes of LDAPUrl(%s) are:\n%s\ninstead of:\n%s' % (
                    repr(unparsed_ldap_url_str),
                    repr(unparsed_ldap_url_obj),
                    repr(test_ldap_url_obj),
                )
            )


class TestLDAPUrl(unittest.TestCase):
    def test_combo(self):
        u = MyLDAPUrl(
            "ldap://127.0.0.1:1234/dc=example,dc=com"
            + "?attr1,attr2,attr3"
            + "?sub"
            + "?" + quote("(objectClass=*)")
            + "?bindname=" + quote("cn=d,c=au")
            + ",X-BINDPW=" + quote("???")
            + ",trace=8"
        )
        self.assertEqual(u.urlscheme, "ldap")
        self.assertEqual(u.hostport, "127.0.0.1:1234")
        self.assertEqual(u.dn, "dc=example,dc=com")
        self.assertEqual(u.attrs, ["attr1","attr2","attr3"])
        self.assertEqual(u.scope, ldapurl.LDAP_SCOPE_SUBTREE)
        self.assertEqual(u.filterstr, "(objectClass=*)")
        self.assertEqual(len(u.extensions), 3)
        self.assertEqual(u.who, "cn=d,c=au")
        self.assertEqual(u.cred, "???")
        self.assertEqual(u.trace_level, "8")

    def test_parse_default_hostport(self):
        u = LDAPUrl("ldap://")
        self.assertEqual(u.urlscheme, "ldap")
        self.assertEqual(u.hostport, "")

    def test_parse_empty_dn(self):
        u = LDAPUrl("ldap://")
        self.assertEqual(u.dn, "")
        u = LDAPUrl("ldap:///")
        self.assertEqual(u.dn, "")
        u = LDAPUrl("ldap:///?")
        self.assertEqual(u.dn, "")

    def test_parse_default_attrs(self):
        u = LDAPUrl("ldap://")
        self.assertIsNone(u.attrs)

    def test_parse_default_scope(self):
        u = LDAPUrl("ldap://")
        self.assertIsNone(u.scope)     # RFC4516 s3

    def test_parse_default_filter(self):
        u = LDAPUrl("ldap://")
        self.assertIsNone(u.filterstr) # RFC4516 s3

    def test_parse_default_extensions(self):
        u = LDAPUrl("ldap://")
        self.assertEqual(len(u.extensions), 0)

    def test_parse_schemes(self):
        u = LDAPUrl("ldap://")
        self.assertEqual(u.urlscheme, "ldap")
        u = LDAPUrl("ldapi://")
        self.assertEqual(u.urlscheme, "ldapi")
        u = LDAPUrl("ldaps://")
        self.assertEqual(u.urlscheme, "ldaps")

    def test_parse_hostport(self):
        u = LDAPUrl("ldap://a")
        self.assertEqual(u.hostport, "a")
        u = LDAPUrl("ldap://a.b")
        self.assertEqual(u.hostport, "a.b")
        u = LDAPUrl("ldap://a.")
        self.assertEqual(u.hostport, "a.")
        u = LDAPUrl("ldap://%61%62:%32/")
        self.assertEqual(u.hostport, "ab:2")
        u = LDAPUrl("ldap://[::1]/")
        self.assertEqual(u.hostport, "[::1]")
        u = LDAPUrl("ldap://[::1]")
        self.assertEqual(u.hostport, "[::1]")
        u = LDAPUrl("ldap://[::1]:123/")
        self.assertEqual(u.hostport, "[::1]:123")
        u = LDAPUrl("ldap://[::1]:123")
        self.assertEqual(u.hostport, "[::1]:123")

    def test_parse_dn(self):
        u = LDAPUrl("ldap:///")
        self.assertEqual(u.dn, "")
        u = LDAPUrl("ldap:///dn=foo")
        self.assertEqual(u.dn, "dn=foo")
        u = LDAPUrl("ldap:///dn=foo%2cdc=bar")
        self.assertEqual(u.dn, "dn=foo,dc=bar")
        u = LDAPUrl("ldap:///dn=foo%20bar")
        self.assertEqual(u.dn, "dn=foo bar")
        u = LDAPUrl("ldap:///dn=foo%2fbar")
        self.assertEqual(u.dn, "dn=foo/bar")
        u = LDAPUrl("ldap:///dn=foo%2fbar?")
        self.assertEqual(u.dn, "dn=foo/bar")
        u = LDAPUrl("ldap:///dn=foo%3f?")
        self.assertEqual(u.dn, "dn=foo?")
        u = LDAPUrl("ldap:///dn=foo%3f")
        self.assertEqual(u.dn, "dn=foo?")
        u = LDAPUrl("ldap:///dn=str%c3%b6der.com")
        self.assertEqual(u.dn, "dn=str\xf6der.com")

    def test_parse_attrs(self):
        u = LDAPUrl("ldap:///?")
        self.assertIsNone(u.attrs)
        u = LDAPUrl("ldap:///??")
        self.assertIsNone(u.attrs)
        u = LDAPUrl("ldap:///?*?")
        self.assertEqual(u.attrs, ['*'])
        u = LDAPUrl("ldap:///?*,*?")
        self.assertEqual(u.attrs, ['*','*'])
        u = LDAPUrl("ldap:///?a")
        self.assertEqual(u.attrs, ['a'])
        u = LDAPUrl("ldap:///?%61")
        self.assertEqual(u.attrs, ['a'])
        u = LDAPUrl("ldap:///?a,b")
        self.assertEqual(u.attrs, ['a','b'])
        u = LDAPUrl("ldap:///?a%3fb")
        self.assertEqual(u.attrs, ['a?b'])

    def test_parse_scope_default(self):
        u = LDAPUrl("ldap:///??")
        self.assertIsNone(u.scope) # on opposite to RFC4516 s3 for referral chasing
        u = LDAPUrl("ldap:///???")
        self.assertIsNone(u.scope) # on opposite to RFC4516 s3 for referral chasing

    def test_parse_scope(self):
        u = LDAPUrl("ldap:///??sub")
        self.assertEqual(u.scope, ldapurl.LDAP_SCOPE_SUBTREE)
        u = LDAPUrl("ldap:///??sub?")
        self.assertEqual(u.scope, ldapurl.LDAP_SCOPE_SUBTREE)
        u = LDAPUrl("ldap:///??base")
        self.assertEqual(u.scope, ldapurl.LDAP_SCOPE_BASE)
        u = LDAPUrl("ldap:///??base?")
        self.assertEqual(u.scope, ldapurl.LDAP_SCOPE_BASE)
        u = LDAPUrl("ldap:///??one")
        self.assertEqual(u.scope, ldapurl.LDAP_SCOPE_ONELEVEL)
        u = LDAPUrl("ldap:///??one?")
        self.assertEqual(u.scope, ldapurl.LDAP_SCOPE_ONELEVEL)
        u = LDAPUrl("ldap:///??subordinates")
        self.assertEqual(u.scope, ldapurl.LDAP_SCOPE_SUBORDINATES)
        u = LDAPUrl("ldap:///??subordinates?")
        self.assertEqual(u.scope, ldapurl.LDAP_SCOPE_SUBORDINATES)

    def test_parse_filter(self):
        u = LDAPUrl("ldap:///???(cn=Bob)")
        self.assertEqual(u.filterstr, "(cn=Bob)")
        u = LDAPUrl("ldap:///???(cn=Bob)?")
        self.assertEqual(u.filterstr, "(cn=Bob)")
        u = LDAPUrl("ldap:///???(cn=Bob%20Smith)?")
        self.assertEqual(u.filterstr, "(cn=Bob Smith)")
        u = LDAPUrl("ldap:///???(cn=Bob/Smith)?")
        self.assertEqual(u.filterstr, "(cn=Bob/Smith)")
        u = LDAPUrl("ldap:///???(cn=Bob:Smith)?")
        self.assertEqual(u.filterstr, "(cn=Bob:Smith)")
        u = LDAPUrl("ldap:///???&(cn=Bob)(objectClass=user)?")
        self.assertEqual(u.filterstr, "&(cn=Bob)(objectClass=user)")
        u = LDAPUrl("ldap:///???|(cn=Bob)(objectClass=user)?")
        self.assertEqual(u.filterstr, "|(cn=Bob)(objectClass=user)")
        u = LDAPUrl("ldap:///???(cn=Q%3f)?")
        self.assertEqual(u.filterstr, "(cn=Q?)")
        u = LDAPUrl("ldap:///???(cn=Q%3f)")
        self.assertEqual(u.filterstr, "(cn=Q?)")
        u = LDAPUrl("ldap:///???(sn=Str%c3%b6der)") # (possibly bad?)
        self.assertEqual(u.filterstr, "(sn=Str\xf6der)")
        u = LDAPUrl("ldap:///???(sn=Str\\c3\\b6der)")
        self.assertEqual(u.filterstr, "(sn=Str\\c3\\b6der)") # (recommended)
        u = LDAPUrl("ldap:///???(cn=*\\2a*)")
        self.assertEqual(u.filterstr, "(cn=*\\2a*)")
        u = LDAPUrl("ldap:///???(cn=*%5c2a*)")
        self.assertEqual(u.filterstr, "(cn=*\\2a*)")

    def test_parse_extensions(self):
        u = LDAPUrl("ldap:///????")
        self.assertIsNone(u.extensions)
        self.assertIsNone(u.who)
        u = LDAPUrl("ldap:///????bindname=cn=root")
        self.assertEqual(len(u.extensions), 1)
        self.assertEqual(u.who, "cn=root")
        u = LDAPUrl("ldap:///????!bindname=cn=root")
        self.assertEqual(len(u.extensions), 1)
        self.assertEqual(u.who, "cn=root")
        u = LDAPUrl("ldap:///????bindname=%3f,X-BINDPW=%2c")
        self.assertEqual(len(u.extensions), 2)
        self.assertEqual(u.who, "?")
        self.assertEqual(u.cred, ",")

    def test_parse_extensions_nulls(self):
        u = LDAPUrl("ldap:///????bindname=%00name")
        self.assertEqual(u.who, "\0name")

    def test_parse_extensions_5questions(self):
        u = LDAPUrl("ldap:///????bindname=?")
        self.assertEqual(len(u.extensions), 1)
        self.assertEqual(u.who, "?")

    def test_parse_extensions_novalue(self):
        u = LDAPUrl("ldap:///????bindname")
        self.assertEqual(len(u.extensions), 1)
        self.assertIsNone(u.who)

    @unittest.expectedFailure
    def test_bad_urls(self):
        failed_urls = []
        for bad in (
                "",
                "ldap:",
                "ldap:/",
                ":///",
                "://",
                "///",
                "//",
                "/",
                "ldap:///?????",       # extension can't start with '?'
                "LDAP://",
                "invalid://",
                "ldap:///??invalid",
                #XXX-- the following should raise exceptions!
                "ldap://:389/",         # [host [COLON port]]
                "ldap://a:/",           # [host [COLON port]]
                r"ldap://%%%/",          # invalid URL encoding
                "ldap:///?,",           # attrdesc *(COMMA attrdesc)
                "ldap:///?a,",          # attrdesc *(COMMA attrdesc)
                "ldap:///?,a",          # attrdesc *(COMMA attrdesc)
                "ldap:///?a,,b",        # attrdesc *(COMMA attrdesc)
                r"ldap://%00/",         # RFC4516 2.1
                r"ldap:///%00",         # RFC4516 2.1
                r"ldap:///?%00",        # RFC4516 2.1
                r"ldap:///??%00",       # RFC4516 2.1
                "ldap:///????0=0",      # extype must start with Alpha
                "ldap:///????a_b=0",    # extype contains only [-a-zA-Z0-9]
                "ldap:///????!!a=0",    # only one exclamation allowed
        ):
            try:
                LDAPUrl(bad)
            except ValueError:
                pass
            else:
                failed_urls.append(bad)
        if failed_urls:
          self.fail("These LDAP URLs should have raised ValueError: %r" % failed_urls)

if __name__ == '__main__':
    unittest.main()
