#!/usr/bin/env python
import argparse
import base64

import re
import logging
import time
from hashlib import sha1

from urlparse import parse_qs
from Cookie import SimpleCookie
import os

from saml2 import server
from saml2 import BINDING_HTTP_ARTIFACT
from saml2 import BINDING_URI
from saml2 import BINDING_PAOS
from saml2 import BINDING_SOAP
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import BINDING_HTTP_POST
from saml2 import time_util
from saml2.authn import is_equal

from saml2.authn_context import AuthnBroker
from saml2.authn_context import PASSWORD
from saml2.authn_context import UNSPECIFIED
from saml2.authn_context import authn_context_class_ref
from saml2.httputil import Response
from saml2.httputil import NotFound
from saml2.httputil import geturl
from saml2.httputil import get_post
from saml2.httputil import Redirect
from saml2.httputil import Unauthorized
from saml2.httputil import BadRequest
from saml2.httputil import ServiceError
from saml2.ident import Unknown
from saml2.metadata import create_metadata_string
from saml2.s_utils import rndstr, exception_trace
from saml2.s_utils import UnknownPrincipal
from saml2.s_utils import UnsupportedBinding
from saml2.s_utils import PolicyError
from saml2.sigver import verify_redirect_signature

logger = logging.getLogger("saml2.idp")


class Cache(object):
    def __init__(self):
        self.user2uid = {}
        self.uid2user = {}


def _expiration(timeout, tformat="%a, %d-%b-%Y %H:%M:%S GMT"):
    """

    :param timeout:
    :param tformat:
    :return:
    """
    if timeout == "now":
        return time_util.instant(tformat)
    elif timeout == "dawn":
        return time.strftime(tformat, time.gmtime(0))
    else:
        # validity time should match lifetime of assertions
        return time_util.in_a_while(minutes=timeout, format=tformat)


def get_eptid(idp, req_info, session):
    return idp.eptid.get(idp.config.entityid,
                         req_info.sender(), session["permanent_id"],
                         session["authn_auth"])

# -----------------------------------------------------------------------------


def dict2list_of_tuples(d):
    return [(k, v) for k, v in d.items()]

# -----------------------------------------------------------------------------


