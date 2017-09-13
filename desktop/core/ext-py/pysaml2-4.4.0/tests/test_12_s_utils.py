# !/usr/bin/env python
# -*- coding: utf-8 -*-

import base64

import six

from saml2 import s_utils as utils
from saml2 import saml
from saml2 import samlp
from saml2.argtree import set_arg

from saml2.s_utils import do_attribute_statement
from saml2.saml import Attribute, Subject
from saml2.saml import NAME_FORMAT_URI

from py.test import raises

from pathutils import full_path

XML_HEADER = '<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n'

SUCCESS_STATUS_NO_HEADER = (
    '<ns0:Status xmlns:ns0="urn:oasis:names:tc:SAML:2.0:protocol"><ns0'
    ':StatusCode '
    'Value="urn:oasis:names:tc:SAML:2.0:status:Success" /></ns0:Status>')
SUCCESS_STATUS = '%s%s' % (XML_HEADER, SUCCESS_STATUS_NO_HEADER)

ERROR_STATUS_NO_HEADER = (
    '<ns0:Status xmlns:ns0="urn:oasis:names:tc:SAML:2.0:protocol"><ns0'
    ':StatusCode '
    'Value="urn:oasis:names:tc:SAML:2.0:status:Responder"><ns0:StatusCode '
    'Value="urn:oasis:names:tc:SAML:2.0:status:UnknownPrincipal" '
    '/></ns0:StatusCode><ns0:StatusMessage>Error resolving '
    'principal</ns0:StatusMessage></ns0:Status>')

ERROR_STATUS_NO_HEADER_EMPTY = (
    '<ns0:Status xmlns:ns0="urn:oasis:names:tc:SAML:2.0:protocol"><ns0'
    ':StatusCode '
    'Value="urn:oasis:names:tc:SAML:2.0:status:Responder"><ns0:StatusCode '
    'Value="urn:oasis:names:tc:SAML:2.0:status:UnknownPrincipal" '
    '/></ns0:StatusCode></ns0:Status>')

ERROR_STATUS = '%s%s' % (XML_HEADER, ERROR_STATUS_NO_HEADER)
ERROR_STATUS_EMPTY = '%s%s' % (XML_HEADER, ERROR_STATUS_NO_HEADER_EMPTY)


def _eq(l1, l2):
    return set(l1) == set(l2)


def _oeq(l1, l2):
    if len(l1) != len(l2):
        print("Different number of items")
        return False
    for item in l1:
        if item not in l2:
            print("%s not in l2" % (item,))
            for ite in l2:
                print("\t%s" % (ite,))
            return False
    return True


def test_inflate_then_deflate():
    txt = """Selma Lagerlöf (1858-1940) was born in Östra Emterwik, Värmland,
    Sweden. She was brought up on Mårbacka, the family estate, which she did 
    not leave until 1881, when she went to a teachers' college at Stockholm"""
    if not isinstance(txt, six.binary_type):
        txt = txt.encode('utf-8')

    interm = utils.deflate_and_base64_encode(txt)
    bis = utils.decode_base64_and_inflate(interm)
    if not isinstance(bis, six.binary_type):
        bis = bis.encode('utf-8')
    assert bis == txt


def test_status_success():
    status = utils.success_status_factory()
    status_text = "%s" % status
    assert status_text in (SUCCESS_STATUS_NO_HEADER, SUCCESS_STATUS)
    assert status.status_code.value == samlp.STATUS_SUCCESS


def test_error_status():
    status = utils.status_message_factory("Error resolving principal",
                                          samlp.STATUS_UNKNOWN_PRINCIPAL,
                                          samlp.STATUS_RESPONDER)

    status_text = "%s" % status
    print(status_text)
    assert status_text in (ERROR_STATUS_NO_HEADER, ERROR_STATUS)


def test_status_from_exception():
    e = utils.UnknownPrincipal("Error resolving principal")
    stat = utils.error_status_factory(e)
    status_text = "%s" % stat
    print(status_text)
    assert status_text in (ERROR_STATUS_NO_HEADER, ERROR_STATUS)


def test_status_from_tuple():
    stat = utils.error_status_factory((samlp.STATUS_UNKNOWN_PRINCIPAL,
                                       'Error resolving principal'))
    status_text = "%s" % stat
    assert status_text in (ERROR_STATUS_NO_HEADER, ERROR_STATUS)


