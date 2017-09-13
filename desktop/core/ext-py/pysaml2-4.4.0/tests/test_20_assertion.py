# coding=utf-8
import pytest

from saml2.argtree import add_path
from saml2.authn_context import pword
from saml2.mdie import to_dict
from saml2 import md, assertion
from saml2.saml import Attribute
from saml2.saml import Issuer
from saml2.saml import NAMEID_FORMAT_ENTITY
from saml2.saml import NAME_FORMAT_URI
from saml2.saml import AttributeValue
from saml2.saml import NameID
from saml2.saml import NAMEID_FORMAT_TRANSIENT
from saml2.assertion import Policy
from saml2.assertion import Assertion
from saml2.assertion import filter_on_attributes
from saml2.assertion import filter_attribute_value_assertions
from saml2.assertion import from_local
from saml2.s_utils import MissingValue
from saml2 import attribute_converter
from saml2.attribute_converter import ac_factory, AttributeConverterNOOP

from py.test import raises

from saml2.extension import mdui
from saml2.extension import idpdisc
from saml2.extension import dri
from saml2.extension import mdattr
from saml2.extension import ui
from saml2 import saml
from saml2 import xmldsig
from saml2 import xmlenc

from pathutils import full_path

ONTS = [saml, mdui, mdattr, dri, ui, idpdisc, md, xmldsig, xmlenc]


def _eq(l1, l2):
    return set(l1) == set(l2)


gn = to_dict(md.RequestedAttribute(name="urn:oid:2.5.4.42",
                                   friendly_name="givenName",
                                   name_format=NAME_FORMAT_URI), ONTS)

sn = to_dict(md.RequestedAttribute(name="urn:oid:2.5.4.4",
                                   friendly_name="surName",
                                   name_format=NAME_FORMAT_URI), ONTS)

mail = to_dict(md.RequestedAttribute(name="urn:oid:0.9.2342.19200300.100.1.3",
                                     friendly_name="mail",
                                     name_format=NAME_FORMAT_URI), ONTS)


# ---------------------------------------------------------------------------


def test_filter_on_attributes_0():
    a = to_dict(Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                          friendly_name="serialNumber"), ONTS)

    required = [a]
    ava = {"serialNumber": ["12345"]}

    ava = filter_on_attributes(ava, required)
    assert list(ava.keys()) == ["serialNumber"]
    assert ava["serialNumber"] == ["12345"]


def test_filter_on_attributes_1():
    a = to_dict(Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                          friendly_name="serialNumber"), ONTS)

    required = [a]
    ava = {"serialNumber": ["12345"], "givenName": ["Lars"]}

    ava = filter_on_attributes(ava, required)
    assert list(ava.keys()) == ["serialNumber"]
    assert ava["serialNumber"] == ["12345"]


def test_filter_on_attributes_without_friendly_name():
    ava = {"eduPersonTargetedID": "test@example.com",
           "eduPersonAffiliation": "test",
           "extra": "foo"}
    eptid = to_dict(
        Attribute(name="urn:oid:1.3.6.1.4.1.5923.1.1.1.10",
                  name_format=NAME_FORMAT_URI), ONTS)
    ep_affiliation = to_dict(
        Attribute(name="urn:oid:1.3.6.1.4.1.5923.1.1.1.1",
                  name_format=NAME_FORMAT_URI), ONTS)

    restricted_ava = filter_on_attributes(ava, required=[eptid],
                                          optional=[ep_affiliation],
                                          acs=ac_factory())
    assert restricted_ava == {"eduPersonTargetedID": "test@example.com",
                              "eduPersonAffiliation": "test"}


def test_filter_on_attributes_with_missing_required_attribute():
    ava = {"extra": "foo"}
    eptid = to_dict(Attribute(
        friendly_name="eduPersonTargetedID",
        name="urn:oid:1.3.6.1.4.1.5923.1.1.1.10",
        name_format=NAME_FORMAT_URI), ONTS)
    with pytest.raises(MissingValue):
        filter_on_attributes(ava, required=[eptid])


def test_filter_on_attributes_with_missing_optional_attribute():
    ava = {"extra": "foo"}
    eptid = to_dict(Attribute(
        friendly_name="eduPersonTargetedID",
        name="urn:oid:1.3.6.1.4.1.5923.1.1.1.10",
        name_format=NAME_FORMAT_URI), ONTS)
    assert filter_on_attributes(ava, optional=[eptid]) == {}