class Service(object):
    def __init__(self, environ, start_response, user=None):
        self.environ = environ
        logger.debug("ENVIRON: %s", environ)
        self.start_response = start_response
        self.user = user

    def unpack_redirect(self):
        if "QUERY_STRING" in self.environ:
            _qs = self.environ["QUERY_STRING"]
            return dict([(k, v[0]) for k, v in parse_qs(_qs).items()])
        else:
            return None

    def unpack_post(self):
        _dict = parse_qs(get_post(self.environ))
        logger.debug("unpack_post:: %s", _dict)
        try:
            return dict([(k, v[0]) for k, v in _dict.items()])
        except Exception:
            return None

    def unpack_soap(self):
        try:
            query = get_post(self.environ)
            return {"SAMLRequest": query, "RelayState": ""}
        except Exception:
            return None

    def unpack_either(self):
        if self.environ["REQUEST_METHOD"] == "GET":
            _dict = self.unpack_redirect()
        elif self.environ["REQUEST_METHOD"] == "POST":
            _dict = self.unpack_post()
        else:
            _dict = None
        logger.debug("_dict: %s", _dict)
        return _dict

    def operation(self, _dict, binding):
        logger.debug("_operation: %s", _dict)
        if not _dict or not 'SAMLRequest' in _dict:
            resp = BadRequest('Error parsing request or no request')
            return resp(self.environ, self.start_response)
        else:
            try:
                return self.do(_dict["SAMLRequest"], binding,
                               _dict["RelayState"])
            except KeyError:
                # Can live with no relay state
                return self.do(_dict["SAMLRequest"], binding)

    def artifact_operation(self, _dict):
        if not _dict:
            resp = BadRequest("Missing query")
            return resp(self.environ, self.start_response)
        else:
            # exchange artifact for request
            request = IDP.artifact2message(_dict["SAMLart"], "spsso")
            try:
                return self.do(request, BINDING_HTTP_ARTIFACT,
                               _dict["RelayState"])
            except KeyError:
                return self.do(request, BINDING_HTTP_ARTIFACT)

    def response(self, binding, http_args):
        if binding == BINDING_HTTP_ARTIFACT:
            resp = Redirect()
        else:
            resp = Response(http_args["data"], headers=http_args["headers"])
        return resp(self.environ, self.start_response)

    def do(self, query, binding, relay_state=""):
        pass

    def redirect(self):
        """ Expects a HTTP-redirect request """

        _dict = self.unpack_redirect()
        return self.operation(_dict, BINDING_HTTP_REDIRECT)

    def post(self):
        """ Expects a HTTP-POST request """

        _dict = self.unpack_post()
        return self.operation(_dict, BINDING_HTTP_POST)

    def artifact(self):
        # Can be either by HTTP_Redirect or HTTP_POST
        _dict = self.unpack_either()
        return self.artifact_operation(_dict)

    def soap(self):
        """
        Single log out using HTTP_SOAP binding
        """
        logger.debug("- SOAP -")
        _dict = self.unpack_soap()
        logger.debug("_dict: %s", _dict)
        return self.operation(_dict, BINDING_SOAP)

    def uri(self):
        _dict = self.unpack_either()
        return self.operation(_dict, BINDING_SOAP)

    # def not_authn(self, key):
    #     """
    #
    #
    #     :return:
    #     """
    #     loc = "http://%s/login" % (self.environ["HTTP_HOST"])
    #     loc += "?%s" % urllib.urlencode({"came_from": self.environ[
    #         "PATH_INFO"], "key": key})
    #     headers = [('Content-Type', 'text/plain')]
    #
    #     logger.debug("location: %s", loc)
    #     logger.debug("headers: %s", headers)
    #
    #     resp = Redirect(loc, headers=headers)
    #
    #     return resp(self.environ, self.start_response)

    def not_authn(self, key, requested_authn_context):
        ruri = geturl(self.environ, query=False)
        return do_authentication(self.environ, self.start_response,
                                 authn_context=requested_authn_context,
                                 key=key, redirect_uri=ruri)


# -----------------------------------------------------------------------------

REPOZE_ID_EQUIVALENT = "uid"
FORM_SPEC = """<form name="myform" method="post" action="%s">
   <input type="hidden" name="SAMLResponse" value="%s" />
   <input type="hidden" name="RelayState" value="%s" />
</form>"""

# -----------------------------------------------------------------------------
# === Single log in ====
# -----------------------------------------------------------------------------


class AuthenticationNeeded(Exception):
    def __init__(self, authn_context=None, *args, **kwargs):
        Exception.__init__(*args, **kwargs)
        self.authn_context = authn_context