def test_status_from_tuple_empty_message():
    stat = utils.error_status_factory((samlp.STATUS_UNKNOWN_PRINCIPAL, None))
    status_text = "%s" % stat
    assert status_text in (ERROR_STATUS_EMPTY, ERROR_STATUS_NO_HEADER_EMPTY)


def test_attribute_sn():
    attr = utils.do_attributes({"surName": ("Jeter", "")})
    assert len(attr) == 1
    print(attr)
    inst = attr[0]
    assert inst.name == "surName"
    assert len(inst.attribute_value) == 1
    av = inst.attribute_value[0]
    assert av.text == "Jeter"


def test_attribute_age():
    attr = utils.do_attributes({"age": (37, "")})

    assert len(attr) == 1
    inst = attr[0]
    print(inst)
    assert inst.name == "age"
    assert len(inst.attribute_value) == 1
    av = inst.attribute_value[0]
    assert av.text == "37"
    assert av.get_type() == "xs:integer"


def test_attribute_onoff():
    attr = utils.do_attributes({"onoff": (False, "")})

    assert len(attr) == 1
    inst = attr[0]
    print(inst)
    assert inst.name == "onoff"
    assert len(inst.attribute_value) == 1
    av = inst.attribute_value[0]
    assert av.text == "false"
    assert av.get_type() == "xs:boolean"


def test_attribute_base64():
    txt = "Selma Lagerlöf"
    if not isinstance(txt, six.binary_type):
        txt = txt.encode("utf-8")
    b64sl = base64.b64encode(txt).decode('ascii')
    attr = utils.do_attributes({"name": (b64sl, "xs:base64Binary")})

    assert len(attr) == 1
    inst = attr[0]
    print(inst)
    assert inst.name == "name"
    assert len(inst.attribute_value) == 1
    av = inst.attribute_value[0]
    assert av.get_type() == "xs:base64Binary"
    assert av.text.strip() == b64sl


def test_attribute_statement():
    statement = do_attribute_statement({"surName": ("Jeter", ""),
                                        "givenName": ("Derek", "")})
    print(statement)
    assert statement.keyswv() == ["attribute"]
    assert len(statement.attribute) == 2
    attr0 = statement.attribute[0]
    assert _eq(attr0.keyswv(), ["name", "attribute_value", "name_format"])
    assert len(attr0.attribute_value) == 1
    attr1 = statement.attribute[1]
    assert _eq(attr1.keyswv(), ["name", "attribute_value", "name_format"])
    assert len(attr1.attribute_value) == 1
    if attr0.name == "givenName":
        assert attr0.attribute_value[0].text == "Derek"
        assert attr1.name == "surName"
        assert attr1.attribute_value[0].text == "Jeter"
    else:
        assert attr0.name == "surName"
        assert attr0.attribute_value[0].text == "Jeter"
        assert attr1.name == "givenName"
        assert attr1.attribute_value[0].text == "Derek"


def test_audience():
    aud_restr = utils.factory(saml.AudienceRestriction,
                              audience=utils.factory(saml.Audience,
                                                     text="urn:foo:bar"))

    assert aud_restr.keyswv() == ["audience"]
    assert aud_restr.audience.text == "urn:foo:bar"


def test_conditions():
    conditions = utils.factory(saml.Conditions,
                               not_before="2009-10-30T07:58:10.852Z",
                               not_on_or_after="2009-10-30T08:03:10.852Z",
                               audience_restriction=[
                                   utils.factory(saml.AudienceRestriction,
                                                 audience=utils.factory(
                                                     saml.Audience,
                                                     text="urn:foo:bar"))])

    assert _eq(conditions.keyswv(), ["not_before", "not_on_or_after",
                                     "audience_restriction"])
    assert conditions.not_before == "2009-10-30T07:58:10.852Z"
    assert conditions.not_on_or_after == "2009-10-30T08:03:10.852Z"
    assert conditions.audience_restriction[0].audience.text == "urn:foo:bar"


def test_value_1():
    # FriendlyName="givenName" Name="urn:oid:2.5.4.42"
    # NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"
    attribute = utils.factory(saml.Attribute, name="urn:oid:2.5.4.42",
                              name_format=NAME_FORMAT_URI)
    assert _eq(attribute.keyswv(), ["name", "name_format"])
    assert attribute.name == "urn:oid:2.5.4.42"
    assert attribute.name_format == saml.NAME_FORMAT_URI


