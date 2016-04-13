import json
import os
import gettext as gettext_module

from django import http
from django.conf import settings
from django.template import Context, Template
from django.utils import importlib
from django.utils.translation import check_for_language, to_locale, get_language
from django.utils.encoding import smart_text
from django.utils.formats import get_format_modules, get_format
from django.utils._os import upath
from django.utils.http import is_safe_url
from django.utils import six

def set_language(request):
    """
    Redirect to a given url while setting the chosen language in the
    session or cookie. The url and the language code need to be
    specified in the request parameters.

    Since this view changes how the user will see the rest of the site, it must
    only be accessed as a POST request. If called as a GET request, it will
    redirect to the page in the request (the 'next' parameter) without changing
    any state.
    """
    next = request.REQUEST.get('next')
    if not is_safe_url(url=next, host=request.get_host()):
        next = request.META.get('HTTP_REFERER')
        if not is_safe_url(url=next, host=request.get_host()):
            next = '/'
    response = http.HttpResponseRedirect(next)
    if request.method == 'POST':
        lang_code = request.POST.get('language', None)
        if lang_code and check_for_language(lang_code):
            if hasattr(request, 'session'):
                request.session['django_language'] = lang_code
            else:
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
    return response


def get_formats():
    """
    Returns all formats strings required for i18n to work
    """
    FORMAT_SETTINGS = (
        'DATE_FORMAT', 'DATETIME_FORMAT', 'TIME_FORMAT',
        'YEAR_MONTH_FORMAT', 'MONTH_DAY_FORMAT', 'SHORT_DATE_FORMAT',
        'SHORT_DATETIME_FORMAT', 'FIRST_DAY_OF_WEEK', 'DECIMAL_SEPARATOR',
        'THOUSAND_SEPARATOR', 'NUMBER_GROUPING',
        'DATE_INPUT_FORMATS', 'TIME_INPUT_FORMATS', 'DATETIME_INPUT_FORMATS'
    )
    result = {}
    for module in [settings] + get_format_modules(reverse=True):
        for attr in FORMAT_SETTINGS:
            result[attr] = get_format(attr)
    formats = {}
    for k, v in result.items():
        if isinstance(v, (six.string_types, int)):
            formats[k] = smart_text(v)
        elif isinstance(v, (tuple, list)):
            formats[k] = [smart_text(value) for value in v]
    return formats


js_catalog_template = r"""
{% autoescape off %}
(function (globals) {

  var django = globals.django || (globals.django = {});

  {% if plural %}
  django.pluralidx = function (n) {
    var v={{ plural }};
    if (typeof(v) == 'boolean') {
      return v ? 1 : 0;
    } else {
      return v;
    }
  };
  {% else %}
  django.pluralidx = function (count) { return (count == 1) ? 0 : 1; };
  {% endif %}

  {% if catalog_str %}
  /* gettext library */

  django.catalog = {{ catalog_str }};

  django.gettext = function (msgid) {
    var value = django.catalog[msgid];
    if (typeof(value) == 'undefined') {
      return msgid;
    } else {
      return (typeof(value) == 'string') ? value : value[0];
    }
  };

  django.ngettext = function (singular, plural, count) {
    var value = django.catalog[singular];
    if (typeof(value) == 'undefined') {
      return (count == 1) ? singular : plural;
    } else {
      return value[django.pluralidx(count)];
    }
  };

  django.gettext_noop = function (msgid) { return msgid; };

  django.pgettext = function (context, msgid) {
    var value = django.gettext(context + '\x04' + msgid);
    if (value.indexOf('\x04') != -1) {
      value = msgid;
    }
    return value;
  };

  django.npgettext = function (context, singular, plural, count) {
    var value = django.ngettext(context + '\x04' + singular, context + '\x04' + plural, count);
    if (value.indexOf('\x04') != -1) {
      value = django.ngettext(singular, plural, count);
    }
    return value;
  };
  {% else %}
  /* gettext identity library */

  django.gettext = function (msgid) { return msgid; };
  django.ngettext = function (singular, plural, count) { return (count == 1) ? singular : plural; };
  django.gettext_noop = function (msgid) { return msgid; };
  django.pgettext = function (context, msgid) { return msgid; };
  django.npgettext = function (context, singular, plural, count) { return (count == 1) ? singular : plural; };
  {% endif %}

  django.interpolate = function (fmt, obj, named) {
    if (named) {
      return fmt.replace(/%\(\w+\)s/g, function(match){return String(obj[match.slice(2,-2)])});
    } else {
      return fmt.replace(/%s/g, function(match){return String(obj.shift())});
    }
  };


  /* formatting library */

  django.formats = {{ formats_str }};

  django.get_format = function (format_type) {
    var value = django.formats[format_type];
    if (typeof(value) == 'undefined') {
      return format_type;
    } else {
      return value;
    }
  };

  /* add to global namespace */
  globals.pluralidx = django.pluralidx;
  globals.gettext = django.gettext;
  globals.ngettext = django.ngettext;
  globals.gettext_noop = django.gettext_noop;
  globals.pgettext = django.pgettext;
  globals.npgettext = django.npgettext;
  globals.interpolate = django.interpolate;
  globals.get_format = django.get_format;

}(this));
{% endautoescape %}
"""