# ----------------------------------------------------------------------

def test_lifetime_1():
    conf = {
        "default": {
            "lifetime": {"minutes": 15},
            "attribute_restrictions": None  # means all I have
        },
        "urn:mace:umu.se:saml:roland:sp": {
            "lifetime": {"minutes": 5},
            "attribute_restrictions": {
                "givenName": None,
                "surName": None,
                "mail": [".*@.*\.umu\.se"],
            }
        }}

    r = Policy(conf)
    assert r is not None

    assert r.get_lifetime("urn:mace:umu.se:saml:roland:sp") == {"minutes": 5}
    assert r.get_lifetime("urn:mace:example.se:saml:sp") == {"minutes": 15}


def test_lifetime_2():
    conf = {
        "default": {
            "attribute_restrictions": None  # means all I have
        },
        "urn:mace:umu.se:saml:roland:sp": {
            "lifetime": {"minutes": 5},
            "attribute_restrictions": {
                "givenName": None,
                "surName": None,
                "mail": [".*@.*\.umu\.se"],
            }
        }}

    r = Policy(conf)
    assert r is not None

    assert r.get_lifetime("urn:mace:umu.se:saml:roland:sp") == {"minutes": 5}
    assert r.get_lifetime("urn:mace:example.se:saml:sp") == {"hours": 1}


def test_ava_filter_1():
    conf = {
        "default": {
            "lifetime": {"minutes": 15},
            "attribute_restrictions": None  # means all I have
        },
        "urn:mace:umu.se:saml:roland:sp": {
            "lifetime": {"minutes": 5},
            "attribute_restrictions": {
                "givenName": None,
                "surName": None,
                "mail": [".*@.*\.umu\.se"],
            }
        }}

    r = Policy(conf)

    ava = {"givenName": "Derek",
           "surName": "Jeter",
           "mail": "derek@example.com"}

    ava = r.filter(ava, "urn:mace:umu.se:saml:roland:sp", None, None)
    assert _eq(list(ava.keys()), ["givenName", "surName"])

    ava = {"givenName": "Derek",
           "mail": "derek@nyy.umu.se"}

    assert _eq(sorted(list(ava.keys())), ["givenName", "mail"])


def test_ava_filter_2():
    conf = {
        "default": {
            "lifetime": {"minutes": 15},
            "attribute_restrictions": None  # means all I have
        },
        "urn:mace:umu.se:saml:roland:sp": {
            "lifetime": {"minutes": 5},
            "attribute_restrictions": {
                "givenName": None,
                "surName": None,
                "mail": [".*@.*\.umu\.se"],
            }
        }}

    policy = Policy(conf)

    ava = {"givenName": "Derek",
           "surName": "Jeter",
           "mail": "derek@example.com"}

    # mail removed because it doesn't match the regular expression
    _ava = policy.filter(ava, 'urn:mace:umu.se:saml:roland:sp', None, [mail],
                         [gn, sn])

    assert _eq(sorted(list(_ava.keys())), ["givenName", "surName"])

    ava = {"givenName": "Derek",
           "surName": "Jeter"}

    # it wasn't there to begin with
    try:
        policy.filter(ava, 'urn:mace:umu.se:saml:roland:sp', None,
                      [gn, sn, mail])
    except MissingValue:
        pass


def test_ava_filter_dont_fail():
    conf = {
        "default": {
            "lifetime": {"minutes": 15},
            "attribute_restrictions": None,  # means all I have
            "fail_on_missing_requested": False
        },
        "urn:mace:umu.se:saml:roland:sp": {
            "lifetime": {"minutes": 5},
            "attribute_restrictions": {
                "givenName": None,
                "surName": None,
                "mail": [".*@.*\.umu\.se"],
            },
            "fail_on_missing_requested": False
        }}

    policy = Policy(conf)

    ava = {"givenName": "Derek",
           "surName": "Jeter",
           "mail": "derek@example.com"}

    # mail removed because it doesn't match the regular expression
    # So it should fail if the 'fail_on_ ...' flag wasn't set
    _ava = policy.filter(ava, 'urn:mace:umu.se:saml:roland:sp', None,
                         [mail], [gn, sn])

    assert _ava

    ava = {"givenName": "Derek",
           "surName": "Jeter"}

    # it wasn't there to begin with
    _ava = policy.filter(ava, 'urn:mace:umu.se:saml:roland:sp',
                         None, [gn, sn, mail])

    assert _ava


