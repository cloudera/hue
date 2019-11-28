#!/usr/bin/env python
from __future__ import print_function

import argparse
import cgi
import importlib
import logging
import os
import re
import sys
import xml.dom.minidom
from saml2.sigver import SignatureError

import six
from six.moves.http_cookies import SimpleCookie
from six.moves.urllib.parse import parse_qs

import saml2.xmldsig as ds
from saml2 import BINDING_HTTP_ARTIFACT
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_REDIRECT, element_to_extension_element
from saml2 import BINDING_SOAP
from saml2 import ecp
from saml2 import time_util
from saml2.client import Saml2Client
from saml2.ecp_client import PAOS_HEADER_INFO
from saml2.extension.pefim import SPCertEnc
from saml2.httputil import BadRequest
from saml2.httputil import NotFound
from saml2.httputil import NotImplemented
from saml2.httputil import Redirect
from saml2.httputil import Response
from saml2.httputil import SeeOther
from saml2.httputil import ServiceError
from saml2.httputil import Unauthorized
from saml2.httputil import get_post
from saml2.httputil import geturl, make_cookie, parse_cookie
from saml2.metadata import create_metadata_string
from saml2.response import StatusError
from saml2.response import VerificationError
from saml2.s_utils import UnknownPrincipal
from saml2.s_utils import UnsupportedBinding
from saml2.s_utils import decode_base64_and_inflate
from saml2.s_utils import rndstr
from saml2.s_utils import sid
from saml2.saml import NAMEID_FORMAT_PERSISTENT
from saml2.samlp import Extensions

logger = logging.getLogger("")
hdlr = logging.FileHandler('spx.log')
base_formatter = logging.Formatter(
    "%(asctime)s %(name)s:%(levelname)s %(message)s")

