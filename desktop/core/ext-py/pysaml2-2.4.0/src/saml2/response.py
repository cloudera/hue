#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import calendar
import logging
from saml2.samlp import STATUS_VERSION_MISMATCH
from saml2.samlp import STATUS_AUTHN_FAILED
from saml2.samlp import STATUS_INVALID_ATTR_NAME_OR_VALUE
from saml2.samlp import STATUS_INVALID_NAMEID_POLICY
from saml2.samlp import STATUS_NO_AUTHN_CONTEXT
from saml2.samlp import STATUS_NO_AVAILABLE_IDP
from saml2.samlp import STATUS_NO_PASSIVE
from saml2.samlp import STATUS_NO_SUPPORTED_IDP
from saml2.samlp import STATUS_PARTIAL_LOGOUT
from saml2.samlp import STATUS_PROXY_COUNT_EXCEEDED
from saml2.samlp import STATUS_REQUEST_DENIED
from saml2.samlp import STATUS_REQUEST_UNSUPPORTED
from saml2.samlp import STATUS_REQUEST_VERSION_DEPRECATED
from saml2.samlp import STATUS_REQUEST_VERSION_TOO_HIGH
from saml2.samlp import STATUS_REQUEST_VERSION_TOO_LOW
from saml2.samlp import STATUS_RESOURCE_NOT_RECOGNIZED
from saml2.samlp import STATUS_TOO_MANY_RESPONSES
from saml2.samlp import STATUS_UNKNOWN_ATTR_PROFILE
from saml2.samlp import STATUS_UNKNOWN_PRINCIPAL
from saml2.samlp import STATUS_UNSUPPORTED_BINDING
from saml2.samlp import STATUS_RESPONDER

import xmldsig as ds
import xmlenc as xenc

from saml2 import samlp
from saml2 import class_name
from saml2 import saml
from saml2 import extension_elements_to_elements
from saml2 import SAMLError
from saml2 import time_util

from saml2.s_utils import RequestVersionTooLow
from saml2.s_utils import RequestVersionTooHigh
from saml2.saml import attribute_from_string, XSI_TYPE
from saml2.saml import SCM_BEARER
from saml2.saml import SCM_HOLDER_OF_KEY
from saml2.saml import SCM_SENDER_VOUCHES
from saml2.saml import encrypted_attribute_from_string
from saml2.sigver import security_context
from saml2.sigver import SignatureError
from saml2.sigver import signed
from saml2.attribute_converter import to_local
from saml2.time_util import str_to_time, later_than

from saml2.validate import validate_on_or_after
from saml2.validate import validate_before
from saml2.validate import valid_instance
from saml2.validate import valid_address
from saml2.validate import NotValid

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------


class IncorrectlySigned(SAMLError):
    pass


class DecryptionFailed(SAMLError):
    pass


class VerificationError(SAMLError):
    pass


class StatusError(SAMLError):
    pass


class UnsolicitedResponse(SAMLError):
    pass


class StatusVersionMismatch(StatusError):
    pass


class StatusAuthnFailed(StatusError):
    pass


class StatusInvalidAttrNameOrValue(StatusError):
    pass


class StatusInvalidNameidPolicy(StatusError):
    pass


class StatusNoAuthnContext(StatusError):
    pass


class StatusNoAvailableIdp(StatusError):
    pass


class StatusNoPassive(StatusError):
    pass


class StatusNoSupportedIdp(StatusError):
    pass


class StatusPartialLogout(StatusError):
    pass


class StatusProxyCountExceeded(StatusError):
    pass


class StatusRequestDenied(StatusError):
    pass


class StatusRequestUnsupported(StatusError):
    pass


class StatusRequestVersionDeprecated(StatusError):
    pass


class StatusRequestVersionTooHigh(StatusError):
    pass


class StatusRequestVersionTooLow(StatusError):
    pass


class StatusResourceNotRecognized(StatusError):
    pass


class StatusTooManyResponses(StatusError):
    pass


class StatusUnknownAttrProfile(StatusError):
    pass


class StatusUnknownPrincipal(StatusError):
    pass


class StatusUnsupportedBinding(StatusError):
    pass

class StatusResponder(StatusError):
    pass

