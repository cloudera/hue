"This is the locale selecting middleware that will look at accept headers"

from django.conf import settings
from django.core.urlresolvers import (is_valid_path, get_resolver,
                                      LocaleRegexURLResolver)
from django.http import HttpResponseRedirect
from django.utils.cache import patch_vary_headers
from django.utils import translation
from django.utils.datastructures import SortedDict


class LocaleMiddleware(object):
    """
    This is a very simple middleware that parses a request
    and decides what translation object to install in the current
    thread context. This allows pages to be dynamically
    translated to the language the user desires (if the language
    is available, of course).
    """

    def __init__(self):
        self._supported_languages = SortedDict(settings.LANGUAGES)
        self._is_language_prefix_patterns_used = False
        for url_pattern in get_resolver(None).url_patterns:
            if isinstance(url_pattern, LocaleRegexURLResolver):
                self._is_language_prefix_patterns_used = True
                break

    def process_request(self, request):
        check_path = self.is_language_prefix_patterns_used()
        language = translation.get_language_from_request(
            request, check_path=check_path)
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        language = translation.get_language()
        language_from_path = translation.get_language_from_path(
                request.path_info, supported=self._supported_languages
        )
        if (response.status_code == 404 and not language_from_path
                and self.is_language_prefix_patterns_used()):
            urlconf = getattr(request, 'urlconf', None)
            language_path = '/%s%s' % (language, request.path_info)
            path_valid = is_valid_path(language_path, urlconf)
            if (not path_valid and settings.APPEND_SLASH
                    and not language_path.endswith('/')):
                path_valid = is_valid_path("%s/" % language_path, urlconf)

            if path_valid:
                language_url = "%s://%s/%s%s" % (
                    'https' if request.is_secure() else 'http',
                    request.get_host(), language, request.get_full_path())
                return HttpResponseRedirect(language_url)

        if not (self.is_language_prefix_patterns_used()
                and language_from_path):
            patch_vary_headers(response, ('Accept-Language',))
        if 'Content-Language' not in response:
            response['Content-Language'] = language
        return response

    def is_language_prefix_patterns_used(self):
        """
        Returns `True` if the `LocaleRegexURLResolver` is used
        at root level of the urlpatterns, else it returns `False`.
        """
        return self._is_language_prefix_patterns_used
