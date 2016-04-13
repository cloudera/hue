#!/usr/bin/env python
import logging
import random
import string

import time
import base64
import sys
import hmac
import string

# from python 2.5
import imp
import traceback

if sys.version_info >= (2, 5):
    import hashlib
else:  # before python 2.5
    import sha

from saml2 import saml
from saml2 import samlp
from saml2 import VERSION
from saml2.time_util import instant

try:
    from hashlib import md5
except ImportError:
    from md5 import md5
import zlib

logger = logging.getLogger(__name__)


class SamlException(Exception):
    pass


class RequestVersionTooLow(SamlException):
    pass


class RequestVersionTooHigh(SamlException):
    pass


class UnknownPrincipal(SamlException):
    pass


class UnknownSystemEntity(SamlException):
    pass


class Unsupported(SamlException):
    pass


class UnsupportedBinding(Unsupported):
    pass


class VersionMismatch(Exception):
    pass


class Unknown(Exception):
    pass


class OtherError(Exception):
    pass


class MissingValue(Exception):
    pass


class PolicyError(Exception):
    pass


class BadRequest(Exception):
    pass


class UnravelError(Exception):
    pass


EXCEPTION2STATUS = {
    VersionMismatch: samlp.STATUS_VERSION_MISMATCH,
    UnknownPrincipal: samlp.STATUS_UNKNOWN_PRINCIPAL,
    UnsupportedBinding: samlp.STATUS_UNSUPPORTED_BINDING,
    RequestVersionTooLow: samlp.STATUS_REQUEST_VERSION_TOO_LOW,
    RequestVersionTooHigh: samlp.STATUS_REQUEST_VERSION_TOO_HIGH,
    OtherError: samlp.STATUS_UNKNOWN_PRINCIPAL,
    MissingValue: samlp.STATUS_REQUEST_UNSUPPORTED,
    # Undefined
    Exception: samlp.STATUS_AUTHN_FAILED,
}

GENERIC_DOMAINS = ["aero", "asia", "biz", "cat", "com", "coop", "edu",
                   "gov", "info", "int", "jobs", "mil", "mobi", "museum",
                   "name", "net", "org", "pro", "tel", "travel"]


def valid_email(emailaddress, domains=GENERIC_DOMAINS):
    """Checks for a syntactically valid email address."""

    # Email address must be at least 6 characters in total.
    # Assuming noone may have addresses of the type a@com
    if len(emailaddress) < 6:
        return False  # Address too short.

    # Split up email address into parts.
    try:
        localpart, domainname = emailaddress.rsplit('@', 1)
        host, toplevel = domainname.rsplit('.', 1)
    except ValueError:
        return False  # Address does not have enough parts.

    # Check for Country code or Generic Domain.
    if len(toplevel) != 2 and toplevel not in domains:
        return False  # Not a domain name.

    for i in '-_.%+.':
        localpart = localpart.replace(i, "")
    for i in '-_.':
        host = host.replace(i, "")

    if localpart.isalnum() and host.isalnum():
        return True  # Email address is fine.
    else:
        return False  # Email address has funny characters.


def decode_base64_and_inflate(string):
    """ base64 decodes and then inflates according to RFC1951

    :param string: a deflated and encoded string
    :return: the string after decoding and inflating
    """

    return zlib.decompress(base64.b64decode(string), -15)


def deflate_and_base64_encode(string_val):
    """
    Deflates and the base64 encodes a string

    :param string_val: The string to deflate and encode
    :return: The deflated and encoded string
    """
    return base64.b64encode(zlib.compress(string_val)[2:-4])


def rndstr(size=16, alphabet=""):
    """
    Returns a string of random ascii characters or digits

    :param size: The length of the string
    :return: string
    """
    rng = random.SystemRandom()
    if not alphabet:
        alphabet = string.letters[0:52] + string.digits
    return str().join(rng.choice(alphabet) for _ in range(size))


def sid():
    """creates an unique SID for each session.
    160-bits long so it fulfills the SAML2 requirements which states
    128-160 bits

    :return: A random string prefix with 'id-' to make it
        compliant with the NCName specification
    """
    return "id-" + rndstr(17)