def test_filter_attribute_value_assertions_0(AVA):
    p = Policy({
        "default": {
            "attribute_restrictions": {
                "surName": [".*berg"],
            }
        }
    })

    ava = filter_attribute_value_assertions(AVA[3].copy(),
                                            p.get_attribute_restrictions(""))

    print(ava)
    assert list(ava.keys()) == ["surName"]
    assert ava["surName"] == ["Hedberg"]


def test_filter_attribute_value_assertions_1(AVA):
    p = Policy({
        "default": {
            "attribute_restrictions": {
                "surName": None,
                "givenName": [".*er.*"],
            }
        }
    })

    ava = filter_attribute_value_assertions(AVA[0].copy(),
                                            p.get_attribute_restrictions(""))

    print(ava)
    assert _eq(ava.keys(), ["givenName", "surName"])
    assert ava["surName"] == ["Jeter"]
    assert ava["givenName"] == ["Derek"]

    ava = filter_attribute_value_assertions(AVA[1].copy(),
                                            p.get_attribute_restrictions(""))

    print(ava)
    assert _eq(list(ava.keys()), ["surName"])
    assert ava["surName"] == ["Howard"]


def test_filter_attribute_value_assertions_2(AVA):
    p = Policy({
        "default": {
            "attribute_restrictions": {
                "givenName": ["^R.*"],
            }
        }
    })

    ava = filter_attribute_value_assertions(AVA[0].copy(),
                                            p.get_attribute_restrictions(""))

    print(ava)
    assert _eq(ava.keys(), [])

    ava = filter_attribute_value_assertions(AVA[1].copy(),
                                            p.get_attribute_restrictions(""))

    print(ava)
    assert _eq(list(ava.keys()), ["givenName"])
    assert ava["givenName"] == ["Ryan"]

    ava = filter_attribute_value_assertions(AVA[3].copy(),
                                            p.get_attribute_restrictions(""))

    print(ava)
    assert _eq(list(ava.keys()), ["givenName"])
    assert ava["givenName"] == ["Roland"]


# ----------------------------------------------------------------------------


def test_assertion_1(AVA):
    ava = Assertion(AVA[0])

    print(ava)
    print(ava.__dict__)

    policy = Policy({
        "default": {
            "attribute_restrictions": {
                "givenName": ["^R.*"],
            }
        }
    })

    ava = ava.apply_policy("", policy)

    print(ava)
    assert _eq(list(ava.keys()), [])

    ava = Assertion(AVA[1].copy())
    ava = ava.apply_policy("", policy)
    assert _eq(list(ava.keys()), ["givenName"])
    assert ava["givenName"] == ["Ryan"]

    ava = Assertion(AVA[3].copy())
    ava = ava.apply_policy("", policy)
    assert _eq(list(ava.keys()), ["givenName"])
    assert ava["givenName"] == ["Roland"]


def test_assertion_2():
    AVA = {'mail': u'roland.hedberg@adm.umu.se',
           'eduPersonTargetedID': 'http://lingon.ladok.umu'
                                  '.se:8090/idp!http://lingon.ladok.umu'
                                  '.se:8088/sp!95e9ae91dbe62d35198fbbd5e1fb0976',
           'displayName': u'Roland Hedberg',
           'uid': 'http://roland.hedberg.myopenid.com/'}

    ava = Assertion(AVA)

    policy = Policy({
        "default": {
            "lifetime": {"minutes": 240},
            "attribute_restrictions": None,  # means all I have
            "name_form": NAME_FORMAT_URI
        },
    })

    ava = ava.apply_policy("", policy)
    acs = ac_factory(full_path("attributemaps"))
    attribute = from_local(acs, ava, policy.get_name_form(""))

    assert len(attribute) == 4
    names = [attr.name for attr in attribute]
    assert _eq(sorted(list(names)), [
        'urn:oid:0.9.2342.19200300.100.1.1',
        'urn:oid:0.9.2342.19200300.100.1.3',
        'urn:oid:1.3.6.1.4.1.5923.1.1.1.10',
        'urn:oid:2.16.840.1.113730.3.1.241'])


