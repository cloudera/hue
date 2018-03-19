import kerberos
import re
import logging
import threading

from requests.auth import AuthBase
from requests.models import Response
from requests.compat import urlparse, StringIO
from requests.structures import CaseInsensitiveDict
from requests.cookies import cookiejar_from_dict

from .exceptions import MutualAuthenticationError

log = logging.getLogger(__name__)


# Different types of mutual authentication:
#  with mutual_authentication set to REQUIRED, all responses will be
#   authenticated with the exception of errors. Errors will have their contents
#   and headers stripped. If a non-error response cannot be authenticated, a
#   MutualAuthenticationError exception will be raised.
# with mutual_authentication set to OPTIONAL, mutual authentication will be
#   attempted if supported, and if supported and failed, a
#   MutualAuthenticationError exception will be raised. Responses which do not
#   support mutual authentication will be returned directly to the user.
# with mutual_authentication set to DISABLED, mutual authentication will not be
#   attempted, even if supported.
REQUIRED = 1
OPTIONAL = 2
DISABLED = 3


class SanitizedResponse(Response):
    """The :class:`Response <Response>` object, which contains a server's
    response to an HTTP request.

    This differs from `requests.models.Response` in that it's headers and
    content have been sanitized. This is only used for HTTP Error messages
    which do not support mutual authentication when mutual authentication is
    required."""

    def __init__(self, response):
        super(SanitizedResponse, self).__init__()
        self.status_code = response.status_code
        self.encoding = response.encoding
        self.raw = response.raw
        self.reason = response.reason
        self.url = response.url
        self.request = response.request
        self.history = list(response.history)
        self.connection = response.connection
        self._content_consumed = True

        self._content = ""
        self.cookies = cookiejar_from_dict({})
        self.headers = CaseInsensitiveDict()
        self.headers['content-length'] = '0'
        for header in ('date', 'server'):
            if header in response.headers:
                self.headers[header] = response.headers[header]


def _negotiate_value(response):
    """Extracts the gssapi authentication token from the appropriate header"""
    if hasattr(_negotiate_value, 'regex'):
        regex = _negotiate_value.regex
    else:
        # There's no need to re-compile this EVERY time it is called. Compile
        # it once and you won't have the performance hit of the compilation.
        regex = re.compile('(?:.*,)*\s*Negotiate\s*([^,]*),?', re.I)
        _negotiate_value.regex = regex

    authreq = response.headers.get('www-authenticate', None)

    if authreq:
        match_obj = regex.search(authreq)
        if match_obj:
            return match_obj.group(1)

    return None


