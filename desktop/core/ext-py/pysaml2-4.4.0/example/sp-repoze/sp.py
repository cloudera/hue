#!/usr/bin/env python
from Cookie import SimpleCookie
import logging
import os
import sp_conf
from sp_conf import CONFIG
import re
import subprocess
from urlparse import parse_qs
import argparse
from saml2 import BINDING_HTTP_REDIRECT, time_util
from saml2.httputil import Response
from saml2.httputil import Unauthorized
from saml2.httputil import NotFound
from saml2.httputil import Redirect
#from saml2.httputil import ServiceError
from saml2.metadata import create_metadata_string
from saml2.metadata import entities_descriptor
from saml2.config import Config
from saml2.sigver import security_context

logger = logging.getLogger("saml2.SP")

args = None
# -----------------------------------------------------------------------------


def dict_to_table(ava, lev=0, width=1):
    txt = ['<table border=%s bordercolor="black">\n' % width]
    for prop, valarr in ava.items():
        txt.append("<tr>\n")
        if isinstance(valarr, basestring):
            txt.append("<th>%s</th>\n" % str(prop))
            try:
                txt.append("<td>%s</td>\n" % valarr.encode("utf8"))
            except AttributeError:
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
                    try:
                        txt.append("<td>%s</td>\n" % val.encode("utf8"))
                    except AttributeError:
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


def _expiration(timeout, tformat=None):
    if timeout == "now":
        return time_util.instant(tformat)
    else:
        # validity time should match lifetime of assertions
        return time_util.in_a_while(minutes=timeout, format=tformat)


def delete_cookie(environ, name):
    kaka = environ.get("HTTP_COOKIE", '')
    if kaka:
        cookie_obj = SimpleCookie(kaka)
        morsel = cookie_obj.get(name, None)
        cookie = SimpleCookie()
        cookie[name] = morsel
        cookie[name]["expires"] = _expiration("now",
                                              "%a, %d-%b-%Y %H:%M:%S CET")
        return tuple(cookie.output().split(": ", 1))
    return None

# ----------------------------------------------------------------------------


#noinspection PyUnusedLocal
def whoami(environ, start_response, user):
    nameid = environ["repoze.who.identity"]["login"]
    ava = environ["repoze.who.identity"]["user"]
    if not nameid:
        return not_authn(environ, start_response)
    if ava:
        response = ["<h2>Your identity is supposed to be</h2>"]
        response.extend(dict_to_table(ava))
    else:
        response = [
            "<h2>The system did not return any information about you</h2>"]

    response.extend("<a href='logout'>Logout</a>")
    resp = Response(response)
    return resp(environ, start_response)


#noinspection PyUnusedLocal
def not_found(environ, start_response):
    """Called if no URL matches."""
    resp = NotFound('Not Found')
    return resp(environ, start_response)


#noinspection PyUnusedLocal
def not_authn(environ, start_response):
    resp = Unauthorized('Unknown user')
    return resp(environ, start_response)


#noinspection PyUnusedLocal
def slo(environ, start_response, user):
    # so here I might get either a LogoutResponse or a LogoutRequest
    client = environ['repoze.who.plugins']["saml2auth"]
    sc = client.saml_client

    if "QUERY_STRING" in environ:
        query = parse_qs(environ["QUERY_STRING"])
        logger.info("query: %s", query)
        try:
            response = sc.parse_logout_request_response(
                query["SAMLResponse"][0], binding=BINDING_HTTP_REDIRECT)
            if response:
                logger.info("LOGOUT response parsed OK")
        except KeyError:
            # return error reply
            response = None

        if response is None:
            request = sc.lo

    headers = []
    delco = delete_cookie(environ, "pysaml2")
    if delco:
        headers.append(delco)
    resp = Redirect("/done", headers=headers)
    return resp(environ, start_response)