class SSO(Service):
    def __init__(self, environ, start_response, user=None):
        Service.__init__(self, environ, start_response, user)
        self.binding = ""
        self.response_bindings = None
        self.resp_args = {}
        self.binding_out = None
        self.destination = None
        self.req_info = None

    def verify_request(self, query, binding):
        """
        :param query: The SAML query, transport encoded
        :param binding: Which binding the query came in over
        """
        resp_args = {}
        if not query:
            logger.info("Missing QUERY")
            resp = Unauthorized('Unknown user')
            return resp_args, resp(self.environ, self.start_response)

        if not self.req_info:
            self.req_info = IDP.parse_authn_request(query, binding)

        logger.info("parsed OK")
        _authn_req = self.req_info.message
        logger.debug("%s", _authn_req)

        self.binding_out, self.destination = IDP.pick_binding(
            "assertion_consumer_service",
            bindings=self.response_bindings,
            entity_id=_authn_req.issuer.text)

        logger.debug("Binding: %s, destination: %s", self.binding_out,
                                                       self.destination)

        resp_args = {}
        try:
            resp_args = IDP.response_args(_authn_req)
            _resp = None
        except UnknownPrincipal as excp:
            _resp = IDP.create_error_response(_authn_req.id,
                                              self.destination, excp)
        except UnsupportedBinding as excp:
            _resp = IDP.create_error_response(_authn_req.id,
                                              self.destination, excp)

        return resp_args, _resp

    def do(self, query, binding_in, relay_state=""):
        try:
            resp_args, _resp = self.verify_request(query, binding_in)
        except UnknownPrincipal as excp:
            logger.error("UnknownPrincipal: %s", excp)
            resp = ServiceError("UnknownPrincipal: %s" % (excp,))
            return resp(self.environ, self.start_response)
        except UnsupportedBinding as excp:
            logger.error("UnsupportedBinding: %s", excp)
            resp = ServiceError("UnsupportedBinding: %s" % (excp,))
            return resp(self.environ, self.start_response)

        if not _resp:
            identity = USERS[self.user].copy()
            #identity["eduPersonTargetedID"] = get_eptid(IDP, query, session)
            logger.info("Identity: %s", identity)

            if REPOZE_ID_EQUIVALENT:
                identity[REPOZE_ID_EQUIVALENT] = self.user
            try:
                sign_assertion = IDP.config.getattr("sign_assertion", "idp")
                if sign_assertion is None:
                    sign_assertion = False
                _resp = IDP.create_authn_response(
                    identity, userid=self.user,
                    authn=AUTHN_BROKER[self.environ["idp.authn_ref"]], sign_assertion=sign_assertion,
                    sign_response=False, **resp_args)
            except Exception as excp:
                logging.error(exception_trace(excp))
                resp = ServiceError("Exception: %s" % (excp,))
                return resp(self.environ, self.start_response)

        logger.info("AuthNResponse: %s", _resp)
        http_args = IDP.apply_binding(self.binding_out,
                                      "%s" % _resp, self.destination,
                                      relay_state, response=True)
        logger.debug("HTTPargs: %s", http_args)
        return self.response(self.binding_out, http_args)

    def _store_request(self, _dict):
        logger.debug("_store_request: %s", _dict)
        key = sha1(_dict["SAMLRequest"]).hexdigest()
        # store the AuthnRequest
        IDP.ticket[key] = _dict
        return key

    def redirect(self):
        """ This is the HTTP-redirect endpoint """

        logger.info("--- In SSO Redirect ---")
        _info = self.unpack_redirect()

        try:
            _key = _info["key"]
            _info = IDP.ticket[_key]
            self.req_info = _info["req_info"]
            del IDP.ticket[_key]
        except KeyError:
            try:
                self.req_info = IDP.parse_authn_request(_info["SAMLRequest"],
                                                        BINDING_HTTP_REDIRECT)
            except KeyError:
                resp = BadRequest("Message signature verification failure")
                return resp(self.environ, self.start_response)

            _req = self.req_info.message

            if "SigAlg" in _info and "Signature" in _info:  # Signed request
                issuer = _req.issuer.text
                _certs = IDP.metadata.certs(issuer, "any", "signing")
                verified_ok = False
                for cert in _certs:
                    if verify_redirect_signature(_info, IDP.sec.sec_backend,
                                                 cert):
                        verified_ok = True
                        break
                if not verified_ok:
                    resp = BadRequest("Message signature verification failure")
                    return resp(self.environ, self.start_response)

            if self.user:
                if _req.force_authn:
                    _info["req_info"] = self.req_info
                    key = self._store_request(_info)
                    return self.not_authn(key, _req.requested_authn_context)
                else:
                    return self.operation(_info, BINDING_HTTP_REDIRECT)
            else:
                _info["req_info"] = self.req_info
                key = self._store_request(_info)
                return self.not_authn(key, _req.requested_authn_context)
        else:
            return self.operation(_info, BINDING_HTTP_REDIRECT)

    def post(self):
        """
        The HTTP-Post endpoint
        """
        logger.info("--- In SSO POST ---")
        _info = self.unpack_either()
        self.req_info = IDP.parse_authn_request(
            _info["SAMLRequest"], BINDING_HTTP_POST)
        _req = self.req_info.message
        if self.user:
            if _req.force_authn:
                _info["req_info"] = self.req_info
                key = self._store_request(_info)
                return self.not_authn(key, _req.requested_authn_context)
            else:
                return self.operation(_info, BINDING_HTTP_POST)
        else:
            _info["req_info"] = self.req_info
            key = self._store_request(_info)
            return self.not_authn(key, _req.requested_authn_context)

    # def artifact(self):
    #     # Can be either by HTTP_Redirect or HTTP_POST
    #     _req = self._store_request(self.unpack_either())
    #     if isinstance(_req, basestring):
    #         return self.not_authn(_req)
    #     return self.artifact_operation(_req)

    def ecp(self):
        # The ECP interface
        logger.info("--- ECP SSO ---")
        resp = None

        try:
            authz_info = self.environ["HTTP_AUTHORIZATION"]
            if authz_info.startswith("Basic "):
                try:
                    _info = base64.b64decode(authz_info[6:])
                except TypeError:
                    resp = Unauthorized()
                else:
                    logger.debug("Authz_info: %s", _info)
                    try:
                        (user, passwd) = _info.split(":")
                        if is_equal(PASSWD[user], passwd):
                            resp = Unauthorized()
                        self.user = user
                    except (ValueError, TypeError):
                        resp = Unauthorized()
            else:
                resp = Unauthorized()
        except KeyError:
            resp = Unauthorized()

        if resp:
            return resp(self.environ, self.start_response)

        _dict = self.unpack_soap()
        self.response_bindings = [BINDING_PAOS]
        # Basic auth ?!
        return self.operation(_dict, BINDING_SOAP)