STATUSCODE2EXCEPTION = {
    STATUS_VERSION_MISMATCH: StatusVersionMismatch,
    STATUS_AUTHN_FAILED: StatusAuthnFailed,
    STATUS_INVALID_ATTR_NAME_OR_VALUE: StatusInvalidAttrNameOrValue,
    STATUS_INVALID_NAMEID_POLICY: StatusInvalidNameidPolicy,
    STATUS_NO_AUTHN_CONTEXT: StatusNoAuthnContext,
    STATUS_NO_AVAILABLE_IDP: StatusNoAvailableIdp,
    STATUS_NO_PASSIVE: StatusNoPassive,
    STATUS_NO_SUPPORTED_IDP: StatusNoSupportedIdp,
    STATUS_PARTIAL_LOGOUT: StatusPartialLogout,
    STATUS_PROXY_COUNT_EXCEEDED: StatusProxyCountExceeded,
    STATUS_REQUEST_DENIED: StatusRequestDenied,
    STATUS_REQUEST_UNSUPPORTED: StatusRequestUnsupported,
    STATUS_REQUEST_VERSION_DEPRECATED: StatusRequestVersionDeprecated,
    STATUS_REQUEST_VERSION_TOO_HIGH: StatusRequestVersionTooHigh,
    STATUS_REQUEST_VERSION_TOO_LOW: StatusRequestVersionTooLow,
    STATUS_RESOURCE_NOT_RECOGNIZED: StatusResourceNotRecognized,
    STATUS_TOO_MANY_RESPONSES: StatusTooManyResponses,
    STATUS_UNKNOWN_ATTR_PROFILE: StatusUnknownAttrProfile,
    STATUS_UNKNOWN_PRINCIPAL: StatusUnknownPrincipal,
    STATUS_UNSUPPORTED_BINDING: StatusUnsupportedBinding,
    STATUS_RESPONDER: StatusResponder,
}
# ---------------------------------------------------------------------------


def _dummy(_):
    return None


def for_me(conditions, myself):
    """ Am I among the intended audiences """

    if not conditions.audience_restriction:  # No audience restriction
        return True

    for restriction in conditions.audience_restriction:
        if not restriction.audience:
            continue
        for audience in restriction.audience:
            if audience.text.strip() == myself:
                return True
            else:
                #print "Not for me: %s != %s" % (audience.text.strip(), myself)
                pass

    return False


def authn_response(conf, return_addrs, outstanding_queries=None, timeslack=0,
                   asynchop=True, allow_unsolicited=False,
                   want_assertions_signed=False):
    sec = security_context(conf)
    if not timeslack:
        try:
            timeslack = int(conf.accepted_time_diff)
        except TypeError:
            timeslack = 0

    return AuthnResponse(sec, conf.attribute_converters, conf.entityid,
                         return_addrs, outstanding_queries, timeslack,
                         asynchop=asynchop, allow_unsolicited=allow_unsolicited,
                         want_assertions_signed=want_assertions_signed)


# comes in over SOAP so synchronous
def attribute_response(conf, return_addrs, timeslack=0, asynchop=False,
                       test=False):
    sec = security_context(conf)
    if not timeslack:
        try:
            timeslack = int(conf.accepted_time_diff)
        except TypeError:
            timeslack = 0

    return AttributeResponse(sec, conf.attribute_converters, conf.entityid,
                             return_addrs, timeslack, asynchop=asynchop,
                             test=test)


