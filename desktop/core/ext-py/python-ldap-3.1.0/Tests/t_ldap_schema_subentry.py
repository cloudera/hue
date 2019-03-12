# -*- coding: utf-8 -*-
"""
Automatic tests for python-ldap's class ldap.schema.SubSchema

See https://www.python-ldap.org/ for details.
"""

import os
import unittest

# Switch off processing .ldaprc or ldap.conf before importing _ldap
os.environ['LDAPNOINIT'] = '1'
import ldap

import ldif
from ldap.ldapobject import SimpleLDAPObject
import ldap.schema
from ldap.schema.models import ObjectClass
from slapdtest import SlapdTestCase, requires_ldapi

HERE = os.path.abspath(os.path.dirname(__file__))

TEST_SUBSCHEMA_FILES = (
    os.path.join(HERE, 'data', 'subschema-ipa.demo1.freeipa.org.ldif'),
    os.path.join(HERE, 'data', 'subschema-openldap-all.ldif'),
)


class TestSubschemaLDIF(unittest.TestCase):
    """
    test ldap.schema.SubSchema with subschema subentries read from LDIF files
    """

    def test_subschema_file(self):
        for test_file in TEST_SUBSCHEMA_FILES:
            # Read and parse LDIF file
            with open(test_file, 'rb') as ldif_file:
                ldif_parser = ldif.LDIFRecordList(ldif_file,max_entries=1)
                ldif_parser.parse()
            _, subschema_subentry = ldif_parser.all_records[0]
            sub_schema = ldap.schema.SubSchema(subschema_subentry)

            # Smoke-check for listall() and attribute_types()
            for objclass in sub_schema.listall(ObjectClass):
                must, may = sub_schema.attribute_types([objclass])

                for oid, attributetype in must.items():
                    self.assertEqual(attributetype.oid, oid)
                for oid, attributetype in may.items():
                    self.assertEqual(attributetype.oid, oid)


class TestSubschemaUrlfetch(unittest.TestCase):
    def test_urlfetch_file(self):
        freeipa_uri = 'file://{}'.format(TEST_SUBSCHEMA_FILES[0])
        dn, schema = ldap.schema.urlfetch(freeipa_uri)
        self.assertEqual(dn, 'cn=schema')
        self.assertIsInstance(schema, ldap.schema.subentry.SubSchema)
        obj = schema.get_obj(ObjectClass, '2.5.6.9')
        self.assertEqual(
            str(obj),
            "( 2.5.6.9 NAME 'groupOfNames' SUP top STRUCTURAL MUST cn "
            "MAY ( member $ businessCategory $ seeAlso $ owner $ ou $ o "
            "$ description ) )"
        )


class TestSubschemaUrlfetchSlapd(SlapdTestCase):
    ldap_object_class = SimpleLDAPObject

    def assertSlapdSchema(self, dn, schema):
        self.assertEqual(dn, 'cn=Subschema')
        self.assertIsInstance(schema, ldap.schema.subentry.SubSchema)
        obj = schema.get_obj(ObjectClass, '1.3.6.1.1.3.1')
        self.assertEqual(
            str(obj),
            "( 1.3.6.1.1.3.1 NAME 'uidObject' DESC 'RFC2377: uid object' "
            "SUP top AUXILIARY MUST uid )"
        )
        entries = schema.ldap_entry()
        self.assertIsInstance(entries, dict)
        self.assertEqual(sorted(entries), [
            'attributeTypes', 'ldapSyntaxes', 'matchingRuleUse',
            'matchingRules', 'objectClasses',
        ])

    def test_urlfetch_ldap(self):
        dn, schema = ldap.schema.urlfetch(self.server.ldap_uri)
        self.assertSlapdSchema(dn, schema)

    @requires_ldapi()
    def test_urlfetch_ldapi(self):
        dn, schema = ldap.schema.urlfetch(self.server.ldapi_uri)
        self.assertSlapdSchema(dn, schema)


if __name__ == '__main__':
    unittest.main()
