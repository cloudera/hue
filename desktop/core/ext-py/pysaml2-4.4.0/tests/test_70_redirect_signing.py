from contextlib import closing
from saml2.pack import http_redirect_message
from saml2.sigver import verify_redirect_signature
from saml2.sigver import import_rsa_key_from_file
from saml2.sigver import SIG_RSA_SHA1
from saml2.server import Server
from saml2 import BINDING_HTTP_REDIRECT
from saml2.client import Saml2Client
from saml2.config import SPConfig
from six.moves.urllib.parse import parse_qs

from pathutils import dotname

__author__ = 'rolandh'


def list_values2simpletons(_dict):
    return dict([(k, v[0]) for k, v in _dict.items()])


def test():
    with closing(Server(config_file=dotname("idp_all_conf"))) as idp:
        conf = SPConfig()
        conf.load_file(dotname("servera_conf"))
        sp = Saml2Client(conf)

        srvs = sp.metadata.single_sign_on_service(idp.config.entityid,
                                                  BINDING_HTTP_REDIRECT)

        destination = srvs[0]["location"]
        req_id, req = sp.create_authn_request(destination, id="id1")

        signer = sp.sec.sec_backend.get_signer(SIG_RSA_SHA1)

        info = http_redirect_message(req, destination, relay_state="RS",
                                     typ="SAMLRequest", sigalg=SIG_RSA_SHA1,
                                     signer=signer)

        verified_ok = False

        for param, val in info["headers"]:
            if param == "Location":
                _dict = parse_qs(val.split("?")[1])
                _certs = idp.metadata.certs(sp.config.entityid, "any", "signing")
                for cert in _certs:
                    if verify_redirect_signature(
                            list_values2simpletons(_dict), sp.sec.sec_backend,
                            cert):
                        verified_ok = True

        assert verified_ok


if __name__ == "__main__":
    test()
