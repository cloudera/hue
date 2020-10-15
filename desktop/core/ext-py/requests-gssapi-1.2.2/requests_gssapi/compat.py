"""
Compatibility library for older versions of python and requests_kerberos
"""
import sys

import gssapi

from .gssapi_ import DISABLED, HTTPSPNEGOAuth, SPNEGOExchangeError, log

# python 2.7 introduced a NullHandler which we want to use, but to support
# older versions, we implement our own if needed.
if sys.version_info[:2] > (2, 6):
    from logging import NullHandler
else:
    from logging import Handler

    class NullHandler(Handler):
        def emit(self, record):
            pass


class HTTPKerberosAuth(HTTPSPNEGOAuth):
    """Deprecated compat shim; see HTTPSPNEGOAuth instead."""
    def __init__(self, mutual_authentication=DISABLED, service="HTTP",
                 delegate=False, force_preemptive=False, principal=None,
                 hostname_override=None, sanitize_mutual_error_response=True):
        # put these here for later
        self.principal = principal
        self.service = service
        self.hostname_override = hostname_override

        HTTPSPNEGOAuth.__init__(
            self,
            mutual_authentication=mutual_authentication,
            target_name=None,
            delegate=delegate,
            opportunistic_auth=force_preemptive,
            creds=None,
            sanitize_mutual_error_response=sanitize_mutual_error_response)

    def generate_request_header(self, response, host, is_preemptive=False):
        # This method needs to be shimmed because `host` isn't exposed to
        # __init__() and we need to derive things from it.  Also, __init__()
        # can't fail, in the strictest compatability sense.
        try:
            if self.principal is not None:
                gss_stage = "acquiring credentials"
                name = gssapi.Name(
                    self.principal, gssapi.NameType.user)
                self.creds = gssapi.Credentials(name=name, usage="initiate")

            # contexts still need to be stored by host, but hostname_override
            # allows use of an arbitrary hostname for the GSSAPI exchange (eg,
            # in cases of aliased hosts, internal vs external, CNAMEs w/
            # name-based HTTP hosting)
            if self.service is not None:
                gss_stage = "initiating context"
                kerb_host = host
                if self.hostname_override:
                    kerb_host = self.hostname_override

                kerb_spn = "{0}@{1}".format(self.service, kerb_host)
                self.target_name = gssapi.Name(
                    kerb_spn, gssapi.NameType.hostbased_service)

            return HTTPSPNEGOAuth.generate_request_header(self, response,
                                                          host, is_preemptive)
        except gssapi.exceptions.GSSError as error:
            msg = error.gen_message()
            log.exception(
                "generate_request_header(): {0} failed:".format(gss_stage))
            log.exception(msg)
            raise SPNEGOExchangeError("%s failed: %s" % (gss_stage, msg))