def parse_attribute_map(filenames):
    """
    Expects a file with each line being composed of the oid for the attribute
    exactly one space, a user friendly name of the attribute and then
    the type specification of the name.

    :param filenames: List of filenames on mapfiles.
    :return: A 2-tuple, one dictionary with the oid as keys and the friendly
        names as values, the other one the other way around.
    """
    forward = {}
    backward = {}
    for filename in filenames:
        for line in open(filename).readlines():
            (name, friendly_name, name_format) = line.strip().split()
            forward[(name, name_format)] = friendly_name
            backward[friendly_name] = (name, name_format)

    return forward, backward


def identity_attribute(form, attribute, forward_map=None):
    if form == "friendly":
        if attribute.friendly_name:
            return attribute.friendly_name
        elif forward_map:
            try:
                return forward_map[(attribute.name, attribute.name_format)]
            except KeyError:
                return attribute.name
    # default is name
    return attribute.name

#----------------------------------------------------------------------------


def error_status_factory(info):
    if isinstance(info, Exception):
        try:
            exc_val = EXCEPTION2STATUS[info.__class__]
        except KeyError:
            exc_val = samlp.STATUS_AUTHN_FAILED
        try:
            msg = info.args[0]
        except IndexError:
            msg = "%s" % info
        status = samlp.Status(
            status_message=samlp.StatusMessage(text=msg),
            status_code=samlp.StatusCode(
                value=samlp.STATUS_RESPONDER,
                status_code=samlp.StatusCode(
                    value=exc_val)))
    else:
        (errcode, text) = info
        status = samlp.Status(
            status_message=samlp.StatusMessage(text=text),
            status_code=samlp.StatusCode(
                value=samlp.STATUS_RESPONDER,
                status_code=samlp.StatusCode(value=errcode)))

    return status


def success_status_factory():
    return samlp.Status(status_code=samlp.StatusCode(
        value=samlp.STATUS_SUCCESS))


def status_message_factory(message, code, fro=samlp.STATUS_RESPONDER):
    return samlp.Status(
        status_message=samlp.StatusMessage(text=message),
        status_code=samlp.StatusCode(value=fro,
                                     status_code=samlp.StatusCode(value=code)))


def assertion_factory(**kwargs):
    assertion = saml.Assertion(version=VERSION, id=sid(),
                               issue_instant=instant())
    for key, val in kwargs.items():
        setattr(assertion, key, val)
    return assertion


def _attrval(val, typ=""):
    if isinstance(val, list) or isinstance(val, set):
        attrval = [saml.AttributeValue(text=v) for v in val]
    elif val is None:
        attrval = None
    else:
        attrval = [saml.AttributeValue(text=val)]

    if typ:
        for ava in attrval:
            ava.set_type(typ)

    return attrval

# --- attribute profiles -----

# xmlns:xs="http://www.w3.org/2001/XMLSchema"
# xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"


def do_ava(val, typ=""):
    if isinstance(val, basestring):
        ava = saml.AttributeValue()
        ava.set_text(val)
        attrval = [ava]
    elif isinstance(val, list):
        attrval = [do_ava(v)[0] for v in val]
    elif val or val is False:
        ava = saml.AttributeValue()
        ava.set_text(val)
        attrval = [ava]
    elif val is None:
        attrval = None
    else:
        raise OtherError("strange value type on: %s" % val)

    if typ:
        for ava in attrval:
            ava.set_type(typ)

    return attrval


def do_attribute(val, typ, key):
    attr = saml.Attribute()
    attrval = do_ava(val, typ)
    if attrval:
        attr.attribute_value = attrval

    if isinstance(key, basestring):
        attr.name = key
    elif isinstance(key, tuple):  # 3-tuple or 2-tuple
        try:
            (name, nformat, friendly) = key
        except ValueError:
            (name, nformat) = key
            friendly = ""
        if name:
            attr.name = name
        if format:
            attr.name_format = nformat
        if friendly:
            attr.friendly_name = friendly
    return attr