def test_value_2():
    attribute = utils.factory(saml.Attribute, name="urn:oid:2.5.4.42",
                              name_format=NAME_FORMAT_URI,
                              friendly_name="givenName")
    assert _eq(attribute.keyswv(), ["name", "name_format", "friendly_name"])
    assert attribute.name == "urn:oid:2.5.4.42"
    assert attribute.name_format == NAME_FORMAT_URI
    assert attribute.friendly_name == "givenName"


def test_value_3():
    attribute = utils.factory(saml.Attribute,
                              attribute_value=[utils.factory(
                                  saml.AttributeValue, text="Derek")],
                              name="urn:oid:2.5.4.42",
                              name_format=NAME_FORMAT_URI,
                              friendly_name="givenName")

    assert _eq(attribute.keyswv(), ["name", "name_format",
                                    "friendly_name", "attribute_value"])
    assert attribute.name == "urn:oid:2.5.4.42"
    assert attribute.name_format == NAME_FORMAT_URI
    assert attribute.friendly_name == "givenName"
    assert len(attribute.attribute_value) == 1
    assert attribute.attribute_value[0].text == "Derek"


def test_value_4():
    attribute = utils.factory(saml.Attribute,
                              attribute_value=[utils.factory(
                                  saml.AttributeValue, text="Derek")],
                              friendly_name="givenName")

    assert _eq(attribute.keyswv(), ["friendly_name", "attribute_value",
                                    "name_format"])
    assert attribute.friendly_name == "givenName"
    assert len(attribute.attribute_value) == 1
    assert attribute.attribute_value[0].text == "Derek"


def test_do_attribute_statement_0():
    statement = do_attribute_statement({"vo_attr": ("foobar", "")})

    assert statement.keyswv() == ["attribute"]
    assert len(statement.attribute) == 1
    attr0 = statement.attribute[0]
    assert _eq(attr0.keyswv(), ["name", "attribute_value", "name_format"])
    assert attr0.name == "vo_attr"
    assert len(attr0.attribute_value) == 1
    assert attr0.attribute_value[0].text == "foobar"


def test_do_attribute_statement():
    statement = do_attribute_statement({"surName": ("Jeter", ""),
                                        "givenName": (["Derek",
                                                       "Sanderson"], "")})

    assert statement.keyswv() == ["attribute"]
    assert len(statement.attribute) == 2
    attr0 = statement.attribute[0]
    assert _eq(attr0.keyswv(), ["name", "attribute_value", "name_format"])
    attr1 = statement.attribute[1]
    assert _eq(attr1.keyswv(), ["name", "attribute_value", "name_format"])
    if attr0.name == "givenName":
        assert len(attr0.attribute_value) == 2
        assert _eq([av.text for av in attr0.attribute_value],
                   ["Derek", "Sanderson"])
        assert attr1.name == "surName"
        assert attr1.attribute_value[0].text == "Jeter"
        assert len(attr1.attribute_value) == 1
    else:
        assert attr0.name == "surName"
        assert attr0.attribute_value[0].text == "Jeter"
        assert len(attr0.attribute_value) == 1
        assert attr1.name == "givenName"
        assert len(attr1.attribute_value) == 2
        assert _eq([av.text for av in attr1.attribute_value],
                   ["Derek", "Sanderson"])


def test_do_attribute_statement_multi():
    statement = do_attribute_statement(
        {("urn:oid:1.3.6.1.4.1.5923.1.1.1.7",
          "urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
          "eduPersonEntitlement"): ("Jeter", "")})

    assert statement.keyswv() == ["attribute"]
    assert len(statement.attribute)
    assert _eq(statement.attribute[0].keyswv(),
               ["name", "name_format", "friendly_name", "attribute_value"])
    attribute = statement.attribute[0]
    assert attribute.name == "urn:oid:1.3.6.1.4.1.5923.1.1.1.7"
    assert attribute.name_format == (
        "urn:oasis:names:tc:SAML:2.0:attrname-format:uri")
    assert attribute.friendly_name == "eduPersonEntitlement"


def test_subject():
    subject = utils.factory(saml.Subject, text="_aaa",
                            name_id=saml.NameID(
                                text=saml.NAMEID_FORMAT_TRANSIENT))

    assert _eq(subject.keyswv(), ["text", "name_id"])
    assert subject.text == "_aaa"
    assert subject.name_id.text == saml.NAMEID_FORMAT_TRANSIENT


