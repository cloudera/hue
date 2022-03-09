import hashlib
import hmac
import logging
import time
import cgi
import six

from six.moves.urllib.parse import quote, parse_qs
from six.moves.http_cookies import SimpleCookie

from saml2 import BINDING_HTTP_ARTIFACT
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_URI
from saml2 import BINDING_SOAP
from saml2 import SAMLError
from saml2 import time_util

__author__ = 'rohe0002'

logger = logging.getLogger(__name__)


class Response(object):
    _template = None
    _status = '200 OK'
    _content_type = 'text/html'
    _mako_template = None
    _mako_lookup = None

    def __init__(self, message=None, **kwargs):
        self.status = kwargs.get('status', self._status)
        self.response = kwargs.get('response', self._response)
        self.template = kwargs.get('template', self._template)
        self.mako_template = kwargs.get('mako_template', self._mako_template)
        self.mako_lookup = kwargs.get('template_lookup', self._mako_lookup)

        self.message = message

        self.headers = kwargs.get('headers', [])
        _content_type = kwargs.get('content', self._content_type)
        addContentType = True
        for header in self.headers:
            if 'content-type' == header[0].lower():
                addContentType = False
        if addContentType:
            self.headers.append(('Content-type', _content_type))

    def __call__(self, environ, start_response, **kwargs):
        try:
            start_response(self.status, self.headers)
        except TypeError:
            pass
        return self.response(self.message or geturl(environ), **kwargs)

    def _response(self, message="", **argv):
        if self.template:
            message = self.template % message
        elif self.mako_lookup and self.mako_template:
            argv["message"] = message
            mte = self.mako_lookup.get_template(self.mako_template)
            message = mte.render(**argv)

        if isinstance(message, six.string_types):
            return [message.encode('utf-8')]
        elif isinstance(message, six.binary_type):
            return [message]
        else:
            return message

    def add_header(self, ava):
        """
        Does *NOT* replace a header of the same type, just adds a new
        :param ava: (type, value) tuple
        """
        self.headers.append(ava)

    def reply(self, **kwargs):
        return self.response(self.message, **kwargs)


class Created(Response):
    _status = "201 Created"


class Redirect(Response):
    _template = '<html>\n<head><title>Redirecting to %s</title></head>\n' \
                '<body>\nYou are being redirected to <a href="%s">%s</a>\n' \
                '</body>\n</html>'
    _status = '302 Found'

    def __call__(self, environ, start_response, **kwargs):
        location = self.message
        self.headers.append(('location', location))
        start_response(self.status, self.headers)
        return self.response((location, location, location))


class SeeOther(Response):
    _template = '<html>\n<head><title>Redirecting to %s</title></head>\n' \
                '<body>\nYou are being redirected to <a href="%s">%s</a>\n' \
                '</body>\n</html>'
    _status = '303 See Other'

    def __call__(self, environ, start_response, **kwargs):
        location = ""
        if self.message:
            location = self.message
            self.headers.append(('location', location))
        else:
            for param, item in self.headers:
                if param == "location":
                    location = item
                    break
        start_response(self.status, self.headers)
        return self.response((location, location, location))


class Forbidden(Response):
    _status = '403 Forbidden'
    _template = "<html>Not allowed to mess with: '%s'</html>"


class BadRequest(Response):
    _status = "400 Bad Request"
    _template = "<html>%s</html>"


class Unauthorized(Response):
    _status = "401 Unauthorized"
    _template = "<html>%s</html>"


class NotFound(Response):
    _status = '404 NOT FOUND'


class NotAcceptable(Response):
    _status = '406 Not Acceptable'


class ServiceError(Response):
    _status = '500 Internal Service Error'


class NotImplemented(Response):
    _status = "501 Not Implemented"
    # override template since we need an environment variable
    template = ('The request method %s is not implemented '
                'for this server.\r\n%s')


class BadGateway(Response):
    _status = "502 Bad Gateway"


class HttpParameters(object):
    """GET or POST signature parameters for Redirect or POST-SimpleSign bindings
    because they are not contained in XML unlike the POST binding
    """
    signature = None
    sigalg = None
    # Relaystate and SAML message are stored elsewhere
    def __init__(self, dict):
        try:
            self.signature = dict["Signature"][0]
            self.sigalg = dict["SigAlg"][0]
        except KeyError:
            pass


def extract(environ, empty=False, err=False):
    """Extracts strings in form data and returns a dict.

    :param environ: WSGI environ
    :param empty: Stops on empty fields (default: Fault)
    :param err: Stops on errors in fields (default: Fault)
    """
    formdata = cgi.parse(environ['wsgi.input'], environ, empty, err)
    # Remove single entries from lists
    for key, value in iter(formdata.items()):
        if len(value) == 1:
            formdata[key] = value[0]
    return formdata


