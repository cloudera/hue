import logging

from django.conf import settings

import saml2.client

logger = logging.getLogger("djangosaml2")


class Saml2Client(saml2.client.Saml2Client):
    """
    Custom Saml2Client that adds a choice of preference for binding used with
    SAML Logout Requests. The preferred binding can be configured via
    SAML_LOGOUT_REQUEST_PREFERRED_BINDING settings variable.
    (Original Saml2Client always prefers SOAP, so it is always used if declared
    in remote metadata); but doesn't actually work and causes crashes.
    """

    def do_logout(self, *args, **kwargs):
        if not kwargs.get("expected_binding"):
            try:
                kwargs[
                    "expected_binding"
                ] = settings.SAML_LOGOUT_REQUEST_PREFERRED_BINDING
            except AttributeError:
                logger.warning(
                    "SAML_LOGOUT_REQUEST_PREFERRED_BINDING setting is"
                    " not defined. Default binding will be used."
                )
        return super().do_logout(*args, **kwargs)