def render_javascript_catalog(catalog=None, plural=None):
    template = Template(js_catalog_template)
    indent = lambda s: s.replace('\n', '\n  ')
    context = Context({
        'catalog_str': indent(json.dumps(
            catalog, sort_keys=True, indent=2)) if catalog else None,
        'formats_str': indent(json.dumps(
            get_formats(), sort_keys=True, indent=2)),
        'plural': plural,
    })

    return http.HttpResponse(template.render(context), 'text/javascript')


def get_javascript_catalog(locale, domain, packages):
    default_locale = to_locale(settings.LANGUAGE_CODE)
    packages = [p for p in packages if p == 'django.conf' or p in settings.INSTALLED_APPS]
    t = {}
    paths = []
    en_selected = locale.startswith('en')
    en_catalog_missing = True
    # paths of requested packages
    for package in packages:
        p = importlib.import_module(package)
        path = os.path.join(os.path.dirname(upath(p.__file__)), 'locale')
        paths.append(path)
    # add the filesystem paths listed in the LOCALE_PATHS setting
    paths.extend(list(reversed(settings.LOCALE_PATHS)))
    # first load all english languages files for defaults
    for path in paths:
        try:
            catalog = gettext_module.translation(domain, path, ['en'])
            t.update(catalog._catalog)
        except IOError:
            pass
        else:
            # 'en' is the selected language and at least one of the packages
            # listed in `packages` has an 'en' catalog
            if en_selected:
                en_catalog_missing = False
    # next load the settings.LANGUAGE_CODE translations if it isn't english
    if default_locale != 'en':
        for path in paths:
            try:
                catalog = gettext_module.translation(domain, path, [default_locale])
            except IOError:
                catalog = None
            if catalog is not None:
                t.update(catalog._catalog)
    # last load the currently selected language, if it isn't identical to the default.
    if locale != default_locale:
        # If the currently selected language is English but it doesn't have a
        # translation catalog (presumably due to being the language translated
        # from) then a wrong language catalog might have been loaded in the
        # previous step. It needs to be discarded.
        if en_selected and en_catalog_missing:
            t = {}
        else:
            locale_t = {}
            for path in paths:
                try:
                    catalog = gettext_module.translation(domain, path, [locale])
                except IOError:
                    catalog = None
                if catalog is not None:
                    locale_t.update(catalog._catalog)
            if locale_t:
                t = locale_t
    plural = None
    if '' in t:
        for l in t[''].split('\n'):
            if l.startswith('Plural-Forms:'):
                plural = l.split(':', 1)[1].strip()
    if plural is not None:
        # this should actually be a compiled function of a typical plural-form:
        # Plural-Forms: nplurals=3; plural=n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2;
        plural = [el.strip() for el in plural.split(';') if el.strip().startswith('plural=')][0].split('=', 1)[1]

    pdict = {}
    maxcnts = {}
    catalog = {}
    for k, v in t.items():
        if k == '':
            continue
        if isinstance(k, six.string_types):
            catalog[k] = v
        elif isinstance(k, tuple):
            msgid = k[0]
            cnt = k[1]
            maxcnts[msgid] = max(cnt, maxcnts.get(msgid, 0))
            pdict.setdefault(msgid, {})[cnt] = v
        else:
            raise TypeError(k)
    for k, v in pdict.items():
        catalog[k] = [v.get(i, '') for i in range(maxcnts[msgid] + 1)]

    return catalog, plural


def null_javascript_catalog(request, domain=None, packages=None):
    """
    Returns "identity" versions of the JavaScript i18n functions -- i.e.,
    versions that don't actually do anything.
    """
    return render_javascript_catalog()


def javascript_catalog(request, domain='djangojs', packages=None):
    """
    Returns the selected language catalog as a javascript library.

    Receives the list of packages to check for translations in the
    packages parameter either from an infodict or as a +-delimited
    string from the request. Default is 'django.conf'.

    Additionally you can override the gettext domain for this view,
    but usually you don't want to do that, as JavaScript messages
    go to the djangojs domain. But this might be needed if you
    deliver your JavaScript source from Django templates.
    """
    locale = to_locale(get_language())

    if request.GET and 'language' in request.GET:
        if check_for_language(request.GET['language']):
            locale = to_locale(request.GET['language'])

    if packages is None:
        packages = ['django.conf']
    if isinstance(packages, six.string_types):
        packages = packages.split('+')

    catalog, plural = get_javascript_catalog(locale, domain, packages)
    return render_javascript_catalog(catalog, plural)
