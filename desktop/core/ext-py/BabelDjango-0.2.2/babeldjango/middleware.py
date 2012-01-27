# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://babel.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://babel.edgewall.org/log/.

from babel import Locale, UnknownLocaleError
from django.conf import settings
try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

__all__ = ['get_current_locale', 'LocaleMiddleware']

_thread_locals = local()

def get_current_locale():
    """Get current locale data outside views.

    See http://babel.edgewall.org/wiki/ApiDocs/babel.core for Locale
    objects documentation
    """
    return getattr(_thread_locals, 'locale', None)


class LocaleMiddleware(object):
    """Simple Django middleware that makes available a Babel `Locale` object
    via the `request.locale` attribute.
    """

    def process_request(self, request):
        try:
            code = getattr(request, 'LANGUAGE_CODE', settings.LANGUAGE_CODE)
            locale = Locale.parse(code, sep='-')
        except (ValueError, UnknownLocaleError):
            pass
        else:
            _thread_locals.locale = request.locale = locale
