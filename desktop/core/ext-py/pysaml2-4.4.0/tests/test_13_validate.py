#!/usr/bin/env python
# -*- coding: utf-8 -*-

import saml2

from saml2 import saml
from saml2 import samlp
from saml2.validate import valid_duration, MustValueError
from saml2.validate import valid_unsigned_short
from saml2.validate import valid_non_negative_integer
from saml2.validate import valid_string
from saml2.validate import valid_instance
from saml2.validate import valid_any_uri
from saml2.validate import NotValid
from saml2.validate import valid_anytype

from py.test import raises


def _eq(l1, l2):
    return set(l1) == set(l2)


def test_duration():
    assert valid_duration("P1Y2M3DT10H30M")
    assert valid_duration("P1Y2M3DT10H30M1.567S")
    assert valid_duration("-P120D")
    assert valid_duration("P1347Y")
    assert valid_duration("P1347M")
    assert valid_duration("P1Y2MT2H")
    assert valid_duration("P0Y1347M")
    assert valid_duration("P0Y1347M0D")
    assert valid_duration("-P1347M")
    assert valid_duration("P1Y2MT2.5H")

    raises(NotValid, 'valid_duration("P-1347M")')
    raises(NotValid, ' valid_duration("P1Y2MT")')
    raises(NotValid, ' valid_duration("P1Y2MT2xH")')


def test_unsigned_short():
    assert valid_unsigned_short("1234")

    raises(NotValid, ' valid_unsigned_short("-1234")')
    raises(NotValid, ' valid_unsigned_short("1234567890")')


def test_valid_non_negative_integer():
    assert valid_non_negative_integer("1234567890")

    raises(NotValid, 'valid_non_negative_integer("-123")')
    raises(NotValid, 'valid_non_negative_integer("123.56")')
    assert valid_non_negative_integer("12345678901234567890")


def test_valid_string():
    assert valid_string(u'example')

    import codecs

    raises(NotValid,
           'valid_string(codecs.getdecoder("hex_codec")'
           '(b"02656c6c6f")[0].decode("utf-8"))')


def test_valid_anyuri():
    assert valid_any_uri("urn:oasis:names:tc:SAML:2.0:attrname-format:uri")


def test_valid_instance():
    attr_statem = saml.AttributeStatement()
    text = ["value of test attribute",
            "value1 of test attribute",
            "value2 of test attribute",
            "value1 of test attribute2",
            "value2 of test attribute2", ]

    attr_statem.attribute.append(saml.Attribute())
    attr_statem.attribute.append(saml.Attribute())
    attr_statem.attribute[0].name = "testAttribute"
    attr_statem.attribute[0].name_format = saml.NAME_FORMAT_URI
    attr_statem.attribute[0].friendly_name = "test attribute"
    attr_statem.attribute[0].attribute_value.append(saml.AttributeValue())
    attr_statem.attribute[0].attribute_value[0].text = text[0]

    attr_statem.attribute[1].name = "testAttribute2"
    attr_statem.attribute[1].name_format = saml.NAME_FORMAT_UNSPECIFIED
    attr_statem.attribute[1].friendly_name = text[2]
    attr_statem.attribute[1].attribute_value.append(saml.AttributeValue())
    attr_statem.attribute[1].attribute_value[0].text = text[2]

    assert valid_instance(attr_statem)

    response = samlp.Response()
    response.id = "response id"
    response.in_response_to = "request id"
    response.version = saml2.VERSION
    response.issue_instant = "2007-09-14T01:05:02Z"
    response.destination = "http://www.example.com/Destination"
    response.consent = saml.CONSENT_UNSPECIFIED
    response.issuer = saml.Issuer()
    response.status = samlp.Status()
    response.assertion.append(saml.Assertion())

    raises(MustValueError, 'valid_instance(response)')


def test_valid_anytype():
    assert valid_anytype("130.239.16.3")
    assert valid_anytype("textstring")
    assert valid_anytype("12345678")
    assert valid_anytype("-1234")
    assert valid_anytype("P1Y2M3DT10H30M")
    assert valid_anytype("urn:oasis:names:tc:SAML:2.0:attrname-format:uri")