# ----------------------------------------------------------------------------


def test_filter_values_req_2():
    a1 = to_dict(Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                           friendly_name="serialNumber"), ONTS)
    a2 = to_dict(Attribute(name="urn:oid:2.5.4.4", name_format=NAME_FORMAT_URI,
                           friendly_name="surName"), ONTS)

    required = [a1, a2]
    ava = {"serialNumber": ["12345"], "givenName": ["Lars"]}

    raises(MissingValue, filter_on_attributes, ava, required)


def test_filter_values_req_3():
    a = to_dict(
        Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                  friendly_name="serialNumber",
                  attribute_value=[AttributeValue(text="12345")]), ONTS)

    required = [a]
    ava = {"serialNumber": ["12345"]}

    ava = filter_on_attributes(ava, required)
    assert list(ava.keys()) == ["serialNumber"]
    assert ava["serialNumber"] == ["12345"]


def test_filter_values_req_4():
    a = to_dict(
        Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                  friendly_name="serialNumber",
                  attribute_value=[AttributeValue(text="54321")]), ONTS)

    required = [a]
    ava = {"serialNumber": ["12345"]}

    raises(MissingValue, filter_on_attributes, ava, required)


def test_filter_values_req_5():
    a = to_dict(
        Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                  friendly_name="serialNumber",
                  attribute_value=[AttributeValue(text="12345")]), ONTS)

    required = [a]
    ava = {"serialNumber": ["12345", "54321"]}

    ava = filter_on_attributes(ava, required)
    assert list(ava.keys()) == ["serialNumber"]
    assert ava["serialNumber"] == ["12345"]


def test_filter_values_req_6():
    a = to_dict(
        Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                  friendly_name="serialNumber",
                  attribute_value=[AttributeValue(text="54321")]), ONTS)

    required = [a]
    ava = {"serialNumber": ["12345", "54321"]}

    ava = filter_on_attributes(ava, required)
    assert list(ava.keys()) == ["serialNumber"]
    assert ava["serialNumber"] == ["54321"]


def test_filter_values_req_opt_0():
    r = to_dict(
        Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                  friendly_name="serialNumber",
                  attribute_value=[AttributeValue(text="54321")]), ONTS)
    o = to_dict(
        Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                  friendly_name="serialNumber",
                  attribute_value=[AttributeValue(text="12345")]), ONTS)

    ava = {"serialNumber": ["12345", "54321"]}

    ava = filter_on_attributes(ava, [r], [o])
    assert list(ava.keys()) == ["serialNumber"]
    assert _eq(ava["serialNumber"], ["12345", "54321"])


def test_filter_values_req_opt_1():
    r = to_dict(
        Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                  friendly_name="serialNumber",
                  attribute_value=[AttributeValue(text="54321")]), ONTS)
    o = to_dict(
        Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                  friendly_name="serialNumber",
                  attribute_value=[AttributeValue(text="12345"),
                                   AttributeValue(text="abcd0")]), ONTS)

    ava = {"serialNumber": ["12345", "54321"]}

    ava = filter_on_attributes(ava, [r], [o])
    assert list(ava.keys()) == ["serialNumber"]
    assert _eq(ava["serialNumber"], ["12345", "54321"])


