import logging

from saml2 import BINDING_HTTP_REDIRECT
from saml2 import time_util
from saml2.attribute_converter import to_local
from saml2.response import IncorrectlySigned
from saml2.s_utils import OtherError
from saml2.s_utils import VersionMismatch
from saml2.sigver import verify_redirect_signature
from saml2.validate import NotValid
from saml2.validate import valid_instance


logger = logging.getLogger(__name__)


def _dummy(data, **_arg):
    return ""


class Request:
    def __init__(self, sec_context, receiver_addrs, attribute_converters=None, timeslack=0):
        self.sec = sec_context
        self.receiver_addrs = receiver_addrs
        self.timeslack = timeslack
        self.xmlstr = ""
        self.name_id = ""
        self.message = None
        self.not_on_or_after = 0
        self.attribute_converters = attribute_converters
        self.binding = None
        self.relay_state = ""
        self.signature_check = _dummy  # has to be set !!!

    def _clear(self):
        self.xmlstr = ""
        self.name_id = ""
        self.message = None
        self.not_on_or_after = 0

    def _loads(
        self,
        xmldata,
        binding=None,
        origdoc=None,
        must=None,
        only_valid_cert=False,
        relay_state=None,
        sigalg=None,
        signature=None,
    ):
        # own copy
        self.xmlstr = xmldata[:]
        logger.debug(
            "xmlstr: %s, relay_state: %s, sigalg: %s, signature: %s", self.xmlstr, relay_state, sigalg, signature
        )

        sign_redirect = must and binding == BINDING_HTTP_REDIRECT
        sign_post = must and not sign_redirect
        incorrectly_signed = IncorrectlySigned("Request was not signed correctly")

        try:
            self.message = self.signature_check(
                xmldata,
                origdoc=origdoc,
                must=sign_post,
                only_valid_cert=only_valid_cert,
            )
        except Exception as e:
            self.message = None
            raise incorrectly_signed from e

        if sign_redirect:
            if sigalg is None or signature is None:
                raise incorrectly_signed

            _saml_msg = {
                "SAMLRequest": origdoc,
                "Signature": signature,
                "SigAlg": sigalg,
            }
            if relay_state is not None:
                _saml_msg["RelayState"] = relay_state
            try:
                sig_verified = self._do_redirect_sig_check(_saml_msg)
            except Exception as e:
                self.message = None
                raise incorrectly_signed from e
            else:
                if not sig_verified:
                    self.message = None
                    raise incorrectly_signed

        if not self.message:
            logger.error("Request was not signed correctly")
            logger.info("Request data: %s", xmldata)
            raise incorrectly_signed

        logger.debug("Request message: %s", self.message)

        try:
            valid_instance(self.message)
        except NotValid as exc:
            logger.error("Request not valid: %s", exc.args[0])
            raise

        return self

    def _do_redirect_sig_check(self, _saml_msg):
        issuer = self.sender()
        certs = self.sec.metadata.certs(issuer, "any", "signing")
        logger.debug("Certs to verify request sig: %s, _saml_msg: %s", certs, _saml_msg)
        verified = any(verify_redirect_signature(_saml_msg, self.sec.sec_backend, cert) for cert_name, cert in certs)
        logger.debug("Redirect request signature check: %s", verified)
        return verified

    def issue_instant_ok(self):
        """Check that the request was issued at a reasonable time"""
        upper = time_util.shift_time(time_util.time_in_a_while(days=1), self.timeslack).timetuple()
        lower = time_util.shift_time(time_util.time_a_while_ago(days=1), -self.timeslack).timetuple()
        # print("issue_instant: %s" % self.message.issue_instant)
        # print("%s < x < %s" % (lower, upper))
        issued_at = time_util.str_to_time(self.message.issue_instant)
        return issued_at > lower and issued_at < upper

    def _verify(self):
        valid_version = "2.0"
        if self.message.version != valid_version:
            raise VersionMismatch(f"Invalid version {self.message.version} should be {valid_version}")

        if self.message.destination and self.receiver_addrs and self.message.destination not in self.receiver_addrs:
            logger.error("%s not in %s", self.message.destination, self.receiver_addrs)
            raise OtherError("Not destined for me!")

        valid = self.issue_instant_ok()
        return valid

    def loads(
        self,
        xmldata,
        binding,
        origdoc=None,
        must=None,
        only_valid_cert=False,
        relay_state=None,
        sigalg=None,
        signature=None,
    ):
        return self._loads(
            xmldata,
            binding,
            origdoc,
            must,
            only_valid_cert=only_valid_cert,
            relay_state=relay_state,
            sigalg=sigalg,
            signature=signature,
        )

    def verify(self):
        try:
            return self._verify()
        except AssertionError:
            return None

    def subject_id(self):
        """The name of the subject can be in either of
        BaseID, NameID or EncryptedID

        :return: The identifier if there is one
        """

        if "subject" in self.message.keys():
            _subj = self.message.subject
            if "base_id" in _subj.keys() and _subj.base_id:
                return _subj.base_id
            elif _subj.name_id:
                return _subj.name_id
        else:
            if "base_id" in self.message.keys() and self.message.base_id:
                return self.message.base_id
            elif self.message.name_id:
                return self.message.name_id
            else:  # EncryptedID
                pass

    def sender(self):
        return self.message.issuer.text.strip()


