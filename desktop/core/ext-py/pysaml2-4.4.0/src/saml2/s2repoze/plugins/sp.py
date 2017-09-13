#
"""
A plugin that allows you to use SAML2 SSO as authentication
and SAML2 attribute aggregations as metadata collector in your
WSGI application.

"""
import logging
import sys
import platform
import shelve
import traceback
import saml2
import six
from saml2.samlp import Extensions
from saml2 import xmldsig as ds

from future.backports.urllib.parse import parse_qs
from future.backports.urllib.parse import urlparse

from six import StringIO

from paste.httpexceptions import HTTPSeeOther, HTTPRedirection
from paste.httpexceptions import HTTPNotImplemented
from paste.httpexceptions import HTTPInternalServerError
from paste.request import parse_dict_querystring
from paste.request import construct_url
from saml2.extension.pefim import SPCertEnc
from saml2.httputil import SeeOther
from saml2.client_base import ECP_SERVICE
from zope.interface import implementer

from repoze.who.interfaces import IChallenger, IIdentifier, IAuthenticator
from repoze.who.interfaces import IMetadataProvider

from saml2 import ecp, BINDING_HTTP_REDIRECT, element_to_extension_element
from saml2 import BINDING_HTTP_POST

from saml2.client import Saml2Client
from saml2.ident import code, decode
from saml2.s_utils import sid
from saml2.config import config_factory
from saml2.profile import paos

# from saml2.population import Population
#from saml2.attribute_resolver import AttributeResolver

logger = logging.getLogger(__name__)

PAOS_HEADER_INFO = 'ver="%s";"%s"' % (paos.NAMESPACE, ECP_SERVICE)


def construct_came_from(environ):
    """ The URL that the user used when the process where interupted
    for single-sign-on processing. """

    came_from = environ.get("PATH_INFO")
    qstr = environ.get("QUERY_STRING", "")
    if qstr:
        came_from += '?' + qstr
    return came_from


def exception_trace(tag, exc, log):
    message = traceback.format_exception(*sys.exc_info())
    log.error("[%s] ExcList: %s" % (tag, "".join(message),))
    log.error("[%s] Exception: %s" % (tag, exc))


class ECP_response(object):
    code = 200
    title = 'OK'

    def __init__(self, content):
        self.content = content

    #noinspection PyUnusedLocal
    def __call__(self, environ, start_response):
        start_response('%s %s' % (self.code, self.title),
                       [('Content-Type', "text/xml")])
        return [self.content]


