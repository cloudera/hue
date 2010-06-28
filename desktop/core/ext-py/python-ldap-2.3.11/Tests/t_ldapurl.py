import ldap, unittest
import urllib

from ldapurl import LDAPUrl

class MyLDAPUrl(LDAPUrl):
  attr2extype = {
    'who':'bindname',
    'cred':'X-BINDPW',
    'start_tls':'startTLS',
    'trace_level':'trace',
  }

def sort(l):
    "Returns a sorted copy of a list"
    l2 = [e for e in l]
    l2.sort()
    return l2

class TestLDAPUrl(unittest.TestCase):

    def assertNone(self, expr, msg=None):
        self.failIf(expr is not None, msg or ("%r" % expr))

    def test_combo(self):
        u = MyLDAPUrl("ldap://127.0.0.1:1234/dc=example,dc=com"
            + "?attr1,attr2,attr3"
            + "?sub"
            + "?" + urllib.quote("(objectClass=*)")
            + "?bindname=" + urllib.quote("cn=d,c=au")
            + ",X-BINDPW=" + urllib.quote("???")
            + ",trace=8"
        )
        self.assertEquals(u.urlscheme, "ldap")
        self.assertEquals(u.hostport, "127.0.0.1:1234")
        self.assertEquals(u.dn, "dc=example,dc=com")
        self.assertEquals(u.attrs, ["attr1","attr2","attr3"])
        self.assertEquals(u.scope, ldap.SCOPE_SUBTREE)
        self.assertEquals(u.filterstr, "(objectClass=*)")
        self.assertEquals(len(u.extensions), 3)
        self.assertEquals(u.who, "cn=d,c=au")
        self.assertEquals(u.cred, "???")
        self.assertEquals(u.trace_level, "8")

    def test_parse_default_hostport(self):
        u = LDAPUrl("ldap://")
        self.assertEquals(u.urlscheme, "ldap")
        self.assertEquals(u.hostport, "")

    def test_parse_empty_dn(self):
        u = LDAPUrl("ldap://")
        self.assertEquals(u.dn, "")
        u = LDAPUrl("ldap:///")
        self.assertEquals(u.dn, "")
        u = LDAPUrl("ldap:///?")
        self.assertEquals(u.dn, "")

    def test_parse_default_attrs(self):
        u = LDAPUrl("ldap://")
        self.assertNone(u.attrs)

    def test_parse_default_scope(self):
        u = LDAPUrl("ldap://")
        self.assertNone(u.scope)     # RFC4516 s3

    def test_parse_default_filter(self):
        u = LDAPUrl("ldap://")
        self.assertNone(u.filterstr) # RFC4516 s3

    def test_parse_default_extensions(self):
        u = LDAPUrl("ldap://")
        self.assertEquals(len(u.extensions), 0)

    def test_parse_schemes(self):
        u = LDAPUrl("ldap://")
        self.assertEquals(u.urlscheme, "ldap")
        u = LDAPUrl("ldapi://")
        self.assertEquals(u.urlscheme, "ldapi")
        u = LDAPUrl("ldaps://")
        self.assertEquals(u.urlscheme, "ldaps")

    def test_parse_hostport(self):
        u = LDAPUrl("ldap://a")
        self.assertEquals(u.hostport, "a")
        u = LDAPUrl("ldap://a.b")
        self.assertEquals(u.hostport, "a.b")
        u = LDAPUrl("ldap://a.")
        self.assertEquals(u.hostport, "a.")
        u = LDAPUrl("ldap://%61%62:%32/")
        self.assertEquals(u.hostport, "ab:2")
        u = LDAPUrl("ldap://[::1]/")
        self.assertEquals(u.hostport, "[::1]")
        u = LDAPUrl("ldap://[::1]")
        self.assertEquals(u.hostport, "[::1]")
        u = LDAPUrl("ldap://[::1]:123/")
        self.assertEquals(u.hostport, "[::1]:123")
        u = LDAPUrl("ldap://[::1]:123")
        self.assertEquals(u.hostport, "[::1]:123")

    def test_parse_dn(self):
        u = LDAPUrl("ldap:///")
        self.assertEquals(u.dn, "")
        u = LDAPUrl("ldap:///dn=foo")
        self.assertEquals(u.dn, "dn=foo")
        u = LDAPUrl("ldap:///dn=foo%2cdc=bar")
        self.assertEquals(u.dn, "dn=foo,dc=bar")
        u = LDAPUrl("ldap:///dn=foo%20bar")
        self.assertEquals(u.dn, "dn=foo bar")
        u = LDAPUrl("ldap:///dn=foo%2fbar")
        self.assertEquals(u.dn, "dn=foo/bar")
        u = LDAPUrl("ldap:///dn=foo%2fbar?")
        self.assertEquals(u.dn, "dn=foo/bar")
        u = LDAPUrl("ldap:///dn=foo%3f?")
        self.assertEquals(u.dn, "dn=foo?")
        u = LDAPUrl("ldap:///dn=foo%3f")
        self.assertEquals(u.dn, "dn=foo?")
        u = LDAPUrl("ldap:///dn=str%c3%b6der.com")
        self.assertEquals(u.dn, "dn=str\xc3\xb6der.com")

    def test_parse_attrs(self):
        u = LDAPUrl("ldap:///?")
        self.assertEquals(u.attrs, None)
        u = LDAPUrl("ldap:///??")
        self.assertEquals(u.attrs, None)
        u = LDAPUrl("ldap:///?*?")
        self.assertEquals(u.attrs, ['*'])
        u = LDAPUrl("ldap:///?*,*?")
        self.assertEquals(u.attrs, ['*','*'])
        u = LDAPUrl("ldap:///?a")
        self.assertEquals(u.attrs, ['a'])
        u = LDAPUrl("ldap:///?%61")
        self.assertEquals(u.attrs, ['a'])
        u = LDAPUrl("ldap:///?a,b")
        self.assertEquals(u.attrs, ['a','b'])
        u = LDAPUrl("ldap:///?a%3fb")
        self.assertEquals(u.attrs, ['a?b'])

    def test_parse_scope_default(self):
        u = LDAPUrl("ldap:///??")
        self.assertNone(u.scope) # on opposite to RFC4516 s3 for referral chasing
        u = LDAPUrl("ldap:///???")
        self.assertNone(u.scope) # on opposite to RFC4516 s3 for referral chasing

    def test_parse_scope(self):
        u = LDAPUrl("ldap:///??sub")
        self.assertEquals(u.scope, ldap.SCOPE_SUBTREE)
        u = LDAPUrl("ldap:///??sub?")
        self.assertEquals(u.scope, ldap.SCOPE_SUBTREE)
        u = LDAPUrl("ldap:///??base")
        self.assertEquals(u.scope, ldap.SCOPE_BASE)
        u = LDAPUrl("ldap:///??base?")
        self.assertEquals(u.scope, ldap.SCOPE_BASE)
        u = LDAPUrl("ldap:///??one")
        self.assertEquals(u.scope, ldap.SCOPE_ONELEVEL)
        u = LDAPUrl("ldap:///??one?")
        self.assertEquals(u.scope, ldap.SCOPE_ONELEVEL)

    def test_parse_filter(self):
        u = LDAPUrl("ldap:///???(cn=Bob)")
        self.assertEquals(u.filterstr, "(cn=Bob)")
        u = LDAPUrl("ldap:///???(cn=Bob)?")
        self.assertEquals(u.filterstr, "(cn=Bob)")
        u = LDAPUrl("ldap:///???(cn=Bob%20Smith)?")
        self.assertEquals(u.filterstr, "(cn=Bob Smith)")
        u = LDAPUrl("ldap:///???(cn=Bob/Smith)?")
        self.assertEquals(u.filterstr, "(cn=Bob/Smith)")
        u = LDAPUrl("ldap:///???(cn=Bob:Smith)?")
        self.assertEquals(u.filterstr, "(cn=Bob:Smith)")
        u = LDAPUrl("ldap:///???&(cn=Bob)(objectClass=user)?")
        self.assertEquals(u.filterstr, "&(cn=Bob)(objectClass=user)")
        u = LDAPUrl("ldap:///???|(cn=Bob)(objectClass=user)?")
        self.assertEquals(u.filterstr, "|(cn=Bob)(objectClass=user)")
        u = LDAPUrl("ldap:///???(cn=Q%3f)?")
        self.assertEquals(u.filterstr, "(cn=Q?)")
        u = LDAPUrl("ldap:///???(cn=Q%3f)")
        self.assertEquals(u.filterstr, "(cn=Q?)")
        u = LDAPUrl("ldap:///???(sn=Str%c3%b6der)") # (possibly bad?)
        self.assertEquals(u.filterstr, "(sn=Str\xc3\xb6der)")
        u = LDAPUrl("ldap:///???(sn=Str\\c3\\b6der)")
        self.assertEquals(u.filterstr, "(sn=Str\\c3\\b6der)") # (recommended)
        u = LDAPUrl("ldap:///???(cn=*\\2a*)")
        self.assertEquals(u.filterstr, "(cn=*\\2a*)")
        u = LDAPUrl("ldap:///???(cn=*%5c2a*)")
        self.assertEquals(u.filterstr, "(cn=*\\2a*)")

    def test_parse_extensions(self):
        u = LDAPUrl("ldap:///????")
        self.assertNone(u.extensions)
        self.assertNone(u.who)
        u = LDAPUrl("ldap:///????bindname=cn=root")
        self.assertEquals(len(u.extensions), 1)
        self.assertEquals(u.who, "cn=root")
        u = LDAPUrl("ldap:///????!bindname=cn=root")
        self.assertEquals(len(u.extensions), 1)
        self.assertEquals(u.who, "cn=root")
        u = LDAPUrl("ldap:///????bindname=%3f,X-BINDPW=%2c")
        self.assertEquals(len(u.extensions), 2)
        self.assertEquals(u.who, "?")
        self.assertEquals(u.cred, ",")

    def test_parse_extensions_nulls(self):
        u = LDAPUrl("ldap:///????bindname=%00name")
        self.assertEquals(u.who, "\0name")

    def test_parse_extensions_5questions(self):
        u = LDAPUrl("ldap:///????bindname=?")
        self.assertEquals(len(u.extensions), 1)
        self.assertEquals(u.who, "?")

    def test_parse_extensions_novalue(self):
        u = LDAPUrl("ldap:///????bindname")
        self.assertEquals(len(u.extensions), 1)
        self.assertNone(u.who)

    def test_bad_urls(self):
        for bad in ("", "ldap:", "ldap:/", ":///", "://", "///", "//", "/",
                "ldap:///?????",       # extension can't start with '?'
                "LDAP://", "invalid://", "ldap:///??invalid",
                #XXX-- the following should raise exceptions!
                "ldap://:389/",         # [host [COLON port]]
                "ldap://a:/",           # [host [COLON port]]
                "ldap://%%%/",          # invalid URL encoding
                "ldap:///?,",           # attrdesc *(COMMA attrdesc)
                "ldap:///?a,",          # attrdesc *(COMMA attrdesc)
                "ldap:///?,a",          # attrdesc *(COMMA attrdesc)
                "ldap:///?a,,b",        # attrdesc *(COMMA attrdesc)
                "ldap://%00/",          # RFC4516 2.1
                "ldap:///%00",          # RFC4516 2.1
                "ldap:///?%00",         # RFC4516 2.1
                "ldap:///??%00",        # RFC4516 2.1
                "ldap:///????0=0",      # extype must start with Alpha
                "ldap:///????a_b=0",    # extype contains only [-a-zA-Z0-9]
                "ldap:///????!!a=0",    # only one exclamation allowed
        ):
            try: 
                LDAPUrl(bad)
                self.fail("should have raised ValueError: %r" % bad)
            except ValueError:
                pass

if __name__ == '__main__':
    unittest.main()