# -----------------------------------------------------------------------------
# === Authentication ====
# -----------------------------------------------------------------------------


def do_authentication(environ, start_response, authn_context, key,
                      redirect_uri):
    """
    Display the login form
    """
    logger.debug("Do authentication")
    auth_info = AUTHN_BROKER.pick(authn_context)

    if len(auth_info):
        method, reference = auth_info[0]
        logger.debug("Authn chosen: %s (ref=%s)", method, reference)
        return method(environ, start_response, reference, key, redirect_uri)
    else:
        resp = Unauthorized("No usable authentication method")
        return resp(environ, start_response)


# -----------------------------------------------------------------------------

PASSWD = {"haho0032": "qwerty",
          "roland": "dianakra",
          "babs": "howes",
          "upper": "crust"}


def username_password_authn(environ, start_response, reference, key,
                            redirect_uri):
    """
    Display the login form
    """
    logger.info("The login page")
    headers = []

    resp = Response(mako_template="login.mako", template_lookup=LOOKUP,
                    headers=headers)

    argv = {
        "action": "/verify",
        "login": "",
        "password": "",
        "key": key,
        "authn_reference": reference,
        "redirect_uri": redirect_uri
    }
    logger.info("do_authentication argv: %s", argv)
    return resp(environ, start_response, **argv)


def verify_username_and_password(dic):
    global PASSWD
    # verify username and password
    if PASSWD[dic["login"][0]] == dic["password"][0]:
        return True, dic["login"][0]
    else:
        return False, ""


def do_verify(environ, start_response, _):
    query = parse_qs(get_post(environ))

    logger.debug("do_verify: %s", query)

    try:
        _ok, user = verify_username_and_password(query)
    except KeyError:
        _ok = False
        user = None

    if not _ok:
        resp = Unauthorized("Unknown user or wrong password")
    else:
        uid = rndstr(24)
        IDP.cache.uid2user[uid] = user
        IDP.cache.user2uid[user] = uid
        logger.debug("Register %s under '%s'", user, uid)

        kaka = set_cookie("idpauthn", "/", uid, query["authn_reference"][0])

        lox = "%s?id=%s&key=%s" % (query["redirect_uri"][0], uid,
                                   query["key"][0])
        logger.debug("Redirect => %s", lox)
        resp = Redirect(lox, headers=[kaka], content="text/html")

    return resp(environ, start_response)