class StatusResponse(object):
    msgtype = "status_response"

    def __init__(self, sec_context, return_addrs=None, timeslack=0,
                 request_id=0, asynchop=True):
        self.sec = sec_context
        self.return_addrs = return_addrs

        self.timeslack = timeslack
        self.request_id = request_id

        self.xmlstr = ""
        self.origxml = ""
        self.name_id = None
        self.response = None
        self.not_on_or_after = 0
        self.in_response_to = None
        self.signature_check = self.sec.correctly_signed_response
        self.require_signature = False
        self.require_response_signature = False
        self.not_signed = False
        self.asynchop = asynchop

    def _clear(self):
        self.xmlstr = ""
        self.name_id = None
        self.response = None
        self.not_on_or_after = 0

    def _postamble(self):
        if not self.response:
            logger.error("Response was not correctly signed")
            if self.xmlstr:
                logger.info(self.xmlstr)
            raise IncorrectlySigned()

        logger.debug("response: %s" % (self.response,))

        try:
            valid_instance(self.response)
        except NotValid as exc:
            logger.error("Not valid response: %s" % exc.args[0])
            self._clear()
            return self

        self.in_response_to = self.response.in_response_to
        return self

    def load_instance(self, instance):
        if signed(instance):
            # This will check signature on Assertion which is the default
            try:
                self.response = self.sec.check_signature(instance)
            except SignatureError:
                # The response as a whole might be signed or not
                self.response = self.sec.check_signature(
                    instance, samlp.NAMESPACE + ":Response")
        else:
            self.not_signed = True
            self.response = instance

        return self._postamble()

    def _loads(self, xmldata, decode=True, origxml=None):

        # own copy
        self.xmlstr = xmldata[:]
        logger.debug("xmlstr: %s" % (self.xmlstr,))
        if origxml:
            self.origxml = origxml
        else:
            self.origxml = self.xmlstr

        try:
            self.response = self.signature_check(
                xmldata, origdoc=origxml, must=self.require_signature,
                require_response_signature=self.require_response_signature)

        except TypeError:
            raise
        except SignatureError:
            raise
        except Exception as excp:
            logger.exception("EXCEPTION: %s", excp)
            raise

        #print "<", self.response

        return self._postamble()

    def status_ok(self):
        if self.response.status:
            status = self.response.status
            logger.info("status: %s" % (status,))
            if status.status_code.value != samlp.STATUS_SUCCESS:
                logger.info("Not successful operation: %s" % status)
                if status.status_code.status_code:
                    excep = STATUSCODE2EXCEPTION[
                        status.status_code.status_code.value]
                else:
                    excep = StatusError
                if status.status_message:
                    msg = status.status_message.text
                else:
                    try:
                        msg = status.status_code.status_code.value
                    except Exception:
                        msg = "Unknown error"
                raise excep(
                    "%s from %s" % (msg, status.status_code.value,))
        return True

    def issue_instant_ok(self):
        """ Check that the response was issued at a reasonable time """
        upper = time_util.shift_time(time_util.time_in_a_while(days=1),
                                     self.timeslack).timetuple()
        lower = time_util.shift_time(time_util.time_a_while_ago(days=1),
                                     -self.timeslack).timetuple()
        # print "issue_instant: %s" % self.response.issue_instant
        # print "%s < x < %s" % (lower, upper)
        issued_at = str_to_time(self.response.issue_instant)
        return lower < issued_at < upper

    def _verify(self):
        if self.request_id and self.in_response_to and \
                        self.in_response_to != self.request_id:
            logger.error("Not the id I expected: %s != %s" % (
                self.in_response_to, self.request_id))
            return None

        try:
            assert self.response.version == "2.0"
        except AssertionError:
            _ver = float(self.response.version)
            if _ver < 2.0:
                raise RequestVersionTooLow()
            else:
                raise RequestVersionTooHigh()

        if self.asynchop:
            if self.response.destination and \
                    self.response.destination not in self.return_addrs:
                logger.error("%s not in %s" % (self.response.destination,
                                               self.return_addrs))
                return None

        assert self.issue_instant_ok()
        assert self.status_ok()
        return self

    def loads(self, xmldata, decode=True, origxml=None):
        return self._loads(xmldata, decode, origxml)

    def verify(self, key_file=""):
        try:
            return self._verify()
        except AssertionError:
            logger.exception("verify")
            return None

    def update(self, mold):
        self.xmlstr = mold.xmlstr
        self.in_response_to = mold.in_response_to
        self.response = mold.response

    def issuer(self):
        return self.response.issuer.text.strip()


class LogoutResponse(StatusResponse):
    msgtype = "logout_response"

    def __init__(self, sec_context, return_addrs=None, timeslack=0,
                 asynchop=True):
        StatusResponse.__init__(self, sec_context, return_addrs, timeslack,
                                asynchop=asynchop)
        self.signature_check = self.sec.correctly_signed_logout_response


