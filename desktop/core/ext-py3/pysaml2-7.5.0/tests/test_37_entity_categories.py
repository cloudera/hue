from contextlib import closing

import pytest

from pathutils import full_path

from saml2 import config
from saml2 import sigver
from saml2.assertion import Policy
from saml2.attribute_converter import ac_factory
from saml2.extension import mdattr
from saml2.md import RequestedAttribute
from saml2.mdie import to_dict
from saml2.mdstore import MetadataStore
from saml2.saml import NAME_FORMAT_URI
from saml2.server import Server


ATTRCONV = ac_factory(full_path("attributemaps"))
sec_config = config.Config()
sec_config.xmlsec_binary = sigver.get_xmlsec_binary(["/opt/local/bin"])

__author__ = "rolandh"

MDS = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)
MDS.imp([{"class": "saml2.mdstore.MetaDataMD", "metadata": [(full_path("swamid.md"),)]}])


def _eq(l1, l2):
    return set(l1) == set(l2)


def test_filter_ava():
    policy_conf = {
        "default": {
            "lifetime": {"minutes": 15},
            # "attribute_restrictions": None  # means all I have
            "entity_categories": ["swamid"],
        }
    }
    policy = Policy(policy_conf, MDS)

    ava = {"givenName": ["Derek"], "sn": ["Jeter"], "mail": ["derek@nyy.mlb.com", "dj@example.com"], "c": ["USA"]}

    ava = policy.filter(ava, "https://connect.sunet.se/shibboleth")

    assert _eq(list(ava.keys()), ["mail", "givenName", "sn", "c"])
    assert _eq(ava["mail"], ["derek@nyy.mlb.com", "dj@example.com"])


def test_filter_ava2():
    policy_conf = {
        "default": {
            "lifetime": {"minutes": 15},
            # "attribute_restrictions": None  # means all I have
            "entity_categories": ["refeds", "edugain"],
        }
    }
    policy = Policy(policy_conf, MDS)

    ava = {
        "givenName": ["Derek"],
        "sn": ["Jeter"],
        "mail": ["derek@nyy.mlb.com"],
        "c": ["USA"],
        "eduPersonTargetedID": "foo!bar!xyz",
    }

    ava = policy.filter(ava, "https://connect.sunet.se/shibboleth")

    # Mismatch, policy deals with eduGAIN, metadata says SWAMID
    # So only minimum should come out
    assert _eq(list(ava.keys()), ["eduPersonTargetedID"])


def test_filter_ava3():
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)
    mds.imp([{"class": "saml2.mdstore.MetaDataFile", "metadata": [(full_path("entity_cat_sfs_hei.xml"),)]}])

    policy_conf = {
        "default": {
            "lifetime": {"minutes": 15},
            # "attribute_restrictions": None  # means all I have
            "entity_categories": ["swamid"],
        }
    }
    policy = Policy(policy_conf, mds)

    ava = {
        "givenName": ["Derek"],
        "sn": ["Jeter"],
        "mail": ["derek@nyy.mlb.com"],
        "c": ["USA"],
        "eduPersonTargetedID": "foo!bar!xyz",
        "norEduPersonNIN": "19800101134",
    }

    ava = policy.filter(ava, "urn:mace:example.com:saml:roland:sp")
    assert _eq(list(ava.keys()), ["norEduPersonNIN"])


def test_filter_ava4():
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)
    mds.imp([{"class": "saml2.mdstore.MetaDataFile", "metadata": [(full_path("entity_cat_re_nren.xml"),)]}])

    policy_conf = {
        "default": {
            "lifetime": {"minutes": 15},
            # "attribute_restrictions": None  # means all I have
            "entity_categories": ["swamid"],
        }
    }
    policy = Policy(policy_conf, mds)

    ava = {
        "givenName": ["Derek"],
        "sn": ["Jeter"],
        "mail": ["derek@nyy.mlb.com"],
        "c": ["USA"],
        "eduPersonTargetedID": "foo!bar!xyz",
        "norEduPersonNIN": "19800101134",
    }

    ava = policy.filter(ava, "urn:mace:example.com:saml:roland:sp")
    assert _eq(list(ava.keys()), ["givenName", "c", "mail", "sn"])