def not_found(environ, start_response):
    """Called if no URL matches."""
    resp = NotFound()
    return resp(environ, start_response)


# -----------------------------------------------------------------------------
# === Single log out ===
# -----------------------------------------------------------------------------

#def _subject_sp_info(req_info):
#    # look for the subject
#    subject = req_info.subject_id()
#    subject = subject.text.strip()
#    sp_entity_id = req_info.message.issuer.text.strip()
#    return subject, sp_entity_id

class SLO(Service):
    def do(self, request, binding, relay_state=""):
        logger.info("--- Single Log Out Service ---")
        try:
            _, body = request.split("\n")
            logger.debug("req: '%s'", body)
            req_info = IDP.parse_logout_request(body, binding)
        except Exception as exc:
            logger.error("Bad request: %s", exc)
            resp = BadRequest("%s" % exc)
            return resp(self.environ, self.start_response)

        msg = req_info.message
        if msg.name_id:
            lid = IDP.ident.find_local_id(msg.name_id)
            logger.info("local identifier: %s", lid)
            if lid in IDP.cache.user2uid:
                uid = IDP.cache.user2uid[lid]
                if uid in IDP.cache.uid2user:
                    del IDP.cache.uid2user[uid]
                del IDP.cache.user2uid[lid]
            # remove the authentication
            try:
                IDP.session_db.remove_authn_statements(msg.name_id)
            except KeyError as exc:
                logger.error("ServiceError: %s", exc)
                resp = ServiceError("%s" % exc)
                return resp(self.environ, self.start_response)

        resp = IDP.create_logout_response(msg, [binding])

        try:
            hinfo = IDP.apply_binding(binding, "%s" % resp, "", relay_state)
        except Exception as exc:
            logger.error("ServiceError: %s", exc)
            resp = ServiceError("%s" % exc)
            return resp(self.environ, self.start_response)

        #_tlh = dict2list_of_tuples(hinfo["headers"])
        delco = delete_cookie(self.environ, "idpauthn")
        if delco:
            hinfo["headers"].append(delco)
        logger.info("Header: %s", hinfo["headers"])
        resp = Response(hinfo["data"], headers=hinfo["headers"])
        return resp(self.environ, self.start_response)

# ----------------------------------------------------------------------------
# Manage Name ID service
# ----------------------------------------------------------------------------


class NMI(Service):

    def do(self, query, binding, relay_state=""):
        logger.info("--- Manage Name ID Service ---")
        req = IDP.parse_manage_name_id_request(query, binding)
        request = req.message

        # Do the necessary stuff
        name_id = IDP.ident.handle_manage_name_id_request(
            request.name_id, request.new_id, request.new_encrypted_id,
            request.terminate)

        logger.debug("New NameID: %s", name_id)

        _resp = IDP.create_manage_name_id_response(request)

        # It's using SOAP binding
        hinfo = IDP.apply_binding(BINDING_SOAP, "%s" % _resp, "",
                                  relay_state, response=True)

        resp = Response(hinfo["data"], headers=hinfo["headers"])
        return resp(self.environ, self.start_response)

# ----------------------------------------------------------------------------
# === Assertion ID request ===
# ----------------------------------------------------------------------------


# Only URI binding
class AIDR(Service):
    def do(self, aid, binding, relay_state=""):
        logger.info("--- Assertion ID Service ---")

        try:
            assertion = IDP.create_assertion_id_request_response(aid)
        except Unknown:
            resp = NotFound(aid)
            return resp(self.environ, self.start_response)

        hinfo = IDP.apply_binding(BINDING_URI, "%s" % assertion, response=True)

        logger.debug("HINFO: %s", hinfo)
        resp = Response(hinfo["data"], headers=hinfo["headers"])
        return resp(self.environ, self.start_response)

    def operation(self, _dict, binding, **kwargs):
        logger.debug("_operation: %s", _dict)
        if not _dict or "ID" not in _dict:
            resp = BadRequest('Error parsing request or no request')
            return resp(self.environ, self.start_response)

        return self.do(_dict["ID"], binding, **kwargs)