class NameIDMappingResponse(StatusResponse):
    msgtype = "name_id_mapping_response"

    def __init__(self, sec_context, return_addrs=None, timeslack=0,
                 request_id=0, asynchop=True):
        StatusResponse.__init__(self, sec_context, return_addrs, timeslack,
                                request_id, asynchop)
        self.signature_check = self.sec\
            .correctly_signed_name_id_mapping_response


class ManageNameIDResponse(StatusResponse):
    msgtype = "manage_name_id_response"

    def __init__(self, sec_context, return_addrs=None, timeslack=0,
                 request_id=0, asynchop=True):
        StatusResponse.__init__(self, sec_context, return_addrs, timeslack,
                                request_id, asynchop)
        self.signature_check = self.sec.correctly_signed_manage_name_id_response


# ----------------------------------------------------------------------------


class AuthnResponse(StatusResponse):
    """ This is where all the profile compliance is checked.
    This one does saml2int compliance. """
    msgtype = "authn_response"

    def __init__(self, sec_context, attribute_converters, entity_id,
                 return_addrs=None, outstanding_queries=None,
                 timeslack=0, asynchop=True, allow_unsolicited=False,
                 test=False, allow_unknown_attributes=False,
                 want_assertions_signed=False, want_response_signed=False,
                 **kwargs):

        StatusResponse.__init__(self, sec_context, return_addrs, timeslack,
                                asynchop=asynchop)
        self.entity_id = entity_id
        self.attribute_converters = attribute_converters
        if outstanding_queries:
            self.outstanding_queries = outstanding_queries
        else:
            self.outstanding_queries = {}
        self.context = "AuthnReq"
        self.came_from = None
        self.ava = None
        self.assertion = None
        self.assertions = []
        self.session_not_on_or_after = 0
        self.allow_unsolicited = allow_unsolicited
        self.require_signature = want_assertions_signed
        self.require_response_signature = want_response_signed
        self.test = test
        self.allow_unknown_attributes = allow_unknown_attributes
        #
        try:
            self.extension_schema = kwargs["extension_schema"]
        except KeyError:
            self.extension_schema = {}

    def check_subject_confirmation_in_response_to(self, irp):
        for assertion in self.response.assertion:
            for _sc in assertion.subject.subject_confirmation:
                try:
                    assert _sc.subject_confirmation_data.in_response_to == irp
                except AssertionError:
                    return False

        return True

    def loads(self, xmldata, decode=True, origxml=None):
        self._loads(xmldata, decode, origxml)

        if self.asynchop:
            if self.in_response_to in self.outstanding_queries:
                self.came_from = self.outstanding_queries[self.in_response_to]
                #del self.outstanding_queries[self.in_response_to]
                try:
                    if not self.check_subject_confirmation_in_response_to(
                            self.in_response_to):
                        logger.exception(
                            "Unsolicited response %s" % self.in_response_to)
                        raise UnsolicitedResponse(
                            "Unsolicited response: %s" % self.in_response_to)
                except AttributeError:
                    pass
            elif self.allow_unsolicited:
                pass
            else:
                logger.exception(
                    "Unsolicited response %s" % self.in_response_to)
                raise UnsolicitedResponse(
                    "Unsolicited response: %s" % self.in_response_to)

        return self

    def clear(self):
        self._clear()
        self.came_from = None
        self.ava = None
        self.assertion = None

    def authn_statement_ok(self, optional=False):
        try:
            # the assertion MUST contain one AuthNStatement
            assert len(self.assertion.authn_statement) == 1
        except AssertionError:
            if optional:
                return True
            else:
                logger.error("No AuthnStatement")
                raise

        authn_statement = self.assertion.authn_statement[0]
        if authn_statement.session_not_on_or_after:
            if validate_on_or_after(authn_statement.session_not_on_or_after,
                                    self.timeslack):
                self.session_not_on_or_after = calendar.timegm(
                    time_util.str_to_time(
                        authn_statement.session_not_on_or_after))
            else:
                return False
        return True
        # check authn_statement.session_index

    def condition_ok(self, lax=False):
        if self.test:
            lax = True

        # The Identity Provider MUST include a <saml:Conditions> element
        assert self.assertion.conditions
        conditions = self.assertion.conditions

        logger.debug("conditions: %s" % conditions)

        # if no sub-elements or elements are supplied, then the
        # assertion is considered to be valid.
        if not conditions.keyswv():
            return True

        # if both are present NotBefore must be earlier than NotOnOrAfter
        if conditions.not_before and conditions.not_on_or_after:
            if not later_than(conditions.not_on_or_after,
                              conditions.not_before):
                return False

        try:
            if conditions.not_on_or_after:
                self.not_on_or_after = validate_on_or_after(
                    conditions.not_on_or_after, self.timeslack)
            if conditions.not_before:
                validate_before(conditions.not_before, self.timeslack)
        except Exception as excp:
            logger.error("Exception on conditions: %s" % (excp,))
            if not lax:
                raise
            else:
                self.not_on_or_after = 0

        if not self.allow_unsolicited:
            if not for_me(conditions, self.entity_id):
                if not lax:
                    raise Exception("Not for me!!!")

        if conditions.condition:  # extra conditions
            for cond in conditions.condition:
                try:
                    if cond.extension_attributes[
                        XSI_TYPE] in self.extension_schema:
                        pass
                    else:
                        raise Exception("Unknown condition")
                except KeyError:
                    raise Exception("Missing xsi:type specification")

        return True

    def decrypt_attributes(self, attribute_statement):
        """
        Decrypts possible encrypted attributes and adds the decrypts to the
        list of attributes.

        :param attribute_statement: A SAML.AttributeStatement which might
            contain both encrypted attributes and attributes.
        """
        #        _node_name = [
        #            "urn:oasis:names:tc:SAML:2.0:assertion:EncryptedData",
        #            "urn:oasis:names:tc:SAML:2.0:assertion:EncryptedAttribute"]

        for encattr in attribute_statement.encrypted_attribute:
            if not encattr.encrypted_key:
                _decr = self.sec.decrypt(encattr.encrypted_data)
                _attr = attribute_from_string(_decr)
                attribute_statement.attribute.append(_attr)
            else:
                _decr = self.sec.decrypt(encattr)
                enc_attr = encrypted_attribute_from_string(_decr)
                attrlist = enc_attr.extensions_as_elements("Attribute", saml)
                attribute_statement.attribute.extend(attrlist)

    def get_identity(self):
        """ The assertion can contain zero or one attributeStatements

        """
        if not self.assertion.attribute_statement:
            logger.error("Missing Attribute Statement")
            ava = {}
        else:
            assert len(self.assertion.attribute_statement) == 1
            _attr_statem = self.assertion.attribute_statement[0]

            logger.debug("Attribute Statement: %s" % (_attr_statem,))
            for aconv in self.attribute_converters:
                logger.debug("Converts name format: %s" % (aconv.name_format,))

            self.decrypt_attributes(_attr_statem)
            ava = to_local(self.attribute_converters, _attr_statem,
                           self.allow_unknown_attributes)
        return ava

    def _bearer_confirmed(self, data):
        if not data:
            return False

        if data.address:
            if not valid_address(data.address):
                return False
                # verify that I got it from the correct sender

        # These two will raise exception if untrue
        validate_on_or_after(data.not_on_or_after, self.timeslack)
        validate_before(data.not_before, self.timeslack)

        # not_before must be < not_on_or_after
        if not later_than(data.not_on_or_after, data.not_before):
            return False

        if self.asynchop and self.came_from is None:
            if data.in_response_to:
                if data.in_response_to in self.outstanding_queries:
                    self.came_from = self.outstanding_queries[
                        data.in_response_to]
                    #del self.outstanding_queries[data.in_response_to]
                elif self.allow_unsolicited:
                    pass
                else:
                    # This is where I don't allow unsolicited reponses
                    # Either in_response_to == None or has a value I don't
                    # recognize
                    logger.debug("in response to: '%s'" % data.in_response_to)
                    logger.info("outstanding queries: %s" % (
                        self.outstanding_queries.keys(),))
                    raise Exception(
                        "Combination of session id and requestURI I don't "
                        "recall")
        return True

    def _holder_of_key_confirmed(self, data):
        if not data:
            return False

        has_keyinfo = False
        for element in extension_elements_to_elements(data,
                                                      [samlp, saml, xenc, ds]):
            if isinstance(element, ds.KeyInfo):
                has_keyinfo = True

        return has_keyinfo

    def get_subject(self):
        """ The assertion must contain a Subject
        """
        assert self.assertion.subject
        subject = self.assertion.subject
        subjconf = []
        for subject_confirmation in subject.subject_confirmation:
            _data = subject_confirmation.subject_confirmation_data

            if subject_confirmation.method == SCM_BEARER:
                if not self._bearer_confirmed(_data):
                    continue
            elif subject_confirmation.method == SCM_HOLDER_OF_KEY:
                if not self._holder_of_key_confirmed(_data):
                    continue
            elif subject_confirmation.method == SCM_SENDER_VOUCHES:
                pass
            else:
                raise ValueError("Unknown subject confirmation method: %s" % (
                    subject_confirmation.method,))

            subjconf.append(subject_confirmation)

        if not subjconf:
            raise VerificationError("No valid subject confirmation")

        subject.subject_confirmation = subjconf

        # The subject must contain a name_id
        try:
            assert subject.name_id
            self.name_id = subject.name_id
        except AssertionError:
            if subject.encrypted_id:
                # decrypt encrypted ID
                _name_id_str = self.sec.decrypt(
                    subject.encrypted_id.encrypted_data.to_string())
                _name_id = saml.name_id_from_string(_name_id_str)
                self.name_id = _name_id
            else:
                raise VerificationError("Missing NameID")

        logger.info("Subject NameID: %s" % self.name_id)
        return self.name_id

    def _assertion(self, assertion, verified=False):
        """
        Check the assertion
        :param assertion:
        :return: True/False depending on if the assertion is sane or not
        """

        if not hasattr(assertion, 'signature') or not assertion.signature:
            logger.debug("unsigned")
            if self.require_signature:
                raise SignatureError("Signature missing for assertion")
        else:
            logger.debug("signed")

            if not verified:
                try:
                    self.sec.check_signature(assertion, class_name(assertion),
                                             self.xmlstr)
                except Exception as exc:
                    logger.error("correctly_signed_response: %s" % exc)
                    raise

        self.assertion = assertion
        logger.debug("assertion context: %s" % (self.context,))
        logger.debug("assertion keys: %s" % (assertion.keyswv()))
        logger.debug("outstanding_queries: %s" % (self.outstanding_queries,))

        #if self.context == "AuthnReq" or self.context == "AttrQuery":
        if self.context == "AuthnReq":
            self.authn_statement_ok()
        #        elif self.context == "AttrQuery":
        #            self.authn_statement_ok(True)

        if not self.condition_ok():
            raise VerificationError("Condition not OK")

        logger.debug("--- Getting Identity ---")

        if self.context == "AuthnReq" or self.context == "AttrQuery":
            self.ava = self.get_identity()

            logger.debug("--- AVA: %s" % (self.ava,))

        try:
            self.get_subject()
            if self.asynchop:
                if self.allow_unsolicited:
                    pass
                elif self.came_from is None:
                    raise VerificationError("Came from")
            return True
        except Exception:
            logger.exception("get subject")
            raise

    def decrypt_assertions(self, encrypted_assertions, decr_txt):
        res = []
        for encrypted_assertion in encrypted_assertions:
            if encrypted_assertion.extension_elements:
                assertions = extension_elements_to_elements(
                    encrypted_assertion.extension_elements, [saml, samlp])
                for assertion in assertions:
                    if assertion.signature:
                        if not self.sec.check_signature(
                                assertion, origdoc=decr_txt,
                                node_name=class_name(assertion)):
                            logger.error(
                                "Failed to verify signature on '%s'" % assertion)
                            raise SignatureError()
                    res.append(assertion)
        return res

    def parse_assertion(self, key_file=""):
        if self.context == "AuthnQuery":
            # can contain one or more assertions
            pass
        else:  # This is a saml2int limitation
            try:
                assert len(self.response.assertion) == 1 or \
                    len(self.response.encrypted_assertion) == 1
            except AssertionError:
                raise Exception("No assertion part")

        res = []
        if self.response.encrypted_assertion:
            logger.debug("***Encrypted assertion/-s***")
            decr_text = self.sec.decrypt(self.xmlstr, key_file)
            resp = samlp.response_from_string(decr_text)
            res = self.decrypt_assertions(resp.encrypted_assertion, decr_text)
            if self.response.assertion:
                self.response.assertion.extend(res)
            else:
                self.response.assertion = res
            self.response.encrypted_assertion = []
            self.xmlstr = decr_text

        if self.response.assertion:
            logger.debug("***Unencrypted assertion***")
            for assertion in self.response.assertion:
                if not self._assertion(assertion, assertion in res):
                    return False
                else:
                    self.assertions.append(assertion)
            self.assertion = self.assertions[0]

        return True

    def verify(self, key_file=""):
        """ Verify that the assertion is syntactically correct and
        the signature is correct if present.
        :param key_file: If not the default key file should be used this is it.
        """

        try:
            res = self._verify()
        except AssertionError as err:
            logger.error("Verification error on the response: %s" % err)
            raise
        else:
            if res is None:
                return None

        if not isinstance(self.response, samlp.Response):
            return self

        if self.parse_assertion(key_file):
            return self
        else:
            logger.error("Could not parse the assertion")
            return None

    def session_id(self):
        """ Returns the SessionID of the response """
        return self.response.in_response_to

    def id(self):
        """ Return the ID of the response """
        return self.response.id

    def authn_info(self):
        res = []
        for astat in self.assertion.authn_statement:
            context = astat.authn_context
            if context:
                try:
                    aclass = context.authn_context_class_ref.text
                except AttributeError:
                    aclass = ""
                try:
                    authn_auth = [a.text for a in
                                  context.authenticating_authority]
                except AttributeError:
                    authn_auth = []
                res.append((aclass, authn_auth))
        return res

    def authz_decision_info(self):
        res = {"permit": [], "deny": [], "indeterminate": []}
        for adstat in self.assertion.authz_decision_statement:
            # one of 'Permit', 'Deny', 'Indeterminate'
            res[adstat.decision.text.lower()] = adstat
        return res

    def session_info(self):
        """ Returns a predefined set of information gleened from the
        response.
        :returns: Dictionary with information
        """
        if self.session_not_on_or_after > 0:
            nooa = self.session_not_on_or_after
        else:
            nooa = self.not_on_or_after

        if self.context == "AuthzQuery":
            return {"name_id": self.name_id, "came_from": self.came_from,
                    "issuer": self.issuer(), "not_on_or_after": nooa,
                    "authz_decision_info": self.authz_decision_info()}
        else:
            return {"ava": self.ava, "name_id": self.name_id,
                    "came_from": self.came_from, "issuer": self.issuer(),
                    "not_on_or_after": nooa, "authn_info": self.authn_info()}

    def __str__(self):
        return "%s" % self.xmlstr

    def verify_attesting_entity(self, address):
        """
        Assumes one assertion. At least one address specification has to be
        correct.

        :param address: IP address of attesting entity
        :return: True/False
        """

        correct = 0
        for subject_conf in self.assertion.subject.subject_confirmation:
            if subject_conf.subject_confirmation_data is None:
                correct += 1  # In reality undefined
            elif subject_conf.subject_confirmation_data.address:
                if subject_conf.subject_confirmation_data.address == address:
                    correct += 1
            else:
                correct += 1

        if correct:
            return True
        else:
            return False