def test_filter_ava5():
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)
    mds.imp([{"class": "saml2.mdstore.MetaDataFile", "metadata": [(full_path("entity_cat_re.xml"),)]}])

    policy = Policy(
        {
            "default": {
                "lifetime": {"minutes": 15},
                # "attribute_restrictions": None  # means all I have
                "entity_categories": ["swamid"],
            }
        },
        mds,
    )

    ava = {
        "givenName": ["Derek"],
        "sn": ["Jeter"],
        "mail": ["derek@nyy.mlb.com"],
        "c": ["USA"],
        "eduPersonTargetedID": "foo!bar!xyz",
        "norEduPersonNIN": "19800101134",
    }

    ava = policy.filter(ava, "urn:mace:example.com:saml:roland:sp")

    assert _eq(list(ava.keys()), [])


def test_idp_policy_filter():
    with closing(Server("idp_conf_ec")) as idp:
        ava = {
            "givenName": ["Derek"],
            "sn": ["Jeter"],
            "mail": ["derek@nyy.mlb.com"],
            "c": ["USA"],
            "eduPersonTargetedID": "foo!bar!xyz",
            "norEduPersonNIN": "19800101134",
        }

        policy = idp.config.getattr("policy", "idp")
        ava = policy.filter(ava, "urn:mace:example.com:saml:roland:sp")
        # because no entity category
        assert list(ava.keys()) == ["eduPersonTargetedID"]


def test_entity_category_import_from_path():
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)
    # The file entity_cat_rs.xml contains the SAML metadata for an SP
    # tagged with the REFEDs R&S entity category.
    mds.imp([{"class": "saml2.mdstore.MetaDataFile", "metadata": [(full_path("entity_cat_rs.xml"),)]}])

    # The entity category module myentitycategory.py is in the tests
    # directory which is on the standard module search path.
    # The module uses a custom interpretation of the REFEDs R&S entity category
    # by adding eduPersonUniqueId.
    policy = Policy({"default": {"lifetime": {"minutes": 15}, "entity_categories": ["myentitycategory"]}}, mds)

    ava = {
        "givenName": ["Derek"],
        "sn": ["Jeter"],
        "displayName": "Derek Jeter",
        "mail": ["derek@nyy.mlb.com"],
        "c": ["USA"],
        "eduPersonTargetedID": "foo!bar!xyz",
        "eduPersonUniqueId": "R13ET7UD68K0HGR153KE@my.org",
        "eduPersonScopedAffiliation": "member@my.org",
        "eduPersonPrincipalName": "user01@my.org",
        "norEduPersonNIN": "19800101134",
    }

    ava = policy.filter(ava, "urn:mace:example.com:saml:roland:sp")

    # We expect c and norEduPersonNIN to be filtered out since they are not
    # part of the custom entity category.
    assert _eq(
        list(ava.keys()),
        [
            "eduPersonTargetedID",
            "eduPersonPrincipalName",
            "eduPersonUniqueId",
            "displayName",
            "givenName",
            "eduPersonScopedAffiliation",
            "mail",
            "sn",
        ],
    )


