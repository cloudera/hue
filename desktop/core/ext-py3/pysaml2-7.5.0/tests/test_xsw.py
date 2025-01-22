from unittest.mock import Mock
from unittest.mock import patch

from pathutils import dotname
from pathutils import full_path
from pytest import raises

from saml2.config import config_factory
from saml2.response import authn_response
from saml2.sigver import SignatureError


SIGNED_XSW_ASSERTION_WRAPPER = full_path("xsw/signed-xsw-assertion-wrapper.xml")
SIGNED_XSW_ASSERTION_EXTENSIONS = full_path("xsw/signed-xsw-assertion-extensions.xml")
SIGNED_XSW_ASSERTION_ASSERTION = full_path("xsw/signed-xsw-assertion-assertion.xml")

SIGNED_ASSERTION_FIRST_SIG = full_path("xsw/signed-xsw-assertion-in-assertion-first-sig.xml")
SIGNED_REPONSE_FIRST_SIG = full_path("xsw/signed-xsw-response-in-response-first-sig.xml")


class TestXSW:
    def setup_class(self):
        self.conf = config_factory("sp", dotname("server_conf"))
        self.ar = authn_response(self.conf, return_addrs="https://example.org/acs/post")

    @patch("saml2.response.validate_on_or_after", return_value=True)
    def test_signed_xsw_assertion_wrapper_should_fail(self, mock_validate_on_or_after):
        self.ar.issue_instant_ok = Mock(return_value=True)

        with open(SIGNED_XSW_ASSERTION_WRAPPER) as fp:
            xml_response = fp.read()

        self.ar.outstanding_queries = {"id-abc": "http://localhost:8088/sso"}
        self.ar.timeslack = 10000
        self.ar.loads(xml_response, decode=False)

        assert self.ar.came_from == "http://localhost:8088/sso"
        assert self.ar.session_id() == "id-abc"
        assert self.ar.issuer() == "urn:mace:example.com:saml:roland:idp"

        with raises(SignatureError):
            self.ar.verify()

        assert self.ar.ava is None
        assert self.ar.name_id is None

    @patch("saml2.response.validate_on_or_after", return_value=True)
    def test_signed_xsw_assertion_extensions_should_fail(self, mock_validate_on_or_after):
        self.ar.issue_instant_ok = Mock(return_value=True)

        with open(SIGNED_XSW_ASSERTION_EXTENSIONS) as fp:
            xml_response = fp.read()

        self.ar.outstanding_queries = {"id-abc": "http://localhost:8088/sso"}
        self.ar.timeslack = 10000
        self.ar.loads(xml_response, decode=False)

        assert self.ar.came_from == "http://localhost:8088/sso"
        assert self.ar.session_id() == "id-abc"
        assert self.ar.issuer() == "urn:mace:example.com:saml:roland:idp"

        with raises(SignatureError):
            self.ar.verify()

        assert self.ar.ava is None
        assert self.ar.name_id is None

    @patch("saml2.response.validate_on_or_after", return_value=True)
    def test_signed_xsw_assertion_assertion_should_fail(self, mock_validate_on_or_after):
        self.ar.issue_instant_ok = Mock(return_value=True)

        with open(SIGNED_XSW_ASSERTION_ASSERTION) as fp:
            xml_response = fp.read()

        self.ar.outstanding_queries = {"id-abc": "http://localhost:8088/sso"}
        self.ar.timeslack = 10000
        self.ar.loads(xml_response, decode=False)

        assert self.ar.came_from == "http://localhost:8088/sso"
        assert self.ar.session_id() == "id-abc"
        assert self.ar.issuer() == "urn:mace:example.com:saml:roland:idp"

        with raises(SignatureError):
            self.ar.verify()

        assert self.ar.ava is None
        assert self.ar.name_id is None


class TestInvalidDepthFirstSig:
    def setup_class(self):
        self.conf = config_factory("sp", dotname("server_conf"))
        self.ar = authn_response(self.conf, return_addrs="https://example.org/acs/post")

    @patch("saml2.response.validate_on_or_after", return_value=True)
    def test_signed_assertion_first_sig_should_fail(self, mock_validate_on_or_after):
        self.ar.issue_instant_ok = Mock(return_value=True)

        with open(SIGNED_ASSERTION_FIRST_SIG) as fp:
            xml_response = fp.read()

        self.ar.outstanding_queries = {"id-abc": "http://localhost:8088/sso"}
        self.ar.timeslack = 10000
        self.ar.loads(xml_response, decode=False)

        assert self.ar.came_from == "http://localhost:8088/sso"
        assert self.ar.session_id() == "id-abc"
        assert self.ar.issuer() == "urn:mace:example.com:saml:roland:idp"

        with raises(SignatureError):
            self.ar.verify()

        assert self.ar.ava is None
        assert self.ar.name_id is None

    @patch("saml2.response.validate_on_or_after", return_value=True)
    def test_signed_response_first_sig_should_fail(self, mock_validate_on_or_after):
        self.ar.issue_instant_ok = Mock(return_value=True)

        with open(SIGNED_REPONSE_FIRST_SIG) as fp:
            xml_response = fp.read()

        self.ar.outstanding_queries = {"id-abc": "http://localhost:8088/sso"}
        self.ar.timeslack = 10000
        with raises(SignatureError):
            self.ar.loads(xml_response, decode=False)