class AuthnQueryResponse(AuthnResponse):
    msgtype = "authn_query_response"

    def __init__(self, sec_context, attribute_converters, entity_id,
                 return_addrs=None, timeslack=0, asynchop=False, test=False):
        AuthnResponse.__init__(self, sec_context, attribute_converters,
                               entity_id, return_addrs, timeslack=timeslack,
                               asynchop=asynchop, test=test)
        self.entity_id = entity_id
        self.attribute_converters = attribute_converters
        self.assertion = None
        self.context = "AuthnQuery"

    def condition_ok(self, lax=False):  # Should I care about conditions ?
        return True


class AttributeResponse(AuthnResponse):
    msgtype = "attribute_response"

    def __init__(self, sec_context, attribute_converters, entity_id,
                 return_addrs=None, timeslack=0, asynchop=False, test=False):
        AuthnResponse.__init__(self, sec_context, attribute_converters,
                               entity_id, return_addrs, timeslack=timeslack,
                               asynchop=asynchop, test=test)
        self.entity_id = entity_id
        self.attribute_converters = attribute_converters
        self.assertion = None
        self.context = "AttrQuery"


class AuthzResponse(AuthnResponse):
    """ A successful response will be in the form of assertions containing
    authorization decision statements."""
    msgtype = "authz_decision_response"

    def __init__(self, sec_context, attribute_converters, entity_id,
                 return_addrs=None, timeslack=0, asynchop=False):
        AuthnResponse.__init__(self, sec_context, attribute_converters,
                               entity_id, return_addrs, timeslack=timeslack,
                               asynchop=asynchop)
        self.entity_id = entity_id
        self.attribute_converters = attribute_converters
        self.assertion = None
        self.context = "AuthzQuery"