def test_filter_ava_required_attributes_with_no_friendly_name():
    entity_id = "https://no-friendly-name.example.edu/saml2/metadata/"
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)
    mds.imp([{"class": "saml2.mdstore.MetaDataFile", "metadata": [(full_path("entity_no_friendly_name_sp.xml"),)]}])

    policy_conf = {"default": {"lifetime": {"minutes": 15}, "entity_categories": ["swamid"]}}
    policy = Policy(policy_conf, mds)

    ava = {
        "givenName": ["Derek"],
        "sn": ["Jeter"],
        "mail": ["derek@nyy.mlb.com"],
        "c": ["USA"],
        "eduPersonTargetedID": "foo!bar!xyz",
        "norEduPersonNIN": "19800101134",
    }

    attribute_requirements = mds.attribute_requirement(entity_id)
    required = attribute_requirements.get("required", [])
    optional = attribute_requirements.get("optional", [])

    # ensure the requirements define the eduPersonTargetedID
    # without the friendlyName attribute
    oid_eptid = "urn:oid:1.3.6.1.4.1.5923.1.1.1.10"
    requested_attribute_eptid = RequestedAttribute(name=oid_eptid, name_format=NAME_FORMAT_URI, is_required="true")
    assert required == [to_dict(requested_attribute_eptid, onts=[mdattr])]

    ava = policy.filter(ava, entity_id, required=required, optional=optional)
    assert _eq(list(ava.keys()), ["eduPersonTargetedID"])


def test_filter_ava_esi_coco():
    entity_id = "https://esi-coco.example.edu/saml2/metadata/"
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)
    mds.imp([{"class": "saml2.mdstore.MetaDataFile", "metadata": [(full_path("entity_esi_and_coco_sp.xml"),)]}])

    policy_conf = {"default": {"lifetime": {"minutes": 15}, "entity_categories": ["swamid"]}}

    policy = Policy(policy_conf, mds)

    ava = {
        "givenName": ["Test"],
        "sn": ["Testsson"],
        "mail": ["test@example.com"],
        "c": ["SE"],
        "schacHomeOrganization": ["example.com"],
        "eduPersonScopedAffiliation": ["student@example.com"],
        "schacPersonalUniqueCode": [
            "urn:schac:personalUniqueCode:int:esi:ladok.se:externtstudentuid-00000000-1111-2222-3333-444444444444"
        ],
    }

    requested_attributes = [
        {
            "friendly_name": "eduPersonScopedAffiliation",
            "name": "1.3.6.1.4.1.5923.1.1.1.9",
            "name_format": NAME_FORMAT_URI,
            "is_required": "true",
        },
        {
            "friendly_name": "schacHomeOrganization",
            "name": "1.3.6.1.4.1.25178.1.2.9",
            "name_format": NAME_FORMAT_URI,
            "is_required": "true",
        },
    ]

    ava = policy.filter(ava, entity_id, required=requested_attributes)

    assert _eq(list(ava.keys()), ["eduPersonScopedAffiliation", "schacHomeOrganization", "schacPersonalUniqueCode"])
    assert _eq(ava["eduPersonScopedAffiliation"], ["student@example.com"])
    assert _eq(ava["schacHomeOrganization"], ["example.com"])
    assert _eq(
        ava["schacPersonalUniqueCode"],
        ["urn:schac:personalUniqueCode:int:esi:ladok.se:externtstudentuid-00000000-1111-2222-3333-444444444444"],
    )


@pytest.mark.skip("Temporarily disabled")
def test_filter_ava_refeds_anonymous_access():
    entity_id = "https://anonymous.example.edu/saml2/metadata/"
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)
    mds.imp([{"class": "saml2.mdstore.MetaDataFile", "metadata": [(full_path("entity_anonymous_sp.xml"),)]}])

    policy_conf = {"default": {"lifetime": {"minutes": 15}, "entity_categories": ["swamid"]}}

    policy = Policy(policy_conf, mds)
    ava = {
        "displayName": ["Test Testsson"],
        "eduPersonAssurance": ["http://www.swamid.se/policy/assurance/al1"],
        "eduPersonScopedAffiliation": ["student@example.com"],
        "eduPersonTargetedID": "foo!bar!xyz",
        "givenName": ["Test"],
        "mail": ["test@example.com"],
        "pairwise-id": ["pairwise-id@example.com"],
        "schacHomeOrganization": ["example.com"],
        "sn": ["Testsson"],
        "subject-id": ["subject-id@example.com"],
    }

    ava = policy.filter(ava, entity_id)

    assert _eq(list(ava.keys()), ["eduPersonScopedAffiliation", "schacHomeOrganization"])
    assert _eq(ava["eduPersonScopedAffiliation"], ["student@example.com"])
    assert _eq(ava["schacHomeOrganization"], ["example.com"])