# ----------------------------------------------------------------------------
# === Artifact resolve service ===
# ----------------------------------------------------------------------------

class ARS(Service):
    def do(self, request, binding, relay_state=""):
        _req = IDP.parse_artifact_resolve(request, binding)

        msg = IDP.create_artifact_response(_req, _req.artifact.text)

        hinfo = IDP.apply_binding(BINDING_SOAP, "%s" % msg, "", "",
                                  response=True)

        resp = Response(hinfo["data"], headers=hinfo["headers"])
        return resp(self.environ, self.start_response)

# ----------------------------------------------------------------------------
# === Authn query service ===
# ----------------------------------------------------------------------------


# Only SOAP binding
class AQS(Service):
    def do(self, request, binding, relay_state=""):
        logger.info("--- Authn Query Service ---")
        _req = IDP.parse_authn_query(request, binding)
        _query = _req.message

        msg = IDP.create_authn_query_response(_query.subject,
                                              _query.requested_authn_context,
                                              _query.session_index)

        logger.debug("response: %s", msg)
        hinfo = IDP.apply_binding(BINDING_SOAP, "%s" % msg, "", "",
                                  response=True)

        resp = Response(hinfo["data"], headers=hinfo["headers"])
        return resp(self.environ, self.start_response)


# ----------------------------------------------------------------------------
# === Attribute query service ===
# ----------------------------------------------------------------------------


# Only SOAP binding
class ATTR(Service):
    def do(self, request, binding, relay_state=""):
        logger.info("--- Attribute Query Service ---")

        _req = IDP.parse_attribute_query(request, binding)
        _query = _req.message

        name_id = _query.subject.name_id
        uid = name_id.text
        logger.debug("Local uid: %s", uid)
        identity = EXTRA[uid]

        # Comes in over SOAP so only need to construct the response
        args = IDP.response_args(_query, [BINDING_SOAP])
        msg = IDP.create_attribute_response(identity,
                                            name_id=name_id, **args)

        logger.debug("response: %s", msg)
        hinfo = IDP.apply_binding(BINDING_SOAP, "%s" % msg, "", "",
                                  response=True)

        resp = Response(hinfo["data"], headers=hinfo["headers"])
        return resp(self.environ, self.start_response)

# ----------------------------------------------------------------------------
# Name ID Mapping service
# When an entity that shares an identifier for a principal with an identity
# provider wishes to obtain a name identifier for the same principal in a
# particular format or federation namespace, it can send a request to
# the identity provider using this protocol.
# ----------------------------------------------------------------------------


class NIM(Service):
    def do(self, query, binding, relay_state=""):
        req = IDP.parse_name_id_mapping_request(query, binding)
        request = req.message
        # Do the necessary stuff
        try:
            name_id = IDP.ident.handle_name_id_mapping_request(
                request.name_id, request.name_id_policy)
        except Unknown:
            resp = BadRequest("Unknown entity")
            return resp(self.environ, self.start_response)
        except PolicyError:
            resp = BadRequest("Unknown entity")
            return resp(self.environ, self.start_response)

        info = IDP.response_args(request)
        _resp = IDP.create_name_id_mapping_response(name_id, **info)

        # Only SOAP
        hinfo = IDP.apply_binding(BINDING_SOAP, "%s" % _resp, "", "",
                                  response=True)

        resp = Response(hinfo["data"], headers=hinfo["headers"])
        return resp(self.environ, self.start_response)


# ----------------------------------------------------------------------------
# Cookie handling
# ----------------------------------------------------------------------------
def info_from_cookie(kaka):
    logger.debug("KAKA: %s", kaka)
    if kaka:
        cookie_obj = SimpleCookie(kaka)
        morsel = cookie_obj.get("idpauthn", None)
        if morsel:
            try:
                key, ref = base64.b64decode(morsel.value).split(":")
                return IDP.cache.uid2user[key], ref
            except (KeyError, TypeError):
                return None, None
        else:
            logger.debug("No idpauthn cookie")
    return None, None


