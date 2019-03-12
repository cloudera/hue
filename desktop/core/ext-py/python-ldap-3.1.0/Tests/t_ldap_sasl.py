# -*- coding: utf-8 -*-
"""
Automatic tests for python-ldap's module ldap.sasl

See https://www.python-ldap.org/ for details.
"""
import os
import unittest

# Switch off processing .ldaprc or ldap.conf before importing _ldap
os.environ['LDAPNOINIT'] = '1'

from ldap.ldapobject import SimpleLDAPObject
import ldap.sasl
from slapdtest import SlapdTestCase
from slapdtest import requires_ldapi, requires_sasl, requires_tls


LDIF = """
dn: {suffix}
objectClass: dcObject
objectClass: organization
dc: {dc}
o: {dc}

dn: {rootdn}
objectClass: applicationProcess
objectClass: simpleSecurityObject
objectClass: uidObject
cn: {rootcn}
userPassword: {rootpw}
uid: {uid}

dn: cn={certuser},{suffix}
objectClass: applicationProcess
cn: {certuser}

"""


@requires_sasl()
class TestSasl(SlapdTestCase):
    ldap_object_class = SimpleLDAPObject
    # from Tests/certs/client.pem
    certuser = 'client'
    certsubject = "cn=client,ou=slapd-test,o=python-ldap,c=de"

    @classmethod
    def setUpClass(cls):
        super(TestSasl, cls).setUpClass()
        ldif = LDIF.format(
            suffix=cls.server.suffix,
            rootdn=cls.server.root_dn,
            rootcn=cls.server.root_cn,
            rootpw=cls.server.root_pw,
            dc=cls.server.suffix.split(',')[0][3:],
            certuser=cls.certuser,
            uid=os.geteuid(),
        )
        cls.server.ldapadd(ldif)

    @requires_ldapi()
    def test_external_ldapi(self):
        # EXTERNAL authentication with LDAPI (AF_UNIX)
        ldap_conn = self.ldap_object_class(self.server.ldapi_uri)

        auth = ldap.sasl.external("some invalid user")
        with self.assertRaises(ldap.INSUFFICIENT_ACCESS):
            ldap_conn.sasl_interactive_bind_s("", auth)

        auth = ldap.sasl.external("")
        ldap_conn.sasl_interactive_bind_s("", auth)
        self.assertEqual(
            ldap_conn.whoami_s().lower(),
            "dn:{}".format(self.server.root_dn.lower())
        )

    @requires_tls()
    def test_external_tlscert(self):
        ldap_conn = self.ldap_object_class(self.server.ldap_uri)
        ldap_conn.set_option(ldap.OPT_X_TLS_CACERTFILE, self.server.cafile)
        ldap_conn.set_option(ldap.OPT_X_TLS_CERTFILE, self.server.clientcert)
        ldap_conn.set_option(ldap.OPT_X_TLS_KEYFILE, self.server.clientkey)
        ldap_conn.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_HARD)
        ldap_conn.set_option(ldap.OPT_X_TLS_NEWCTX, 0)
        ldap_conn.start_tls_s()

        auth = ldap.sasl.external()
        ldap_conn.sasl_interactive_bind_s("", auth)
        self.assertEqual(
            ldap_conn.whoami_s().lower(),
            "dn:{}".format(self.certsubject)
        )

if __name__ == '__main__':
    unittest.main()
