# -*- coding: utf-8 -*-
from pymongo.errors import ConnectionFailure

__author__ = 'rolandh'

from saml2.attribute_converter import d_to_local_name
from saml2.attribute_converter import ac_factory
from saml2.mongo_store import export_mdstore_to_mongo_db
from saml2.mongo_store import MetadataMDB
from saml2.mdstore import MetadataStore
from saml2.mdstore import destinations
from saml2.mdstore import name

from saml2 import saml
from saml2 import md
from saml2 import config

from saml2.extension import mdui
from saml2.extension import idpdisc
from saml2.extension import dri
from saml2.extension import mdattr
from saml2.extension import ui
import xmldsig
import xmlenc

from pathutils import full_path

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

ATTRCONV = ac_factory(full_path("attributemaps"))


def _eq(l1, l2):
    return set(l1) == set(l2)


def test_metadata():
    conf = config.Config()
    conf.load_file("idp_conf_mdb")
    UMU_IDP = 'https://idp.umu.se/saml2/idp/metadata.php'
    # Set up a Metadata store
    mds = MetadataStore(ONTS.values(), ATTRCONV, conf,
                        disable_ssl_certificate_validation=True)

    # Import metadata from local file.
    mds.imp([{"class": "saml2.mdstore.MetaDataFile", "metadata": [(full_path("swamid-2.0.xml"), )]}])
    assert len(mds) == 1  # One source

    try:
        export_mdstore_to_mongo_db(mds, "metadata", "test")
    except ConnectionFailure:
        pass
    else:
        mdmdb = MetadataMDB(ONTS, ATTRCONV, "metadata", "test")
        # replace all metadata instances with this one
        mds.metadata = {"mongo_db": mdmdb}

        idps = mds.with_descriptor("idpsso")
        assert idps.keys()
        idpsso = mds.single_sign_on_service(UMU_IDP)
        assert len(idpsso) == 1
        assert destinations(idpsso) == [
            'https://idp.umu.se/saml2/idp/SSOService.php']

        _name = name(mds[UMU_IDP])
        assert _name == u'Ume\xe5 University'
        certs = mds.certs(UMU_IDP, "idpsso", "signing")
        assert len(certs) == 1

        sps = mds.with_descriptor("spsso")
        assert len(sps) == 417

        wants = mds.attribute_requirement('https://connect.sunet.se/shibboleth')
        assert wants["optional"] == []
        lnamn = [d_to_local_name(mds.attrc, attr) for attr in wants["required"]]
        assert _eq(lnamn, ['eduPersonPrincipalName', 'mail', 'givenName', 'sn',
                           'eduPersonScopedAffiliation', 'eduPersonAffiliation'])

        wants = mds.attribute_requirement(
            "https://gidp.geant.net/sp/module.php/saml/sp/metadata.php/default-sp")
        # Optional
        lnamn = [d_to_local_name(mds.attrc, attr) for attr in wants["optional"]]
        assert _eq(lnamn, ['displayName', 'commonName', 'schacHomeOrganization',
                           'eduPersonAffiliation', 'schacHomeOrganizationType'])
        # Required
        lnamn = [d_to_local_name(mds.attrc, attr) for attr in wants["required"]]
        assert _eq(lnamn, ['eduPersonTargetedID', 'mail',
                           'eduPersonScopedAffiliation'])

if __name__ == "__main__":
    test_metadata()