# ---------------------------------------------------------------------------

def test_parse_attribute_map():
    (forward, backward) = utils.parse_attribute_map(
        [full_path("attribute.map")])

    assert _eq(forward.keys(), backward.values())
    assert _eq(forward.values(), backward.keys())
    print(forward.keys())
    assert _oeq(forward.keys(), [
        ('urn:oid:1.3.6.1.4.1.5923.1.1.1.7', NAME_FORMAT_URI),
        ('urn:oid:0.9.2342.19200300.100.1.1', NAME_FORMAT_URI),
        ('urn:oid:1.3.6.1.4.1.5923.1.1.1.1', NAME_FORMAT_URI),
        ('urn:oid:2.5.4.42', NAME_FORMAT_URI),
        ('urn:oid:2.5.4.4', NAME_FORMAT_URI),
        ('urn:oid:0.9.2342.19200300.100.1.3', NAME_FORMAT_URI),
        ('urn:oid:2.5.4.12', NAME_FORMAT_URI)])
    assert _eq(forward.keys(), [
        ('urn:oid:1.3.6.1.4.1.5923.1.1.1.7', NAME_FORMAT_URI),
        ('urn:oid:0.9.2342.19200300.100.1.1', NAME_FORMAT_URI),
        ('urn:oid:1.3.6.1.4.1.5923.1.1.1.1', NAME_FORMAT_URI),
        ('urn:oid:2.5.4.42', NAME_FORMAT_URI),
        ('urn:oid:2.5.4.4', NAME_FORMAT_URI),
        ('urn:oid:0.9.2342.19200300.100.1.3', NAME_FORMAT_URI),
        ('urn:oid:2.5.4.12', NAME_FORMAT_URI)])
    assert _eq(backward.keys(), ["surName", "givenName", "title", "uid", "mail",
                                 "eduPersonAffiliation",
                                 "eduPersonEntitlement"])


def test_identity_attribute_0():
    (forward, backward) = utils.parse_attribute_map(
        [full_path("attribute.map")])
    a = Attribute(name="urn:oid:2.5.4.4", name_format=NAME_FORMAT_URI,
                  friendly_name="surName")

    assert utils.identity_attribute("name", a, forward) == "urn:oid:2.5.4.4"
    assert utils.identity_attribute("friendly", a, forward) == "surName"


def test_identity_attribute_1():
    (forward, backward) = utils.parse_attribute_map(
        [full_path("attribute.map")])
    a = Attribute(name="urn:oid:2.5.4.4", name_format=NAME_FORMAT_URI)

    assert utils.identity_attribute("name", a, forward) == "urn:oid:2.5.4.4"
    assert utils.identity_attribute("friendly", a, forward) == "surName"


def test_identity_attribute_2():
    (forward, backward) = utils.parse_attribute_map(
        [full_path("attribute.map")])
    a = Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI)

    assert utils.identity_attribute("name", a, forward) == "urn:oid:2.5.4.5"
    # if there would be a map it would be serialNumber
    assert utils.identity_attribute("friendly", a, forward) == "urn:oid:2.5.4.5"


def test_identity_attribute_3():
    a = Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI)

    assert utils.identity_attribute("name", a) == "urn:oid:2.5.4.5"
    # if there would be a map it would be serialNumber
    assert utils.identity_attribute("friendly", a) == "urn:oid:2.5.4.5"


def test_identity_attribute_4():
    a = Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                  friendly_name="serialNumber")

    assert utils.identity_attribute("name", a) == "urn:oid:2.5.4.5"
    # if there would be a map it would be serialNumber
    assert utils.identity_attribute("friendly", a) == "serialNumber"


def given_name(a):
    assert a["name"] == "urn:oid:2.5.4.42"
    assert a["friendly_name"] == "givenName"
    assert len(a["attribute_value"]) == 1
    assert a["attribute_value"] == [{"text": "Derek"}]


def sur_name(a):
    assert a["name"] == "urn:oid:2.5.4.4"
    assert a["friendly_name"] == "surName"
    assert len(a["attribute_value"]) == 1
    assert a["attribute_value"] == [{"text": "Jeter"}]


def test_nameformat_email():
    assert utils.valid_email("foo@example.com")
    assert utils.valid_email("a@b.com")
    assert utils.valid_email("a@b.se")
    assert utils.valid_email("john@doe@johndoe.com") is False