def delete_cookie(environ, name):
    kaka = environ.get("HTTP_COOKIE", '')
    logger.debug("delete KAKA: %s", kaka)
    if kaka:
        cookie_obj = SimpleCookie(kaka)
        morsel = cookie_obj.get(name, None)
        cookie = SimpleCookie()
        cookie[name] = ""
        cookie[name]['path'] = "/"
        logger.debug("Expire: %s", morsel)
        cookie[name]["expires"] = _expiration("dawn")
        return tuple(cookie.output().split(": ", 1))
    return None


def set_cookie(name, _, *args):
    cookie = SimpleCookie()
    cookie[name] = base64.b64encode(":".join(args))
    cookie[name]['path'] = "/"
    cookie[name]["expires"] = _expiration(5)  # 5 minutes from now
    logger.debug("Cookie expires: %s", cookie[name]["expires"])
    return tuple(cookie.output().split(": ", 1))

# ----------------------------------------------------------------------------

# map urls to functions
AUTHN_URLS = [
    # sso
    (r'sso/post$', (SSO, "post")),
    (r'sso/post/(.*)$', (SSO, "post")),
    (r'sso/redirect$', (SSO, "redirect")),
    (r'sso/redirect/(.*)$', (SSO, "redirect")),
    (r'sso/art$', (SSO, "artifact")),
    (r'sso/art/(.*)$', (SSO, "artifact")),
    # slo
    (r'slo/redirect$', (SLO, "redirect")),
    (r'slo/redirect/(.*)$', (SLO, "redirect")),
    (r'slo/post$', (SLO, "post")),
    (r'slo/post/(.*)$', (SLO, "post")),
    (r'slo/soap$', (SLO, "soap")),
    (r'slo/soap/(.*)$', (SLO, "soap")),
    #
    (r'airs$', (AIDR, "uri")),
    (r'ars$', (ARS, "soap")),
    # mni
    (r'mni/post$', (NMI, "post")),
    (r'mni/post/(.*)$', (NMI, "post")),
    (r'mni/redirect$', (NMI, "redirect")),
    (r'mni/redirect/(.*)$', (NMI, "redirect")),
    (r'mni/art$', (NMI, "artifact")),
    (r'mni/art/(.*)$', (NMI, "artifact")),
    (r'mni/soap$', (NMI, "soap")),
    (r'mni/soap/(.*)$', (NMI, "soap")),
    # nim
    (r'nim$', (NIM, "soap")),
    (r'nim/(.*)$', (NIM, "soap")),
    #
    (r'aqs$', (AQS, "soap")),
    (r'attr$', (ATTR, "soap"))
]

NON_AUTHN_URLS = [
    #(r'login?(.*)$', do_authentication),
    (r'verify?(.*)$', do_verify),
    (r'sso/ecp$', (SSO, "ecp")),
]

# ----------------------------------------------------------------------------


def metadata(environ, start_response):
    try:
        path = args.path
        if path is None or len(path) == 0:
            path = os.path.dirname(os.path.abspath( __file__ ))
        if path[-1] != "/":
            path += "/"
        metadata = create_metadata_string(path+args.config, IDP.config,
                                          args.valid, args.cert, args.keyfile,
                                          args.id, args.name, args.sign)
        start_response('200 OK', [('Content-Type', "text/xml")])
        return metadata
    except Exception as ex:
        logger.error("An error occured while creating metadata: %s", ex.message)
        return not_found(environ, start_response)

def staticfile(environ, start_response):
    try:
        path = args.path
        if path is None or len(path) == 0:
            path = os.path.dirname(os.path.abspath(__file__))
        if path[-1] != "/":
            path += "/"
        path += environ.get('PATH_INFO', '').lstrip('/')
        start_response('200 OK', [('Content-Type', "text/xml")])
        return open(path, 'r').read()
    except Exception as ex:
        logger.error("An error occured while creating metadata: %s", ex.message)
        return not_found(environ, start_response)

