from unittest.mock import Mock
from unittest.mock import patch

from pathutils import dotname
from pathutils import full_path
from pytest import raises

from saml2.config import config_factory
from saml2.response import authn_response
from saml2.sigver import SignatureError


SIGNED_RESPONSE_HMAC = full_path("xmlsec1-keydata/signed-response-with-hmac.xml")
SIGNED_ASSERTION_HMAC = full_path("xmlsec1-keydata/signed-assertion-with-hmac.xml")
SIGNED_ASSERTION_RANDOM_EMBEDDED_CERT = full_path("xmlsec1-keydata/signed-assertion-random-embedded-cert.xml")


class TestAuthnResponse:
    @patch("saml2.response.validate_on_or_after", return_value=True)
    def test_signed_response_with_hmac_should_fail(self, mock_validate_on_or_after):
        conf = config_factory("sp", dotname("server_conf"))
        ar = authn_response(conf, return_addrs="https://example.org/acs/post")
        ar.issue_instant_ok = Mock(return_value=True)

        with open(SIGNED_RESPONSE_HMAC) as fp:
            xml_response = fp.read()

        ar.outstanding_queries = {"id-abc": "http://localhost:8088/sso"}
        ar.timeslack = 10000

        # .loads checks the response signature
        with raises(SignatureError):
            ar.loads(xml_response, decode=False)

        assert ar.ava is None
        assert ar.name_id is None

    @patch("saml2.response.validate_on_or_after", return_value=True)
    def test_signed_assertion_with_hmac_should_fail(self, mock_validate_on_or_after):
        conf = config_factory("sp", dotname("server_conf"))
        ar = authn_response(conf, return_addrs="https://example.org/acs/post")
        ar.issue_instant_ok = Mock(return_value=True)

        with open(SIGNED_ASSERTION_HMAC) as fp:
            xml_response = fp.read()

        ar.outstanding_queries = {"id-abc": "http://localhost:8088/sso"}
        ar.timeslack = 10000

        # .loads does not check the assertion, only the response signature
        # use .verify to verify the contents of the response
        assert ar.loads(xml_response, decode=False)
        with raises(SignatureError):
            ar.verify()

        assert ar.ava is None
        assert ar.name_id is None

    @patch("saml2.response.validate_on_or_after", return_value=True)
    def test_signed_assertion_with_random_embedded_cert_should_be_ignored(self, mock_validate_on_or_after):
        """
        if the embedded cert is not ignored then verification will fail
        """

        conf = config_factory("sp", dotname("server_conf"))
        ar = authn_response(conf, return_addrs="https://51.15.251.81.xip.io/acs/post")
        ar.issue_instant_ok = Mock(return_value=True)

        with open(SIGNED_ASSERTION_RANDOM_EMBEDDED_CERT) as fp:
            xml_response = fp.read()

        ar.outstanding_queries = {"id-abc": "http://localhost:8088/sso"}
        ar.timeslack = 10000

        # .loads does not check the assertion, only the response signature
        # use .verify to verify the contents of the response
        assert ar.loads(xml_response, decode=False)
        assert ar.verify()
