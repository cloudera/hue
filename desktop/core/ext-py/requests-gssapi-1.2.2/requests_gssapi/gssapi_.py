import re
import logging

from base64 import b64encode, b64decode

import gssapi

from requests.auth import AuthBase
from requests.models import Response
from requests.compat import urlparse
from requests.structures import CaseInsensitiveDict
from requests.cookies import cookiejar_from_dict

from .exceptions import MutualAuthenticationError, SPNEGOExchangeError

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
        regex = re.compile(r'Negotiate\s*([^,]*)', re.I)
        _negotiate_value.regex = regex

    authreq = response.headers.get('www-authenticate', None)
    if authreq:
        match_obj = regex.search(authreq)
        if match_obj:
            return b64decode(match_obj.group(1))

    return None


class HTTPSPNEGOAuth(AuthBase):
    """Attaches HTTP GSSAPI Authentication to the given Request object.

    `mutual_authentication` controls whether GSSAPI should attempt mutual
    authentication.  It may be `REQUIRED`, `OPTIONAL`, or `DISABLED`
    (default).

    `target_name` specifies the remote principal name.  It may be either a
    GSSAPI Name type or a string.  If a string, it will be treated as a
    hostbased service; if it contains no '@', the DNS host will be supplied.
    (default: "HTTP" at the DNS host).

    `delegate` indicates whether we should attempt credential delegation.
    Default is `False`.

    `opportunistic_auth` indicates whether we should assume the server will
    ask for Negotiation.  Defaut is `False`.

    `creds` is GSSAPI credentials (gssapi.Credentials) to use for negotiation.
    Default is `None`.

    `mech` is GSSAPI Mechanism (gssapi.Mechanism) to use for negotiation.
    Default is `None`

    `sanitize_mutual_error_response` controls whether we should clean up
    server responses.  See the `SanitizedResponse` class.

    """
    def __init__(self, mutual_authentication=DISABLED, target_name="HTTP",
                 delegate=False, opportunistic_auth=False, creds=None,
                 mech=None, sanitize_mutual_error_response=True):
        self.context = {}
        self.pos = None
        self.mutual_authentication = mutual_authentication
        self.target_name = target_name
        self.delegate = delegate
        self.opportunistic_auth = opportunistic_auth
        self.creds = creds
        self.mech = mech
        self.sanitize_mutual_error_response = sanitize_mutual_error_response

    def generate_request_header(self, response, host, is_preemptive=False):
        """
        Generates the GSSAPI authentication token

        If any GSSAPI step fails, raise SPNEGOExchangeError
        with failure detail.

        """

        gssflags = [gssapi.RequirementFlag.out_of_sequence_detection]
        if self.delegate:
            gssflags.append(gssapi.RequirementFlag.delegate_to_peer)
        if self.mutual_authentication != DISABLED:
            gssflags.append(gssapi.RequirementFlag.mutual_authentication)

        try:
            gss_stage = "initiating context"
            name = self.target_name
            if type(name) != gssapi.Name:
                if '@' not in name:
                    name = "%s@%s" % (name, host)

                name = gssapi.Name(name, gssapi.NameType.hostbased_service)
            self.context[host] = gssapi.SecurityContext(
                usage="initiate", flags=gssflags, name=name,
                creds=self.creds, mech=self.mech)

            gss_stage = "stepping context"
            if is_preemptive:
                gss_response = self.context[host].step()
            else:
                gss_response = self.context[host].step(
                    _negotiate_value(response))

            return "Negotiate {0}".format(b64encode(gss_response).decode())

        except gssapi.exceptions.GSSError as error:
            msg = error.gen_message()
            log.exception(
                "generate_request_header(): {0} failed:".format(gss_stage))
            log.exception(msg)
            raise SPNEGOExchangeError("%s failed: %s" % (gss_stage, msg))

    def authenticate_user(self, response, **kwargs):
        """Handles user authentication with GSSAPI"""

        host = urlparse(response.url).hostname

        try:
            auth_header = self.generate_request_header(response, host)
        except SPNEGOExchangeError:
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
        """Handles 401's, attempts to use GSSAPI authentication"""

        log.debug("handle_401(): Handling: 401")
        if _negotiate_value(response) is not None:
            _r = self.authenticate_user(response, **kwargs)
            log.debug("handle_401(): returning {0}".format(_r))
            return _r
        else:
            log.debug("handle_401(): GSSAPI is not supported")
            log.debug("handle_401(): returning {0}".format(response))
            return response

    def handle_other(self, response):
        """Handles all responses with the exception of 401s.

        This is necessary so that we can authenticate responses if requested"""

        log.debug("handle_other(): Handling: %d" % response.status_code)

        if self.mutual_authentication not in (REQUIRED, OPTIONAL):
            log.debug("handle_other(): returning {0}".format(response))
            return response

        is_http_error = response.status_code >= 400

        if _negotiate_value(response) is not None:
            log.debug("handle_other(): Authenticating the server")
            if not self.authenticate_server(response):
                # Mutual authentication failure when mutual auth is wanted,
                # raise an exception so the user doesn't use an untrusted
                # response.
                log.error("handle_other(): Mutual authentication failed")
                raise MutualAuthenticationError(
                    "Unable to authenticate {0}".format(response))

            # Authentication successful
            log.debug("handle_other(): returning {0}".format(response))
            return response
        elif is_http_error or self.mutual_authentication == OPTIONAL:
            if not response.ok:
                log.error(
                    "handle_other(): Mutual authentication unavailable on"
                    " {0} response".format(response.status_code))

            if self.mutual_authentication == REQUIRED and \
               self.sanitize_mutual_error_response:
                return SanitizedResponse(response)
            return response
        else:
            # Unable to attempt mutual authentication when mutual auth is
            # required, raise an exception so the user doesn't use an
            # untrusted response.
            log.error("handle_other(): Mutual authentication failed")
            raise MutualAuthenticationError(
                "Unable to authenticate {0}".format(response))

    def authenticate_server(self, response):
        """
        Uses GSSAPI to authenticate the server.

        Returns True on success, False on failure.
        """

        log.debug("authenticate_server(): Authenticate header: {0}".format(
            _negotiate_value(response)))

        host = urlparse(response.url).hostname

        try:
            # If the handshake isn't complete here, nothing we can do
            self.context[host].step(_negotiate_value(response))
        except gssapi.exceptions.GSSError as error:
            log.exception("authenticate_server(): context stepping failed:")
            log.exception(error.gen_message())
            return False

        log.debug("authenticate_server(): returning {0}".format(response))
        return True

    def handle_response(self, response, **kwargs):
        """Takes the given response and tries GSSAPI auth, as needed."""
        num_401s = kwargs.pop('num_401s', 0)

        if self.pos is not None:
            # Rewind the file position indicator of the body to where
            # it was to resend the request.
            response.request.body.seek(self.pos)

        if response.status_code == 401 and num_401s < 2:
            # 401 Unauthorized. Handle it, and if it still comes back as 401,
            # that means authentication failed.
            _r = self.handle_401(response, **kwargs)
            log.debug("handle_response(): returning %s", _r)
            log.debug("handle_response() has seen %d 401 responses", num_401s)
            num_401s += 1
            return self.handle_response(_r, num_401s=num_401s, **kwargs)
        elif response.status_code == 401 and num_401s >= 2:
            # Still receiving 401 responses after attempting to handle them.
            # Authentication has failed. Return the 401 response.
            log.debug("handle_response(): returning 401 %s", response)
            return response

        _r = self.handle_other(response)
        log.debug("handle_response(): returning %s", _r)
        return _r

    def deregister(self, response):
        """Deregisters the response handler"""
        response.request.deregister_hook('response', self.handle_response)

    def __call__(self, request):
        if self.opportunistic_auth:
            # add Authorization header before we receive a 401
            # by the 401 handler
            host = urlparse(request.url).hostname

            auth_header = self.generate_request_header(None, host,
                                                       is_preemptive=True)

            log.debug(
                "HTTPSPNEGOAuth: Preemptive Authorization header: {0}"
                .format(auth_header))

            request.headers['Authorization'] = auth_header

        request.register_hook('response', self.handle_response)
        try:
            self.pos = request.body.tell()
        except AttributeError:
            # In the case of HTTPSPNEGOAuth being reused and the body
            # of the previous request was a file-like object, pos has
            # the file position of the previous body. Ensure it's set to
            # None.
            self.pos = None
        return request
