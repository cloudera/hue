import time

from django import VERSION
from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.utils.cache import patch_vary_headers
from django.utils.http import http_date

from django.contrib.sessions.backends.base import UpdateError
from django.contrib.sessions.middleware import SessionMiddleware

django_version = float("{}.{}".format(*VERSION[:2]))
SAMESITE_NONE = None if django_version < 3.1 else "None"


class SamlSessionMiddleware(SessionMiddleware):
    cookie_name = getattr(settings, "SAML_SESSION_COOKIE_NAME", "saml_session")

    def process_request(self, request):
        session_key = request.COOKIES.get(self.cookie_name, None)
        request.saml_session = self.SessionStore(session_key)

    def process_response(self, request, response):
        """
        If request.saml_session was modified, or if the configuration is to save the
        session every time, save the changes and set a session cookie or delete
        the session cookie if the session has been emptied.
        """
        SAMESITE = getattr(settings, "SAML_SESSION_COOKIE_SAMESITE", SAMESITE_NONE)

        try:
            accessed = request.saml_session.accessed
            modified = request.saml_session.modified
            empty = request.saml_session.is_empty()
        except AttributeError:
            return response
        # First check if we need to delete this cookie.
        # The session should be deleted only if the session is entirely empty.
        if self.cookie_name in request.COOKIES and empty:
            response.delete_cookie(
                self.cookie_name,
                path=settings.SESSION_COOKIE_PATH,
                domain=settings.SESSION_COOKIE_DOMAIN,
                samesite=SAMESITE,
            )
            patch_vary_headers(response, ("Cookie",))
        else:
            if accessed:
                patch_vary_headers(response, ("Cookie",))
            # relies and the global one
            if (modified or settings.SESSION_SAVE_EVERY_REQUEST) and not empty:
                if request.saml_session.get_expire_at_browser_close():
                    max_age = None
                    expires = None
                else:
                    max_age = request.saml_session.get_expiry_age()
                    expires_time = time.time() + max_age
                    expires = http_date(expires_time)
                # Save the session data and refresh the client cookie.
                # Skip session save for 500 responses, refs #3881.
                if response.status_code != 500:
                    try:
                        request.saml_session.save()
                    except UpdateError:
                        raise SuspiciousOperation(
                            "The request's session was deleted before the "
                            "request completed. The user may have logged "
                            "out in a concurrent request, for example."
                        )
                    response.set_cookie(
                        self.cookie_name,
                        request.saml_session.session_key,
                        max_age=max_age,
                        expires=expires,
                        domain=settings.SESSION_COOKIE_DOMAIN,
                        path=settings.SESSION_COOKIE_PATH,
                        secure=settings.SESSION_COOKIE_SECURE or None,
                        httponly=settings.SESSION_COOKIE_HTTPONLY or None,
                        samesite=SAMESITE,
                    )
        return response
