__author__ = 'rolandh'

from saml2 import md
from saml2.mdie import from_dict

from saml2 import saml

from saml2.extension import mdui
from saml2.extension import idpdisc
from saml2.extension import dri
from saml2.extension import mdattr
from saml2.extension import ui
import xmldsig
import xmlenc

ONTS = {
    saml.NAMESPACE: saml,
    mdui.NAMESPACE: mdui,
    mdattr.NAMESPACE: mdattr,
    dri.NAMESPACE: dri,
    ui.NAMESPACE: ui,
    idpdisc.NAMESPACE: idpdisc,
    md.NAMESPACE: md,
    xmldsig.NAMESPACE: xmldsig,
    xmlenc.NAMESPACE: xmlenc
}


def _eq(l1, l2):
    return set(l1) == set(l2)


def _class(cls):
    return "%s&%s" % (cls.c_namespace, cls.c_tag)


def test_construct_contact():
    c = from_dict({
        "__class__": _class(md.ContactPerson),
        "given_name": {"text": "Roland", "__class__": _class(md.GivenName)},
        "sur_name": {"text": "Hedberg", "__class__": _class(md.SurName)},
        "email_address": [{"text":"roland@catalogix.se",
                          "__class__": _class(md.EmailAddress)}],
    }, ONTS)

    print c
    assert c.given_name.text == "Roland"
    assert c.sur_name.text == "Hedberg"
    assert c.email_address[0].text == "roland@catalogix.se"
    assert _eq(c.keyswv(), ["given_name", "sur_name", "email_address"])