class LogoutRequest(Request):
    msgtype = "logout_request"

    def __init__(self, sec_context, receiver_addrs, attribute_converters=None, timeslack=0):
        Request.__init__(self, sec_context, receiver_addrs, attribute_converters, timeslack)
        self.signature_check = self.sec.correctly_signed_logout_request

    @property
    def issuer(self):
        return self.message.issuer


class AttributeQuery(Request):
    msgtype = "attribute_query"

    def __init__(self, sec_context, receiver_addrs, attribute_converters=None, timeslack=0):
        Request.__init__(self, sec_context, receiver_addrs, attribute_converters, timeslack)
        self.signature_check = self.sec.correctly_signed_attribute_query

    def attribute(self):
        """Which attributes that are sought for"""
        return []


class AuthnRequest(Request):
    msgtype = "authn_request"

    def __init__(self, sec_context, receiver_addrs, attribute_converters, timeslack=0):
        Request.__init__(self, sec_context, receiver_addrs, attribute_converters, timeslack)
        self.signature_check = self.sec.correctly_signed_authn_request

    def attributes(self):
        return to_local(self.attribute_converters, self.message)


class AuthnQuery(Request):
    msgtype = "authn_query"

    def __init__(self, sec_context, receiver_addrs, attribute_converters, timeslack=0):
        Request.__init__(self, sec_context, receiver_addrs, attribute_converters, timeslack)
        self.signature_check = self.sec.correctly_signed_authn_query

    def attributes(self):
        return to_local(self.attribute_converters, self.message)


class AssertionIDRequest(Request):
    msgtype = "assertion_id_request"

    def __init__(self, sec_context, receiver_addrs, attribute_converters, timeslack=0):
        Request.__init__(self, sec_context, receiver_addrs, attribute_converters, timeslack)
        self.signature_check = self.sec.correctly_signed_assertion_id_request

    def attributes(self):
        return to_local(self.attribute_converters, self.message)


class AuthzDecisionQuery(Request):
    msgtype = "authz_decision_query"

    def __init__(self, sec_context, receiver_addrs, attribute_converters=None, timeslack=0):
        Request.__init__(self, sec_context, receiver_addrs, attribute_converters, timeslack)
        self.signature_check = self.sec.correctly_signed_authz_decision_query

    def action(self):
        """Which action authorization is requested for"""

    def evidence(self):
        """The evidence on which the decision is based"""

    def resource(self):
        """On which resource the action is expected to occur"""


class NameIDMappingRequest(Request):
    msgtype = "name_id_mapping_request"

    def __init__(self, sec_context, receiver_addrs, attribute_converters, timeslack=0):
        Request.__init__(self, sec_context, receiver_addrs, attribute_converters, timeslack)
        self.signature_check = self.sec.correctly_signed_name_id_mapping_request


class ManageNameIDRequest(Request):
    msgtype = "manage_name_id_request"

    def __init__(self, sec_context, receiver_addrs, attribute_converters, timeslack=0):
        Request.__init__(self, sec_context, receiver_addrs, attribute_converters, timeslack)
        self.signature_check = self.sec.correctly_signed_manage_name_id_request


SERVICE2REQUEST = {
    "single_sign_on_service": AuthnRequest,
    "attribute_service": AttributeQuery,
    "authz_service": AuthzDecisionQuery,
    "assertion_id_request_service": AssertionIDRequest,
    "authn_query_service": AuthnQuery,
    "manage_name_id_service": ManageNameIDRequest,
    "name_id_mapping_service": NameIDMappingRequest,
    # "artifact_resolve_service": ArtifactResolve,
    "single_logout_service": LogoutRequest,
}
