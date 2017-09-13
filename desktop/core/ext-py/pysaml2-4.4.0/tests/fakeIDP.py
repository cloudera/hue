from six.moves.urllib.parse import parse_qs
from saml2.authn_context import INTERNETPROTOCOLPASSWORD
from saml2.samlp import attribute_query_from_string, logout_request_from_string
from saml2 import BINDING_HTTP_REDIRECT, pack
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_SOAP
from saml2.server import Server
from saml2.soap import parse_soap_enveloped_saml_attribute_query
from saml2.soap import parse_soap_enveloped_saml_logout_request
from saml2.soap import make_soap_enveloped_saml_thingy

__author__ = 'rolandh'

TYP = {
    "GET": [BINDING_HTTP_REDIRECT],
    "POST": [BINDING_HTTP_POST, BINDING_SOAP]
}


AUTHN = {
    "class_ref": INTERNETPROTOCOLPASSWORD,
    "authn_auth": "http://www.example.com/login"
}


def unpack_form(_str, ver="SAMLRequest"):
    SR_STR = "name=\"%s\" value=\"" % ver
    RS_STR = 'name="RelayState" value="'

    i = _str.find(SR_STR)
    i += len(SR_STR)
    j = _str.find('"', i)

    sr = _str[i:j]

    k = _str.find(RS_STR, j)
    k += len(RS_STR)
    l = _str.find('"', k)

    rs = _str[k:l]

    return {ver: sr, "RelayState": rs}


class DummyResponse(object):
    def __init__(self, code, data, headers=None):
        self.status_code = code
        self.text = data
        self.headers = headers or []
        self.content = data


class FakeIDP(Server):
    def __init__(self, config_file=""):
        Server.__init__(self, config_file)
        #self.sign = False

    def receive(self, url, method="GET", **kwargs):
        """
        Interface to receive HTTP calls on

        :param url:
        :param method:
        :param kwargs:
        :return:
        """

        if method == "GET":
            path, query = url.split("?")
            qs_dict = parse_qs(kwargs["data"])
            req = qs_dict["SAMLRequest"][0]
            rstate = qs_dict["RelayState"][0]
        else:
            # Could be either POST or SOAP
            path = url
            try:
                qs_dict = parse_qs(kwargs["data"])
                req = qs_dict["SAMLRequest"][0]
                rstate = qs_dict["RelayState"][0]
            except KeyError:
                req = kwargs["data"]
                rstate = ""

        response = ""

        # Get service from path

        for key, vals in self.config.getattr("endpoints", "idp").items():
            for endp, binding in vals:
                if path == endp:
                    assert binding in TYP[method]
                    if key == "single_sign_on_service":
                        return self.authn_request_endpoint(req, binding,
                                                           rstate)
                    elif key == "single_logout_service":
                        return self.logout_endpoint(req, binding)

        for key, vals in self.config.getattr("endpoints", "aa").items():
            for endp, binding in vals:
                if path == endp:
                    assert binding in TYP[method]
                    if key == "attribute_service":
                        return self.attribute_query_endpoint(req, binding)

        return response

    def authn_request_endpoint(self, req, binding, relay_state):
        req = self.parse_authn_request(req, binding)
        if req.message.protocol_binding == BINDING_HTTP_REDIRECT:
            _binding = BINDING_HTTP_POST
        else:
            _binding = req.message.protocol_binding

        try:
            resp_args = self.response_args(req.message, [_binding])
        except Exception:
            raise

        identity = {"surName": "Hedberg", "givenName": "Roland",
                    "title": "supertramp", "mail": "roland@example.com"}
        userid = "Pavill"

        authn_resp = self.create_authn_response(identity,
                                                userid=userid,
                                                authn=AUTHN,
                                                **resp_args)

        response = "%s" % authn_resp

        _dict = pack.factory(_binding, response,
                             resp_args["destination"], relay_state,
                             "SAMLResponse")
        return DummyResponse(200, **_dict)

    def attribute_query_endpoint(self, xml_str, binding):
        if binding == BINDING_SOAP:
            _str = parse_soap_enveloped_saml_attribute_query(xml_str)
        else:
            _str = xml_str

        aquery = attribute_query_from_string(_str)
        extra = {"eduPersonAffiliation": "faculty"}
        #userid = "Pavill"

        name_id = aquery.subject.name_id
        attr_resp = self.create_attribute_response(
            extra, aquery.id, None, sp_entity_id=aquery.issuer.text,
            name_id=name_id, attributes=aquery.attribute)

        if binding == BINDING_SOAP:
            # SOAP packing
            #headers = {"content-type": "application/soap+xml"}
            soap_message = make_soap_enveloped_saml_thingy(attr_resp)
            #            if self.sign and self.sec:
            #                _signed = self.sec.sign_statement_using_xmlsec(soap_message,
            #                                                               class_name(attr_resp),
            #                                                               nodeid=attr_resp.id)
            #                soap_message = _signed
            response = "%s" % soap_message
        else:  # Just POST
            response = "%s" % attr_resp

        return DummyResponse(200, response)

    def logout_endpoint(self, xml_str, binding):
        if binding == BINDING_SOAP:
            _str = parse_soap_enveloped_saml_logout_request(xml_str)
        else:
            _str = xml_str

        req = logout_request_from_string(_str)

        _resp = self.create_logout_response(req, [binding])

        if binding == BINDING_SOAP:
            # SOAP packing
            #headers = {"content-type": "application/soap+xml"}
            soap_message = make_soap_enveloped_saml_thingy(_resp)
            #            if self.sign and self.sec:
            #                _signed = self.sec.sign_statement_using_xmlsec(soap_message,
            #                                                               class_name(attr_resp),
            #                                                               nodeid=attr_resp.id)
            #                soap_message = _signed
            response = "%s" % soap_message
        else: # Just POST
            response = "%s" % _resp

        return DummyResponse(200, response)