class ArtifactResponse(AuthnResponse):
    msgtype = "artifact_response"

    def __init__(self, sec_context, attribute_converters, entity_id,
                 return_addrs=None, timeslack=0, asynchop=False, test=False):
        AuthnResponse.__init__(self, sec_context, attribute_converters,
                               entity_id, return_addrs, timeslack=timeslack,
                               asynchop=asynchop, test=test)
        self.entity_id = entity_id
        self.attribute_converters = attribute_converters
        self.assertion = None
        self.context = "ArtifactResolve"


def response_factory(xmlstr, conf, return_addrs=None, outstanding_queries=None,
                     timeslack=0, decode=True, request_id=0, origxml=None,
                     asynchop=True, allow_unsolicited=False,
                     want_assertions_signed=False):
    sec_context = security_context(conf)
    if not timeslack:
        try:
            timeslack = int(conf.accepted_time_diff)
        except TypeError:
            timeslack = 0

    attribute_converters = conf.attribute_converters
    entity_id = conf.entityid
    extension_schema = conf.extension_schema

    response = StatusResponse(sec_context, return_addrs, timeslack, request_id,
                              asynchop)
    try:
        response.loads(xmlstr, decode, origxml)
        if response.response.assertion or response.response.encrypted_assertion:
            authnresp = AuthnResponse(sec_context, attribute_converters,
                                      entity_id, return_addrs,
                                      outstanding_queries, timeslack, asynchop,
                                      allow_unsolicited,
                                      extension_schema=extension_schema,
                                      want_assertions_signed=want_assertions_signed)
            authnresp.update(response)
            return authnresp
    except TypeError:
        response.signature_check = sec_context.correctly_signed_logout_response
        response.loads(xmlstr, decode, origxml)
        logoutresp = LogoutResponse(sec_context, return_addrs, timeslack,
                                    asynchop=asynchop)
        logoutresp.update(response)
        return logoutresp

    return response