def test_attribute():
    a = utils.factory(saml.Attribute,
                      friendly_name="eduPersonScopedAffiliation",
                      name="urn:oid:1.3.6.1.4.1.5923.1.1.1.9",
                      name_format="urn:oasis:names:tc:SAML:2.0:attrname"
                                  "-format:uri")

    assert _eq(a.keyswv(), ["friendly_name", "name", "name_format"])

    a = utils.factory(
        saml.Attribute, friendly_name="eduPersonScopedAffiliation",
        name="urn:oid:1.3.6.1.4.1.5923.1.1.1.9",
        name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
        attribute_value=[saml.AttributeValue(text="member@example.com")])

    assert _eq(a.keyswv(), ["friendly_name", "name", "name_format",
                            "attribute_value"])


def test_attribute_statement_2():
    statement = utils.factory(saml.Statement,
                              attribute=[
                                  utils.factory(saml.Attribute,
                                                attribute_value=[
                                                    utils.factory(
                                                        saml.AttributeValue,
                                                        text="Derek")],
                                                friendly_name="givenName"),
                                  utils.factory(saml.Attribute,
                                                attribute_value=[
                                                    utils.factory(
                                                        saml.AttributeValue,
                                                        text="Jeter")],
                                                friendly_name="surName"),
                              ])
    assert statement.keyswv() == ["attribute"]
    assert len(statement.attribute) == 2


def test_subject_confirmation_data():
    s = utils.factory(saml.SubjectConfirmation,
                      in_response_to="_12345678",
                      not_before="2010-02-11T07:30:00Z",
                      not_on_or_after="2010-02-11T07:35:00Z",
                      recipient="http://example.com/sp/",
                      address="192.168.0.10")

    assert _eq(s.keyswv(), ["in_response_to", "not_before", "not_on_or_after",
                            "recipient", "address"])


def test_subject_confirmation():
    s = utils.factory(saml.SubjectConfirmation,
                      method="urn:oasis:names:tc:SAML:2.0:profiles:SSO:browser",
                      base_id="1234",
                      name_id="abcd",
                      subject_confirmation_data=utils.factory(
                          saml.SubjectConfirmationData,
                          in_response_to="_1234567890",
                          recipient="http://example.com/sp/"))

    assert _eq(s.keyswv(),
               ["method", "base_id", "name_id", "subject_confirmation_data"])
    assert s.method == "urn:oasis:names:tc:SAML:2.0:profiles:SSO:browser"


def test_authn_context_class_ref():
    a = utils.factory(saml.AuthnContextClassRef,
                      text="urn:oasis:names:tc:SAML:2.0:ac:classes:unspecified")
    assert a.keyswv() == ["text"]
    assert a.text == "urn:oasis:names:tc:SAML:2.0:ac:classes:unspecified"


def test_authn_context():
    accr = utils.factory(
        saml.AuthnContext,
        text="urn:oasis:names:tc:SAML:2.0:ac:classes:unspecified")
    a = utils.factory(saml.AuthnContext, authn_context_class_ref=accr)

    assert a.keyswv() == ["authn_context_class_ref"]


def test_authn_statement():
    accr = utils.factory(
        saml.AuthnContextClassRef,
        text="urn:oasis:names:tc:SAML:2.0:ac:classes:unspecified")
    ac = utils.factory(saml.AuthnContext,
                       authn_context_class_ref=accr)
    ast = utils.factory(saml.AuthnStatement,
                        authn_instant="2010-03-10T12:33:00Z",
                        session_index="_12345",
                        session_not_on_or_after="2010-03-11T12:00:00Z",
                        authn_context=ac)
    assert _eq(ast.keyswv(), ["authn_instant", "session_index",
                              "session_not_on_or_after",
                              "authn_context"])


def test_signature():
    arr = ["foobar", "1234567890"]
    csum = utils.signature("abcdef", arr)
    arr.append(csum)

    assert utils.verify_signature("abcdef", arr)


def test_complex_factory():
    r = set_arg(Subject, 'in_response_to', '123456')
    subject = utils.factory(Subject, **r[0])
    assert _eq(subject.keyswv(), ['subject_confirmation'])
    assert _eq(subject.subject_confirmation.keyswv(),
               ['subject_confirmation_data'])
    assert _eq(subject.subject_confirmation.subject_confirmation_data.keyswv(),
               ['in_response_to'])
    assert subject.subject_confirmation.subject_confirmation_data.in_response_to == '123456'