def do_attributes(identity):
    attrs = []
    if not identity:
        return attrs
    for key, spec in identity.items():
        try:
            val, typ = spec
        except ValueError:
            val = spec
            typ = ""
        except TypeError:
            val = ""
            typ = ""

        attr = do_attribute(val, typ, key)
        attrs.append(attr)
    return attrs


def do_attribute_statement(identity):
    """
    :param identity: A dictionary with fiendly names as keys
    :return:
    """
    return saml.AttributeStatement(attribute=do_attributes(identity))


def factory(klass, **kwargs):
    instance = klass()
    for key, val in kwargs.items():
        setattr(instance, key, val)
    return instance


def signature(secret, parts):
    """Generates a signature.
    """
    if sys.version_info >= (2, 5):
        csum = hmac.new(secret, digestmod=hashlib.sha1)
    else:
        csum = hmac.new(secret, digestmod=sha)

    for part in parts:
        csum.update(part)

    return csum.hexdigest()


def verify_signature(secret, parts):
    """ Checks that the signature is correct """
    if signature(secret, parts[:-1]) == parts[-1]:
        return True
    else:
        return False


FTICKS_FORMAT = "F-TICKS/SWAMID/2.0%s#"


def fticks_log(sp, logf, idp_entity_id, user_id, secret, assertion):
    """
    'F-TICKS/' federationIdentifier '/' version *('#' attribute '=' value) '#'
    Allowed attributes:
        TS	the login time stamp
        RP	the relying party entityID
        AP	the asserting party entityID (typcially the IdP)
        PN	a sha256-hash of the local principal name and a unique key
        AM	the authentication method URN

    :param sp: Client instance
    :param logf: The log function to use
    :param idp_entity_id: IdP entity ID
    :param user_id: The user identifier
    :param secret: A salt to make the hash more secure
    :param assertion: A SAML Assertion instance gotten from the IdP
    """
    csum = hmac.new(secret, digestmod=hashlib.sha1)
    csum.update(user_id)
    ac = assertion.AuthnStatement[0].AuthnContext[0]

    info = {
        "TS": time.time(),
        "RP": sp.entity_id,
        "AP": idp_entity_id,
        "PN": csum.hexdigest(),
        "AM": ac.AuthnContextClassRef.text
    }
    logf.info(FTICKS_FORMAT % "#".join(["%s=%s" % (a, v) for a, v in info]))


def dynamic_importer(name, class_name=None):
    """
    Dynamically imports modules / classes
    """
    try:
        fp, pathname, description = imp.find_module(name)
    except ImportError:
        print "unable to locate module: " + name
        return None, None

    try:
        package = imp.load_module(name, fp, pathname, description)
    except Exception:
        raise

    if class_name:
        try:
            _class = imp.load_module("%s.%s" % (name, class_name), fp,
                                     pathname, description)
        except Exception:
            raise

        return package, _class
    else:
        return package, None


def exception_trace(exc):
    message = traceback.format_exception(*sys.exc_info())

    try:
        _exc = "Exception: %s" % exc
    except UnicodeEncodeError:
        _exc = "Exception: %s" % exc.message.encode("utf-8", "replace")

    return {"message": _exc, "content": "".join(message)}


def rec_factory(cls, **kwargs):
    _inst = cls()
    for key, val in kwargs.items():
        if key in ["text", "lang"]:
            setattr(_inst, key, val)
        elif key in _inst.c_attributes:
            try:
                val = str(val)
            except Exception:
                continue
            else:
                setattr(_inst, _inst.c_attributes[key][0], val)
        elif key in _inst.c_child_order:
            for tag, _cls in _inst.c_children.values():
                if tag == key:
                    if isinstance(_cls, list):
                        _cls = _cls[0]
                        claim = []
                        if isinstance(val, list):
                            for v in val:
                                claim.append(rec_factory(_cls, **v))
                        else:
                            claim.append(rec_factory(_cls, **val))
                    else:
                        claim = rec_factory(_cls, **val)
                    setattr(_inst, key, claim)
                    break

    return _inst