def geturl(environ, query=True, path=True, use_server_name=False):
    """Rebuilds a request URL (from PEP 333).
    You may want to chose to use the environment variables
    server_name and server_port instead of http_host in some case.
    The parameter use_server_name allows you to chose.

    :param query: Is QUERY_STRING included in URI (default: True)
    :param path: Is path included in URI (default: True)
    :param use_server_name: If SERVER_NAME/_HOST should be used instead of
        HTTP_HOST
    """
    url = [environ['wsgi.url_scheme'] + '://']
    if use_server_name:
        url.append(environ['SERVER_NAME'])
        if environ['wsgi.url_scheme'] == 'https':
            if environ['SERVER_PORT'] != '443':
                url.append(':' + environ['SERVER_PORT'])
        else:
            if environ['SERVER_PORT'] != '80':
                url.append(':' + environ['SERVER_PORT'])
    else:
        url.append(environ['HTTP_HOST'])
    if path:
        url.append(getpath(environ))
    if query and environ.get('QUERY_STRING'):
        url.append('?' + environ['QUERY_STRING'])
    return ''.join(url)


def getpath(environ):
    """Builds a path."""
    return ''.join([quote(environ.get('SCRIPT_NAME', '')),
                    quote(environ.get('PATH_INFO', ''))])


def get_post(environ):
    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0

    # When the method is POST the query string will be sent
    # in the HTTP request body which is passed by the WSGI server
    # in the file like wsgi.input environment variable.
    return environ['wsgi.input'].read(request_body_size)


def get_response(environ, start_response):
    if environ.get("REQUEST_METHOD") == "GET":
        query = environ.get("QUERY_STRING")
    elif environ.get("REQUEST_METHOD") == "POST":
        query = get_post(environ)
    else:
        resp = BadRequest("Unsupported method")
        return resp(environ, start_response)

    return query


def unpack_redirect(environ):
    if "QUERY_STRING" in environ:
        _qs = environ["QUERY_STRING"]
        return dict([(k, v[0]) for k, v in parse_qs(_qs).items()])
    else:
        return None


def unpack_post(environ):
    return dict([(k, v[0]) for k, v in parse_qs(get_post(environ))])


def unpack_soap(environ):
    try:
        query = get_post(environ)
        return {"SAMLRequest": query, "RelayState": ""}
    except Exception:
        return None


def unpack_artifact(environ):
    if environ["REQUEST_METHOD"] == "GET":
        _dict = unpack_redirect(environ)
    elif environ["REQUEST_METHOD"] == "POST":
        _dict = unpack_post(environ)
    else:
        _dict = None
    return _dict


def unpack_any(environ):
    if environ['REQUEST_METHOD'].upper() == 'GET':
        # Could be either redirect or artifact
        _dict = unpack_redirect(environ)
        if "ID" in _dict:
            binding = BINDING_URI
        elif "SAMLart" in _dict:
            binding = BINDING_HTTP_ARTIFACT
        else:
            binding = BINDING_HTTP_REDIRECT
    else:
        content_type = environ.get('CONTENT_TYPE', 'application/soap+xml')
        if content_type != 'application/soap+xml':
            # normal post
            _dict = unpack_post(environ)
            if "SAMLart" in _dict:
                binding = BINDING_HTTP_ARTIFACT
            else:
                binding = BINDING_HTTP_POST
        else:
            _dict = unpack_soap(environ)
            binding = BINDING_SOAP

    return _dict, binding


def _expiration(timeout, time_format=None):
    if timeout == "now":
        return time_util.instant(time_format)
    else:
        # validity time should match lifetime of assertions
        return time_util.in_a_while(minutes=timeout, format=time_format)


def cookie_signature(seed, *parts):
    """Generates a cookie signature."""
    sha1 = hmac.new(seed, digestmod=hashlib.sha1)
    for part in parts:
        if part:
            sha1.update(part)
    return sha1.hexdigest()


def make_cookie(name, load, seed, expire=0, domain="", path="",
                timestamp=""):
    """
    Create and return a cookie

    :param name: Cookie name
    :param load: Cookie load
    :param seed: A seed for the HMAC function
    :param expire: Number of minutes before this cookie goes stale
    :param domain: The domain of the cookie
    :param path: The path specification for the cookie
    :return: A tuple to be added to headers
    """
    cookie = SimpleCookie()
    if not timestamp:
        timestamp = str(int(time.mktime(time.gmtime())))
    signature = cookie_signature(seed, load, timestamp)
    cookie[name] = "|".join([load, timestamp, signature])
    if path:
        cookie[name]["path"] = path
    if domain:
        cookie[name]["domain"] = domain
    if expire:
        cookie[name]["expires"] = _expiration(expire,
                                              "%a, %d-%b-%Y %H:%M:%S GMT")

    return tuple(cookie.output().split(": ", 1))


def parse_cookie(name, seed, kaka):
    """Parses and verifies a cookie value

    :param seed: A seed used for the HMAC signature
    :param kaka: The cookie
    :return: A tuple consisting of (payload, timestamp)
    """
    if not kaka:
        return None

    cookie_obj = SimpleCookie(kaka)
    morsel = cookie_obj.get(name)

    if morsel:
        parts = morsel.value.split("|")
        if len(parts) != 3:
            return None
            # verify the cookie signature
        sig = cookie_signature(seed, parts[0], parts[1])
        if sig != parts[2]:
            raise SAMLError("Invalid cookie signature")

        try:
            return parts[0].strip(), parts[1]
        except KeyError:
            return None
    else:
        return None


def cookie_parts(name, kaka):
    cookie_obj = SimpleCookie(kaka)
    morsel = cookie_obj.get(name)
    if morsel:
        return morsel.value.split("|")
    else:
        return None