# ===========================================================================
# A class of it's own


class AssertionIDResponse(object):
    msgtype = "assertion_id_response"

    def __init__(self, sec_context, attribute_converters, timeslack=0,
                 **kwargs):

        self.sec = sec_context
        self.timeslack = timeslack
        self.xmlstr = ""
        self.origxml = ""
        self.name_id = ""
        self.response = None
        self.not_signed = False
        self.attribute_converters = attribute_converters
        self.assertion = None
        self.context = "AssertionIdResponse"
        self.signature_check = self.sec.correctly_signed_assertion_id_response

    def loads(self, xmldata, decode=True, origxml=None):
        # own copy
        self.xmlstr = xmldata[:]
        logger.debug("xmlstr: %s" % (self.xmlstr,))
        self.origxml = origxml

        try:
            self.response = self.signature_check(xmldata, origdoc=origxml)
            self.assertion = self.response
        except TypeError:
            raise
        except SignatureError:
            raise
        except Exception as excp:
            logger.exception("EXCEPTION: %s", excp)
            raise

        #print "<", self.response

        return self._postamble()

    def verify(self, key_file=""):
        try:
            valid_instance(self.response)
        except NotValid as exc:
            logger.error("Not valid response: %s" % exc.args[0])
            raise
        return self

    def _postamble(self):
        if not self.response:
            logger.error("Response was not correctly signed")
            if self.xmlstr:
                logger.info(self.xmlstr)
            raise IncorrectlySigned()

        logger.debug("response: %s" % (self.response,))

        return self