class HTTPKerberosAuth(AuthBase):
    """Attaches HTTP GSSAPI/Kerberos Authentication to the given Request
    object."""
    def __init__(self, mutual_authentication=REQUIRED, service="HTTP"):
        self.context = {}
        self.mutual_authentication = mutual_authentication
        self.pos = None
        self.service = service

    def generate_request_header(self, response):
        """
        Generates the GSSAPI authentication token with kerberos.

        If any GSSAPI step fails, return None.

        """
        host = urlparse(response.url).hostname

        # Initialize uniq key for the self.context dictionary
        host_port_thread = "%s_%s_%s" % (urlparse(response.url).hostname,
                                         urlparse(response.url).port,
                                         threading.current_thread().ident)

        try:
            result, self.context[host_port_thread] = kerberos.authGSSClientInit(
                "{0}@{1}".format(self.service, host))
        except kerberos.GSSError:
            log.exception("generate_request_header(): authGSSClientInit() failed:")
            return None

        if result < 1:
            log.error("generate_request_header(): authGSSClientInit() failed: "
                      "{0}".format(result))
            return None

        try:
            result = kerberos.authGSSClientStep(self.context[host_port_thread],
                                                _negotiate_value(response))
        except kerberos.GSSError:
            log.exception("generate_request_header(): authGSSClientStep() failed:")
            return None

        if result < 0:
            log.error("generate_request_header(): authGSSClientStep() failed: "
                      "{0}".format(result))
            return None

        try:
            gss_response = kerberos.authGSSClientResponse(self.context[host_port_thread])
        except kerberos.GSSError:
            log.exception("generate_request_header(): authGSSClientResponse() "
                      "failed:")
            return None

        return "Negotiate {0}".format(gss_response)

    def authenticate_user(self, response, **kwargs):
        """Handles user authentication with gssapi/kerberos"""

        auth_header = self.generate_request_header(response)
        if auth_header is None:
            # GSS Failure, return existing response
            return response

        log.debug("authenticate_user(): Authorization header: {0}".format(
            auth_header))
        response.request.headers['Authorization'] = auth_header

        # Consume the content so we can reuse the connection for the next
        # request.
        response.content
        response.raw.release_conn()

        _r = response.connection.send(response.request, **kwargs)
        _r.history.append(response)

        log.debug("authenticate_user(): returning {0}".format(_r))
        return _r

    def handle_401(self, response, **kwargs):
        """Handles 401's, attempts to use gssapi/kerberos authentication"""

        log.debug("handle_401(): Handling: 401")
        if _negotiate_value(response) is not None:
            _r = self.authenticate_user(response, **kwargs)
            log.debug("handle_401(): returning {0}".format(_r))
            return _r
        else:
            log.debug("handle_401(): Kerberos is not supported")
            log.debug("handle_401(): returning {0}".format(response))
            return response

    def handle_mutual_auth(self, response):
        """
        Performs mutual auth checking if possible and requested. This handling
        is applied to *all* responses, not just 401s.
        """

        log.debug("handle_mutual_auth(): Handling: %d" % response.status_code)

        if self.mutual_authentication in (REQUIRED, OPTIONAL):

            is_http_error = response.status_code >= 400

            if _negotiate_value(response) is not None:
                log.debug("handle_mutual_auth(): Authenticating the server")
                if not self.authenticate_server(response):
                    # Mutual authentication failure when mutual auth is wanted,
                    # raise an exception so the user doesn't use an untrusted
                    # response.
                    log.error("handle_mutual_auth(): Mutual authentication failed")
                    raise MutualAuthenticationError("Unable to authenticate "
                                                    "{0}".format(response))

                # Authentication successful
                log.debug("handle_mutual_auth(): returning {0}".format(response))
                return response

            elif is_http_error or self.mutual_authentication == OPTIONAL:
                if not response.ok:
                    log.error("handle_mutual_auth(): Mutual authentication unavailable "
                              "on {0} response".format(response.status_code))

                if self.mutual_authentication == REQUIRED:
                    return SanitizedResponse(response)
                else:
                    return response
            else:
                # Unable to attempt mutual authentication when mutual auth is
                # required, raise an exception so the user doesnt use an
                # untrusted response.
                log.error("handle_mutual_auth(): Mutual authentication failed")
                raise MutualAuthenticationError("Unable to authenticate "
                                                "{0}".format(response))
        else:
            log.debug("handle_mutual_auth(): returning {0}".format(response))
            return response

    def authenticate_server(self, response):
        """
        Uses GSSAPI to authenticate the server.

        Returns True on success, False on failure.
        """

        log.debug("authenticate_server(): Authenticate header: {0}".format(
            _negotiate_value(response)))

        host_port_thread = "%s_%s_%s" % (urlparse(response.url).hostname,
                                         urlparse(response.url).port,
                                         threading.current_thread().ident)

        try:
            result = kerberos.authGSSClientStep(self.context[host_port_thread],
                                                _negotiate_value(response))
        except kerberos.GSSError:
            log.exception("authenticate_server(): authGSSClientStep() failed:")
            return False

        if result < 1:
            log.error("authenticate_server(): authGSSClientStep() failed: "
                      "{0}".format(result))
            return False

        log.debug("authenticate_server(): returning {0}".format(response))
        return True

    def handle_response(self, response, **kwargs):
        """Takes the given response and tries kerberos-auth, as needed."""

        if self.pos is not None:
            # Rewind the file position indicator of the body to where
            # it was to resend the request.
            response.request.body.seek(self.pos)

        if response.status_code == 401:
            _r = self.handle_401(response, **kwargs)
            log.debug("handle_response(): returning {0}".format(_r))
            return self.handle_mutual_auth(_r)
        else:
            _r = self.handle_mutual_auth(response)
            log.debug("handle_response(): returning {0}".format(_r))
            return _r

    def deregister(self, response):
        """Deregisters the response handler"""
        response.request.deregister_hook('response', self.handle_response)

    def __call__(self, request):
        request.register_hook('response', self.handle_response)
        try:
            self.pos = request.body.tell()
        except AttributeError:
            # In the case of HTTPKerberosAuth being reused and the body
            # of the previous request was a file-like object, pos has
            # the file position of the previous body. Ensure it's set to
            # None.
            self.pos = None
        return request
