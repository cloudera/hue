#!/usr/bin/env python

from xml.etree import ElementTree as ElementTree

from defusedxml.common import EntitiesForbidden
from pytest import raises

from saml2 import soap
from saml2.samlp import NAMESPACE as SAMLP_NAMESPACE
import saml2.samlp as samlp


NAMESPACE = "http://schemas.xmlsoap.org/soap/envelope/"

example = """<Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/">
    <Body>
        <samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" 
            xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" 
            ID="_6c3a4f8b9c2d" Version="2.0" IssueInstant="2004-03-27T08:42:00Z">
        <saml:Issuer>https://www.example.com/SAML</saml:Issuer>
        <Status>
        <StatusCode Value='urn:oasis:names:tc:SAML:2.0:status:Success'/>
        </Status>
        <saml:Assertion>
        <saml:Subject></saml:Subject>
        <saml:AttributeStatement></saml:AttributeStatement>
        </saml:Assertion>
        </samlp:Response>
    </Body>
</Envelope>
"""


def test_parse_soap_envelope():
    envelope = ElementTree.fromstring(example)
    assert envelope.tag == "{%s}Envelope" % NAMESPACE
    # How to check that it's the right type ?
    assert len(envelope) == 1
    body = envelope[0]
    assert body.tag == "{%s}Body" % NAMESPACE
    assert len(body) == 1
    saml_part = body[0]
    assert saml_part.tag == "{%s}Response" % SAMLP_NAMESPACE
    # {http://schemas.xmlsoap.org/soap/envelope/}Envelope


def test_make_soap_envelope():
    envelope = ElementTree.Element("")
    envelope.tag = "{%s}Envelope" % NAMESPACE
    body = ElementTree.Element("")
    body.tag = "{%s}Body" % NAMESPACE
    envelope.append(body)
    request = samlp.AuthnRequest()
    request.become_child_element_of(body)

    assert envelope.tag == "{%s}Envelope" % NAMESPACE
    assert len(envelope) == 1
    body = envelope[0]
    assert body.tag == "{%s}Body" % NAMESPACE
    assert len(body) == 1
    saml_part = body[0]
    assert saml_part.tag == "{%s}AuthnRequest" % SAMLP_NAMESPACE


def test_parse_soap_enveloped_saml_thingy_xxe():
    xml = """<?xml version="1.0"?>
    <!DOCTYPE lolz [
    <!ENTITY lol "lol">
    <!ELEMENT lolz (#PCDATA)>
    <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
    ]>
    <lolz>&lol1;</lolz>
    """
    with raises(EntitiesForbidden):
        soap.parse_soap_enveloped_saml_thingy(xml, None)


def test_class_instances_from_soap_enveloped_saml_thingies_xxe():
    xml = """<?xml version="1.0"?>
    <!DOCTYPE lolz [
    <!ENTITY lol "lol">
    <!ELEMENT lolz (#PCDATA)>
    <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
    ]>
    <lolz>&lol1;</lolz>
    """
    with raises(soap.XmlParseError):
        soap.class_instances_from_soap_enveloped_saml_thingies(xml, None)


def test_open_soap_envelope_xxe():
    xml = """<?xml version="1.0"?>
    <!DOCTYPE lolz [
    <!ENTITY lol "lol">
    <!ELEMENT lolz (#PCDATA)>
    <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
    ]>
    <lolz>&lol1;</lolz>
    """
    with raises(soap.XmlParseError):
        soap.open_soap_envelope(xml)
