from urllib import parse

from saml2.entity import Entity
from saml2.response import VerificationError


__author__ = "rolandh"

IDPDISC_POLICY = "urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol:single"


class DiscoveryServer(Entity):
    def __init__(self, config=None, config_file=""):
        if config or config_file:
            Entity.__init__(self, "disco", config, config_file)

    def parse_discovery_service_request(self, url="", query=""):
        if url:
            part = parse.urlparse(url)
            dsr = parse.parse_qs(part[4])
        elif query:
            dsr = parse.parse_qs(query)
        else:
            dsr = {}

        # verify

        for key in ["isPassive", "return", "returnIDParam", "policy", "entityID"]:
            try:
                if len(dsr[key]) != 1:
                    raise Exception(f"Invalid DS request keys: {key}")
                dsr[key] = dsr[key][0]
            except KeyError:
                pass

        if "return" in dsr:
            part = parse.urlparse(dsr["return"])
            if part.query:
                qp = parse.parse_qs(part.query)
                if "returnIDParam" in dsr:
                    if dsr["returnIDParam"] in qp.keys():
                        raise Exception("returnIDParam value should not be in the query params")
                else:
                    if "entityID" in qp.keys():
                        raise Exception("entityID should not be in the query params")
        else:
            # If metadata not used this is mandatory
            raise VerificationError("Missing mandatory parameter 'return'")

        if "policy" not in dsr:
            dsr["policy"] = IDPDISC_POLICY

        is_passive = dsr.get("isPassive")
        if is_passive not in ["true", "false"]:
            raise ValueError(f"Invalid value '{is_passive}' for attribute 'isPassive'")

        if "isPassive" in dsr and dsr["isPassive"] == "true":
            dsr["isPassive"] = True
        else:
            dsr["isPassive"] = False

        if "returnIDParam" not in dsr:
            dsr["returnIDParam"] = "entityID"

        return dsr

    # -------------------------------------------------------------------------

    @staticmethod
    def create_discovery_service_response(return_url=None, returnIDParam="entityID", entity_id=None, **kwargs):
        if return_url is None:
            return_url = kwargs["return"]

        if entity_id:
            qp = parse.urlencode({returnIDParam: entity_id})

            part = parse.urlparse(return_url)
            if part.query:
                # Iff there is a query part add the new info at the end
                return_url = f"{return_url}&{qp}"
            else:
                return_url = f"{return_url}?{qp}"

        return return_url

    def verify_sp_in_metadata(self, entity_id):
        if self.metadata:
            endp = self.metadata.discovery_response(entity_id)
            if endp:
                return True

        return False

    def verify_return(self, entity_id, return_url):
        for endp in self.metadata.discovery_response(entity_id):
            if not return_url.startswith(endp["location"]):
                return True
        return False