hdlr.setFormatter(base_formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

SP = None
SEED = ""
POLICY = None


def dict_to_table(ava, lev=0, width=1):
    txt = ['<table border=%s bordercolor="black">\n' % width]
    for prop, valarr in ava.items():
        txt.append("<tr>\n")
        if isinstance(valarr, six.string_types):
            txt.append("<th>%s</th>\n" % str(prop))
            txt.append("<td>%s</td>\n" % valarr)
        elif isinstance(valarr, list):
            i = 0
            n = len(valarr)
            for val in valarr:
                if not i:
                    txt.append("<th rowspan=%d>%s</td>\n" % (len(valarr), prop))
                else:
                    txt.append("<tr>\n")
                if isinstance(val, dict):
                    txt.append("<td>\n")
                    txt.extend(dict_to_table(val, lev + 1, width - 1))
                    txt.append("</td>\n")
                else:
                    txt.append("<td>%s</td>\n" % val)
                if n > 1:
                    txt.append("</tr>\n")
                n -= 1
                i += 1
        elif isinstance(valarr, dict):
            txt.append("<th>%s</th>\n" % prop)
            txt.append("<td>\n")
            txt.extend(dict_to_table(valarr, lev + 1, width - 1))
            txt.append("</td>\n")
        txt.append("</tr>\n")
    txt.append('</table>\n')
    return txt


def handle_static(environ, start_response, path):
    """
    Creates a response for a static file. There might be a longer path
    then just /static/... - if so strip the path leading up to static.

    :param environ: wsgi enviroment
    :param start_response: wsgi start response
    :param path: the static file and path to the file.
    :return: wsgi response for the static file.
    """
    try:
        text = open(path).read()
        if path.endswith(".ico"):
            resp = Response(text, headers=[('Content-Type', "image/x-icon")])
        elif path.endswith(".html"):
            resp = Response(text, headers=[('Content-Type', 'text/html')])
        elif path.endswith(".txt"):
            resp = Response(text, headers=[('Content-Type', 'text/plain')])
        elif path.endswith(".css"):
            resp = Response(text, headers=[('Content-Type', 'text/css')])
        elif path.endswith(".js"):
            resp = Response(text, headers=[('Content-Type', 'text/javascript')])
        elif path.endswith(".png"):
            resp = Response(text, headers=[('Content-Type', 'image/png')])
        else:
            resp = Response(text)
    except IOError:
        resp = NotFound()
    return resp(environ, start_response)


class ECPResponse(object):
    code = 200
    title = 'OK'

    def __init__(self, content):
        self.content = content

    # noinspection PyUnusedLocal
    def __call__(self, environ, start_response):
        start_response('%s %s' % (self.code, self.title),
                       [('Content-Type', "text/xml")])
        return [self.content]


def _expiration(timeout, tformat=None):
    # Wed, 06-Jun-2012 01:34:34 GMT
    if not tformat:
        tformat = '%a, %d-%b-%Y %T GMT'

    if timeout == "now":
        return time_util.instant(tformat)
    else:
        # validity time should match lifetime of assertions
        return time_util.in_a_while(minutes=timeout, format=tformat)


class Cache(object):
    def __init__(self):
        self.uid2user = {}
        self.cookie_name = "spauthn"
        self.outstanding_queries = {}
        self.outstanding_certs = {}
        self.relay_state = {}
        self.user = {}
        self.result = {}

    def get_user(self, environ):
        cookie = environ.get("HTTP_COOKIE", '')
        logger.debug("Cookie: %s", cookie)
        if cookie:
            cookie_obj = SimpleCookie(cookie)
            morsel = cookie_obj.get(self.cookie_name, None)
            if morsel:
                try:
                    return self.uid2user[morsel.value]
                except KeyError:
                    return None
            else:
                logger.debug("No %s cookie", self.cookie_name)

        return None

    def delete_cookie(self, environ):
        cookie = environ.get("HTTP_COOKIE", '')
        logger.debug("delete cookie: %s", cookie)
        if cookie:
            _name = self.cookie_name
            cookie_obj = SimpleCookie(cookie)
            morsel = cookie_obj.get(_name, None)
            cookie = SimpleCookie()
            cookie[_name] = ""
            cookie[_name]['path'] = "/"
            logger.debug("Expire: %s", morsel)
            cookie[_name]["expires"] = _expiration("now")
            return cookie.output().split(": ", 1)
        return None

    def set_cookie(self, user):
        uid = rndstr(32)
        self.uid2user[uid] = user
        cookie = SimpleCookie()
        cookie[self.cookie_name] = uid
        cookie[self.cookie_name]['path'] = "/"
        cookie[self.cookie_name]["expires"] = _expiration(480)
        logger.debug("Cookie expires: %s", cookie[self.cookie_name]["expires"])
        return cookie.output().split(": ", 1)


# -----------------------------------------------------------------------------
# RECEIVERS
# -----------------------------------------------------------------------------


class Service(object):
    def __init__(self, environ, start_response, user=None):
        self.environ = environ
        logger.debug("ENVIRON: %s", environ)
        self.start_response = start_response
        self.user = user
        self.sp = None

    def unpack_redirect(self):
        if "QUERY_STRING" in self.environ:
            _qs = self.environ["QUERY_STRING"]
            return dict([(k, v[0]) for k, v in parse_qs(_qs).items()])
        else:
            return None

    def unpack_post(self):
        _dict = parse_qs(get_post(self.environ).decode('utf8'))
        logger.debug("unpack_post:: %s", _dict)
        return dict([(k, v[0]) for k, v in _dict.items()])

    def unpack_soap(self):
        try:
            query = get_post(self.environ)
            return {"SAMLResponse": query, "RelayState": ""}
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
        if not _dict:
            resp = BadRequest('Error parsing request or no request')
            return resp(self.environ, self.start_response)
        else:
            try:
                _relay_state = _dict["RelayState"]
            except KeyError:
                _relay_state = ""
            if "SAMLResponse" in _dict:
                return self.do(_dict["SAMLResponse"], binding,
                               _relay_state, mtype="response")
            elif "SAMLRequest" in _dict:
                return self.do(_dict["SAMLRequest"], binding,
                               _relay_state, mtype="request")

    def artifact_operation(self, _dict):
        if not _dict:
            resp = BadRequest("Missing query")
            return resp(self.environ, self.start_response)
        else:
            # exchange artifact for response
            request = self.sp.artifact2message(_dict["SAMLart"], "spsso")
            return self.do(request, BINDING_HTTP_ARTIFACT, _dict["RelayState"])

    def response(self, binding, http_args):
        if binding == BINDING_HTTP_ARTIFACT:
            resp = Redirect()
        else:
            resp = Response(http_args["data"], headers=http_args["headers"])
        return resp(self.environ, self.start_response)

    def do(self, query, binding, relay_state="", mtype="response"):
        pass

    def redirect(self):
        """ Expects a HTTP-redirect response """

        _dict = self.unpack_redirect()
        return self.operation(_dict, BINDING_HTTP_REDIRECT)

    def post(self):
        """ Expects a HTTP-POST response """

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

    def not_authn(self):
        resp = Unauthorized('Unknown user')
        return resp(self.environ, self.start_response)


# -----------------------------------------------------------------------------
#  Attribute Consuming service
# -----------------------------------------------------------------------------


class User(object):
    def __init__(self, name_id, data, saml_response):
        self.name_id = name_id
        self.data = data
        self.response = saml_response

    @property
    def authn_statement(self):
        xml_doc = xml.dom.minidom.parseString(
            str(self.response.assertion.authn_statement[0]))
        return xml_doc.toprettyxml()


class ACS(Service):
    def __init__(self, sp, environ, start_response, cache=None, **kwargs):
        Service.__init__(self, environ, start_response)
        self.sp = sp
        self.outstanding_queries = cache.outstanding_queries
        self.cache = cache
        self.response = None
        self.kwargs = kwargs

    def do(self, response, binding, relay_state="", mtype="response"):
        """
        :param response: The SAML response, transport encoded
        :param binding: Which binding the query came in over
        """
        # tmp_outstanding_queries = dict(self.outstanding_queries)
        if not response:
            logger.info("Missing Response")
            resp = Unauthorized('Unknown user')
            return resp(self.environ, self.start_response)

        try:
            conv_info = {'remote_addr': self.environ['REMOTE_ADDR'],
                         'request_uri': self.environ['REQUEST_URI'],
                         'entity_id': self.sp.config.entityid,
                         'endpoints': self.sp.config.getattr('endpoints', 'sp')}

            self.response = self.sp.parse_authn_request_response(
                response, binding, self.outstanding_queries,
                self.cache.outstanding_certs, conv_info=conv_info)
        except UnknownPrincipal as excp:
            logger.error("UnknownPrincipal: %s", excp)
            resp = ServiceError("UnknownPrincipal: %s" % (excp,))
            return resp(self.environ, self.start_response)
        except UnsupportedBinding as excp:
            logger.error("UnsupportedBinding: %s", excp)
            resp = ServiceError("UnsupportedBinding: %s" % (excp,))
            return resp(self.environ, self.start_response)
        except VerificationError as err:
            resp = ServiceError("Verification error: %s" % (err,))
            return resp(self.environ, self.start_response)
        except SignatureError as err:
            resp = ServiceError("Signature error: %s" % (err,))
            return resp(self.environ, self.start_response)
        except Exception as err:
            resp = ServiceError("Other error: %s" % (err,))
            return resp(self.environ, self.start_response)

        logger.info("AVA: %s", self.response.ava)

        user = User(self.response.name_id, self.response.ava, self.response)
        cookie = self.cache.set_cookie(user)

        resp = Redirect("/", headers=[
            cookie,
        ])
        return resp(self.environ, self.start_response)

    def verify_attributes(self, ava):
        logger.info("SP: %s", self.sp.config.entityid)
        rest = POLICY.get_entity_categories(
            self.sp.config.entityid, self.sp.metadata)

        akeys = [k.lower() for k in ava.keys()]

        res = {"less": [], "more": []}
        for key, attr in rest.items():
            if key not in ava:
                if key not in akeys:
                    res["less"].append(key)

        for key, attr in ava.items():
            _key = key.lower()
            if _key not in rest:
                res["more"].append(key)

        return res


# -----------------------------------------------------------------------------
# REQUESTERS
# -----------------------------------------------------------------------------


class SSO(object):
    def __init__(self, sp, environ, start_response, cache=None,
                 wayf=None, discosrv=None, bindings=None):
        self.sp = sp
        self.environ = environ
        self.start_response = start_response
        self.cache = cache
        self.idp_query_param = "IdpQuery"
        self.wayf = wayf
        self.discosrv = discosrv
        if bindings:
            self.bindings = bindings
        else:
            self.bindings = [BINDING_HTTP_REDIRECT, BINDING_HTTP_POST,
                             BINDING_HTTP_ARTIFACT]
        logger.debug("--- SSO ---")

    def response(self, binding, http_args, do_not_start_response=False):
        if binding == BINDING_HTTP_ARTIFACT:
            resp = Redirect()
        elif binding == BINDING_HTTP_REDIRECT:
            for param, value in http_args["headers"]:
                if param == "Location":
                    resp = SeeOther(str(value))
                    break
            else:
                resp = ServiceError("Parameter error")
        else:
            resp = Response(http_args["data"], headers=http_args["headers"])

        if do_not_start_response:
            return resp
        else:
            return resp(self.environ, self.start_response)

    def _wayf_redirect(self, came_from):
        sid_ = sid()
        self.cache.outstanding_queries[sid_] = came_from
        logger.debug("Redirect to WAYF function: %s", self.wayf)
        return -1, SeeOther(headers=[('Location', "%s?%s" % (self.wayf, sid_))])

    def _pick_idp(self, came_from):
        """
        If more than one idp and if none is selected, I have to do wayf or
        disco
        """

        _cli = self.sp

        logger.debug("[_pick_idp] %s", self.environ)
        if "HTTP_PAOS" in self.environ:
            if self.environ["HTTP_PAOS"] == PAOS_HEADER_INFO:
                if 'application/vnd.paos+xml' in self.environ["HTTP_ACCEPT"]:
                    # Where should I redirect the user to
                    # entityid -> the IdP to use
                    # relay_state -> when back from authentication

                    logger.debug("- ECP client detected -")

                    _rstate = rndstr()
                    self.cache.relay_state[_rstate] = geturl(self.environ)
                    _entityid = _cli.config.ecp_endpoint(
                        self.environ["REMOTE_ADDR"])

                    if not _entityid:
                        return -1, ServiceError("No IdP to talk to")
                    logger.debug("IdP to talk to: %s", _entityid)
                    return ecp.ecp_auth_request(_cli, _entityid, _rstate)
                else:
                    return -1, ServiceError('Faulty Accept header')
            else:
                return -1, ServiceError('unknown ECP version')

        # Find all IdPs
        idps = self.sp.metadata.with_descriptor("idpsso")

        idp_entity_id = None

        kaka = self.environ.get("HTTP_COOKIE", '')
        if kaka:
            try:
                (idp_entity_id, _) = parse_cookie("ve_disco", "SEED_SAW", kaka)
            except ValueError:
                pass
            except TypeError:
                pass

        # Any specific IdP specified in a query part
        query = self.environ.get("QUERY_STRING")
        if not idp_entity_id and query:
            try:
                _idp_entity_id = dict(parse_qs(query))[
                    self.idp_query_param][0]
                if _idp_entity_id in idps:
                    idp_entity_id = _idp_entity_id
            except KeyError:
                logger.debug("No IdP entity ID in query: %s", query)
                pass

        if not idp_entity_id:

            if self.wayf:
                if query:
                    try:
                        wayf_selected = dict(parse_qs(query))[
                            "wayf_selected"][0]
                    except KeyError:
                        return self._wayf_redirect(came_from)
                    idp_entity_id = wayf_selected
                else:
                    return self._wayf_redirect(came_from)
            elif self.discosrv:
                if query:
                    idp_entity_id = _cli.parse_discovery_service_response(
                        query=self.environ.get("QUERY_STRING"))
                if not idp_entity_id:
                    sid_ = sid()
                    self.cache.outstanding_queries[sid_] = came_from
                    logger.debug("Redirect to Discovery Service function")
                    eid = _cli.config.entityid
                    ret = _cli.config.getattr("endpoints",
                                              "sp")["discovery_response"][0][0]
                    ret += "?sid=%s" % sid_
                    loc = _cli.create_discovery_service_request(
                        self.discosrv, eid, **{"return": ret})
                    return -1, SeeOther(loc)
            elif len(idps) == 1:
                # idps is a dictionary
                idp_entity_id = list(idps.keys())[0]
            elif not len(idps):
                return -1, ServiceError('Misconfiguration')
            else:
                return -1, NotImplemented("No WAYF or DS present!")

        logger.info("Chosen IdP: '%s'", idp_entity_id)
        return 0, idp_entity_id

    def redirect_to_auth(self, _cli, entity_id, came_from, sigalg=""):
        try:
            # Picks a binding to use for sending the Request to the IDP
            _binding, destination = _cli.pick_binding(
                "single_sign_on_service", self.bindings, "idpsso",
                entity_id=entity_id)
            logger.debug("binding: %s, destination: %s", _binding,
                         destination)
            # Binding here is the response binding that is which binding the
            # IDP should use to return the response.
            acs = _cli.config.getattr("endpoints", "sp")[
                "assertion_consumer_service"]
            # just pick one
            endp, return_binding = acs[0]

            extensions = None
            cert = None
            if _cli.config.generate_cert_func is not None:
                cert_str, req_key_str = _cli.config.generate_cert_func()
                cert = {
                    "cert": cert_str,
                    "key": req_key_str
                }
                spcertenc = SPCertEnc(x509_data=ds.X509Data(
                    x509_certificate=ds.X509Certificate(text=cert_str)))
                extensions = Extensions(extension_elements=[
                    element_to_extension_element(spcertenc)])

            req_id, req = _cli.create_authn_request(destination,
                                                    binding=return_binding,
                                                    extensions=extensions,
                                                    nameid_format=NAMEID_FORMAT_PERSISTENT)
            _rstate = rndstr()
            self.cache.relay_state[_rstate] = came_from
            ht_args = _cli.apply_binding(_binding, "%s" % req, destination,
                                         relay_state=_rstate,
                                         sigalg=sigalg)
            _sid = req_id

            if cert is not None:
                self.cache.outstanding_certs[_sid] = cert

        except Exception as exc:
            logger.exception(exc)
            resp = ServiceError(
                "Failed to construct the AuthnRequest: %s" % exc)
            return resp

        # remember the request
        self.cache.outstanding_queries[_sid] = came_from
        return self.response(_binding, ht_args, do_not_start_response=True)

    def do(self):
        _cli = self.sp

        # Which page was accessed to get here
        came_from = geturl(self.environ)
        logger.debug("[sp.challenge] RelayState >> '%s'", came_from)

        # If more than one idp and if none is selected, I have to do wayf
        (done, response) = self._pick_idp(came_from)
        # Three cases: -1 something went wrong or Discovery service used
        #               0 I've got an IdP to send a request to
        #               >0 ECP in progress
        logger.debug("_idp_pick returned: %s", done)
        if done == -1:
            return response(self.environ, self.start_response)
        elif done > 0:
            self.cache.outstanding_queries[done] = came_from
            return ECPResponse(response)
        else:
            entity_id = response
            # Do the AuthnRequest
            resp = self.redirect_to_auth(_cli, entity_id, came_from)
            return resp(self.environ, self.start_response)


# ----------------------------------------------------------------------------


class SLO(Service):
    def __init__(self, sp, environ, start_response, cache=None):
        Service.__init__(self, environ, start_response)
        self.sp = sp
        self.cache = cache

    def do(self, message, binding, relay_state="", mtype="response"):
        try:
            txt = decode_base64_and_inflate(message)
            is_logout_request = 'LogoutRequest' in txt.split('>', 1)[0]
        except:  # TODO: parse the XML correctly
            is_logout_request = False

        if is_logout_request:
            self.sp.parse_logout_request(message, binding)
        else:
            self.sp.parse_logout_request_response(message, binding)

        return finish_logout(self.environ, self.start_response)


# ----------------------------------------------------------------------------


# noinspection PyUnusedLocal
def not_found(environ, start_response):
    """Called if no URL matches."""
    resp = NotFound('Not Found')
    return resp(environ, start_response)


# ----------------------------------------------------------------------------


# noinspection PyUnusedLocal
def main(environ, start_response, sp):
    user = CACHE.get_user(environ)

    if user is None:
        sso = SSO(sp, environ, start_response, cache=CACHE, **ARGS)
        return sso.do()

    body = dict_to_table(user.data)
    authn_stmt = cgi.escape(user.authn_statement)
    body.append('<br><pre>' + authn_stmt + "</pre>")
    body.append('<br><a href="/logout">logout</a>')

    resp = Response(body)
    return resp(environ, start_response)


def disco(environ, start_response, _sp):
    query = parse_qs(environ["QUERY_STRING"])
    entity_id = query["entityID"][0]
    _sid = query["sid"][0]
    came_from = CACHE.outstanding_queries[_sid]
    _sso = SSO(_sp, environ, start_response, cache=CACHE, **ARGS)
    resp = _sso.redirect_to_auth(_sso.sp, entity_id, came_from)

    # Add cookie
    kaka = make_cookie("ve_disco", entity_id, "SEED_SAW")
    resp.headers.append(kaka)
    return resp(environ, start_response)


# ----------------------------------------------------------------------------


# noinspection PyUnusedLocal
def logout(environ, start_response, sp):
    user = CACHE.get_user(environ)

    if user is None:
        sso = SSO(sp, environ, start_response, cache=CACHE, **ARGS)
        return sso.do()

    logger.info("[logout] subject_id: '%s'", user.name_id)

    # What if more than one
    data = sp.global_logout(user.name_id)
    logger.info("[logout] global_logout > %s", data)

    for entity_id, logout_info in data.items():
        if isinstance(logout_info, tuple):
            binding, http_info = logout_info

            if binding == BINDING_HTTP_POST:
                body = ''.join(http_info['data'])
                resp = Response(body)
                return resp(environ, start_response)
            elif binding == BINDING_HTTP_REDIRECT:
                for key, value in http_info['headers']:
                    if key.lower() == 'location':
                        resp = Redirect(value)
                        return resp(environ, start_response)

                resp = ServiceError('missing Location header')
                return resp(environ, start_response)
            else:
                resp = ServiceError('unknown logout binding: %s', binding)
                return resp(environ, start_response)
        else:  # result from logout, should be OK
            pass

    return finish_logout(environ, start_response)


def finish_logout(environ, start_response):
    logger.info("[logout done] environ: %s", environ)
    logger.info("[logout done] remaining subjects: %s", CACHE.uid2user.values())

    # remove cookie and stored info
    cookie = CACHE.delete_cookie(environ)

    resp = Response('You are now logged out of this service', headers=[
        cookie,
    ])
    return resp(environ, start_response)


# ----------------------------------------------------------------------------

# map urls to functions
urls = [
    # Hmm, place holder, NOT used
    ('place', ("holder", None)),
    (r'^$', main),
    (r'^disco', disco),
    (r'^logout$', logout),
]


def add_urls():
    base = "acs"

    urls.append(("%s/post$" % base, (ACS, "post", SP)))
    urls.append(("%s/post/(.*)$" % base, (ACS, "post", SP)))
    urls.append(("%s/redirect$" % base, (ACS, "redirect", SP)))
    urls.append(("%s/redirect/(.*)$" % base, (ACS, "redirect", SP)))

    base = "slo"

    urls.append(("%s/post$" % base, (SLO, "post", SP)))
    urls.append(("%s/post/(.*)$" % base, (SLO, "post", SP)))
    urls.append(("%s/redirect$" % base, (SLO, "redirect", SP)))
    urls.append(("%s/redirect/(.*)$" % base, (SLO, "redirect", SP)))


# ----------------------------------------------------------------------------

def metadata(environ, start_response):
    try:
        path = _args.path
        if path is None or len(path) == 0:
            path = os.path.dirname(os.path.abspath(__file__))
        if path[-1] != "/":
            path += "/"
        metadata = create_metadata_string(path + "sp_conf.py", None,
                                          _args.valid, _args.cert,
                                          _args.keyfile,
                                          _args.id, _args.name, _args.sign)
        start_response('200 OK', [('Content-Type', "text/xml")])
        return metadata
    except Exception as ex:
        logger.error("An error occured while creating metadata: %s", ex.message)
        return not_found(environ, start_response)


def application(environ, start_response):
    """
    The main WSGI application. Dispatch the current request to
    the functions from above.

    If nothing matches, call the `not_found` function.

    :param environ: The HTTP application environment
    :param start_response: The application to run when the handling of the
        request is done
    :return: The response as a list of lines
    """
    path = environ.get('PATH_INFO', '').lstrip('/')
    logger.debug("<application> PATH: '%s'", path)

    if path == "metadata":
        return metadata(environ, start_response)

    logger.debug("Finding callback to run")
    try:
        for regex, spec in urls:
            match = re.search(regex, path)
            if match is not None:
                if isinstance(spec, tuple):
                    callback, func_name, _sp = spec
                    cls = callback(_sp, environ, start_response, cache=CACHE)
                    func = getattr(cls, func_name)
                    return func()
                else:
                    return spec(environ, start_response, SP)
        if re.match(".*static/.*", path):
            return handle_static(environ, start_response, path)
        return not_found(environ, start_response)
    except StatusError as err:
        logging.error("StatusError: %s" % err)
        resp = BadRequest("%s" % err)
        return resp(environ, start_response)
    except Exception as err:
        # _err = exception_trace("RUN", err)
        # logging.error(exception_trace("RUN", _err))
        print(err, file=sys.stderr)
        resp = ServiceError("%s" % err)
        return resp(environ, start_response)


if __name__ == '__main__':
    from cherrypy import wsgiserver

    _parser = argparse.ArgumentParser()
    _parser.add_argument('-d', dest='debug', action='store_true',
                         help="Print debug information")
    _parser.add_argument('-D', dest='discosrv',
                         help="Which disco server to use")
    _parser.add_argument('-s', dest='seed',
                         help="Cookie seed")
    _parser.add_argument('-W', dest='wayf', action='store_true',
                         help="Which WAYF url to use")
    _parser.add_argument("config", help="SAML client config")
    _parser.add_argument('-p', dest='path', help='Path to configuration file.')
    _parser.add_argument('-v', dest='valid', default="4",
                         help="How long, in days, the metadata is valid from "
                              "the time of creation")
    _parser.add_argument('-c', dest='cert', help='certificate')
    _parser.add_argument('-i', dest='id',
                         help="The ID of the entities descriptor in the "
                              "metadata")
    _parser.add_argument('-k', dest='keyfile',
                         help="A file with a key to sign the metadata with")
    _parser.add_argument('-n', dest='name')
    _parser.add_argument('-S', dest='sign', action='store_true',
                         help="sign the metadata")
    _parser.add_argument('-C', dest='service_conf_module',
                         help="service config module")

    ARGS = {}
    _args = _parser.parse_args()
    if _args.discosrv:
        ARGS["discosrv"] = _args.discosrv
    if _args.wayf:
        ARGS["wayf"] = _args.wayf

    CACHE = Cache()
    CNFBASE = _args.config
    if _args.seed:
        SEED = _args.seed
    else:
        SEED = "SnabbtInspel"

    if _args.service_conf_module:
        service_conf = importlib.import_module(_args.service_conf_module)
    else:
        import service_conf

    HOST = service_conf.HOST
    PORT = service_conf.PORT
    # ------- HTTPS -------
    # These should point to relevant files
    SERVER_CERT = service_conf.SERVER_CERT
    SERVER_KEY = service_conf.SERVER_KEY
    # This is of course the certificate chain for the CA that signed
    # your cert and all the way up to the top
    CERT_CHAIN = service_conf.CERT_CHAIN

    SP = Saml2Client(config_file="%s" % CNFBASE)

    POLICY = service_conf.POLICY

    add_urls()
    sign_alg = None
    digest_alg = None
    try:
        sign_alg = service_conf.SIGN_ALG
    except:
        pass
    try:
        digest_alg = service_conf.DIGEST_ALG
    except:
        pass
    ds.DefaultSignature(sign_alg, digest_alg)

    SRV = wsgiserver.CherryPyWSGIServer((HOST, PORT), application)

    _https = ""
    if service_conf.HTTPS:
        from cherrypy.wsgiserver import ssl_pyopenssl

        SRV.ssl_adapter = ssl_pyopenssl.pyOpenSSLAdapter(SERVER_CERT,
                                                         SERVER_KEY, CERT_CHAIN)
        _https = " using SSL/TLS"
    logger.info("Server starting")
    print("SP listening on %s:%s%s" % (HOST, PORT, _https))
    try:
        SRV.start()
    except KeyboardInterrupt:
        SRV.stop()