#noinspection PyUnusedLocal
def logout(environ, start_response, user):
    # This is where it starts when a user wants to log out
    client = environ['repoze.who.plugins']["saml2auth"]
    subject_id = environ["repoze.who.identity"]['repoze.who.userid']
    logger.info("[logout] subject_id: '%s'", subject_id)
    target = "/done"

    # What if more than one
    _dict = client.saml_client.global_logout(subject_id)
    logger.info("[logout] global_logout > %s", _dict)
    rem = environ['repoze.who.plugins'][client.rememberer_name]
    rem.forget(environ, subject_id)

    for key, item in _dict.items():
        if isinstance(item, tuple):
            binding, htargs = item
        else:  # result from logout, should be OK
            pass

    resp = Redirect("Successful Logout", headers=[("Location", target)])
    return resp(environ, start_response)
    # else:
    #     resp = ServiceError("Failed to logout from identity services")
    #     start_response("500 Internal Server Error")
    #     return []


#noinspection PyUnusedLocal
def done(environ, start_response, user):
    # remove cookie and stored info
    logger.info("[done] environ: %s", environ)
    subject_id = environ["repoze.who.identity"]['repoze.who.userid']
    client = environ['repoze.who.plugins']["saml2auth"]
    logger.info("[logout done] remaining subjects: %s",
        client.saml_client.users.subjects())

    start_response('200 OK', [('Content-Type', 'text/html')])
    return ["<h3>You are now logged out from this service</h3>"]

# ----------------------------------------------------------------------------

# map urls to functions
urls = [
    (r'whoami$', whoami),
    (r'logout$', logout),
    (r'done$', done),
    (r'slo$', slo),
    (r'^$', whoami),
]

# ----------------------------------------------------------------------------

def metadata(environ, start_response):
    try:
        path = args.path
        if path is None or len(path) == 0:
            path = os.path.dirname(os.path.abspath( __file__ ))
        if path[-1] != "/":
            path += "/"
        metadata = create_metadata_string(path+"sp_conf.py", None,
                                          args.valid, args.cert, args.keyfile,
                                          args.id, args.name, args.sign)
        start_response('200 OK', [('Content-Type', "text/xml")])
        return metadata
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
    logger.info("<application> PATH: %s", path)

    if path == "metadata":
        return metadata(environ, start_response)

    user = environ.get("REMOTE_USER", "")
    if not user:
        user = environ.get("repoze.who.identity", "")
        logger.info("repoze.who.identity: '%s'", user)
    else:
        logger.info("REMOTE_USER: '%s'", user)
    #logger.info(logging.Logger.manager.loggerDict)
    for regex, callback in urls:
        if user:
            match = re.search(regex, path)
            if match is not None:
                try:
                    environ['myapp.url_args'] = match.groups()[0]
                except IndexError:
                    environ['myapp.url_args'] = path
                return callback(environ, start_response, user)
        else:
            return not_authn(environ, start_response)

    return not_found(environ, start_response)

# ----------------------------------------------------------------------------

from repoze.who.config import make_middleware_with_config

app_with_auth = make_middleware_with_config(application, {"here": "."},
                                            './who.ini',
                                            log_file="repoze_who.log")

# ----------------------------------------------------------------------------
HOST = sp_conf.HOST
PORT = sp_conf.PORT

# allow uwsgi or gunicorn mount
# by moving some initialization out of __name__ == '__main__' section.
# uwsgi -s 0.0.0.0:8087 --protocol http --callable app_with_auth --module idp

if __name__ == '__main__':
    #make_metadata arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', dest='path', help='Path to configuration file.')
    parser.add_argument('-v', dest='valid', default="4",
                        help="How long, in days, the metadata is valid from the time of creation")
    parser.add_argument('-c', dest='cert', help='certificate')
    parser.add_argument('-i', dest='id',
                        help="The ID of the entities descriptor in the metadata")
    parser.add_argument('-k', dest='keyfile',
                        help="A file with a key to sign the metadata with")
    parser.add_argument('-n', dest='name')
    parser.add_argument('-s', dest='sign', action='store_true',
                        help="sign the metadata")
    args = parser.parse_args()

    from wsgiref.simple_server import make_server
    srv = make_server(HOST, PORT, app_with_auth)
    print("SP listening on %s:%s" % (HOST, PORT))
    srv.serve_forever()