@pytest.mark.skip("Temporarily disabled")
def test_filter_ava_refeds_pseudonymous_access():
    entity_id = "https://pseudonymous.example.edu/saml2/metadata/"
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)
    mds.imp([{"class": "saml2.mdstore.MetaDataFile", "metadata": [(full_path("entity_pseudonymous_sp.xml"),)]}])

    policy_conf = {"default": {"lifetime": {"minutes": 15}, "entity_categories": ["swamid"]}}

    policy = Policy(policy_conf, mds)
    ava = {
        "displayName": ["Test Testsson"],
        "eduPersonAssurance": ["http://www.swamid.se/policy/assurance/al1"],
        "eduPersonScopedAffiliation": ["student@example.com"],
        "eduPersonTargetedID": "foo!bar!xyz",
        "givenName": ["Test"],
        "mail": ["test@example.com"],
        "pairwise-id": ["pairwise-id@example.com"],
        "schacHomeOrganization": ["example.com"],
        "sn": ["Testsson"],
        "subject-id": ["subject-id@example.com"],
    }

    ava = policy.filter(ava, entity_id)

    assert _eq(
        list(ava.keys()), ["pairwise-id", "eduPersonScopedAffiliation", "eduPersonAssurance", "schacHomeOrganization"]
    )
    assert _eq(ava["pairwise-id"], ["pairwise-id@example.com"])
    assert _eq(ava["eduPersonScopedAffiliation"], ["student@example.com"])
    assert _eq(ava["eduPersonAssurance"], ["http://www.swamid.se/policy/assurance/al1"])
    assert _eq(ava["schacHomeOrganization"], ["example.com"])


@pytest.mark.skip("Temporarily disabled")
def test_filter_ava_refeds_personalized_access():
    entity_id = "https://personalized.example.edu/saml2/metadata/"
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)
    mds.imp([{"class": "saml2.mdstore.MetaDataFile", "metadata": [(full_path("entity_personalized_sp.xml"),)]}])

    policy_conf = {"default": {"lifetime": {"minutes": 15}, "entity_categories": ["swamid"]}}

    policy = Policy(policy_conf, mds)
    ava = {
        "displayName": ["Test Testsson"],
        "eduPersonAssurance": ["http://www.swamid.se/policy/assurance/al1"],
        "eduPersonScopedAffiliation": ["student@example.com"],
        "eduPersonTargetedID": "foo!bar!xyz",
        "givenName": ["Test"],
        "mail": ["test@example.com"],
        "pairwise-id": ["pairwise-id@example.com"],
        "schacHomeOrganization": ["example.com"],
        "sn": ["Testsson"],
        "subject-id": ["subject-id@example.com"],
    }

    ava = policy.filter(ava, entity_id)

    assert _eq(
        list(ava.keys()),
        [
            "subject-id",
            "mail",
            "displayName",
            "givenName",
            "sn",
            "eduPersonScopedAffiliation",
            "eduPersonAssurance",
            "schacHomeOrganization",
        ],
    )
    assert _eq(ava["subject-id"], ["subject-id@example.com"])
    assert _eq(ava["mail"], ["test@example.com"])
    assert _eq(ava["displayName"], ["Test Testsson"])
    assert _eq(ava["givenName"], ["Test"])
    assert _eq(ava["sn"], ["Testsson"])
    assert _eq(ava["eduPersonScopedAffiliation"], ["student@example.com"])
    assert _eq(ava["eduPersonAssurance"], ["http://www.swamid.se/policy/assurance/al1"])
    assert _eq(ava["schacHomeOrganization"], ["example.com"])