@implementer(IChallenger, IIdentifier, IAuthenticator, IMetadataProvider)
class SAML2Plugin(object):

    def __init__(self, rememberer_name, config, saml_client, wayf, cache,
                 sid_store=None, discovery="", idp_query_param="",
                 sid_store_cert=None, ):
        self.rememberer_name = rememberer_name
        self.wayf = wayf
        self.saml_client = saml_client
        self.conf = config
        self.cache = cache
        self.discosrv = discovery
        self.idp_query_param = idp_query_param
        self.logout_endpoints = [urlparse(ep)[2] for ep in config.endpoint(
            "single_logout_service")]
        try:
            self.metadata = self.conf.metadata
        except KeyError:
            self.metadata = None
        if sid_store:
            self.outstanding_queries = shelve.open(sid_store, writeback=True,
                                                   protocol=2)
        else:
            self.outstanding_queries = {}
        if sid_store_cert:
            self.outstanding_certs = shelve.open(sid_store_cert, writeback=True,
                                                 protocol=2)
        else:
            self.outstanding_certs = {}

        self.iam = platform.node()

    def _get_rememberer(self, environ):
        rememberer = environ['repoze.who.plugins'][self.rememberer_name]
        return rememberer

    #### IIdentifier ####
    def remember(self, environ, identity):
        rememberer = self._get_rememberer(environ)
        return rememberer.remember(environ, identity)

    #### IIdentifier ####
    def forget(self, environ, identity):
        rememberer = self._get_rememberer(environ)
        return rememberer.forget(environ, identity)

    def _get_post(self, environ):
        """
        Get the posted information

        :param environ: A dictionary with environment variables
        """

        body = ''
        try:
            length = int(environ.get('CONTENT_LENGTH', '0'))
        except ValueError:
            length = 0
        if length != 0:
            body = environ['wsgi.input'].read(length)  # get the POST variables
            environ[
                's2repoze.body'] = body  # store the request body for later
                # use by pysaml2
            environ['wsgi.input'] = StringIO(body)  # restore the request body
                # as a stream so that everything seems untouched

        post = parse_qs(body)  # parse the POST fields into a dict

        logger.debug('identify post: %s', post)

        return post

    def _wayf_redirect(self, came_from):
        sid_ = sid()
        self.outstanding_queries[sid_] = came_from
        logger.info("Redirect to WAYF function: %s", self.wayf)
        return -1, HTTPSeeOther(headers=[('Location',
                                          "%s?%s" % (self.wayf, sid_))])

    #noinspection PyUnusedLocal
    def _pick_idp(self, environ, came_from):
        """
        If more than one idp and if none is selected, I have to do wayf or
        disco
        """

        # check headers to see if it's an ECP request
        #        headers = {
        #                    'Accept' : 'text/html; application/vnd.paos+xml',
        #                    'PAOS'   : 'ver="%s";"%s"' % (paos.NAMESPACE,
        # SERVICE)
        #                    }

        _cli = self.saml_client

        logger.info("[_pick_idp] %s", environ)
        if "HTTP_PAOS" in environ:
            if environ["HTTP_PAOS"] == PAOS_HEADER_INFO:
                if 'application/vnd.paos+xml' in environ["HTTP_ACCEPT"]:
                    # Where should I redirect the user to
                    # entityid -> the IdP to use
                    # relay_state -> when back from authentication

                    logger.info("- ECP client detected -")

                    _relay_state = construct_came_from(environ)
                    _entityid = _cli.config.ecp_endpoint(environ["REMOTE_ADDR"])

                    if not _entityid:
                        return -1, HTTPInternalServerError(
                            detail="No IdP to talk to")
                    logger.info("IdP to talk to: %s", _entityid)
                    return ecp.ecp_auth_request(_cli, _entityid,
                                                _relay_state)
                else:
                    return -1, HTTPInternalServerError(
                        detail='Faulty Accept header')
            else:
                return -1, HTTPInternalServerError(
                    detail='unknown ECP version')

        idps = self.metadata.with_descriptor("idpsso")

        logger.info("IdP URL: %s", idps)

        idp_entity_id = query = None

        for key in ['s2repoze.body', "QUERY_STRING"]:
            query = environ.get(key)
            if query:
                try:
                    _idp_entity_id = dict(parse_qs(query))[
                        self.idp_query_param][0]
                    if _idp_entity_id in idps:
                        idp_entity_id = _idp_entity_id
                    break
                except KeyError:
                    logger.debug("No IdP entity ID in query: %s", query)
                    pass

        if idp_entity_id is None:
            if len(idps) == 1:
                # idps is a dictionary
                idp_entity_id = idps.keys()[0]
            elif not len(idps):
                return -1, HTTPInternalServerError(detail='Misconfiguration')
            else:
                idp_entity_id = ""
                logger.info("ENVIRON: %s", environ)

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
                            query=environ.get("QUERY_STRING"))
                    else:
                        sid_ = sid()
                        self.outstanding_queries[sid_] = came_from
                        logger.debug("Redirect to Discovery Service function")
                        eid = _cli.config.entityid
                        ret = _cli.config.getattr(
                            "endpoints", "sp")["discovery_response"][0][0]
                        ret += "?sid=%s" % sid_
                        loc = _cli.create_discovery_service_request(
                            self.discosrv, eid, **{"return": ret})
                        return -1, SeeOther(loc)

                else:
                    return -1, HTTPNotImplemented(
                        detail='No WAYF or DJ present!')

        logger.info("Chosen IdP: '%s'", idp_entity_id)
        return 0, idp_entity_id

    #### IChallenger ####
    #noinspection PyUnusedLocal
    def challenge(self, environ, _status, _app_headers, _forget_headers):

        _cli = self.saml_client

        if 'REMOTE_USER' in environ:
            name_id = decode(environ["REMOTE_USER"])

            _cli = self.saml_client
            path_info = environ['PATH_INFO']

            if 'samlsp.logout' in environ:
                responses = _cli.global_logout(name_id)
                return self._handle_logout(responses)

        if 'samlsp.pending' in environ:
            response = environ['samlsp.pending']
            if isinstance(response, HTTPRedirection):
                response.headers += _forget_headers
            return response

        #logger = environ.get('repoze.who.logger','')

        # Which page was accessed to get here
        came_from = construct_came_from(environ)
        environ["myapp.came_from"] = came_from
        logger.debug("[sp.challenge] RelayState >> '%s'", came_from)

        # Am I part of a virtual organization or more than one ?
        try:
            vorg_name = environ["myapp.vo"]
        except KeyError:
            try:
                vorg_name = _cli.vorg._name
            except AttributeError:
                vorg_name = ""

        logger.info("[sp.challenge] VO: %s", vorg_name)

        # If more than one idp and if none is selected, I have to do wayf
        (done, response) = self._pick_idp(environ, came_from)
        # Three cases: -1 something went wrong or Discovery service used
        #               0 I've got an IdP to send a request to
        #               >0 ECP in progress
        logger.debug("_idp_pick returned: %s", done)
        if done == -1:
            return response
        elif done > 0:
            self.outstanding_queries[done] = came_from
            return ECP_response(response)
        else:
            entity_id = response
            logger.info("[sp.challenge] entity_id: %s", entity_id)
            # Do the AuthnRequest
            _binding = BINDING_HTTP_REDIRECT
            try:
                srvs = _cli.metadata.single_sign_on_service(entity_id, _binding)
                logger.debug("srvs: %s", srvs)
                dest = srvs[0]["location"]
                logger.debug("destination: %s", dest)

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

                if _cli.authn_requests_signed:
                    _sid = saml2.s_utils.sid()
                    req_id, msg_str = _cli.create_authn_request(
                        dest, vorg=vorg_name, sign=_cli.authn_requests_signed,
                        message_id=_sid, extensions=extensions)
                    _sid = req_id
                else:
                    req_id, req = _cli.create_authn_request(
                        dest, vorg=vorg_name, sign=False, extensions=extensions)
                    msg_str = "%s" % req
                    _sid = req_id

                if cert is not None:
                    self.outstanding_certs[_sid] = cert

                ht_args = _cli.apply_binding(_binding, msg_str,
                                             destination=dest,
                                             relay_state=came_from)

                logger.debug("ht_args: %s", ht_args)
            except Exception as exc:
                logger.exception(exc)
                raise Exception(
                    "Failed to construct the AuthnRequest: %s" % exc)

            try:
                ret = _cli.config.getattr(
                    "endpoints", "sp")["discovery_response"][0][0]
                if (environ["PATH_INFO"]) in ret and ret.split(
                        environ["PATH_INFO"])[1] == "":
                    query = parse_qs(environ["QUERY_STRING"])
                    sid = query["sid"][0]
                    came_from = self.outstanding_queries[sid]
            except:
                pass
            # remember the request
            self.outstanding_queries[_sid] = came_from

            if not ht_args["data"] and ht_args["headers"][0][0] == "Location":
                logger.debug('redirect to: %s', ht_args["headers"][0][1])
                return HTTPSeeOther(headers=ht_args["headers"])
            else:
                return ht_args["data"]

    def _construct_identity(self, session_info):
        cni = code(session_info["name_id"])
        identity = {
            "login": cni,
            "password": "",
            'repoze.who.userid': cni,
            "user": session_info["ava"],
        }
        logger.debug("Identity: %s", identity)

        return identity

    def _eval_authn_response(self, environ, post, binding=BINDING_HTTP_POST):
        logger.info("Got AuthN response, checking..")
        logger.info("Outstanding: %s", self.outstanding_queries)

        try:
            # Evaluate the response, returns a AuthnResponse instance
            try:
                authresp = self.saml_client.parse_authn_request_response(
                    post["SAMLResponse"][0], binding, self.outstanding_queries,
                    self.outstanding_certs)

            except Exception as excp:
                logger.exception("Exception: %s" % (excp,))
                raise

            session_info = authresp.session_info()
        except TypeError as excp:
            logger.exception("Exception: %s" % (excp,))
            return None

        if session_info["came_from"]:
            logger.debug("came_from << %s", session_info["came_from"])
            try:
                path, query = session_info["came_from"].split('?')
                environ["PATH_INFO"] = path
                environ["QUERY_STRING"] = query
            except ValueError:
                environ["PATH_INFO"] = session_info["came_from"]

        logger.info("Session_info: %s", session_info)
        return session_info

    def do_ecp_response(self, body, environ):
        response, _relay_state = ecp.handle_ecp_authn_response(self.saml_client,
                                                               body)

        environ["s2repoze.relay_state"] = _relay_state.text
        session_info = response.session_info()
        logger.info("Session_info: %s", session_info)

        return session_info

    #### IIdentifier ####
    def identify(self, environ):
        """
        Tries to do the identification
        """
        #logger = environ.get('repoze.who.logger', '')

        query = parse_dict_querystring(environ)
        if ("CONTENT_LENGTH" not in environ or not environ[
            "CONTENT_LENGTH"]) and \
                        "SAMLResponse" not in query and "SAMLRequest" not in \
                query:
            logger.debug('[identify] get or empty post')
            return None

        # if logger:
        #     logger.info("ENVIRON: %s", environ)
        #     logger.info("self: %s", self.__dict__)

        uri = environ.get('REQUEST_URI', construct_url(environ))

        logger.debug('[sp.identify] uri: %s', uri)

        query = parse_dict_querystring(environ)
        logger.debug('[sp.identify] query: %s', query)

        if "SAMLResponse" in query or "SAMLRequest" in query:
            post = query
            binding = BINDING_HTTP_REDIRECT
        else:
            post = self._get_post(environ)
            binding = BINDING_HTTP_POST

        try:
            logger.debug('[sp.identify] post keys: %s', post.keys())
        except (TypeError, IndexError):
            pass

        try:
            path_info = environ['PATH_INFO']
            logout = False
            if path_info in self.logout_endpoints:
                logout = True

            if logout and "SAMLRequest" in post:
                print("logout request received")
                try:
                    response = self.saml_client.handle_logout_request(
                        post["SAMLRequest"][0],
                        self.saml_client.users.subjects()[0], binding)
                    environ['samlsp.pending'] = self._handle_logout(response)
                    return {}
                except:
                    import traceback

                    traceback.print_exc()
            elif "SAMLResponse" not in post:
                logger.info("[sp.identify] --- NOT SAMLResponse ---")
                # Not for me, put the post back where next in line can
                # find it
                environ["post.fieldstorage"] = post
                # restore wsgi.input incase that is needed
                # only of s2repoze.body is present
                if 's2repoze.body' in environ:
                    environ['wsgi.input'] = StringIO(environ['s2repoze.body'])
                return {}
            else:
                logger.info("[sp.identify] --- SAMLResponse ---")
                # check for SAML2 authN response
                #if self.debug:
                try:
                    if logout:
                        response = \
                            self.saml_client.parse_logout_request_response(
                            post["SAMLResponse"][0], binding)
                        if response:
                            action = self.saml_client.handle_logout_response(
                                response)

                            if type(action) == dict:
                                request = self._handle_logout(action)
                            else:
                                #logout complete
                                request = HTTPSeeOther(headers=[
                                    ('Location', "/")])
                            if request:
                                environ['samlsp.pending'] = request
                            return {}
                    else:
                        session_info = self._eval_authn_response(
                            environ, post,
                            binding=binding)
                except Exception as err:
                    environ["s2repoze.saml_error"] = err
                    return {}
        except TypeError as exc:
            # might be a ECP (=SOAP) response
            body = environ.get('s2repoze.body', None)
            if body:
                # might be a ECP response
                try:
                    session_info = self.do_ecp_response(body, environ)
                except Exception as err:
                    environ["post.fieldstorage"] = post
                    environ["s2repoze.saml_error"] = err
                    return {}
            else:
                exception_trace("sp.identity", exc, logger)
                environ["post.fieldstorage"] = post
                return {}

        if session_info:
            environ["s2repoze.sessioninfo"] = session_info
            return self._construct_identity(session_info)
        else:
            return None

    # IMetadataProvider
    def add_metadata(self, environ, identity):
        """ Add information to the knowledge I have about the user """
        name_id = identity['repoze.who.userid']
        if isinstance(name_id, six.string_types):
            try:
                # Make sure that userids authenticated by another plugin
                # don't cause problems here.
                name_id = decode(name_id)
            except:
                pass

        _cli = self.saml_client
        logger.debug("[add_metadata] for %s", name_id)
        try:
            logger.debug("Issuers: %s", _cli.users.sources(name_id))
        except KeyError:
            pass

        if "user" not in identity:
            identity["user"] = {}
        try:
            (ava, _) = _cli.users.get_identity(name_id)
            #now = time.gmtime()
            logger.debug("[add_metadata] adds: %s", ava)
            identity["user"].update(ava)
        except KeyError:
            pass

        if "pysaml2_vo_expanded" not in identity and _cli.vorg:
            # is this a Virtual Organization situation
            for vo in _cli.vorg.values():
                try:
                    if vo.do_aggregation(name_id):
                        # Get the extended identity
                        identity["user"] = _cli.users.get_identity(name_id)[0]
                        # Only do this once, mark that the identity has been
                        # expanded
                        identity["pysaml2_vo_expanded"] = 1
                except KeyError:
                    logger.exception("Failed to do attribute aggregation, "
                                     "missing common attribute")
        logger.debug("[add_metadata] returns: %s", dict(identity))

        if not identity["user"]:
            # remove cookie and demand re-authentication
            pass

    # used 2 times : one to get the ticket, the other to validate it
    @staticmethod
    def _service_url(environ, qstr=None):
        if qstr is not None:
            url = construct_url(environ, querystring=qstr)
        else:
            url = construct_url(environ)
        return url

    #### IAuthenticatorPlugin ####
    #noinspection PyUnusedLocal
    def authenticate(self, environ, identity=None):
        if identity:
            if identity.get('user') and environ.get(
                    's2repoze.sessioninfo') and identity.get(
                    'user') == environ.get('s2repoze.sessioninfo').get('ava'):
                return identity.get('login')
            tktuser = identity.get('repoze.who.plugins.auth_tkt.userid', None)
            if tktuser and self.saml_client.is_logged_in(decode(tktuser)):
                return tktuser
            return None
        else:
            return None

    @staticmethod
    def _handle_logout(responses):
        if 'data' in responses:
            ht_args = responses
        else:
            ht_args = responses[responses.keys()[0]][1]
        if not ht_args["data"] and ht_args["headers"][0][0] == "Location":
            logger.debug('redirect to: %s', ht_args["headers"][0][1])
            return HTTPSeeOther(headers=ht_args["headers"])
        else:
            return ht_args["data"]


def make_plugin(remember_name=None,  # plugin for remember
                cache="",  # cache
                # Which virtual organization to support
                virtual_organization="",
                saml_conf="",
                wayf="",
                sid_store="",
                identity_cache="",
                discovery="",
                idp_query_param=""
):
    if saml_conf is "":
        raise ValueError(
            'must include saml_conf in configuration')

    if remember_name is None:
        raise ValueError('must include remember_name in configuration')

    conf = config_factory("sp", saml_conf)

    scl = Saml2Client(config=conf, identity_cache=identity_cache,
                      virtual_organization=virtual_organization)

    plugin = SAML2Plugin(remember_name, conf, scl, wayf, cache, sid_store,
                         discovery, idp_query_param)
    return plugin
