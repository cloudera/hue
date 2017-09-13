from future.backports.urllib.parse import parse_qs
from future.backports.urllib.parse import urlencode
from future.backports.urllib.parse import urlparse

from saml2.entity import Entity
from saml2.response import VerificationError

__author__ = 'rolandh'

IDPDISC_POLICY = "urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol:single"


class DiscoveryServer(Entity):
    def __init__(self, config=None, config_file=""):
        if config or config_file:
            Entity.__init__(self, "disco", config, config_file)

    def parse_discovery_service_request(self, url="", query=""):
        if url:
            part = urlparse(url)
            dsr = parse_qs(part[4])
        elif query:
            dsr = parse_qs(query)
        else:
            dsr = {}

        # verify

        for key in ["isPassive", "return", "returnIDParam", "policy",
                    'entityID']:
            try:
                assert len(dsr[key]) == 1
                dsr[key] = dsr[key][0]
            except KeyError:
                pass

        if "return" in dsr:
            part = urlparse(dsr["return"])
            if part.query:
                qp = parse_qs(part.query)
                if "returnIDParam" in dsr:
                    assert dsr["returnIDParam"] not in qp.keys()
                else:
                    assert "entityID" not in qp.keys()
        else:
            # If metadata not used this is mandatory
            raise VerificationError("Missing mandatory parameter 'return'")

        if "policy" not in dsr:
            dsr["policy"] = IDPDISC_POLICY

        try:
            assert dsr["isPassive"] in ["true", "false"]
        except KeyError:
            pass

        if "isPassive" in dsr and dsr["isPassive"] == "true":
            dsr["isPassive"] = True
        else:
            dsr["isPassive"] = False

        if not "returnIDParam" in dsr:
            dsr["returnIDParam"] = "entityID"

        return dsr

    # -------------------------------------------------------------------------

    @staticmethod
    def create_discovery_service_response(return_url=None,
                                          returnIDParam="entityID",
                                          entity_id=None, **kwargs):
        if return_url is None:
            return_url = kwargs["return"]

        if entity_id:
            qp = urlencode({returnIDParam: entity_id})

            part = urlparse(return_url)
            if part.query:
                # Iff there is a query part add the new info at the end
                return_url = "%s&%s" % (return_url, qp)
            else:
                return_url = "%s?%s" % (return_url, qp)

        return return_url

    def verify_sp_in_metadata(self, entity_id):
        if self.metadata:
            endp = self.metadata.discovery_response(entity_id)
            if endp:
                return True

        return False

    def verify_return(self, entity_id, return_url):
        for endp in self.metadata.discovery_response(entity_id):
            try:
                assert return_url.startswith(endp["location"])
            except AssertionError:
                pass
            else:
                return True
        return False