def application(environ, start_response):
    """
    The main WSGI application. Dispatch the current request to
    the functions from above and store the regular expression
    captures in the WSGI environment as `myapp.url_args` so that
    the functions from above can access the url placeholders.

    If nothing matches, call the `not_found` function.

    :param environ: The HTTP application environment
    :param start_response: The application to run when the handling of the
        request is done
    :return: The response as a list of lines
    """

    path = environ.get('PATH_INFO', '').lstrip('/')

    if path == "metadata":
        return metadata(environ, start_response)

    kaka = environ.get("HTTP_COOKIE", None)
    logger.info("<application> PATH: %s", path)

    if kaka:
        logger.info("= KAKA =")
        user, authn_ref = info_from_cookie(kaka)
        environ["idp.authn_ref"] = authn_ref
    else:
        try:
            query = parse_qs(environ["QUERY_STRING"])
            logger.debug("QUERY: %s", query)
            user = IDP.cache.uid2user[query["id"][0]]
        except KeyError:
            user = None

    url_patterns = AUTHN_URLS
    if not user:
        logger.info("-- No USER --")
        # insert NON_AUTHN_URLS first in case there is no user
        url_patterns = NON_AUTHN_URLS + url_patterns

    for regex, callback in url_patterns:
        match = re.search(regex, path)
        if match is not None:
            try:
                environ['myapp.url_args'] = match.groups()[0]
            except IndexError:
                environ['myapp.url_args'] = path

            logger.debug("Callback: %s", (callback,))
            if isinstance(callback, tuple):
                cls = callback[0](environ, start_response, user)
                func = getattr(cls, callback[1])
                return func()
            return callback(environ, start_response, user)

    if re.search(r'static/.*', path) is not None:
        return staticfile(environ, start_response)
    return not_found(environ, start_response)

# ----------------------------------------------------------------------------

# allow uwsgi or gunicorn mount
# by moving some initialization out of __name__ == '__main__' section.
# uwsgi -s 0.0.0.0:8088 --protocol http --callable application --module idp

args = type('Config', (object,), { })
args.config = 'idp_conf'
args.mako_root = './'
args.path = None

import socket
from idp_user import USERS
from idp_user import EXTRA
from mako.lookup import TemplateLookup

AUTHN_BROKER = AuthnBroker()
AUTHN_BROKER.add(authn_context_class_ref(PASSWORD),
             username_password_authn, 10,
             "http://%s" % socket.gethostname())
AUTHN_BROKER.add(authn_context_class_ref(UNSPECIFIED),
             "", 0, "http://%s" % socket.gethostname())

IDP = server.Server(args.config, cache=Cache())
IDP.ticket = {}

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', dest='path', help='Path to configuration file.')
    parser.add_argument('-v', dest='valid',
                        help="How long, in days, the metadata is valid from the time of creation")
    parser.add_argument('-c', dest='cert', help='certificate')
    parser.add_argument('-i', dest='id',
                        help="The ID of the entities descriptor")
    parser.add_argument('-k', dest='keyfile',
                        help="A file with a key to sign the metadata with")
    parser.add_argument('-n', dest='name')
    parser.add_argument('-s', dest='sign', action='store_true',
                        help="sign the metadata")
    parser.add_argument('-m', dest='mako_root', default="./")
    parser.add_argument(dest="config")
    args = parser.parse_args()

    _rot = args.mako_root
    LOOKUP = TemplateLookup(directories=[_rot + 'templates', _rot + 'htdocs'],
                            module_directory=_rot + 'modules',
                            input_encoding='utf-8', output_encoding='utf-8')

    HOST = '127.0.0.1'
    PORT = 8088

    SRV = make_server(HOST, PORT, application)
    print("IdP listening on %s:%s" % (HOST, PORT))
    SRV.serve_forever()
else:
    _rot = args.mako_root
    LOOKUP = TemplateLookup(directories=[_rot + 'templates', _rot + 'htdocs'],
                            module_directory=_rot + 'modules',
                            input_encoding='utf-8', output_encoding='utf-8')
