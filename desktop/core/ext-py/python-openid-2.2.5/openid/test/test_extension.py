from openid import extension
from openid import message

import unittest

class DummyExtension(extension.Extension):
    ns_uri = 'http://an.extension/'
    ns_alias = 'dummy'

    def getExtensionArgs(self):
        return {}

class ToMessageTest(unittest.TestCase):
    def test_OpenID1(self):
        oid1_msg = message.Message(message.OPENID1_NS)
        ext = DummyExtension()
        ext.toMessage(oid1_msg)
        namespaces = oid1_msg.namespaces
        self.failUnless(namespaces.isImplicit(DummyExtension.ns_uri))
        self.failUnlessEqual(
            DummyExtension.ns_uri,
            namespaces.getNamespaceURI(DummyExtension.ns_alias))
        self.failUnlessEqual(DummyExtension.ns_alias,
                             namespaces.getAlias(DummyExtension.ns_uri))

    def test_OpenID2(self):
        oid2_msg = message.Message(message.OPENID2_NS)
        ext = DummyExtension()
        ext.toMessage(oid2_msg)
        namespaces = oid2_msg.namespaces
        self.failIf(namespaces.isImplicit(DummyExtension.ns_uri))
        self.failUnlessEqual(
            DummyExtension.ns_uri,
            namespaces.getNamespaceURI(DummyExtension.ns_alias))
        self.failUnlessEqual(DummyExtension.ns_alias,
                             namespaces.getAlias(DummyExtension.ns_uri))