def test_filter_values_req_opt_2():
    r = [
        to_dict(
            Attribute(
                friendly_name="surName",
                name="urn:oid:2.5.4.4",
                name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"),
            ONTS),
        to_dict(
            Attribute(
                friendly_name="givenName",
                name="urn:oid:2.5.4.42",
                name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"),
            ONTS),
        to_dict(
            Attribute(
                friendly_name="mail",
                name="urn:oid:0.9.2342.19200300.100.1.3",
                name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"),
            ONTS)]
    o = [
        to_dict(
            Attribute(
                friendly_name="title",
                name="urn:oid:2.5.4.12",
                name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"),
            ONTS)]

    ava = {"surname": ["Hedberg"], "givenName": ["Roland"],
           "eduPersonAffiliation": ["staff"], "uid": ["rohe0002"]}

    raises(MissingValue, "filter_on_attributes(ava, r, o)")


# ---------------------------------------------------------------------------


def test_filter_values_req_opt_4():
    r = [
        Attribute(
            friendly_name="surName",
            name="urn:oid:2.5.4.4",
            name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"),
        Attribute(
            friendly_name="givenName",
            name="urn:oid:2.5.4.42",
            name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri")]
    o = [
        Attribute(
            friendly_name="title",
            name="urn:oid:2.5.4.12",
            name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri")]

    acs = attribute_converter.ac_factory(full_path("attributemaps"))

    rava = attribute_converter.list_to_local(acs, r)
    oava = attribute_converter.list_to_local(acs, o)

    ava = {"sn": ["Hedberg"], "givenName": ["Roland"],
           "eduPersonAffiliation": ["staff"], "uid": ["rohe0002"]}

    ava = assertion.filter_on_demands(ava, rava, oava)
    print(ava)
    assert _eq(sorted(list(ava.keys())), ['givenName', 'sn'])
    assert ava == {'givenName': ['Roland'], 'sn': ['Hedberg']}


# ---------------------------------------------------------------------------


def test_filter_ava_0():
    policy = Policy(
        {
            "default": {
                "lifetime": {"minutes": 15},
                "attribute_restrictions": None  # means all I have
            },
            "urn:mace:example.com:saml:roland:sp": {
                "lifetime": {"minutes": 5},
            }
        }
    )

    ava = {"givenName": ["Derek"], "surName": ["Jeter"],
           "mail": ["derek@nyy.mlb.com"]}

    # No restrictions apply
    ava = policy.filter(ava, "urn:mace:example.com:saml:roland:sp", [], [])

    assert _eq(sorted(list(ava.keys())), ["givenName", "mail", "surName"])
    assert ava["givenName"] == ["Derek"]
    assert ava["surName"] == ["Jeter"]
    assert ava["mail"] == ["derek@nyy.mlb.com"]


def test_filter_ava_1():
    """ No mail address returned """
    policy = Policy({
        "default": {
            "lifetime": {"minutes": 15},
            "attribute_restrictions": None  # means all I have
        },
        "urn:mace:example.com:saml:roland:sp": {
            "lifetime": {"minutes": 5},
            "attribute_restrictions": {
                "givenName": None,
                "surName": None,
            }
        }})

    ava = {"givenName": ["Derek"], "surName": ["Jeter"],
           "mail": ["derek@nyy.mlb.com"]}

    # No restrictions apply
    ava = policy.filter(ava, "urn:mace:example.com:saml:roland:sp", [], [])

    assert _eq(sorted(list(ava.keys())), ["givenName", "surName"])
    assert ava["givenName"] == ["Derek"]
    assert ava["surName"] == ["Jeter"]


def test_filter_ava_2():
    """ Only mail returned """
    policy = Policy({
        "default": {
            "lifetime": {"minutes": 15},
            "attribute_restrictions": None  # means all I have
        },
        "urn:mace:example.com:saml:roland:sp": {
            "lifetime": {"minutes": 5},
            "attribute_restrictions": {
                "mail": None,
            }
        }})

    ava = {"givenName": ["Derek"], "surName": ["Jeter"],
           "mail": ["derek@nyy.mlb.com"]}

    # No restrictions apply
    ava = policy.filter(ava, "urn:mace:example.com:saml:roland:sp", [], [])

    assert _eq(list(ava.keys()), ["mail"])
    assert ava["mail"] == ["derek@nyy.mlb.com"]


def test_filter_ava_3():
    """ Only example.com mail addresses returned """
    policy = Policy({
        "default": {
            "lifetime": {"minutes": 15},
            "attribute_restrictions": None  # means all I have
        },
        "urn:mace:example.com:saml:roland:sp": {
            "lifetime": {"minutes": 5},
            "attribute_restrictions": {
                "mail": [".*@example\.com$"],
            }
        }})

    ava = {"givenName": ["Derek"], "surName": ["Jeter"],
           "mail": ["derek@nyy.mlb.com", "dj@example.com"]}

    # No restrictions apply
    ava = policy.filter(ava, "urn:mace:example.com:saml:roland:sp", [], [])

    assert _eq(list(ava.keys()), ["mail"])
    assert ava["mail"] == ["dj@example.com"]


def test_filter_ava_4():
    """ Return everything as default policy is used """
    policy = Policy({
        "default": {
            "lifetime": {"minutes": 15},
            "attribute_restrictions": None  # means all I have
        },
        "urn:mace:example.com:saml:roland:sp": {
            "lifetime": {"minutes": 5},
            "attribute_restrictions": {
                "mail": [".*@example\.com$"],
            }
        }})

    ava = {"givenName": ["Derek"], "surName": ["Jeter"],
           "mail": ["derek@nyy.mlb.com", "dj@example.com"]}

    # No restrictions apply
    ava = policy.filter(ava, "urn:mace:example.com:saml:curt:sp", [], [])

    assert _eq(sorted(list(ava.keys())), ['mail', 'givenName', 'surName'])
    assert _eq(ava["mail"], ["derek@nyy.mlb.com", "dj@example.com"])


def test_req_opt():
    req = [
        to_dict(
            md.RequestedAttribute(
                friendly_name="surname", name="urn:oid:2.5.4.4",
                name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
                is_required="true"), ONTS),
        to_dict(
            md.RequestedAttribute(
                friendly_name="givenname",
                name="urn:oid:2.5.4.42",
                name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
                is_required="true"), ONTS),
        to_dict(
            md.RequestedAttribute(
                friendly_name="edupersonaffiliation",
                name="urn:oid:1.3.6.1.4.1.5923.1.1.1.1",
                name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
                is_required="true"), ONTS)]

    opt = [
        to_dict(
            md.RequestedAttribute(
                friendly_name="title",
                name="urn:oid:2.5.4.12",
                name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
                is_required="false"), ONTS)]

    policy = Policy()
    ava = {'givenname': 'Roland', 'surname': 'Hedberg',
           'uid': 'rohe0002', 'edupersonaffiliation': 'staff'}

    sp_entity_id = "urn:mace:example.com:saml:curt:sp"
    fava = policy.filter(ava, sp_entity_id, None, req, opt)
    assert fava


def test_filter_on_wire_representation_1():
    r = [
        Attribute(
            friendly_name="surName",
            name="urn:oid:2.5.4.4",
            name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"),
        Attribute(
            friendly_name="givenName",
            name="urn:oid:2.5.4.42",
            name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri")]
    o = [
        Attribute(
            friendly_name="title",
            name="urn:oid:2.5.4.12",
            name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri")]

    acs = attribute_converter.ac_factory(full_path("attributemaps"))

    ava = {"sn": ["Hedberg"], "givenname": ["Roland"],
           "edupersonaffiliation": ["staff"], "uid": ["rohe0002"]}

    ava = assertion.filter_on_wire_representation(ava, acs, r, o)
    assert _eq(sorted(list(ava.keys())), ["givenname", "sn"])


def test_filter_on_wire_representation_2():
    r = [
        Attribute(
            friendly_name="surName",
            name="urn:oid:2.5.4.4",
            name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"),
        Attribute(
            friendly_name="givenName",
            name="urn:oid:2.5.4.42",
            name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri")]
    o = [
        Attribute(
            friendly_name="title",
            name="urn:oid:2.5.4.12",
            name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri")]

    acs = attribute_converter.ac_factory(full_path("attributemaps"))

    ava = {"sn": ["Hedberg"], "givenname": ["Roland"],
           "title": ["Master"], "uid": ["rohe0002"]}

    ava = assertion.filter_on_wire_representation(ava, acs, r, o)
    assert _eq(sorted(list(ava.keys())), ["givenname", "sn", "title"])


length = pword.Length(min="4")
restricted_password = pword.RestrictedPassword(length=length)
authenticator = pword.Authenticator(restricted_password=restricted_password)
authn_method = pword.AuthnMethod(authenticator=authenticator)
ACD = pword.AuthenticationContextDeclaration(authn_method=authn_method)


def test_assertion_with_noop_attribute_conv():
    ava = {"urn:oid:2.5.4.4": "Roland", "urn:oid:2.5.4.42": "Hedberg"}
    ast = Assertion(ava)
    policy = Policy({
        "default": {
            "lifetime": {"minutes": 240},
            "attribute_restrictions": None,  # means all I have
            "name_form": NAME_FORMAT_URI
        },
    })
    name_id = NameID(format=NAMEID_FORMAT_TRANSIENT, text="foobar")
    issuer = Issuer(text="entityid", format=NAMEID_FORMAT_ENTITY)

    farg = add_path(
        {},
        ['subject', 'subject_confirmation', 'method', saml.SCM_BEARER])
    add_path(
        farg['subject']['subject_confirmation'],
        ['subject_confirmation_data', 'in_response_to', 'in_response_to'])
    add_path(
        farg['subject']['subject_confirmation'],
        ['subject_confirmation_data', 'recipient', 'consumer_url'])

    msg = ast.construct(
        "sp_entity_id", [AttributeConverterNOOP(NAME_FORMAT_URI)], policy,
        issuer=issuer, farg=farg, authn_decl=ACD, name_id=name_id,
        authn_auth="authn_authn")

    print(msg)
    for attr in msg.attribute_statement[0].attribute:
        assert attr.name_format == NAME_FORMAT_URI
        assert len(attr.attribute_value) == 1
        if attr.name == "urn:oid:2.5.4.42":
            assert attr.attribute_value[0].text == "Hedberg"
        elif attr.name == "urn:oid:2.5.4.4":
            assert attr.attribute_value[0].text == "Roland"


# THis test doesn't work without a MetadataStore instance
# def test_filter_ava_5():
#    policy = Policy({
#        "default": {
#            "lifetime": {"minutes": 15},
#            #"attribute_restrictions": None  # means all I have
#            "entity_categories": ["swamid", "edugain"]
#        }
#    })
#
#    ava = {"givenName": ["Derek"], "surName": ["Jeter"],
#           "mail": ["derek@nyy.mlb.com", "dj@example.com"]}
#
#    ava = policy.filter(ava, "urn:mace:example.com:saml:curt:sp", None, [], [])
#
#    # using entity_categories means there *always* are restrictions
#    # in this case the only allowed attribute is eduPersonTargetedID
#    # which isn't available in the ava hence zip is returned.
#    assert ava == {}


def test_assertion_with_zero_attributes():
    ava = {}
    ast = Assertion(ava)
    policy = Policy({
        "default": {
            "lifetime": {"minutes": 240},
            "attribute_restrictions": None,  # means all I have
            "name_form": NAME_FORMAT_URI
        },
    })
    name_id = NameID(format=NAMEID_FORMAT_TRANSIENT, text="foobar")
    issuer = Issuer(text="entityid", format=NAMEID_FORMAT_ENTITY)
    farg = add_path(
        {},
        ['subject', 'subject_confirmation', 'method', saml.SCM_BEARER])
    add_path(
        farg['subject']['subject_confirmation'],
        ['subject_confirmation_data', 'in_response_to', 'in_response_to'])
    add_path(
        farg['subject']['subject_confirmation'],
        ['subject_confirmation_data', 'recipient', 'consumer_url'])

    msg = ast.construct(
        "sp_entity_id", [AttributeConverterNOOP(NAME_FORMAT_URI)], policy,
        issuer=issuer, authn_decl=ACD, authn_auth="authn_authn",
        name_id=name_id, farg=farg)

    print(msg)
    assert msg.attribute_statement == []


def test_assertion_with_authn_instant():
    ava = {}
    ast = Assertion(ava)
    policy = Policy({
        "default": {
            "lifetime": {"minutes": 240},
            "attribute_restrictions": None,  # means all I have
            "name_form": NAME_FORMAT_URI
        },
    })
    name_id = NameID(format=NAMEID_FORMAT_TRANSIENT, text="foobar")
    issuer = Issuer(text="entityid", format=NAMEID_FORMAT_ENTITY)

    farg = add_path(
        {},
        ['subject', 'subject_confirmation', 'method', saml.SCM_BEARER])
    add_path(
        farg['subject']['subject_confirmation'],
        ['subject_confirmation_data', 'in_response_to', 'in_response_to'])
    add_path(
        farg['subject']['subject_confirmation'],
        ['subject_confirmation_data', 'recipient', 'consumer_url'])

    msg = ast.construct(
        "sp_entity_id", [AttributeConverterNOOP(NAME_FORMAT_URI)], policy,
        issuer=issuer, authn_decl=ACD, authn_auth="authn_authn",
        authn_instant=1234567890, name_id=name_id, farg=farg)

    print(msg)
    assert msg.authn_statement[0].authn_instant == "2009-02-13T23:31:30Z"


if __name__ == "__main__":
    test_assertion_2()
