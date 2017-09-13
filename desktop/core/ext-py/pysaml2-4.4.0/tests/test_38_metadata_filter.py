from saml2 import md
from saml2 import saml
from saml2 import config
from saml2 import xmldsig
from saml2 import xmlenc

from saml2.filter import AllowDescriptor
from saml2.mdstore import MetadataStore
from saml2.attribute_converter import ac_factory
from saml2.extension import mdui
from saml2.extension import idpdisc
from saml2.extension import dri
from saml2.extension import mdattr
from saml2.extension import ui

from pathutils import full_path

__author__ = 'roland'

sec_config = config.Config()


ATTRCONV = ac_factory(full_path("attributemaps"))

METADATACONF = {
    "1": [{
        "class": "saml2.mdstore.MetaDataFile",
        "metadata": [(full_path("swamid-2.0.xml"), )],
    }],
}

def test_swamid_sp():
    mds = MetadataStore(ATTRCONV, sec_config,
                        disable_ssl_certificate_validation=True,
                        filter=AllowDescriptor(["spsso"]))

    mds.imp(METADATACONF["1"])
    sps = mds.with_descriptor("spsso")
    assert len(sps) == 417
    idps = mds.with_descriptor("idpsso")
    assert idps == {}

def test_swamid_idp():
    mds = MetadataStore(ATTRCONV, sec_config,
                        disable_ssl_certificate_validation=True,
                        filter=AllowDescriptor(["idpsso"]))

    mds.imp(METADATACONF["1"])
    sps = mds.with_descriptor("spsso")
    assert len(sps) == 0
    idps = mds.with_descriptor("idpsso")
    assert len(idps) == 275

if __name__ == "__main__":
    test_swamid_idp()
